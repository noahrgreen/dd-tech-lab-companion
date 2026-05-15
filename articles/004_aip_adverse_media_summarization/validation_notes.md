# Validation Notes — Article 004 Companion Bundle

## Validation scope

- **Prompt YAML** mirrors the seed's AIP prompt pattern: target_ontology_object, inputs (news_corpus, prior_risk_rating, jurisdiction), system_prompt, user_prompt_template, output_validation chain (schema + citation_check + hallucination_check).
- **Output schema** is a valid JSON Schema (draft 2020-12) with all 6 fields from seed §"AIP prompt pattern": summary_text, factual_assertions[], rating_pressure_direction, rating_pressure_strength, insufficient_corpus, items_flagged_for_human_review. Verified with `jsonschema.Draft202012Validator.check_schema()`.
- **Citation-check tool** (tools/citation_check.py) implements substring-match-after-whitespace-normalization-and-case-fold per the seed's citation-check post-processor specification. Verified end-to-end against synthetic corpus + sample output: 8/8 assertions pass.
- **Hallucination-check verifier** (tools/verifier_prompt_template.md) provides the two-stage approach the seed §5 describes: substring check first, faithfulness assessment second. Verifier prompt is provider-agnostic.
- **Synthetic corpus** (synthetic_data/adverse_media_corpus.json) contains 4 fully-fabricated adverse-media items about a fully-fabricated counterparty (Meridian Holdings Pte Ltd, jurisdiction Singapore). Articles cover the mix of signals the article walks: port-documentation holds (operational), civil suit at pleadings (legal), regulator's compliance-dialogue framing (regulatory), Q1 revenue announcement (offsetting positive).
- **Sample AIP output** (sample_output/aip_summary_output_example.json) demonstrates what a passing run looks like: 8 grounded factual assertions, 3 items flagged for human review, advisory rating-pressure signal (upward / medium). Verified to pass both schema validation and citation_check.py.

## Known limits

- This is a portable companion bundle, not a live Foundry AIP deployment. No actual AIP Function exists here; the YAML describes the function definition.
- The hallucination-check verifier is a prompt template — running it requires hooking it to an LLM provider, which is institution-specific.
- The synthetic counterparty + adverse-media corpus are demonstration-only. Any resemblance to real organizations is coincidental. Do not use this corpus for production prompt-engineering tuning — build a real labeled holdout set per seed §"Model-evaluation methodology".
- The verifier-LLM precision/recall estimates in tools/verifier_prompt_template.md ("calibration notes" section) are illustrative ranges, not measured values for any specific provider/model. Calibrate before promoting `blocking: false → true` in hallucination_gate.yaml.
- Rating-pressure fields are explicitly ADVISORY ONLY per the gate `no_automated_rating_action`. Article 005's Actions framework wires the human review-and-acceptance event that any rating change actually requires; this bundle does not implement that handoff.

## Validation tools (reproducibility)

```bash
# Schema check
python3 -c "import json, jsonschema; s=json.load(open('schemas/grounded_summary_schema.json')); jsonschema.Draft202012Validator.check_schema(s); print('schema OK')"

# Sample output validates against schema
python3 -c "
import json, jsonschema
s = json.load(open('schemas/grounded_summary_schema.json'))
o = json.load(open('sample_output/aip_summary_output_example.json'))
errs = list(jsonschema.Draft202012Validator(s).iter_errors(o))
print('OK' if not errs else errs)"

# Citation check on sample
python3 tools/citation_check.py \
  --aip-output sample_output/aip_summary_output_example.json \
  --news-corpus synthetic_data/adverse_media_corpus.json
# Expected: n_failures=0, all_passed=true, exit code 0
```

## Regulatory framing reminder

SR 11-7 / OCC 2011-12 apply. LLM-generated summaries are model output; the
audit trail must capture (a) the AIP output, (b) the analyst's review-and-acceptance
decision, (c) any rating action that follows. This bundle's contribution is the
generation + first-line validation layer; downstream audit-trail wiring is
Article 005's scope.
