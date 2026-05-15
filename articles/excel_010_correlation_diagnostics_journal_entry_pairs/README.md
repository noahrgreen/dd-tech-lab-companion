# Excel Article 010 — Companion Bundle

**Title:** Correlation Diagnostics for Journal-Entry Pairs in Excel — Detecting Round-Tripping and Mirror-Posting Patterns

**Series:** Claude in Excel for Fraud Detection
**Article ID:** SPP-DD-TECH-EXCEL-010
**Bundle status:** `validated_bundle` (validated at tab-structure scope; see `artifact_manifest.json`)
**Prepared by:** Noah Green CPA CFE

## What this bundle contains

| Path | Purpose |
|---|---|
| `../../workbooks/010-correlation-diagnostics-journal-entry-pairs.xlsx` | Workbook scaffold with 5 tabs matching article-described workpaper organization (README, Inputs, Pairing Matrix, Correlation Signals, Checks). Tab content is placeholder; full content build is the next promotion stage. |
| `artifact_manifest.json` | Bundle metadata including audit reference and explicit scope/limits. |

## Validation scope

Tab structure matches the article's described workpaper organization.
The audit script
(`/Users/noahgreen/NGO/outbox/owner_review/dd_tech_lab_kickoff_2026-05-10/coordination/excel_content_match_audit_2026-05-15.py`)
verifies the 5 tabs are present.

**Validation does NOT cover:** account-pair construction, PEARSON /
SPEARMAN.RHO / CORREL formulas, anti-correlation threshold flags, or
mirror-posting pattern detection.

## What's NOT in this bundle (the deeper promotion stage)

To upgrade from `validated_at_tab_structure_scope` to full content-fidelity:

- Inputs tab: sample journal-entry extract with synthetic round-tripping pairs
- Pairing Matrix tab: account-pair construction + counterparty linkage
- Correlation Signals tab: PEARSON / SPEARMAN.RHO / CORREL + threshold flags
- Checks tab: anti-correlation pattern detection + manual-review pivot

Approximate effort: 4-6 hours per workbook. Deferred to a deeper promotion stage.

## Source article

`/Users/noahgreen/NGO/outbox/owner_review/dd_tech_lab_kickoff_2026-05-10/excel_fraud/articles_v6/010_correlation-diagnostics_DRAFT_v6_2026-05-13.md`
