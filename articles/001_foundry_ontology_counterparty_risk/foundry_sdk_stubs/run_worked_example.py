"""
Reproduces the worked counterparty-risk investigation walkthrough from
Foundry Article 001 end-to-end in plain Python.

Run:
    python3 run_worked_example.py

Output: the synthetic counterparty's state before and after the
ElevateRiskRating Action invocation, plus the resulting AuditEntry.
"""
from __future__ import annotations

from datetime import datetime, date

from ontology_classes import (
    Counterparty,
    Person,
    AdverseMediaMention,
    UltimateBeneficialOwner,
    elevate_risk_rating,
    cumulative_ownership,
)


def main() -> None:
    # ------------------------------------------------------------------
    # Initial ontology state (matches synthetic_data/*.csv)
    # ------------------------------------------------------------------
    counterparty = Counterparty(
        counterparty_id="C-SYN-12345",
        legal_name="ACME Holdings (Z)",
        jurisdiction="ZZ",
        risk_rating="medium",
        last_kyc_refresh=datetime.fromisoformat("2026-02-14T00:00:00"),
        pipeline_run_id="prod-2026-05-11T03:00:00Z-run-4821",
        source_extract_date=datetime.fromisoformat("2026-05-11T02:14:00"),
    )

    ubo_person = Person(
        person_id="P-SYN-08832",
        legal_name_canonical="SYNTHETIC PERSON 08832",
        nationality=["ZZ"],
        pep_status="none",
    )

    ubo_link = UltimateBeneficialOwner(
        counterparty_id=counterparty.counterparty_id,
        person_id=ubo_person.person_id,
        ownership_percentage=0.408,
        ownership_type="indirect_calculated",
        effective_from=date(2024, 3, 1),
        effective_to=None,
        disclosure_source="fincen_boi",
        disclosure_date=date(2024, 3, 15),
    )

    adverse_media = [
        AdverseMediaMention("AMM-1", counterparty.counterparty_id, "NA-SYN-001",
                            date(2026, 4, 22), "high"),
        AdverseMediaMention("AMM-2", counterparty.counterparty_id, "NA-SYN-002",
                            date(2026, 4, 30), "medium"),
        AdverseMediaMention("AMM-3", counterparty.counterparty_id, "NA-SYN-003",
                            date(2026, 5, 8), "high"),
    ]

    sanctions_hits: list = []  # no active sanctions exposure

    print("=" * 70)
    print("BEFORE ElevateRiskRating Action:")
    print("=" * 70)
    print(f"  Counterparty: {counterparty.counterparty_id} ({counterparty.legal_name})")
    print(f"  risk_rating: {counterparty.risk_rating}")
    print(f"  last_risk_change: {counterparty.last_risk_change}")
    print(f"  AdverseMediaMention count (90d): {len(adverse_media)}")
    print(f"  SanctionsHit active: {len(sanctions_hits)}")
    print(f"  UltimateBeneficialOwner: {ubo_person.person_id} @ {ubo_link.ownership_percentage:.1%}")

    # ------------------------------------------------------------------
    # Cumulative-ownership math (article §4 numerical example)
    # ------------------------------------------------------------------
    print()
    print("=" * 70)
    print("Cumulative-ownership computation (article §4 worked example):")
    print("=" * 70)
    # Path 1: P -> E1 -> C, 0.51 * 0.80 = 0.408
    # Path 2: P -> E2 -> C, 0.60 * 0.30 = 0.180
    cumulative = cumulative_ownership([[0.51, 0.80], [0.60, 0.30]])
    print(f"  Path 1 (51% x 80%): {0.51 * 0.80:.3f}")
    print(f"  Path 2 (60% x 30%): {0.60 * 0.30:.3f}")
    print(f"  Cumulative ownership: {cumulative:.3f}  (58.8%)")
    print(f"  Above 25% FinCEN BOI threshold (subject to current rule status): True")
    print(f"  Anti-double-counting: caller must enumerate DISTINCT simple paths")

    # ------------------------------------------------------------------
    # Invoke ElevateRiskRating Action
    # ------------------------------------------------------------------
    print()
    print("=" * 70)
    print("Invoking ElevateRiskRating Action ...")
    print("=" * 70)
    justification = (
        "Three adverse-media mentions in trailing 90 days, two flagged "
        "high-risk-relevance under AIP grounding (AMM-1, AMM-3). "
        "Pattern consistent with material reputational exposure warranting "
        "enhanced due diligence under the institution's CDD/EDD framework "
        "as informed by the FFIEC BSA/AML Examination Manual."
    )

    counterparty, audit_entry = elevate_risk_rating(
        target=counterparty,
        new_risk_rating="high",
        justification=justification,
        supporting_evidence=adverse_media,
        actor_id="investigator_001",
        actor_role="senior_analyst",
    )

    print()
    print("=" * 70)
    print("AFTER ElevateRiskRating Action:")
    print("=" * 70)
    print(f"  Counterparty.risk_rating: {counterparty.risk_rating}")
    print(f"  Counterparty.last_risk_change: {counterparty.last_risk_change.isoformat()}")
    print()
    print("AuditEntry created:")
    print(f"  audit_entry_id: {audit_entry.audit_entry_id}")
    print(f"  action_type:    {audit_entry.action_type}")
    print(f"  actor:          {audit_entry.actor} ({audit_entry.actor_role})")
    print(f"  timestamp:      {audit_entry.timestamp.isoformat()}")
    print(f"  target_id:      {audit_entry.target_id}")
    print(f"  prior_state:    {audit_entry.prior_state}")
    print(f"  new_state:      {audit_entry.new_state}")
    print(f"  supporting_evidence_ids: {audit_entry.supporting_evidence_ids}")
    print(f"  justification (first 100 chars): {audit_entry.justification[:100]}...")
    print()
    print("NOTE: This AuditEntry is created in memory by the stub.")
    print("In a production institution, the AuditEntry would be:")
    print("  - written to the AuditEntry ontology object via the Action's side-effect layer,")
    print("  - constrained to append-only / supersession semantics by institutional discipline,")
    print("  - subject to retention policy and periodic control testing,")
    print("  - reconciled against Foundry's platform-level audit logs.")


if __name__ == "__main__":
    main()
