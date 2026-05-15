"""Pytest contract tests for silver_to_gold_counterparty transform.

Tests the pure-Spark variant (compute_counterparty_gold_pure) which has no
Foundry decorator. The decorated version is identical except for the
Input/Output wiring, which is exercised by Foundry-side integration tests.

Run:
    pytest tests/test_silver_to_gold.py -v
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import (StructType, StructField, StringType,
                                IntegerType, DateType)

# Make the transforms module importable
sys.path.insert(0, str(Path(__file__).parent.parent / "transforms"))
from pyspark_silver_to_gold import (
    compute_counterparty_gold_pure,
    TRANSFORM_VERSION,
)


@pytest.fixture(scope="module")
def spark():
    s = (SparkSession.builder
         .master("local[2]")
         .appName("test_silver_to_gold")
         .config("spark.sql.shuffle.partitions", "2")
         .getOrCreate())
    yield s
    s.stop()


@pytest.fixture
def silver_resolved(spark):
    schema = StructType([
        StructField("counterparty_id", StringType()),
        StructField("legal_name", StringType()),
        StructField("jurisdiction", StringType()),
    ])
    return spark.createDataFrame(
        [
            ("CP-001", "Alpha Corp", "US"),
            ("CP-002", "Beta Holdings", "SG"),
            ("CP-003", "Gamma Ltd", "UK"),
            ("CP-004", "Delta GmbH", "DE"),
        ],
        schema,
    )


@pytest.fixture
def sanctions(spark):
    schema = StructType([
        StructField("counterparty_id", StringType()),
        StructField("sanctions_list_id", StringType()),
        StructField("effective_date", DateType()),
    ])
    return spark.createDataFrame(
        [
            # CP-002 has two sanctions hits; most recent should win
            ("CP-002", "OFAC-SDN-2024", date(2025, 6, 1)),
            ("CP-002", "OFAC-SDN-2026", date(2026, 1, 10)),
            # CP-003 has a sanctions hit OUTSIDE the 365-day window — should drop
            ("CP-003", "OFAC-SDN-OLD", date(2024, 1, 1)),
            # CP-001 has one in-window hit
            ("CP-001", "EU-FROZEN", date(2026, 4, 15)),
        ],
        schema,
    )


@pytest.fixture
def adverse_media(spark):
    schema = StructType([
        StructField("counterparty_id", StringType()),
        StructField("mention_date", DateType()),
    ])
    return spark.createDataFrame(
        [
            # CP-001: 5 mentions inside 90-day window
            *[("CP-001", date(2026, 5, 1)) for _ in range(5)],
            # CP-002: 2 inside, 3 OUTSIDE 90-day window (should not be counted)
            ("CP-002", date(2026, 4, 1)),
            ("CP-002", date(2026, 3, 1)),
            *[("CP-002", date(2025, 1, 1)) for _ in range(3)],
            # CP-004: no mentions at all → coalesced to 0
        ],
        schema,
    )


def test_gold_includes_all_counterparties(spark, silver_resolved, sanctions, adverse_media):
    gold = compute_counterparty_gold_pure(silver_resolved, sanctions, adverse_media)
    assert gold.count() == 4, "all silver_resolved rows survive the left joins"
    ids = {row.counterparty_id for row in gold.collect()}
    assert ids == {"CP-001", "CP-002", "CP-003", "CP-004"}


def test_sanctions_most_recent_wins(spark, silver_resolved, sanctions, adverse_media):
    gold = compute_counterparty_gold_pure(silver_resolved, sanctions, adverse_media)
    cp_002 = gold.filter("counterparty_id = 'CP-002'").collect()[0]
    assert cp_002["sanctions_list_id"] == "OFAC-SDN-2026", \
        "window function picks the most recent hit per counterparty"


def test_sanctions_outside_window_dropped(spark, silver_resolved, sanctions, adverse_media):
    gold = compute_counterparty_gold_pure(silver_resolved, sanctions, adverse_media)
    cp_003 = gold.filter("counterparty_id = 'CP-003'").collect()[0]
    assert cp_003["sanctions_list_id"] is None, \
        "365-day filter drops out-of-window hits before join"


def test_no_sanctions_yields_null(spark, silver_resolved, sanctions, adverse_media):
    gold = compute_counterparty_gold_pure(silver_resolved, sanctions, adverse_media)
    cp_004 = gold.filter("counterparty_id = 'CP-004'").collect()[0]
    assert cp_004["sanctions_list_id"] is None


def test_adverse_media_density_counts_in_window(spark, silver_resolved, sanctions, adverse_media):
    gold = compute_counterparty_gold_pure(silver_resolved, sanctions, adverse_media)
    rows = {r.counterparty_id: r for r in gold.collect()}
    assert rows["CP-001"]["mention_count_90d"] == 5
    assert rows["CP-002"]["mention_count_90d"] == 2, "out-of-window mentions dropped"


def test_no_adverse_media_coalesces_to_zero(spark, silver_resolved, sanctions, adverse_media):
    gold = compute_counterparty_gold_pure(silver_resolved, sanctions, adverse_media)
    cp_004 = gold.filter("counterparty_id = 'CP-004'").collect()[0]
    assert cp_004["mention_count_90d"] == 0, \
        "coalesce(mention_count_90d, 0) replaces nulls with zero"


def test_audit_metadata_columns_present(spark, silver_resolved, sanctions, adverse_media):
    gold = compute_counterparty_gold_pure(
        silver_resolved, sanctions, adverse_media, run_id="test_run_42")
    rows = gold.collect()
    for row in rows:
        assert row["pipeline_run_id"] == "test_run_42"
        assert row["transform_version"] == TRANSFORM_VERSION
        assert row["computed_at"] is not None, \
            "audit metadata is non-optional on every output row"


def test_idempotent_under_repeat_runs(spark, silver_resolved, sanctions, adverse_media):
    # Audit metadata changes (computed_at, run_id) but business-logic columns are stable
    g1 = compute_counterparty_gold_pure(silver_resolved, sanctions, adverse_media, "r1")
    g2 = compute_counterparty_gold_pure(silver_resolved, sanctions, adverse_media, "r1")
    biz_cols = [c for c in g1.columns if c not in ("computed_at",)]
    r1 = {r.counterparty_id: tuple(r[c] for c in biz_cols) for r in g1.collect()}
    r2 = {r.counterparty_id: tuple(r[c] for c in biz_cols) for r in g2.collect()}
    assert r1 == r2, "business-logic output is deterministic given same inputs"
