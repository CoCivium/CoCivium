#!/usr/bin/env python3
import json, sys
from pathlib import Path

def fail(code):
    raise SystemExit("FAIL_CLOSED__" + code)

p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ai/examples/covirtual-sense-record-example-r0.json")
d = json.loads(p.read_text(encoding="utf-8"))

required = [
    "sense_id","receiver","subject","source_refs","source_class","capture_method",
    "observed_at","currentness","uncertainty","authority_ceiling","privacy_class",
    "provenance","epistemic_class"
]
for k in required:
    if k not in d:
        fail("MISSING_" + k.upper())

allowed = {
    "OBSERVED","MEASURED","DERIVED","INFERRED","ESTIMATED","PREDICTED",
    "COUNTERFACTUAL","SIMULATED","INTERPRETED","MYTHIC_OR_SYMBOLIC",
    "SPIRITUAL_OR_THEOLOGICAL_INTERPRETATION","UNKNOWN_OR_UNCLASSIFIED"
}
if d["epistemic_class"] not in allowed:
    fail("UNKNOWN_EPISTEMIC_CLASS")

if not isinstance(d["source_refs"], list) or not d["source_refs"]:
    fail("SOURCE_REFS_REQUIRED")

if d["epistemic_class"] == "PREDICTED":
    if "forecast_values" not in d or not d["forecast_values"]:
        fail("PREDICTION_REQUIRES_FORECAST_VALUES")
    if d.get("confidence") in (None, ""):
        fail("PREDICTION_REQUIRES_CONFIDENCE")

if d["epistemic_class"] in {"INFERRED","ESTIMATED","PREDICTED","COUNTERFACTUAL","SIMULATED"}:
    if d.get("uncertainty") in (None, "", {}):
        fail("MODELLED_CLASS_REQUIRES_UNCERTAINTY")

if d["epistemic_class"] in {"MYTHIC_OR_SYMBOLIC","SPIRITUAL_OR_THEOLOGICAL_INTERPRETATION"}:
    if d.get("measured_values"):
        fail("INTERPRETIVE_CLASS_CANNOT_CLAIM_MEASURED_VALUES_AS_SAME_CLASS")

if d["source_class"] == "SYNTHETIC_EXAMPLE" and d["currentness"] != "EXAMPLE_ONLY":
    fail("SYNTHETIC_EXAMPLE_CURRENTNESS_MUST_BE_EXAMPLE_ONLY")

effect_words = {"EXECUTE","ACTUATE","MUTATE","SEND","PUBLISH","PURCHASE","DELETE"}
authority = str(d["authority_ceiling"]).upper()
if any(x in authority for x in effect_words) and str(d["privacy_class"]).upper() == "UNKNOWN":
    fail("EFFECT_AUTHORITY_WITH_UNKNOWN_PRIVACY")

print("PASS_BOUNDED_COVIRTUAL_SENSE_RECORD")
print("sense_id=" + str(d["sense_id"]))
print("epistemic_class=" + str(d["epistemic_class"]))
print("privacy_class=" + str(d["privacy_class"]))
