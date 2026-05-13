"""
Foundry-ontology data-shape stubs for the Foundry Article 001 worked example.

These are illustrative `dataclass` representations of the ontology objects
referenced in the article. They are NOT runnable Foundry SDK calls — Foundry
ontology creation runs through the Ontology Manager UI or the Foundry SDK with
real platform endpoints. These stubs let a reader run the worked example
end-to-end in plain Python (3.10+ stdlib only) to verify the data shapes match
the article's descriptions.

Run:
    python3 run_worked_example.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional


# ============================================================================
# Object types
# ============================================================================

@dataclass
class Counterparty:
    counterparty_id: str
    legal_name: str
    jurisdiction: str
    risk_rating: str  # "low" | "medium" | "high" | "critical"
    last_kyc_refresh: datetime
    pipeline_run_id: str
    source_extract_date: datetime
    last_risk_change: Optional[datetime] = None


@dataclass
class Person:
    person_id: str
    legal_name_canonical: str
    nationality: list[str]
    pep_status: Optional[str] = None
    date_of_birth: Optional[date] = None
    legal_name_variants: list[str] = field(default_factory=list)


@dataclass
class AdverseMediaMention:
    amm_id: str
    counterparty_id: str
    news_article_id: str
    mention_date: date
    risk_relevance: str  # "low" | "medium" | "high"


@dataclass
class SanctionsHit:
    sanctions_hit_id: str
    counterparty_id: str
    sanctions_list_id: str
    hit_type: str
    effective_from: datetime
    effective_to: Optional[datetime] = None


@dataclass
class AuditEntry:
    """
    Institution-modeled audit log entry. The institution must enforce
    write-only / supersession / no-bypass semantics through permissioned
    write paths + retention policy + control testing. Append-only by
    convention; supersession by later AuditEntry rather than edit/delete.
    """
    audit_entry_id: str
    action_type: str
    actor: str
    actor_role: str
    timestamp: datetime
    target_id: str
    prior_state: dict
    new_state: dict
    justification: str
    supporting_evidence_ids: list[str]
    superseded_by: Optional[str] = None


# ============================================================================
# Link types
# ============================================================================

@dataclass
class UltimateBeneficialOwner:
    """Link: Counterparty -> Person"""
    counterparty_id: str
    person_id: str
    ownership_percentage: float
    ownership_type: str  # "direct_voting" | "direct_economic" | "indirect_calculated"
    effective_from: date
    effective_to: Optional[date] = None
    disclosure_source: str = "voluntary"
    disclosure_date: Optional[date] = None


@dataclass
class TransactedWith:
    """Link: Counterparty -> Counterparty"""
    source_counterparty_id: str
    dest_counterparty_id: str
    aggregated_volume_usd: float
    aggregated_count: int
    last_transaction_date: datetime
    direction: str  # "bilateral" | "source_to_dest_only" | "dest_to_source_only"


# ============================================================================
# Action types
# ============================================================================

class ActionValidationError(ValueError):
    """Raised when an Action invocation fails its input constraints."""


def elevate_risk_rating(
    target: Counterparty,
    new_risk_rating: str,
    justification: str,
    supporting_evidence: list,  # list of AdverseMediaMention / SanctionsHit / ...
    actor_id: str,
    actor_role: str,
) -> tuple[Counterparty, AuditEntry]:
    """
    ElevateRiskRating ActionType implementation.

    Validates inputs, mutates the target Counterparty's risk_rating, and produces
    a structured AuditEntry. Designed for institutional implementations to
    follow — direct dataset edits should NOT bypass this Action surface.

    Returns (mutated_counterparty, audit_entry).
    """
    rating_order = ["low", "medium", "high", "critical"]
    if rating_order.index(new_risk_rating) <= rating_order.index(target.risk_rating):
        raise ActionValidationError(
            f"new_risk_rating ({new_risk_rating}) must be HIGHER than "
            f"current ({target.risk_rating})"
        )
    if len(justification) < 200:
        raise ActionValidationError(
            f"justification must be >=200 characters; got {len(justification)}"
        )
    if not supporting_evidence:
        raise ActionValidationError("supporting_evidence ObjectSet must be non-empty")
    allowed_evidence_types = (AdverseMediaMention, SanctionsHit)
    if not any(isinstance(e, allowed_evidence_types) for e in supporting_evidence):
        raise ActionValidationError(
            "supporting_evidence must contain at least one AdverseMediaMention "
            "or SanctionsHit (or TransactionAnomaly in production)"
        )

    prior_state = {"risk_rating": target.risk_rating}
    target.risk_rating = new_risk_rating
    target.last_risk_change = datetime.utcnow()
    new_state = {"risk_rating": target.risk_rating}

    audit_entry = AuditEntry(
        audit_entry_id=f"AE-{int(datetime.utcnow().timestamp())}",
        action_type="ElevateRiskRating",
        actor=actor_id,
        actor_role=actor_role,
        timestamp=datetime.utcnow(),
        target_id=target.counterparty_id,
        prior_state=prior_state,
        new_state=new_state,
        justification=justification,
        supporting_evidence_ids=[getattr(e, "amm_id", None) or getattr(e, "sanctions_hit_id", None)
                                  for e in supporting_evidence],
    )

    return target, audit_entry


# ============================================================================
# Cumulative-ownership computation (article's math section)
# ============================================================================

def cumulative_ownership(
    paths: list[list[float]],
) -> float:
    """
    Sum-of-products over distinct simple paths.

    Each path is a list of ownership-percentage values along its OWNS edges.
    The product of percentages along a path gives that path's contribution;
    cumulative ownership sums across paths.

    IMPORTANT: this function assumes the caller has already enumerated DISTINCT
    SIMPLE paths (no repeated nodes) AND deduplicated by edge identity. Paths
    sharing intermediate ownership interests must not be double-counted; the
    deduplication is a property of the graph traversal that feeds this
    function, not of the summation itself.

    Example from the article:
        Path 1: P -> E1 -> C, ownership product = 0.51 * 0.80 = 0.408
        Path 2: P -> E2 -> C, ownership product = 0.60 * 0.30 = 0.180
        cumulative_ownership([[0.51, 0.80], [0.60, 0.30]]) == 0.588
    """
    total = 0.0
    for path_pcts in paths:
        product = 1.0
        for pct in path_pcts:
            product *= pct
        total += product
    return total
