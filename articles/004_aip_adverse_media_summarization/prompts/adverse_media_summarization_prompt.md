# AIP Adverse-Media Summarization Prompt

Reusable Palantir AIP prompt pattern for adverse-media review at scale. Designed
for RAG-style grounding with structured-output enforcement, citation
post-processing, and a verifier-LLM hallucination gate. Model-agnostic — AIP
routes the prompt across whichever provider the institutional deployment
configures (Anthropic, OpenAI, Mistral, etc.).

## AIP function definition

```yaml
aip_prompt: adverse_media_summary
target_ontology_object: Counterparty
inputs:
  - news_corpus: AdverseMediaMention objects linked to Counterparty
                 (lookback = 90 days)
  - prior_risk_rating: Counterparty.risk_rating
  - jurisdiction: Counterparty.jurisdiction

output_schema_ref: schemas/grounded_summary_schema.json

output_validation:
  - schema: jsonschema_validate
  - citation_check: every factual_assertion.source_passage must be a substring
                    of the article identified by source_article_id (tools/citation_check.py)
  - hallucination_check: pass each factual_assertion through a verifier-LLM call
                         against the cited passage (tools/verifier_prompt_template.md)
```

## System prompt

```
You are an analyst reviewing adverse-media coverage for due-diligence
risk-rating purposes. Produce a structured summary with explicit citations.

You MUST NOT make any factual assertion that is not directly supported by a
cited source-article passage. The source_passage field for each factual
assertion must be a verbatim substring of the named source article — not a
paraphrase, not a summary, not an inference.

If the corpus is insufficient to produce a meaningful summary (fewer than
three substantive articles, or all articles cover the same single event), set
insufficient_corpus = true and explain the gap in summary_text. Producing
plausible-but-empty text on a thin corpus is the failure mode this control
exists to prevent.

For ambiguous items — claims that may be material but require a specific
analyst judgment call (e.g., whether a lawsuit allegation rises to a risk
escalation) — populate items_flagged_for_human_review rather than asserting a
direction yourself. The summary augments analyst judgment; it does not
substitute for it.
```

## User prompt template

```
Counterparty: {legal_name} ({jurisdiction})
Current risk rating: {prior_risk_rating}
News corpus ({n_articles} articles, last 90 days):

{articles_with_ids}

Produce a JSON object conforming to grounded_summary_schema.json. The
summary_text field should not exceed 200 words. Every factual_assertion
entry must include a source_passage that appears verbatim in the article
identified by source_article_id.
```

## Operating notes

- The lookback window (default 90 days) is institution-configurable; the AIP
  Function should accept it as an input rather than hard-coding.
- For thin-corpus jurisdictions (e.g., emerging-market counterparties with
  little English-language coverage), the `insufficient_corpus = true` branch
  is the expected and correct output — not a failure of the prompt.
- The `rating_pressure_direction` and `rating_pressure_strength` fields are
  ADVISORY signals for the analyst's review queue prioritization; they do not
  drive automated rating changes. SR 11-7 / OCC 2011-12 compliance posture
  requires a human-in-the-loop on every rating action.
- The Workshop application's review queue consumes `items_flagged_for_human_review`
  directly (see Article 003 companion bundle for the Actions wiring).

## Voice / drafting discipline (for the article, not the bundle)

- Do not name specific LLM providers gratuitously; the pattern is provider-agnostic.
- The grounding pattern (citation_check + verifier_LLM) is the editorial centerpiece.
- The insufficient_corpus failure mode is the single most important section.
- Model-evaluation methodology must be specific — vague "we tested it" fails.

## Authority anchors

- Palantir AIP documentation: Functions, Logic, Output Schemas, Grounding
- Anthropic Constitutional AI / prompt-engineering guidance
- Lewis et al. (2020), "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", NeurIPS
- Ji et al. (2023), "Survey of Hallucination in Natural Language Generation", ACM Computing Surveys 55(12)
- Federal Reserve SR 11-7 / OCC Bulletin 2011-12 — Model Risk Management
- FFIEC BSA/AML Examination Manual — adverse-media review expectation framing
