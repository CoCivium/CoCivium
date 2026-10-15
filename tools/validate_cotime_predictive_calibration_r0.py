#!/usr/bin/env python3
import copy, json, subprocess
from pathlib import Path

P=Path("fixtures/cotime/cotime_predictive_calibration_r0.json")

def git_blob(path):
    return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"],text=True).strip()

def valid_forecast(f):
    return (
        f.get("epistemic_class")=="PREDICTED"
        and bool(f.get("calibration_due"))
        and bool(f.get("discriminating_observation"))
        and bool(f.get("claim"))
    )

def calibrate(f):
    if f.get("assumption_changed"): return "INVALIDATED_BY_ASSUMPTION_CHANGE"
    o=f.get("outcome")
    if o is None or o=="mixed_or_insufficient": return "UNRESOLVED"
    if o=="state_A": return "HIT"
    if o=="not_state_A": return "MISS"
    return "UNRESOLVED"

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    src=d["source_bindings"]
    if git_blob(src["cotime_doc_path"])!=src["cotime_doc_blob_sha"]:
        raise SystemExit("FAIL:COTIME_SOURCE_DRIFT")

    for f in d["forecasts"]:
        if not valid_forecast(f): raise SystemExit("FAIL:INVALID_VALID_CASE:"+f["id"])
        got=calibrate(f)
        if got!=f["expected"]: raise SystemExit(f"FAIL:{f['id']} got={got} expected={f['expected']}")

    template=copy.deepcopy(d["forecasts"][0])
    for n in d["negative_cases"]:
        x=copy.deepcopy(template)
        x["epistemic_class"]=n["epistemic_class"]
        if n.get("missing"): x.pop(n["missing"],None)
        got=valid_forecast(x)
        if got is not n["expected_valid"]: raise SystemExit("FAIL:"+n["id"])

    p=d["preparation"]
    if p["effect_authority_before"] is not False or p["effect_authority_after"] is not False:
        raise SystemExit("FAIL:PREPARATION_AUTHORITY_DRIFT")

    print("PASS: CoTime predictive calibration policy fixture")

if __name__=="__main__": main()
