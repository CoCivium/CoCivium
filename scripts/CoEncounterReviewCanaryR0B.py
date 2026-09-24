#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def sha256_path(path: Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(path: Path)->dict[str,Any]:
    obj=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj,dict): raise ValueError(path)
    return obj


def run_json(cmd:list[str])->dict[str,Any]:
    cp=subprocess.run(cmd,check=True,capture_output=True,text=True)
    line=cp.stdout.strip().splitlines()[-1]
    obj=json.loads(line)
    if not isinstance(obj,dict): raise RuntimeError("terminal output not object")
    return obj


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--reviewer",required=True)
    ap.add_argument("--encounters",required=True)
    ap.add_argument("--receivers",required=True)
    ap.add_argument("--out-root",required=True)
    args=ap.parse_args()

    out_root=Path(args.out_root).resolve()
    if out_root.exists(): raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out_root}")
    out_root.mkdir(parents=True,exist_ok=False)

    reviewer=str(Path(args.reviewer).resolve())
    encounters=str(Path(args.encounters).resolve())
    receivers=str(Path(args.receivers).resolve())
    receiver_ids=[
        "receiver:ux-translator-current-low",
        "receiver:education-translator-current-high",
        "receiver:language-translator-stale-low",
    ]

    runs=[]
    for idx,rid in enumerate(receiver_ids):
        out=out_root/f"review-{idx+1}.json"
        terminal=run_json([
            sys.executable,reviewer,
            "--encounters",encounters,
            "--receivers",receivers,
            "--receiver-id",rid,
            "--output",str(out),
        ])
        runs.append({
            "receiver_id":rid,
            "path":out,
            "sha256":sha256_path(out),
            "artifact":load(out),
            "terminal":terminal,
        })

    source_hashes={r["artifact"]["source_bindings"]["encounter_fixture_sha256"] for r in runs}
    if len(source_hashes)!=1: raise SystemExit("FAIL_CLOSED__SOURCE_HASH_DIVERGENCE")
    pids=[r["artifact"]["receiver"]["process_id"] for r in runs]
    if len(set(pids))!=3: raise SystemExit("FAIL_CLOSED__PROCESS_IDS_NOT_DISTINCT")

    route_by_receiver={}
    for r in runs:
        routes=r["artifact"]["open_relation_routes"]
        if len(routes)!=1: raise SystemExit("FAIL_CLOSED__EXPECTED_ONE_OPEN_RELATION")
        route_by_receiver[r["receiver_id"]]=routes[0]

    a=route_by_receiver["receiver:ux-translator-current-low"]
    b=route_by_receiver["receiver:education-translator-current-high"]
    c=route_by_receiver["receiver:language-translator-stale-low"]

    if a["route_state"]!="MATCH_CANDIDATE": raise SystemExit("FAIL_CLOSED__LOW_COST_CURRENT_MATCH_NOT_ELECTED")
    if b["route_state"]!="HELD" or "cost_ok" not in b["held_reasons"]: raise SystemExit("FAIL_CLOSED__HIGH_COST_NOT_HELD")
    if c["route_state"]!="HELD" or "currentness_ok" not in c["held_reasons"]: raise SystemExit("FAIL_CLOSED__STALE_NOT_HELD")
    if any(x["assignment_executed"] or x["notification_executed"] or x["authority_change"] for x in (a,b,c)):
        raise SystemExit("FAIL_CLOSED__UNEXPECTED_EFFECT")
    if any(rv["semantic_acceptance"]!="NOT_PROVEN" for r in runs for rv in r["artifact"]["reviews"]):
        raise SystemExit("FAIL_CLOSED__SEMANTIC_ACCEPTANCE_INFERRED")

    result={
        "schema":"CoEncounterIndependentReviewCanary.R0B.v0.1-candidate",
        "state":"PASS_R0B_THREE_DISTINCT_RECEIVER_PROCESSES__INDEPENDENT_REVIEW__OPEN_RELATION_MATCH_CANDIDATE_ONLY__COST_AND_STALENESS_HELD__NO_AUTHORITY_INFLATION",
        "coverage":{
            "receiver_processes":3,
            "encounters_reviewed_per_receiver":3,
            "same_encounter_fixture_sha256":next(iter(source_hashes)),
            "open_relations":1,
        },
        "receivers":[
            {
                "receiver_id":r["receiver_id"],
                "process_id":r["artifact"]["receiver"]["process_id"],
                "review_artifact_sha256":r["sha256"],
                "route_state":r["artifact"]["open_relation_routes"][0]["route_state"],
                "held_reasons":r["artifact"]["open_relation_routes"][0]["held_reasons"],
            } for r in runs
        ],
        "checks":{
            "distinct_process_ids":True,
            "same_source_fixture":True,
            "independent_structural_review":True,
            "semantic_acceptance_not_inferred":True,
            "low_cost_current_capable_receiver_match_candidate":True,
            "high_cost_capable_receiver_held":True,
            "stale_capable_receiver_held":True,
            "assignment_executed":False,
            "notification_executed":False,
            "authority_change":False,
        },
        "effects":{
            "repo_mutations":0,
            "assignments":0,
            "notifications":0,
            "authority_changes":0,
            "provider_session_mutations":0
        },
        "next":"R0C_EXACT_MATCH_PACKET_PICKUP__CONTRIBUTION_LINEAGE_BINDING__NO_AUTO_ASSIGNMENT",
        "nonclaims":[
            "VALIDATION_IS_NOT_ACCEPTANCE",
            "INDEPENDENT_REVIEW_NE_TRUTH",
            "MATCH_NE_ASSIGNMENT_AUTHORITY",
            "ROUTE_CANDIDATE_NE_PICKUP",
            "TWO_OR_MORE_PROCESSES_NE_TWO_OR_MORE_FAILURE_DOMAINS",
            "LOCAL_CANARY_NE_RUNTIME_INTEGRATION",
            "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE"
        ]
    }
    result_path=out_root/"r0b-result.json"
    enc=(json.dumps(result,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
    result_path.write_bytes(enc)
    print(json.dumps({
        "STATE":result["state"],
        "OUTPUT":str(result_path),
        "OUTPUT_SHA256":hashlib.sha256(enc).hexdigest().upper(),
        "RECEIVER_PIDS":pids,
        "NEXT":result["next"]
    },separators=(",",":")))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
