#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", required=True)
    ap.add_argument("--expected-packet-sha256", required=True)
    ap.add_argument("--expected-receiver-id", required=True)
    ap.add_argument("--receiver-instance-id", required=True)
    ap.add_argument("--expected-last-acked-cursor", type=int, required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    packet_path = Path(args.packet).resolve()
    out = Path(args.output).resolve()
    if out.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out}")

    raw = packet_path.read_bytes()
    packet_sha = sha256_bytes(raw)
    if packet_sha != args.expected_packet_sha256.upper():
        raise SystemExit(
            f"FAIL_CLOSED__PACKET_HASH_DRIFT__EXPECTED={args.expected_packet_sha256.upper()}__ACTUAL={packet_sha}"
        )

    packet = json.loads(raw.decode("utf-8"))
    if not isinstance(packet, dict):
        raise SystemExit("FAIL_CLOSED__PACKET_NOT_OBJECT")
    if packet.get("state") != "PUBLIC_SAFE_PACKET_COMPILED__DELIVERY_NOT_PICKUP":
        raise SystemExit("FAIL_CLOSED__PACKET_STATE_UNEXPECTED")
    if packet.get("receiver_id") != args.expected_receiver_id:
        raise SystemExit("FAIL_CLOSED__RECEIVER_ID_MISMATCH")

    cursor = packet.get("cursor") or {}
    last_acked = cursor.get("last_acked_cursor")
    unchanged = cursor.get("ack_cursor_unchanged")
    candidate = cursor.get("candidate_delivered_cursor")
    if last_acked != args.expected_last_acked_cursor or unchanged != args.expected_last_acked_cursor:
        raise SystemExit("FAIL_CLOSED__ACK_CURSOR_INPUT_MISMATCH")
    if not isinstance(candidate, int) or candidate < args.expected_last_acked_cursor:
        raise SystemExit("FAIL_CLOSED__CANDIDATE_DELIVERED_CURSOR_INVALID")

    selected = list(packet.get("selected_pulses") or [])
    pulse_ids: list[str] = []
    pulse_cursors: list[int] = []
    for p in selected:
        if not isinstance(p, dict):
            raise SystemExit("FAIL_CLOSED__SELECTED_PULSE_NOT_OBJECT")
        pid = str(p.get("pulse_id") or "")
        pcursor = p.get("cursor")
        if not pid or not isinstance(pcursor, int):
            raise SystemExit("FAIL_CLOSED__SELECTED_PULSE_ID_OR_CURSOR_INVALID")
        if pcursor <= args.expected_last_acked_cursor:
            raise SystemExit("FAIL_CLOSED__PACKET_CONTAINS_ACKED_OR_OLDER_PULSE")
        pulse_ids.append(pid)
        pulse_cursors.append(pcursor)

    process_id = os.getpid()
    proof = {
        "schema":"CoPulseReceiverReadproof.R0B.v0.1-candidate",
        "state":"PICKED_UP_BOUNDED_EXACT_PACKET_READPROOF",
        "receiver_instance_id":args.receiver_instance_id,
        "receiver_id":args.expected_receiver_id,
        "receiver_process_id":process_id,
        "packet":{
            "path":str(packet_path),
            "packet_id":packet.get("packet_id"),
            "sha256":packet_sha,
            "profile_id":packet.get("profile_id"),
            "source_bindings":packet.get("source_bindings"),
        },
        "coverage":{
            "selected_pulse_count":len(selected),
            "selected_pulse_ids":pulse_ids,
            "selected_pulse_cursors":pulse_cursors,
        },
        "cursor":{
            "prior_acked_cursor":args.expected_last_acked_cursor,
            "packet_candidate_delivered_cursor":candidate,
            "proposed_receiver_ack_cursor":candidate,
            "ack_cursor_mutation_executed":False,
        },
        "acceptance":{
            "exact_packet_bytes_read":True,
            "packet_hash_verified":True,
            "receiver_identity_verified":True,
            "selected_entries_parsed":True,
            "working_baseline_integration":"NOT_PROVEN",
        },
        "next":"SEPARATE_ACK_COMMIT_ONLY_AFTER_RECEIVER_POLICY_ACCEPTS_PACKET",
        "nonclaims":[
            "PICKED_UP_NE_INTEGRATED",
            "PICKED_UP_NE_COEX",
            "READPROOF_NE_SHARED_ACK_MUTATION",
            "RECEIVER_PROCESS_NE_PROVIDER_SESSION",
            "PUBLIC_PACKET_NE_PRIVATE_BUS",
        ],
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    encoded=(json.dumps(proof,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
    out.write_bytes(encoded)
    print(json.dumps({
        "STATE":proof["state"],
        "OUTPUT":str(out),
        "OUTPUT_SHA256":sha256_bytes(encoded),
        "RECEIVER_INSTANCE_ID":args.receiver_instance_id,
        "RECEIVER_PROCESS_ID":process_id,
        "PACKET_SHA256":packet_sha,
        "SELECTED":len(selected),
        "PRIOR_ACK":args.expected_last_acked_cursor,
        "PROPOSED_ACK":candidate,
        "ACK_MUTATION_EXECUTED":False,
        "NEXT":proof["next"],
    },separators=(",",":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
