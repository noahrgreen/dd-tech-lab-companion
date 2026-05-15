
# Knowledge Graphs Article 001 — Companion Artifacts

**Article:** From Beneficial-Ownership Lists to Cypher: A Practical Knowledge-Graph Setup for DD
**Series:** Knowledge Graphs / Neo4j
**Artifact bundle version:** v1.0 (2026-05-14)

## Included artifacts

- `synthetic_data/synthetic_ownership_generator.py` — deterministic generator lifted from the article
- `synthetic_data/ownership_synthetic.csv` — generated dataset used by the Cypher loads
- `load_queries/pass1_person_owners.cypher` — person-owner load
- `load_queries/pass2_entity_owners.cypher` — entity-owner load
- root-level compatibility copy: `/ownership_synthetic.csv`

The synthetic dataset uses the article's fixed seed and keeps `TARGET_ENTITY = "E-0042"` as the worked-example entity.
