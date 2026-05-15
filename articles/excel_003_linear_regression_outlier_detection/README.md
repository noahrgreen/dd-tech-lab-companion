# Excel Article 003 — Companion Bundle

**Title:** Linear Regression for Outlier Detection in Excel — Building the Standardized-Residual Workpaper for Expense-Account Analytics

**Series:** Claude in Excel for Fraud Detection
**Article ID:** SPP-DD-TECH-EXCEL-003
**Bundle status:** `validated_bundle` (validated at tab-structure scope; see `artifact_manifest.json`)
**Prepared by:** Noah Green CPA CFE

## What this bundle contains

| Path | Purpose |
|---|---|
| `../../workbooks/003-linear-regression-outlier-detection.xlsx` | Workbook scaffold with 5 tabs matching article-described workpaper organization (README, Inputs, Regression Model, Residual Review, Checks). Tab content is placeholder; full content build is the next promotion stage. |
| `artifact_manifest.json` | Bundle metadata including audit reference and explicit scope/limits. |

## Validation scope

Tab structure matches the article's described workpaper organization. The
audit script (`/Users/noahgreen/NGO/outbox/owner_review/dd_tech_lab_kickoff_2026-05-10/coordination/excel_content_match_audit_2026-05-15.py`)
verifies the 5 tabs are present.

**Validation does NOT cover:** LINEST formulas, standardized-residual
computation with degrees-of-freedom accounting, conditional formatting
for outlier flagging, FILTER-based extraction of flagged records, or
Claude-prompt cells for pre-flight validation. The workbook is a tab-
structure scaffold.

## What's NOT in this bundle (the deeper promotion stage)

To upgrade from `validated_at_tab_structure_scope` to full content-fidelity,
the workbook needs:

- Inputs tab: sample driver-expense dataset (e.g., 500-store utility × square footage)
- Regression Model tab: LINEST setup with named ranges + standardized-residual computation
- Residual Review tab: conditional formatting + outlier FILTER expressions
- Checks tab: AS 2305.14-.16 precision-of-expectation validation per article framework
- Claude-prompt cells (J1 named range "DataValidationPrompt" per article)

Approximate effort: 4-6 hours per workbook. Deferred to a deeper promotion stage.

## Source article

`/Users/noahgreen/NGO/outbox/owner_review/dd_tech_lab_kickoff_2026-05-10/excel_fraud/articles_v6/003_linear-regression-outlier-detection_DRAFT_v6_2026-05-13.md`
