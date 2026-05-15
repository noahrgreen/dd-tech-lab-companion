# Validation Notes — Article 007 Companion Bundle

## Validation scope

- **Quiver query pack** (query_pack/quiver_counterparty_queries.yaml): 5 saved queries covering the article's worked example + 4 additional patterns: counterparty exposure to specific issuer (seed's worked example), sanctions overlap via beneficial ownership, adverse-media density quantile screen, rating-change volume by analyst (cross-refs Article 005's AuditEntry), portfolio risk distribution. Each query specifies target_object_class, filters, aggregations, visualization (primary + secondary primitives), parameters (with type, default, prompt, validation), share_link_default_permission, expected_runtime.
- **Graduation criteria checklist** (graduation_criteria/quiver_to_workshop_checklist.md): 7-criterion self-assessment template — recurrence frequency, distinct user count, action depth, cognitive load, visualization complexity, audit/regulatory significance, performance/volume. Threshold: 4+ criteria met = graduate to Workshop. Includes worked examples of cost-of-getting-it-wrong in each direction.
- **Audit considerations** (audit_considerations.md): The load-bearing regulatory framing the seed flagged. Distinguishes what Quiver activity logs DO capture (query + parameters + user + timestamp + result count + share-link events) from what they DON'T (specific rows returned, analyst interpretation, downstream decisions). Explains the failure mode of treating Quiver results as sufficient documentation, the snapshot discipline that bridges to Article 005's AuditEntry, and the regulatory mapping (SR 11-7 §V, FFIEC BSA/AML, PCAOB AS 2201).
- **Synthetic data** (synthetic_data/counterparty_query_examples.csv): The 5 queries' expected inputs/outputs at a glance, with runtime estimates and large-universe caveats for performance-sensitive cases.

## Validation reproducibility

```bash
# YAML files parse
python3 -c "
import yaml
for p in ['query_pack/quiver_counterparty_queries.yaml']:
    yaml.safe_load(open(p))
    print(f'{p}: parses')"

# All 5 queries have required fields
python3 -c "
import yaml
qp = yaml.safe_load(open('query_pack/quiver_counterparty_queries.yaml'))
required = {'name', 'description', 'target_object_class', 'filters', 'aggregations', 'visualization', 'parameters'}
for q in qp['queries']:
    missing = required - set(q.keys())
    print(f\"{q['name']}: {'OK' if not missing else f'MISSING {missing}'}\")"
```

## Known limits

- Quiver is Foundry-proprietary; the YAML schema mirrors Quiver's saved-query structure but is not directly importable into Quiver via API. Re-keying into Quiver UI required.
- The 5 sample queries reference ontology objects (Counterparty, BeneficialOwner, SanctionsHit, AdverseMediaMention, AuditEntry, TransactedWith) that align with the broader DD Tech Lab series; the specific institution's ontology may differ.
- The graduation-criteria checklist is heuristic, not algorithmic. Specific score thresholds (4-of-7) are calibrated against typical institutional patterns; institution-specific calibration may shift the threshold.
- Audit_considerations.md captures the *pattern*; the specific Foundry activity-log retention policy is institution-configurable and may be longer or shorter than the typical 180-day-to-1-year range.

## Framing reminder (per seed)

Quiver is the right tool for one-off questions; Workshop is the right tool for repeated workflows. The bundle's editorial center is the decision framework, not the Quiver vendor pitch. The patterns (instant query, parameterized query, share-link, graduation criteria) are general — Snowflake Streamlit-on-Snowflake and Databricks Lakeview offer comparable ad-hoc-query surfaces, and the graduation criteria apply across platforms. Article 010 walks the cross-platform comparison explicitly.

The audit-considerations section is the load-bearing regulatory framing: Quiver activity logs alone are insufficient to reconstruct an investigation. The combined Quiver activity + Article 005 AuditEntry + analyst justification text is the audit-trail discipline the institution must maintain.
