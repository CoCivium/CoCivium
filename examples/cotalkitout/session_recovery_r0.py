"""CoTalkItOut session recovery triage R0: pure policy, no takeover or messages."""
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass(frozen=True)
class Observation:
    session_id: str
    work_id: str
    observed_at: int
    last_progress_at: Optional[int]
    due_at: Optional[int]
    phase: str
    has_open_obligation: bool
    next_wake_at: Optional[int]
    is_lease_active: bool
    lease_epoch: int
    receipt_refs: Tuple[str, ...]
    peer_ids: Tuple[str, ...] = ()
    context_compatible: bool = False
    consent_to_peer_assist: bool = False
    conflict_detected: bool = False
    human_authority_required: bool = False

@dataclass(frozen=True)
class TriagePolicy:
    max_stalled_seconds: int = 3600
    min_evidence_signals: int = 2
    # Metric families are not a claim to currently measuring 325 independent units.
    metric_families: Tuple[str, ...] = (
        "verified_progress", "obligation_due", "lease_freshness",
        "source_currentness", "receiver_effect", "recovery_readiness",
        "resource_pressure", "quality_and_safety", "human_relay_cost")

def classify(o: Observation, policy: TriagePolicy = TriagePolicy()):
    """Propose safe assistance; never execute reassignment or infer subjective aliveness."""
    if not o.session_id or not o.work_id or o.observed_at < 0 or o.lease_epoch < 0:
        return {"state": "UNKNOWN", "next": "OBSERVE", "reason": "invalid_identity_or_time"}
    if o.last_progress_at is not None and o.last_progress_at > o.observed_at:
        return {"state": "UNKNOWN", "next": "OBSERVE", "reason": "future_progress_timestamp"}
    if o.human_authority_required:
        return {"state": "HELD", "next": "HUMAN_GATE", "reason": "authority_required"}
    if o.conflict_detected:
        return {"state": "DEGRADED", "next": "FENCE_AND_CHALLENGE",
                "reason": "conflicting_evidence"}
    # A deliberate hold or future wake is not a zombie just because nothing ran.
    if o.phase in ("GRACEFUL_HOLD", "DORMANT", "COMPLETE") and (
        not o.has_open_obligation or
        (o.next_wake_at is not None and o.observed_at < o.next_wake_at)):
        return {"state": "HEALTHY_QUIET", "next": "SLEEP", "reason": "not_due"}
    if not o.has_open_obligation:
        return {"state": "HEALTHY_QUIET", "next": "SLEEP", "reason": "no_due_work"}
    overdue = o.due_at is not None and o.observed_at >= o.due_at
    stale = o.last_progress_at is not None and (
        o.observed_at - o.last_progress_at >= policy.max_stalled_seconds)
    evidence_count = int(overdue) + int(stale) + int(bool(o.receipt_refs))
    if o.last_progress_at is None or evidence_count < policy.min_evidence_signals:
        return {"state": "UNKNOWN", "next": "OBSERVE",
                "reason": "insufficient_stall_evidence"}
    if not (overdue and stale):
        return {"state": "ACTIVE_OR_WAITING", "next": "RECHECK",
                "reason": "not_jointly_stalled"}
    if not o.context_compatible or not o.peer_ids:
        return {"state": "STALLED", "next": "TALK_OR_ISOLATED_TEST",
                "reason": "no_qualified_peer"}
    if not o.consent_to_peer_assist:
        return {"state": "STALLED", "next": "TALK_OR_ISOLATED_TEST",
                "reason": "peer_assist_not_authorized"}
    if o.is_lease_active:
        return {"state": "STALLED", "next": "FENCE_FIRST",
                "reason": "live_lease_must_be_fenced"}
    return {"state": "STALLED", "next": "PROPOSE_PEER_HANDOFF",
            "reason": "qualified_peer_candidate",
            "candidate_peer": sorted(set(o.peer_ids))[0],
            "work_id": o.work_id, "previous_epoch": o.lease_epoch}
