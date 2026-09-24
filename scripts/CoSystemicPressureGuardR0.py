#!/usr/bin/env python3
from __future__ import annotations
import argparse, json

ACTIONS={"NORMAL":["ALLOW_EXISTING_POLICY"],"CONTRACT":["SUPPRESS_BROAD_DISCOVERY","SUPPRESS_OPTIONAL_MATERIALIZATION","PREFER_DEDUPE","PREFER_FANIN","PREFER_COMPACTION","PREFER_RETIREMENT","PRESERVE_BOUND_WAKE_PREDICATES"],"INSUFFICIENT_EVIDENCE":["NO_AUTOMATIC_EXPANSION","REQUEST_BOUNDED_OBSERVATION"]}

def classify(o):
    required=("discovery_capacity","fanin_compaction_capacity","internal_work_created","internal_work_retired","receiver_benefit")
    if any(k not in o for k in required): return "INSUFFICIENT_EVIDENCE","MISSING_REQUIRED_SIGNAL"
    d=float(o["discovery_capacity"]); f=float(o["fanin_compaction_capacity"])
    created=float(o["internal_work_created"]); retired=float(o["internal_work_retired"]); benefit=float(o["receiver_benefit"])
    if f<=0:return "CONTRACT","FANIN_COMPACTION_CAPACITY_NONPOSITIVE"
    if created>retired:return "CONTRACT","INTERNAL_WORK_CREATED_GT_RETIRED"
    if d/f>float(o.get("discovery_fanin_ratio_threshold",1.0)) and benefit<=float(o.get("receiver_benefit_floor",0.0)):
        return "CONTRACT","DISCOVERY_FANIN_RATIO_HIGH_WITHOUT_RECEIVER_BENEFIT"
    return "NORMAL","NO_CONTRACTION_TRIGGER_PROVEN"

def compile_guard(o):
    disposition,basis=classify(o)
    return {"schema":"CoSystemicPressureGuard.R0.v0.1-candidate","state":"BOUNDED_SYSTEMIC_PRESSURE_DISPOSITION__NO_RUNTIME_ADOPTION","disposition":disposition,"basis":basis,"actions":ACTIONS[disposition],"effects":{"live_workers_started":0,"provider_mutations":0,"authority_changes":0},"nonclaims":["SYSTEMIC_HEALTH_NE_SUM_OF_LOCAL_PASSES","OBSERVABILITY_NE_CONTROL","DISPOSITION_NE_RUNTIME_ADOPTION","CONTRACTION_NE_DELETE"]}

def selftest():
    cases=[
      ({"discovery_capacity":2,"fanin_compaction_capacity":1,"internal_work_created":3,"internal_work_retired":2,"receiver_benefit":1},"CONTRACT"),
      ({"discovery_capacity":2,"fanin_compaction_capacity":1,"internal_work_created":1,"internal_work_retired":1,"receiver_benefit":0},"CONTRACT"),
      ({"discovery_capacity":1,"fanin_compaction_capacity":2,"internal_work_created":1,"internal_work_retired":2,"receiver_benefit":1},"NORMAL"),
      ({"discovery_capacity":1},"INSUFFICIENT_EVIDENCE")]
    for obs,want in cases:
        got=compile_guard(obs)["disposition"]; assert got==want,(got,want,obs)
    print("SELFTEST=PASS_CONTRACT_NORMAL_INSUFFICIENT__NO_EFFECTS"); return 0

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--selftest",action="store_true"); ap.add_argument("--input"); a=ap.parse_args()
    if a.selftest:return selftest()
    if not a.input:raise SystemExit("FAIL_CLOSED__INPUT_REQUIRED")
    with open(a.input,encoding="utf-8") as fh:o=json.load(fh)
    print(json.dumps(compile_guard(o),sort_keys=True,separators=(",",":"))); return 0
if __name__=="__main__":raise SystemExit(main())
