#!/usr/bin/env python3
"""Companion artifact for DD Tech Lab Stochastic / Markov Article 002 —
Modeling Journal-Entry Sequences in Production.

End-to-end reproducible script. Consolidates the subledger mapping, the mid-period
and close-cycle baselines, the synthesize-entity-month generator, the chi2_test
function, and the Holm-corrected focus-list pipeline into one runnable script.
Reproduces the canonical focus-list output under seed=42 deterministically.

Audience:    audit-portfolio risk officers, DD analysts, forensic-accounting
             practitioners building Markov-chain journal-entry diagnostics on
             production audit data.
Reproducibility: deterministic under seed=42. Print output is the source of
             truth for the article's reported numbers.
Run:         python 002_journal_entry_production.py
"""
import numpy as np
import pandas as pd
from scipy.stats import chi2 as chi2_dist
from statsmodels.stats.multitest import multipletests


# =============================================================================
# State encoding (subledger granularity)
# =============================================================================
SUBLEDGER_MAP = {
    "cash":             ["1010", "1020", "1030"],
    "ar":               ["1100", "1110", "1120"],
    "inventory":        ["1200", "1210", "1220"],
    "fixed_assets":     ["1500", "1510", "1520", "1530"],
    "intangibles":      ["1600", "1610", "1620"],
    "ap":               ["2000", "2010", "2020"],
    "accrued":          ["2100", "2110", "2120"],
    "deferred_revenue": ["2200", "2210"],
    "debt":             ["2500", "2510", "2520"],
    "equity":           ["3000", "3010", "3020"],
    "revenue":          ["4000", "4010", "4020", "4030"],
    "cogs":             ["5000", "5010", "5020"],
    "opex":             ["6000", "6010", "6020", "6030", "6040"],
    "depreciation":     ["6500", "6510"],
    "intercompany":     ["9000", "9010", "9020"],
}
STATES = list(SUBLEDGER_MAP.keys())
STATE_INDEX = {s: i for i, s in enumerate(STATES)}
N_STATES = len(STATES)


# =============================================================================
# Realistic period-specific baselines
# =============================================================================
def _row(weights: dict) -> np.ndarray:
    """Build a row-stochastic 15-vector from a {state: weight} dict."""
    row = np.zeros(N_STATES)
    for s, w in weights.items():
        row[STATE_INDEX[s]] = w
    return row / row.sum()


# Mid-period baseline: revenue + AR + cash + inventory + COGS dominate; accruals minimal
P_MID_BASELINE = np.array([
    _row({"cash": 0.15, "ar": 0.20, "ap": 0.20, "opex": 0.15, "inventory": 0.10,
            "fixed_assets": 0.05, "intercompany": 0.10, "intangibles": 0.05}),
    _row({"cash": 0.45, "ar": 0.15, "revenue": 0.25, "deferred_revenue": 0.05, "intercompany": 0.10}),
    _row({"cogs": 0.50, "inventory": 0.20, "ap": 0.20, "fixed_assets": 0.05, "intercompany": 0.05}),
    _row({"depreciation": 0.30, "fixed_assets": 0.25, "ap": 0.20, "cash": 0.15, "intercompany": 0.10}),
    _row({"depreciation": 0.40, "intangibles": 0.30, "ap": 0.15, "cash": 0.15}),
    _row({"cash": 0.55, "ap": 0.10, "opex": 0.20, "inventory": 0.10, "intercompany": 0.05}),
    _row({"cash": 0.30, "accrued": 0.10, "opex": 0.40, "ap": 0.15, "intercompany": 0.05}),
    _row({"revenue": 0.50, "cash": 0.20, "ar": 0.15, "deferred_revenue": 0.10, "intercompany": 0.05}),
    _row({"cash": 0.40, "debt": 0.25, "accrued": 0.20, "opex": 0.10, "intercompany": 0.05}),
    _row({"cash": 0.35, "equity": 0.35, "intercompany": 0.20, "debt": 0.10}),
    _row({"ar": 0.60, "cash": 0.20, "revenue": 0.10, "deferred_revenue": 0.05, "intercompany": 0.05}),
    _row({"inventory": 0.50, "cogs": 0.20, "ap": 0.15, "intercompany": 0.10, "accrued": 0.05}),
    _row({"cash": 0.35, "ap": 0.30, "accrued": 0.15, "opex": 0.10, "intercompany": 0.10}),
    _row({"fixed_assets": 0.40, "depreciation": 0.20, "accrued": 0.20, "intangibles": 0.10, "intercompany": 0.10}),
    _row({"intercompany": 0.30, "cash": 0.20, "ap": 0.15, "ar": 0.15, "accrued": 0.10, "equity": 0.10}),
])
assert np.allclose(P_MID_BASELINE.sum(axis=1), 1.0)

