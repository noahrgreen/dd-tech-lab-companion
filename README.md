# DD Tech Lab — Companion Repository

Reproducible artifacts accompanying the **DD Tech Lab** publication series at sheepdogprosperitypartners.com.

**Maintainer:** Noah Green CPA CFE
**Repository status:** Initial release (Foundry sub-series article 001 artifacts published; subsequent article artifacts ship alongside their corresponding articles)
**License:** MIT (see LICENSE — pending finalization; until then, artifacts may be downloaded and used for educational and practitioner-internal purposes)

---

## What this repository is

This is the companion repository for the **DD Tech Lab** publication on Palantir Foundry, knowledge graphs, stochastic methods, and Excel-augmented fraud detection for Wall Street financial-statement auditors, FA/FDD officers, and DD analysts.

Each published article in the DD Tech Lab series ships with reproducible artifacts here. Artifacts vary by article type:

- **Ontology schemas** — parseable YAML files documenting object types, link types, and properties referenced in Foundry-sub-series articles
- **Synthetic datasets** — CSV / Parquet files matching the worked examples in each article (synthetic data only; no real counterparties, persons, or transactions)
- **Foundry SDK stubs** — illustrative Python `dataclass` representations of the ontology objects shown in each article (these are NOT runnable Foundry SDK calls — Foundry ontology creation runs through the Ontology Manager UI or actual Foundry SDK; the stubs are educational shape-only representations)
- **Workshop module specs** — JSON stubs documenting investigator-facing application layouts referenced in articles
- **Action templates** — YAML specifications for the ActionType definitions discussed in articles
- **Code notebooks** — Jupyter notebooks for the Stochastic, Excel-fraud, and Neo4j sub-series articles (executable Python / R / Cypher)

## What this repository is NOT

- This is **not a Palantir-supported reference implementation** — it is independent practitioner content
- These are **not production-grade Foundry deployments** — the schemas are illustrative; production institutions design ontology objects through their own Ontology Manager UI / SDK workflow with institutional review and governance
- The synthetic data is **fully synthetic** — no real counterparties, persons, transactions, or matters are represented; any resemblance to real entities is coincidental
- The author byline is **practitioner methodology** — the CPA / CFE credentials apply to the author's professional standing in audit and fraud-examination practice and do not imply Palantir endorsement of any specific architecture

## Repository structure

```
companion_repo_dd_tech_lab/
├── README.md                      (this file)
├── articles_index.md              (article-by-article artifact map)
├── articles/
│   ├── 001_foundry_ontology_counterparty_risk/
│   │   ├── README.md              (article-specific notes + reproduction steps)
│   │   ├── ontology_schema/       (parseable YAML schemas)
│   │   ├── synthetic_data/        (CSV worked-example datasets)
│   │   ├── foundry_sdk_stubs/     (illustrative Python dataclass representations)
│   │   ├── workshop_module/       (Workshop application JSON spec)
│   │   └── action_templates/      (ActionType YAML definitions)
│   ├── 002_pipeline_builder_dd_data_ingestion/   (forthcoming with Article 002 release)
│   ├── 003_workshop_application_patterns/        (forthcoming with Article 003 release)
│   └── ... (subsequent Foundry sub-series articles)
```

## Reproduction

Most artifacts here are documentation files (YAML, JSON, CSV, Markdown) that any text editor can open. Python stubs require Python 3.10+ and standard library only (no external dependencies for the Foundry-sub-series stubs). Notebooks for the Stochastic / Excel / Neo4j sub-series (when published) will list their dependencies in per-article `requirements.txt` files.

## Contact

For questions about specific artifacts, requests for artifacts ahead of public release, or to flag errors / suggest improvements: noah@sheepdogtax.com (or noah@noahgreencpa.com during the transition period). Source articles published at sheepdogprosperitypartners.com.

---

**Initial release: 2026-05-13**
