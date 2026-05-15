#!/usr/bin/env python3
"""Regenerate the deterministic 5,000-counterparty demo data for Foundry Article 003."""
from pathlib import Path
import csv
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[1] / "synthetic_data"
BASE_DATE = date(2026, 5, 1)
JURISDICTIONS = ["US", "GB", "KY", "DE", "AE", "SG"]
RATINGS = ["low", "medium", "high", "critical"]

with (ROOT / "counterparties.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["counterparty_id", "legal_name", "jurisdiction", "risk_rating", "last_kyc_refresh", "sanctions_hits", "ubo_count", "aip_grounded_risk_summary"])
    for i in range(1, 5001):
        rating = RATINGS[(i * 7) % len(RATINGS)]
        hits = 1 if i % 997 == 0 else 0
        ubo = 1 + (i % 4)
        refresh = BASE_DATE - timedelta(days=(i % 365))
        w.writerow([f"CP-{i:05d}", f"Counterparty {i:05d} Holdings", JURISDICTIONS[i % len(JURISDICTIONS)], rating, refresh.isoformat(), hits, ubo, f"Grounded summary for CP-{i:05d}: jurisdictional exposure, UBO depth {ubo}, sanctions hits {hits}."])
