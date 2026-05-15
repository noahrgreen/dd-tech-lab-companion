# Validation Notes — Article 008 Companion Bundle

## Validation scope

- **PySpark trajectory transform** (`transforms/counterparty_risk_trajectory.py`): full @transform with 4 Inputs (counterparty, sanctions, adverse_media, transactions), 1 Output (counterparty_risk_score time series). Builds daily date spine over 730-day lookback, computes 4 component signals (sanctions decay with 90-day half-life, log-scaled 90-day media count, |z-score| transaction anomaly, KYC freshness), combines to composite_risk_score via illustrative weights (0.40/0.25/0.20/0.15).
- **Feature schema** (`feature_schema/risk_trajectory_features.yaml`): canonical definitions for each of 4 component signals (source data, mathematical construction, bounded range, illustrative weight, audit-defensibility note) + composite formula + 2 alternative composite functions (Beneish-M style, Dechow-F style) for sensitivity-analysis validation.
- **Pipeline template** (`pipeline_templates/trajectory_alert_pipeline.yaml`): full Foundry Pipeline Builder pipeline shape with daily cron schedule, 4 dataset inputs, 3 transforms (Code Repo trajectory production + Pipeline Builder breach detection + Pipeline Builder AlertEntry emission), monitoring SLAs.
- **Threshold-alerting rules** (`threshold_alerting/threshold_to_action_handoff.yaml`): 4 alerting rules (composite crosses 0.60 high threshold → EscalateToEDD; composite crosses 0.85 critical threshold → ElevateRiskRating with dual-approval per Article 005; CUSUM/z-score change-point → EscalateToEDD; 14-day persistent-high-no-action queue-staleness alert), each with action handoff specification + rationale.
- **SR 11-7 / OCC 2011-12 validation framework** (`model_governance/sr_11_7_validation_framework.md`): 8-section framework matching SR 11-7's requirements — model identification, pre-deployment validation (conceptual soundness + quantitative + outcomes-based + documentation), ongoing monitoring, periodic re-validation, model change governance, independence, examiner readiness. Load-bearing per the seed's risk note.
- **Synthetic-data generator + outputs** (`tools/generate_synthetic_trajectories.py` + `synthetic_data/counterparty_risk_timeseries_full.csv` + `counterparty_risk_timeseries_sample.csv`): deterministic 50-counterparty × 365-day time series with 2 injected deterioration patterns. CP-SYN-007 (gradual_sanctions_buildup) crosses composite 0.40 on day 285. CP-SYN-023 (episodic_media_spike) crosses composite 0.60 on day 255. Generator confirmed reproducible under seed=42.

## Validation reproducibility

```bash
# Regenerate synthetic trajectories (deterministic; pure Python stdlib)
python3 tools/generate_synthetic_trajectories.py
# Expected:
#   Wrote 18,250 rows to .../counterparty_risk_timeseries_full.csv
#   Wrote 1,825 rows to .../counterparty_risk_timeseries_sample.csv
#   CP-SYN-007 first crosses composite>=0.40 on 2026-02-25 (score=0.4019, day=285)
#   CP-SYN-023 first crosses composite>=0.60 on 2026-01-26 (score=0.6313, day=255)

# Transform module parses
python3 -c "import ast; ast.parse(open('transforms/counterparty_risk_trajectory.py').read()); print('SYNTAX OK')"

# YAML files parse
python3 -c "
import yaml
for p in ['feature_schema/risk_trajectory_features.yaml',
          'pipeline_templates/trajectory_alert_pipeline.yaml',
          'threshold_alerting/threshold_to_action_handoff.yaml']:
    yaml.safe_load(open(p))
    print(f'{p}: parses')"
```

## Known limits

- Composite weights (0.40/0.25/0.20/0.15) and threshold values (0.60, 0.85, z-score 3.0) are ILLUSTRATIVE ONLY per the seed's load-bearing risk note. Production deployment requires institutional calibration per the SR 11-7 validation framework.
- Synthetic data is deterministic-by-seed but not representative of any specific institution's risk distribution. The 50-counterparty × 365-day shape is sufficient to exercise the patterns; production validation requires institutional data.
- Component-signal mathematical forms (90-day exponential decay for sanctions, 540-day linear ramp for KYC, etc.) are reasonable defaults but not the only defensible choices. Sensitivity analysis on functional forms is part of the SR 11-7 conceptual-soundness review.
- The Pipeline Builder transform structure assumes Foundry-specific operators (`lag_compute`, `rolling_stats`, `map_to_object`); equivalent Snowflake/Databricks pipelines require different operator vocabulary.
- The change-point-detection rule uses |z-score| as a CUSUM proxy; rigorous change-point detection (Page 1954 CUSUM, Bayesian change-point models) is the topic of Stochastic Article 005 and is referenced as a graduation path from this rule.

## Critical framing reminder (per seed)

The composite-risk-score model is genuinely useful for portfolio-level monitoring. The SR 11-7 validation framework is what makes it deployable in a regulated context. Skipping the validation steps does not eliminate the regulatory expectation; it defers the consequence to the next examination cycle.

**Every threshold, weight, and decision rule in this bundle is flagged as "illustrative only; production institution must validate and document under their own model-risk governance program."** This framing is the load-bearing editorial discipline the seed requires.

The platform (Foundry) provides the time-series primitives, the transform runtime, and the audit-trail wiring. The institution provides the model-risk discipline. The validation framework is the institution's responsibility.
