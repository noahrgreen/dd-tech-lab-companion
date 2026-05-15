"""counterparty_risk_trajectory.py — Daily-frequency time-series for composite counterparty risk score.

Companion artifact for Foundry Article 008. Produces a daily TimeSeries
per Counterparty over the last 730 days, with a composite risk score
derived from four component signals (sanctions decay, adverse-media
rolling count, transaction z-score, KYC freshness).

CRITICAL: Composite weights and threshold parameters in this transform
are ILLUSTRATIVE ONLY. Production deployment requires institutional
calibration, validation, and documentation under the institution's own
model-risk-management program per SR 11-7 / OCC 2011-12 §V. See
model_governance/sr_11_7_validation_framework.md.

Lives in (production):
    /Code Repositories/dd_ingestion/transforms/counterparty_risk_trajectory.py
"""
from __future__ import annotations

try:
    from transforms.api import transform, Input, Output  # type: ignore
except ImportError:
    def transform(*args, **kwargs):
        def _wrap(fn):
            return fn
        return _wrap
    class _IO:
        def __init__(self, path: str):
            self.path = path
    Input = _IO
    Output = _IO

from pyspark.sql import functions as F, Window  # noqa: E402
from pyspark.sql.types import DateType  # noqa: E402

TRANSFORM_VERSION = "counterparty_risk_trajectory@v1.0"

# ── Illustrative composite weights ──────────────────────────────────────────
# These weights are NOT production-validated. The article's purpose is to
# demonstrate the engineering pattern. The institution must elicit, validate,
# and periodically re-review composite weights under their own model-risk
# governance per SR 11-7 §IV / §V.
COMPOSITE_WEIGHTS_ILLUSTRATIVE = {
    "sanctions": 0.40,
    "media": 0.25,
    "transaction": 0.20,
    "kyc": 0.15,
}
assert abs(sum(COMPOSITE_WEIGHTS_ILLUSTRATIVE.values()) - 1.0) < 1e-9

# ── Illustrative threshold parameters ───────────────────────────────────────
# Threshold values that trigger Article 005 Actions handoff. Production
# values require institutional calibration on labeled holdout data to manage
# false-positive rate / alert-fatigue trade-off.
THRESHOLDS_ILLUSTRATIVE = {
    "elevate_to_high": 0.60,    # composite score crossing 0.60 triggers EscalateToEDD review
    "elevate_to_critical": 0.85, # composite > 0.85 routes to ElevateRiskRating (critical)
    "change_point_zscore": 3.0,  # CUSUM/z-score breach of 3.0 over 30-day baseline
}


@transform(
    output=Output("/dd/timeseries/counterparty_risk_score"),
    counterparty=Input("/dd/ontology/Counterparty"),
    sanctions=Input("/dd/silver/sanctions_hits"),
    adverse_media=Input("/dd/silver/adverse_media_mentions"),
    transactions=Input("/dd/silver/transactions"),
)
def compute_risk_trajectory(ctx, counterparty, sanctions, adverse_media,
                             transactions, output):
    """Produce daily counterparty risk-score time series over 730-day lookback."""
    spark = ctx.spark_session
    date_spine = _build_date_spine(spark, days_back=730)

    cp_ids = counterparty.dataframe().select("counterparty_id").distinct()
    counterparty_dates = cp_ids.crossJoin(date_spine)

    sanctions_signal = _compute_sanctions_decay(sanctions.dataframe(), counterparty_dates)
    media_signal = _compute_media_rolling_count(
        adverse_media.dataframe(), counterparty_dates, window=90
    )
    transaction_signal = _compute_transaction_zscore(
        transactions.dataframe(), counterparty_dates, window=30
    )
    kyc_signal = _compute_kyc_freshness(counterparty.dataframe(), counterparty_dates)

    composite = (
        counterparty_dates
        .join(sanctions_signal, ["counterparty_id", "date"], "left")
        .join(media_signal, ["counterparty_id", "date"], "left")
        .join(transaction_signal, ["counterparty_id", "date"], "left")
        .join(kyc_signal, ["counterparty_id", "date"], "left")
        .fillna(0.0, subset=["sanctions_signal", "media_signal",
                              "transaction_signal", "kyc_signal"])
        .withColumn(
            "composite_risk_score",
            COMPOSITE_WEIGHTS_ILLUSTRATIVE["sanctions"] * F.col("sanctions_signal")
            + COMPOSITE_WEIGHTS_ILLUSTRATIVE["media"] * F.col("media_signal")
            + COMPOSITE_WEIGHTS_ILLUSTRATIVE["transaction"] * F.col("transaction_signal")
            + COMPOSITE_WEIGHTS_ILLUSTRATIVE["kyc"] * F.col("kyc_signal"),
        )
        .withColumn("pipeline_run_id", F.lit(ctx.run_id))
        .withColumn("transform_version", F.lit(TRANSFORM_VERSION))
        .withColumn("computed_at", F.current_timestamp())
    )

    output.write_dataframe(composite)


