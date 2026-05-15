# Foundry Article 009 — Validated Companion Bundle

This validated bundle implements the ontology pattern described in the article seed: Person, Entity, Jurisdiction, and officer/control relationships with temporal ownership properties, disclosure-source provenance, and as-of-date traversal queries.

## Bundle contents
- `ontology_schema/beneficial_ownership_ontology.yaml` — object/link taxonomy with temporal and provenance properties
- `synthetic_data/jurisdictions.csv` — disclosure-regime dimension table
- `synthetic_data/persons.csv` — synthetic beneficial-owner and officer population
- `synthetic_data/entities.csv` — synthetic bank-group counterparty entities
- `synthetic_data/ownership_links.csv` — temporal OWNS links
- `synthetic_data/officer_links.csv` — OFFICER_OF links
- `synthetic_data/registration_links.csv` — REGISTERED_IN links
- `queries/beneficial_ownership_path_queries.cypher` — traversal starter queries
- `harmonization_rules.yaml` — cross-jurisdiction conflict-resolution rules
- `validation_notes.md` — validation scope and limits
