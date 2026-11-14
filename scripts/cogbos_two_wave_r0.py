#!/usr/bin/env python3
"""CoGBOS two-wave offline proof. Synthetic only; no network or external effects."""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass

WORK_ID = "copregeneric:handoff:public-seed-path:r0:20261109"
SOURCE_BLOB_SHA = "8ce4e8d81ca78209a083fd92d034da3676eaed7c"

@dataclass(frozen=True)
class Proposal:
    name: str
    wave: int
    strategy: str
    source_sha: str
    consent: bool
    score: int
    writer: str

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def elect(proposals, allowed_writers, baseline):
    """Qualify, elect exactly one allowed writer or preserve baseline."""
    rejected = []
    eligible = []
    for p in proposals:
        reasons = []
        if p.source_sha != SOURCE_BLOB_SHA:
            reasons.append("SOURCE_MISMATCH")
        if not p.consent:
            reasons.append("CONSENT_MISSING")
        if p.writer not in allowed_writers:
            reasons.append("WRITER_UNAUTHORIZED")
        if reasons:
            rejected.append({"name": p.name, "reasons": reasons})
        else:
            eligible.append(p)
    # A deterministic collision election. Not a real distributed lock.
    eligible.sort(key=lambda p: (-p.score, p.name, p.writer))
    winner = eligible[0] if eligible else None
    return {
        "winner": winner.name if winner else None,
        "actuator": winner.writer if winner else None,
        "rejected": rejected,
        "eligible": [p.name for p in eligible],
        "selected_state": digest({"work_id": WORK_ID, "winner": winner.name}) if winner else baseline,
        "disposition": "CANDIDATE_SELECTED_NOT_DEPLOYED" if winner else "ROLLBACK_TO_BASELINE"
    }

def run_demo():
    baseline = digest({"work_id": WORK_ID, "version": "baseline"})
    wave1 = [
        Proposal("story_parable", 1, "narrative", SOURCE_BLOB_SHA, True, 8, "worker-a"),
        Proposal("diagram", 1, "visual", SOURCE_BLOB_SHA, True, 7, "worker-b"),
        Proposal("untrusted_signal", 1, "speculative", "0"*40, False, 99, "worker-c"),
    ]
    first = elect(wave1, {"worker-a", "worker-b"}, baseline)
    wave2 = [
        Proposal("failed_followup", 2, "adversarial", "f"*40, False, 100, "worker-b"),
        Proposal("unauthorized_writer", 2, "control", SOURCE_BLOB_SHA, True, 90, "worker-c"),
    ]
    second = elect(wave2, {"worker-a", "worker-b"}, first["selected_state"])
    # The second wave may not advance the state, and 'rollback' here returns to
    # the previous qualified candidate only; it does not mutate the filesystem.
    report = {
        "schema": "CoGBOS.TwoWaveOfflineProof.R0",
        "work_id": WORK_ID,
        "source_blob_sha": SOURCE_BLOB_SHA,
        "scope": "SYNTHETIC_OFFLINE_NO_SIDE_EFFECTS",
        "wave_count": 2,
        "distinct_strategies": sorted({p.strategy for p in wave1 + wave2}),
        "wave1": first,
        "wave2": second,
        "preserved_state": second["selected_state"],
        "receiver": {"state": "NO_INDEPENDENT_RECEIVER", "ack": None},
        "deployment": "NONE",
        "mirror_status": "NOT_VERIFIED",
        "nonclaims": [
            "VALIDATION_IS_NOT_ACCEPTANCE", "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
            "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
            "NO_CROSS_SESSION_SYNC", "NO_24H_SURVIVAL_PROOF",
            "LOCAL_IS_NOT_LANDED", "HASHING_IS_NOT_SEMANTIC_INGESTION",
            "DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY"
        ]
    }
    return report

if __name__ == "__main__":
    print(json.dumps(run_demo(), sort_keys=True, indent=2))