# ── Helper functions ────────────────────────────────────────────────────────

def _build_date_spine(spark, days_back: int):
    """Generate a daily date spine for the lookback window."""
    return (
        spark.range(0, days_back + 1)
        .withColumnRenamed("id", "offset")
        .withColumn("date", F.date_sub(F.current_date(), F.col("offset").cast("int")))
        .select("date")
    )


def _compute_sanctions_decay(sanctions, counterparty_dates):
    """Sanctions signal: 1.0 at hit date, exponential decay with 90-day half-life."""
    HALF_LIFE_DAYS = 90.0
    decay_rate = F.log(F.lit(2.0)) / F.lit(HALF_LIFE_DAYS)

    return (
        sanctions
        .alias("s")
        .join(
            counterparty_dates.alias("d"),
            (F.col("s.counterparty_id") == F.col("d.counterparty_id"))
            & (F.col("s.effective_date") <= F.col("d.date")),
            "inner",
        )
        .withColumn("days_since", F.datediff(F.col("d.date"), F.col("s.effective_date")))
        .withColumn("decay", F.exp(-decay_rate * F.col("days_since")))
        .groupBy(F.col("d.counterparty_id").alias("counterparty_id"),
                  F.col("d.date").alias("date"))
        .agg(F.coalesce(F.max("decay"), F.lit(0.0)).alias("sanctions_signal"))
    )


def _compute_media_rolling_count(adverse_media, counterparty_dates, window: int):
    """Adverse-media signal: log-scaled rolling-window mention count."""
    return (
        adverse_media
        .alias("am")
        .join(
            counterparty_dates.alias("d"),
            (F.col("am.counterparty_id") == F.col("d.counterparty_id"))
            & (F.col("am.mention_date") <= F.col("d.date"))
            & (F.col("am.mention_date") >= F.date_sub(F.col("d.date"), window - 1)),
            "inner",
        )
        .groupBy(F.col("d.counterparty_id").alias("counterparty_id"),
                  F.col("d.date").alias("date"))
        .agg(F.count("*").alias("mention_count"))
        .withColumn(
            "media_signal",
            F.least(F.log1p(F.col("mention_count")) / F.lit(5.0), F.lit(1.0)),
        )
        .select("counterparty_id", "date", "media_signal")
    )


def _compute_transaction_zscore(transactions, counterparty_dates, window: int):
    """Transaction-anomaly signal: |z-score| of daily volume vs rolling-window baseline."""
    daily_vol = (
        transactions
        .groupBy("counterparty_id",
                  F.col("transaction_date").alias("date"))
        .agg(F.sum("volume_usd").alias("daily_volume"))
    )
    w = (Window
         .partitionBy("counterparty_id")
         .orderBy("date")
         .rowsBetween(-(window - 1), -1))
    return (
        daily_vol
        .withColumn("rolling_mean", F.avg("daily_volume").over(w))
        .withColumn("rolling_std", F.stddev("daily_volume").over(w))
        .withColumn(
            "z_score",
            F.when(F.col("rolling_std") > 0,
                    F.abs((F.col("daily_volume") - F.col("rolling_mean"))
                           / F.col("rolling_std")))
             .otherwise(F.lit(0.0)),
        )
        .withColumn(
            "transaction_signal",
            F.least(F.col("z_score") / F.lit(5.0), F.lit(1.0)),
        )
        .select("counterparty_id", "date", "transaction_signal")
    )


def _compute_kyc_freshness(counterparty, counterparty_dates):
    """KYC freshness signal: 0.0 immediately after refresh, 1.0 at 18 months stale."""
    KYC_STALE_DAYS = 540.0  # 18 months
    return (
        counterparty.select("counterparty_id", "last_kyc_refresh_date")
        .alias("k")
        .join(counterparty_dates.alias("d"),
              F.col("k.counterparty_id") == F.col("d.counterparty_id"),
              "inner")
        .withColumn(
            "days_since_kyc",
            F.datediff(F.col("d.date"), F.col("k.last_kyc_refresh_date")),
        )
        .withColumn(
            "kyc_signal",
            F.least(F.greatest(F.col("days_since_kyc") / F.lit(KYC_STALE_DAYS),
                                  F.lit(0.0)),
                     F.lit(1.0)),
        )
        .select(F.col("d.counterparty_id").alias("counterparty_id"),
                F.col("d.date").alias("date"),
                "kyc_signal")
    )
