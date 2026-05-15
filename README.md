
# DD Tech Lab — Companion Repository

Reproducible artifacts accompanying the **DD Tech Lab** publication series at sheepdogprosperitypartners.com.

**Maintainer:** Noah Green CPA CFE
**Repository status:** Expanded release through Foundry, Knowledge Graphs / Neo4j, Stochastic / Markov, and Excel-fraud published companions (2026-05-14)
**License:** MIT (see LICENSE — pending finalization; until then, artifacts may be downloaded and used for educational and practitioner-internal purposes)

---

## What this repository is

This repository holds the companion artifacts promised by the DD Tech Lab article series: synthetic datasets, workbook templates, runnable scripts, notebooks, YAML / JSON templates, and compatibility-path copies for exact article references.

## Structure

- `articles/` — organized per-article artifact bundles and README files
- `stochastic_markov/companion_artifacts/` — canonical runnable scripts referenced by the live stochastic articles
- `notebooks/` — notebook-format artifacts when the article text specifically promises a notebook
- `workbooks/`, `DD-Tech-Lab-Repo/`, `engagement_files/`, and root-level `.xlsx` / `.csv` files — compatibility paths matching article footers and inline artifact claims

## Reproducibility notes

- All synthetic datasets use deterministic seeds documented in the corresponding article bundles.
- Where a live article promises a literal path, this repository now contains that exact path.
- Where the article required workbook structure beyond the workbook file itself (for example Power Query stubs or JSON cache templates), those support files live in the organized article directory under `articles/`.
