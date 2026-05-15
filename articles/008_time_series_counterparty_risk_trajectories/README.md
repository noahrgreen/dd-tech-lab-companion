# Foundry Article 008 — Companion Bundle

**Title:** Time Series in Foundry — Modeling Counterparty Risk Trajectories and Early-Warning Indicator Pipelines

**Series:** Palantir Foundry for Due Diligence
**Article ID:** SPP-DD-TECH-FOUNDRY-008
**Bundle status:** `validated_bundle`
**Prepared by:** Noah Green CPA CFE

## What this bundle contains

| Path | Purpose |
|---|---|
| `transforms/counterparty_risk_trajectory.py` | Daily-frequency PySpark transform. Builds a 730-day daily date spine, computes 4 component signals (sanctions exponential decay with 90-day half-life, log-scaled 90-day media count, abs-z-score transaction anomaly, KYC freshness linear ramp), composes to weighted composite_risk_score (illustrative weights 0.40/0.25/0.20/0.15). Pure-Spark helpers callable independently. |
| `feature_schema/risk_trajectory_features.yaml` | Canonical definitions for each component signal (source data, mathematical construction, bounded range, illustrative weight, audit-defensibility note) + composite formula + 2 alternative composite functions (Beneish-M / Dechow-F style) for sensitivity analysis. |
| `pipeline_templates/trajectory_alert_pipeline.yaml` | Full Foundry Pipeline shape: daily 04:00 cron, 4 dataset inputs, 3 transforms (Code Repo trajectory + Pipeline Builder breach detection + AlertEntry emission), monitoring SLAs. |
| `threshold_alerting/threshold_to_action_handoff.yaml` | 4 alerting rules mapped to Article 005 Actions: composite_crosses_high → EscalateToEDD; composite_crosses_critical → ElevateRiskRating (dual-approval); CUSUM/z-score change-point → EscalateToEDD; 14-day persistent-high-no-action queue-staleness alert. Plus alert-fatigue calibration checklist. |
| `model_governance/sr_11_7_validation_framework.md` | 8-section SR 11-7 / OCC 2011-12 validation framework: model identification, pre-deployment validation (conceptual + quantitative + outcomes-based + documentation), ongoing monitoring, periodic re-validation, model-change governance, independence, examiner readiness. **Load-bearing per the seed's risk note.** |
| `tools/generate_synthetic_trajectories.py` | Deterministic synthetic-data generator (50 counterparties × 365 days). Two injected deterioration patterns: gradual_sanctions_buildup (CP-SYN-007, breaches composite=0.40 on day 285) and episodic_media_spike (CP-SYN-023, breaches composite=0.60 on day 255). Pure-Python stdlib; reproducible under seed=42. |
| `synthetic_data/counterparty_risk_timeseries_full.csv` | 18,250 rows: 50 counterparties × 365 days. Generated output. |
| `synthetic_data/counterparty_risk_timeseries_sample.csv` | 1,825-row sample (5 counterparties × 365 days, including both deterioration patterns). |
| `screenshot_equivalents.md` | 4 text-based Foundry UI surfaces: TimeSeries Object Viewer with component breakdown, AlertEntry triage card, Workshop drill-down, Pipeline Builder DAG. |
| `validation_notes.md` | Scope + known limits + reproducibility commands. |

## Quick start (validation reproducibility)

```bash
# Regenerate synthetic trajectories (deterministic)
python3 tools/generate_synthetic_trajectories.py
# Expected:
#   18,250 rows written
#   CP-SYN-007 first crosses composite>=0.40 on 2026-02-25 (day 285)
#   CP-SYN-023 first crosses composite>=0.60 on 2026-01-26 (day 255)

# YAML files parse
python3 -c "
import yaml
for p in ['feature_schema/risk_trajectory_features.yaml',
          'pipeline_templates/trajectory_alert_pipeline.yaml',
          'threshold_alerting/threshold_to_action_handoff.yaml']:
    yaml.safe_load(open(p))
    print(f'{p}: parses')"

# Transform module syntax
python3 -c "import ast; ast.parse(open('transforms/counterparty_risk_trajectory.py').read()); print('SYNTAX OK')"
```

## Critical framing reminder

**EVERY threshold, weight, and decision rule in this bundle is illustrative
only.** Composite weights (0.40/0.25/0.20/0.15), threshold values
(0.60/0.85/z-score 3.0), and component-signal functional forms are
demonstrations of the engineering pattern, not production recommendations.
Production deployment requires institutional calibration, validation, and
documentation under the SR 11-7 / OCC 2011-12 framework in
`model_governance/sr_11_7_validation_framework.md`.

This framing is load-bearing per the seed's risk note. Composite scoring
with documented weights + threshold-based alerting + change-point detection
are exactly the kinds of "models" SR 11-7 governs. The bundle's
contribution is the engineering pattern + the validation framework the
institution must execute; not a model the institution can deploy without
its own validation work.

## Connection to other articles in the series

- **Article 001** (Counterparty ontology): provides the target object class
- **Article 003** (Workshop): consumes the TimeSeries for trajectory visualization (see screenshot_equivalents.md)
- **Article 005** (Actions framework): receives alerting handoffs via the threshold rules
- **Article 006** (Code Repositories): the trajectory transform itself is a Code Repo pattern; this bundle is a worked second example
- **Stochastic Article 005** (random-walk tests) + **Article 007** (stochastic volatility): rigorous change-point and volatility methods that the threshold_to_action handoff's z-score rule references as a graduation path