# Close-cycle baseline: accruals + deferred revenue + intercompany dominate
P_CLOSE_BASELINE = np.array([
    _row({"accrued": 0.20, "cash": 0.15, "ap": 0.15, "opex": 0.15, "intercompany": 0.15, "ar": 0.10, "deferred_revenue": 0.10}),
    _row({"deferred_revenue": 0.25, "revenue": 0.20, "accrued": 0.15, "intercompany": 0.15, "cash": 0.15, "ar": 0.10}),
    _row({"accrued": 0.20, "cogs": 0.30, "inventory": 0.20, "ap": 0.15, "intercompany": 0.15}),
    _row({"depreciation": 0.40, "accrued": 0.20, "fixed_assets": 0.15, "intercompany": 0.15, "intangibles": 0.10}),
    _row({"depreciation": 0.40, "intangibles": 0.25, "accrued": 0.20, "intercompany": 0.15}),
    _row({"accrued": 0.30, "ap": 0.20, "cash": 0.20, "opex": 0.15, "intercompany": 0.15}),
    _row({"opex": 0.35, "accrued": 0.20, "ap": 0.15, "cash": 0.15, "intercompany": 0.15}),
    _row({"deferred_revenue": 0.30, "revenue": 0.25, "accrued": 0.20, "ar": 0.15, "intercompany": 0.10}),
    _row({"accrued": 0.30, "debt": 0.20, "cash": 0.20, "opex": 0.15, "intercompany": 0.15}),
    _row({"equity": 0.30, "intercompany": 0.25, "accrued": 0.20, "cash": 0.15, "debt": 0.10}),
    _row({"deferred_revenue": 0.30, "ar": 0.30, "revenue": 0.15, "accrued": 0.15, "intercompany": 0.10}),
    _row({"accrued": 0.25, "inventory": 0.25, "cogs": 0.20, "ap": 0.15, "intercompany": 0.15}),
    _row({"accrued": 0.35, "ap": 0.20, "opex": 0.15, "cash": 0.15, "intercompany": 0.15}),
    _row({"depreciation": 0.25, "fixed_assets": 0.25, "accrued": 0.25, "intangibles": 0.15, "intercompany": 0.10}),
    _row({"intercompany": 0.35, "accrued": 0.25, "ap": 0.15, "ar": 0.10, "cash": 0.10, "equity": 0.05}),
])
assert np.allclose(P_CLOSE_BASELINE.sum(axis=1), 1.0)


