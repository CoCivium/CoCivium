#!/usr/bin/env python3
import copy, json
from pathlib import Path

P=Path("fixtures/cotime/cotime_calibration_set_integrity_r0.json")

def validate(fs, claim_full=False):
    ids={f["id"] for f in fs}
    required={"C01","C02","C03","C04","C05","C06","C07"}
    if ids!=required:
        return False
    for f in fs:
        if f.get("excluded") and not f.get("exclusion_reason"):
            return False
        if f["id"]=="C04" and f.get("disposition")!="CENSORED":
            return False
        if f["id"]=="C03" and f.get("disposition")!="UNRESOLVED":
            return False
        if f["id"]=="C02" and f.get("disposition")!="MISS":
            return False
    if claim_full:
        return False
    return True

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    fs=d["forecasts"]
    if not validate(fs):
        raise SystemExit("FAIL: baseline registry invalid")

    e=d["expected"]
    registered=len(fs)
    due=sum(1 for f in fs if f["due"])
    unresolved=sum(1 for f in fs if f.get("disposition")=="UNRESOLVED")
    censored=sum(1 for f in fs if f.get("disposition")=="CENSORED")
    not_due=sum(1 for f in fs if not f["due"])
    invalidated=sum(1 for f in fs if f.get("disposition")=="INVALIDATED_BY_ASSUMPTION_CHANGE")
    explained=sum(1 for f in fs if f.get("excluded") and f.get("exclusion_reason"))
    observed_due=sum(1 for f in fs if f["due"] and f.get("disposition") is not None)

    got={
      "registered_count":registered,
      "due_count":due,
      "observed_or_dispositioned_due_count":observed_due,
      "unresolved_count":unresolved,
      "censored_count":censored,
      "not_yet_due_count":not_due,
      "invalidated_count":invalidated,
      "explained_exclusion_count":explained
    }
    for k,v in got.items():
        if v!=e[k]:
            raise SystemExit(f"FAIL:{k} got={v} expected={e[k]}")
    if e["full_registry_performance_claim_allowed"] is not False:
        raise SystemExit("FAIL: full-registry performance claim drift")

    for n in d["negative_cases"]:
        x=copy.deepcopy(fs)
        claim_full=False
        if n["mutation"]=="drop_exclusion_reason":
            next(f for f in x if f["id"]=="C07").pop("exclusion_reason",None)
        elif n["mutation"]=="remove_C02":
            x=[f for f in x if f["id"]!="C02"]
        elif n["mutation"]=="remove_C03":
            x=[f for f in x if f["id"]!="C03"]
        elif n["mutation"]=="censored_to_hit":
            next(f for f in x if f["id"]=="C04")["disposition"]="HIT"
        elif n["mutation"]=="observed_subset_as_full_registry":
            claim_full=True
        else:
            raise SystemExit("FAIL: unknown negative mutation")
        got_valid=validate(x,claim_full)
        if got_valid is not n["expected_valid"]:
            raise SystemExit("FAIL:"+n["id"])

    print("PASS: CoTime calibration-set integrity and selection-bias guard")

if __name__=="__main__":
    main()
