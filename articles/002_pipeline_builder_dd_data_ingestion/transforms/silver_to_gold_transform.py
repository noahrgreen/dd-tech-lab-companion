"""
silver_to_gold_transform.py — Illustrative PySpark transform for the
                              gold-layer Counterparty production.

Companion artifact for: DD Tech Lab — Foundry Article 002
Status: Illustrative — NOT a runnable Foundry Code Repository deployment

In a real Foundry Code Repository, this transform lives at:
    /Code Repositories/dd_ingestion/transforms/silver_to_gold_counterparty.py

It is triggered by Pipeline Builder when the silver_counterparties_resolved
dataset updates. The @transform decorator and Input/Output objects are
Foundry-platform-specific; the structure below is the standard pattern
articulated in Article 006 of this sub-series.

The transform shown here demonstrates the four audit-metadata columns
(pipeline_run_id, source_extract_date, transform_version, computed_at) that
every gold-layer record carries per the article's discipline.
"""
from __future__ import annotations


# In actual Foundry deployment:
#     from transforms.api import transform, Input, Output
#     from pyspark.sql import functions as F, Window
#
# For this illustrative artifact, those imports are not needed — the function
# signature below documents the shape rather than running standalone.


# @transform(
#     output=Output("/dd/ontology/Counterparty"),
#     silver_resolved=Input("/dd/silver/counterparties_resolved"),
#     silver_kyc=Input("/dd/silver/kyc_status"),
#     silver_sanctions=Input("/dd/silver/sanctions_hits"),
#     silver_adverse_media=Input("/dd/silver/adverse_media_mentions"),
# )
def compute_counterparty_gold(ctx, silver_resolved, silver_kyc, silver_sanctions, silver_adverse_media):
    """
    Produce the gold-layer Counterparty ontology objects with audit metadata.

    Args:
        ctx: Foundry transform context. Provides ctx.run_id (current pipeline-run UUID)
             and ctx.run_timestamp (pipeline-run-context timestamp; used for any
             "now"-derived computation to maintain idempotency).
        silver_resolved: Input — the deduplicated silver counterparty dataset.
        silver_kyc: Input — KYC status by silver_counterparty_id.
        silver_sanctions: Input — active sanctions hits by silver_counterparty_id.
        silver_adverse_media: Input — adverse-media-mention links by silver_counterparty_id.

    Returns:
        A gold-layer DataFrame ready for ontology projection. Each row has
        the four audit-metadata columns: pipeline_run_id, source_extract_date,
        transform_version, computed_at.
    """

    # --- 1. Active sanctions: most recent hit per counterparty within 365-day lookback
    #     (illustrative — actual implementation uses Window functions)
    sanctions_active = "<window-function: row_number() over partition by counterparty_id order by effective_date desc, filtered to last 365d, rank = 1>"

    # --- 2. Adverse-media density: count of mentions in trailing 90 days
    media_density = "<count of silver_adverse_media filtered to mention_date >= ctx.run_timestamp - 90d, grouped by counterparty_id>"

    # --- 3. KYC freshness: latest KYC completion date by counterparty
    kyc_latest = "<select most-recent kyc_completion_date per counterparty_id from silver_kyc>"

    # --- 4. Gold materialization
    gold = (
        # Conceptual SQL/PySpark:
        # SELECT
        #     s.silver_counterparty_id AS counterparty_id,
        #     s.legal_name_canonical AS legal_name,
        #     s.jurisdiction_iso2 AS jurisdiction,
        #     s.risk_rating,
        #     k.kyc_completion_date AS last_kyc_refresh,
        #     ctx.run_id AS pipeline_run_id,
        #     ctx.source_extract_date,  -- from upstream bronze metadata
        #     'silver_to_gold@v2.1' AS transform_version,
        #     ctx.run_timestamp AS computed_at
        # FROM silver_resolved s
        # LEFT JOIN sanctions_active sa ON s.silver_counterparty_id = sa.counterparty_id
        # LEFT JOIN media_density md ON s.silver_counterparty_id = md.counterparty_id
        # LEFT JOIN kyc_latest k ON s.silver_counterparty_id = k.counterparty_id
        # WITH UPSERT semantics on counterparty_id primary key
        "<illustrative gold DataFrame; runnable equivalent in actual Foundry deployment>"
    )

    # --- 5. Asserts (production institutions add these as Foundry expectations):
    #     * gold.counterparty_id is non-null and unique
    #     * gold.jurisdiction matches ISO 3166-1 alpha-2 (length == 2, uppercase)
    #     * gold.risk_rating in {low, medium, high, critical}
    #     * gold.pipeline_run_id == ctx.run_id  (idempotency check)
    #     * gold.source_extract_date <= ctx.run_timestamp

    # output.write_dataframe(gold, upsert_key="counterparty_id")
    return gold


# ----------------------------------------------------------------------------
# Notes on running this in production
# ----------------------------------------------------------------------------
#
# 1. Deploy via Foundry Code Repositories with semantic version tagging
#    (transform_version baked into the gold-layer audit metadata).
#
# 2. The Pipeline Builder pipeline (see pipeline_template.yaml) triggers this
#    transform when silver datasets update; transform runs against the latest
#    silver state and upserts gold by counterparty_id.
#
# 3. Foundry expectations (assertion framework) catch schema or data violations
#    before they propagate to the ontology projection. Configure expectations
#    on every gold-layer column with a documented invariant.
#
# 4. The transform is idempotent: re-running against the same silver state
#    produces the same gold state (same audit-metadata columns, same upserts).
#    This is the precondition for back-fills and parallel-environment validation.
#
# 5. Bypass channels: direct gold-dataset writes via the Foundry UI, admin SQL
#    sessions, or manual CSV imports route AROUND this transform and ARE NOT
#    captured in the transform_version trail. The institution must address
#    bypass channels through permission policies and separate audit treatment.
#    See Foundry Article 005 for the Actions-framework discipline.
