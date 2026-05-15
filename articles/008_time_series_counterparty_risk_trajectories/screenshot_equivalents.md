# Screenshot Equivalents — Foundry Time-Series Surfaces

Text-based renderings of the Foundry surfaces that consume the
counterparty_risk_score time series. The bundle is portable; these
screen-equivalents map artifacts to UI.

## TimeSeries Object Viewer — CP-SYN-007 (gradual_sanctions_buildup)

```
┌─ Counterparty: CP-SYN-007  •  Composite Risk Trajectory (730-day) ────────────┐
│                                                                                │
│  Current composite_risk_score:  0.6841  (▲ from 0.412 30 days ago)            │
│  Risk rating:                   high     (last elevated 2026-04-02)           │
│  Trajectory pattern:            gradual_sanctions_buildup                     │
│                                                                                │
│  ┌─ Composite score (last 365 days) ──────────────────────────────────────┐ │
│  │                                                                          │ │
│  │ 1.0 ┤                                                                    │ │
│  │     │                                                                    │ │
│  │ 0.8 ┤                                                              ▄▄▆▇  │ │
│  │     │                                                       ▃▄▅▅▆▇      │ │
│  │ 0.6 ┤  ── crit threshold ────────────────────────────  ▃▄▄▅▆            │ │
│  │     │                                              ▃▃▃▄                  │ │
│  │ 0.4 ┤  ── high threshold ────────────────────  ▃▄▄                       │ │
│  │     │                                       ▃▃▃   ←─── breach 2026-02-25 │ │
│  │ 0.2 ┤      ▁▁                            ▃▃▃                              │ │
│  │     │ ▁▁▁▁▁  ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▃▃▃▃▃                                │ │
│  │ 0.0 ┴───────────────────────────────────────────────────────────────────  │ │
│  │      2025-05  2025-08  2025-11  2026-02  2026-05                          │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ Component contributions (latest) ──────────────────────────────────────┐ │
│  │  sanctions_signal   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.950 × 0.40 = 0.380 (55.5%)  │ │
│  │  media_signal       ▓▓▓▓▓▓ 0.180 × 0.25 = 0.045  (6.6%)                  │ │
│  │  transaction_signal ▓▓▓▓▓▓▓▓ 0.400 × 0.20 = 0.080 (11.7%)                │ │
│  │  kyc_signal         ▓▓▓▓▓▓▓▓▓ 0.450 × 0.15 = 0.068 (9.9%)                │ │
│  │  ─────────────────────────────────────                                   │ │
│  │  composite                              0.684                            │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  [ View AlertEntry history ▸ ]   [ View AuditEntry chain ▸ ]                  │
└────────────────────────────────────────────────────────────────────────────────┘
```

## AlertEntry Triggered — CP-SYN-007 breach event

```
┌─ AlertEntry: 2026-02-25 ─ CP-SYN-007 ─ composite_crosses_high ────────────────┐
│                                                                                │
│  Generated:        2026-02-25 04:18 UTC                                        │
│  Counterparty:     CP-SYN-007                                                  │
│  composite_score:  0.4019  (prior day: 0.3927)                                 │
│  Breach type:      composite_crosses_high                                      │
│  Status:           OPEN  ─── routed to senior_analyst review queue            │
│  Recommended Action: EscalateToEDD                                             │
│                                                                                │
│  ┌─ Why this alert fired ──────────────────────────────────────────────────┐ │
│  │  composite_risk_score crossed 0.40 high-threshold on 2026-02-25.        │ │
│  │                                                                          │ │
│  │  Primary driver:  sanctions_signal ramping (currently 0.95)              │ │
│  │  Secondary:       transaction_signal ramping in parallel (0.40)          │ │
│  │  Background:      media and kyc signals stable at baseline               │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  [ Submit Action: EscalateToEDD ▸ ]   [ Dismiss with reason ▸ ]              │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Workshop Drill-Down — investigator view

```
┌─ Counterparty CP-SYN-007 ─ Workshop View ─ Trajectory Tab ────────────────────┐
│                                                                                │
│  [ Overview ]  [ Trajectory ]  [ Evidence ]  [ Audit Trail ]                   │
│                                                                                │
│  ┌─ Composite + Component Signals (365 days) ─────────────────────────────┐ │
│  │  [Click-and-drag to drill into a window]                                 │ │
│  │                                                                          │ │
│  │     Composite      ───────────────────────────                          │ │
│  │     Sanctions      ............................                          │ │
│  │     Media          ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─                            │ │
│  │     Transaction    ··········                                            │ │
│  │     KYC            ──── ─── ──── ────                                    │ │
│  │                                                                          │ │
│  │     2025-05    2025-08    2025-11    2026-02    2026-05                  │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  Selected window: 2026-02-15 → 2026-02-28 (the breach event)                  │
│                                                                                │
│  ┌─ Linked events in selected window ──────────────────────────────────────┐ │
│  │  2026-02-21  SanctionsHit (OFAC-SDN-2026-LIST)        sanctions: 0.0 → 0.95 │
│  │  2026-02-23  Transaction surge (3.2σ above baseline)  transaction: 0.04 → 0.40 │
│  │  2026-02-25  AlertEntry triggered                     ──── this alert ───  │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  [ Submit Action: EscalateToEDD ▸ ]   [ Pin to investigation ▸ ]              │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Pipeline Builder DAG — pipeline overview

```
┌─ counterparty_risk_trajectory_alerting  ─  Pipeline Builder ─────────────────┐
│                                                                                │
│  Schedule: daily 04:00 America/New_York                                       │
│  Last run: 2026-05-15 04:14 UTC  •  SUCCESS  •  Duration 18m 42s              │
│                                                                                │
│  ┌─ DAG ─────────────────────────────────────────────────────────────────┐ │
│  │                                                                          │ │
│  │  /dd/ontology/Counterparty ──────┐                                       │ │
│  │  /dd/silver/sanctions_hits ──────┤                                       │ │
│  │  /dd/silver/adverse_media_men... ┼─► [Code Repo] counterparty_risk_traj. │ │
│  │  /dd/silver/transactions  ───────┘             ↓                          │ │
│  │                                  /dd/timeseries/counterparty_risk_score │ │
│  │                                                ↓                          │ │
│  │                                  [Pipeline Builder] detect_threshold_b... │ │
│  │                                                ↓                          │ │
│  │                                  /dd/timeseries/risk_score_breaches      │ │
│  │                                                ↓                          │ │
│  │                                  [Pipeline Builder] emit_alert_entries  │ │
│  │                                                ↓                          │ │
│  │                                  /dd/ontology/AlertEntry                 │ │
│  │                                                ↓                          │ │
│  │                                  [Workshop review queue (Article 003)]   │ │
│  │                                                ↓                          │ │
│  │                                  [Analyst Action (Article 005)]          │ │
│  │                                                                          │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  [ View metrics ▸ ]   [ View materiality assessment ▸ ]                        │
└────────────────────────────────────────────────────────────────────────────────┘
```

These layouts are illustrative — actual Foundry surfaces differ by version.
The patterns (TimeSeries viewer with component decomposition, AlertEntry
triage card, Workshop drill-down, Pipeline DAG view) are stable across
versions.
