# Workshop module — Foundry Article 001

Illustrative Workshop module specification for the counterparty-risk-investigation single-pane-of-glass investigator surface described in the article.

**File:** `counterparty_risk_investigation_module.json`

## What this is

A JSON spec documenting the layout, components, conditional formatting, action wiring, and performance considerations of the Workshop module the article references. The format is illustrative — actual Foundry Workshop modules are JSON exports from the Workshop UI with platform-internal structure that this stub does not reproduce.

## What this maps to

- **Primary pane** — the Counterparty object card with header, AIP risk summary, and relationships sections
- **Secondary pane** — the contextual navigator that responds to primary-pane selection (transaction time series, ownership graph, sanctions full text, adverse-media article view)
- **Actions** — ElevateRiskRating, InitiateEnhancedDueDiligence, DismissSanctionsHit
- **Performance notes** — search-index strategy, pagination, lazy-loading, time-series aggregation

## Reproduction in a real Foundry deployment

1. Create the ontology objects from `ontology_schema/counterparty_risk_ontology.yaml` via the Ontology Manager UI
2. Load the synthetic data from `synthetic_data/*.csv` via Pipeline Builder
3. Define the ActionTypes from `action_templates/*.yaml` via the Actions UI
4. Build a Workshop module following the layout in `counterparty_risk_investigation_module.json` using Workshop's drag-and-drop UI
5. Configure AIP function `adverse_media_summary` with the grounding-and-citation discipline described in the article

Article 003 in the Foundry sub-series walks the Workshop application patterns in detail.
