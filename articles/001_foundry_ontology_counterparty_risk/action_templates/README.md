# Action templates — Foundry Article 001

YAML specifications for the ActionTypes the article references.

## Files

| File | ActionType |
|------|-----------|
| `elevate_risk_rating.yaml` | Elevates a Counterparty's risk_rating with required justification + supporting-evidence ObjectSet; creates an immutable AuditEntry |

## What these are

Illustrative ActionType specifications documenting the inputs, side effects, and post-execution hooks the article describes. Actual Foundry Actions are defined through the Actions UI in the Foundry platform; this YAML documents the SHAPE the article describes.

## Bypass-controls discipline

Every ActionType template here includes a `bypass_controls_note` reminding implementers that the Actions framework captures state changes that route through Actions only. Direct dataset edits, admin overrides, emergency backfills, and transform redeployments require separate audit treatment. Audit-trail completeness is an institutional discipline, not a platform guarantee. Foundry Article 005 walks this discipline in full.

## Subsequent ActionTypes

Forthcoming ActionTypes (referenced in Workshop module spec, not yet templated): `InitiateEnhancedDueDiligence`, `DismissSanctionsHit`. These will ship alongside subsequent Foundry sub-series articles.
