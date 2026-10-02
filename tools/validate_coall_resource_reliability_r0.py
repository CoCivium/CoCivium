#!/usr/bin/env python3
import json
from pathlib import Path

P=Path("fixtures/cocivia/coall_resource_reliability_r0.json")

def eligible(resources, task):
    return [
        r for r in resources
        if r["grant_state"]=="ACTIVE"
        and r["current"] is True
        and r["task_class"]==task
    ]

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    rs=d["resources"]
    cases={c["id"]:c for c in d["cases"]}

    compute=eligible(rs,"PUBLIC_CANARY_COMPUTE")
    ordered=sorted(compute,key=lambda r:r["reliability"],reverse=True)
    if ordered[0]["id"]!=cases["Q01_MATCHING_CURRENT_PREFERRED"]["expected_first"]:
        raise SystemExit("FAIL: matching current preference")
    ids={r["id"] for r in compute}
    for x in cases["Q02_REVOKED_EXCLUDED"]["must_exclude"]:
        if x in ids: raise SystemExit("FAIL: revoked resource remained eligible")
    for x in cases["Q03_SCOPE_DOES_NOT_TRANSFER"]["must_exclude"]:
        if x in ids: raise SystemExit("FAIL: cross-scope reliability transfer")
    for x in cases["Q04_STALE_DOES_NOT_DOMINATE"]["must_exclude"]:
        if x in ids: raise SystemExit("FAIL: stale resource remained eligible")
    if ids != set(cases["Q05_DIVERSITY_REMAINS"]["expected_eligible"]):
        raise SystemExit(f"FAIL: diversity set mismatch {ids}")
    if any(r["governance_weight"]!=cases["Q06_NO_GOVERNANCE_WEIGHT"]["expected_all_governance_weight"] for r in rs):
        raise SystemExit("FAIL: reliability changed governance weight")
    print("PASS: resource reliability remains scoped, current, revocable and non-governing")

if __name__=="__main__":
    main()
