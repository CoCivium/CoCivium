#!/usr/bin/env python3
import json, sys
from pathlib import Path

def fail(x):
    raise SystemExit("FAIL_CLOSED__"+x)

p=Path(sys.argv[1])
d=json.loads(p.read_text(encoding="utf-8"))

req=["schema","object_id","epistemic_class","information_class","currentness","source_refs","observed_at","action_class","scope_class","regulatory_profile","route","authority_ceiling","nonclaims"]
for k in req:
    if k not in d: fail("MISSING_"+k.upper())
if d["schema"]!="CoTimeAdvisoryEvidence.v0.1-candidate": fail("SCHEMA")
if d["authority_ceiling"]!="ADVISORY_ONLY": fail("AUTHORITY")

effectful={"PORTFOLIO_REVIEW_TRIGGER","SECURITIES_TRANSACTION_RECOMMENDATION","TRADE_EXECUTION"}
sensitive={"POTENTIALLY_MATERIAL_NONPUBLIC_INFORMATION","UNKNOWN_INFORMATION_CLASS"}

if d["action_class"]=="TRADE_EXECUTION" and d["route"]["state"]!="DENY_R0_TRADE_EXECUTION":
    fail("TRADE_EXECUTION_NOT_DENIED")

if d["currentness"] in {"STALE","SUPERSEDED","UNKNOWN"} and d["action_class"] in effectful:
    if d["route"]["state"] not in {"HOLD_CURRENTNESS","DENY_R0_TRADE_EXECUTION"}:
        fail("NONCURRENT_EFFECTFUL_ROUTE")

if d["information_class"] in sensitive and d["action_class"] in effectful:
    if d["route"]["state"] not in {"HOLD_INFORMATION_CLASS","DENY_R0_TRADE_EXECUTION"}:
        fail("SENSITIVE_INFORMATION_EFFECTFUL_ROUTE")

if d["regulatory_profile"]=="UNKNOWN" and d["action_class"] in effectful:
    if d["route"]["state"] not in {"HOLD_REGULATORY_PROFILE","HOLD_INFORMATION_CLASS","HOLD_CURRENTNESS","DENY_R0_TRADE_EXECUTION"}:
        fail("UNKNOWN_REGULATORY_PROFILE_EFFECTFUL_ROUTE")

if d["scope_class"]=="SPECIFIC_CLIENT_OR_ACCOUNT" and d["action_class"] in effectful:
    if d.get("professional_review_required") is not True:
        fail("CLIENT_EFFECT_REQUIRES_PROFESSIONAL_REVIEW")

if d["epistemic_class"]=="PREDICTED":
    if d.get("calibration_due") in (None,""):
        fail("PREDICTION_NEEDS_CALIBRATION_DUE")
    if d.get("confidence") is None:
        fail("PREDICTION_NEEDS_CONFIDENCE")

rails=set(d["nonclaims"])
for x in ("PREDICTION_NE_EVIDENCE","ANALYSIS_NE_TRADE_AUTHORITY"):
    if x not in rails: fail("MISSING_RAIL_"+x)

print("PASS_BOUNDED_COTIME_ADVISORY_EVIDENCE_CANARY")
print("object_id="+d["object_id"])
print("route_state="+d["route"]["state"])
