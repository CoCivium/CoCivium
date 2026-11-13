"""CoFront+ / CoEcho+ / CoTime+ R0: bounded historical replay projections.

This is a deterministic read-only replay of explicit candidate records, not
a historical crawler, a proof that all sessions were scanned, or canonization.
Private source references stay out of public output.
"""
from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class Echo:
    source_ref: str
    work_id: str
    revision: str
    content_sha256: str
    observed_at: str = ""  # ISO 8601 or unknown, not necessarily event time
    historical_at: str = ""  # explicit original time or empty
    front_id: str = ""
    kind: str = "ARTIFACT"
    privacy_scope: str = "RESTRICTED"
    relationship: str = "UNKNOWN"
    evidence_ref: str = ""
    semantic_reviewed: bool = False


def stable_identity(item):
    """Exact WorkID + revision + bytes: duplicate appearance != new work."""
    raw = json.dumps([item.work_id, item.revision, item.content_sha256],
                     ensure_ascii=False, separators=(",", ":"))
    return sha256(raw.encode("utf-8")).hexdigest()


def replay(echoes, *, max_records=100, known_fronts=()):
    """Append-only candidate reconstruction; no guessed chronology or ownership."""
    if max_records < 1:
        raise ValueError("positive bounded replay required")
    accepted, held, duplicates, seen = [], [], [], set()
    for index, item in enumerate(echoes):
        if index >= max_records:
            held.append(("UNINSPECTED_REMAINDER", "SCAN_BOUND_REACHED"))
            break
        if not item.source_ref or not item.work_id or not item.revision or not item.content_sha256:
            held.append((item.work_id or "UNKNOWN", "INCOMPLETE_PROVENANCE"))
            continue
        if (len(item.content_sha256) != 64
                or any(c not in "0123456789abcdef" for c in item.content_sha256.lower())):
            held.append((item.work_id, "INVALID_HASH_FORMAT"))
            continue
        if item.privacy_scope not in ("PUBLIC", "RESTRICTED"):
            held.append((item.work_id, "UNKNOWN_PRIVACY_SCOPE"))
            continue
        key = stable_identity(item)
        if key in seen:
            duplicates.append(key)
            continue
        seen.add(key)
        accepted.append({
            "identity": key,
            "work_id": item.work_id,
            "revision": item.revision,
            "front_id": item.front_id or "UNCLASSIFIED_FRONT",
            "historical_at": item.historical_at or None,
            "observed_at": item.observed_at or None,
            "relationship": item.relationship,
            "semantic_status": ("REVIEWED_CANDIDATE" if item.semantic_reviewed
                                else "NOT_SEMANTICALLY_REVIEWED"),
            "privacy_scope": item.privacy_scope,
            "source_ref": item.source_ref,
            "evidence_ref": item.evidence_ref,
            "lifecycle": "VERIFIED_POINTER_NOT_ACCEPTED",
            "coex": False,
        })
    classified = {x["front_id"] for x in accepted}
    debt = sorted(set(known_fronts) - classified)
    return {
        "schema": "CoFront.RetroEcho.R0",
        "accepted_candidates": accepted,
        "duplicate_identities": duplicates,
        "held": held,
        "fronts_without_evidence": debt,
        "coverage": {"scanned_candidate_records": min(len(echoes), max_records),
                     "known_fronts_in_scope": len(set(known_fronts)),
                     "complete_history": False,
                     "retro_predictive_accuracy_proven": False},
        "nonclaims": ["LOCAL_IS_NOT_LANDED", "VALIDATION_IS_NOT_ACCEPTANCE",
                      "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
                      "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
                      "HASHING_IS_NOT_SEMANTIC_INGESTION",
                      "DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY"],
    }


def chronological_view(report):
    """Known historical dates sort; unknown dates remain a separate bucket."""
    dated = sorted((x for x in report["accepted_candidates"] if x["historical_at"]),
                   key=lambda x: (x["historical_at"], x["identity"]))
    undated = sorted((x for x in report["accepted_candidates"] if not x["historical_at"]),
                     key=lambda x: x["identity"])
    return {"known_historical_order": dated,
            "unknown_historical_order": undated,
            "timestamps_independently_verified": False}


def public_rollup(report):
    """No source paths, WorkIDs, evidence IDs or content hashes exposed."""
    return {
        "schema": report["schema"],
        "candidate_count": len(report["accepted_candidates"]),
        "duplicate_count": len(report["duplicate_identities"]),
        "held_count": len(report["held"]),
        "uncovered_front_count": len(report["fronts_without_evidence"]),
        "historical_coverage_complete": False,
        "receiver_pickup_proven": False,
        "semantic_ingestion_proven": False,
    }
