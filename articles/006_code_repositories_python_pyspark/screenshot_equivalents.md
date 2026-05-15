# Screenshot Equivalents — Foundry Code Repositories

Text-based renderings of the Foundry Code Repository surfaces the article
walks. The bundle is portable (PySpark + pytest + YAML); these
screen-equivalents map the bundle artifacts to the Foundry UI.

## Code Repository Browser — `dd_ingestion` project

```
┌─ Code Repositories / dd_ingestion ────────────────────────────────────────────┐
│                                                                                │
│  ⌗ main          v2.1 (deployed)         3 commits ahead of staging            │
│  Owner:          data_engineering_lead                                         │
│  Last build:     2026-05-15 06:14 UTC  •  SUCCESS                              │
│                                                                                │
│  ┌─ Files ─────────────────────────────────────────────────────────────────┐ │
│  │  📂 transforms/                                                          │ │
│  │     📄 silver_to_gold_counterparty.py        v2.1   modified 2 days ago  │ │
│  │     📄 silver_to_gold_sanctions_aggregate.py v1.4   modified 1 wk ago    │ │
│  │     📄 bronze_to_silver_adverse_media.py     v3.0   modified 3 days ago  │ │
│  │  📂 tests/                                                               │ │
│  │     📄 test_silver_to_gold_counterparty.py                               │ │
│  │     📂 integration/                                                      │ │
│  │  📄 requirements.txt                                                     │ │
│  │  📄 .ci/foundry_pipeline.yaml                                            │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  [ View build history ▸ ]   [ View deployment audit ▸ ]   [ Open in IDE ▸ ]   │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Transform File View

```
┌─ silver_to_gold_counterparty.py ──────────────────────────────────────────────┐
│  v2.1   •   modified 2 days ago by data_engineering_lead                       │
│  Status: PRODUCTION  •  Last build: SUCCESS  •  PR-locked                      │
│                                                                                │
│  @transform(                                                                   │
│      output=Output("/dd/ontology/Counterparty"),                              │
│      silver_resolved=Input("/dd/silver/counterparties_resolved"),             │
│      sanctions=Input("/dd/silver/sanctions_hits"),                            │
│      adverse_media=Input("/dd/silver/adverse_media_mentions"),                │
│  )                                                                             │
│  def compute_counterparty_gold(ctx, silver_resolved, sanctions, adverse_...   │
│      ...                                                                       │
│                                                                                │
│  ┌─ Linked datasets ───────────────────────────────────────────────────────┐ │
│  │  Inputs:                                                                 │ │
│  │    /dd/silver/counterparties_resolved   (50.2M rows, updated daily)      │ │
│  │    /dd/silver/sanctions_hits            (840K rows, updated hourly)      │ │
│  │    /dd/silver/adverse_media_mentions    (12.4M rows, updated hourly)     │ │
│  │  Outputs:                                                                │ │
│  │    /dd/ontology/Counterparty            (50.2M rows, produced ~04:00)    │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  [ Run on staging ▸ ]   [ View last run ▸ ]   [ View dependency DAG ▸ ]       │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Build Result

```
┌─ Build: silver_to_gold_counterparty @ v2.1 ─ commit f4a8c1d ──────────────────┐
│                                                                                │
│  Started:   2026-05-15 06:14:02 UTC                                            │
│  Duration:  47s                                                                │
│  Status:    ✓ SUCCESS                                                          │
│                                                                                │
│  ┌─ Stage 1: lint ─────────────────────────────────────────────────────────┐ │
│  │  ✓ ruff       no issues                                                  │ │
│  │  ✓ black      no formatting changes needed                               │ │
│  │  ✓ mypy       no type errors                                             │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│  ┌─ Stage 2: unit_test ────────────────────────────────────────────────────┐ │
│  │  pytest tests/                                                            │ │
│  │  ✓ 7 passed in 12.4s                                                     │ │
│  │     test_gold_includes_all_counterparties                                │ │
│  │     test_sanctions_most_recent_wins                                      │ │
│  │     test_sanctions_outside_window_dropped                                │ │
│  │     test_no_sanctions_yields_null                                        │ │
│  │     test_adverse_media_density_counts_in_window                          │ │
│  │     test_no_adverse_media_coalesces_to_zero                              │ │
│  │     test_audit_metadata_columns_present                                  │ │
│  │     test_idempotent_under_repeat_runs                                    │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│  ┌─ Stage 3: integration_test ─────────────────────────────────────────────┐ │
│  │  ✓ 2 passed in 38.1s (against sampled 100K-row dataset slice)            │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  [ View full log ▸ ]   [ Deploy to staging ▸ ]                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Pipeline Builder Dataset Dependency View

```
┌─ Dataset: /dd/ontology/Counterparty ──────────────────────────────────────────┐
│                                                                                │
│  Producer:     Code Repository ⟶ dd_ingestion/silver_to_gold_counterparty.py  │
│                                  ↳ Build silver_to_gold_counterparty@v2.1     │
│                                                                                │
│  ┌─ Dependency DAG ────────────────────────────────────────────────────────┐ │
│  │                                                                          │ │
│  │   /dd/silver/counterparties_resolved ────┐                              │ │
│  │       (Pipeline Builder transform)        │                              │ │
│  │                                            │                              │ │
│  │   /dd/silver/sanctions_hits ───────────────┼──► silver_to_gold_count...  │ │
│  │       (Pipeline Builder transform)        │     (Code Repository)       │ │
│  │                                            │                              │ │
│  │   /dd/silver/adverse_media_mentions ──────┘                              │ │
│  │       (Pipeline Builder transform)                                       │ │
│  │                                            │                              │ │
│  │                                            ▼                              │ │
│  │                                  /dd/ontology/Counterparty               │ │
│  │                                            │                              │ │
│  │                                            ▼                              │ │
│  │                          [Workshop apps consume Counterparty]            │ │
│  │                                                                          │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  Note: 3 of 4 transforms are Pipeline Builder (the 80% no-code path); the     │
│  silver→gold transform is the 20% Code Repository case because of the         │
│  window function and broadcast-join performance tuning. Article 006 walks     │
│  the decision boundary explicitly.                                            │
└────────────────────────────────────────────────────────────────────────────────┘
```

The hybrid Pipeline-Builder-plus-Code-Repo pattern shown above is the
"mixed pipeline" the seed discusses in §7. It works when the Code Repo
portion is well-documented and PR-gated (which the CI/CD template enforces);
it produces the "20% nobody can debug" failure mode when ownership and
documentation discipline lapse.
