"""CoPre R0: deterministic, append-only session-drain intake qualification.

No connected session is contacted and no public log is written. The caller
provides explicit records from an authorized adapter. A transcript claim that
a prompt was pasted is not a provider readback or an independently received ACK.
"""
from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class DrainEcho:
    session_ref: str
    source_ref: str
    seed_revision: str
    body: str
    source_scope: str = "RESTRICTED"
    provider_readback: str = ""
    reviewer_approved_public: bool = False


def fingerprint(echo):
    """Stable identical-content identity; never normalize different revisions."""
    values = [echo.session_ref, echo.source_ref, echo.seed_revision, echo.body]
    return sha256(json.dumps(values, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def reconcile(echoes, *, known_seed_revisions=(), max_records=100):
    if max_records < 1:
        raise ValueError("positive bounded intake required")
    accepted, duplicates, held, seen = [], [], [], set()
    for index, echo in enumerate(echoes):
        if index >= max_records:
            held.append(("OUTSIDE_BOUND", "REMAINING_UNINSPECTED"))
            break
        digest = fingerprint(echo)
        if digest in seen:
            duplicates.append(digest)
            continue
        seen.add(digest)
        if not echo.session_ref or not echo.source_ref or not echo.seed_revision or not echo.body:
            held.append((digest, "INCOMPLETE_PROVENANCE"))
        elif echo.seed_revision not in known_seed_revisions:
            held.append((digest, "UNQUALIFIED_SEED_REVISION"))
        elif echo.source_scope not in ("PUBLIC", "RESTRICTED"):
            held.append((digest, "INVALID_SCOPE"))
        elif not echo.provider_readback:
            held.append((digest, "NO_INDEPENDENT_SESSION_READBACK"))
        else:
            accepted.append({
                "fingerprint": digest, "session_ref": echo.session_ref,
                "seed_revision": echo.seed_revision,
                "state": "RECEIVED_FOR_REVIEW",
                "source_scope": echo.source_scope,
                "public_projection_eligible": (
                    echo.source_scope == "PUBLIC" and echo.reviewer_approved_public),
                "actual_session_drain_proven": False,
                "cross_provider_sync_proven": False,
            })
    return {"schema": "CoPre.DrainIntake.R0",
            "accepted_for_review": accepted,
            "identical_echo_duplicates": duplicates,
            "held": held,
            "complete_session_history": False,
            "external_delivery_effects": 0,
            "public_write_effects": 0}


def safe_public_rollup(report):
    """No body, provider receipt, session identity or private source refs."""
    return {"schema": report["schema"], "accepted_for_review_count":
            len(report["accepted_for_review"]),
            "identical_duplicate_count": len(report["identical_echo_duplicates"]),
            "held_count": len(report["held"]),
            "complete_session_history": False,
            "verified_drains": 0,
            "public_write_effects": 0}
