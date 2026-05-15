# Graduation Criteria — Quiver Query → Workshop Application

Companion artifact for Foundry Article 007. The decision framework for when
a recurring Quiver query has earned promotion to a proper Workshop
application (Article 003's pattern). Built as a checklist so the
investigator can self-assess without engineering judgment.

A Quiver query graduates to Workshop when **at least four of the seven
criteria below are satisfied**. Fewer than four → keep it in Quiver; more
than four → engineering investment is now cheaper than continuing to
re-execute the Quiver query manually.

## The seven criteria

### 1. Recurrence frequency

| Frequency | Score |
|---|---|
| Daily or more | ✓ |
| Weekly (regular team workflow) | ✓ |
| Monthly (routine cycle) | maybe — depends on stakes |
| Quarterly or less | ✗ |
| One-off | ✗ |

Stays in Quiver: ad-hoc strategy questions, regulatory list scans,
news-driven exposure checks.

Graduates to Workshop: monthly portfolio reviews, weekly EDD-queue health
checks, daily watchlist scans.

### 2. Number of distinct users

| User pattern | Score |
|---|---|
| Used by 5+ team members regularly | ✓ |
| Used by a single team across roles | ✓ |
| Used by 1-2 individuals | ✗ |

The Workshop value-add is sharing-with-permissioning and consistent UX.
For single-user workflows, the share-link mechanic in Quiver suffices.

### 3. Action depth (read-only vs. state-changing)

| Pattern | Score |
|---|---|
| Read-only investigation followed by analyst decision recorded elsewhere | ✗ |
| Investigation surfaces items that require state-change Actions (Article 005) | ✓ |

Quiver is read-only by design. The moment the workflow involves analysts
selecting items in the query result and triggering an Action on each, the
investigator needs the Workshop application's review-queue surface —
Quiver's data-table view is not designed for select-and-action
workflows at scale.

### 4. Cognitive load / time-to-answer

| Pattern | Score |
|---|---|
| Single Quiver query gets the answer in under 5 min | ✗ |
| Investigator runs 2-3 Quiver queries in sequence to piece together the answer | maybe |
| Investigator runs 4+ Quiver queries or copies results between queries | ✓ |

Multi-query chained workflows are where Workshop's joined-views,
linked-filters, and persistent state earn their keep.

### 5. Visualization complexity

| Pattern | Score |
|---|---|
| One bar chart + one data table | ✗ |
| Mix of bar chart + table + heatmap (Quiver primitives) | maybe |
| Custom visualization (e.g., entity-relationship network with custom node decorations, time-series with markers, geo-map with custom layers) | ✓ |
| Investigator-specific controls (custom filters, drill-down sequences) | ✓ |

Quiver's visualization primitives are deliberately limited. Custom
visualization needs are Workshop's territory.

### 6. Audit / regulatory significance

| Pattern | Score |
|---|---|
| Investigation drives risk-rating decisions or other regulated state changes | ✓ |
| Read-only with no downstream regulated action | ✗ |
| Investigation results retained as engagement documentation | ✓ |

When the Quiver query's output is part of the institution's evidentiary
record (cited in a SAR filing, in a board pack, in a regulatory submission),
the workflow benefits from Workshop's persistent state and the Actions
framework's audit trail.

### 7. Performance / data volume

| Pattern | Score |
|---|---|
| Query runs in under 5 seconds on full universe | ✗ |
| Query times out or runs > 30 seconds; requires materialized rollups | ✓ |
| Result set exceeds 10,000 rows and investigators need pagination/filtering | ✓ |

Quiver's index-driven query path has limits. When queries need
materialized rollups (Pipeline Builder transforms producing pre-computed
aggregates), the architecture has crossed into Workshop territory anyway.

## Self-assessment template

```
Quiver query name:        ______________________________________________
Date of assessment:       ______________________________________________
Assessed by:              ______________________________________________

Criterion                                          Met? (✓/✗)
─────────────────────────────────────────────────  ─────────
1. Recurrence frequency (daily/weekly/monthly)         ___
2. ≥ 5 distinct users regularly                        ___
3. Surfaces items requiring state-change Actions       ___
4. Multi-query chained workflow                        ___
5. Custom visualization beyond Quiver primitives       ___
6. Audit / regulatory significance                     ___
7. Performance / volume requires materialization       ___

Met total:                                             ___ / 7

Decision: ____ Stay in Quiver  |  ____ Promote to Workshop
```

## Cost of getting it wrong (either direction)

**Building a Workshop application that should have been a Quiver query:**
- Engineering investment (typically 1-3 sprints) for a workflow the team
  may abandon in 2 months
- Maintenance burden (ontology schema changes propagate; the application
  needs upkeep)
- Permission complexity (Workshop's RBAC model is heavier than Quiver's
  share-link mechanic)

**Keeping a Quiver query that should be a Workshop application:**
- Recurring cognitive cost (analysts re-run the query, re-interpret
  results, re-apply context that should be baked into the UI)
- Audit gap (state-change Actions don't fire from Quiver; the workflow's
  evidentiary chain is fragmented)
- Performance ceiling (Quiver hits index-query limits; analysts work around
  with manual Excel exports, which is its own failure mode)

The graduation criteria are designed to give the institution an objective
self-assessment point. When in doubt, run the checklist on a real query
the team uses; the assessment usually clarifies the decision.
