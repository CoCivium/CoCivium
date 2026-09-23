#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def run_json(cmd: list[str]) -> dict[str, Any]:
    cp = subprocess.run(cmd, check=True, capture_output=True, text=True)
    line = cp.stdout.strip().splitlines()[-1]
    obj = json.loads(line)
    if not isinstance(obj, dict):
        raise RuntimeError("subprocess terminal output not JSON object")
    return obj


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"not object: {path}")
    return obj


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--router", required=True)
    ap.add_argument("--receiver", required=True)
    ap.add_argument("--pulses", required=True)
    ap.add_argument("--profiles", required=True)
    ap.add_argument("--evolution-lanes", required=True)
    ap.add_argument("--out-root", required=True)
    args = ap.parse_args()

    out_root = Path(args.out_root).resolve()
    if out_root.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out_root}")
    out_root.mkdir(parents=True, exist_ok=False)

    router = str(Path(args.router).resolve())
    receiver = str(Path(args.receiver).resolve())
    pulses = str(Path(args.pulses).resolve())
    profiles = str(Path(args.profiles).resolve())
    lanes = str(Path(args.evolution_lanes).resolve())

    specs = [
        {
            "name":"A",
            "receiver_id":"VirtualReceiver-CoUX-A",
            "instance_id":"receiver-process-CoUX-A",
            "profile":"CoUX",
            "last_ack":0,
        },
        {
            "name":"B",
            "receiver_id":"VirtualReceiver-CoTheory-B",
            "instance_id":"receiver-process-CoTheory-B",
            "profile":"CoTheory",
            "last_ack":1,
        },
    ]

    records: list[dict[str, Any]] = []
    for spec in specs:
        packet_path = out_root / f"packet-{spec['name']}.json"
        router_terminal = run_json([
            sys.executable, router,
            "--pulses", pulses,
            "--profiles", profiles,
            "--evolution-lanes", lanes,
            "--profile-id", spec["profile"],
            "--last-acked-cursor", str(spec["last_ack"]),
            "--receiver-id", spec["receiver_id"],
            "--output", str(packet_path),
        ])
        packet_sha = sha256_path(packet_path)

        proof_path = out_root / f"readproof-{spec['name']}.json"
        receiver_terminal = run_json([
            sys.executable, receiver,
            "--packet", str(packet_path),
            "--expected-packet-sha256", packet_sha,
            "--expected-receiver-id", spec["receiver_id"],
            "--receiver-instance-id", spec["instance_id"],
            "--expected-last-acked-cursor", str(spec["last_ack"]),
            "--output", str(proof_path),
        ])

        packet = load(packet_path)
        proof = load(proof_path)
        records.append({
            "spec":spec,
            "router_terminal":router_terminal,
            "receiver_terminal":receiver_terminal,
            "packet_path":str(packet_path),
            "packet_sha256":packet_sha,
            "packet":packet,
            "proof_path":str(proof_path),
            "proof_sha256":sha256_path(proof_path),
            "proof":proof,
        })

    a,b = records
    if a["proof"]["receiver_process_id"] == b["proof"]["receiver_process_id"]:
        raise SystemExit("FAIL_CLOSED__RECEIVER_PROCESS_IDS_NOT_DISTINCT")
    if a["packet_sha256"] == b["packet_sha256"]:
        raise SystemExit("FAIL_CLOSED__ROLE_SPECIFIC_PACKETS_NOT_DISTINCT")

    a_source = (a["packet"].get("source_bindings") or {}).get("pulses_sha256")
    b_source = (b["packet"].get("source_bindings") or {}).get("pulses_sha256")
    if not a_source or a_source != b_source:
        raise SystemExit("FAIL_CLOSED__PACKETS_NOT_BOUND_TO_SAME_PULSE_FIELD")

    if a["proof"]["cursor"]["prior_acked_cursor"] == b["proof"]["cursor"]["prior_acked_cursor"]:
        raise SystemExit("FAIL_CLOSED__ACK_START_STATE_NOT_DISTINCT")
    if a["proof"]["cursor"]["ack_cursor_mutation_executed"] or b["proof"]["cursor"]["ack_cursor_mutation_executed"]:
        raise SystemExit("FAIL_CLOSED__UNEXPECTED_ACK_MUTATION")

    a_ids=set(a["proof"]["coverage"]["selected_pulse_ids"])
    b_ids=set(b["proof"]["coverage"]["selected_pulse_ids"])
    if a_ids == b_ids:
        raise SystemExit("FAIL_CLOSED__ROLE_SPECIFIC_SELECTED_SETS_NOT_DISTINCT")

    result = {
        "schema":"CoPulseTwoReceiverCanary.R0B.v0.1-candidate",
        "state":"PASS_R0B_TWO_DISTINCT_RECEIVER_PROCESSES__SAME_PULSE_FIELD__ROLE_SPECIFIC_PACKETS__INDEPENDENT_ACK_STATE__NO_SHARED_ACK_MUTATION",
        "coverage":{
            "pulse_field_sha256":a_source,
            "receiver_count":2,
            "same_failure_domain":"SAME_LOCAL_HOST_CONTAINER_FOR_THIS_CANARY",
            "global_bus":"UNPROVEN",
        },
        "receivers":[
            {
                "receiver_instance_id":r["proof"]["receiver_instance_id"],
                "receiver_id":r["proof"]["receiver_id"],
                "receiver_process_id":r["proof"]["receiver_process_id"],
                "profile_id":r["packet"]["profile_id"],
                "packet_sha256":r["packet_sha256"],
                "readproof_sha256":r["proof_sha256"],
                "prior_acked_cursor":r["proof"]["cursor"]["prior_acked_cursor"],
                "proposed_ack_cursor":r["proof"]["cursor"]["proposed_receiver_ack_cursor"],
                "selected_pulse_ids":r["proof"]["coverage"]["selected_pulse_ids"],
                "lifecycle_state":"PICKED_UP",
            }
            for r in records
        ],
        "independence_checks":{
            "distinct_process_ids":True,
            "distinct_receiver_ids":True,
            "distinct_profile_ids":a["packet"]["profile_id"] != b["packet"]["profile_id"],
            "same_pulse_field_hash":True,
            "distinct_packet_hashes":True,
            "distinct_selected_pulse_sets":True,
            "distinct_prior_ack_cursors":True,
            "shared_ack_mutation":False,
        },
        "effects":{
            "provider_session_mutation":0,
            "shared_ack_mutation":0,
            "authority_change":0,
            "public_outreach":0,
        },
        "next":"R0C_EXPLICIT_PER_RECEIVER_ACK_COMMIT_AND_BACKFILL_REPLAY_CANARY",
        "nonclaims":[
            "PICKED_UP_NE_INTEGRATED",
            "TWO_PROCESSES_NE_TWO_FAILURE_DOMAINS",
            "LOCAL_CANARY_NE_LIVE_GLOBAL_BUS",
            "PUBLIC_PACKET_NE_PRIVATE_BUS",
            "ACK_PROPOSAL_NE_ACK_COMMIT",
            "NO_PROVIDER_SESSION_PICKUP_CLAIM",
        ],
    }

    result_path=out_root/"canary-result.json"
    encoded=(json.dumps(result,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
    result_path.write_bytes(encoded)
    print(json.dumps({
        "STATE":result["state"],
        "OUTPUT":str(result_path),
        "OUTPUT_SHA256":hashlib.sha256(encoded).hexdigest().upper(),
        "RECEIVER_A_PID":a["proof"]["receiver_process_id"],
        "RECEIVER_B_PID":b["proof"]["receiver_process_id"],
        "PACKET_A_SHA256":a["packet_sha256"],
        "PACKET_B_SHA256":b["packet_sha256"],
        "PULSE_FIELD_SHA256":a_source,
        "NEXT":result["next"],
    },separators=(",",":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
