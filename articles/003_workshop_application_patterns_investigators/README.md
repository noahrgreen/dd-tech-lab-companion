# Foundry Article 003 — Validated Companion Bundle

This validated bundle implements the artifact shape described in the article seed: a single-pane-of-glass Workshop layout, action templates that force state changes through the Actions framework, a deterministic synthetic 5,000-counterparty dataset generator, and screenshot-equivalent markdown that documents the worked-example surfaces for readers who cannot access a live Workshop instance.

## Bundle contents
- `workshop_module/workshop_layout.yaml` — article-faithful Workshop layout spec
- `action_templates/investigator_actions.yaml` — actions with visibility, required fields, and audit-trail hooks
- `synthetic_data/counterparties.csv` — generated 5,000-counterparty object-card surface
- `synthetic_data/relationships.csv` — top-line relationship graph edges for the worked example
- `synthetic_data/time_series_metrics.csv` — monthly transaction-volume metrics for contextual navigation
- `screenshot_equivalents.md` — prose equivalents of the screenshots referenced in the article
- `validation_notes.md` — validation scope and limits
- `tools/generate_counterparty_demo_data.py` — deterministic data generator
