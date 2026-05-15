# Decision Archetypes — Platform-Selection Patterns

Companion artifact for Foundry Article 010. Three institutional archetypes
that emerge from the comparison framework. Each archetype's typical
right answer is contingent on the institution's actual situation; the
archetypes are starting points for the institution's own decision
discussion, not verdicts.

## Archetype 1: Large bank with high compliance burden

**Profile:** Tier-1 or Tier-2 bank; SR 11-7 model risk management mature;
SOX §404 controls already documented; OCC / Fed examination cycle is
active; engineering team 30+ across data + platform; budget envelope
$10M+ for the relevant build; risk-tech leadership has board visibility.

**Typical priorities:**
- Regulatory documentation maturity (built-in audit trail primitives)
- Predictable cost (annual budget; avoid consumption-pricing surprises)
- Vendor partnership maturity (vendor support track record on compliance
  cases)
- Integration with existing compliance technology stack
- Implementation risk (the build itself must not become a 24-month
  regulatory exposure)

**Typical right answer (with the typical caveats):**
> Foundry is the typical right answer for this archetype IF the institution
> can absorb the lock-in posture as a strategic risk. The
> built-in Ontology + Workshop + Actions value-add closes the
> regulatory-documentation gap that Snowflake or Databricks would require
> the institution to build itself; the build cost saved + the vendor's
> regulatory-focus product positioning typically justify the lock-in for
> this archetype.
>
> The case AGAINST Foundry for this archetype: institutions with an
> existing significant Snowflake or Databricks footprint, mature
> compliance-tech build capabilities, and conservative lock-in posture.
> For those institutions, the cost of building the ontology + audit-trail
> layer is amortizable against the existing platform investment, and the
> lock-in concern dominates.

**Examiner-readiness framing:** Article 005's bypass-control discipline
applies regardless of platform. No vendor decision substitutes for the
institution's overall control environment. The vendor choice affects
where the controls live, not whether they're required.

## Archetype 2: Mid-size advisory shop with cost sensitivity

**Profile:** 50-200-person advisory / consulting firm; client engagements
drive workload; regulatory burden present (typically AML/KYC for the
firm's own AUM, plus advisory-related compliance) but lighter than a
tier-1 bank; engineering team 5-15; cost-discipline is the dominant
constraint; flexibility to scale up/down with engagement cadence is
valuable.

**Typical priorities:**
- Total cost of ownership over 5 years (the bulk of TCO is consumption-
  variable, not licensed)
- Skill alignment (SQL + Python developers, not Palantir-specific)
- Ability to scale down between engagements
- Lower lock-in (the firm may shift strategy faster than a bank)
- Adequate (not maximum) regulatory documentation maturity

**Typical right answer (with the typical caveats):**
> Snowflake + DBT is typically the right answer for this archetype.
> Consumption pricing aligns with the firm's actual workload; SQL + Python
> skill alignment matches the talent pool the firm hires from; the
> portability lowers strategic risk if the firm's tech strategy shifts.
> The "build the ontology layer yourself" cost is the meaningful
> trade-off — but for a 50-200-person firm, the absence of the
> Foundry-bundled value-add (Workshop, Ontology, Actions) is recoverable
> with proportionally smaller engineering investment than a tier-1 bank
> would face.
>
> The case AGAINST Snowflake + DBT for this archetype: firms with
> a Palantir-aligned customer mix (e.g., government or defense clients
> who use Foundry themselves, generating workflow demand on the same
> platform), or firms whose primary work product requires Foundry-
> proprietary patterns. Those firms benefit from platform alignment
> with their customer base even at higher cost.

**Examiner-readiness framing:** The mid-size advisory shop has the
flexibility to build the audit-trail discipline on top of Snowflake / DBT
without bank-scale resources; the build is tractable and the result is
fully portable. Investment in the build is itself a strategic asset.

## Archetype 3: PE-DD firm with intermittent heavy use

**Profile:** Private-equity-focused due-diligence firm; engagements are
episodic and high-intensity (10-12 weeks of dense investigation,
followed by weeks of low platform use); each engagement has its own
client confidentiality requirements; the platform must accommodate both
peak workload and quiet periods without cost penalty during the quiet
periods.

**Typical priorities:**
- Cross-engagement portability (data and analyses must move between
  engagements; vendor lock-in directly conflicts with the engagement-
  isolation requirement)
- Consumption pricing that aligns with the intermittent-heavy-use
  pattern (high spike usage during engagements; near-zero between)
- Investigator UI that supports rapid analyst ramp-up per engagement
- LLM integration for adverse-media review at scale (each engagement
  involves significant adverse-media review under tight timelines)
- Regulatory documentation maturity matters but the audit-trail surface
  is narrower (fewer regulated state changes per engagement than a bank
  generates per quarter)

**Typical right answer (with the typical caveats):**
> The hybrid pattern is typically the right answer for this archetype.
> Foundry for the investigator-surface workload during peak engagements
> (Workshop applications, Quiver queries, AIP-driven adverse-media review)
> rides on top of a Snowflake or Databricks warehouse layer holding the
> firm's portable analytic foundation. The Foundry side scales up and
> down with engagement cadence; the warehouse side retains cross-
> engagement data assets without vendor lock-in.
>
> The hybrid pattern's implementation cost is higher than either single-
> vendor approach in year 1, but the cross-engagement portability of the
> warehouse layer + the investigator-surface productivity of the Foundry
> layer typically justify the integration complexity over 5 years.
>
> The case AGAINST the hybrid pattern: firms with engagement counts low
> enough that the integration complexity exceeds the productivity benefit.
> Below ~10 active engagements per year, the simpler single-vendor
> approach (Snowflake + DBT + Streamlit, building the investigator
> surface as needed) may dominate.

**Examiner-readiness framing:** PE-DD firms typically have lighter
regulatory documentation requirements than banks (their clients carry the
regulatory burden; the firm's own platform decisions are more
operationally focused than compliance-focused). The audit-trail
discipline still applies but is narrower in scope.

## How to use the archetypes

The institution should:

1. **Identify the closest archetype.** Most institutions are 60-80%
   one archetype with 20-40% characteristics of another. Note which.
2. **Run the weight elicitation** against the closest-archetype preset
   weights (see `templates/platform_evaluation_weights.yaml`) AS A
   STARTING POINT, not as a verdict. Adjust weights based on the
   institution's actual situation.
3. **Score each platform** against the scorecard
   (`decision_matrix/platform_tradeoff_scorecard.csv`).
4. **Compute weighted scores** for each platform.
5. **Run sensitivity analysis** by perturbing the top-weighted dimensions
   ±0.10 and recomputing. If the platform ranking flips under reasonable
   weight perturbations, the institution has not yet converged on a
   confident decision — additional discussion is warranted.
6. **Document the decision rationale** including weights, scoring, and
   sensitivity results. This documentation is what later answers "why
   did we pick this platform" when the question comes up in a board
   review or examiner conversation.

The archetypes are starting points. The institution's actual situation
will diverge in important ways, and the article's purpose is to give the
architect the framework to reason about the divergence — not a one-size-
fits-all verdict.
