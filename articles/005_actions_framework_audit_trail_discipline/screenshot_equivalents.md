# Screenshot Equivalents — Foundry Actions Framework

Text-based renderings of the Foundry surfaces the article walks. The bundle is
portable (YAML + JSON + Markdown); these screen-equivalents help the reader
map the bundle artifacts to the Foundry UI a production deployment exposes.

## Action Editor — `ElevateRiskRating`

```
┌─ Action Editor: ElevateRiskRating ────────────────────────────────────────────┐
│                                                                                │
│  Target object type   Counterparty                                             │
│  Authorization level  senior_analyst_or_above   ▾                              │
│  Status               PRODUCTION-LOCKED  •  v3 deployed 2026-04-18             │
│                                                                                │
│  ┌─ Required inputs ────────────────────────────────────────────────────────┐ │
│  │  new_risk_rating         enum[medium, high, critical]                    │ │
│  │                          ⊟ must exceed current Counterparty.risk_rating  │ │
│  │                                                                           │ │
│  │  justification           text                                            │ │
│  │                          ⊟ min_length = 200 characters                   │ │
│  │                                                                           │ │
│  │  supporting_evidence     ObjectSet                                       │ │
│  │                          ⊟ must contain ≥ 1 of:                          │ │
│  │                              • AdverseMediaMention                       │ │
│  │                              • SanctionsHit                              │ │
│  │                              • TransactionAnomaly                        │ │
│  │                              • InternalEscalationNote                    │ │
│  │                                                                           │ │
│  │  dual_approval_required  boolean  (derived: new_risk_rating == critical) │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ Side effects ──────────────────────────────────────────────────────────┐ │
│  │  1. update  Counterparty.risk_rating ← new_risk_rating                   │ │
│  │  2. update  Counterparty.last_risk_change_timestamp ← now                │ │
│  │  3. create  AuditEntry (immutable = true)                                │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  [ Test Action ▸ ]   [ View AuditEntry Schema ▸ ]   [ Deployment History ▸ ]  │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Action Submission — analyst-side

```
┌─ Submit Action: ElevateRiskRating ────────────────────────────────────────────┐
│                                                                                │
│  Target: Meridian Holdings (Pte) Ltd  (CP-SYNTH-00042, Singapore)              │
│  Current risk rating:  B+                                                      │
│                                                                                │
│  ┌─ new_risk_rating ────────────────────────────────────────────────────────┐ │
│  │  ● high                                                                  │ │
│  │  ○ medium  (would be a downgrade — disabled)                             │ │
│  │  ○ critical  (requires dual approval ✓ — see below)                      │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ justification ─────────────────────────────────────────────────────────┐ │
│  │ Elevation from B+ to high based on aggregate adverse-media review (AIP  │ │
│  │ summary action_id ams-2026-05-15-CP-SYNTH-00042). Three open signals    │ │
│  │ concentrated in 90-day window: civil complaint at pleadings stage       │ │
│  │ (AM-003), highest individual count on the Q1 regulator named-firms      │ │
│  │ list (AM-004)...                                                        │ │
│  │                                              [847 / 200 minimum]   ✓    │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ supporting_evidence (5 objects) ───────────────────────────────────────┐ │
│  │  ☑ AM-001  AdverseMediaMention  Port-doc holds                          │ │
│  │  ☑ AM-002  AdverseMediaMention  Q1 revenue announcement                 │ │
│  │  ☑ AM-003  AdverseMediaMention  Civil suit, pleadings stage             │ │
│  │  ☑ AM-004  AdverseMediaMention  Regulator named-firms list              │ │
│  │  ☑ ams-2026-05-15-CP-SYNTH-00042  AIPSummary  (Article 004 output)      │ │
│  │  [ Add evidence ▸ ]                                                      │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ Validation ────────────────────────────────────────────────────────────┐ │
│  │  ✓ Authorization (senior_analyst — your role)                            │ │
│  │  ✓ Justification length ≥ 200                                            │ │
│  │  ✓ Evidence set non-empty + allowed types                                │ │
│  │  ✓ new_rating > current_rating                                           │ │
│  │  — Dual approval not required (new_rating != critical)                   │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  [ Submit Action ]   [ Save as draft ]   [ Cancel ]                            │
└────────────────────────────────────────────────────────────────────────────────┘
```

## AuditEntry View — examiner-facing

```
┌─ AuditEntry: a1f7c3d4-9b22-4e58-a3c1-7f2a8d6e4901 ────────────────────────────┐
│                                                                                │
│  Type:        ElevateRiskRating          IMMUTABLE  •  retention: 7-year      │
│  Timestamp:   2026-05-15T15:42:18+00:00                                       │
│  Actor:       analyst.kowalski  (senior_analyst at execution time)            │
│  Approver:    n/a  (single-auth — not critical elevation)                     │
│  Target:      Meridian Holdings (Pte) Ltd  (CP-SYNTH-00042)                   │
│                                                                                │
│  ┌─ State change ──────────────────────────────────────────────────────────┐ │
│  │  risk_rating:  B+  →  high                                              │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ Justification ─────────────────────────────────────────────────────────┐ │
│  │ Elevation from B+ to high based on aggregate adverse-media review...    │ │
│  │ [847 characters; full text follows]                                      │ │
│  │                                                                          │ │
│  │ [...]                                                                    │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ Supporting evidence (5 snapshot) ──────────────────────────────────────┐ │
│  │  AM-001  AdverseMediaMention  (snapshot at execution → view)            │ │
│  │  AM-002  AdverseMediaMention  (snapshot at execution → view)            │ │
│  │  AM-003  AdverseMediaMention  (snapshot at execution → view)            │ │
│  │  AM-004  AdverseMediaMention  (snapshot at execution → view)            │ │
│  │  ams-... AIPSummary            (article 004 output → view)              │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ Audit chain ───────────────────────────────────────────────────────────┐ │
│  │  Superseded by: none (this is the current state)                        │ │
│  │  Prior actions on this target (descending):                             │ │
│  │    2025-11-12  ElevateRiskRating  B → B+  (1 yr ago)                    │ │
│  │    2024-08-03  InitialRiskAssignment  none → B  (initial)               │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Examiner Query Result — Query 1 ("rating changes in last 24 months")

```
$ examiner_query 1 --counterparty CP-SYNTH-00042 --months 24

Results: 2 rating-change AuditEntries

┌────────────┬─────────────────────┬──────────────────┬─────┬──────┬──────────┐
│ timestamp  │ action_id           │ actor            │ prv │ new  │ evidence │
├────────────┼─────────────────────┼──────────────────┼─────┼──────┼──────────┤
│ 2026-05-15 │ a1f7c3d4-9b22-4...  │ analyst.kowalski │ B+  │ high │ 5 items  │
│ 2025-11-12 │ 8c5e6b7a-3d11-4...  │ analyst.kowalski │ B   │ B+   │ 2 items  │
└────────────┴─────────────────────┴──────────────────┴─────┴──────┴──────────┘

[ Drill into 2026-05-15 AuditEntry ▸ ]
[ Drill into 2025-11-12 AuditEntry ▸ ]
[ Export as examiner-facing PDF ▸ ]

Query time: 1.8s
```

These layouts are illustrative — the actual Foundry UI differs by version
and by Workshop application configuration. The patterns (Action Editor,
Submission, AuditEntry View, Examiner Query Result) are stable across
versions.
