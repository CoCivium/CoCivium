#!/usr/bin/env python3
"""CoSession succession evidence-shape gate R0 (public synthetic, zero effects).

This is a regression guard for source-preserving convergence, not a
provider-session reader, independent receiver, or session-close actuator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCHEMA = "CoSession.SuccessionFixture.R0"
NONCLAIMS = [
    "SYNTHETIC_RECEIPT_SHAPE_NE_INDEPENDENT_ACK",
    "SHARED_FRONT_NE_PROVIDER_SESSION_MERGE",
    "CLOSE_SAFE_CANDIDATE_NE_DELETE_SAFE",
    "NO_PROVIDER_MUTATION_OR_PUBLIC_PRIVATE_DATA_ECHO",
    "SOURCE_HASH_NE_SEMANTIC_INGESTION",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
]
EFFECTS = {
    "provider_sessions_closed": 0,
    "provider_sessions_deleted": 0,
    "external_messages": 0,
    "runtime_changes": 0,
    "account_changes": 0,
    "publications": 0,
}


def digest(record: dict) -> str:
    return hashlib.sha256(json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def valid_actor_id(value: object) -> bool:
    """Bounded, printable, unambiguous claimed actor label; not authentication."""
    return (type(value) is str and 1 <= len(value) <= 128
            and all(c.isascii() and (c.isalnum() or c in "._:-") for c in value))


def evaluate(payload: dict) -> dict:
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA:
        raise ValueError("HOLD_SCHEMA")
    shared = payload.get("work_id")
    records = payload.get("sources")
    if not isinstance(shared, str) or not shared or not isinstance(records, list) or not 2 <= len(records) <= 8:
        raise ValueError("HOLD_SCOPE")
    seen_ids, seen_refs = set(), set()
    reasons, contributions, dissent, obligations = set(), set(), set(), set()
    sources = []
    for r in records:
        if not isinstance(r, dict):
            raise ValueError("HOLD_SOURCE_SHAPE")
        sid, ref, sha = r.get("session_id"), r.get("source_ref"), r.get("source_sha256")
        if not isinstance(sid, str) or not sid or sid in seen_ids:
            raise ValueError("HOLD_SOURCE_IDENTITY")
        if not isinstance(ref, str) or not ref or ref in seen_refs:
            raise ValueError("HOLD_SOURCE_REF")
        if not isinstance(sha, str) or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            raise ValueError("HOLD_SOURCE_HASH")
        seen_ids.add(sid)
        seen_refs.add(ref)
        if r.get("work_id") != shared:
            reasons.add("WORK_ID_COLLISION")
        if r.get("privacy_class") != "PUBLIC_SYNTHETIC":
            reasons.add("PRIVACY_NOT_QUALIFIED")
        if r.get("authority_ceiling") != "NO_EFFECTS":
            reasons.add("AUTHORITY_MISMATCH")
        for field in ("contribution_ids", "dissent_ids", "unresolved_obligations"):
            v = r.get(field)
            if not isinstance(v, list) or any(not isinstance(x, str) or not x for x in v):
                raise ValueError("HOLD_" + field.upper())
        contributions.update(r["contribution_ids"])
        dissent.update(r["dissent_ids"])
        obligations.update(r["unresolved_obligations"])
        sources.append({"session_id": sid, "source_ref": ref, "source_sha256": sha, "disposition": "PRESERVED"})
    successor = payload.get("successor")
    if not isinstance(successor, dict):
        raise ValueError("HOLD_SUCCESSOR_SHAPE")
    if successor.get("work_id") != shared:
        reasons.add("SUCCESSOR_WORK_ID_MISMATCH")
    if successor.get("privacy_class") != "PUBLIC_SYNTHETIC" or successor.get("authority_ceiling") != "NO_EFFECTS":
        reasons.add("SUCCESSOR_SCOPE_MISMATCH")
    # These labels remain claims, NOT independent receiver authentication.
    # Malformed or missing claimed identities may not qualify even a shadow front.
    producer_id = successor.get("producer_id")
    verifier_id = successor.get("verifier_id")
    if not valid_actor_id(producer_id):
        reasons.add("PRODUCER_IDENTITY_INVALID")
    if not valid_actor_id(verifier_id):
        reasons.add("VERIFIER_IDENTITY_INVALID")
    if (valid_actor_id(producer_id) and valid_actor_id(verifier_id)
            and producer_id == verifier_id):
        reasons.add("VERIFIER_NOT_DISTINCT")
    claimed = successor.get("source_digests")
    if not isinstance(claimed, dict) or claimed != {x["session_id"]: x["source_sha256"] for x in sources}:
        reasons.add("MISSING_OR_CHANGED_SOURCE_DIGEST")
    for key, original in (("contribution_ids", contributions), ("dissent_ids", dissent), ("accepted_obligations", obligations)):
        value = successor.get(key)
        if not isinstance(value, list) or set(value) != original or len(value) != len(set(value)):
            reasons.add("SUCCESSOR_" + key.upper() + "_LOSS")
    if successor.get("receiver_readproof") is not True:
        reasons.add("RECEIVER_READPROOF_NOT_DECLARED")
    # A user-controlled fixture cannot prove an independent receiver actually read it.
    # Never turn this label into native close, merge, deletion, or provider authorization.
    state = "SHADOW_CANDIDATE__INDEPENDENT_RECEIVER_UNVERIFIED" if not reasons else "HELD__SOURCE_OR_SUCCESSOR_GAP"
    return {
        "schema": "CoSession.SuccessionProjection.R0",
        "state": state,
        "work_id": shared,
        "coverage": {"observed_source_count": len(records), "global_session_census": "UNPROVEN"},
        "source_lineage": sources,
        "distinct_contribution_count": len(contributions),
        "preserved_dissent_ids": sorted(dissent),
        "preserved_unresolved_obligations": sorted(obligations),
        "reasons": sorted(reasons),
        "receiver_proof": "SYNTHETIC_SHAPE_ONLY_NOT_INDEPENDENT",
        "close_safe": False,
        "delete_safe": False,
        "one_visible_front_candidate": not reasons,
        "next_safe_deed": "OBTAIN_RECEIVER_ORIGIN_EXACT_READPROOF_AND_RESTORE_TEST" if not reasons else "RESOLVE_SOURCE_AND_SUCCESSOR_GAPS",
        "effects": dict(EFFECTS),
        "nonclaims": list(NONCLAIMS),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--fixture", type=Path, required=True)
    args = p.parse_args()
    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    print(json.dumps(evaluate(fixture), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
