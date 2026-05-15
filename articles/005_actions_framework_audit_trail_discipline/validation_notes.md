# Validation Notes — Article 005 Companion Bundle

## Validation scope

- **ActionType YAML** (action_templates/risk_rating_change_action.yaml) matches the seed's ElevateRiskRating specification: target_object, authorization_level, required_inputs (new_risk_rating enum, justification 200-char floor, supporting_evidence ObjectSet with allowed_types constraint, derived dual_approval_required), side_effects (Counterparty update + AuditEntry create), post_execution hooks (critical notify, sanctions queue-for-filing).
- **AuditEntry schema** (audit_log/risk_decision_audit_log_schema.json) is a valid JSON Schema (draft 2020-12) capturing every field the article walks: action_id, action_type, actor + role, approver + role, timestamp, target_object_id, prior_state, new_state, justification (200-char minLength), supporting_evidence_ids (minItems 1), supporting_evidence_snapshot_uri, immutable=true, superseded_by, retention_policy.
- **Example AuditEntry** (synthetic_data/example_audit_entry.json) validates against the schema. Cross-references Article 004's Meridian Holdings synthetic counterparty (CP-SYNTH-00042) — demonstrates the 004 → 005 handoff (analyst reviews AIP summary, accepts, elevates rating).
- **Retention + approvals matrix** (retention/retention_and_approvals_matrix.yaml) covers 6 retention buckets (with 7-year regulatory floor + citations) and 5 ActionType authorization patterns (single auth, dual auth for criticals, dual auth for dismiss/de-escalate/beneficial-ownership changes).
- **Examiner-ready queries** (audit_log/examiner_ready_query_templates.md) ship 10 query templates matching seed §7 CTA: counterparty-history, analyst-actions-in-window, sanctions-dismissals, EDD-from-adverse-media, critical-elevations-with-approval-chain, data-quality screens (missing evidence, short justifications), supersession lineage, segregation-of-duties anomaly screening, AND the **action-vs-bypass reconciliation query** that catches the bypass-control gap explicitly.
- **Bypass controls** (bypass_controls/bypass_audit_controls.yaml) enumerates 6 bypass paths (direct dataset edit, admin override, transform redeployment, emergency backfill, api_direct_write, ontology object undelete) with recommended controls per path and a quarterly self-assessment requirement. Addresses the seed's "critical drafting discipline" note about bypass paths the institution must control separately.
- **Regulatory mapping** (regulatory_mapping/regulatory_mapping.yaml) maps 6 regulations (SR 11-7, OCC 2011-12, SOX §404, FFIEC BSA/AML, FinCEN CDD Rule 31 CFR §1010.230, PCAOB AS 2201) to specific bundle artifacts. Each entry separates "Foundry contribution" from "institution responsibility" per the seed's framing discipline ("provides primitives" vs "satisfies requirements").

## Validation reproducibility

```bash
# Schema valid + example validates
python3 -c "
import json, jsonschema
s = json.load(open('audit_log/risk_decision_audit_log_schema.json'))
o = json.load(open('synthetic_data/example_audit_entry.json'))
jsonschema.Draft202012Validator.check_schema(s)
errs = list(jsonschema.Draft202012Validator(s).iter_errors(o))
print('OK' if not errs else errs)"

# YAML files parse
python3 -c "
import yaml
for p in ['action_templates/risk_rating_change_action.yaml',
          'retention/retention_and_approvals_matrix.yaml',
          'bypass_controls/bypass_audit_controls.yaml',
          'regulatory_mapping/regulatory_mapping.yaml']:
    yaml.safe_load(open(p))
    print(f'{p}: parses')"
```

## Known limits

- This is a portable companion bundle, not a live Foundry Actions deployment. ActionType YAML describes the specification; no Foundry runtime executes it.
- The dual-approval mechanic in `risk_rating_change_action.yaml` describes the expected platform behavior; whether the institution's RBAC implementation actually enforces it requires deployment-specific configuration.
- The regulatory mapping cites specific sections (SR 11-7 §V, PCAOB AS 2201 ¶34, etc.) accurate as of 2026-05-15; regulators update guidance. Re-verify before relying on the mapping for engagement-level documentation.
- The synthetic AuditEntry references Article 004's synthetic counterparty (CP-SYNTH-00042 / Meridian Holdings Pte Ltd). The cross-reference is for demonstration of the 004 → 005 article-flow handoff only; both are fully fabricated.
- The 200-character justification floor is a regulatory-defensible floor, not a quality measure. Justification text quality is institution-side training discipline, not a platform-enforceable constraint.

## Framing discipline (from seed's critical drafting note)

This bundle's deliverables describe the **primitives** the institution uses to BUILD an audit-trail discipline consistent with SR 11-7 / SOX §404 / FFIEC BSA/AML / OCC 2011-12 documentation expectations. They do NOT substitute for the institution's overall control environment. Specifically:

- The bypass-control discipline (bypass_controls/) is non-optional; without it, every "primitive" in this bundle leaks via the bypass paths.
- The quarterly self-assessment in bypass_controls/ is the institution's
  examiner-readiness check; not running it leaves the bypass paths uncontrolled.
- Regulatory mapping separates Foundry contribution from institution responsibility intentionally. The framing "Actions framework satisfies SR 11-7" is an overclaim; the correct framing is "Actions framework gives the institution the primitives to satisfy SR 11-7, contingent on the bypass discipline and the broader control environment."