# =============================================================================
# Helpers
# =============================================================================
def transition_matrix(sequence, states):
    """Empirical first-order transition count matrix from a state sequence."""
    idx = {s: i for i, s in enumerate(states)}
    n = len(states)
    N = np.zeros((n, n), dtype=int)
    for prev, curr in zip(sequence[:-1], sequence[1:]):
        N[idx[prev], idx[curr]] += 1
    row_sums = N.sum(axis=1, keepdims=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        P_hat = np.where(row_sums > 0, N / row_sums, 0.0)
    return P_hat, N


def synthesize_entity_month(P_mid, P_close, n, close_fraction, seed):
    """Generate (mid_period_sequence, close_cycle_sequence) string-label sequences."""
    rng = np.random.default_rng(seed)
    n_close = int(n * close_fraction)
    n_mid = n - n_close
    seq_mid_idx = [0]
    for _ in range(n_mid - 1):
        seq_mid_idx.append(int(rng.choice(N_STATES, p=P_mid[seq_mid_idx[-1]])))
    seq_close_idx = [seq_mid_idx[-1]]
    for _ in range(n_close - 1):
        seq_close_idx.append(int(rng.choice(N_STATES, p=P_close[seq_close_idx[-1]])))
    return [STATES[s] for s in seq_mid_idx], [STATES[s] for s in seq_close_idx]


def chi2_test(N, P_baseline):
    """Chi-squared test on transition counts vs baseline.

    Simplified df (mask.sum() - n_states). For engagements where E_ij < 5 in many
    cells, escalate to Article 001's chi2_with_pooling routine.
    """
    E = N.sum(axis=1, keepdims=True) * P_baseline
    mask = E > 0
    chi2_stat = ((N[mask] - E[mask]) ** 2 / E[mask]).sum()
    df = int(mask.sum() - N.shape[0])
    p = 1.0 - chi2_dist.cdf(chi2_stat, df)
    return chi2_stat, p


# =============================================================================
# Main
# =============================================================================
def main():
    np.random.seed(42)
    N_ENTITIES = 20
    N_MONTHS = 3
    N_ENTRIES_PER_ENTITY_MONTH = 6000
    CLOSE_CYCLE_FRACTION = 1 / 6
    N_WINDOWS_PER_ENTITY_MONTH = 2
    m_family = N_ENTITIES * N_MONTHS * N_WINDOWS_PER_ENTITY_MONTH

    print("=" * 78)
    print("DD Tech Lab Stochastic Article 002 — companion artifact")
    print(f"Subledger encoding: {N_STATES} states; m_family = {m_family} tests")
    print("=" * 78)

    results = []
    for entity in range(N_ENTITIES):
        for month in range(N_MONTHS):
            seed = 1000 * entity + month
            mid_seq, close_seq = synthesize_entity_month(
                P_MID_BASELINE, P_CLOSE_BASELINE,
                N_ENTRIES_PER_ENTITY_MONTH, CLOSE_CYCLE_FRACTION, seed,
            )
            for window_label, w_seq, w_baseline in [
                ("mid", mid_seq, P_MID_BASELINE),
                ("close", close_seq, P_CLOSE_BASELINE),
            ]:
                _, N_obs = transition_matrix(w_seq, STATES)
                chi2_stat, p_val = chi2_test(N_obs, w_baseline)
                results.append({
                    "entity": entity, "month": month,
                    "window": window_label, "chi2": chi2_stat, "p": p_val,
                })

    results_df = pd.DataFrame(results)
    assert len(results_df) == m_family
    reject, p_adj, _, _ = multipletests(results_df["p"].values, alpha=0.05, method="holm")
    results_df["p_adjusted_holm"] = p_adj
    results_df["reject_holm"] = reject

    print(f"\nTotal tests: {len(results_df)}")
    print(f"Tests rejecting at family-wise alpha = 0.05 (Holm): "
          f"{int(results_df['reject_holm'].sum())}")

    focus_list = (results_df.groupby(["entity", "window"])["reject_holm"]
                  .sum().unstack(fill_value=0).reset_index())
    focus_list.columns = ["entity", "close_rejections", "mid_rejections"]
    focus_list["total_rejections"] = (
        focus_list["mid_rejections"] + focus_list["close_rejections"]
    )
    focus_list = focus_list.sort_values("total_rejections", ascending=False)
    print("\nFocus list (top 10 by total rejection count):")
    print(focus_list.head(10).to_string(index=False))

    print("\n" + "=" * 78)
    print("Workpaper artifact ready: engagement team reviews top-rejection entities,")
    print("expands substantive AS 2401 §60 sampling on transition cells with largest")
    print("standardized residuals, and triggers analytical-procedure follow-up under")
    print("AS 2305 §10-17 for moderate-rejection entities.")
    print("=" * 78)


if __name__ == "__main__":
    main()
