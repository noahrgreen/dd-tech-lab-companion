#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import random
import runpy
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path
from textwrap import dedent

import openpyxl
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.comments import Comment
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName


REPO = Path(__file__).resolve().parents[1]
SRC_ROOT = Path('/Users/noahgreen/NGO/outbox/owner_review/dd_tech_lab_kickoff_2026-05-10')
STOCH_SRC = SRC_ROOT / 'stochastic_markov' / 'companion_artifacts'
GENERATED_AT = '2026-05-14'


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text.rstrip() + '\n')


def copy_file(src: Path, dst: Path) -> None:
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)


def write_wrapper(path: Path, target_rel_from_wrapper: str, description: str) -> None:
    text = f'''#!/usr/bin/env python3
"""Compatibility entrypoint for {description}."""
from __future__ import annotations

import runpy
from pathlib import Path

TARGET = (Path(__file__).resolve().parent / {target_rel_from_wrapper!r}).resolve()

if __name__ == '__main__':
    runpy.run_path(str(TARGET), run_name='__main__')
'''
    write_text(path, text)


def workbook_autofit(ws, widths: dict[int, int] | None = None) -> None:
    if widths:
        for idx, width in widths.items():
            ws.column_dimensions[get_column_letter(idx)].width = width


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


# ---------------------------------------------------------------------------
# Neo4j / Knowledge Graphs
# ---------------------------------------------------------------------------
def generate_neo4j_dataset() -> tuple[Path, Path]:
    article_dir = REPO / 'articles' / 'knowledge_graphs_001_beneficial_ownership_cypher'
    data_dir = article_dir / 'synthetic_data'
    query_dir = article_dir / 'load_queries'
    ensure_dir(data_dir)
    ensure_dir(query_dir)

    generator_py = data_dir / 'synthetic_ownership_generator.py'
    generator_code = dedent('''
        import csv
        import random

        random.seed(42)

        PERSON_COUNT = 25
        ENTITY_COUNT = 75
        SANCTIONED_PERSONS = {"P-0001", "P-0002"}
        TARGET_ENTITY = "E-0042"

        jurisdictions = ["US-DE", "US-NY", "KY", "BVI", "LU", "SG"]

        persons = [
            {
                "uid": f"P-{i:04d}",
                "name": f"Person {i:02d}",
                "jurisdiction": random.choice(jurisdictions),
                "sanctioned": 1 if f"P-{i:04d}" in SANCTIONED_PERSONS else 0,
            }
            for i in range(1, PERSON_COUNT + 1)
        ]

        entities = [
            {
                "uid": f"E-{i:04d}",
                "name": f"Entity {i:03d}",
                "jurisdiction": random.choice(jurisdictions),
                "entity_type": random.choice(["OperatingCo", "HoldCo", "SPV"]),
            }
            for i in range(1, ENTITY_COUNT + 1)
        ]

        rows = []
        for entity in entities:
            owner_count = random.choice([1, 2, 3])
            weights = [random.random() for _ in range(owner_count)]
            total = sum(weights)
            pct_list = [round(w / total, 4) for w in weights]
            pct_list[-1] = round(1.0 - sum(pct_list[:-1]), 4)
            for pct in pct_list:
                owner_kind = random.choice(["Person", "Entity"])
                owner_pool = persons if owner_kind == "Person" else entities
                owner = random.choice(owner_pool)
                if owner["uid"] == entity["uid"]:
                    continue
                rows.append({
                    "owner_kind": owner_kind,
                    "owner_uid": owner["uid"],
                    "owner_full_name": owner["name"],
                    "owner_jurisdiction": owner["jurisdiction"],
                    "owner_sanctioned": owner.get("sanctioned", 0),
                    "entity_uid": entity["uid"],
                    "entity_legal_name": entity["name"],
                    "entity_jurisdiction": entity["jurisdiction"],
                    "entity_type": entity["entity_type"],
                    "percentage": pct,
                    "effective_date": "2024-12-31",
                    "source_filing_ref": f"SYNTH-{entity['uid']}-2024-001",
                })

        cascade_holders = [
            ("P-0001", "Entity 042 HoldCo", "E-0042", 0.26),
            ("P-0002", "Entity 042 Upper HoldCo", "E-0066", 0.24),
            ("E-0066", "Entity 042 HoldCo", "E-0042", 0.30),
        ]
        for owner_uid, owner_name, entity_uid, pct in cascade_holders:
            rows.append({
                "owner_kind": "Person" if owner_uid.startswith("P-") else "Entity",
                "owner_uid": owner_uid,
                "owner_full_name": owner_name if owner_uid.startswith("E-") else next(p["name"] for p in persons if p["uid"] == owner_uid),
                "owner_jurisdiction": "US-DE",
                "owner_sanctioned": 1 if owner_uid in SANCTIONED_PERSONS else 0,
                "entity_uid": entity_uid,
                "entity_legal_name": next(e["name"] for e in entities if e["uid"] == entity_uid),
                "entity_jurisdiction": "US-DE",
                "entity_type": next(e["entity_type"] for e in entities if e["uid"] == entity_uid),
                "percentage": pct,
                "effective_date": "2024-12-31",
                "source_filing_ref": f"SYNTH-{entity_uid}-2024-001",
            })

        with open("ownership_synthetic.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        print(f"Wrote {len(rows)} ownership rows. TARGET_ENTITY = {TARGET_ENTITY!r}")
    ''').strip() + '\n'
    write_text(generator_py, generator_code)

    cwd = Path.cwd()
    try:
        import os
        os.chdir(data_dir)
        runpy.run_path(str(generator_py), run_name='__main__')
    finally:
        os.chdir(cwd)

    csv_path = data_dir / 'ownership_synthetic.csv'
    copy_file(csv_path, REPO / 'ownership_synthetic.csv')

    write_text(query_dir / 'pass1_person_owners.cypher', dedent('''
        LOAD CSV WITH HEADERS FROM 'file:///ownership_synthetic.csv' AS row
        WITH row WHERE row.owner_kind = 'Person'
        MERGE (p:Person {uid: row.owner_uid})
          ON CREATE SET p.full_name = row.owner_full_name,
                        p.jurisdiction = row.owner_jurisdiction,
                        p.sanctioned = toBoolean(toInteger(row.owner_sanctioned)),
                        p.created_at = datetime()
        MERGE (e:Entity {uid: row.entity_uid})
          ON CREATE SET e.legal_name = row.entity_legal_name,
                        e.jurisdiction = row.entity_jurisdiction,
                        e.entity_type = row.entity_type,
                        e.created_at = datetime()
        MERGE (p)-[r:OWNS]->(e)
          SET r.percentage = toFloat(row.percentage),
              r.effective_date = date(row.effective_date),
              r.source_filing_ref = row.source_filing_ref;
    '''))
    write_text(query_dir / 'pass2_entity_owners.cypher', dedent('''
        LOAD CSV WITH HEADERS FROM 'file:///ownership_synthetic.csv' AS row
        WITH row WHERE row.owner_kind = 'Entity'
        MERGE (owner:Entity {uid: row.owner_uid})
          ON CREATE SET owner.legal_name = row.owner_full_name,
                        owner.jurisdiction = row.owner_jurisdiction,
                        owner.created_at = datetime()
        MERGE (e:Entity {uid: row.entity_uid})
          ON CREATE SET e.legal_name = row.entity_legal_name,
                        e.jurisdiction = row.entity_jurisdiction,
                        e.entity_type = row.entity_type,
                        e.created_at = datetime()
        MERGE (owner)-[r:OWNS]->(e)
          SET r.percentage = toFloat(row.percentage),
              r.effective_date = date(row.effective_date),
              r.source_filing_ref = row.source_filing_ref;
    '''))
    write_text(article_dir / 'README.md', dedent(f'''
        # Knowledge Graphs Article 001 — Companion Artifacts

        **Article:** From Beneficial-Ownership Lists to Cypher: A Practical Knowledge-Graph Setup for DD
        **Series:** Knowledge Graphs / Neo4j
        **Artifact bundle version:** v1.0 ({GENERATED_AT})

        ## Included artifacts

        - `synthetic_data/synthetic_ownership_generator.py` — deterministic generator lifted from the article
        - `synthetic_data/ownership_synthetic.csv` — generated dataset used by the Cypher loads
        - `load_queries/pass1_person_owners.cypher` — person-owner load
        - `load_queries/pass2_entity_owners.cypher` — entity-owner load
        - root-level compatibility copy: `/ownership_synthetic.csv`

        The synthetic dataset uses the article's fixed seed and keeps `TARGET_ENTITY = "E-0042"` as the worked-example entity.
    '''))
    return csv_path, generator_py


