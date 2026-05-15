#!/usr/bin/env python3
"""Generate synthetic 50-counterparty × 365-day composite-risk-score trajectories.

Companion artifact for Foundry Article 008. Produces a deterministic
synthetic time series matching the seed §8 worked-example description:
50 counterparties, 365-day window, with two injected deterioration patterns:

  - "gradual_sanctions_buildup" (CP-SYN-007): linear sanctions_signal ramp
    from 0.0 to 0.55 over days 180-365; composite score crosses 0.40 around
    day 300.
  - "episodic_media_spike"      (CP-SYN-023): 4-week adverse-media spike
    starting day 250, decaying afterward; composite score spikes above 0.65
    in the spike window.

All other counterparties get baseline noise around composite_score=0.15-0.30.

Run:
    python tools/generate_synthetic_trajectories.py
    # Writes: synthetic_data/counterparty_risk_timeseries_full.csv (50 × 365 rows)
    #         synthetic_data/counterparty_risk_timeseries_sample.csv (5 × 365 head rows)
"""
from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path
import math
import random


N_COUNTERPARTIES = 50
N_DAYS = 365
END_DATE = date(2026, 5, 15)
START_DATE = END_DATE - timedelta(days=N_DAYS - 1)
SEED = 42


def baseline_signal(rng: random.Random) -> tuple[float, float, float, float]:
    """Return baseline (sanctions, media, transaction, kyc) signals at a low-noise level."""
    return (
        max(0.0, rng.gauss(0.05, 0.03)),     # sanctions: low constant baseline
        max(0.0, rng.gauss(0.20, 0.08)),     # media: low-moderate baseline
        max(0.0, rng.gauss(0.10, 0.05)),     # transaction: low baseline
        max(0.0, rng.gauss(0.30, 0.10)),     # kyc: moderate-stale baseline
    )


def composite(s: float, m: float, t: float, k: float) -> float:
    return min(1.0, 0.40 * s + 0.25 * m + 0.20 * t + 0.15 * k)


def write_csv(rows, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "counterparty_id", "date", "sanctions_signal", "media_signal",
            "transaction_signal", "kyc_signal", "composite_risk_score",
            "deterioration_pattern",
        ])
        for r in rows:
            w.writerow(r)


def generate() -> list[tuple]:
    rng = random.Random(SEED)
    rows: list[tuple] = []

    for cp_idx in range(N_COUNTERPARTIES):
        cp_id = f"CP-SYN-{cp_idx:03d}"

        if cp_idx == 7:
            pattern = "gradual_sanctions_buildup"
        elif cp_idx == 23:
            pattern = "episodic_media_spike"
        else:
            pattern = "baseline"

        for day in range(N_DAYS):
            d = START_DATE + timedelta(days=day)
            s, m, t, k = baseline_signal(rng)

            if pattern == "gradual_sanctions_buildup" and day >= 180:
                # Ramp sanctions signal to near-saturation by day 365.
                # With weight 0.40, sanctions=0.95 contributes 0.38 to composite alone.
                ramp = min((day - 180) / (N_DAYS - 180), 1.0)
                s = max(s, 0.95 * ramp)
                # Plus a secondary buildup in transaction-anomaly signal
                t = max(t, 0.40 * ramp)

            if pattern == "episodic_media_spike" and 250 <= day < 280:
                # Spike: media surges over 4 weeks then decays.
                # With weight 0.25, media=1.0 + saturated transaction=1.0
                # gives 0.25 + 0.20 = 0.45 spike contribution. Combined with
                # the baseline (~0.10) and sustained transaction surge,
                # composite crosses 0.60.
                spike_position = (day - 250) / 30.0
                spike_intensity = 1.0 * math.exp(-2.0 * (spike_position - 0.3) ** 2)
                m = max(m, spike_intensity)
                # Transactions co-spike (the event triggers both media and txn surveillance)
                t = max(t, 0.95 * math.exp(-2.0 * (spike_position - 0.4) ** 2))
                # Sanctions also elevates moderately
                s = max(s, 0.50 * math.exp(-2.0 * (spike_position - 0.5) ** 2))

            comp = composite(s, m, t, k)
            rows.append((cp_id, d.isoformat(), round(s, 4), round(m, 4),
                          round(t, 4), round(k, 4), round(comp, 4), pattern))

    return rows


def main() -> None:
    here = Path(__file__).parent.parent
    rows = generate()

    full_path = here / "synthetic_data" / "counterparty_risk_timeseries_full.csv"
    write_csv(rows, full_path)
    print(f"Wrote {len(rows):,} rows to {full_path}")

    sample_rows = [r for r in rows if r[0] in
                    {"CP-SYN-007", "CP-SYN-023", "CP-SYN-000", "CP-SYN-001", "CP-SYN-002"}]
    sample_path = here / "synthetic_data" / "counterparty_risk_timeseries_sample.csv"
    write_csv(sample_rows, sample_path)
    print(f"Wrote {len(sample_rows):,} rows to {sample_path}")

    print("\nDeterioration-pattern summary:")
    breached_007 = [r for r in rows if r[0] == "CP-SYN-007" and r[6] >= 0.40]
    breached_023 = [r for r in rows if r[0] == "CP-SYN-023" and r[6] >= 0.60]
    if breached_007:
        first = breached_007[0]
        print(f"  CP-SYN-007 first crosses composite>=0.40 on {first[1]} "
              f"(score={first[6]}, day={(date.fromisoformat(first[1]) - START_DATE).days})")
    if breached_023:
        first = breached_023[0]
        print(f"  CP-SYN-023 first crosses composite>=0.60 on {first[1]} "
              f"(score={first[6]}, day={(date.fromisoformat(first[1]) - START_DATE).days})")


if __name__ == "__main__":
    main()
