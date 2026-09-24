#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os
from pathlib import Path
from typing import Any

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()

def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def load(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    obj = json.loads(raw.decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("FAIL_CLOSED__EXPECTED_OBJECT")
    return obj, raw

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    out = Path(args.output).resolve()
    if out.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out}")
    review, review_raw = load(Path(args.review).resolve())
    routes = list(review.get("open_relation_routes") or [])
    matches = [r for r in routes if r.get("route_state") == "MATCH_CANDIDATE"]
    if len(matches) != 1:
        raise SystemExit(f"FAIL_CLOSED__EXPECTED_ONE_MATCH={len(matches)}")
    route = matches[0]
    if route.get("assignment_executed") or route.get("notification_executed") or route.get("authority_change"):
        raise SystemExit("FAIL_CLOSED__R0B_EFFECT_BOUNDARY_BROKEN")
    deed = route.get("candidate_deed")
    if not isinstance(deed, dict) or deed.get("execution_authorized") is not False:
        raise SystemExit("FAIL_CLOSED__DEED_NOT_NONEXECUTING")
    src = review.get("source_bindings") or {}
    stable_basis = {
        "receiver_id": route.get("receiver_id"),
        "relation_id": route.get("relation_id"),
        "encounter_id": route.get("encounter_id"),
        "encounter_fixture_sha256": src.get("encounter_fixture_sha256"),
        "receiver_fixture_sha256": src.get("receiver_fixture_sha256"),
        "route_gates": route.get("gates"),
        "candidate_deed": deed,
    }
    route_digest = sha256_bytes(canonical(stable_basis))
    packet_id = "coencounter-packet:r0c:" + route_digest[:24]
    artifact = {
        "schema": "CoEncounterMatchPacket.R0C.v0.2-candidate",
        "state": "EXACT_MATCH_PACKET_COMPILED__DELIVERED_CANDIDATE__PICKUP_UNPROVEN",
        "packet_id": packet_id,
        "receiver_id": route["receiver_id"],
        "relation_id": route["relation_id"],
        "encounter_id": route["encounter_id"],
        "stable_route_digest_sha256": route_digest,
        "source_bindings": {
            "encounter_fixture_sha256": src.get("encounter_fixture_sha256"),
            "receiver_fixture_sha256": src.get("receiver_fixture_sha256"),
        },
        "route_gates": route.get("gates"),
        "candidate_deed": deed,
        "effects": {
            "assignment": 0,
            "notification": 0,
            "authority_change": 0,
            "receiver_context_mutation": 0,
            "provider_session_mutation": 0,
        },
        "next": "ELECTED_RECEIVER_EXACT_PACKET_READPROOF_BEFORE_PICKED_UP",
        "nonclaims": [
            "DELIVERY_NE_PICKUP",
            "MATCH_NE_ASSIGNMENT_AUTHORITY",
            "PACKET_NE_EXECUTION_AUTHORITY",
            "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
            "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
        ],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    enc = (json.dumps(artifact, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    out.write_bytes(enc)
    print(json.dumps({
        "STATE": artifact["state"],
        "OUTPUT": str(out),
        "OUTPUT_SHA256": sha256_bytes(enc),
        "PACKET_ID": packet_id,
        "STABLE_ROUTE_DIGEST_SHA256": route_digest,
        "SOURCE_REVIEW_SHA256": sha256_bytes(review_raw),
        "PROCESS_ID": os.getpid(),
        "NEXT": artifact["next"],
    }, separators=(",", ":")))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
