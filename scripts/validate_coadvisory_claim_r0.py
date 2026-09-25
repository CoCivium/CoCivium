#!/usr/bin/env python3
import json, sys
from pathlib import Path

def fail(msg):
    raise SystemExit("FAIL_CLOSED__" + msg)

p=Path(sys.argv[1]) if len(sys.argv)>1 else Path("examples/coadvisory-claim-v0.1.example.json")
d=json.loads(p.read_text(encoding="utf-8"))
required=["schema","claim_id","class","statement","source_refs","assumptions","counterarguments","uncertainty","falsifiers","time_horizon","financial_scope","account_action","nonclaims"]
for k in required:
    if k not in d: fail("MISSING_"+k.upper())
if d["schema"]!="CoAdvisory.Claim.v0.1-candidate": fail("SCHEMA")
if d["class"]=="OBSERVED" and not d["source_refs"]: fail("OBSERVED_NE_SOURCE")
if not d["falsifiers"]: fail("FALSIFIER_REQUIRED")
if d["financial_scope"] in {"ISSUER_SPECIFIC_ANALYSIS","SECURITIES_SPECIFIC","INVESTMENT_RECOMMENDATION"} and d["account_action"]!="EXPLICIT_HUMAN_REVIEW_REQUIRED":
    fail("FINANCIAL_SCOPE_REQUIRES_HUMAN_REVIEW")
if d["financial_scope"]=="INVESTMENT_RECOMMENDATION" and d["publication_scope"]=="PUBLIC_SAFE":
    fail("INVESTMENT_RECOMMENDATION_NE_PUBLIC_SAFE")
if d["class"]=="SCENARIO" and "SCENARIO_NE_FORECAST_CERTAINTY" not in d["nonclaims"]:
    fail("SCENARIO_NE_FORECAST_CERTAINTY_RAIL_REQUIRED")
print("PASS_COADVISORY_CLAIM_CONTRACT")
print("claim_id="+d["claim_id"])
print("class="+d["class"])
print("financial_scope="+d["financial_scope"])
print("account_action="+d["account_action"])
