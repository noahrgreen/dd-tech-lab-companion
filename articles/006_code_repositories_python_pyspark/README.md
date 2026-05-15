# Foundry Article 006 — Companion Bundle

**Title:** Code Repositories in Foundry — When to Embed Python / PySpark in the Pipeline (and When to Stay in Pipeline Builder)

**Series:** Palantir Foundry for Due Diligence
**Article ID:** SPP-DD-TECH-FOUNDRY-006
**Bundle status:** `validated_bundle`
**Prepared by:** Noah Green CPA CFE

## What this bundle contains

| Path | Purpose |
|---|---|
| `transforms/pyspark_silver_to_gold.py` | Full PySpark transform implementing the seed's worked example: `@transform` decorator, three Inputs (silver_resolved, sanctions, adverse_media), one Output (Counterparty ontology dataset), window function for most-recent-sanctions-per-counterparty, 90-day adverse-media density aggregation, three audit-metadata columns (pipeline_run_id, transform_version, computed_at). Includes a pure-Spark variant for pytest. |
| `tests/test_silver_to_gold.py` | 7 pytest contract tests: counterparty coverage, sanctions window function, out-of-window drop, no-sanctions null case, adverse-media density, no-adverse-media coalesce-to-zero, audit-metadata always present + idempotent. Uses synthetic Spark DataFrames via fixtures. |
| `decision_matrix/pipeline_vs_code_repo_matrix.csv` | 18-criterion comparison: when to use Pipeline Builder (no-code) vs. Code Repository (PySpark). Each row gives a one-sentence rationale. |
| `ci_cd/foundry_code_repo_ci_template.yaml` | 7-stage CI/CD template: lint → unit_test → integration_test → security_scan → foundry_build → staging_deploy → manual_approval_gate → production_deploy. Dual-approval gate for gold-layer regulated-ontology writers. |
| `performance_notes.md` | Production-scale failure modes (skew, partition imbalance, shuffle bloat) with concrete mitigation code (salting, repartition-before-join, broadcast hints) + pre-production gate criteria. Addresses the seed's "what happens at 100-million-row scale" risk. |
| `requirements.txt` | pyspark + pytest (the project's Python deps). |
| `screenshot_equivalents.md` | 4 text-based Foundry UI renderings: Code Repository Browser, Transform File View, Build Result, Pipeline Builder Dataset Dependency View. |
| `validation_notes.md` | Scope + known limits + reproducibility commands. |

## Quick start (validation reproducibility)

```bash
# Module imports cleanly (stubs Foundry-only types so it works locally)
python3 -c "
import sys
sys.path.insert(0, 'transforms')
import pyspark_silver_to_gold
print('imports OK; version =', pyspark_silver_to_gold.TRANSFORM_VERSION)"

# pytest contract tests (requires pyspark + pytest)
pytest tests/ -v --tb=short
# Expected: 7 passed
```

## Article-pattern summary

8 sections per seed: 80/20 rule of Foundry transforms → Code Repository project structure → dependency management → PySpark patterns for DD → testing harness → CI/CD pattern → mixed-pipeline problem → worked example. This bundle implements the worked example end-to-end (transform + tests + decision matrix + CI/CD template + performance notes) and demonstrates the hybrid Pipeline-Builder-plus-Code-Repo pattern via the dependency-DAG screen equivalent.

## What's NOT in this bundle

- A live Foundry deployment. The `@transform` decorator + Input/Output API are Foundry-specific; the module stubs them for local imports.
- Institution-specific CI platform configuration. The CI/CD template uses generic GitLab/GitHub CI keys; adapt to actual platform (Jenkins, CircleCI, etc.).
- Performance-tuning thresholds calibrated to the institution's dataset. `performance_notes.md` gives the patterns; `N_SALT = 50` and `target_partitions = 5000` are placeholders pending institutional tuning.
- The Article 008 streaming-aggregation pattern for counterparty universes > 500M. The architecture-escalation note in performance_notes.md flags the boundary.

## Framing reminder

The PySpark code is portable Spark; the `@transform` decorator + Input/Output API are the Foundry value-add. Practitioners can reuse the PySpark patterns on Snowflake (via Snowpark) or Databricks (via PySpark in notebooks) with minor adjustments — Article 010 (platform tradeoff framework) walks this comparison explicitly.
