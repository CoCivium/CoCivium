#!/usr/bin/env python3
import json, sys
from pathlib import Path

def fail(msg):
    raise SystemExit("FAIL_CLOSED__" + msg)

p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/cojurisdiction-deed-v0.1.example.json")
d = json.loads(p.read_text(encoding="utf-8"))

required = ["schema","deed_id","observed_at","deed_class","principals","participants","nodes","candidate_regimes","route_disposition","authority_ceiling","responsibility_graph","evidence_refs","nonclaims"]
for k in required:
    if k not in d:
        fail("MISSING_" + k.upper())

if d["schema"] != "CoJurisdictionWeave.DeedApplicability.v0.1-candidate":
    fail("SCHEMA_ID")

regs = d["candidate_regimes"]
if not isinstance(regs, list) or not regs:
    fail("NO_CANDIDATE_REGIMES")
for i, r in enumerate(regs):
    for k in ("regime_id","source_ref","valid_time","applicability_state","confidence"):
        if k not in r:
            fail(f"REGIME_{i}_MISSING_{k.upper()}")
    if not 0 <= float(r["confidence"]) <= 1:
        fail(f"REGIME_{i}_CONFIDENCE_RANGE")

disp = d["route_disposition"]
if disp.get("state") in {"ALLOW_BOUNDED","ALLOW_WITH_CONDITIONS"} and d.get("unresolved_conflicts"):
    fail("ALLOW_WITH_UNRESOLVED_CONFLICTS")
if any(r.get("applicability_state") in {"MAY_APPLY","CONFLICTING_EVIDENCE","UNKNOWN"} for r in regs):
    if disp.get("human_review_required") is not True:
        fail("UNCERTAINTY_REQUIRES_HUMAN_REVIEW")

rels = {x.get("relation") for x in d["responsibility_graph"] if isinstance(x, dict)}
if not ({"PROPOSED_BY","AUTHORIZED_BY"} & rels):
    fail("RESPONSIBILITY_GRAPH_TOO_THIN")

rails = set(d["nonclaims"])
for rail in ("NODE_LOCATION_NE_SOLE_JURISDICTION","DISTRIBUTION_NE_RESPONSIBILITY_ERASURE"):
    if rail not in rails:
        fail("MISSING_RAIL_" + rail)

print("PASS_BOUNDED_STATIC_JURISDICTION_DEED_CANARY")
print("deed_id=" + d["deed_id"])
print("candidate_regimes=" + str(len(regs)))
print("route_state=" + disp["state"])
print("human_review_required=" + str(disp.get("human_review_required")).lower())
