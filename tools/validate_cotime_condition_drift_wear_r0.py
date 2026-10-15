#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/cotime/cotime_condition_drift_wear_r0.json")

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    obs=d["observations"]
    if not all(x["functioning"] for x in obs):
        raise SystemExit("FAIL:functioning baseline")
    if not (obs[0]["condition"] > obs[1]["condition"] > obs[2]["condition"]):
        raise SystemExit("FAIL:condition trajectory")
    if d["comparison"][0]["age"] <= d["comparison"][1]["age"]:
        raise SystemExit("FAIL:age ordering fixture")
    if d["comparison"][0]["condition"] <= d["comparison"][1]["condition"]:
        raise SystemExit("FAIL:age must not determine condition")
    f=d["forecast"]
    if not f.get("horizon_end") or not f.get("assumptions"):
        raise SystemExit("FAIL:forecast calibration path")
    if f["replacement_authority"] is not False:
        raise SystemExit("FAIL:forecast authority drift")
    m=d["maintenance"]
    if m["after_condition"] <= m["before_condition"]:
        raise SystemExit("FAIL:maintenance improvement fixture")
    if m["role_identity_before"] != m["role_identity_after"]:
        raise SystemExit("FAIL:maintenance identity drift")
    s=d["successor"]
    if s["continuity_preserved"] is not True or s["identical_material_object"] is not False:
        raise SystemExit("FAIL:successor continuity fixture")
    vh=d["visible_hidden"]
    if vh["visible_wear"] is not True or vh["hidden_failure_proven"] is not False:
        raise SystemExit("FAIL:visible-hidden distinction")
    for n in d["negative_cases"]:
        if n["expected_valid"] is not False:
            raise SystemExit("FAIL:negative case drift")
    print("PASS: CoTime condition drift and wear trajectory policy fixture")

if __name__=="__main__": main()
