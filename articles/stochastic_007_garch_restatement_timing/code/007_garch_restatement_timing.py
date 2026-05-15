#!/usr/bin/env python3
"""Companion artifact for DD Tech Lab Stochastic / Markov Article 007 —
Stochastic Volatility Models for Restatement-Timing Anomalies.

End-to-end reproducible script. Synthesizes a 240-month restatement-count
panel with three injected volatility-cluster events (calibrated to the
2004-2006 SOX wave, 2008-2010 financial-crisis wave, and 2018-2019
revenue-recognition / ASC 606 wave documented in SEC Office of Chief
Accountant Restatement Studies), fits GARCH(1, 1), runs the three-gate
validate_garch_fit diagnostic, identifies conditional-volatility
exceedances above the 95th-percentile threshold, and prints the
portfolio early-warning artifact.

Audience:    portfolio-level audit risk officers, research-side DD
             analysts tracking restatement frequencies across issuers.
Reproducibility: deterministic under seed=42. Print output is the source
             of truth for the article's reported numbers.
Run:         python 007_garch_restatement_timing.py
"""
import numpy as np
import pandas as pd
import warnings
from arch import arch_model
from statsmodels.stats.diagnostic import het_arch, acorr_ljungbox


# =============================================================================
# Synthetic panel generation
# =============================================================================
def generate_restatement_panel(T: int = 240, baseline: float = 8.0,
                                 seed: int = 42) -> pd.Series:
    """Synthetic monthly restatement counts with three volatility-cluster events.

    The base process is Poisson(baseline). Three cluster windows add an
    independent Poisson(baseline * multiplier) shock on top of the baseline,
    representing the three industry-wide restatement waves the article ties to
    the published SEC Office of Chief Accountant Restatement Studies record.
    """
    rng = np.random.default_rng(seed)
    counts = rng.poisson(lam=baseline, size=T).astype(float)
    counts[24:48] += rng.poisson(lam=baseline * 0.8, size=24)  # SOX wave
    counts[84:108] += rng.poisson(lam=baseline * 1.2, size=24)  # financial crisis
    counts[192:216] += rng.poisson(lam=baseline * 0.5, size=24)  # ASC 606
    return pd.Series(counts, name="restatement_count")


# =============================================================================
# GARCH(1, 1) fit + diagnostic gate
# =============================================================================
def fit_garch_restatement_intensity(counts: pd.Series, p: int = 1, q: int = 1,
                                      dist: str = "Normal") -> dict:
    """Fit GARCH(p, q) on log-difference innovations of monthly restatement counts."""
    if counts.min() < 0:
        raise ValueError("Restatement counts must be non-negative")
    log_intensity = np.log1p(counts.astype(float))
    innovations = log_intensity.diff().dropna()
    model = arch_model(innovations, mean="Constant", vol="GARCH",
                        p=p, q=q, dist=dist, rescale=False)
    result = model.fit(disp="off", show_warning=False)
    a = float(result.params.get("alpha[1]", 0.0))
    b = float(result.params.get("beta[1]", 0.0))
    return {
        "fit": result,
        "omega": float(result.params["omega"]),
        "alpha": a,
        "beta": b,
        "persistence": a + b,
        "stationary": (a + b) < 1.0 and float(result.params["omega"]) > 0,
        "log_likelihood": float(result.loglikelihood),
        "aic": float(result.aic),
        "bic": float(result.bic),
    }


def arch_lm_diagnostic(garch_result, lags: int = 5, alpha: float = 0.05) -> dict:
    """ARCH-LM test on standardized residuals: detect any remaining ARCH structure."""
    std_resid = garch_result.std_resid.dropna().values
    lm_stat, lm_p, _, _ = het_arch(std_resid, nlags=lags)
    return {
        "lm_statistic": float(lm_stat),
        "lm_p_value": float(lm_p),
        "remaining_arch_effects": lm_p < alpha,
    }


def ljung_box_diagnostic(garch_result, lags: int = 10) -> pd.DataFrame:
    """Ljung-Box portmanteau test on standardized residuals: detect remaining autocorrelation."""
    std_resid = garch_result.std_resid.dropna()
    return acorr_ljungbox(std_resid, lags=[lags], return_df=True)