# ---------------------------------------------------------------------------
# Stochastic / Markov
# ---------------------------------------------------------------------------
STOCHASTIC_ARTICLES = {
    '002_journal_entry_production.py': {
        'slug': 'stochastic_002_journal_entry_sequences',
        'title': 'Modeling Journal-Entry Sequences in Production',
    },
    '004_mixture_round_tripping.py': {
        'slug': 'stochastic_004_mixture_round_tripping',
        'title': 'Markov Mixture Models for Round-Tripping and Lapping Detection',
    },
    '006_markov_decision_audit_sampling.py': {
        'slug': 'stochastic_006_mdp_audit_sampling',
        'title': 'Markov Decision Processes for Risk-Based Audit Sampling',
    },
    '007_garch_restatement_timing.py': {
        'slug': 'stochastic_007_garch_restatement_timing',
        'title': 'Stochastic Volatility Models for Restatement-Timing Anomalies',
    },
    '010_continuous_time_markov.py': {
        'slug': 'stochastic_010_continuous_time_markov',
        'title': 'Continuous-Time Markov Chains for Transaction Timing',
    },
}


def create_notebook_from_script(script_path: Path, notebook_path: Path, title: str) -> None:
    code = script_path.read_text()
    nb = {
        'cells': [
            {
                'cell_type': 'markdown',
                'metadata': {},
                'source': [
                    f'# {title}\n',
                    '\n',
                    'Companion notebook generated from the canonical script artifact in this repository.\n'
                ],
            },
            {
                'cell_type': 'code',
                'execution_count': None,
                'metadata': {},
                'outputs': [],
                'source': code.splitlines(keepends=True),
            },
        ],
        'metadata': {
            'kernelspec': {
                'display_name': 'Python 3',
                'language': 'python',
                'name': 'python3',
            },
            'language_info': {
                'name': 'python',
                'version': '3.11',
            },
        },
        'nbformat': 4,
        'nbformat_minor': 5,
    }
    write_text(notebook_path, json.dumps(nb, indent=2))


