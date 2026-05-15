"""silver_to_gold_counterparty.py — PySpark transform for gold-layer Counterparty production.

Companion artifact for Foundry Article 006. Demonstrates the Code Repository
pattern for transforms that exceed Pipeline Builder's no-code envelope:
window functions, multi-source joins, dynamic-date filtering relative to
pipeline-run timestamp, and audit-metadata columns connecting each output
row back to the specific code version that produced it.

Lives in (production):
    /Code Repositories/dd_ingestion/transforms/silver_to_gold_counterparty.py

Triggered by:
    Pipeline Builder dataset dependency on silver.counterparties_resolved.

The `@transform` decorator and `Input`/`Output` symbols are Foundry-specific
(imported from `transforms.api`). The rest of the body is portable PySpark.
"""
from __future__ import annotations

# ─── Foundry-specific imports ───
# Stubbed here for portability; in a real Foundry Code Repo, these come from the
# Foundry-provided transforms library:
try:
    from transforms.api import transform, Input, Output  # type: ignore
except ImportError:  # local dev / pytest path — stub for static-analysis friendliness
    def transform(*args, **kwargs):  # noqa: D401
        def _wrap(fn):
            return fn
        return _wrap

    class _IO:
        def __init__(self, path: str):
            self.path = path

    Input = _IO
    Output = _IO

# ─── Portable PySpark imports ───
from pyspark.sql import functions as F, Window  # noqa: E402

TRANSFORM_VERSION = "silver_to_gold_counterparty@v2.1"


@transform(
    output=Output("/dd/ontology/Counterparty"),
    silver_resolved=Input("/dd/silver/counterparties_resolved"),
    sanctions=Input("/dd/silver/sanctions_hits"),
    adverse_media=Input("/dd/silver/adverse_media_mentions"),
)
def compute_counterparty_gold(ctx, silver_resolved, sanctions, adverse_media, output):
    """Produce gold-layer Counterparty ontology objects with link metadata.

    Joins three silver-layer inputs:
      - silver_resolved: the canonical Counterparty record set
      - sanctions: most-recent active sanctions hit per counterparty (365-day lookback)
      - adverse_media: 90-day adverse-media mention density per counterparty

    The transform adds three audit-metadata columns to every output row
    (pipeline_run_id, transform_version, computed_at) that connect the row
    to the specific build that produced it. These columns are how a DD
    workpaper later answers "which code generated this specific value".
    """
    # Most-recent sanctions hit per counterparty (365-day lookback)
    sanctions_active = (
        sanctions.dataframe()
        .filter(F.col("effective_date") >= F.date_sub(F.current_date(), 365))
        .withColumn(
            "rank",
            F.row_number().over(
                Window.partitionBy("counterparty_id").orderBy(F.col("effective_date").desc())
            ),
        )
        .filter(F.col("rank") == 1)
        .select("counterparty_id", "sanctions_list_id", "effective_date")
    )

    # 90-day adverse-media density per counterparty
    media_density = (
        adverse_media.dataframe()
        .filter(F.col("mention_date") >= F.date_sub(F.current_date(), 90))
        .groupBy("counterparty_id")
        .agg(F.count("*").alias("mention_count_90d"))
    )

    # Compose gold output with audit metadata
    gold = (
        silver_resolved.dataframe()
        .join(sanctions_active, "counterparty_id", "left")
        .join(media_density, "counterparty_id", "left")
        .withColumn(
            "mention_count_90d",
            F.coalesce(F.col("mention_count_90d"), F.lit(0)),
        )
        .withColumn("pipeline_run_id", F.lit(ctx.run_id))
        .withColumn("transform_version", F.lit(TRANSFORM_VERSION))
        .withColumn("computed_at", F.current_timestamp())
    )

    output.write_dataframe(gold)


# ─── Pure-Spark variant for local testing ───
# The version below has no Foundry decorator and accepts plain DataFrames.
# Importable into pytest without the Foundry runtime. Used by tests/.
def compute_counterparty_gold_pure(silver_resolved, sanctions, adverse_media,
                                    run_id: str = "test_run"):
    sanctions_active = (
        sanctions
        .filter(F.col("effective_date") >= F.date_sub(F.current_date(), 365))
        .withColumn(
            "rank",
            F.row_number().over(
                Window.partitionBy("counterparty_id").orderBy(F.col("effective_date").desc())
            ),
        )
        .filter(F.col("rank") == 1)
        .select("counterparty_id", "sanctions_list_id", "effective_date")
    )

    media_density = (
        adverse_media
        .filter(F.col("mention_date") >= F.date_sub(F.current_date(), 90))
        .groupBy("counterparty_id")
        .agg(F.count("*").alias("mention_count_90d"))
    )

    return (
        silver_resolved
        .join(sanctions_active, "counterparty_id", "left")
        .join(media_density, "counterparty_id", "left")
        .withColumn(
            "mention_count_90d",
            F.coalesce(F.col("mention_count_90d"), F.lit(0)),
        )
        .withColumn("pipeline_run_id", F.lit(run_id))
        .withColumn("transform_version", F.lit(TRANSFORM_VERSION))
        .withColumn("computed_at", F.current_timestamp())
    )
