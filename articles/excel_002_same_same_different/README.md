# Excel Article 002 — Companion Bundle

**Title:** Same-Same-Different in Excel — Detecting Identical-Value-Different-Date Patterns Across Vendor Files

**Series:** Claude in Excel for Fraud Detection
**Article ID:** SPP-DD-TECH-EXCEL-002
**Bundle status:** `validated_bundle` (validated at tab-structure scope; see `artifact_manifest.json` for scope detail)
**Prepared by:** Noah Green CPA CFE

## What this bundle contains

| Path | Purpose |
|---|---|
| `../../workbooks/002-same-same-different.xlsx` | Workbook scaffold with 5 tabs matching article-described workpaper organization (README, Inputs, Pairing Logic, Exception Review, Checks). Tab content is placeholder rows; full content build is the next promotion stage. |
| `artifact_manifest.json` | Bundle metadata including audit reference and explicit scope/limits. |

## Validation scope

Tab structure of the workbook matches the article's described workpaper
organization. The audit script
(`/Users/noahgreen/NGO/outbox/owner_review/dd_tech_lab_kickoff_2026-05-10/coordination/excel_content_match_audit_2026-05-15.py`)
verifies the 5 tabs are present and reports findings.

**Validation does NOT cover:** cell-level content fidelity (COUNTIFS
pairing logic, normalization formulas, exception-review FILTER
expressions, Checks-tab cross-validation). The workbook is a tab-structure
scaffold; readers expecting a complete working workbook with the article's
full worked example will find tab names but not populated cell content.

## Audit reference

`/Users/noahgreen/NGO/outbox/owner_review/dd_tech_lab_kickoff_2026-05-10/coordination/excel_content_match_audit_2026-05-15.{json,md}`

## What's NOT in this bundle (the deeper promotion stage)

To upgrade from `validated_at_tab_structure_scope` to full content-fidelity
validation, the workbook needs:

- Inputs tab: complete sample vendor master + invoice extract (~100-500 rows)
- Pairing Logic tab: live COUNTIFS formulas + named ranges per article
- Exception Review tab: FILTER expressions producing the flagged-record view
- Checks tab: cross-validation formulas per the article's QA pattern
- Claude-prompt cells where the article references LLM augmentation

Approximate effort: 4-6 hours per workbook. Deferred to a deeper promotion stage.

## Source article

`/Users/noahgreen/NGO/outbox/owner_review/dd_tech_lab_kickoff_2026-05-10/excel_fraud/articles_v4/002_same-same-different-in-excel_DRAFT_v4_2026-05-13.md`
