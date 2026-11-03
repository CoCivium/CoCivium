#!/usr/bin/env python3
import hashlib
import itertools
import json
import subprocess
from collections import defaultdict
from pathlib import Path

P = Path("fixtures/cocivia/coall_resource_activation_metabolism_r0.json")

def fail(code):
    raise SystemExit(code)

def git_blob(path):
    return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"],text=True).strip()

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj,sort_keys=True,separators=(",",":")).encode()
    ).hexdigest().upper()

def eligible(r):
    return r["state"]=="ACTIVE" and r["explicit_accept"] is True and r["current"] is True

def comparable(a,b):
    keys=[
        "substitutability_group","resource_class","purpose","privacy_scope",
        "owner","failure_domain"
    ]
    return all(a[k]==b[k] for k in keys)

def dominates(a,b):
    if not comparable(a,b) or a["id"]==b["id"]:
        return False
    weak=(
        a["capacity"]>=b["capacity"]
        and a["reliability_bp"]>=b["reliability_bp"]
        and a["cost_units"]<=b["cost_units"]
    )
    strict=(
        a["capacity"]>b["capacity"]
        or a["reliability_bp"]>b["reliability_bp"]
        or a["cost_units"]<b["cost_units"]
    )
    return weak and strict

def retained_frontier(compaction):
    before=[r for r in compaction["resources"] if eligible(r)]
    dominated=set()
    for b in before:
        if any(dominates(a,b) for a in before):
            dominated.add(b["id"])
    return [r for r in before if r["id"] not in dominated]

def matches(r, req):
    return (
        r["resource_class"]==req["resource_class"]
        and r["purpose"]==req["purpose"]
        and r["privacy_scope"]==req["privacy_scope"]
    )

def select(candidates, required, max_count):
    best=None
    ordered=sorted(candidates,key=lambda r:r["id"])
    for n in range(1,min(max_count,len(ordered))+1):
        for combo in itertools.combinations(ordered,n):
            cap=sum(r["capacity"] for r in combo)
            if cap<required:
                continue
            cost=sum(r["cost_units"] for r in combo)
            overshoot=cap-required
            key=(overshoot,n,cost,tuple(r["id"] for r in combo))
            if best is None or key<best[0]:
                best=(key,list(combo))
    return [] if best is None else best[1]

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    src=d["source_bindings"]
    if git_blob(src["compaction_fixture_path"])!=src["compaction_fixture_blob_sha"]:
        fail("FAIL_COMPACTION_SOURCE_DRIFT")
    if git_blob(src["pulsefield_doc_path"])!=src["pulsefield_doc_blob_sha"]:
        fail("FAIL_PULSEFIELD_SOURCE_DRIFT")

    compaction=json.loads(Path(src["compaction_fixture_path"]).read_text(encoding="utf-8"))
    frontier=retained_frontier(compaction)
    if len(frontier)!=d["expected"]["retained_frontier_count"]:
        fail("FAIL_FRONTIER_COUNT")

    policy=d["policy"]
    if policy["default_materialization_state"]!="DORMANT_ELIGIBLE":
        fail("FAIL_DORMANT_DEFAULT")
    if policy["demand_required_before_selection"] is not True:
        fail("FAIL_DEMAND_GATE")
    if policy["real_execution_authorized"] is not False:
        fail("FAIL_EXECUTION_AUTHORITY")

    observed=[]
    max_selected=0
    for s in d["scenarios"]:
        req=s.get("requirement")
        if req is None:
            chosen=[]
        else:
            candidates=[r for r in frontier if matches(r,req)]
            chosen=select(
                candidates,
                req["required_capacity"],
                policy["max_hot_resources_per_requirement"]
            )
            if sum(r["capacity"] for r in chosen)<req["required_capacity"]:
                fail("FAIL_UNMET_REQUIREMENT:"+s["id"])

        ids=sorted(r["id"] for r in chosen)
        cap=sum(r["capacity"] for r in chosen)
        dormant=len(frontier)-len(chosen)

        if ids!=sorted(s["expected_selected_ids"]):
            fail("FAIL_SELECTION:"+s["id"]+":"+json.dumps(ids))
        if cap!=s["expected_selected_capacity"]:
            fail("FAIL_SELECTED_CAPACITY:"+s["id"])
        if dormant!=s["expected_dormant_frontier_count"]:
            fail("FAIL_DORMANT_COUNT:"+s["id"])
        if len(chosen)>policy["max_hot_resources_per_requirement"]:
            fail("FAIL_HOT_WIDTH:"+s["id"])

        max_selected=max(max_selected,len(chosen))
        observed.append({
            "id":s["id"],
            "selected_ids":ids,
            "selected_capacity":cap,
            "dormant_frontier_count":dormant,
            "selected_state":policy["selected_state"]
        })

    if len(observed)!=d["expected"]["scenario_count"]:
        fail("FAIL_SCENARIO_COUNT")
    if max_selected!=d["expected"]["max_selected_resource_count_observed"]:
        fail("FAIL_MAX_SELECTED_COUNT")

    mention=[x for x in observed if x["id"]=="A05_MENTION_ONLY_NO_RESOURCE_DEMAND"][0]
    if mention["selected_ids"]:
        fail("FAIL_MENTION_WOKE_RESOURCE")

    head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    print(json.dumps({
        "STATE":"PASS_COALL_RESOURCE_ACTIVATION_METABOLISM_R0",
        "checked_out_head_sha":head,
        "fixture_semantic_sha256":canonical_sha(d),
        "retained_frontier_count":len(frontier),
        "scenario_count":len(observed),
        "max_selected_resource_count_observed":max_selected,
        "real_resource_wake_count":0,
        "real_resource_execution_count":0,
        "current_runtime_authority":False,
        "observed":observed,
        "rails":d["rails"]
    },separators=(",",":")))

if __name__=="__main__":
    main()
