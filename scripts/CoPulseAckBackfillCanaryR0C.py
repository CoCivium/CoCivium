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


def load(path: Path) -> dict[str, Any]:
    obj=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"not object: {path}")
    return obj


def run_json(cmd: list[str]) -> dict[str, Any]:
    cp=subprocess.run(cmd,check=True,capture_output=True,text=True)
    line=cp.stdout.strip().splitlines()[-1]
    obj=json.loads(line)
    if not isinstance(obj,dict):
        raise RuntimeError("terminal output not JSON object")
    return obj


def route_receive_commit(
    *,
    python_exe: str,
    router: str,
    receiver: str,
    ack_commit: str,
    pulses: str,
    profiles: str,
    lanes: str,
    profile: str,
    receiver_id: str,
    instance_id: str,
    prior_cursor: int,
    recorded_at: str,
    out_root: Path,
    suffix: str,
    prior_ack_path: Path | None = None,
) -> dict[str, Any]:
    packet_path=out_root/f"packet-{suffix}.json"
    run_json([
        python_exe,router,
        "--pulses",pulses,
        "--profiles",profiles,
        "--evolution-lanes",lanes,
        "--profile-id",profile,
        "--last-acked-cursor",str(prior_cursor),
        "--receiver-id",receiver_id,
        "--output",str(packet_path),
    ])
    packet_sha=sha256_path(packet_path)

    proof_path=out_root/f"readproof-{suffix}.json"
    proof_terminal=run_json([
        python_exe,receiver,
        "--packet",str(packet_path),
        "--expected-packet-sha256",packet_sha,
        "--expected-receiver-id",receiver_id,
        "--receiver-instance-id",instance_id,
        "--expected-last-acked-cursor",str(prior_cursor),
        "--output",str(proof_path),
    ])
    proof_sha=sha256_path(proof_path)

    ack_path=out_root/f"ack-{suffix}.json"
    cmd=[
        python_exe,ack_commit,
        "--readproof",str(proof_path),
        "--expected-readproof-sha256",proof_sha,
        "--expected-receiver-id",receiver_id,
        "--expected-prior-acked-cursor",str(prior_cursor),
        "--recorded-at",recorded_at,
        "--output",str(ack_path),
    ]
    if prior_ack_path is not None:
        cmd.extend([
            "--prior-ack",str(prior_ack_path),
            "--expected-prior-ack-sha256",sha256_path(prior_ack_path),
        ])
    ack_terminal=run_json(cmd)

    return {
        "packet_path":packet_path,
        "packet_sha256":packet_sha,
        "packet":load(packet_path),
        "proof_path":proof_path,
        "proof_sha256":proof_sha,
        "proof":load(proof_path),
        "proof_terminal":proof_terminal,
        "ack_path":ack_path,
        "ack_sha256":sha256_path(ack_path),
        "ack":load(ack_path),
        "ack_terminal":ack_terminal,
    }


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--router",required=True)
    ap.add_argument("--receiver",required=True)
    ap.add_argument("--ack-commit",required=True)
    ap.add_argument("--base-pulses",required=True)
    ap.add_argument("--extended-pulses",required=True)
    ap.add_argument("--profiles",required=True)
    ap.add_argument("--evolution-lanes",required=True)
    ap.add_argument("--out-root",required=True)
    args=ap.parse_args()

    out_root=Path(args.out_root).resolve()
    if out_root.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out_root}")
    out_root.mkdir(parents=True,exist_ok=False)

    python_exe=sys.executable
    router=str(Path(args.router).resolve())
    receiver=str(Path(args.receiver).resolve())
    ack_commit=str(Path(args.ack_commit).resolve())
    profiles=str(Path(args.profiles).resolve())
    lanes=str(Path(args.evolution_lanes).resolve())

    a1=route_receive_commit(
        python_exe=python_exe,router=router,receiver=receiver,ack_commit=ack_commit,
        pulses=str(Path(args.base_pulses).resolve()),profiles=profiles,lanes=lanes,
        profile="CoUX",receiver_id="VirtualReceiver-CoUX-A",instance_id="receiver-process-CoUX-A-R1",
        prior_cursor=0,recorded_at="2026-09-23T12:20:00Z",out_root=out_root,suffix="A1"
    )
    b1=route_receive_commit(
        python_exe=python_exe,router=router,receiver=receiver,ack_commit=ack_commit,
        pulses=str(Path(args.base_pulses).resolve()),profiles=profiles,lanes=lanes,
        profile="CoTheory",receiver_id="VirtualReceiver-CoTheory-B",instance_id="receiver-process-CoTheory-B-R1",
        prior_cursor=1,recorded_at="2026-09-23T12:20:01Z",out_root=out_root,suffix="B1"
    )

    if a1["ack"]["committed_acked_cursor"] != 3 or b1["ack"]["committed_acked_cursor"] != 3:
        raise SystemExit("FAIL_CLOSED__ROUND1_ACK_EXPECTATION")

    a2=route_receive_commit(
        python_exe=python_exe,router=router,receiver=receiver,ack_commit=ack_commit,
        pulses=str(Path(args.extended_pulses).resolve()),profiles=profiles,lanes=lanes,
        profile="CoUX",receiver_id="VirtualReceiver-CoUX-A",instance_id="receiver-process-CoUX-A-R2",
        prior_cursor=a1["ack"]["committed_acked_cursor"],recorded_at="2026-09-23T12:20:02Z",
        out_root=out_root,suffix="A2",prior_ack_path=a1["ack_path"]
    )
    b2=route_receive_commit(
        python_exe=python_exe,router=router,receiver=receiver,ack_commit=ack_commit,
        pulses=str(Path(args.extended_pulses).resolve()),profiles=profiles,lanes=lanes,
        profile="CoTheory",receiver_id="VirtualReceiver-CoTheory-B",instance_id="receiver-process-CoTheory-B-R2",
        prior_cursor=b1["ack"]["committed_acked_cursor"],recorded_at="2026-09-23T12:20:03Z",
        out_root=out_root,suffix="B2",prior_ack_path=b1["ack_path"]
    )

    if a2["proof"]["coverage"]["selected_pulse_ids"] != ["pulse.fixture.ux.004"]:
        raise SystemExit("FAIL_CLOSED__COUX_BACKFILL_SELECTION_UNEXPECTED")
    if b2["proof"]["coverage"]["selected_pulse_ids"] != ["pulse.fixture.theory.005"]:
        raise SystemExit("FAIL_CLOSED__COTHEORY_BACKFILL_SELECTION_UNEXPECTED")
    if a2["ack"]["committed_acked_cursor"] != 4:
        raise SystemExit("FAIL_CLOSED__COUX_FINAL_ACK_UNEXPECTED")
    if b2["ack"]["committed_acked_cursor"] != 5:
        raise SystemExit("FAIL_CLOSED__COTHEORY_FINAL_ACK_UNEXPECTED")
    if a2["ack"]["prior_ack"]["sha256"] != a1["ack_sha256"]:
        raise SystemExit("FAIL_CLOSED__COUX_ACK_CHAIN_BROKEN")
    if b2["ack"]["prior_ack"]["sha256"] != b1["ack_sha256"]:
        raise SystemExit("FAIL_CLOSED__COTHEORY_ACK_CHAIN_BROKEN")
    if a2["ack"]["prior_ack"]["sha256"] == b2["ack"]["prior_ack"]["sha256"]:
        raise SystemExit("FAIL_CLOSED__RECEIVER_ACK_CHAINS_COLLAPSED")

    ext_source_a=(a2["packet"].get("source_bindings") or {}).get("pulses_sha256")
    ext_source_b=(b2["packet"].get("source_bindings") or {}).get("pulses_sha256")
    if not ext_source_a or ext_source_a != ext_source_b:
        raise SystemExit("FAIL_CLOSED__ROUND2_NOT_SAME_EXTENDED_PULSE_FIELD")

    result={
        "schema":"CoPulseAckBackfillCanary.R0C.v0.1-candidate",
        "state":"PASS_R0C_PER_RECEIVER_ACK_COMMIT__CHAINED_READPROOF__ROLE_SPECIFIC_BACKFILL_REPLAY__INDEPENDENT_CURSOR_ADVANCE",
        "coverage":{
            "receiver_count":2,
            "rounds":2,
            "round2_extended_pulse_field_sha256":ext_source_a,
            "same_failure_domain":"SAME_LOCAL_HOST_CONTAINER_FOR_THIS_CANARY",
        },
        "receivers":[
            {
                "receiver_id":"VirtualReceiver-CoUX-A",
                "round1_ack_sha256":a1["ack_sha256"],
                "round1_committed_cursor":a1["ack"]["committed_acked_cursor"],
                "round2_readproof_sha256":a2["proof_sha256"],
                "round2_selected_pulse_ids":a2["proof"]["coverage"]["selected_pulse_ids"],
                "round2_ack_sha256":a2["ack_sha256"],
                "final_committed_cursor":a2["ack"]["committed_acked_cursor"],
            },
            {
                "receiver_id":"VirtualReceiver-CoTheory-B",
                "round1_ack_sha256":b1["ack_sha256"],
                "round1_committed_cursor":b1["ack"]["committed_acked_cursor"],
                "round2_readproof_sha256":b2["proof_sha256"],
                "round2_selected_pulse_ids":b2["proof"]["coverage"]["selected_pulse_ids"],
                "round2_ack_sha256":b2["ack_sha256"],
                "final_committed_cursor":b2["ack"]["committed_acked_cursor"],
            },
        ],
        "checks":{
            "readproof_before_each_ack":True,
            "prior_ack_hash_chain_bound":True,
            "no_cursor_regression":True,
            "receiver_ack_chains_distinct":True,
            "same_extended_pulse_field":True,
            "role_specific_backfill":True,
            "final_cursors_diverge":True,
        },
        "effects":{
            "receiver_local_ack_files_written":4,
            "shared_global_ack_mutation":0,
            "provider_session_mutation":0,
            "authority_change":0,
        },
        "next":"R0D_COPRESSURE_DIGEST_COMPACTION_WITH_EXPLICIT_LOSS_REPORT_AND_REPLAY",
        "nonclaims":[
            "ACK_COMMIT_NE_INTEGRATION",
            "ACK_COMMIT_NE_COEX",
            "RECEIVER_LOCAL_ACK_NE_GLOBAL_ACK",
            "TWO_RECEIVERS_NE_TWO_FAILURE_DOMAINS",
            "LOCAL_CANARY_NE_LIVE_GLOBAL_BUS",
            "NO_PROVIDER_SESSION_PICKUP_CLAIM",
        ],
    }

    result_path=out_root/"r0c-result.json"
    encoded=(json.dumps(result,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
    result_path.write_bytes(encoded)
    print(json.dumps({
        "STATE":result["state"],
        "OUTPUT":str(result_path),
        "OUTPUT_SHA256":hashlib.sha256(encoded).hexdigest().upper(),
        "COUX_FINAL_ACK":a2["ack"]["committed_acked_cursor"],
        "COTHEORY_FINAL_ACK":b2["ack"]["committed_acked_cursor"],
        "COUX_BACKFILL":a2["proof"]["coverage"]["selected_pulse_ids"],
        "COTHEORY_BACKFILL":b2["proof"]["coverage"]["selected_pulse_ids"],
        "NEXT":result["next"],
    },separators=(",",":")))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
