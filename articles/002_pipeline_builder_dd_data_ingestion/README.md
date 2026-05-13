# Foundry Article 002 — Companion Artifacts

**Article:** Pipeline Builder for DD Data Ingestion — Connecting Bank-Internal Systems to the Ontology Layer
**DD Tech Lab series:** Palantir Foundry for Due Diligence — Article 002 of 10
**Article URL:** [TBD on publication at sheepdogprosperitypartners.com]
**Artifact-bundle version:** v1.0 (2026-05-13)

## What's in this bundle

| File / Directory | Contents | Notes |
|-----------------|----------|-------|
| `pipeline_template.yaml` | Full four-layer (bronze / silver / gold / ontology-projection) pipeline declaration with conformance, idempotency, and schema-drift policy | Parseable YAML — verify with `yaml.safe_load`. Illustrative pipeline shape; actual Foundry pipelines are configured through Pipeline Builder UI |
| `entity_resolution_rules.yaml` | Deterministic-first, probabilistic-fallback entity-resolution rule set with composite-score thresholds and review-flag band | Parseable YAML — verify with `yaml.safe_load` |
| `synthetic_data/source_a_core_banking.csv` | Bronze-layer extract from `Core Banking System A` (illustrative source-system category) | 5 records, including a duplicate (CB-001 / CB-004) to test entity resolution |
| `synthetic_data/source_b_kyc_platform.csv` | Bronze-layer extract from `KYC Platform B` | 5 records with LEI identifiers |
| `synthetic_data/source_c_crm_master.csv` | Bronze-layer extract from `CRM / Counterparty Master C` | 6 records, one with no registration_id (tests fallback path) |
| `synthetic_data/silver_counterparties_resolved.csv` | Silver-layer output after entity resolution | 6 resolved entities from 16 source records; shows deterministic + probabilistic match outcomes |
| `synthetic_data/gold_counterparty_ontology.csv` | Gold-layer output with audit metadata | 6 records, each with `pipeline_run_id`, `source_extract_date`, `transform_version`, `computed_at` |
| `transforms/silver_to_gold_transform.py` | Illustrative PySpark transform for the silver→gold materialization | Documents the shape; production deployment requires Foundry Code Repositories (Article 006) |

## Reproduction steps

1. Verify the YAMLs parse:
   ```python
   import yaml
   yaml.safe_load(open('pipeline_template.yaml'))
   yaml.safe_load(open('entity_resolution_rules.yaml'))
   ```

2. Inspect the bronze→silver entity-resolution outcome:
   ```python
   import pandas as pd
   src_a = pd.read_csv('synthetic_data/source_a_core_banking.csv')
   src_b = pd.read_csv('synthetic_data/source_b_kyc_platform.csv')
   src_c = pd.read_csv('synthetic_data/source_c_crm_master.csv')
   silver = pd.read_csv('synthetic_data/silver_counterparties_resolved.csv')
   # 16 bronze records resolve to 6 silver entities; SILV-1001 absorbs four source rows
   ```

3. Read `transforms/silver_to_gold_transform.py` to see the audit-metadata pattern that gold-layer transforms apply.

## What this bundle is NOT

- Not a runnable Foundry Code Repository deployment — the `@transform` decorator and Input/Output classes are platform-defined
- Not a Pipeline Builder UI export — the YAML pipeline template documents shape, not literal config syntax
- Not a production entity-resolution implementation — the rule-set parameters are illustrative; production institutions tune against their own corpus

## Article cross-reference

This bundle accompanies the v1 release of Foundry Article 002. The article's bronze/silver/gold pattern, source-system connector discussion, entity-resolution rule structure, idempotency requirements, schema-drift policy, audit-metadata columns, and worked three-source example all resolve to artifacts in this bundle.

Article 006 (Code Repositories) walks the actual PySpark deployment pattern that the illustrative transform here gestures toward.

---

**Prepared by Noah Green CPA CFE — 2026-05-13**
