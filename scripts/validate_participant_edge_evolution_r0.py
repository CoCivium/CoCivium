#!/usr/bin/env python3
import json, sys
from pathlib import Path

p=Path(sys.argv[1]) if len(sys.argv)>1 else Path("ai/participant-edge-evolution-lanes-r0.json")
d=json.loads(p.read_text(encoding="utf-8"))
req=["schema","authority_ceiling","physical_materialization","lanes","fanin"]
for k in req:
    if k not in d: raise SystemExit("FAIL_CLOSED__MISSING_"+k.upper())
lanes=d["lanes"]
if not isinstance(lanes,list) or len(lanes)<8:
    raise SystemExit("FAIL_CLOSED__INSUFFICIENT_LOGICAL_LANES")
ids=set(); domains=set()
for i,l in enumerate(lanes):
    for k in ["lane_id","receiver","effect_class","benefit_hypothesis","evidence_gate","pressure_budget","collision_domain","nonclaims"]:
        if k not in l: raise SystemExit(f"FAIL_CLOSED__LANE_{i}_MISSING_{k.upper()}")
    if l["lane_id"] in ids: raise SystemExit("FAIL_CLOSED__DUPLICATE_LANE_ID")
    if l["collision_domain"] in domains: raise SystemExit("FAIL_CLOSED__DUPLICATE_COLLISION_DOMAIN")
    ids.add(l["lane_id"]); domains.add(l["collision_domain"])
    b=l["pressure_budget"]
    if int(b.get("max_active_physical_workers",0))<1 or int(b.get("max_unexternalized_deeds",-1))<0:
        raise SystemExit("FAIL_CLOSED__INVALID_PRESSURE_BUDGET")
    nc=set(l["nonclaims"])
    for rail in ["LOGICAL_LANE_NE_WORKER","CI_PASS_NE_RUNTIME","BENEFIT_HYPOTHESIS_NE_BENEFIT_PROVEN"]:
        if rail not in nc: raise SystemExit("FAIL_CLOSED__MISSING_LANE_RAIL_"+rail)
print("PASS_BOUNDED_PARTICIPANT_EDGE_EVOLUTION_LANES")
print("lanes="+str(len(lanes)))
print("collision_domains="+str(len(domains)))
