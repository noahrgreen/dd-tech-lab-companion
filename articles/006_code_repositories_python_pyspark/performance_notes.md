# Performance Notes — silver_to_gold_counterparty at scale

The worked example in `transforms/pyspark_silver_to_gold.py` is correct under
small inputs. At production scale (50-100M counterparties × multi-billion
silver-layer rows), the same logic will encounter the three classic Spark
failure modes: skew, partition imbalance, and shuffle bloat. Address them
before promoting the transform to production.

## Skew

**Symptom.** A small number of `counterparty_id` values have far more
`adverse_media_mentions` or `sanctions_hits` rows than others (e.g., a
global megacap counterparty with 50K mentions vs. a mid-market counterparty
with 5). The `groupBy("counterparty_id")` aggregation produces partition
imbalance — one or two tasks take 100× the time of the median task.

**Detection.** Spark UI → Stage view → look for tasks where the input-size
distribution has a long right tail. Stage duration dominated by one or two
straggler tasks confirms skew.

**Mitigation.**

```python
# Salt the join key for the heavy partitions, then aggregate twice.
from pyspark.sql import functions as F

# Step 1: Salt heavy counterparties
heavy_counterparties = (
    adverse_media
    .groupBy("counterparty_id")
    .agg(F.count("*").alias("mention_count"))
    .filter(F.col("mention_count") > 10_000)  # threshold per institution
    .select("counterparty_id")
    .collect()
)
heavy_set = {r.counterparty_id for r in heavy_counterparties}

N_SALT = 50  # tune per skew severity
salted = adverse_media.withColumn(
    "salt",
    F.when(F.col("counterparty_id").isin(heavy_set),
           (F.rand() * N_SALT).cast("int"))
    .otherwise(F.lit(0))
)

# Step 2: Partial aggregation on (counterparty_id, salt)
partial = (salted
    .filter(F.col("mention_date") >= F.date_sub(F.current_date(), 90))
    .groupBy("counterparty_id", "salt")
    .agg(F.count("*").alias("partial_count"))
)

# Step 3: Final aggregation collapses the salt
media_density = (partial
    .groupBy("counterparty_id")
    .agg(F.sum("partial_count").alias("mention_count_90d"))
)
```

The two-stage aggregation distributes work across N_SALT partitions per
heavy counterparty, eliminating the long-tail straggler.

## Partition imbalance

**Symptom.** `spark.sql.shuffle.partitions` default of 200 is wrong for
the dataset size. Either too few (each partition holds gigabytes; OOM) or
too many (millions of tiny partitions; task scheduling overhead dominates).

**Detection.** Spark UI → Stage view → task input-size distribution. Median
task input size should be 100-500MB for steady-state Spark performance. If
median is < 10MB or > 2GB, repartition.

**Mitigation.**

```python
# Compute a target partition count: total input size ÷ ~200MB per partition
# For a 1TB silver_resolved input → ~5000 partitions
target_partitions = 5000

silver_resolved = silver_resolved.repartition(target_partitions, "counterparty_id")
```

Hash-partitioning on `counterparty_id` BEFORE the join makes the join
itself a partition-local operation (no shuffle), which collapses shuffle
bloat to near-zero for the join stage.

## Shuffle bloat

**Symptom.** The job moves 10× more data over the network than the input
size justifies. Wide transforms (joins, groupBy) shuffle row-by-row across
the cluster.

**Detection.** Spark UI → Stage view → Shuffle Read / Shuffle Write columns.
Compare to input dataset size. Shuffle volumes > 3× input size indicate
opportunity for pre-shuffle filtering or broadcast joins.

**Mitigation.**

```python
# 1. Filter BEFORE joining (predicate pushdown)
# Already in the transform: 365-day filter applied to sanctions BEFORE join.
# Verify the Spark plan via .explain() shows filter pushdown to source.

# 2. Broadcast small dimensions
from pyspark.sql.functions import broadcast

# sanctions_active is typically < 1% of silver_resolved (only counterparties
# WITH active sanctions). Broadcast it.
gold = (
    silver_resolved
    .join(broadcast(sanctions_active), "counterparty_id", "left")
    .join(broadcast(media_density), "counterparty_id", "left")
    ...
)
```

Broadcast joins skip the shuffle entirely for the small side. Rule of thumb:
broadcast if the small side fits in ~10% of executor memory (typically
< 1GB).

## Memory tuning

Production deployment of this transform on a 50-100M counterparty universe
typically needs:

- Executor memory: 8-16GB per executor
- Executor cores: 4-8
- Number of executors: scale to ~target_partitions / (executor_cores × 2)
- Driver memory: 4-8GB (the worked example doesn't `.collect()` to driver,
  so driver memory needs are modest; the skew mitigation's `.collect()`
  of heavy-counterparty IDs is small)

## When to escalate beyond Spark

For counterparty universes > 500M with rich link metadata, the transform
should be re-architected:

- Pre-compute media_density as a streaming aggregation maintained by a
  separate pipeline (Foundry Streaming or Kafka + materialized view),
  rather than full-scan-aggregating every pipeline run.
- Pre-compute sanctions_active similarly; sanctions list changes are
  daily-rate, not pipeline-run-rate.
- The gold-layer transform then becomes a join-only step on
  pre-aggregated dimensions, which is partition-local.

This re-architecture is beyond the scope of Article 006; see Article 008
(Time Series in Foundry) for the streaming-aggregation pattern.

## Pre-production gates

Before promoting `silver_to_gold_counterparty@v2.1` to production, the
data-engineering team must:

- Run the transform on at least three different scale tiers: 1M, 10M, and
  representative-of-production. Record wall time, shuffle volume, and peak
  executor memory at each tier.
- Confirm the skew mitigation is in place if any heavy counterparty
  exceeds the threshold.
- Confirm broadcast hints are correctly applied. The Spark plan should show
  BroadcastHashJoin for the sanctions and media_density joins, not
  SortMergeJoin.
- Verify the audit-metadata columns are non-null on every output row
  (pytest already covers this; verify it holds at production scale).
