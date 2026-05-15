# Foundry Article 004 — Companion Bundle

**Title:** AIP-Driven Adverse-Media Summarization for DD Engagements — Prompt Patterns, Grounding Strategy, Hallucination Controls

**Series:** Palantir Foundry for Due Diligence
**Article ID:** SPP-DD-TECH-FOUNDRY-004
**Bundle status:** `validated_bundle`
**Prepared by:** Noah Green CPA CFE

## What this bundle contains

| Path | Purpose |
|---|---|
| `prompts/adverse_media_summarization_prompt.md` | Full AIP prompt pattern: function definition, system prompt, user prompt template, operating notes |
| `schemas/grounded_summary_schema.json` | JSON Schema (draft 2020-12) enforcing the 6-field structured output (`summary_text`, `factual_assertions[]`, `rating_pressure_direction`, `rating_pressure_strength`, `insufficient_corpus`, `items_flagged_for_human_review[]`) |
| `evaluations/hallucination_gate.yaml` | The 5-gate output-validation chain: schema_validate, citation_substring, hallucination_verifier_llm, insufficient_corpus_required_when_thin, no_automated_rating_action |
| `tools/citation_check.py` | Reusable substring-match validator. Run on AIP output to verify every `factual_assertion.source_passage` is a true substring of the cited article (whitespace-normalized, case-insensitive). |
| `tools/verifier_prompt_template.md` | Second-pass hallucination-check verifier prompt template (provider-agnostic) |
| `synthetic_data/counterparty.json` | One fully-fabricated counterparty (Meridian Holdings Pte Ltd, Singapore) |
| `synthetic_data/adverse_media_corpus.json` | 4 fully-fabricated adverse-media articles for demonstration |
| `sample_output/aip_summary_output_example.json` | Example passing AIP output: 8 grounded assertions, 3 review-queue items, advisory rating-pressure signal |
| `screenshot_equivalents.md` | Text-based renderings of the AIP Function Editor, Test Result, Review Queue, and Citation Modal screens |
| `validation_notes.md` | What this bundle validates, what it doesn't, reproducibility commands |

## Quick start (validation reproducibility)

```bash
# All commands run from this directory.

# 1. Schema is valid JSON Schema
python3 -c "import json,jsonschema; s=json.load(open('schemas/grounded_summary_schema.json')); jsonschema.Draft202012Validator.check_schema(s); print('schema OK')"

# 2. Sample output validates against schema
python3 -c "
import json, jsonschema
s = json.load(open('schemas/grounded_summary_schema.json'))
o = json.load(open('sample_output/aip_summary_output_example.json'))
errs = list(jsonschema.Draft202012Validator(s).iter_errors(o))
print('validates' if not errs else errs)"

# 3. Citation check passes on sample (n_failures=0, exit 0)
python3 tools/citation_check.py \
  --aip-output sample_output/aip_summary_output_example.json \
  --news-corpus synthetic_data/adverse_media_corpus.json
```

## Article-pattern summary

The article walks 8 sections: scale problem, AIP framing, structured output, citation check, hallucination check, insufficient-corpus handling, human-review handoff (forward-references Article 003), model-evaluation methodology. This bundle implements the pattern (prompt + schema + gates + citation tool + verifier template) and demonstrates a passing run end-to-end on synthetic data.

## What's NOT in this bundle

- A live Foundry AIP deployment (no AIP runtime in this repo)
- Hallucination-verifier-LLM precision/recall numbers (illustrative ranges given in `tools/verifier_prompt_template.md` — calibrate before promoting `blocking: false → true`)
- Article 005's downstream Actions wiring for the human review-and-acceptance event (separate companion bundle)
- A labeled holdout set for prompt-engineering tuning (institution-specific; build per the article's §"Model-evaluation methodology")

## Regulatory framing reminder

SR 11-7 / OCC 2011-12 apply. AIP-generated summaries are model output; the audit
trail must capture both the AIP output and the analyst's review-and-acceptance
decision. Rating actions require a human-in-the-loop event regardless of the
advisory `rating_pressure_*` fields' values.
