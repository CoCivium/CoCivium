#!/usr/bin/env python3
import json,sys
from pathlib import Path

def fail(msg):
    raise SystemExit("FAIL_CLOSED__"+msg)

p=Path(sys.argv[1]) if len(sys.argv)>1 else Path("examples/coresearch-evidence-v0.1.example.json")
d=json.loads(p.read_text(encoding="utf-8"))
required=["schema","record_id","observed_at","epistemic_class","claim","source_refs","tests","confidence","authority_ceiling","confidentiality","nonclaims"]
for k in required:
    if k not in d:
        fail("MISSING_"+k.upper())
if d["schema"]!="CoAll.ResearchEvidence.v0.1-candidate":
    fail("SCHEMA_ID")
if not 0 <= float(d["confidence"]) <= 1:
    fail("CONFIDENCE_RANGE")
if not d["source_refs"]:
    fail("NO_SOURCE_REFS")
if not d["nonclaims"]:
    fail("NO_NONCLAIMS")
if d["epistemic_class"] in {"HYPOTHESIS","PREDICTED","COUNTERFACTUAL"} and "HYPOTHESIS_NE_FACT" not in d["nonclaims"] and "PREDICTION_NE_FUTURE_FACT" not in d["nonclaims"]:
    fail("MISSING_EPISTEMIC_BOUNDARY")
if any(t.get("state")=="PASS" for t in d["tests"]) and "CI_PASS_NE_REAL_WORLD_PROOF" not in d["nonclaims"]:
    fail("MISSING_CI_NONCLAIM")
print("PASS_BOUNDED_RESEARCH_EVIDENCE_CONTRACT")
print("record_id="+d["record_id"])
print("epistemic_class="+d["epistemic_class"])
print("tests="+str(len(d["tests"])))
print("source_refs="+str(len(d["source_refs"])))
