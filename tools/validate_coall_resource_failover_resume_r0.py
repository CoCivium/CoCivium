#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

P=Path("fixtures/cocivia/coall_resource_failover_resume_r0.json")

def fail(msg):
    raise SystemExit("FAIL: "+msg)

def git_blob(path):
    return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"],text=True).strip()

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    src=d["source_bindings"]
    if git_blob(src["cosubstrate_field_path"])!=src["cosubstrate_field_blob_sha"]:
        fail("CoSubstrateField donor drift")

    source=d["source"]
    cp=d["checkpoint"]
    if source["state"]!="FAILED":
        fail("source must be failed in canary")
    if not cp["provenance_bound"] or not cp["receipt_valid"]:
        fail("checkpoint must be provenance-bound and receipted")
    if cp["task_id"]!=source["task_id"] or cp["source_lease_id"]!=source["lease_id"] or cp["source_fence"]!=source["fence"]:
        fail("checkpoint source binding mismatch")
    if cp["completed_units"]+cp["remaining_units"]!=source["total_units"]:
        fail("checkpoint work partition mismatch")

    observed={}
    for r in d["replacements"]:
        if r["grant_state"]!="ACTIVE":
            got="HOLD_NO_ACTIVE_GRANT"
        elif not r["compatible"]:
            got="HOLD_INCOMPATIBLE"
        elif r.get("adapter_required") and not r.get("adapter_bound",False):
            got="HOLD_ADAPTER_UNBOUND"
        elif r["authority"]!=source["authority"] or r["privacy_scope"]!=source["privacy_scope"]:
            got="HOLD_AUTHORITY_OR_PRIVACY_DRIFT"
        elif r.get("new_fence",0)<=source["fence"]:
            got="HOLD_FENCE_NOT_ADVANCED"
        elif not r.get("new_lease_id"):
            got="HOLD_NEW_LEASE_MISSING"
        else:
            got=f"RESUME_REMAINING_{cp['remaining_units']}"
        observed[r["id"]]=got
        if got!=r["expected"]:
            fail(f"{r['id']} got={got} expected={r['expected']}")

    for n in d["negative_cases"]:
        if n["id"]=="N01_STALE_SOURCE_RECONNECT":
            got="REJECT_STALE_FENCE" if n["presented_fence"]<n["current_fence"] else "ACCEPT"
        elif n["id"]=="N02_MISSING_CHECKPOINT_PROVENANCE":
            got="HOLD_UNTRUSTED_CHECKPOINT" if not n["checkpoint_provenance_bound"] else "ACCEPT"
        elif n["id"]=="N03_AUTHORITY_EXPANSION":
            got="HOLD_AUTHORITY_EXPANSION" if n["replacement_authority"]!=n["source_authority"] else "ACCEPT"
        else:
            fail("unknown negative case")
        if got!=n["expected"]:
            fail(f"{n['id']} got={got} expected={n['expected']}")

    e=d["expected"]
    if e["source_completed_units_preserved"]!=cp["completed_units"]:
        fail("completed history not preserved")
    if e["resumed_units"]!=cp["remaining_units"]:
        fail("resume range mismatch")
    if e["duplicate_remaining_execution"] is not False:
        fail("duplicate execution expectation drift")
    if e["authority_transferred"] is not False:
        fail("authority transfer expectation drift")
    if e["real_execution_count"]!=0:
        fail("real execution forbidden")

    print("PASS: resource failover resumes remaining work with new lease/fence and no authority inheritance")

if __name__=="__main__":
    main()
