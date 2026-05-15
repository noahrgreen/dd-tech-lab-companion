# Foundry Article 010 — Companion Bundle

**Title:** Foundry vs Snowflake + DBT vs Databricks for DD Analytics — Architecture Trade-Off Framework

**Series:** Palantir Foundry for Due Diligence
**Article ID:** SPP-DD-TECH-FOUNDRY-010
**Bundle status:** `validated_bundle`
**Prepared by:** Noah Green CPA CFE

## What this bundle contains

| Path | Purpose |
|---|---|
| `decision_matrix/platform_tradeoff_scorecard.csv` | 10-dimension comparison: ontology layer, investigator UI, pipeline no-code, pipeline code path, LLM integration, audit trail, cost model, skill alignment, vendor lock-in, regulatory documentation maturity. Each cell qualifies the vendor's state in narrative text with an `assessment_as_of` date stamp. **No blanket built-in/build-yourself ratings without qualification.** |
| `templates/platform_evaluation_weights.yaml` | 3 archetype-preset weight profiles (large_bank_high_compliance, mid_size_advisory_cost_sensitive, pe_dd_intermittent_heavy_use) + weight-elicitation discipline section. Each archetype is explicitly framed as a starting point, not a recommendation. Includes elicitation validation checklist. |
| `tco_model/five_year_tco_template.yaml` | Parameterizable 5-year TCO component structure for all 3 archetypes. Every cost value is `REPLACE_WITH_VENDOR_QUOTE` — the template scaffolds the institution's own TCO analysis without prejudging the result. Qualitative-notes section per archetype. |
| `decision_archetypes/decision_archetypes.md` | 3 institutional archetypes (large bank, mid-size advisory, PE-DD firm) with priorities, typical-right-answer narrative, case-AGAINST narrative, examiner-readiness framing. |
| `hybrid_patterns/foundry_warehouse_hybrid.md` | The editorial value-add per the seed: when the right architecture is not "one platform" but Foundry for the investigator surface + Snowflake (or Databricks) for the warehouse layer. Reference architecture + boundary design decisions + cost/complexity trade-off + operational discipline. |
| `validation_notes.md` | Scope + known limits + reproducibility commands + the seed's critical-drafting-discipline reminder. |

## Quick start (validation reproducibility)

```bash
# Scorecard CSV parses
python3 -c "
import csv
with open('decision_matrix/platform_tradeoff_scorecard.csv') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    print(f'{len(rows)} dimensions; columns: {list(reader.fieldnames)}')"

# Weight presets sum to 1.0
python3 -c "
import yaml
w = yaml.safe_load(open('templates/platform_evaluation_weights.yaml'))
for archetype in ['large_bank_high_compliance', 'mid_size_advisory_cost_sensitive', 'pe_dd_intermittent_heavy_use']:
    s = sum(w[archetype].values())
    assert abs(s - 1.0) < 0.001, f'{archetype}: sum = {s}'
    print(f'{archetype}: sum = {s:.4f} OK')"
```

## CRITICAL framing discipline (per seed — highest PR-sensitivity)

This is the **highest PR-sensitivity article in the Foundry sub-series.**
Each of the three platforms is a publicly-traded or publicly-prominent
vendor. The bundle has been designed with these explicit discipline rules:

1. **No blanket feature ratings without qualification.** Every scorecard
   cell narrates the qualification — no "● built-in" / "○ build-
   yourself" symbols without text.
2. **Every comparison is date-stamped.** Every scorecard cell carries
   an `assessment_as_of` date inviting re-verification.
3. **No absolute "winner" framing.** The hybrid pattern is the editorial
   value-add; single-vendor approaches fit specific archetypes; no vendor
   is recommended in the abstract.
4. **No Gartner-as-scoring-authority citations.** The bundle does not
   cite Gartner placements as validating the comparison's ratings.
5. **TCO numbers are placeholders only.** Every cost value is a
   `REPLACE_WITH_VENDOR_QUOTE` marker.
6. **Decision archetypes carry "case AGAINST" framings.** Each archetype's
   typical-right-answer is paired with the case for considering an
   alternative.

## Article-pattern summary

9 sections per seed: why the comparison is hard → ontology-layer comparison
→ investigator-UI comparison → pipeline / transform-layer comparison →
LLM-integration comparison → audit-trail and regulatory documentation
comparison → cost model and TCO → decision archetypes → the hybrid pattern.
This bundle implements all 9 sections' supporting artifacts: the 10-dimension
scorecard, the 3 archetype weight profiles + elicitation discipline, the
parameterizable TCO template, the 3 decision archetypes with case-against
framings, and the hybrid-pattern reference architecture + boundary design.

## What the bundle does NOT do

- It does not recommend a vendor.
- It does not endorse a specific weight set.
- It does not provide TCO numbers usable for procurement without
  vendor-quote substitution.
- It does not assume the institution's overall control environment is
  sufficient regardless of vendor choice (Article 005's bypass-control
  framework applies on every platform).

The article and bundle exist to give the architect the comparison framework
rigorous enough that the resulting decision is defensible to the
institution's board, regulators, and successor teams.
