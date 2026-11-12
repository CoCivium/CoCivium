#!/usr/bin/env python3
"""Cross-run CoSession source-delta gate. No model, network, OS or provider effects.

Inputs are two public-source logical-turn receipts plus metadata about a
GitHub Actions *successful prior run*, supplied by the EXISTING pulse.
If the prior cannot be qualified, HOLD. A matching prior becomes QUIESCENT,
not 'new useful work'. This is not independently operated CoStead recovery.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA = "CoAll.CoSessionAutocycle.SourceDeltaGuard.R1"
INPUT_SCHEMA = "CoAll.CoSessionAutocycle.SourceBoundTurn.R1"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
SHA1 = re.compile(r"[0-9a-f]{40}\Z")
RUN = re.compile(r"[1-9][0-9]*\Z")
NONCLAIMS = [
    "QUIET_CI_PULSE_NE_LIVE_CHAT_SESSION_QUIESCENCE",
    "PRIOR_ARTIFACT_NE_INDEPENDENT_EXTERNAL_RECEIVER",
    "NO_NEW_SOURCE_DELTA_NE_NO_NEW_PRIVATE_WORK",
    "PUBLIC_SOURCE_PROOF_NE_RUNTIME_WORK",
    "CI_SUCCESS_NE_X2_KEYBOARD_RECOVERY",
    "ONE_WORKID_REELECTION_NE_NEW_WORK_EFFECT",
    "LOCAL_IS_NOT_LANDED",
    "VALIDATION_IS_NOT_ACCEPTANCE",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
    "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
    "HASHING_IS_NOT_SEMANTIC_INGESTION",
    "DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY",
]


def _hold(reason, current=None):
    return {
        "schema": SCHEMA,
        "state": "HOLD_PRIOR_OR_SOURCE_UNQUALIFIED",
        "reason": reason,
        "current_run_id": (current or {}).get("run", {}).get("run_id") if isinstance(current,dict) else None,
        "source_delta_count": None,
        "next_source_workid": None,
        "new_machine_effect_authorized": False,
        "external_receiver_ack": False,
        "provider_sessions_cycled": 0,
        "nonclaims": NONCLAIMS,
    }


def _snapshot(receipt):
    if not isinstance(receipt, dict):
        raise ValueError("NOT_OBJECT")
    if receipt.get("schema") != INPUT_SCHEMA or receipt.get("state") != "ONE_SOURCE_WORKID_RECHECKED_AND_LOGICAL_FLEET_PROJECTED":
        raise ValueError("SOURCE_SCHEMA_OR_STATE")
    if receipt.get("receiver_ack") is not False or receipt.get("external_work_effect_claimed") is not False:
        raise ValueError("UNSUPPORTED_RUNTIME_EFFECT")
    run = receipt.get("run")
    if not isinstance(run,dict) or not isinstance(run.get("run_id"),str) or not RUN.fullmatch(run["run_id"]):
        raise ValueError("RUN_ID")
    if not isinstance(run.get("attempt"),str) or not RUN.fullmatch(run["attempt"]):
        raise ValueError("RUN_ATTEMPT")
    if not isinstance(run.get("head_sha"),str) or not SHA1.fullmatch(run["head_sha"]):
        raise ValueError("COMMIT_SHA")
    if run.get("executor") != "EXISTING_GITHUB_ACTIONS_HOURLY_PULSE":
        raise ValueError("EXECUTION_SCOPE")
    ins = receipt.get("input")
    if not isinstance(ins,dict) or not isinstance(ins.get("sha256"),str) or not SHA256.fullmatch(ins["sha256"]):
        raise ValueError("WORKSET_DIGEST")
    if ins.get("path") != "ai/session-autoturn-public-sources-r1.json":
        raise ValueError("WORKSET_PATH")
    sources=receipt.get("sources")
    if not isinstance(sources,list) or not 1<=len(sources)<=8:
        raise ValueError("SOURCE_COUNT")
    m={}
    for row in sources:
        if not isinstance(row,dict):
            raise ValueError("SOURCE_ROW")
        work=row.get("work_id")
        if not isinstance(work,str) or not work or len(work)>140 or work in m:
            raise ValueError("SOURCE_WORK_IDENTITY")
        if not isinstance(row.get("source_sha256"),str) or not SHA256.fullmatch(row["source_sha256"]):
            raise ValueError("SOURCE_DIGEST")
        if (not isinstance(row.get("source_path"),str) or not row["source_path"].startswith("ai/currentness/")
                or "\\" in row["source_path"] or ".." in Path(row["source_path"]).parts):
            raise ValueError("SOURCE_PATH")
        if row.get("native_effect_authorized") is not False or row.get("source_effect_verified") != "PUBLIC_SOURCE_READ_ONLY":
            raise ValueError("SOURCE_AUTHORITY")
        if type(row.get("priority")) is not int or row["priority"]<0 or row["priority"]>1000:
            raise ValueError("PRIORITY")
        m[work] = {
            "work_id":work, "sha256":row["source_sha256"],
            "source_path":row["source_path"], "priority":row["priority"],
            "owner":row.get("owner"), "role":row.get("role"),
            "projection":row.get("projection"),
            "next_safe_deed":row.get("next_safe_deed"),
        }
    if ins.get("work_item_count") != len(m):
        raise ValueError("COUNT_MISMATCH")
    gauges=receipt.get("co_speedo")
    if not isinstance(gauges,dict) or gauges.get("x2_processes_started")!=0 or gauges.get("provider_tabs_cycled")!=0:
        raise ValueError("FORBIDDEN_PROCESS_OR_PROVIDER_EFFECT")
    return ins["sha256"],m


def compare(current, previous, meta):
    try:
        current_set, current_map=_snapshot(current)
    except (ValueError,TypeError) as exc:
        return _hold("CURRENT_"+str(exc),current)
    if not isinstance(meta,dict) or meta.get("retrieval_state")!="VERIFIED_SUCCESSFUL_GITHUB_RUN_ARTIFACT":
        return _hold("NO_VERIFIED_PRIOR_GITHUB_RUN",current)
    try:
        prior_set, prior_map=_snapshot(previous)
    except (ValueError,TypeError) as exc:
        return _hold("PRIOR_"+str(exc),current)
    c=current["run"]; p=previous["run"]
    if (meta.get("repository")!="CoCivium/CoCivium"
        or meta.get("workflow_path")!=".github/workflows/cogoall-unattended-proof-pulse.yml"
        or meta.get("conclusion")!="success"
        or meta.get("run_id")!=p["run_id"] or meta.get("attempt")!=p["attempt"]
        or meta.get("head_sha")!=p["head_sha"]
        or meta.get("artifact_name")!="cogoall-proof-"+p["run_id"]+"-"+p["attempt"]
        or p["run_id"]==c["run_id"] or int(p["run_id"])>=int(c["run_id"])):
        return _hold("PRIOR_PROVENANCE_OR_ORDER",current)
    # Configuration edits are not themselves new source knowledge. Require a
    # rebase/review of identities and permissions before comparing work states.
    if current_set != prior_set or set(current_map) != set(prior_map):
        return {
            "schema":SCHEMA,
            "state":"HOLD_WORKSET_CONFIGURATION_DRIFT_REBASE_REQUIRED",
            "reason":"WORKSET_OR_WORKID_SET_CHANGED_NOT_NEW_KNOWLEDGE",
            "current_run_id":c["run_id"],
            "prior_run_id":p["run_id"],
            "current_workset_sha256":current_set,
            "prior_workset_sha256":prior_set,
            "source_delta_count":None,
            "next_source_workid":None,
            "novel_public_source_objects":None,
            "verified_useful_work_outcomes":0,
            "new_machine_effect_authorized":False,
            "external_receiver_ack":False,
            "provider_sessions_cycled":0,
            "nonclaims":NONCLAIMS,
        }
    # A stable workset binds owner, priority, role and policy. If those
    # fields change without a workset revision, HOLD instead of fabricating
    # a public-source delta or granting a new election.
    for work,row in current_map.items():
        other=prior_map[work]
        if ({k:v for k,v in row.items() if k!="sha256"} !=
            {k:v for k,v in other.items() if k!="sha256"}):
            return {
                "schema":SCHEMA,
                "state":"HOLD_SOURCE_METADATA_DRIFT_WITH_STATIC_WORKSET",
                "reason":"NON_SOURCE_METADATA_CHANGED_WITHOUT_WORKSET_REBASE",
                "current_run_id":c["run_id"],
                "prior_run_id":p["run_id"],
                "source_delta_count":None,
                "next_source_workid":None,
                "verified_useful_work_outcomes":0,
                "new_machine_effect_authorized":False,
                "external_receiver_ack":False,
                "provider_sessions_cycled":0,
                "nonclaims":NONCLAIMS,
            }
    changed=[
        row for work,row in current_map.items()
        if row["sha256"]!=prior_map[work]["sha256"]
    ]
    changed.sort(key=lambda x:(-x["priority"],x["work_id"]))
    removed=[]
    if changed:
        state="PUBLIC_SOURCE_BYTES_CHANGED_SEMANTIC_REVIEW_REQUIRED"
        elected=changed[0]["work_id"]
        reason="SOURCE_BYTES_DIFFER_BUT_NEW_MEANING_AND_VALUE_UNPROVEN"
    else:
        state="QUIESCENT_NO_MATERIAL_SOURCE_CHANGE"
        elected=None
        reason="SAME_PUBLIC_SOURCE_OBJECTS_AND_WORKSET_AS_LAST_QUALIFIED_RUN"
    return {
        "schema":SCHEMA,
        "state":state, "reason":reason,
        "current_run_id":c["run_id"],"prior_run_id":p["run_id"],
        "prior_same_provider":"GITHUB_ACTIONS",
        "current_workset_sha256":current_set,
        "prior_workset_sha256":prior_set,
        "current_work_count":len(current_map),
        "source_delta_count":len(changed),
        "changed_workids":[x["work_id"] for x in changed],
        "removed_workids":[],
        "next_source_workid":elected,
        "novel_public_source_objects":0 if not changed else None,
        "verified_useful_work_outcomes":0,
        "source_bytes_changed_not_semantically_reviewed":bool(changed),
        "unchanged_workids_suppressed":len(current_map)-len(changed),
        "co_speedo":{
            "bounded_work_contexts":len(current_map),
            "new_source_changes":len(changed)+len(removed),
            "no_change_quiescence":state=="QUIESCENT_NO_MATERIAL_SOURCE_CHANGE",
            "actual_chat_sessions_cycled":0,
            "actual_model_workers_started":0,
            "human_time_saved_seconds":None,
        },
        "co_needle":{
            "focus_source_workid":elected,
            "actual_oomph_or_productivity_gain":None,
            "interpretation":"SOURCE_DELTA_PROJECTION_ONLY",
        },
        "new_machine_effect_authorized":False,
        "external_receiver_ack":False,
        "provider_sessions_cycled":0,
        "nonclaims":NONCLAIMS,
    }


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--current",type=Path,required=True)
    p.add_argument("--prior",type=Path,required=True)
    p.add_argument("--metadata",type=Path,required=True)
    p.add_argument("--output",type=Path)
    p.add_argument("--check",type=Path)
    p.add_argument("--receipt",type=Path)
    args=p.parse_args(argv)
    if bool(args.output)==bool(args.check) or (args.check and not args.receipt):
        p.error("exactly one --output or --check plus --receipt required")
    try:
        current=json.loads(args.current.read_text("utf-8"))
        prior=json.loads(args.prior.read_text("utf-8")) if args.prior.is_file() else None
        meta=json.loads(args.metadata.read_text("utf-8")) if args.metadata.is_file() else None
        result=compare(current,prior,meta)
        if args.check:
            original=json.loads(args.check.read_text("utf-8"))
            if original != result:
                raise ValueError("HOLD_CROSS_JOB_RECOMPUTE_DIFFERENCE")
            result={
                "schema":"CoAll.CoSessionAutocycle.DeltaGuardJobReadback.R1",
                "state":"PASS_SAME_PROVIDER_DIFFERENT_JOB_RECOMPUTE",
                "current_run_id":result["current_run_id"],
                "decision_state":result["state"],
                "producer_receipt_sha256":hashlib.sha256(args.check.read_bytes()).hexdigest(),
                "external_receiver_ack":False,
                "nonclaims":NONCLAIMS,
            }
        target=args.receipt if args.check else args.output
        if target.exists():
            raise ValueError("HOLD_NO_CLOBBER")
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({"state":result["state"],"current_run_id":result["current_run_id"]},sort_keys=True))
        return 0
    except (OSError,ValueError,TypeError,json.JSONDecodeError) as exc:
        print(json.dumps({"state":"HOLD_DELTA_GUARD_EXECUTION","reason":str(exc)},sort_keys=True))
        return 2


if __name__=="__main__":
    sys.exit(main())
