# Audit Considerations for Quiver Queries

Companion artifact for Foundry Article 007. Quiver queries are *read-only
investigation activity* — they produce **analyst activity logs**, not
**AuditEntry objects** (Article 005's pattern). This distinction has
real implications for the audit-trail discipline.

## What Quiver activity DOES capture

The platform-side activity log records:

- Query name + parameters at execution time
- User who ran the query
- Timestamp
- Result row count
- Share-link generation events (who shared, what query, with whom)

This activity log lives in the platform's audit-and-monitoring layer and
is typically retained per the institution's standard activity-log policy
(180 days to 1 year is common; institutional policy may extend).

## What Quiver activity does NOT capture

- The specific *rows* returned by the query at that point in time. The
  underlying ontology data may change between query executions; Quiver
  does not snapshot what the analyst actually saw.
- The analyst's interpretation of the result. A query returning 12
  counterparties exposed to issuer X tells the platform what the query
  returned; it does not tell the platform whether the analyst decided
  any of those 12 warranted further investigation, escalation, or rating
  action.
- The downstream decision triggered by the query. Quiver does not (and
  by design should not) write to ontology state. The decision that
  follows the query is captured separately, and only if the analyst
  triggers an ActionType per Article 005's framework.

## The implication for audit trail

When an examiner asks "what investigation occurred between the analyst
becoming aware of issuer X's news event on 2026-04-12 and the rating
elevation on 2026-04-15?", the answer must combine:

1. **AuditEntry records** (Article 005) — for the rating elevation
   itself, with timestamps, actor, justification, supporting evidence.
2. **Quiver activity logs** — for the investigative queries that informed
   the analyst's reasoning. Activity log shows which queries the analyst
   ran, with what parameters, and when.
3. **Analyst-side documentation** — for the narrative interpretation
   that ties the Quiver outputs to the rating decision. The justification
   text field on the AuditEntry is where this narrative lives.

The Quiver activity log alone is insufficient to reconstruct the
investigation. The AuditEntry alone is insufficient to show that
investigation was *thorough* (the regulator may want to know what
queries were considered and discarded, not just the one that
produced the cited evidence). The combination is what the audit
trail discipline requires.

## Failure mode to avoid

The most dangerous failure mode is treating a Quiver query result as
sufficient documentation in itself. A screenshot of a Quiver query
result is NOT an AuditEntry. If the analyst's decision to elevate
risk_rating relied on the query result, the result must be:

1. Captured as a supporting-evidence ObjectSet (per Article 005's
   ElevateRiskRating ActionType constraint).
2. Snapshotted via the ActionType's `supporting_evidence_snapshot_uri`
   field — because the underlying ontology data may drift after the
   query was run.
3. Referenced in the justification text on the AuditEntry.

Screenshots of Quiver query results pasted into informal documentation
(email, ticket, Word doc) are exactly the fragmented-audit-trail
failure mode that the Actions framework exists to eliminate. The
analyst's discipline is to use Quiver to *form* the judgment, and use
the Actions framework to *record* it.

## What the institution must do

- Train analysts on the read-only-vs-state-change distinction. Quiver
  is for forming judgments; Actions is for recording them.
- Retain Quiver activity logs at least as long as the relevant
  AuditEntries reference them (typically 7 years).
- Periodic-review the Quiver query activity for patterns that should be
  promoted to Workshop applications with proper Action wiring (the
  graduation criteria checklist).
- For high-stakes investigations (sanctions hits, EDD escalations,
  critical-rating elevations), require that the supporting evidence
  cited on the resulting AuditEntry include a snapshot of any Quiver
  result the analyst relied on — not just a reference to the query.

## Mapping to regulatory expectations

- **SR 11-7 §V** (documentation): Quiver activity logs contribute to the
  documentation chain but are not sufficient alone. The AuditEntry's
  justification text and supporting_evidence_snapshot_uri are the
  load-bearing artifacts.
- **FFIEC BSA/AML Examination Manual**: Examiners may ask "show me the
  investigation that preceded this CDD/EDD decision." The combined
  Quiver activity log + AuditEntry is the answer; either alone is
  insufficient.
- **PCAOB AS 2201**: For SOX §404 internal-controls testing, the
  AuditEntry population is what the auditor samples. Quiver activity
  logs are corroborating evidence, not primary controls.
