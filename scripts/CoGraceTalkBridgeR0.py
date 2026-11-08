"""CoGrace -> CoTalkItOut shadow adapter.

Only interprets a policy verdict into a bounded request for peer challenge.
Neither reads model/session transports nor executes work or creates authority.
"""
from __future__ import annotations

from scripts.CoTalkItOutR0 import Proposal, Work, decide
from scripts.CoSessionGraceRecoveryR0 import Session, Peer, Measure, evaluate

def reconcile(session: Session, windows: tuple[tuple[Measure, ...], ...],
              peers: tuple[Peer, ...], *, source_revision: str,
              receiver_attested: bool = False, lease_attested: bool = False,
              as_of_utc: str | None = None) -> dict:
    if not source_revision or source_revision != session.revision:
        raise ValueError("SOURCE_REVISION_MISMATCH")
    health = evaluate(session, windows, peers, actual_receiver=receiver_attested,
                      fenced_lease=lease_attested, as_of_utc=as_of_utc)
    verdict = health["verdict"]
    # Keep the original health decision and its proof boundaries. No new peer
    # receives an executor identity or source authority from this conversion.
    if verdict not in {"PROPOSE_PEER_REVIEW", "PROPOSE_REVERSIBLE_HANDOFF"}:
        return {"work_id": session.work_id, "health": health,
                "coordination": "NO_FANOUT", "reason": verdict,
                "actual_handoff": False, "external_ack": False}
    eligible = [p for p in peers if p.session_id in health["peer_candidates"]]
    proposals = tuple(Proposal(peer=p.session_id, option="REVIEW_STALLED_WORK",
                               evidence_ref=p.evidence_ref,
                               evidence_class="SOURCE_LANDED",
                               risk="READ_ONLY") for p in eligible)
    # We intentionally do not elect an actuator. Peer review is safe to
    # propose; actual effect or transfer still requires independent authority.
    decision = decide(Work(work_id=session.work_id, source_revision=source_revision,
                           blocker="NONE", options=proposals, elected_actuator="",
                           independent_ack=False, authority_present=False))
    if decision["verdict"] not in {"HOLD", "CHALLENGE"}:
        raise RuntimeError("UNEXPECTED_COORDINATION_PRIVILEGE")
    return {"work_id": session.work_id, "health": health,
            "coordination": "REVIEW_CANDIDATE_ONLY",
            "decision": decision, "actual_handoff": False, "external_ack": False}