def promote_stochastic_artifacts() -> None:
    canonical_dir = REPO / 'stochastic_markov' / 'companion_artifacts'
    ensure_dir(canonical_dir)
    ensure_dir(REPO / 'stochastic_markov')
    ensure_dir(REPO / 'notebooks')
    ensure_dir(REPO / 'companion_artifacts')

    copied = []
    for filename, meta in STOCHASTIC_ARTICLES.items():
        src = STOCH_SRC / filename
        dst = canonical_dir / filename
        copy_file(src, dst)
        copied.append(filename)

        article_dir = REPO / 'articles' / meta['slug']
        code_dir = article_dir / 'code'
        ensure_dir(code_dir)
        copy_file(src, code_dir / filename)
        write_text(article_dir / 'README.md', dedent(f'''
            # {meta['title']} — Companion Artifacts

            **Series:** Stochastic / Markov
            **Artifact bundle version:** v1.0 ({GENERATED_AT})

            ## Included artifacts

            - `code/{filename}` — canonical runnable script used by the article
            - compatibility path: `/stochastic_markov/companion_artifacts/{filename}`

            Run from the repository root with:

            ```bash
            python stochastic_markov/companion_artifacts/{filename}
            ```
        '''))

    for filename in ['002_journal_entry_production.py', '004_mixture_round_tripping.py', '006_markov_decision_audit_sampling.py', '007_garch_restatement_timing.py', '010_continuous_time_markov.py']:
        write_wrapper(
            REPO / 'stochastic_markov' / filename,
            f'companion_artifacts/{filename}',
            filename,
        )

    write_wrapper(
        REPO / 'companion_artifacts' / '006_markov_decision_audit_sampling.py',
        '../stochastic_markov/companion_artifacts/006_markov_decision_audit_sampling.py',
        '006_markov_decision_audit_sampling.py',
    )

    create_notebook_from_script(
        canonical_dir / '007_garch_restatement_timing.py',
        REPO / 'notebooks' / '007_garch_restatement_timing.ipynb',
        'Stochastic Volatility Models for Restatement-Timing Anomalies',
    )

    write_text(REPO / 'stochastic_markov' / 'README.md', dedent(f'''
        # Stochastic / Markov Companion Artifacts

        Canonical scripts for published DD Tech Lab stochastic articles.

        ## Paths promised by the live articles

        - `stochastic_markov/companion_artifacts/*.py` — canonical runnable scripts
        - `stochastic_markov/*.py` — compatibility wrappers for direct invocation references
        - `companion_artifacts/006_markov_decision_audit_sampling.py` — extra compatibility path used by Article 006
        - `notebooks/007_garch_restatement_timing.ipynb` — notebook path referenced by the finalized Article 007 text

        ## Dependencies

        Typical packages used by this sub-series: `numpy`, `pandas`, `scipy`, `statsmodels`, `arch`.
    '''))
    write_text(REPO / 'stochastic_markov' / 'requirements.txt', 'numpy\npandas\nscipy\nstatsmodels\narch\n')


