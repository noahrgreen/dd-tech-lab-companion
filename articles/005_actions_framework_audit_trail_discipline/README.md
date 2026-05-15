# Foundry Article 005 — Companion Bundle

**Title:** Foundry Actions Framework for Audit-Trail Discipline — Risk-Rating Changes, Regulatory Documentation, and the Examiner-Ready Audit Log

**Series:** Palantir Foundry for Due Diligence
**Article ID:** SPP-DD-TECH-FOUNDRY-005
**Bundle status:** `validated_bundle`
**Prepared by:** Noah Green CPA CFE

## What this bundle contains

| Path | Purpose |
|---|---|
| `action_templates/risk_rating_change_action.yaml` | Full ElevateRiskRating ActionType specification: target_object, authorization, required_inputs with constraints (200-char justification floor, ObjectSet evidence constraint, dual_approval_required for critical), side_effects (Counterparty update + AuditEntry create), post_execution hooks (critical notify, sanctions queue-for-filing). Includes the bypass-control note that distinguishes sanctioned-path writes from bypass-path writes. |
| `audit_log/risk_decision_audit_log_schema.json` | Valid JSON Schema (draft 2020-12) for the AuditEntry ontology object: action_id, action_type, actor + role at execution, approver + role, immutable=true, supersession chain, supporting_evidence_snapshot_uri (the field that preserves evidence-as-of-decision-time), retention_policy. |
| `audit_log/examiner_ready_query_templates.md` | The 10 examiner queries: counterparty rating history, analyst actions in window, sanctions dismissals, EDD escalations from adverse-media, critical elevations with dual-approval chain, data-quality screens (missing evidence, short justifications), supersession lineage, segregation-of-duties anomaly screening, AND the action-vs-bypass reconciliation query that catches the bypass-control gap continuously. |
| `bypass_controls/bypass_audit_controls.yaml` | 6 bypass paths (direct dataset edit, admin override, transform redeployment, emergency backfill, API direct write, ontology object undelete) with recommended per-path controls and a quarterly self-assessment requirement. Addresses the seed's critical-drafting-discipline note explicitly. |
| `retention/retention_and_approvals_matrix.yaml` | 6 retention buckets with 7-year regulatory floors + citations (FFIEC BSA/AML, SOX §404, SR 11-7 §V, FinCEN, OFAC); 5 ActionType authorization patterns (single auth, dual auth for criticals, dual auth for sanctions dismissals / EDD termination / beneficial-ownership changes); segregation-of-duties enforcement rules. |
| `regulatory_mapping/regulatory_mapping.yaml` | Mapping of 6 regulations (SR 11-7, OCC 2011-12, SOX §404, FFIEC BSA/AML, FinCEN CDD Rule 31 CFR §1010.230, PCAOB AS 2201) to specific bundle artifacts. Each entry separates "Foundry contribution" from "institution responsibility" — the framing discipline the seed flagged. |
| `synthetic_data/example_audit_entry.json` | Worked example: senior_analyst elevates Meridian Holdings (Pte) Ltd from B+ to high, supported by 5 evidence items including Article 004's AIP summary output. Validates against the schema. Demonstrates the 004 → 005 article-flow handoff. |
| `screenshot_equivalents.md` | 4 text-based Foundry UI renderings: Action Editor, Action Submission, AuditEntry View, Examiner Query Result. |
| `validation_notes.md` | What this bundle validates, what it doesn't, reproducibility commands, framing discipline reminder. |

## Quick start (validation reproducibility)

```bash
# All commands run from this directory.

# 1. AuditEntry schema valid + example validates
python3 -c "
import json, jsonschema
s = json.load(open('audit_log/risk_decision_audit_log_schema.json'))
o = json.load(open('synthetic_data/example_audit_entry.json'))
jsonschema.Draft202012Validator.check_schema(s)
errs = list(jsonschema.Draft202012Validator(s).iter_errors(o))
print('OK' if not errs else errs)"

# 2. YAML files parse
python3 -c "
import yaml
for p in ['action_templates/risk_rating_change_action.yaml',
          'retention/retention_and_approvals_matrix.yaml',
          'bypass_controls/bypass_audit_controls.yaml',
          'regulatory_mapping/regulatory_mapping.yaml']:
    yaml.safe_load(open(p))
    print(f'{p}: parses')"
```

## Article-pattern summary

8 sections per seed: audit-trail problem → Actions primitives → immutability and audit-entry design → authorization-level enforcement → supporting-evidence linking → regulatory mapping → examiner-ready audit log → worked example. This bundle implements all 8 surfaces: the Action YAML, the AuditEntry schema, the bypass controls (a non-optional companion to the sanctioned path), the retention + approvals matrix, the regulatory mapping, the 10 examiner queries, and a synthetic AuditEntry demonstrating the worked example end-to-end.

## What's NOT in this bundle

- A live Foundry deployment. The ActionType YAML describes the specification; no Foundry runtime executes it here.
- The institution's overall control environment. The Actions framework provides primitives; the institution must implement bypass controls, ongoing-monitoring cadence, analyst training, control testing, and SAR-filing workflow integration separately.
- Specific institutional RBAC mappings. The authorization_level values reference generic roles (senior_analyst, compliance_manager, etc.); the institution maps these to its actual RBAC implementation in deployment config.
- Regulatory interpretation as of dates after 2026-05-15. Regulators update guidance; the regulatory_mapping.yaml cites specific sections accurate at this date.

## Critical framing reminder

Per the seed's drafting discipline:

> Foundry Actions framework gives the institution the **primitives** to build
> an audit-trail discipline consistent with SR 11-7 / SOX §404 / FFIEC BSA/AML
> / OCC 2011-12 documentation expectations. It does NOT, by itself, satisfy
> any specific regulator's requirements. The institution's overall control
> environment determines examiner readiness.

The platform provides the primitive; the institution provides the discipline.
Either alone is insufficient.
