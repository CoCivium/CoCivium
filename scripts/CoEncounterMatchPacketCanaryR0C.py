#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
from typing import Any

def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(path)
    return obj

def run_json(cmd: list[str]) -> dict[str, Any]:
    cp = subprocess.run(cmd, check=True, capture_output=True, text=True)
    line = cp.stdout.strip().splitlines()[-1]
    obj = json.loads(line)
    if not isinstance(obj, dict):
        raise RuntimeError("terminal output not object")
    return obj

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet-builder", required=True)
    ap.add_argument("--readproof", required=True)
    ap.add_argument("--lineage-binder", required=True)
    ap.add_argument("--review", required=True)
    ap.add_argument("--contribution-payload", required=True)
    ap.add_argument("--out-root", required=True)
    args = ap.parse_args()
    root = Path(args.out_root).resolve()
    if root.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={root}")
    root.mkdir(parents=True, exist_ok=False)
    packet = root / "match-packet.json"
    pterm = run_json([sys.executable, str(Path(args.packet_builder).resolve()), "--review", str(Path(args.review).resolve()), "--output", str(packet)])
    packet_sha = sha256_path(packet)
    pobj = load(packet)
    proof = root / "receiver-readproof.json"
    run_json([sys.executable, str(Path(args.readproof).resolve()), "--packet", str(packet), "--expected-sha256", packet_sha, "--receiver-id", pobj["receiver_id"], "--output", str(proof)])
    proof_obj = load(proof)
    if proof_obj["packet_sha256"] != packet_sha:
        raise SystemExit("FAIL_CLOSED__READPROOF_SHA")
    if proof_obj["receiver_process_id"] == pterm["PROCESS_ID"]:
        raise SystemExit("FAIL_CLOSED__SAME_PROCESS_PICKUP")
    payload_path = Path(args.contribution_payload).resolve()
    payload = load(payload_path)
    if payload.get("relation_id") != pobj["relation_id"]:
        raise SystemExit("FAIL_CLOSED__PAYLOAD_RELATION_MISMATCH")
    if payload.get("semantic_status") != "CANDIDATE_NOT_ACCEPTED":
        raise SystemExit("FAIL_CLOSED__PAYLOAD_SEMANTIC_STATUS")
    contribution = root / "contribution-candidate.json"
    contribution_obj = {
        "schema": "CoContributionCandidate.R0C.v0.2-candidate",
        "state": "PROPOSED_CONTRIBUTION_CANDIDATE__NOT_ACCEPTED",
        "contribution_id": payload["contribution_id"],
        "receiver_id": pobj["receiver_id"],
        "packet_id": pobj["packet_id"],
        "relation_id": pobj["relation_id"],
        "payload_sha256": sha256_path(payload_path),
        "proposal": payload["proposal"],
        "semantic_acceptance": "UNPROVEN",
        "integration": False,
        "authority_change": False,
        "nonclaims": ["PROPOSED_NE_ACCEPTED", "CONTRIBUTION_NE_INTEGRATION", "ATTRIBUTION_NE_OWNERSHIP"],
    }
    contribution.write_text(json.dumps(contribution_obj, indent=2) + "\n", encoding="utf-8")
    lineage = root / "contribution-lineage.json"
    run_json([sys.executable, str(Path(args.lineage_binder).resolve()), "--packet", str(packet), "--readproof", str(proof), "--contribution", str(contribution), "--output", str(lineage)])
    lineage_obj = load(lineage)
    if lineage_obj["acceptance_relation"] is not None or lineage_obj["integration_relation"] is not None:
        raise SystemExit("FAIL_CLOSED__PREMATURE_ACCEPTANCE")
    pids = [pterm["PROCESS_ID"], proof_obj["receiver_process_id"], lineage_obj["process_id"]]
    if len(set(pids)) != 3:
        raise SystemExit("FAIL_CLOSED__PROCESS_SEPARATION")
    result = {
        "schema": "CoEncounterMatchPacketCanary.R0C.v0.2-candidate",
        "state": "PASS_R0C_EXACT_MATCH_PACKET__RECEIVER_READPROOF_PICKUP__DURABLE_SEMANTIC_PAYLOAD_BINDING__PROPOSED_LINEAGE__NO_AUTO_ASSIGNMENT",
        "coverage": {"match_packets": 1, "receiver_readproofs": 1, "bounded_pickups": 1, "proposed_contributions": 1, "lineage_objects": 1, "semantic_payload_fixtures": 1, "semantic_acceptances": 0, "integrations": 0},
        "hashes": {"source_review_sha256": pterm["SOURCE_REVIEW_SHA256"], "stable_route_digest_sha256": pterm["STABLE_ROUTE_DIGEST_SHA256"], "packet_sha256": packet_sha, "readproof_sha256": sha256_path(proof), "contribution_payload_sha256": sha256_path(payload_path), "contribution_sha256": sha256_path(contribution), "lineage_sha256": sha256_path(lineage)},
        "process_ids": pids,
        "checks": {"separate_packet_receiver_lineage_processes": True, "exact_packet_sha_read": True, "receiver_identity_bound": True, "pickup_proven_for_exact_packet": True, "durable_semantic_payload_bound": True, "auto_assignment": False, "execution_authorized": False, "semantic_acceptance_inferred": False, "integration_inferred": False},
        "effects": {"assignment": 0, "notification": 0, "authority_change": 0, "execution": 0, "provider_session_mutation": 0},
        "next": "R0D_SEMANTIC_CONTRIBUTION_DISPOSITION_OR_HETEROGENEOUS_RECEIVER_PACKET_CANARY__NO_AUTO_ASSIGNMENT",
        "nonclaims": ["PICKED_UP_NE_INTEGRATED", "READPROOF_NE_SEMANTIC_ACCEPTANCE", "LINEAGE_NE_ACCEPTANCE", "TWO_OR_MORE_PROCESSES_NE_TWO_OR_MORE_FAILURE_DOMAINS", "LOCAL_CANARY_NE_RUNTIME_INTEGRATION", "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE"],
    }
    result_path = root / "r0c-result.json"
    result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"STATE": result["state"], "OUTPUT": str(result_path), "OUTPUT_SHA256": sha256_path(result_path), "PACKET_SHA256": packet_sha, "PICKUPS": 1, "PIDS": pids, "NEXT": result["next"]}, separators=(",", ":")))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
