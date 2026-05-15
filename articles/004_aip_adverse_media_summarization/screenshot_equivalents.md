# Screenshot Equivalents — Foundry AIP Adverse-Media Summarization

Text-based renderings of the Foundry AIP screens the article references. The
companion bundle is portable (YAML / JSON / Python), not a live Foundry export;
these screen-equivalents help readers map the bundle's artifacts to the AIP
UI they would see in a production deployment.

## AIP Function Editor — `adverse_media_summary`

```
┌─ AIP Function: adverse_media_summary ─────────────────────────────────────────┐
│                                                                                │
│  Target ontology object  Counterparty                                          │
│  Output schema           grounded_summary_schema.json                          │
│  Status                  draft (not deployed)                                  │
│                                                                                │
│  ┌─ Inputs ─────────────────────────────────────────────────────────────────┐ │
│  │  news_corpus       → AdverseMediaMention[Counterparty] (90-day lookback) │ │
│  │  prior_risk_rating → Counterparty.risk_rating                            │ │
│  │  jurisdiction      → Counterparty.jurisdiction                           │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ System prompt ──────────────────────────────────────────────────────────┐ │
│  │  [See prompts/adverse_media_summarization_prompt.md — system prompt]     │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌─ Output validation chain ────────────────────────────────────────────────┐ │
│  │  1. schema_validate            [blocking]                                │ │
│  │  2. citation_substring         [blocking]    tool: citation_check.py    │ │
│  │  3. hallucination_verifier_llm [advisory]    tool: verifier_prompt      │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  [ Test ▸ ]  [ Save ]  [ Deploy ▸ ]                                            │
└────────────────────────────────────────────────────────────────────────────────┘
```

## AIP Function Test Result — Meridian Holdings (synthetic)

```
┌─ Test Run #1234  ─────────────────────────────────────────────────────────────┐
│  Counterparty: Meridian Holdings (Pte) Ltd  (CP-SYNTH-00042, Singapore)       │
│  Corpus:       4 articles, 90-day lookback                                    │
│  Started:      2026-05-15 07:30:12 UTC                                        │
│  Duration:     3.7s (generation 2.1s, validation 1.6s)                        │
│                                                                                │
│  ── Generation ──                                                              │
│    summary_text: "Three open adverse-media signals concentrated in the…"      │
│    factual_assertions: 8                                                      │
│    rating_pressure_direction: upward                                          │
│    rating_pressure_strength:  medium                                          │
│    insufficient_corpus: false                                                 │
│    items_flagged_for_human_review: 3                                          │
│                                                                                │
│  ── Validation ──                                                              │
│    schema_validate         ✓ PASS                                              │
│    citation_substring      ✓ PASS  (8/8 assertions)                            │
│    hallucination_verifier  ✓ PASS  (8 SUPPORTED, 0 NOT_SUPPORTED, 0 AMBIG.)    │
│                                                                                │
│  ── Routing ──                                                                 │
│    Output: ACCEPTED → Counterparty.adverse_media_summary (write Action)        │
│    Review queue: 3 items added to analyst.review_queue                        │
│                                                                                │
│  [ View output ▸ ]  [ View raw LLM trace ▸ ]                                  │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Workshop Review Queue — analyst surface

```
┌─ Adverse-Media Review Queue ─ Counterparty: Meridian Holdings ────────────────┐
│                                                                                │
│  Generated 2026-05-15 07:30 UTC  •  Model output flag: ADVISORY (not action)  │
│                                                                                │
│  ┌─ Summary ────────────────────────────────────────────────────────────────┐ │
│  │ Three open adverse-media signals concentrated in the 90-day lookback.    │ │
│  │ (1) A civil complaint filed 2026-04-29 in Singapore High Court names     │ │
│  │ Meridian Holdings among three specialty-chemical trading defendants…     │ │
│  │ [expand]                                                                  │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  Suggested rating pressure: ▲ UPWARD  •  Strength: ●●○ MEDIUM (advisory)      │
│                                                                                │
│  ┌─ Items for analyst judgment ─────────────────────────────────────────────┐ │
│  │ ☐ Civil complaint at pleadings stage; escalate before substantive resp.? │ │
│  │ ☐ Four documentation holds is high — weigh non-enforcement framing      │ │
│  │ ☐ Q1 revenue announcement omitted both adverse signals — disclosure?    │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  Analyst decision: [ Accept summary ] [ Edit ] [ Reject + add notes ]         │
│                                                                                │
│  Rating action: [ Maintain ] [ Downgrade ▸ ]  (logs via Article 005 Actions)  │
└────────────────────────────────────────────────────────────────────────────────┘
```

## Source articles, on-hover citation modal

```
┌─ Source: AM-003 ──────────────────────────────────────────────────────────────┐
│  Source:   (SYNTHETIC) Asian Compliance Review                                 │
│  Date:     2026-05-02                                                          │
│  Headline: Civil suit filed against three specialty-chemical traders over     │
│            alleged labeling discrepancies                                      │
│                                                                                │
│  Cited passage (verbatim, substring-validated):                                │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ "A civil complaint filed in Singapore High Court on 2026-04-29 names   │  │
│  │ three specialty-chemical trading firms — including Meridian Holdings   │  │
│  │ (Pte) Ltd — as defendants in a labeling-discrepancy matter"            │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  [ View full article ▸ ]                                                       │
└────────────────────────────────────────────────────────────────────────────────┘
```

These layouts are illustrative — the actual Foundry UI differs by version. The
patterns (function editor, test result, review queue, citation modal) are stable
across versions.
