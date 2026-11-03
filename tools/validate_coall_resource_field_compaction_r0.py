#!/usr/bin/env python3
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path

P = Path("fixtures/cocivia/coall_resource_field_compaction_r0.json")

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

def cell(r):
    return (r["resource_class"],r["purpose"],r["privacy_scope"])

def feasible(resources,task):
    for req in task["requirements"]:
        rs=[
            r for r in resources
            if cell(r)==(req["resource_class"],req["purpose"],req["privacy_scope"])
        ]
        if sum(r["capacity"] for r in rs)<req["required_capacity"]:
            return False
    return True

def cartesian_count(resources,signature):
    counts=[
        sum(1 for r in resources if cell(r)==tuple(sig))
        for sig in signature
    ]
    out=1
    for n in counts:
        out*=n
    return out,counts

def domain_sets(resources):
    d=defaultdict(set)
    for r in resources:
        d[cell(r)].add(r["failure_domain"])
    return {k:sorted(v) for k,v in d.items()}

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    src=d["source_bindings"]
    if git_blob(src["aggregation_fixture_path"])!=src["aggregation_fixture_blob_sha"]:
        fail("FAIL_AGGREGATION_SOURCE_DRIFT")
    if git_blob(src["composition_fixture_path"])!=src["composition_fixture_blob_sha"]:
        fail("FAIL_COMPOSITION_SOURCE_DRIFT")

    raw=d["resources"]
    if len(raw)!=d["expected"]["raw_resource_count"]:
        fail("FAIL_RAW_COUNT")
    if len({r["id"] for r in raw})!=len(raw):
        fail("FAIL_DUPLICATE_RESOURCE_ID")

    before=[r for r in raw if eligible(r)]
    if len(before)!=d["expected"]["eligible_resource_count"]:
        fail("FAIL_ELIGIBLE_COUNT")

    dominated=set()
    domination_edges=[]
    for b in before:
        ds=[a for a in before if dominates(a,b)]
        if ds:
            winner=sorted(ds,key=lambda r:r["id"])[0]
            dominated.add(b["id"])
            domination_edges.append({"dominated":b["id"],"retained_by":winner["id"]})

    if sorted(dominated)!=sorted(d["expected"]["dominated_resource_ids"]):
        fail("FAIL_DOMINATED_SET:"+json.dumps(sorted(dominated)))

    after=[r for r in before if r["id"] not in dominated]
    if len(after)!=d["expected"]["retained_resource_count"]:
        fail("FAIL_RETAINED_COUNT")

    if domain_sets(before)!=domain_sets(after):
        fail("FAIL_FAILURE_DOMAIN_COVERAGE_CHANGED")

    cb,cb_counts=cartesian_count(before,d["public_pipeline_signature"])
    ca,ca_counts=cartesian_count(after,d["public_pipeline_signature"])
    if cb!=d["expected"]["public_pipeline_cartesian_candidates_before"]:
        fail("FAIL_CARTESIAN_BEFORE:"+str(cb))
    if ca!=d["expected"]["public_pipeline_cartesian_candidates_after"]:
        fail("FAIL_CARTESIAN_AFTER:"+str(ca))
    if ca>=cb:
        fail("FAIL_NO_OPTION_SPACE_REDUCTION")

    observed=[]
    for task in d["tasks"]:
        fb=feasible(before,task)
        fa=feasible(after,task)
        if fb is not task["expected_before"]:
            fail("FAIL_TASK_BEFORE:"+task["id"])
        if fa is not task["expected_after"]:
            fail("FAIL_TASK_AFTER:"+task["id"])
        if fb!=fa:
            fail("FAIL_TASK_FEASIBILITY_CHANGED:"+task["id"])
        observed.append({"id":task["id"],"before":fb,"after":fa})

    retained={r["id"] for r in after}
    for required in ["C-X1","C-B1-NEW","C-D1-NEW","S-Y1","S-C1-NEW"]:
        if required not in retained:
            fail("FAIL_DIVERSITY_OR_FRONTIER_LOST:"+required)

    head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    print(json.dumps({
        "STATE":"PASS_COALL_RESOURCE_FIELD_COMPACTION_R0",
        "checked_out_head_sha":head,
        "fixture_semantic_sha256":canonical_sha(d),
        "raw_resource_count":len(raw),
        "eligible_resource_count":len(before),
        "retained_resource_count":len(after),
        "dominated_resource_ids":sorted(dominated),
        "domination_edges":domination_edges,
        "public_pipeline_candidate_counts_before":cb_counts,
        "public_pipeline_candidate_counts_after":ca_counts,
        "public_pipeline_cartesian_candidates_before":cb,
        "public_pipeline_cartesian_candidates_after":ca,
        "cartesian_reduction_ratio":{"numerator":cb-ca,"denominator":cb},
        "failure_domain_sets_preserved":True,
        "task_feasibility_preserved":True,
        "tasks":observed,
        "real_resource_execution_count":0,
        "current_runtime_authority":False,
        "rails":d["rails"]
    },separators=(",",":")))

if __name__=="__main__":
    main()
