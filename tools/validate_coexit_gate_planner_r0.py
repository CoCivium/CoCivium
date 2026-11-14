#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/resilience/coexit_gate_planner_r0.json")
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    sats=sum(1 for g in d["gates"] if g["satisfied"])
    unsats=sum(1 for g in d["gates"] if not g["satisfied"])
    if sats!=d["satisfied_gate_count"] or unsats!=d["unsatisfied_gate_count"]:
        raise SystemExit("FAIL: gate count drift")
    closable=[g for g in d["gates"] if not g["satisfied"] and g["github_only_closable"]]
    if len(closable)!=d["expected"]["github_only_unsatisfied_closable_count"]:
        raise SystemExit("FAIL: github-only closure drift")
    if closable:
        raise SystemExit("FAIL: unexpected actionable github-only gate")
    if d["expected"]["elected_next"]!="HOLD_FOR_INDEPENDENT_ROUTE_OR_ACCOUNT_CENSUS":
        raise SystemExit("FAIL: election drift")
    if d["expected"]["destructive_authority"] is not False:
        raise SystemExit("FAIL: destructive authority drift")
    if not d["wake_conditions"]:
        raise SystemExit("FAIL: wake conditions missing")
    print(json.dumps({
      "STATE":"PASS_EXIT_GATE_PLANNER_R0",
      "satisfied_gate_count":sats,
      "unsatisfied_gate_count":unsats,
      "github_only_unsatisfied_closable_count":0,
      "elected_next":d["expected"]["elected_next"],
      "destructive_authority":False
    },separators=(",",":")))
if __name__=="__main__": main()
