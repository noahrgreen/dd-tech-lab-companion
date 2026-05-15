# Screenshot Equivalents — Foundry Quiver

Text-based renderings of the Foundry Quiver surfaces the article walks.
The bundle is portable (YAML query specs); these screen-equivalents map
the bundle artifacts to the Quiver UI.

## Quiver Instant-Query Mode — "exposure to issuer ISS-00042"

```
┌─ Quiver — Instant Query ──────────────────────────────────────────────────────┐
│                                                                                │
│  Target object class:   Counterparty                                  ▾        │
│                                                                                │
│  ┌─ Filters ───────────────────────────────────────────────────────────────┐ │
│  │  ✓ has_link  TransactedWith                                              │ │
│  │  ✓ link_target.issuer_id  ==  ISS-00042                                  │ │
│  │  ✓ TransactedWith.volume_usd  ≥  100000                                  │ │
│  │  [ + Add filter ]                                                         │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ Aggregate ─────────────────────────────────────────────────────────────┐ │
│  │  Count:     counterparties                                                │ │
│  │  Sum:       TransactedWith.volume_usd                                    │ │
│  │  Group by:  jurisdiction                                       ▾         │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  [ Run query ]   ─── est. runtime 2-5s on full universe                        │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Quiver Query Result — bar chart + data table

```
┌─ counterparty_exposure_to_issuer  •  ran 2026-05-15 14:22 ─────────────────────┐
│                                                                                │
│  Issuer: ISS-00042  •  Min volume: $100,000  •  18 counterparties returned    │
│                                                                                │
│  ┌─ Counterparties exposed by jurisdiction ────────────────────────────────┐ │
│  │   ▓▓▓▓▓▓▓▓▓ Singapore       (6)                                          │ │
│  │   ▓▓▓▓▓▓▓   UK              (4)                                          │ │
│  │   ▓▓▓▓▓     US              (3)                                          │ │
│  │   ▓▓▓       Germany         (2)                                          │ │
│  │   ▓▓        Switzerland     (2)                                          │ │
│  │   ▓         Cayman          (1)                                          │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ Data table (sorted by total_volume_usd desc) ──────────────────────────┐ │
│  │  counterparty_id  legal_name             jurisdiction  total_volume_usd │ │
│  │  CP-SYNTH-00042   Meridian Holdings Pte  Singapore          $4.2M       │ │
│  │  CP-00133         Acme Trading Ltd       UK                 $3.8M       │ │
│  │  CP-00471         BluePoint Capital      Singapore          $2.9M       │ │
│  │  CP-00088         GreenLeaf Holdings     UK                 $1.7M       │ │
│  │  CP-00219         (synthetic ID)          US                $1.4M       │ │
│  │  ... (13 more rows)                                                      │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  [ Save as parameterized query ▸ ]   [ Share link ▸ ]   [ Export CSV ▸ ]      │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Quiver Save-As-Parameterized — turning the instant query into a saved query

```
┌─ Save Query — counterparty_exposure_to_issuer ─────────────────────────────────┐
│                                                                                │
│  Name:         counterparty_exposure_to_issuer                                 │
│  Description:  Returns counterparties exposed to a named issuer above a USD   │
│                threshold, grouped by jurisdiction.                             │
│                                                                                │
│  ┌─ Parameters ────────────────────────────────────────────────────────────┐ │
│  │  ☑ Make :issuer_id (ISS-00042) into a parameter                          │ │
│  │     Name:         issuer_id_parameter                                    │ │
│  │     Type:         string                                                  │ │
│  │     Prompt:       "Issuer ID to scan exposure for"                       │ │
│  │     Validation:   non_empty                                              │ │
│  │                                                                          │ │
│  │  ☑ Make :min_volume (100000) into a parameter                            │ │
│  │     Name:         min_volume_parameter                                   │ │
│  │     Type:         number                                                 │ │
│  │     Default:      100000                                                 │ │
│  │     Prompt:       "Minimum USD exposure threshold"                       │ │
│  │     Validation:   positive_number                                        │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  Share default:   ● Read-only      ○ Editable                                 │
│                                                                                │
│  [ Save ]   [ Save and run ]   [ Cancel ]                                      │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Quiver Share Link — read-only handoff to colleague

```
┌─ Share Link ─────────────────────────────────────────────────────────────────┐
│                                                                                │
│  Query:            counterparty_exposure_to_issuer                             │
│  Permission:       Read-only (recipient sees query and result; cannot edit)    │
│  Expires:          Never (revocable any time)                                 │
│                                                                                │
│  Link:             foundry://quiver/share/q-9f3a2c-x42d8                       │
│                                                                                │
│  Recipients can:                                                               │
│    ✓ Run the query with their own parameter values                             │
│    ✓ Export results to CSV                                                    │
│    ✗ Modify the saved query                                                   │
│    ✗ Change the target ontology data                                          │
│                                                                                │
│  [ Copy link ]   [ Send to team chat ]   [ Revoke link ]                       │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Graduation-Criteria Self-Assessment — embedded checklist

```
┌─ Graduation Self-Assessment — counterparty_exposure_to_issuer ────────────────┐
│                                                                                │
│  Score this Quiver query against the 7-criterion checklist:                    │
│                                                                                │
│  ☐  Daily/weekly recurrence                                                    │
│  ☑  ≥ 5 distinct users (12 team members ran in last 30 days)                  │
│  ☐  Surfaces items requiring state-change Actions                              │
│  ☐  Multi-query chained workflow                                               │
│  ☐  Custom visualization beyond Quiver primitives                              │
│  ☑  Audit / regulatory significance (results cited in CDD updates)            │
│  ☑  Performance limits (full-universe runs > 30s; materialization in place)    │
│                                                                                │
│  Score: 3 / 7  •  Recommendation: keep in Quiver                              │
│                                                                                │
│  [ Run assessment ]   [ Reset ]   [ View criteria details ▸ ]                  │
└────────────────────────────────────────────────────────────────────────────────┘
```

These layouts are illustrative. The actual Quiver UI differs by Foundry
version. The patterns (instant query, save-as-parameterized, share-link,
graduation-self-assessment) are stable across versions.
