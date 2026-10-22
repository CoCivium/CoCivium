#!/usr/bin/env python3
import json, sys
from pathlib import Path

ALLOWED = {
    "OPERATIVE_RULE_OR_ORDER","FINAL_RULE_WITHDRAWAL","HISTORICAL_PROPOSAL",
    "ENFORCEMENT_ACTION","OFFICIAL_STAFF_REMARK","OFFICIAL_GUIDANCE",
    "CURRENTNESS_INDEX","SECONDARY_ANALYSIS","COALL_INFERENCE","SCENARIO"
}

def fail(msg):
    raise SystemExit("FAIL_CLOSED__" + msg)

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/research/sec-ai-regulatory-evidence-r0.json")
d = json.loads(path.read_text(encoding="utf-8"))

for key in ("schema","observed_at","domain","sources","rails","nonclaims"):
    if key not in d:
        fail("MISSING_" + key.upper())

if not isinstance(d["sources"], list) or not d["sources"]:
    fail("NO_SOURCES")

for i, s in enumerate(d["sources"]):
    for key in ("source_id","evidence_class","official_url","title","interpretation_state"):
        if not s.get(key):
            fail(f"SOURCE_{i}_MISSING_{key.upper()}")
    if s["evidence_class"] not in ALLOWED:
        fail(f"SOURCE_{i}_UNKNOWN_EVIDENCE_CLASS")
    if not s["official_url"].startswith("https://"):
        fail(f"SOURCE_{i}_NON_HTTPS")

rails = set(d["rails"])
for r in (
    "HISTORICAL_PROPOSAL_NE_OPERATIVE_RULE",
    "STAFF_REMARK_NE_COMMISSION_RULE",
    "ENFORCEMENT_CASE_NE_UNIVERSAL_REQUIREMENT",
    "CI_PASS_NE_LEGAL_CONCLUSION",
):
    if r not in rails:
        fail("MISSING_RAIL_" + r)

nonclaims = set(d["nonclaims"])
if "NOT_LEGAL_ADVICE" not in nonclaims:
    fail("MISSING_NOT_LEGAL_ADVICE")

print("PASS_BOUNDED_COLAW_RESEARCH_REGISTRY_CANARY")
print("source_count=" + str(len(d["sources"])))
print("classes=" + ",".join(sorted({s["evidence_class"] for s in d["sources"]})))
