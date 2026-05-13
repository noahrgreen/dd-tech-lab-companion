# Foundry Article 001 — Companion Artifacts

**Article:** Foundry Ontology Design for Counterparty Risk Investigations
**DD Tech Lab series:** Palantir Foundry for Due Diligence — Article 001 of 10
**Article URL:** [TBD on publication at sheepdogprosperitypartners.com]
**Artifact-bundle version:** v1.0 (2026-05-13)

## What's in this bundle

| Directory | Contents | Notes |
|-----------|----------|-------|
| `ontology_schema/` | Parseable YAML files for the Counterparty, Person, Transaction, and SanctionsHit object types plus UltimateBeneficialOwner and TransactedWith link types | These are illustrative ontology schemas; Foundry ontology objects are created via the Ontology Manager UI or the Foundry SDK, not by YAML ingest |
| `synthetic_data/` | CSV files with the synthetic counterparty C-SYN-12345 worked example: counterparty, ubo Person, adverse-media mentions, transactions | Fully synthetic — no real entities |
| `foundry_sdk_stubs/` | Python dataclass representations of the ontology objects | Runnable with Python 3.10+ stdlib only; illustrative shape, not actual Foundry SDK calls |
| `workshop_module/` | JSON specification of the Workshop investigator-card layout described in the article | Stub format — actual Workshop module export is JSON via the Foundry Workshop UI |
| `action_templates/` | YAML specification of the `ElevateRiskRating` ActionType | Stub format — actual Foundry ActionType definitions live in the Foundry platform |

## Reproduction steps

1. Open `synthetic_data/` CSVs in any spreadsheet or load via pandas:
   ```python
   import pandas as pd
   df = pd.read_csv('synthetic_data/counterparty.csv')
   ```
2. Run the Python stubs to materialize the example as in-memory objects:
   ```bash
   python3 foundry_sdk_stubs/run_worked_example.py
   ```
   (Stdlib only; no installs required.)
3. The Workshop and Action templates document the configuration shape; reproducing the actual investigator flow requires a Foundry deployment + Workshop module import + ActionType creation through the platform.

## Article cross-reference

This bundle accompanies the v1.3 release of the article. The article's YAML schema blocks, math notation, and worked example all resolve to artifacts in this bundle.

If you find a discrepancy between the article and these artifacts, the artifacts are canonical and the article will be corrected in the next revision.

---

**Prepared by Noah Green CPA CFE — 2026-05-13**
