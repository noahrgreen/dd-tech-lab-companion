# Excel-Fraud Content-Match Audit

Generated: 2026-05-15T19:22:07.100919+00:00
Scope: Excel-fraud companion-bundle tab-structure audit (Articles 002/003/004/007/010)

| Article | Verdict | Tabs Present | Populated / Sparse |
|---|---|---:|---:|
| Excel 002 | `tab_structure_match_scaffold_only` | 5 | 0 / 5 |
| Excel 003 | `tab_structure_match_scaffold_only` | 5 | 0 / 5 |
| Excel 004 | `tab_structure_match_scaffold_only` | 5 | 0 / 5 |
| Excel 007 | `tab_structure_match_scaffold_only` | 5 | 0 / 5 |
| Excel 010 | `tab_structure_match_scaffold_only` | 5 | 0 / 5 |

## Per-article details

### Excel 002 (tab_structure_match_scaffold_only)

- Workbook: `/Users/noahgreen/NGO/outbox/owner_review/dd_tech_lab_kickoff_2026-05-10/companion_repo_dd_tech_lab/workbooks/002-same-same-different.xlsx`
- Expected tabs: ['README', 'Inputs', 'Pairing Logic', 'Exception Review', 'Checks']
- Actual tabs: ['README', 'Inputs', 'Pairing Logic', 'Exception Review', 'Checks']
  - all_expected_tabs_present: PASS
  - no_unexpected_tabs: PASS
  - tabs_have_content_beyond_placeholder: FAIL — populated=0, sparse=5
  - Sparse tabs detail: [{'tab': 'README', 'max_row': 4}, {'tab': 'Inputs', 'max_row': 2}, {'tab': 'Pairing Logic', 'max_row': 2}, {'tab': 'Exception Review', 'max_row': 2}, {'tab': 'Checks', 'max_row': 2}]

### Excel 003 (tab_structure_match_scaffold_only)

- Workbook: `/Users/noahgreen/NGO/outbox/owner_review/dd_tech_lab_kickoff_2026-05-10/companion_repo_dd_tech_lab/workbooks/003-linear-regression-outlier-detection.xlsx`
- Expected tabs: ['README', 'Inputs', 'Regression Model', 'Residual Review', 'Checks']
- Actual tabs: ['README', 'Inputs', 'Regression Model', 'Residual Review', 'Checks']
  - all_expected_tabs_present: PASS
  - no_unexpected_tabs: PASS
  - tabs_have_content_beyond_placeholder: FAIL — populated=0, sparse=5
  - Sparse tabs detail: [{'tab': 'README', 'max_row': 4}, {'tab': 'Inputs', 'max_row': 2}, {'tab': 'Regression Model', 'max_row': 2}, {'tab': 'Residual Review', 'max_row': 2}, {'tab': 'Checks', 'max_row': 2}]

### Excel 004 (tab_structure_match_scaffold_only)

- Workbook: `/Users/noahgreen/NGO/outbox/owner_review/dd_tech_lab_kickoff_2026-05-10/companion_repo_dd_tech_lab/workbooks/004-geospatial-address-mapping.xlsx`
- Expected tabs: ['README', 'Inputs', 'Coordinate Prep', 'Distance Review', 'Checks']
- Actual tabs: ['README', 'Inputs', 'Coordinate Prep', 'Distance Review', 'Checks']
  - all_expected_tabs_present: PASS
  - no_unexpected_tabs: PASS
  - tabs_have_content_beyond_placeholder: FAIL — populated=0, sparse=5
  - Sparse tabs detail: [{'tab': 'README', 'max_row': 4}, {'tab': 'Inputs', 'max_row': 2}, {'tab': 'Coordinate Prep', 'max_row': 2}, {'tab': 'Distance Review', 'max_row': 2}, {'tab': 'Checks', 'max_row': 2}]

### Excel 007 (tab_structure_match_scaffold_only)

- Workbook: `/Users/noahgreen/NGO/outbox/owner_review/dd_tech_lab_kickoff_2026-05-10/companion_repo_dd_tech_lab/workbooks/007-round-number-bias-threshold-avoidance.xlsx`
- Expected tabs: ['README', 'Inputs', 'Digit Flags', 'Threshold Bands', 'Checks']
- Actual tabs: ['README', 'Inputs', 'Digit Flags', 'Threshold Bands', 'Checks']
  - all_expected_tabs_present: PASS
  - no_unexpected_tabs: PASS
  - tabs_have_content_beyond_placeholder: FAIL — populated=0, sparse=5
  - Sparse tabs detail: [{'tab': 'README', 'max_row': 4}, {'tab': 'Inputs', 'max_row': 2}, {'tab': 'Digit Flags', 'max_row': 2}, {'tab': 'Threshold Bands', 'max_row': 2}, {'tab': 'Checks', 'max_row': 2}]

### Excel 010 (tab_structure_match_scaffold_only)

- Workbook: `/Users/noahgreen/NGO/outbox/owner_review/dd_tech_lab_kickoff_2026-05-10/companion_repo_dd_tech_lab/workbooks/010-correlation-diagnostics-journal-entry-pairs.xlsx`
- Expected tabs: ['README', 'Inputs', 'Pairing Matrix', 'Correlation Signals', 'Checks']
- Actual tabs: ['README', 'Inputs', 'Pairing Matrix', 'Correlation Signals', 'Checks']
  - all_expected_tabs_present: PASS
  - no_unexpected_tabs: PASS
  - tabs_have_content_beyond_placeholder: FAIL — populated=0, sparse=5
  - Sparse tabs detail: [{'tab': 'README', 'max_row': 4}, {'tab': 'Inputs', 'max_row': 2}, {'tab': 'Pairing Matrix', 'max_row': 2}, {'tab': 'Correlation Signals', 'max_row': 2}, {'tab': 'Checks', 'max_row': 2}]

## Scope caveats
- Tab-structure audit ONLY. Cell-level content fidelity (formulas, sample data, ranges named in article) NOT verified.
- Workbooks ship as starter scaffolds with tab names matching article structure; richer content build is a separate (deeper) promotion stage.
- This audit's purpose is to validate the structural foundation; full content build would require expanding each workbook's tabs with the article-referenced formulas, sample data, and named ranges.
