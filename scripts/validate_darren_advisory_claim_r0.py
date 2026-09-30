#!/usr/bin/env python3
import json, sys
from pathlib import Path

p = Path(sys.argv[1])
d = json.loads(p.read_text(encoding="utf-8"))

required = [
    "claim_id","claim_text","epistemic_class","observed_at",
    "source_refs","information_class","challenge_status","currentness"
]
for k in required:
    if k not in d:
        raise SystemExit("FAIL_CLOSED__MISSING_"+k.upper())

allowed_epi={"OBSERVED","INFERRED","HYPOTHESIZED","SCENARIO","UNKNOWN"}
allowed_status={"UNTESTED","CHALLENGED","SUPPORTED","WEAKENED","REFUTED","SUPERSEDED","OPEN"}
if d["epistemic_class"] not in allowed_epi:
    raise SystemExit("FAIL_CLOSED__BAD_EPISTEMIC_CLASS")
if d["challenge_status"] not in allowed_status:
    raise SystemExit("FAIL_CLOSED__BAD_CHALLENGE_STATUS")
if not isinstance(d["source_refs"], list) or not d["source_refs"]:
    raise SystemExit("FAIL_CLOSED__NO_SOURCE_REFS")

public_classes={"PUBLIC_INFORMATION","RESEARCH","SCENARIO"}
private_classes={"CLIENT_CONFIDENTIAL","POTENTIAL_MATERIAL_NONPUBLIC_INFORMATION","UNKNOWN_INFORMATION_CLASS"}
if d["information_class"] in private_classes and d.get("public_projection", False):
    raise SystemExit("FAIL_CLOSED__PRIVATE_OR_UNKNOWN_CLASS_PUBLIC_PROJECTION")

if d.get("creates_order_or_transaction", False):
    if d.get("authorized_effect_gate") is not True:
        raise SystemExit("FAIL_CLOSED__ORDER_OR_TRANSACTION_WITHOUT_AUTHORIZED_GATE")

if d["epistemic_class"] == "HYPOTHESIZED" and d.get("rendered_as_observed", False):
    raise SystemExit("FAIL_CLOSED__HYPOTHESIS_RENDERED_AS_OBSERVED")

if d.get("reflexive_market_forecast", False) and not d.get("reflexivity_flag", False):
    raise SystemExit("FAIL_CLOSED__MISSING_REFLEXIVITY_FLAG")

print("PASS_BOUNDED_ADVISORY_CLAIM_CANARY")
print("claim_id="+d["claim_id"])
print("epistemic_class="+d["epistemic_class"])
print("information_class="+d["information_class"])
