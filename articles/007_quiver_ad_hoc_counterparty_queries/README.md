# Foundry Article 007 — Companion Bundle

**Title:** Quiver for Ad-Hoc Counterparty Queries — Lightweight Investigator Tooling Without a Full Workshop Build

**Series:** Palantir Foundry for Due Diligence
**Article ID:** SPP-DD-TECH-FOUNDRY-007
**Bundle status:** `validated_bundle`
**Prepared by:** Noah Green CPA CFE

## What this bundle contains

| Path | Purpose |
|---|---|
| `query_pack/quiver_counterparty_queries.yaml` | 5 saved Quiver queries: counterparty exposure to issuer (seed's worked example), sanctions overlap via beneficial ownership, adverse-media density quantile screen, rating-change volume by analyst (cross-refs Article 005's AuditEntry), portfolio risk distribution. Each query specifies target_object_class, filters, aggregations, visualization (primary + secondary primitives), parameters, share_link_default_permission, expected_runtime. |
| `graduation_criteria/quiver_to_workshop_checklist.md` | 7-criterion self-assessment for promoting recurring Quiver queries to Workshop applications: recurrence frequency, distinct user count, action depth, cognitive load, visualization complexity, audit/regulatory significance, performance/volume. Threshold: 4+ met = graduate. Includes cost-of-getting-it-wrong analysis in each direction. |
| `audit_considerations.md` | The load-bearing regulatory framing the seed flagged. Distinguishes what Quiver activity logs DO capture from what they DON'T; the failure mode of treating Quiver results as sufficient documentation; the snapshot discipline that bridges to Article 005's AuditEntry; mapping to SR 11-7 §V, FFIEC BSA/AML, PCAOB AS 2201. |
| `synthetic_data/counterparty_query_examples.csv` | The 5 queries at a glance: parameter inputs, expected result shape, runtime estimate, large-universe caveat. |
| `screenshot_equivalents.md` | 5 text-based Quiver UI surfaces: Instant-Query Mode, Query Result (bar chart + data table), Save-As-Parameterized, Share Link, Graduation-Criteria Self-Assessment. |
| `validation_notes.md` | Scope + known limits + reproducibility commands + framing reminder. |

## Quick start (validation reproducibility)

```bash
# YAML parses
python3 -c "
import yaml
qp = yaml.safe_load(open('query_pack/quiver_counterparty_queries.yaml'))
print(f\"{len(qp['queries'])} queries loaded\")"

# All 5 queries have required fields
python3 -c "
import yaml
qp = yaml.safe_load(open('query_pack/quiver_counterparty_queries.yaml'))
required = {'name', 'description', 'target_object_class', 'filters', 'aggregations', 'visualization', 'parameters'}
for q in qp['queries']:
    missing = required - set(q.keys())
    print(f\"{q['name']}: {'OK' if not missing else f'MISSING {missing}'}\")"
```

## Article-pattern summary

8 sections per seed: Workshop-vs-Quiver decision → instant-query mode → parameterized queries → visualization primitives → performance under large object sets → graduation criteria → audit considerations → worked example. This bundle implements the worked example end-to-end (5-query pack), the graduation checklist (7-criterion self-assessment with thresholds), and the audit-considerations regulatory framing.

## What's NOT in this bundle

- A live Quiver runtime. The YAML query specs mirror Quiver's saved-query structure but require re-keying into the Quiver UI.
- Institution-specific ontology adaptations. Queries reference generic ontology objects (Counterparty, BeneficialOwner, SanctionsHit, etc.); institution-specific schemas may differ.
- Quiver visualization rendering (the screen-equivalents show the layouts; actual rendering requires Quiver itself).
- Cross-platform Quiver-equivalent implementations. The patterns are general enough to map to Snowflake Streamlit-on-Snowflake or Databricks Lakeview, but the specific YAML schema is Foundry-shaped.

## Framing reminder

Quiver is for one-off questions; Workshop is for repeated workflows. The bundle's editorial center is the decision framework, not the Quiver vendor pitch. The graduation criteria are platform-agnostic — they apply to any ad-hoc-query / full-app graduation decision. Article 010 walks the cross-platform comparison explicitly.

The audit-considerations section is the load-bearing regulatory framing: Quiver activity logs alone are insufficient to reconstruct an investigation. Combined Quiver activity + Article 005 AuditEntry + analyst justification text is the audit-trail discipline the institution must maintain.
