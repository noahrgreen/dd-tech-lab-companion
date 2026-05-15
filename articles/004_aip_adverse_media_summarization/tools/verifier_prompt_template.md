# Hallucination-Check Verifier Prompt Template

Second-pass LLM call run after citation_check.py passes. The citation check
confirms `source_passage` is a substring of the cited article; the verifier
confirms the `assertion` is faithfully supported by `source_passage` (not just
substring-matched).

Run independently per `factual_assertion`. Cheap-model is fine (verifier
quality dominates over generator latency on accuracy).

## System prompt

```
You are an adverse-media-summary verifier. Your job is to assess whether a
proposed factual assertion is faithfully supported by the cited source passage.

Do NOT use any outside knowledge. Use ONLY the passage provided. If the
passage does not support the assertion — including cases where the passage
mentions related facts but not the specific assertion — answer NOT_SUPPORTED.

Faithful support means: a careful reader would conclude the passage entails
the assertion, with no inferential leap beyond what the passage states.
Paraphrase is allowed; extrapolation is not.
```

## User prompt template

```
Source passage:
{source_passage}

Proposed assertion:
{assertion}

Reply with one of:
- SUPPORTED
- NOT_SUPPORTED
- AMBIGUOUS

If NOT_SUPPORTED or AMBIGUOUS, follow the verdict with a one-sentence reason.
```

## Routing

- `SUPPORTED` → assertion passes hallucination check, included in final output
- `NOT_SUPPORTED` → assertion REMOVED from factual_assertions[]; assertion text moved to items_flagged_for_human_review[] with prefix "Removed by verifier: "
- `AMBIGUOUS` → assertion retained but added to items_flagged_for_human_review[] with prefix "Verifier ambiguous: "

If `factual_assertions[]` empties out post-verification, set
`insufficient_corpus = true` and write a summary_text noting the corpus
covered facts the model could not faithfully ground.

## Calibration notes

- Run verifier on a labeled holdout set before promoting blocking: false → true in hallucination_gate.yaml
- Expected verifier-LLM precision on cited-passage assessments: ~0.92-0.96 at production scale
- Expected verifier-LLM recall: ~0.88-0.93 (some genuinely-supported assertions get NOT_SUPPORTED on first pass — accept the lower recall in exchange for the higher precision; missed-positives go through the human review queue)
- Two-stage approach trades latency for confidence — total wall time per counterparty ~2-3x single-pass; acceptable for batch DD workflows, not for interactive UX

## Operating reminder

The verifier is the apparatus that lets human judgment scale, not the
apparatus that replaces it. Every assertion that survives both gates still
gets a human review-and-acceptance event before driving any rating action,
per SR 11-7 / OCC 2011-12.