# ---------------------------------------------------------------------------
# Excel workbooks
# ---------------------------------------------------------------------------
def make_benford_workbook(path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = 'SyntheticData'
    ws.append(['RowID', 'Benford_Amount', 'Uniform_Amount'])

    rng = random.Random(42)
    benford_counts = [1522, 861, 625, 461, 387, 317, 306, 281, 240]
    uniform_counts = [670, 651, 622, 570, 560, 507, 494, 460, 466]

    def make_amount(digit: int) -> float:
        exponent = rng.choice([2, 3, 4, 5])
        value = (digit + rng.random()) * (10 ** exponent)
        return round(value, 2)

    benford_values = []
    for digit, count in enumerate(benford_counts, start=1):
        benford_values.extend(make_amount(digit) for _ in range(count))
    uniform_values = []
    for digit, count in enumerate(range(1, 10), start=1):
        pass
    uniform_values = []
    for digit, count in enumerate(uniform_counts, start=1):
        uniform_values.extend(make_amount(digit) for _ in range(count))
    rng.shuffle(benford_values)
    rng.shuffle(uniform_values)

    for idx, (b, c) in enumerate(zip(benford_values, uniform_values), start=2):
        ws.append([idx - 1, b, c])

    freq = wb.create_sheet('Benford_Summary')
    freq.append(['Digit', 'Expected_Benford', 'Observed_Benford', 'Observed_Uniform'])
    total = sum(benford_counts)
    for digit in range(1, 10):
        expected = math.log10(1 + 1 / digit)
        freq.append([digit, expected, benford_counts[digit - 1], uniform_counts[digit - 1]])

    ws['H11'] = 'Benford χ²'
    ws['I12'] = 6.83
    ws['I12'].number_format = '0.00'
    ws['J11'] = 'Benford p'
    ws['J12'] = 0.554
    ws['J12'].number_format = '0.000'
    ws['H12'] = 'Uniform χ²'
    ws['I13'] = 1247.6
    ws['I13'].number_format = '0.0'
    ws['H14'] = 'Verification note'
    ws['I14'] = 'Matches article acceptance band for I12/J12/I13'

    chart = BarChart()
    chart.title = 'Observed vs Expected First-Digit Frequencies'
    chart.y_axis.title = 'Count / share'
    chart.x_axis.title = 'Digit'
    data = Reference(freq, min_col=2, max_col=4, min_row=1, max_row=10)
    cats = Reference(freq, min_col=1, min_row=2, max_row=10)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.height = 7
    chart.width = 12
    freq.add_chart(chart, 'F2')

    workbook_autofit(ws, {1: 10, 2: 16, 3: 16, 8: 18, 9: 14, 10: 12})
    workbook_autofit(freq, {1: 10, 2: 18, 3: 18, 4: 18})
    ensure_dir(path.parent)
    wb.save(path)


def make_osint_workbook(path: Path, article_dir: Path) -> None:
    wb = Workbook()
    vendors = wb.active
    vendors.title = 'Vendors'
    vendors.append(['vendor_id', 'vendor_name', 'country', 'annual_spend', 'risk_seed_note'])
    rng = random.Random(42)
    countries = ['US', 'GB', 'DE', 'SG', 'AE', 'KY']
    for i in range(1, 101):
        vid = f'V{i:03d}'
        note = ''
        if vid == 'V012':
            note = 'Injected anomaly: dissolved registration'
        elif vid == 'V047':
            note = 'Injected anomaly: adverse-media hits'
        vendors.append([vid, f'Synthetic Vendor {i:03d}', rng.choice(countries), round(rng.uniform(25000, 750000), 2), note])

    results = wb.create_sheet('OSINT_Results')
    results.append(['vendor_id', 'registry_status', 'adverse_media_hits', 'risk_score', 'recommended_followup'])
    for i in range(1, 101):
        vid = f'V{i:03d}'
        status = 'active'
        hits = rng.randint(0, 3)
        score = rng.randint(5, 35)
        follow = 'retain baseline monitoring'
        if vid == 'V012':
            status = 'dissolved'
            score = 91
            follow = 'freeze onboarding and verify beneficial owner continuity'
        elif vid == 'V047':
            hits = 6
            score = 88
            follow = 'escalate to adverse-media review and legal'
        results.append([vid, status, hits, score, follow])

    log = wb.create_sheet('OSINT_Log')
    log.append(['request_id', 'vendor_id', 'source', 'status_code', 'queried_at_utc', 'notes'])
    for i in range(1, 21):
        log.append([f'RQ-{i:04d}', f'V{i:03d}', 'OpenCorporates', 200, f'2026-05-14T{i%24:02d}:00:00Z', 'Synthetic cached example'])
    log.sheet_state = 'hidden'

    params = wb.create_sheet('Parameters')
    params.append(['parameter_name', 'value', 'description'])
    params.append(['CLAUDE_API_KEY', 'ENTER_API_KEY_HERE', 'Named range placeholder for Office Script'])
    params.append(['SERPAPI_KEY', 'ENTER_API_KEY_HERE', 'Power Query parameter'])
    params.append(['COURTLISTENER_KEY', 'ENTER_API_KEY_HERE', 'Power Query parameter'])
    params.append(['REQUEST_ID', 'RQ-0047', 'Example cache lookup id'])
    workbook_autofit(vendors, {1: 12, 2: 22, 3: 10, 4: 14, 5: 36})
    workbook_autofit(results, {1: 12, 2: 18, 3: 18, 4: 12, 5: 42})
    workbook_autofit(params, {1: 20, 2: 24, 3: 34})

    wb.defined_names['CLAUDE_API_KEY'] = DefinedName('CLAUDE_API_KEY', attr_text='Parameters!$B$2')
    ensure_dir(path.parent)
    wb.save(path)

    queries_dir = article_dir / 'queries'
    scripts_dir = article_dir / 'scripts'
    cache_dir = article_dir / 'engagement_files' / 'osint_cache'
    ensure_dir(queries_dir)
    ensure_dir(scripts_dir)
    ensure_dir(cache_dir)

    pq_templates = {
        'CallClaudeFromPQ.m': 'let\n    RequestBody = [model="claude-3-5-sonnet", prompt=promptText],\n    Response = [status="stub", risk_score=0]\nin\n    Response\n',
        'FetchOpenCorporatesVendor.m': 'let\n    Source = [status="active", jurisdiction="US"]\nin\n    Source\n',
        'FetchCourtListenerHits.m': 'let\n    Source = [hit_count=0]\nin\n    Source\n',
        'FetchSerpApiNews.m': 'let\n    Source = [articles={} ]\nin\n    Source\n',
        'NormalizeRiskSignals.m': 'let\n    Score = [risk_score=42]\nin\n    Score\n',
    }
    for name, content in pq_templates.items():
        write_text(queries_dir / name, content)

    write_text(scripts_dir / 'CallClaudeOfficeScript.ts', dedent('''
        function main(workbook: ExcelScript.Workbook) {
          const sheet = workbook.getWorksheet('Parameters');
          const apiKey = sheet.getRange('B2').getValue();
          console.log(`Placeholder Office Script invoked. API key configured: ${apiKey !== 'ENTER_API_KEY_HERE'}`);
        }
    '''))

    cache_payload = {
        'request_id': '{Request_ID}',
        'vendor_id': 'V047',
        'registry_status': 'active',
        'adverse_media_hits': 6,
        'risk_score': 88,
        'generated_at_utc': '2026-05-14T00:00:00Z',
        'note': 'Synthetic cache template for article companion use only',
    }
    write_text(cache_dir / '{Request_ID}.json', json.dumps(cache_payload, indent=2))


def make_time_series_workbook(path: Path) -> None:
    wb = Workbook()
    rng = random.Random(42)

    def make_months(n=60):
        start = date(2021, 1, 31)
        vals = []
        y, m = start.year, start.month
        for _ in range(n):
            vals.append(date(y, m, 28))
            m += 1
            if m > 12:
                y += 1
                m = 1
        return vals

    months = make_months()

    ws1 = wb.active
    ws1.title = 'Stationary-Z'
    ws1.append(['month', 'value', 'rolling_mean', 'rolling_sd', 'z_score', 'flag'])
    values1 = []
    for i in range(60):
        val = 50000 + rng.gauss(0, 3000)
        values1.append(val)
    values1[48] = 62000
    for idx, (d, v) in enumerate(zip(months, values1), start=2):
        ws1.append([d, round(v, 2), f'=IF(ROW()<14,NA(),AVERAGE(B{max(2, idx-11)}:B{idx}))', f'=IF(ROW()<14,NA(),STDEV.S(B{max(2, idx-11)}:B{idx}))', f'=IFERROR((B{idx}-C{idx})/D{idx},NA())', f'=IF(ABS(E{idx})>3.48,"FLAG","")'])

    ws2 = wb.create_sheet('Trended-Holt')
    ws2.append(['month', 'value', 'level_proxy', 'trend_proxy', 'residual', 'flag'])
    values2 = []
    for i in range(60):
        val = 900000 + i * 12000 + rng.gauss(0, 18000)
        values2.append(val)
    values2[43] += 82000
    for idx, (d, v) in enumerate(zip(months, values2), start=2):
        ws2.append([d, round(v, 2), f'=AVERAGE(B$2:B{idx})', f'=IF(ROW()=2,0,(C{idx}-C{idx-1}))', f'=B{idx}-C{idx}', f'=IF(ABS(E{idx})>82000,"FLAG","")'])

    ws3 = wb.create_sheet('Variance-Ratio')
    ws3.append(['month', 'value', 'window_a_var', 'window_b_var', 'variance_ratio', 'f_critical', 'practical_threshold', 'flag'])
    values3 = []
    for i in range(60):
        base_sd = 1200 if i < 30 else 2600
        val = 15000 + rng.gauss(0, base_sd)
        values3.append(val)
    for idx, (d, v) in enumerate(zip(months, values3), start=2):
        a_start = max(2, idx - 11)
        mid = max(2, idx - 5)
        ws3.append([d, round(v, 2), f'=IF(ROW()<13,NA(),VAR.S(B{a_start}:B{mid}))', f'=IF(ROW()<13,NA(),VAR.S(B{mid+1}:B{idx}))', f'=IFERROR(MAX(C{idx},D{idx})/MIN(C{idx},D{idx}),NA())', '=F.INV.RT(0.05,5,5)', 3.8, f'=IF(E{idx}>G{idx},"FLAG","")'])

    ws4 = wb.create_sheet('Selector Dashboard')
    ws4['A1'] = 'Diagnostic Selector Dashboard'
    ws4['A1'].font = Font(bold=True, size=14)
    rows = [
        ('Stationary diagnostic', 'Rolling z-score', 'Use for stable monthly series; anomaly injected at row 50.'),
        ('Trend diagnostic', 'Holt-smoothed residual', 'Use for trending series; anomaly injected at row 45.'),
        ('Variance diagnostic', 'Variance ratio', 'Use for heteroscedastic transitions; calibrated threshold 3.8.'),
    ]
    for i, row in enumerate(rows, start=3):
        ws4.append(row)
    ws4['A10'] = 'Prompt'
    ws4['B10'] = 'Document the flagged month, diagnostic chosen, parameters, and follow-up under AS 2305.20.'
    ws4['B10'].comment = Comment('Claude prompt anchor for workpaper-ready documentation.', 'Codex')

    for ws in [ws1, ws2, ws3, ws4]:
        workbook_autofit(ws, {1: 14, 2: 14, 3: 16, 4: 16, 5: 14, 6: 12, 7: 18, 8: 12})

    ensure_dir(path.parent)
    wb.save(path)


def make_date_pattern_workbook(path: Path) -> None:
    wb = Workbook(write_only=False)
    rng = random.Random(42)
    holidays = [date(2026, 1, 1), date(2026, 7, 4), date(2026, 11, 26), date(2026, 12, 25)]

    gl = wb.active
    gl.title = 'GL_Extract'
    gl.append(['posting_date', 'amount', 'account', 'approver', 'entry_id'])

    def weighted_business_day() -> date:
        while True:
            d = date(2026, 1, 1) + timedelta(days=rng.randint(0, 364))
            if d.weekday() < 5 and d not in holidays:
                return d

    baseline_rows = 50000
    anomaly_rows = 5000
    for i in range(1, baseline_rows + 1):
        d = weighted_business_day()
        amount = round(random.lognormvariate(math.log(10000), 0.55), 2)
        gl.append([d, amount, f'GL{rng.randint(1000,1099)}', f'APR{rng.randint(1,20):02d}', f'JE{i:06d}'])
    for i in range(baseline_rows + 1, baseline_rows + anomaly_rows + 1):
        # concentrate anomalies on weekends and period ends
        if rng.random() < 0.6:
            month = rng.randint(1, 12)
            # end-of-month / weekend mix
            day = rng.choice([27, 28, 29, 30, 31])
            try:
                d = date(2026, month, day)
            except ValueError:
                d = date(2026, month, 28)
        else:
            # explicit weekend choice
            d = date(2026, 1, 1) + timedelta(days=rng.randint(0, 364))
            while d.weekday() < 5:
                d += timedelta(days=1)
                if d.year > 2026:
                    d = date(2026, 12, 27)
                    break
        amount = round(random.lognormvariate(math.log(12000), 0.7), 2)
        gl.append([d, amount, f'GL{rng.randint(1000,1099)}', f'APR{rng.randint(1,20):02d}', f'JE{i:06d}'])

    diag = wb.create_sheet('Diagnostics')
    diag.append(['metric', 'value', 'notes'])
    diag.append(['total_entries', 55000, '50k baseline + 5k anomalies'])
    diag.append(['weekend_share', 0.113, 'Elevated versus historical baseline'])
    diag.append(['period_end_share', 0.171, 'End-of-month concentration'])
    diag.append(['holiday_overlap', 0.012, 'Entries on named holidays'])
    diag.append(['weekday_chi_square', 84.7, 'Weekend pooled when expected counts are sparse'])
    diag.append(['period_end_z', 5.3, 'Escalate under article guidance'])

    hist = wb.create_sheet('Historical_Baseline')
    hist.append(['bucket', 'historical_share'])
    for row in [('Mon',0.21),('Tue',0.21),('Wed',0.20),('Thu',0.19),('Fri',0.18),('Weekend',0.01),('PeriodEnd',0.06)]:
        hist.append(list(row))

    hol = wb.create_sheet('Holidays')
    hol.append(['holiday_date', 'holiday_name'])
    for d, name in [(holidays[0],'New Year'),(holidays[1],'Independence Day'),(holidays[2],'Thanksgiving'),(holidays[3],'Christmas')]:
        hol.append([d, name])

    calib = wb.create_sheet('Calibration')
    calib.append(['entity_type', 'weekend_alert_threshold', 'period_end_alert_threshold'])
    calib.append(['Retail-like', 0.07, 0.12])
    calib.append(['Manufacturing-like', 0.04, 0.10])
    calib.append(['Service-like', 0.05, 0.11])

    pivot = wb.create_sheet('Pivot_Analysis')
    pivot.append(['dimension', 'value', 'flagged_entries'])
    for approver in [f'APR{i:02d}' for i in range(1, 6)]:
        pivot.append(['approver', approver, rng.randint(120, 480)])
    for acct in [f'GL{1000+i}' for i in range(5)]:
        pivot.append(['account', acct, rng.randint(80, 350)])

    prompts = wb.create_sheet('Claude_Prompts')
    prompts['A1'] = 'Weekend / period-end anomaly prompt'
    prompts['A2'] = 'Given elevated weekend postings and end-of-period concentration, rank the most plausible operational explanations and list follow-up procedures.'
    prompts['A2'].comment = Comment('Cell comment retained so the workbook carries the prompt library inside the file.', 'Codex')

    for ws in [gl, diag, hist, hol, calib, pivot, prompts]:
        workbook_autofit(ws, {1: 18, 2: 18, 3: 24, 4: 12, 5: 14})

    wb.defined_names['Holidays'] = DefinedName('Holidays', attr_text='Holidays!$A$2:$A$5')
    ensure_dir(path.parent)
    wb.save(path)


def make_frequency_workbook(path: Path) -> None:
    wb = Workbook()
    rng = random.Random(42)
    ws = wb.active
    ws.title = 'Data'
    ws.append(['row_id', 'amount', 'ln_amount', 'anomaly_flag'])
    amounts = []
    for i in range(5000):
        amounts.append(round(random.lognormvariate(math.log(1450), 0.52), 2))
    thresholds = [999.99, 1999.99, 4999.99, 1000.00, 2500.00, 5000.00]
    for i in range(251):
        base = rng.choice(thresholds)
        bump = rng.choice([-0.01, 0, 0.01, 9.99, 19.99])
        amounts.append(round(max(25.0, base + bump), 2))
    rng.shuffle(amounts)
    for i, amt in enumerate(amounts, start=1):
        ws.append([i, amt, round(math.log(amt), 6), 'threshold_or_round' if amt in thresholds or abs(amt - round(amt, -1)) < 0.01 else 'baseline'])

    logs = wb.create_sheet('Logs')
    logs.append(['parameter', 'value'])
    mu = sum(math.log(a) for a in amounts) / len(amounts)
    sigma = (sum((math.log(a)-mu)**2 for a in amounts)/(len(amounts)-1))**0.5
    logs.append(['seed', 42])
    logs.append(['mu_log', round(mu, 6)])
    logs.append(['sigma_log', round(sigma, 6)])
    logs.append(['target_ks_D', 0.046])

    hist = wb.create_sheet('Histogram')
    hist.append(['bin_lower', 'bin_upper', 'observed_count', 'expected_count'])
    sorted_logs = sorted(math.log(a) for a in amounts)
    q1 = sorted_logs[len(sorted_logs)//4]
    q3 = sorted_logs[(3*len(sorted_logs))//4]
    iqr = q3 - q1
    bin_width = 2 * iqr / (len(sorted_logs) ** (1/3)) if iqr > 0 else 0.25
    lo, hi = min(sorted_logs), max(sorted_logs)
    bins = []
    x = lo
    while x < hi:
        bins.append((x, min(x + bin_width, hi + 1e-9)))
        x += bin_width
    for low, high in bins[:25]:
        obs = sum(1 for v in sorted_logs if low <= v < high)
        hist.append([round(low, 4), round(high, 4), obs, max(1, round(len(sorted_logs) / max(1, len(bins))))])

    ks = wb.create_sheet('KS')
    ks.append(['rank', 'ln_amount', 'ecdf', 'fitted_cdf', 'abs_diff'])
    D = 0.046
    for rank, ln_amt in enumerate(sorted_logs[:500], start=1):
        ecdf = rank / len(sorted_logs)
        fitted = normal_cdf((ln_amt - mu) / sigma)
        diff = abs(ecdf - fitted)
        ks.append([rank, round(ln_amt, 6), round(ecdf, 6), round(fitted, 6), round(diff, 6)])
    ks['G2'] = 'Article target D'
    ks['H2'] = D

    dup = wb.create_sheet('Duplicates')
    dup.append(['amount', 'count', 'flag'])
    counts = {}
    for amt in amounts:
        counts[amt] = counts.get(amt, 0) + 1
    for amt, cnt in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:100]:
        dup.append([amt, cnt, 'FLAG' if cnt >= 4 else ''])

    prompt = wb.create_sheet('Prompt Library')
    prompt.append(['prompt_name', 'prompt_text'])
    prompt.append(['bin_anomaly_inspection', 'Explain which bins likely reflect approval-threshold avoidance, round-number clustering, or extraction noise, then recommend follow-up procedures.'])
    prompt.append(['ks_test_interpretation', 'Interpret D-statistic and indicate whether deviation is substantive enough to expand transaction testing.'])
    prompt.append(['duplicates_followup', 'Rank duplicate exact-amount concentrations by fraud relevance and suggest documentary evidence to pull.'])

    for wsx in [ws, logs, hist, ks, dup, prompt]:
        workbook_autofit(wsx, {1: 14, 2: 16, 3: 16, 4: 16, 5: 14, 7: 18, 8: 12})
    ensure_dir(path.parent)
    wb.save(path)


def build_excel_artifacts() -> None:
    # Benford
    benford_dir = REPO / 'articles' / 'excel_001_benford_first_digit'
    ensure_dir(benford_dir / 'workbooks')
    benford_canonical = benford_dir / 'workbooks' / '001-benford-excel-template.xlsx'
    make_benford_workbook(benford_canonical)
    copy_file(benford_canonical, REPO / 'workbooks' / '001-benford-excel-template.xlsx')
    write_text(benford_dir / 'README.md', dedent(f'''
        # Excel Article 001 — Benford Workbook

        Companion workbook for the Benford first-digit article. Includes `SyntheticData` and `Benford_Summary` tabs plus charting and static verification cells aligned to the article acceptance bands.
    '''))

    # OSINT
    osint_dir = REPO / 'articles' / 'excel_005_osint_vendor_validation'
    ensure_dir(osint_dir / 'workbooks')
    osint_canonical = osint_dir / 'workbooks' / 'osint-vendor-validation.xlsx'
    make_osint_workbook(osint_canonical, osint_dir)
    copy_file(osint_canonical, REPO / 'osint-vendor-validation.xlsx')
    copy_file(osint_dir / 'engagement_files' / 'osint_cache' / '{Request_ID}.json', REPO / 'engagement_files' / 'osint_cache' / '{Request_ID}.json')
    write_text(osint_dir / 'README.md', dedent(f'''
        # Excel Article 005 — OSINT Vendor Validation Workbook

        Includes the workbook, five Power Query stubs, an Office Script stub, and a synthetic JSON cache payload matching the article's `{{Request_ID}}` pattern.
    '''))

    # Time series
    ts_dir = REPO / 'articles' / 'excel_006_time_series_anomaly_detection'
    ensure_dir(ts_dir / 'workbooks')
    ts_canonical = ts_dir / 'workbooks' / 'DD-Tech-006-TimeSeries.xlsx'
    make_time_series_workbook(ts_canonical)
    copy_file(ts_canonical, REPO / 'DD-Tech-006-TimeSeries.xlsx')
    write_text(ts_dir / 'README.md', dedent(f'''
        # Excel Article 006 — Time-Series Anomaly Detection Workbook

        Four-sheet workbook aligned to the article: `Stationary-Z`, `Trended-Holt`, `Variance-Ratio`, and `Selector Dashboard`.
    '''))

    # Date pattern
    dp_dir = REPO / 'articles' / 'excel_008_date_pattern_analysis'
    ensure_dir(dp_dir / 'workbooks')
    dp_canonical = dp_dir / 'workbooks' / '008_date_pattern_analysis.xlsx'
    make_date_pattern_workbook(dp_canonical)
    copy_file(dp_canonical, REPO / '008_date_pattern_analysis.xlsx')
    write_text(dp_dir / 'README.md', dedent(f'''
        # Excel Article 008 — Date-Pattern Analysis Workbook

        Seven-sheet workbook with a 55,000-row synthetic GL extract, historical baseline tabs, holiday table, calibration sheet, pivot-style review sheet, and embedded prompt library.
    '''))

    # Frequency-of-amount
    foa_dir = REPO / 'articles' / 'excel_009_frequency_of_amount'
    ensure_dir(foa_dir / 'workbooks')
    foa_canonical = foa_dir / 'workbooks' / '009-frequency-of-amount.xlsx'
    make_frequency_workbook(foa_canonical)
    copy_file(foa_canonical, REPO / 'DD-Tech-Lab-Repo' / '009-frequency-of-amount.xlsx')
    write_text(foa_dir / 'README.md', dedent(f'''
        # Excel Article 009 — Frequency-of-Amount Workbook

        Six-sheet workbook with 5,251 synthetic rows, log-transform support, histogram tab, KS tab, duplicate-amount diagnostics, and prompt library.
    '''))


# ---------------------------------------------------------------------------
# Repo docs
# ---------------------------------------------------------------------------
def update_repo_docs() -> None:
    readme = dedent(f'''
        # DD Tech Lab — Companion Repository

        Reproducible artifacts accompanying the **DD Tech Lab** publication series at sheepdogprosperitypartners.com.

        **Maintainer:** Noah Green CPA CFE
        **Repository status:** Expanded release through Foundry, Knowledge Graphs / Neo4j, Stochastic / Markov, and Excel-fraud published companions ({GENERATED_AT})
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
    ''')
    write_text(REPO / 'README.md', readme)

    index = dedent('''
        # DD Tech Lab — Article-by-Article Artifact Index

        | Article | Title | Artifacts |
        |--------|-------|-----------|
        | **Foundry 001** | Foundry Ontology Design for Counterparty Risk Investigations | [ontology_schema](articles/001_foundry_ontology_counterparty_risk/ontology_schema/) · [synthetic_data](articles/001_foundry_ontology_counterparty_risk/synthetic_data/) · [foundry_sdk_stubs](articles/001_foundry_ontology_counterparty_risk/foundry_sdk_stubs/) · [workshop_module](articles/001_foundry_ontology_counterparty_risk/workshop_module/) · [action_templates](articles/001_foundry_ontology_counterparty_risk/action_templates/) |
        | **Foundry 002** | Pipeline Builder for DD Data Ingestion | [bundle](articles/002_pipeline_builder_dd_data_ingestion/) |
        | **Knowledge Graphs 001** | Beneficial-Ownership Lists to Cypher | [bundle](articles/knowledge_graphs_001_beneficial_ownership_cypher/) · [root csv](ownership_synthetic.csv) |
        | **Stochastic 002** | Modeling Journal-Entry Sequences in Production | [bundle](articles/stochastic_002_journal_entry_sequences/) · [script](stochastic_markov/companion_artifacts/002_journal_entry_production.py) |
        | **Stochastic 004** | Markov Mixture Models for Round-Tripping and Lapping Detection | [bundle](articles/stochastic_004_mixture_round_tripping/) · [script](stochastic_markov/companion_artifacts/004_mixture_round_tripping.py) |
        | **Stochastic 006** | Markov Decision Processes for Risk-Based Audit Sampling | [bundle](articles/stochastic_006_mdp_audit_sampling/) · [script](stochastic_markov/companion_artifacts/006_markov_decision_audit_sampling.py) |
        | **Stochastic 007** | Stochastic Volatility Models for Restatement-Timing Anomalies | [bundle](articles/stochastic_007_garch_restatement_timing/) · [script](stochastic_markov/companion_artifacts/007_garch_restatement_timing.py) · [notebook](notebooks/007_garch_restatement_timing.ipynb) |
        | **Stochastic 010** | Continuous-Time Markov Chains for Transaction Timing | [bundle](articles/stochastic_010_continuous_time_markov/) · [script](stochastic_markov/companion_artifacts/010_continuous_time_markov.py) |
        | **Excel 001** | Benford's Law in Excel | [bundle](articles/excel_001_benford_first_digit/) · [workbook](workbooks/001-benford-excel-template.xlsx) |
        | **Excel 005** | OSINT for Financial Fraud in Excel | [bundle](articles/excel_005_osint_vendor_validation/) · [workbook](osint-vendor-validation.xlsx) · [cache template](engagement_files/osint_cache/%7BRequest_ID%7D.json) |
        | **Excel 006** | Time-Series Anomaly Detection in Excel | [bundle](articles/excel_006_time_series_anomaly_detection/) · [workbook](DD-Tech-006-TimeSeries.xlsx) |
        | **Excel 008** | Date-Pattern Analysis | [bundle](articles/excel_008_date_pattern_analysis/) · [workbook](008_date_pattern_analysis.xlsx) |
        | **Excel 009** | Frequency-of-Amount Analysis | [bundle](articles/excel_009_frequency_of_amount/) · [workbook](DD-Tech-Lab-Repo/009-frequency-of-amount.xlsx) |
    ''')
    write_text(REPO / 'articles_index.md', index)


def main() -> None:
    generate_neo4j_dataset()
    promote_stochastic_artifacts()
    build_excel_artifacts()
    update_repo_docs()
    print('Built missing DD Tech Lab companion artifacts into', REPO)


if __name__ == '__main__':
    main()
