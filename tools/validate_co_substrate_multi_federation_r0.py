#!/usr/bin/env python3
import json
from pathlib import Path

FIXTURE=Path("fixtures/substrate/co_substrate_multi_federation_r0.json")

def fail(msg):
    raise SystemExit(f"FAIL: {msg}")

def main():
    if not FIXTURE.exists():
        fail("fixture missing")
    data=json.loads(FIXTURE.read_text(encoding="utf-8"))
    cases=data.get("cases",[])
    if len(cases)!=5:
        fail("expected five federation cases")

    expected_ids={
        "F01_READ_ONLY_REPLICAS",
        "F02_CONCURRENT_DIVERGENCE",
        "F03_UNAUTHORIZED_WRITER",
        "F04_MERGE_DOES_NOT_ERASE_LINEAGE",
        "F05_FAILOVER_NOT_IDENTITY_TRANSFER",
    }
    if {c.get("id") for c in cases}!=expected_ids:
        fail("case set mismatch")

    for c in cases:
        instances={i["instance_id"]:i for i in c.get("instances",[])}
        if not instances:
            fail(f"{c['id']}: no instances")

        for w in c.get("writes",[]):
            inst=instances.get(w.get("instance_id"))
            if inst is None:
                fail(f"{c['id']}: write references unknown instance")
            if inst.get("authority")=="READ_ONLY":
                actual="REJECT_UNAUTHORIZED_WRITE"
                break
        else:
            if c["id"]=="F02_CONCURRENT_DIVERGENCE":
                deltas={w["delta_id"] for w in c.get("writes",[])}
                writers={w["instance_id"] for w in c.get("writes",[])}
                actual="DIVERGED_REQUIRES_RECONCILIATION" if len(deltas)>1 and len(writers)>1 else "COEXIST_OK"
            elif c["id"]=="F04_MERGE_DOES_NOT_ERASE_LINEAGE":
                r=c.get("reconciliation",{})
                parents=r.get("parents",[])
                if len(parents)<2 or r.get("preserves_parent_lineage") is not True:
                    fail(f"{c['id']}: merged state must preserve both parent lineages")
                actual="MERGE_ACCEPTABLE_WITH_PARENT_LINEAGE"
            elif c["id"]=="F05_FAILOVER_NOT_IDENTITY_TRANSFER":
                f=c.get("failover",{})
                if f.get("from") not in instances or f.get("to") not in instances:
                    fail(f"{c['id']}: failover endpoints invalid")
                if c["expected"].get("identity_transfer_claim_allowed") is not False:
                    fail(f"{c['id']}: identity transfer must remain unclaimed")
                actual="CONTINUATION_ELIGIBLE_FOR_SCOPE"
            else:
                actual="COEXIST_OK"

        if actual!=c["expected"]["status"]:
            fail(f"{c['id']}: status mismatch got={actual} expected={c['expected']['status']}")
        if c["expected"].get("single_current_instance_required") is not False:
            fail(f"{c['id']}: single-current-instance assumption forbidden")

    rails=set(data.get("rails",[]))
    required={
        "MULTI_INSTANCE_NE_MULTI_IDENTITY",
        "ONE_LINEAGE_NE_ONE_ACTIVE_INSTANCE",
        "CONCURRENT_WRITES_NE_AUTOMATIC_MERGE",
        "FAILOVER_NE_IDENTITY_TRANSFER",
        "MERGE_NE_HISTORY_ERASURE"
    }
    if not required.issubset(rails):
        fail("required federation rails missing")

    print("PASS: CoSubstrate multi-substrate federation R0 validated (5 cases)")

if __name__=="__main__":
    main()
