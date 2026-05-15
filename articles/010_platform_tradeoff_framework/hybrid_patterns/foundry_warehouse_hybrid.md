# Hybrid Pattern — Foundry for Investigator Surface, Snowflake for Warehouse

Companion artifact for Foundry Article 010. The hybrid pattern is the
editorial value-add of the article: many institutions assume the
platform decision is binary (one vendor wins), and the hybrid framing
opens an option many overlook.

## When the hybrid pattern fits

The pattern fits when:

- The institution has materially different workload patterns at the
  warehouse layer (large-volume batch transforms, multi-source data
  integration, analytical query patterns) vs. the investigator surface
  (interactive ad-hoc queries, workflow-driven case management, LLM-
  augmented review).
- Cross-engagement or cross-line-of-business data portability matters
  (PE-DD firms; multi-subsidiary advisory groups).
- The institution wants Foundry's investigator-surface productivity
  without accepting the warehouse-layer lock-in for the analytical
  data foundation.

## When the hybrid pattern does NOT fit

Avoid the hybrid pattern when:

- The institution has insufficient engineering capacity to maintain the
  integration layer (typically requires a 2-3 engineer steady-state on
  the integration boundary alone).
- The integration latency is unacceptable (Foundry's incremental sync
  from Snowflake is meaningfully slower than Foundry-native Ontology
  storage; investigators may notice).
- The institution's data volume is small enough that the single-platform
  approach wins on simplicity (the integration complexity dominates the
  benefits at smaller scale).

## Reference architecture

```
        ┌──────────────────────────────────────────┐
        │ External data sources (vendors, feeds)   │
        └──────────────────────────────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────────────┐
        │ Snowflake (warehouse-layer foundation)   │
        │   - bronze (raw ingestion)               │
        │   - silver (resolved + cleaned)          │
        │   - gold (analytics-ready datasets)      │
        │   - audit-trail Time Travel for ingest  │
        └──────────────────────────────────────────┘
                          │
                          │  Incremental sync via
                          │  Snowflake Sharing / Foundry
                          │  External Datasource pattern
                          ▼
        ┌──────────────────────────────────────────┐
        │ Foundry (investigator-surface layer)     │
        │   - Ontology (Counterparty, AdverseMedia,│
        │     Sanctions, AuditEntry, ...)          │
        │   - Workshop applications                │
        │   - Actions framework (Article 005)     │
        │   - Quiver (Article 007)                │
        │   - AIP (Article 004)                    │
        │   - TimeSeries (Article 008)            │
        └──────────────────────────────────────────┘
```

## Boundary design decisions

The hybrid pattern's success or failure typically hinges on three
boundary decisions:

### 1. Which data lives on which side

- **Warehouse-side (Snowflake):** raw ingestion, multi-source resolution,
  long-form analytical data (transaction histories at fine granularity,
  full-text adverse-media corpus, historical regulatory filings).
- **Foundry-side (Ontology):** the resolved Counterparty and linked
  ontology objects, the AuditEntry chain, the active review queues, the
  TimeSeries objects driving alerting.

The decision rule: data that the investigator-surface needs to query
fast and frequently belongs in the Ontology; data that the warehouse
side needs for batch transforms and analytics belongs in Snowflake.

### 2. Sync mechanics

- **Direction:** typically Snowflake → Foundry (warehouse is upstream).
  Reverse syncs (Foundry-state changes flowing back to Snowflake) are
  more complex and should be minimized; when needed, mediate through
  ActionType side-effects (Article 005 pattern) so the sync events are
  themselves AuditEntries.
- **Cadence:** incremental sync on a 15-minute to 1-hour cadence is
  typical for investigator workloads; sub-15-minute requires
  near-real-time integration which substantially raises complexity.
- **Failure mode:** sync lag must be observable. Foundry-side queries
  may return stale data during sync issues; the investigator must know
  the data freshness to interpret the result correctly.

### 3. Audit-trail boundary

This is the regulatory-defensibility concern that distinguishes a
disciplined hybrid from a brittle one:

- **AuditEntry objects live on the Foundry side** (per Article 005's
  Actions framework). State changes routed through the Actions framework
  produce immutable AuditEntries in the Foundry ontology.
- **Warehouse-side state changes** (ingestion of new bronze data, DBT
  transform re-runs, schema evolution) must produce
  audit-trail records on the warehouse side AS WELL. Snowflake Time
  Travel provides the primitive; the institution must build the audit-
  trail discipline using it.
- **Reconciliation between sides** is non-optional. The action-vs-bypass
  reconciliation query (Article 005 Query #10) must run across the
  warehouse-Foundry boundary: every regulated state change in either
  system must be findable in the audit-chain.

## Cost / complexity trade-off

The hybrid pattern's TCO at bank-group scale typically lands between
single-vendor approaches. The dimensions:

- **Implementation cost:** higher than single-vendor (need integration
  layer + boundary discipline)
- **Operating cost:** similar to Foundry-only (warehouse savings on the
  Snowflake side roughly offsets Foundry-side licensing on the
  investigator workload)
- **Engineering capacity required:** highest of the three approaches
  (need both Foundry-specific and Snowflake/DBT skill sets, plus the
  integration-boundary expertise)
- **Strategic optionality:** highest (warehouse layer is portable;
  Foundry surface can be reduced or expanded with budget changes)

## Operational discipline required

The hybrid pattern is the easiest to mismanage. Specific disciplines the
institution must maintain:

- **Single source of truth designation per data class.** No ambiguity
  about whether the warehouse copy or the Foundry copy is authoritative.
- **Sync-lag observability** at the investigator surface (analysts see
  the data freshness in their UI; institution monitors the metric).
- **Cross-boundary audit reconciliation** as a quarterly self-assessment.
- **Disaster-recovery design** that handles each side independently
  (Foundry-side outages must not destroy warehouse data; warehouse-side
  outages must not corrupt the Foundry investigator state).

The hybrid pattern works when the institution treats the boundary as a
first-class architectural concern. It fails when the boundary is treated
as plumbing.
