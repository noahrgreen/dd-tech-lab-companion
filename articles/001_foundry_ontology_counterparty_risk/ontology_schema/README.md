# Ontology schema — Foundry Article 001

Parseable YAML documenting the object types, link types, and ActionTypes the article references.

## Files

| File | Contents |
|------|----------|
| `counterparty_risk_ontology.yaml` | Full ontology schema — 6 ObjectTypes (Counterparty + Person + Transaction + SanctionsHit + AdverseMediaMention + AuditEntry), 3 LinkTypes (UltimateBeneficialOwner + TransactedWith + OfficerOf), 1 ActionType (ElevateRiskRating) |

## What this is

Illustrative ontology schema documenting the data shape the article references. The YAML parses cleanly via PyYAML (`yaml.safe_load`); verify with:

```python
import yaml
data = yaml.safe_load(open('counterparty_risk_ontology.yaml'))
assert list(data.keys()) == ['ObjectTypes', 'LinkTypes', 'ActionTypes']
```

## What this is NOT

Foundry ontology objects are created through the Ontology Manager UI or the Foundry SDK, not by direct YAML ingest. This file documents the SHAPE of the ontology; reproducing the actual ontology requires the corresponding Foundry-platform workflow (object-type creation via Ontology Manager, property mappings via Pipeline Builder, link-type registration, ActionType definition via the Actions UI).

## How to use

- Read alongside the article to verify the YAML schemas shown match the structure of `counterparty_risk_ontology.yaml`
- Use as the starting specification when building the corresponding Foundry ontology in an actual deployment
- Modify and extend for institution-specific use cases — add properties, sub-types, additional link types — without breaking the article's worked example
