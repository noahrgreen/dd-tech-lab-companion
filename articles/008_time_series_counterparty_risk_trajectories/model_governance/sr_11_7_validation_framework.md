# SR 11-7 / OCC 2011-12 Validation Framework — Composite Risk Score

The composite-risk-score model produced by `counterparty_risk_trajectory.py`
falls squarely within the definition of "model" under SR 11-7 and OCC
Bulletin 2011-12: it applies statistical, economic, financial, and
mathematical theories, techniques, and assumptions to process input data
into quantitative estimates.

**THE COMPOSITE WEIGHTS, THRESHOLDS, AND COMPONENT-SIGNAL CONSTRUCTIONS
SHIPPED WITH THIS BUNDLE ARE ILLUSTRATIVE ONLY.** Production deployment
requires institutional calibration, validation, and documentation under
the institution's own model-risk-management program. This document is
the validation framework the institution must execute, not a substitute
for executing it.

## 1. Model identification and inventory (SR 11-7 §IV)

The institution must:

- Register the composite-risk-score model in the institutional model
  inventory.
- Assign an owner (typically the head of model risk or the senior risk
  officer for the relevant portfolio).
- Assign a validator independent of the developer (segregation-of-duties
  per SR 11-7 §IV).
- Tier the model by inherent risk (composite scoring driving regulatory
  rating actions is typically Tier 1 or Tier 2 — re-validate annually).

## 2. Pre-deployment validation (SR 11-7 §V.A)

Before promoting the model to production, the validator must independently
confirm:

### 2.1 Conceptual soundness

- Component signals (sanctions decay, adverse-media rolling count,
  transaction z-score, KYC freshness) are conceptually justified — each
  has a clear causal story for why it should contribute to risk.
- Weight allocation (40/25/20/15 illustrative) is consistent with the
  institution's risk-rating taxonomy and historical loss experience.
- Functional forms (exponential decay for sanctions, log-scale for media,
  z-score for transactions, linear-bounded for KYC) are appropriate for
  each signal's distributional shape.

### 2.2 Quantitative testing

- **Holdout backtesting.** Train weights on data through year-end Y-2;
  predict counterparty deteriorations in year Y-1; measure AUC, precision,
  recall on the holdout.
- **Sensitivity analysis on weights.** Vary each weight by ±50% (subject to
  the constraint that weights sum to 1); confirm rank-ordering stability of
  top-decile counterparties across perturbations.
- **Sensitivity analysis on thresholds.** Vary `elevate_to_high` and
  `elevate_to_critical` thresholds ±0.10; confirm the resulting alert
  volume is operationally tractable (alert-fatigue ceiling).
- **Component-signal regression.** Compute composite-score correlation
  with each component signal independently. No component should explain
  > 60% of composite variance (collinearity concern).
- **Edge-case stress tests.** Run the pipeline on synthetic counterparties
  with extreme inputs (decade-old sanctions, hundreds of adverse-media
  mentions, no KYC refresh on record). Confirm graceful degradation, not
  crash.

### 2.3 Outcomes-based testing

- Document the labeled validation set (counterparties that experienced
  rating downgrades, sanctions enforcement, or financial-loss events in
  the holdout window).
- Compute precision/recall at the production thresholds.
- Document the false-positive trade-off: how many additional analyst
  hours per quarter does the alert volume imply, and is that operationally
  sustainable.

### 2.4 Documentation

Per SR 11-7 §V.A.4, validation documentation must allow parties unfamiliar
with the model to understand its construction, limitations, and key
assumptions. The validation report must include:

- Component-signal mathematical definitions
- Weight-elicitation methodology
- Threshold-calibration methodology
- Quantitative testing results
- Outcomes-based testing results
- Limitations and known weaknesses
- Conditions under which the model would need to be re-validated outside
  the periodic cadence

## 3. Ongoing monitoring (SR 11-7 §V.B)

Once in production:

- **Process verification (monthly).** Confirm the pipeline runs on schedule;
  no data-feed gaps; output row counts within expected range.
- **Outcomes analysis (quarterly).** Compute model precision/recall on the
  trailing quarter's actuals; compare to pre-deployment validation
  benchmarks; flag any material degradation.
- **Benchmarking (annually).** Compare composite scores against any
  alternative model the institution maintains (challenger model, vendor
  scoring product, external rating agency action).
- **Sensitivity drift (annually).** Re-run weight and threshold sensitivity
  analyses; check for material drift from baseline.

## 4. Periodic re-validation (SR 11-7 §V.A)

- Tier 1 models: annual full revalidation
- Tier 2 models: full revalidation every 2-3 years; annual review of
  ongoing-monitoring results
- Tier 3 models: review-on-trigger (material data drift, regulatory
  change, performance degradation)

The composite risk score is typically Tier 1 or Tier 2 depending on the
downstream Actions it drives. If it informs sanctions-related rating
decisions, treat as Tier 1.

## 5. Model change governance (SR 11-7 §V.A.5)

Any change to:

- Component-signal mathematical definitions
- Weights
- Thresholds
- Lookback windows

constitutes a model change. Each change requires:

- Pre-change validator review of the proposed change's rationale
- Re-validation on the same labeled holdout set as the original validation
- Documentation update
- Approval from the institutional model-risk committee
- A TransformChangeEntry audit record per Article 005's bypass-control
  framework

The illustrative weights and thresholds in `counterparty_risk_trajectory.py`
constants block must be replaced with the institution's calibrated values
during deployment; the version-controlled commit substituting them is
itself a model-change event under this framework.

## 6. Independence and segregation of duties (SR 11-7 §IV)

- Model developer ≠ model validator (different individuals; different
  reporting chains)
- Model owner ≠ model approver
- Production-deployment approver must include both the model owner and a
  compliance-side approver
- The Article 005 CI/CD dual-approval gate on regulated-ontology writers
  enforces the deployment-side discipline; the institution must add the
  model-validation-sign-off gate separately

## 7. Examiner readiness

When an examiner asks "show me the validation documentation for the
counterparty-risk-trajectory model," the institution must produce:

- The model identification record (inventory entry)
- The pre-deployment validation report
- The most recent annual revalidation report
- The ongoing-monitoring quarterly results (last 4 quarters)
- The change log (every model change since deployment, with rationale,
  validator review, and approval chain)

These five documents are the SR 11-7 §V baseline. Institutions with
ongoing examiner relationships should also produce sensitivity-analysis
results, benchmark comparisons, and the labeled validation-set
documentation.

## 8. Framing reminder

The composite-risk-score model is genuinely useful for portfolio-level
monitoring. The validation framework above is what makes it deployable in
a regulated context. Skipping the validation steps does not eliminate the
regulatory expectation; it just defers the consequence to the next
examination cycle.

The platform (Foundry) provides the time-series primitives, the transform
runtime, and the audit-trail wiring. The institution provides the
validation discipline. The model-risk governance program is the
institution's responsibility.
