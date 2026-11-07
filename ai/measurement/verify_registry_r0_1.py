#!/usr/bin/env python3
"""CoAll Measurement R0 private evaluator, stdlib only, no external effects."""
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

BASE = Path(__file__).parent
REG = BASE / "registry_r0_1.json"

def fraction(v):
    return Fraction(str(v))

def load():
    b=REG.read_bytes()
    return json.loads(b.decode("utf-8-sig")),hashlib.sha256(b).hexdigest()

def convert(value, src, dst, units):
    a,b=units[src],units[dst]
    if a["quantity_kind"] != b["quantity_kind"]:
        raise ValueError("HOLD_DIFFERENT_QUANTITY_KINDS")
    if a["dimensions"] != b["dimensions"]:
        raise ValueError("HOLD_DIMENSION_MISMATCH")
    absolute=fraction(value)*fraction(a["scale_to_anchor"])+fraction(a["offset_to_anchor"])
    return (absolute-fraction(b["offset_to_anchor"]))/fraction(b["scale_to_anchor"])

def validate_value(state, value):
    nonfinite={"MISSING","UNKNOWN","NOT_APPLICABLE","BELOW_DETECTION_LIMIT","REDACTED","INVALID","UNDEFINED","INFINITE_SYMBOLIC"}
    if state in nonfinite:
        if value is not None:
            raise ValueError("HOLD_NULL_MISREPRESENTED_AS_NUMBER")
    elif state == "OBSERVED_ZERO":
        if value is None or fraction(value)!=0:
            raise ValueError("HOLD_ZERO_INVALID")
    else:
        raise ValueError("HOLD_UNKNOWN_VALUE_STATE")

def check():
    reg,sha=load()
    units={u["id"]:u for u in reg["units"]}
    assert len(units)==len(reg["units"]),"duplicate unit ids"
    assert all(len(u["dimensions"])==7 for u in units.values())
    for m in reg["metric_families"]:
        assert m["unit_id"] in units,(m["id"],"UNBOUND_UNIT_ID",m["unit_id"])
        assert m["quantity_kind"]==units[m["unit_id"]]["quantity_kind"],(m["id"],"QUANTITY_KIND_MISMATCH")
    cases=[
        ("centimetre",convert("100","cm","m",units),Fraction(1)),
        ("millisecond",convert("1000","ms","s",units),Fraction(1)),
        ("kilometre",convert("2","km","m",units),Fraction(2000)),
        ("speed",convert("36","km_per_h","m_per_s",units),Fraction(10)),
        ("celsius_kelvin",convert("0","Cel","K",units),Fraction(27315,100)),
        ("kelvin_celsius",convert("273.15","K","Cel",units),Fraction(0)),
        ("percent",convert("50","percent","ratio",units),Fraction(1,2)),
        ("duration",convert("6","min","s",units),Fraction(360)),
        ("zero",convert("0","cm","m",units),Fraction(0))
    ]
    for label, actual,expected in cases:
        assert actual==expected,(label,actual,expected)
    blocked=0
    for src,dst in [("m","s"),("Hz","s"),("count","ratio"),("count","percent"),("J","W")]:
        try: convert(1,src,dst,units)
        except ValueError: blocked+=1
        else: raise AssertionError("conversion wrongfully allowed "+src+"/"+dst)
    assert blocked==5
    for state in ["MISSING","UNKNOWN","NOT_APPLICABLE","REDACTED","INVALID"]:
        validate_value(state,None)
    validate_value("OBSERVED_ZERO",0)
    for state,value in [("MISSING",0),("UNKNOWN",0),("OBSERVED_ZERO",1),("BOGUS",None)]:
        try:validate_value(state,value)
        except ValueError:blocked+=1
        else:raise AssertionError("invalid null state accepted")
    assert blocked==9
    result={"schema":"CoAll.MeasurementRegistryTestReceipt.R0",
      "registry_sha256":sha,
      "conversion_tests_passed":len(cases),
      "invalid_conversions_rejected":5,
      "null_states_passed":6,
      "null_misrepresentations_rejected":4,
      "total_asserted_cases":len(cases)+5+6+4,
      "state":"PASS_FOR_SCOPE","effects":{"network":0,"model_calls":0,"public_writes":0,"system_changes":0},
      "nonclaims":["NOT_SI_CERTIFIED","NOT_COPRIMATH_CANON","NOT_CROSS_SESSION_ADOPTED"]}
    output=BASE/"registry_test_receipt_r0.json"
    if output.exists():
        prior=json.loads(output.read_text(encoding="utf-8-sig"))
        assert prior==result, "HOLD_EXISTING_RECEIPT_CONFLICT"
    else:
        with output.open("x",encoding="utf-8") as f: json.dump(result,f,indent=2)
    print(json.dumps({"receipt":str(output),"receipt_sha256":hashlib.sha256(output.read_bytes()).hexdigest(),**result},sort_keys=True))

if __name__=="__main__":
    check()