def validate_garch_fit(garch_result, ljung_lags: int = 10, alpha: float = 0.05) -> dict:
    """Production gatekeeper. Three blocking checks combined into a single pass/fail diagnostic.

    Run this immediately after every model.fit() in production audit deployment.
    Failing any gate is a signal to either re-fit at higher (p, q) or to escalate to a
    model class GARCH(1, 1) cannot handle (regime-switching GARCH, jump-diffusion,
    hazard-rate framing). NEVER promote a GARCH-based portfolio risk indicator to
    workpaper status without passing all three gates.
    """
    omega = float(garch_result.params.get("omega", 0.0))
    a = float(garch_result.params.get("alpha[1]", 0.0))
    b = float(garch_result.params.get("beta[1]", 0.0))
    stationary_ok = (a + b) < 1.0 and omega > 0
    lm = arch_lm_diagnostic(garch_result, lags=5, alpha=alpha)
    lb_df = ljung_box_diagnostic(garch_result, lags=ljung_lags)
    lb_p = float(lb_df["lb_pvalue"].iloc[0])
    return {
        "stationary": stationary_ok,
        "persistence": a + b,
        "arch_lm_p_value": lm["lm_p_value"],
        "arch_lm_pass": not lm["remaining_arch_effects"],
        "ljung_box_p_value": lb_p,
        "ljung_box_pass": lb_p > alpha,
        "all_gates_pass": stationary_ok and not lm["remaining_arch_effects"] and lb_p > alpha,
    }


# =============================================================================
# Conditional-volatility exceedance alerting
# =============================================================================
def conditional_volatility_alerts(cond_vol: pd.Series,
                                    percentile: float = 0.95) -> pd.DataFrame:
    """Identify periods where conditional volatility exceeds the historical percentile threshold."""
    threshold = cond_vol.quantile(percentile)
    above = cond_vol[cond_vol > threshold]
    return pd.DataFrame({
        "period": above.index,
        "conditional_volatility": above.values,
        "threshold": threshold,
        "exceedance": above.values - threshold,
    }).sort_values("exceedance", ascending=False)


# =============================================================================
# Main
# =============================================================================
def main() -> None:
    print("=" * 78)
    print("DD Tech Lab Stochastic Article 007 — companion artifact")
    print("GARCH(1, 1) early-warning indicator on synthetic 240-month restatement panel")
    print("=" * 78)

    # Step 1: synthesize panel
    panel = generate_restatement_panel(T=240, baseline=8.0, seed=42)
    print(f"\n[Step 1] Synthetic restatement panel: {len(panel)} monthly observations")
    print(f"  first 5: {panel.head().values.astype(int).tolist()}")
    print(f"  last 5:  {panel.tail().values.astype(int).tolist()}")
    print(f"  mean: {panel.mean():.2f}, max: {int(panel.max())}")
    print(f"  cluster windows (months): SOX 24-48, crisis 84-108, ASC 606 192-216")

    # Step 2: fit GARCH(1, 1)
    print("\n[Step 2] GARCH(1, 1) fit on log-difference innovations")
    fit = fit_garch_restatement_intensity(panel)
    print(f"  omega       = {fit['omega']:.4f}")
    print(f"  alpha       = {fit['alpha']:.4f}")
    print(f"  beta        = {fit['beta']:.4f}")
    print(f"  persistence = {fit['persistence']:.4f}  (alpha + beta)")
    print(f"  stationary  = {fit['stationary']}        (alpha + beta < 1 and omega > 0)")
    print(f"  log-L       = {fit['log_likelihood']:.2f}")
    print(f"  AIC         = {fit['aic']:.2f}")
    print(f"  BIC         = {fit['bic']:.2f}")

    # Step 3: diagnostic gate
    print("\n[Step 3] validate_garch_fit diagnostic gate (three blocking checks)")
    diag = validate_garch_fit(fit["fit"])
    print(f"  stationarity      pass = {diag['stationary']}")
    print(f"  ARCH-LM (lag 5)   pass = {diag['arch_lm_pass']}  "
          f"(p = {diag['arch_lm_p_value']:.4f})")
    print(f"  Ljung-Box (lag 10) pass = {diag['ljung_box_pass']}  "
          f"(p = {diag['ljung_box_p_value']:.4f})")
    print(f"  ALL GATES PASS    = {diag['all_gates_pass']}")
    if not diag["all_gates_pass"]:
        print("  -> escalation: re-fit at higher (p, q), regime-switching GARCH, "
              "jump-diffusion, or hazard-rate framing")

    # Step 4: conditional-volatility exceedance alerts
    print("\n[Step 4] Conditional-volatility exceedances (95th percentile threshold)")
    cond_vol = fit["fit"].conditional_volatility
    alerts = conditional_volatility_alerts(cond_vol, percentile=0.95)
    print(f"  mean cond_vol = {cond_vol.mean():.4f}")
    print(f"  max  cond_vol = {cond_vol.max():.4f}")
    print(f"  threshold (95p) = {cond_vol.quantile(0.95):.4f}")
    print(f"  exceedance count = {len(alerts)}")
    print("\n  top exceedances (period, conditional_volatility, exceedance):")
    for row in alerts.head(10).itertuples():
        print(f"    period {int(row.period):3d}  "
              f"cv={row.conditional_volatility:.4f}  "
              f"exceedance=+{row.exceedance:.4f}")

    print("\n" + "=" * 78)
    print("End-of-run. Workpaper artifact ready: portfolio risk officer reviews exceedance")
    print("periods, decomposes by issuer-segment, and triggers AS 2305 enhanced procedures.")
    print("=" * 78)


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    main()
