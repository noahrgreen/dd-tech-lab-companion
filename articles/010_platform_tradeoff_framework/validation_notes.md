# Validation Notes — Article 010 Companion Bundle

## Validation scope

- **Platform comparison scorecard** (`decision_matrix/platform_tradeoff_scorecard.csv`): 10 dimensions covering ontology layer, investigator UI, pipeline no-code, pipeline code path, LLM integration, audit trail, cost model, skill alignment, vendor lock-in, regulatory documentation maturity. Each cell qualifies the vendor's state in narrative text — no blanket "built-in / build-yourself" ratings without qualification per the seed's drafting discipline. Every cell carries an `assessment_as_of` date stamp (2026-05) explicitly inviting re-verification.
- **Evaluation weights** (`templates/platform_evaluation_weights.yaml`): 3 archetype-preset weight profiles (large_bank_high_compliance, mid_size_advisory_cost_sensitive, pe_dd_intermittent_heavy_use) PLUS a weight-elicitation discipline section describing the structured process the institution should run. Each archetype's weights are explicitly framed as starting points, not recommendations.
- **5-year TCO template** (`tco_model/five_year_tco_template.yaml`): parameterizable component structure for all 3 vendor archetypes (Foundry / Snowflake+DBT / Databricks+Unity). Every cost value is a `REPLACE_WITH_VENDOR_QUOTE` placeholder; the template scaffolds the institution's own TCO analysis without recommending specific cost numbers. Includes qualitative-notes section per archetype explaining how TCO components behave across years.
- **Decision archetypes** (`decision_archetypes/decision_archetypes.md`): 3 institutional archetype patterns with priorities, typical-right-answer narrative, case-against narrative, and examiner-readiness framing. Every "typical right answer" is qualified with the case AGAINST so the institution sees both sides of the trade-off.
- **Hybrid pattern** (`hybrid_patterns/foundry_warehouse_hybrid.md`): the editorial value-add the seed identifies. Reference architecture + boundary design decisions (which data lives on which side, sync mechanics, audit-trail boundary) + cost/complexity trade-off + operational discipline requirements.

## Validation reproducibility

```bash
# CSV parses as 10-row 6-column comparison
python3 -c "
import csv
with open('decision_matrix/platform_tradeoff_scorecard.csv') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    print(f'{len(rows)} dimensions; columns: {list(reader.fieldnames)}')"

# YAML files parse
python3 -c "
import yaml
for p in ['templates/platform_evaluation_weights.yaml',
          'tco_model/five_year_tco_template.yaml']:
    yaml.safe_load(open(p))
    print(f'{p}: parses')"

# Each weight profile sums to 1.0 ± 0.001
python3 -c "
import yaml
w = yaml.safe_load(open('templates/platform_evaluation_weights.yaml'))
for archetype in ['large_bank_high_compliance', 'mid_size_advisory_cost_sensitive', 'pe_dd_intermittent_heavy_use']:
    s = sum(w[archetype].values())
    assert abs(s - 1.0) < 0.001, f'{archetype}: sum = {s}'
    print(f'{archetype}: sum = {s:.4f} OK')"
```

## Known limits

- **Vendor state evolves quarterly.** Every cell in the scorecard carries an `assessment_as_of` date. Institutions must re-verify against current public vendor documentation before relying on the comparison for procurement. Specifically: Foundry AIP capabilities, Snowflake Cortex AI features, Snowflake Streamlit-on-Snowflake maturity, Databricks Unity Catalog ontology features, and Databricks Foundation Models integration are all on rapid release cadences.
- **TCO placeholders are NOT vendor pricing recommendations.** All cost values in `tco_model/five_year_tco_template.yaml` are `REPLACE_WITH_VENDOR_QUOTE` markers. Vendor quotes vary 2-3x by contract negotiation, deployment scope, and institutional volume; the template structures the analysis without prejudging the result.
- **Weight presets are starting points only.** The 3 archetype weight profiles are NOT verdicts. The weight-elicitation discipline in the template's commentary describes the structured process the institution should run with its own leadership.
- **Decision archetypes are not exhaustive.** Most institutions are a hybrid of 2 archetypes; some are entirely unique (e.g., a regulator or a multi-government consortium). The framework adapts to non-archetype situations through the weight-elicitation discipline.
- **No Gartner citations as scoring authority** per the seed's drafting discipline. The bundle references the comparison-methodology framing but no specific quadrant placement is cited as validating any vendor's score.
- **No specific institution identified.** Decision archetypes describe institutional patterns, not specific institutions. The bundle does not reference any institution's actual platform decision.

## Critical framing discipline (per seed)

The seed flagged this as the **highest PR-sensitivity article in the
Foundry sub-series.** Each of the three platforms is a publicly-traded or
publicly-prominent vendor; specific feature-comparison claims can be
disputed, and the article will be read with vendor-political scrutiny.

Drafting discipline preserved in this bundle:

1. **Every feature claim is qualified.** No blanket "built-in /
   build-yourself" ratings. Each cell narrates the qualification.
2. **Every comparison is date-stamped.** Every scorecard cell carries
   an `assessment_as_of` date. Readers are explicitly invited to
   re-verify.
3. **No absolute "winner" framing.** The hybrid pattern is the editorial
   value-add. Single-vendor approaches are reasonable for the archetypes
   they fit; the framework helps the institution decide which fits.
4. **No Gartner-as-scoring-authority citations.** The bundle does not
   cite Gartner Magic Quadrant placements as validating the comparison's
   ratings.
5. **TCO numbers are placeholders.** No specific cost recommendations.
6. **Decision archetypes carry "case AGAINST" framings.** Each archetype's
   typical-right-answer is paired with the case for considering an
   alternative.

## What the bundle does NOT do

- It does not recommend a vendor.
- It does not endorse a specific weight set.
- It does not provide TCO numbers usable for procurement without
  vendor-quote substitution.
- It does not assume the institution's overall control environment is
  sufficient regardless of vendor choice (see Article 005's bypass-
  control framework — that discipline applies on every platform).

The article and bundle exist to give the architect the comparison framework
rigorous enough that the resulting decision is defensible to the
institution's board, regulators, and successor teams.
