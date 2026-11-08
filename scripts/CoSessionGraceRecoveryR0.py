"""CoSessionGraceRecovery R0: advisory, reversible session-health peer aid.

Neither downtime nor low activity proves dysfunction. No session takeover,
provider orchestration or new authority. Raw metrics are untrusted until
defined, sourced, time-windowed and independently verified.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite

SCHEMA_TARGET = 325   # requested registry *target*, not 325 observed measurements
MAX_METRICS = 512
MAX_PEERS = 12

@dataclass(frozen=True)
class Measure:
    name: str
    value: float
    unit: str
    source: str
    observed_utc: str
    verifier: str
    window_start_utc: str
    window_end_utc: str
    # For monotonic health checks, a bad predicate is explicit and testable.
    adverse: bool = False

@dataclass(frozen=True)
class Session:
    session_id: str
    work_id: str
    revision: str
    state: str
    healthy_quiet: bool = False
    explicit_sleep: bool = False
    consent_to_peer_aid: bool = False
    pause_requested: bool = False

@dataclass(frozen=True)
class Peer:
    session_id: str
    capabilities: tuple[str, ...]
    availability: str
    consent_to_aid: bool
    health: str
    source_revision: str
    evidence_ref: str

def _validated(m: Measure) -> bool:
    return bool(m.name and m.unit and m.source and m.verifier
                and m.observed_utc and m.window_start_utc and m.window_end_utc
                and isinstance(m.value, (float, int))
                and not isinstance(m.value, bool) and isfinite(m.value)
                and m.window_start_utc <= m.observed_utc <= m.window_end_utc)

def evaluate(session: Session, windows: tuple[tuple[Measure, ...], ...],
             peers: tuple[Peer, ...] = (), *,
             registry_count: int = 0, registry_verified: bool = False,
             actual_receiver: bool = False, fenced_lease: bool = False) -> dict:
    """One source-bound advisory decision, no effect and no automatic merging.

    Two distinct qualified windows with adverse metrics allow an aid proposal.
    Recovery is harder than detection: a peer must be healthy, consented,
    source-bound, available and capability-compatible. None can steal a session.
    """
    if not session.session_id or not session.work_id or not session.revision:
        raise ValueError("MISSING_SESSION_BINDING")
    if registry_count < 0 or registry_count > 100000:
        raise ValueError("INVALID_REGISTRY_COUNT")
    if len(peers) > MAX_PEERS or any(len(w) > MAX_METRICS for w in windows):
        raise ValueError("EXCESS_INPUT")
    if any(not p.session_id or not p.source_revision or not p.evidence_ref for p in peers):
        raise ValueError("UNBOUND_PEER")
    if len({p.session_id for p in peers}) != len(peers):
        raise ValueError("DUPLICATE_PEER")
    base = {
        "session_id": session.session_id, "work_id": session.work_id,
        "source_revision": session.revision,
        "registry_target": SCHEMA_TARGET,
        "registry_observed": registry_count if registry_verified else None,
        "registry_target_met": registry_verified and registry_count >= SCHEMA_TARGET,
        "physical_takeover": False, "effect_executed": False,
        "independent_receiver_ack": False,
        "peer_candidates": [], "reason": "", "verdict": "",
    }
    if session.pause_requested or session.explicit_sleep or session.healthy_quiet:
        return dict(base, verdict="QUIET_HEALTHY", reason="QUIET_IS_NOT_ZOMBIE")
    valid_windows = []
    window_ids = set()
    for window in windows:
        good = [m for m in window if _validated(m)]
        if good:
            marker = tuple(sorted((m.window_start_utc, m.window_end_utc) for m in good))
            if marker in window_ids:
                continue
            window_ids.add(marker)
            valid_windows.append(good)
    if len(valid_windows) < 2:
        return dict(base, verdict="OBSERVE", reason="INSUFFICIENT_DISTINCT_VERIFIED_WINDOWS")
    adverse_windows = sum(any(m.adverse for m in w) for w in valid_windows)
    if adverse_windows < 2:
        return dict(base, verdict="QUIET", reason="NO_PERSISTENT_ADVERSE_EVIDENCE")
    if not session.consent_to_peer_aid:
        return dict(base, verdict="HOLD", reason="NO_PEER_AID_CONSENT")
    suitable = sorted(p.session_id for p in peers if p.session_id != session.session_id
                      and p.consent_to_aid and p.availability == "AVAILABLE"
                      and p.health == "HEALTHY_VERIFIED"
                      and "REVIEW" in p.capabilities)
    if not suitable:
        return dict(base, verdict="HOLD", reason="NO_QUALIFIED_CONSENTED_PEER")
    if not actual_receiver or not fenced_lease:
        return dict(base, verdict="PROPOSE_PEER_REVIEW",
                    reason="RECOVERY_NEEDS_AUTHENTICATED_RECEIVER_AND_FENCING",
                    peer_candidates=suitable)
    # Even with a receiver and lease this is an advisory handoff request, not
    # authority to close, impersonate, merge, mutate, or replace a live session.
    return dict(base, verdict="PROPOSE_REVERSIBLE_HANDOFF",
                reason="EVIDENCE_AND_FENCING_PRESENT__INDEPENDENT_ACK_STILL_REQUIRED",
                peer_candidates=suitable)
