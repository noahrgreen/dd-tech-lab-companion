# Examiner-Ready Query Templates

The standard ten queries an examiner asks first when reviewing the
institution's DD audit trail. Phrased as Foundry Quiver / OntologyQuery
patterns; translatable to the institution's preferred query syntax.

Each query is designed to satisfy an examiner request in a single roundtrip —
no follow-up "now show me the evidence for that" required. The supporting
evidence is pre-joined.

The SLA expectation is that any of these queries returns in **under 30
seconds** at typical institutional scale (10s of millions of AuditEntries).
If your deployment fails that SLA, examine the AuditEntry indexing and the
supporting-evidence snapshot storage strategy before the examiner asks.

---

## 1. Every risk-rating change for a specific counterparty in the last N months

```
ontology_query:
  object_type: AuditEntry
  filter:
    action_type: ElevateRiskRating  OR  LowerRiskRating
    target_object_id: {counterparty_id}
    timestamp: last_n_months({n})
  join:
    - supporting_evidence_ids → AdverseMediaMention, SanctionsHit, TransactionAnomaly
    - actor → User
    - approver → User (where present)
  sort: timestamp DESC
  return: action_id, timestamp, actor, actor_role, approver, prior_state.risk_rating,
          new_state.risk_rating, justification, supporting_evidence (full snapshot)
```

## 2. Every action a specific analyst took in a date range

```
ontology_query:
  object_type: AuditEntry
  filter:
    actor: {user_id}
    timestamp: between({start_date}, {end_date})
  sort: timestamp DESC
  return: action_id, action_type, target_object_id, timestamp, justification
```

## 3. Every sanctions-hit dismissal in a date range, with reviewer

```
ontology_query:
  object_type: AuditEntry
  filter:
    action_type: DismissSanctionsHit
    timestamp: between({start_date}, {end_date})
  join:
    - supporting_evidence_ids → SanctionsHit
    - actor → User
    - approver → User
  return: action_id, target_object_id, actor, approver, justification,
          supporting_evidence (full SanctionsHit snapshot)
```

## 4. All EDD escalations triggered by adverse-media findings in a quarter

```
ontology_query:
  object_type: AuditEntry
  filter:
    action_type: EscalateToEDD
    supporting_evidence.object_type: AdverseMediaMention
    timestamp: quarter({yyyy}, {q})
  join:
    - supporting_evidence_ids → AdverseMediaMention
  return: action_id, target_object_id, actor, justification,
          supporting_evidence
```

## 5. All critical-rating elevations, with dual-approval chain, in last 12 months

```
ontology_query:
  object_type: AuditEntry
  filter:
    action_type: ElevateRiskRating
    new_state.risk_rating: critical
    timestamp: last_n_months(12)
  return: action_id, target_object_id, actor, actor_role, approver, approver_role,
          timestamp, justification, supporting_evidence
```

## 6. Find any AuditEntries with missing supporting evidence (DATA-QUALITY query)

```
ontology_query:
  object_type: AuditEntry
  filter:
    supporting_evidence_ids: empty_array
  return: action_id, action_type, actor, timestamp, target_object_id
```

Expected result: **zero rows**. Any rows returned indicate either a
pre-Actions-framework legacy entry or a bypass-control gap. Investigate before
the examiner asks.

## 7. Find any AuditEntries with justification length below the 200-char floor

```
ontology_query:
  object_type: AuditEntry
  filter:
    length(justification) < 200
  return: action_id, action_type, actor, justification_length, timestamp
```

Expected result: **zero rows**. Any rows are either legacy entries (pre-floor)
or platform-level constraint-bypass evidence.

## 8. Superseded AuditEntries with the superseding entry's lineage

```
ontology_query:
  object_type: AuditEntry
  filter:
    superseded_by: not_null
  join:
    - superseded_by → AuditEntry (recursive, show full supersession chain)
  return: original_action_id, original_timestamp, supersession_chain (array of action_ids)
```

Supersessions should be rare. A high rate of supersession indicates either
Action-definition drift or analyst workflow problems.

## 9. Same-day Action volume per actor (segregation-of-duties anomaly screening)

```
ontology_query:
  object_type: AuditEntry
  aggregate:
    group_by: [actor, date(timestamp)]
    count: distinct(action_id)
  having:
    count > 50   # adjust threshold to institutional norm
  sort: count DESC
  return: actor, date, count
```

Outliers in same-day Action volume can indicate batch-script-via-UI
patterns, possible RBAC misconfiguration, or actor-level workflow issues
worth investigating.

## 10. Action-vs-bypass reconciliation for risk-rating changes

```
combined_query:
  # Set A: every Counterparty.risk_rating change captured by Actions framework
  audit_entries:
    object_type: AuditEntry
    filter:
      action_type: ElevateRiskRating OR LowerRiskRating
      timestamp: last_n_days({n})
    return: (target_object_id, prior_state.risk_rating, new_state.risk_rating, timestamp)

  # Set B: every Counterparty.risk_rating change reflected in the ontology object history
  ontology_history:
    object_type: Counterparty
    field: risk_rating
    change_window: last_n_days({n})
    return: (counterparty_id, prior_value, new_value, change_timestamp)

  reconcile:
    join_on: target_object_id = counterparty_id, timestamp ≈ change_timestamp (±1 minute)
    return:
      - matched: rows in both sets
      - audit_only: rows in audit_entries but not in ontology_history
      - bypass_only: rows in ontology_history but not in audit_entries
```

**`bypass_only` rows are the examiner-readiness red flag.** Any row in
`bypass_only` represents a risk-rating change that occurred WITHOUT firing the
ElevateRiskRating ActionType — i.e., the bypass paths (direct dataset edit,
admin override, transform redeployment, emergency backfill) that the
institution must address with separate audit treatment per the
bypass_controls/ section of this bundle.

Run this query continuously (not just when the examiner asks). Any non-zero
`bypass_only` count should generate an internal audit ticket the same business
day.
