# Validation Notes — Article 006 Companion Bundle

## Validation scope

- **PySpark transform** (transforms/pyspark_silver_to_gold.py) implements the seed's worked example with the `@transform` decorator, three Inputs (silver_resolved, sanctions, adverse_media), one Output (Counterparty ontology dataset). Body includes window function for most-recent-sanctions-per-counterparty (365-day lookback), 90-day adverse-media density aggregation, three audit-metadata columns (pipeline_run_id, transform_version, computed_at). Foundry-specific imports are wrapped in try/except so the module is locally importable.
- **Pure-Spark variant** (`compute_counterparty_gold_pure`) shares the business logic but takes plain DataFrames — allows pytest to exercise the logic without a live Foundry runtime.
- **pytest contract tests** (tests/test_silver_to_gold.py): 7 test cases — covers (1) all counterparties survive the left joins; (2) sanctions window function picks most-recent hit; (3) out-of-365-day-window sanctions drop; (4) no-sanctions case yields null; (5) adverse-media counts respect 90-day window; (6) no-adverse-media coalesces to zero; (7) audit metadata always present and idempotent across re-runs.
- **Decision matrix** (decision_matrix/pipeline_vs_code_repo_matrix.csv): 18 criteria covering schema mapping, date filtering patterns, windowing, joins (simple + array-typed), conditional aggregations, custom string-parsing, schema-drift handling, ML inference, performance tuning, audit metadata, testing/CI patterns, debuggability, analyst-editability, onboarding time. Each row labels whether Pipeline Builder or Code Repo is preferred plus a one-sentence rationale.
- **CI/CD template** (ci_cd/foundry_code_repo_ci_template.yaml): 7-stage pipeline (lint → unit_test → integration_test → security_scan → foundry_build → staging_deploy → manual_approval_gate → production_deploy) with explicit dual-approval gate for gold-layer regulated-ontology writers and post-deploy reconciliation note that connects to Article 005's TransformChangeEntry.
- **Performance notes** (performance_notes.md): Production-scale failure modes (skew, partition imbalance, shuffle bloat) with concrete mitigation code (salting for skew, repartition-before-join, broadcast hints) and pre-production gate criteria. Addresses the seed's "what happens at 100-million-row scale" risk note.

## Validation reproducibility

```bash
# Module imports cleanly
python3 -c "
import sys
sys.path.insert(0, 'transforms')
import pyspark_silver_to_gold
print('imports OK; version =', pyspark_silver_to_gold.TRANSFORM_VERSION)"

# pytest passes (requires pyspark + pytest installed)
cd ./tests && pytest test_silver_to_gold.py -v --tb=short
# Expected: 7 passed
```

## Known limits

- The PySpark transform is portable Spark code; the `@transform` decorator + Input/Output API are Foundry-specific. Running the decorated version outside Foundry requires the `transforms.api` library (stubbed in the module to allow local imports).
- The pytest suite uses local Spark (`local[2]`) — production deployments tune for the cluster's resource shape per `performance_notes.md`.
- The CI/CD template is illustrative — adapt the `runner`/`image`/`stages` keys to the institution's actual CI platform (GitLab CI, GitHub Actions, Jenkins, etc.).
- Performance notes mitigations (salting, broadcast hints) are pattern-level; specific thresholds (`N_SALT = 50`, `target_partitions = 5000`) require tuning per the institution's specific dataset shape.
- The transform does not implement the Article 008 streaming-aggregation pattern; for counterparty universes > 500M the architecture should be reconsidered (see performance_notes.md "When to escalate beyond Spark").

## Framing discipline reminder

Article 006 is the most technical article in the Foundry sub-series. The
PySpark code shown is portable Spark; only the `@transform` decorator and
the Input/Output API are Foundry-specific. The Foundry value-add is the
integration patterns (decorator + audit metadata + Pipeline Builder
dependency wiring), not the Spark code itself. Practitioners can reuse the
PySpark patterns on Snowflake (via Snowpark) or Databricks (via PySpark in
notebooks) with minor adjustments — the architecture comparison in Article
010 walks this surface explicitly.
