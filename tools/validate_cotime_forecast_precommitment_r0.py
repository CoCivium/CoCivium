#!/usr/bin/env python3
import json
from pathlib import Path

P=Path("fixtures/cotime/cotime_forecast_precommitment_r0.json")

def judge(f):
    if f["registered_at"] >= f["outcome_observed_at"]:
        return False,"POSTDICTION",None
    if "edited_claim_after_outcome" in f:
        return False,"FORECAST_MUTATED_AFTER_OUTCOME",None
    if "edited_confidence_after_outcome" in f:
        return False,"CONFIDENCE_MUTATED_AFTER_OUTCOME",None
    o=f.get("outcome")
    if o=="state_A": d="HIT"
    elif o=="not_state_A": d="MISS"
    else: d="UNRESOLVED"
    return True,None,d

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    if len(d["forecasts"])!=6:
        raise SystemExit("FAIL: expected six forecast cases")
    retained=[]
    for f in d["forecasts"]:
        valid,reason,disp=judge(f)
        if valid is not f["expected_valid"]:
            raise SystemExit("FAIL:"+f["id"]+":validity")
        if valid:
            retained.append((f["id"],disp))
            if disp!=f["expected_disposition"]:
                raise SystemExit("FAIL:"+f["id"]+":disposition")
        else:
            if reason!=f["expected_reason"]:
                raise SystemExit("FAIL:"+f["id"]+":reason")
    if ("P05_MISS_RETAINED","MISS") not in retained:
        raise SystemExit("FAIL: miss dropped")
    if ("P06_UNRESOLVED_RETAINED","UNRESOLVED") not in retained:
        raise SystemExit("FAIL: unresolved dropped")
    s=d["supersession"]
    if s["successor"]["id"]==s["prior"]["id"]:
        raise SystemExit("FAIL: successor overwrote prior ID")
    if s["successor"]["supersedes"]!=s["prior"]["id"]:
        raise SystemExit("FAIL: supersession link missing")
    if s["expected_history_preserved"] is not True:
        raise SystemExit("FAIL: history preservation drift")
    print("PASS: CoTime forecast precommitment and hindsight guard")

if __name__=="__main__":
    main()
