# Foundry SDK stubs — Foundry Article 001

Illustrative Python `dataclass` representations of the ontology objects, link types, and Action shown in the article. **Not actual Foundry SDK calls** — Foundry ontology creation runs through the Ontology Manager UI or the real Foundry SDK with platform endpoints. These stubs let a reader run the worked example end-to-end in plain Python (3.10+ stdlib only) to verify the data shapes match the article's descriptions.

## Files

| File | Contents |
|------|----------|
| `ontology_classes.py` | dataclass definitions for Counterparty, Person, AdverseMediaMention, SanctionsHit, AuditEntry, UltimateBeneficialOwner, TransactedWith + the `elevate_risk_rating()` function + `cumulative_ownership()` math implementation |
| `run_worked_example.py` | Runs the article's worked counterparty-risk investigation end-to-end — instantiates the synthetic counterparty, computes the cumulative-ownership figure, invokes `elevate_risk_rating()`, prints the resulting state + AuditEntry |

## Run

```bash
cd articles/001_foundry_ontology_counterparty_risk/foundry_sdk_stubs/
python3 run_worked_example.py
```

No dependencies beyond Python 3.10 stdlib. Output matches the article's worked-example walkthrough.

## What this is NOT

- Not a Palantir SDK reference implementation
- Not a runnable Foundry deployment (no platform endpoints)
- Not production-grade — no persistence, no permissions, no platform audit-log integration
- Not a substitute for actual Foundry ontology design done through the Ontology Manager UI / SDK with institutional review and governance
