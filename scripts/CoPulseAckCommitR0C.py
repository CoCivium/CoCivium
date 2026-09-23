#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def load_object(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    obj = json.loads(raw.decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"expected JSON object: {path}")
    return obj, raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readproof", required=True)
    ap.add_argument("--expected-readproof-sha256", required=True)
    ap.add_argument("--expected-receiver-id", required=True)
    ap.add_argument("--expected-prior-acked-cursor", type=int, required=True)
    ap.add_argument("--recorded-at", required=True)
    ap.add_argument("--prior-ack")
    ap.add_argument("--expected-prior-ack-sha256")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    if args.expected_prior_acked_cursor < 0:
        raise SystemExit("FAIL_CLOSED__NEGATIVE_PRIOR_CURSOR")

    out = Path(args.output).resolve()
    if out.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out}")

    proof_path = Path(args.readproof).resolve()
    proof, proof_raw = load_object(proof_path)
    proof_sha = sha256_bytes(proof_raw)
    if proof_sha != args.expected_readproof_sha256.upper():
        raise SystemExit("FAIL_CLOSED__READPROOF_HASH_DRIFT")
    if proof.get("state") != "PICKED_UP_BOUNDED_EXACT_PACKET_READPROOF":
        raise SystemExit("FAIL_CLOSED__READPROOF_STATE_UNEXPECTED")
    if proof.get("receiver_id") != args.expected_receiver_id:
        raise SystemExit("FAIL_CLOSED__RECEIVER_ID_MISMATCH")

    cursor = proof.get("cursor") or {}
    prior = cursor.get("prior_acked_cursor")
    proposed = cursor.get("proposed_receiver_ack_cursor")
    if prior != args.expected_prior_acked_cursor:
        raise SystemExit("FAIL_CLOSED__READPROOF_PRIOR_CURSOR_MISMATCH")
    if cursor.get("ack_cursor_mutation_executed") is not False:
        raise SystemExit("FAIL_CLOSED__READPROOF_ALREADY_MUTATED_ACK")
    if not isinstance(proposed, int) or proposed < prior:
        raise SystemExit("FAIL_CLOSED__PROPOSED_ACK_INVALID")

    prior_ack_binding = None
    if args.prior_ack:
        if not args.expected_prior_ack_sha256:
            raise SystemExit("FAIL_CLOSED__PRIOR_ACK_HASH_REQUIRED")
        prior_path = Path(args.prior_ack).resolve()
        prior_ack, prior_raw = load_object(prior_path)
        prior_sha = sha256_bytes(prior_raw)
        if prior_sha != args.expected_prior_ack_sha256.upper():
            raise SystemExit("FAIL_CLOSED__PRIOR_ACK_HASH_DRIFT")
        if prior_ack.get("state") != "ACK_COMMITTED_BOUNDED_EXACT_READPROOF":
            raise SystemExit("FAIL_CLOSED__PRIOR_ACK_STATE_UNEXPECTED")
        if prior_ack.get("receiver_id") != args.expected_receiver_id:
            raise SystemExit("FAIL_CLOSED__PRIOR_ACK_RECEIVER_MISMATCH")
        if prior_ack.get("committed_acked_cursor") != prior:
            raise SystemExit("FAIL_CLOSED__PRIOR_ACK_CURSOR_CHAIN_BREAK")
        prior_ack_binding = {
            "path":str(prior_path),
            "sha256":prior_sha,
            "ack_event_id":prior_ack.get("ack_event_id"),
            "committed_acked_cursor":prior_ack.get("committed_acked_cursor"),
        }
    elif args.expected_prior_ack_sha256:
        raise SystemExit("FAIL_CLOSED__PRIOR_ACK_PATH_REQUIRED")

    packet = proof.get("packet") or {}
    packet_sha = str(packet.get("sha256") or "")
    if len(packet_sha) != 64:
        raise SystemExit("FAIL_CLOSED__PACKET_SHA256_MISSING")

    event_basis = {
        "receiver_id":args.expected_receiver_id,
        "prior":prior,
        "committed":proposed,
        "readproof_sha256":proof_sha,
        "recorded_at":args.recorded_at,
    }
    ack_event_id = "copulseack:" + sha256_bytes(
        json.dumps(event_basis, sort_keys=True, separators=(",",":")).encode("utf-8")
    )[:24]

    ack = {
        "schema":"CoPulseReceiverAck.R0C.v0.1-candidate",
        "state":"ACK_COMMITTED_BOUNDED_EXACT_READPROOF",
        "ack_event_id":ack_event_id,
        "recorded_at":args.recorded_at,
        "receiver_id":args.expected_receiver_id,
        "receiver_instance_id":proof.get("receiver_instance_id"),
        "previous_acked_cursor":prior,
        "committed_acked_cursor":proposed,
        "readproof":{
            "path":str(proof_path),
            "sha256":proof_sha,
        },
        "packet":{
            "packet_id":packet.get("packet_id"),
            "sha256":packet_sha,
            "profile_id":packet.get("profile_id"),
            "source_bindings":packet.get("source_bindings"),
        },
        "prior_ack":prior_ack_binding,
        "coverage":{
            "selected_pulse_ids":list((proof.get("coverage") or {}).get("selected_pulse_ids") or []),
            "selected_pulse_cursors":list((proof.get("coverage") or {}).get("selected_pulse_cursors") or []),
        },
        "effects":{
            "receiver_local_ack_commit":1,
            "shared_global_ack_mutation":0,
            "provider_session_mutation":0,
            "authority_change":0,
        },
        "next":"ROUTE_BACKFILL_AFTER_COMMITTED_CURSOR",
        "nonclaims":[
            "ACK_COMMIT_NE_INTEGRATION",
            "ACK_COMMIT_NE_COEX",
            "RECEIVER_LOCAL_ACK_NE_GLOBAL_ACK",
            "ACK_CURSOR_NE_PROVIDER_CONTEXT_MUTATION",
        ],
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    encoded=(json.dumps(ack,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
    out.write_bytes(encoded)
    print(json.dumps({
        "STATE":ack["state"],
        "OUTPUT":str(out),
        "OUTPUT_SHA256":sha256_bytes(encoded),
        "RECEIVER_ID":args.expected_receiver_id,
        "PREVIOUS_ACK":prior,
        "COMMITTED_ACK":proposed,
        "PRIOR_ACK_BOUND":prior_ack_binding is not None,
        "NEXT":ack["next"],
    },separators=(",",":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
