#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/condition/cowear_condition_rel_r0.json")

REQUIRED_RAILS = {
    "AGE_NE_WEAR",
    "USE_NE_DAMAGE",
    "WEAR_NE_FAILURE",
    "OLD_NE_OBSOLETE",
    "MAINTENANCE_NE_FOREVER",
    "MAINTENANCE_NE_RESTORE_ORIGINAL",
    "REPAIR_NE_HISTORY_ERASURE",
    "REPLACEMENT_NE_PROGRESS",
    "CONDITION_NE_VALUE",
    "VISIBLE_WEAR_NE_TOTAL_CONDITION",
    "SEMANTIC_OVERUSE_NE_FALSEHOOD",
    "PREDICTED_EOL_NE_CERTAINTY",
    "METAPHOR_NE_MECHANISM",
    "CONDITION_MODEL_NE_REALITY_TOTALITY",
    "VALIDATION_IS_NOT_ACCEPTANCE"
}

def fail(code):
    raise SystemExit(code)

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    if d["state"] != "CANDIDATE_CROSS_DOMAIN_CONDITION_TRAJECTORY__NO_CANON_NO_RUNTIME_NO_AUTHORITY_CHANGE":
        fail("FAIL_STATE")
    if len(d["scenarios"]) != 7:
        fail("FAIL_SCENARIO_COUNT")
    if not REQUIRED_RAILS.issubset(set(d["rails"])):
        fail("FAIL_REQUIRED_RAILS")

    by_id = {x["id"]: x for x in d["scenarios"]}

    w1 = by_id["W01_ACTIVE_SHOE_WEAR"]["observations"]
    if not (w1[1]["use_cycles"] > w1[0]["use_cycles"] and w1[1]["tread_mm"] < w1[0]["tread_mm"]):
        fail("FAIL_ACTIVE_SHOE_TRAJECTORY")

    w2 = by_id["W02_STORED_SHOE_AGING_WITHOUT_USE"]["observations"]
    if not (w2[1]["age_days"] > w2[0]["age_days"] and w2[1]["use_cycles"] == 0):
        fail("FAIL_AGE_WITHOUT_USE")
    if "USE_WEAR_NOT_OBSERVED" not in by_id["W02_STORED_SHOE_AGING_WITHOUT_USE"]["expected_relations"]:
        fail("FAIL_AGE_NE_WEAR_FIXTURE")

    w3 = by_id["W03_MAINTENANCE_DOES_NOT_REWIND_HISTORY"]
    if w3["after"]["tread_mm"] != w3["before"]["tread_mm"]:
        fail("FAIL_MAINTENANCE_FALSELY_RESTORED_TREAD")
    if not (w3["after"]["surface_cleanliness"] > w3["before"]["surface_cleanliness"]):
        fail("FAIL_MAINTENANCE_NO_DIMENSION_GAIN")

    w4 = by_id["W04_SOFTWARE_CAN_DEGRADE_WITHOUT_PHYSICAL_ABRASION"]["observations"]
    if not (w4[1]["local_code_changes"] == 0 and w4[1]["upstream_dependency_changes"] > 0 and w4[1]["compatibility_index"] < w4[0]["compatibility_index"]):
        fail("FAIL_DEPENDENCY_DRIFT")

    w5 = by_id["W05_METAPHOR_CAN_WEAR_SEMANTICALLY"]["observations"]
    if not (w5[1]["contexts_used"] > w5[0]["contexts_used"] and w5[1]["semantic_precision_index"] < w5[0]["semantic_precision_index"]):
        fail("FAIL_SEMANTIC_OVERUSE")

    w6 = by_id["W06_REPLACEMENT_NE_PROGRESS"]
    if w6["before"]["system_identity"] != w6["after"]["system_identity"]:
        fail("FAIL_FIXTURE_SYSTEM_IDENTITY")
    if w6["after"]["condition_index"] <= w6["before"]["condition_index"]:
        fail("FAIL_REPLACEMENT_CONDITION_DELTA")

    w7 = by_id["W07_PREDICTIVE_EOL_IS_A_WINDOW_NOT_CERTAINTY"]["candidate_prediction"]
    if not (w7["earliest_days"] < w7["latest_days"]):
        fail("FAIL_EOL_WINDOW")
    if w7["confidence"] == "CERTAIN":
        fail("FAIL_EOL_CERTAINTY")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    out = {
        "STATE": "PASS_COWEAR_CONDITION_REL_R0",
        "checked_out_head_sha": head,
        "scenario_count": len(d["scenarios"]),
        "physical_wear_scenarios": 3,
        "nonphysical_condition_scenarios": 2,
        "replacement_scenarios": 1,
        "prediction_scenarios": 1,
        "fixture_semantic_sha256": canonical_sha(d),
        "rails_checked": sorted(REQUIRED_RAILS),
        "runtime_authority": False,
        "canon_state": "UNPROVEN"
    }
    print(json.dumps(out, separators=(",", ":")))

if __name__ == "__main__":
    main()
