# Excel Article 007 — Companion Bundle

**Title:** Round-Number Bias and Threshold Avoidance in Excel — Detecting Just-Under-Authorization-Limit Manipulation Patterns

**Series:** Claude in Excel for Fraud Detection
**Article ID:** SPP-DD-TECH-EXCEL-007
**Bundle status:** `validated_bundle` (validated at tab-structure scope; see `artifact_manifest.json`)
**Prepared by:** Noah Green CPA CFE

## What this bundle contains

| Path | Purpose |
|---|---|
| `../../workbooks/007-round-number-bias-threshold-avoidance.xlsx` | Workbook scaffold with 5 tabs matching article-described workpaper organization (README, Inputs, Digit Flags, Threshold Bands, Checks). Tab content is placeholder; full content build is the next promotion stage. |
| `artifact_manifest.json` | Bundle metadata including audit reference and explicit scope/limits. |

## Validation scope

Tab structure matches the article's described workpaper organization.
The audit script
(`/Users/noahgreen/NGO/outbox/owner_review/dd_tech_lab_kickoff_2026-05-10/coordination/excel_content_match_audit_2026-05-15.py`)
verifies the 5 tabs are present.

**Validation does NOT cover:** RIGHT/MOD/MID parsing for last-digit
analysis, COUNTIFS for threshold-band bunching, chi-squared
goodness-of-fit against uniform-digit expectation, or the
authorization-threshold cross-reference table.

## What's NOT in this bundle (the deeper promotion stage)

To upgrade from `validated_at_tab_structure_scope` to full content-fidelity:

- Inputs tab: sample transaction extract with synthetic just-under-threshold patterns
- Digit Flags tab: RIGHT/MOD/MID parsing + last-digit distribution analysis
- Threshold Bands tab: COUNTIFS for threshold-proximity bunching + authorization-limit lookup
- Checks tab: chi-squared goodness-of-fit against uniform expectation

Approximate effort: 4-6 hours per workbook. Deferred to a deeper promotion stage.

## Source article

`/Users/noahgreen/NGO/outbox/owner_review/dd_tech_lab_kickoff_2026-05-10/excel_fraud/articles_v6/007_round-number-bias-threshold-avoidance_DRAFT_v6_2026-05-13.md`
