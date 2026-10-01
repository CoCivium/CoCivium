#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/cotime/coinbet_cotime_optionality_r0.json")
def classify(x):
    return {
      "felt_right_left_asymmetry":["OBSERVED_EXPERIENCE","MECHANISM_UNPROVEN"],
      "surprising_relation_without_mechanism":["UNKNOWN_MECHANISM","NO_PARANORMAL_INFERENCE"],
      "likely_future_state":["PREDICTED","CALIBRATION_REQUIRED"],
      "forecast_triggers_reversible_preparation":["PREPARE_ALLOWED","EFFECT_AUTHORITY_UNCHANGED"],
      "cryptoasset_candidate_reserve":["OPTIONALITY_ONLY","NO_TRADE_AUTHORITY","SEPARATE_CUSTODY_RISK"],
      "transition_state":["PRESERVE_INTERMEDIATE_STATE","NO_BINARY_COLLAPSE"]
    }.get(x,["UNKNOWN"])
def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    if len(d["cases"])!=6: raise SystemExit("FAIL: expected six cases")
    for c in d["cases"]:
        got=classify(c["input"])
        if got!=c["expected"]: raise SystemExit(f"FAIL:{c['id']} got={got} expected={c['expected']}")
    required={"COINBET_PROJECTION_NE_NEW_ROOT_ONTOLOGY","EXPERIENCE_NE_MECHANISM","SPOOKY_NE_PARANORMAL","PREDICTION_NE_EVIDENCE","PREPARATION_NE_EXECUTION_AUTHORITY","TREASURY_OPTIONALITY_NE_TRADING_AUTHORITY"}
    if not required.issubset(set(d["rails"])): raise SystemExit("FAIL: required rails missing")
    print("PASS: CoInBet/CoTime optionality relation policy fixture (6 cases)")
if __name__=="__main__": main()
