#!/usr/bin/env python3
"""Citation-check validator for AIP adverse_media_summary output.

For each factual_assertion in the AIP output, verifies that source_passage is
a substring of the article identified by source_article_id (after whitespace
normalization and case-insensitive match). Any failed assertion drops the
overall output to insufficient_corpus = true and routes the item for human
review.

Run:
    python citation_check.py --aip-output <path> --news-corpus <path>

Exit codes:
    0 = all citations validate
    1 = one or more citation failures (output rejected per hallucination_gate.yaml)
    2 = schema or input error
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path


def normalize(s: str) -> str:
    """Whitespace-collapse + lowercase for substring matching."""
    return re.sub(r"\s+", " ", s).strip().lower()


def validate_citation(assertion: dict, corpus: dict[str, dict]) -> tuple[bool, str]:
    """Return (passed, reason). assertion is one factual_assertions[] entry."""
    aid = assertion.get("source_article_id")
    passage = assertion.get("source_passage", "")
    if aid not in corpus:
        return False, f"source_article_id {aid!r} not present in news_corpus"
    article = corpus[aid]
    article_body = article.get("body", "")
    if normalize(passage) not in normalize(article_body):
        return False, f"source_passage not a substring of article {aid!r} body (post-normalization)"
    return True, "ok"


def check(aip_output: dict, news_corpus: list[dict]) -> dict:
    """Run all citation checks. Return a structured result."""
    corpus_by_id = {a["article_id"]: a for a in news_corpus}
    assertions = aip_output.get("factual_assertions", [])
    failures = []
    for idx, a in enumerate(assertions):
        passed, reason = validate_citation(a, corpus_by_id)
        if not passed:
            failures.append({"assertion_index": idx, "assertion": a, "reason": reason})
    return {
        "n_assertions": len(assertions),
        "n_failures": len(failures),
        "all_passed": len(failures) == 0,
        "failures": failures,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--aip-output", type=Path, required=True,
                   help="Path to AIP function's JSON output")
    p.add_argument("--news-corpus", type=Path, required=True,
                   help="Path to JSON file with news_corpus array")
    args = p.parse_args()

    try:
        aip_output = json.loads(args.aip_output.read_text())
        news_corpus = json.loads(args.news_corpus.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if not isinstance(news_corpus, list):
        news_corpus = news_corpus.get("articles", [])

    result = check(aip_output, news_corpus)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["all_passed"] else 1)


if __name__ == "__main__":
    main()
