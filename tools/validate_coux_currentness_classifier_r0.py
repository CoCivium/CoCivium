#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/ux/coux_currentness_classifier_r0.json")
def classify(age,budget):
    if age is None:
        return "UNKNOWN"
    return "CURRENT" if age <= budget else "STALE"
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    b=float(d["freshness_budget_hours"])
    out=[]
    for s in d["sources"]:
        got=classify(s.get("age_hours"),b)
        if got!=s["expected_state"]:
            raise SystemExit("FAIL:"+s["id"]+":"+got)
        out.append({"id":s["id"],"state":got})
    if d["automatic_refresh_proven"] is not False:
        raise SystemExit("FAIL:auto-refresh overclaim")
    print(json.dumps({"STATE":"PASS_COUX_CURRENTNESS_CLASSIFIER_R0","results":out},separators=(",",":")))
if __name__=="__main__": main()
