# Excel Article 004 — Companion Bundle

**Title:** Geospatial Address Mapping in Excel — Detecting Same-Address Vendor Clusters and Suspicious Proximity Patterns

**Series:** Claude in Excel for Fraud Detection
**Article ID:** SPP-DD-TECH-EXCEL-004
**Bundle status:** `validated_bundle` (validated at tab-structure scope; see `artifact_manifest.json`)
**Prepared by:** Noah Green CPA CFE

## What this bundle contains

| Path | Purpose |
|---|---|
| `../../workbooks/004-geospatial-address-mapping.xlsx` | Workbook scaffold with 5 tabs matching article-described workpaper organization (README, Inputs, Coordinate Prep, Distance Review, Checks). Tab content is placeholder; full content build is the next promotion stage. |
| `artifact_manifest.json` | Bundle metadata including audit reference and explicit scope/limits. |

## Validation scope

Tab structure matches the article's described workpaper organization.
The audit script
(`/Users/noahgreen/NGO/outbox/owner_review/dd_tech_lab_kickoff_2026-05-10/coordination/excel_content_match_audit_2026-05-15.py`)
verifies the 5 tabs are present.

**Validation does NOT cover:** coordinate-extraction formulas, haversine
distance computation, distance-band threshold flags, address-cluster
review pivot, or sample vendor address data.

## What's NOT in this bundle (the deeper promotion stage)

To upgrade from `validated_at_tab_structure_scope` to full content-fidelity:

- Inputs tab: sample vendor address dataset (200-500 vendor records)
- Coordinate Prep tab: address parsing + geocoding result columns
- Distance Review tab: haversine distance formula + distance-band flags
- Checks tab: cluster-flagging logic + manual-review pivot

Approximate effort: 4-6 hours per workbook. Deferred to a deeper promotion stage.

## Source article

`/Users/noahgreen/NGO/outbox/owner_review/dd_tech_lab_kickoff_2026-05-10/excel_fraud/articles_v4/004_geospatial-address-mapping_DRAFT_v4_2026-05-13.md`
