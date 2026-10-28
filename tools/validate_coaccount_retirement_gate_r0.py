#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/resilience/coaccount_retirement_gate_r0.json")

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    gates=d["gates"]
    ids=[g["id"] for g in gates]
    if len(ids)!=len(set(ids)):
        raise SystemExit("FAIL: duplicate gate")
    if len(gates)!=13:
        raise SystemExit("FAIL: gate count")
    all_green=all(g["satisfied"] for g in gates)
    state="EXIT_READY_UNAUTHORIZED" if all_green else "HOLD_NOT_EXIT_READY"
    if state != d["expected"]["account_retirement_state"]:
        raise SystemExit("FAIL: retirement state")
    if d["expected"]["destructive_authority"] is not False:
        raise SystemExit("FAIL: destructive authority drift")
    if d["expected"]["account_deletion_allowed"] is not False:
        raise SystemExit("FAIL: account deletion enabled")
    if d["prior_cleanroom_proof"]["self_contained_orientation_proven"] is not True:
        raise SystemExit("FAIL: cleanroom proof missing")
    if sum(1 for g in gates if not g["satisfied"]) < 1:
        raise SystemExit("FAIL: expected hold disappeared")
    print(json.dumps({
      "STATE":state,
      "gate_count":len(gates),
      "satisfied_count":sum(1 for g in gates if g["satisfied"]),
      "unsatisfied_count":sum(1 for g in gates if not g["satisfied"]),
      "destructive_authority":False,
      "account_deletion_allowed":False
    }, separators=(",",":")))

if __name__=="__main__": main()
