#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/condition/cowear_relir_projection_r0.json")
SOURCE = Path("fixtures/condition/cowear_condition_rel_r0.json")

PRIMITIVES = {
    "ENTITY", "RELATION", "EVENT", "STATE", "TIME", "OBSERVER", "CONTEXT",
    "EVIDENCE", "PROVENANCE", "AUTHORITY", "UNCERTAINTY", "POSSIBILITY",
    "TRANSFORMATION", "PROJECTION"
}

REQUIRED_RULES = {
    "COTERM_NE_PRIMITIVE_BY_DEFAULT",
    "COWEAR_NE_NEW_PRIMITIVE",
    "CONDITION_TRAJECTORY_NE_OBJECT_IDENTITY",
    "FORECAST_NE_STATE",
    "POSSIBILITY_NE_FACT",
    "TRANSFORMATION_NE_IMPROVEMENT",
    "PROJECTION_NE_REALITY_TOTALITY",
    "METAPHOR_NE_MECHANISM"
}

def fail(code):
    raise SystemExit(code)

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    source = json.loads(SOURCE.read_text(encoding="utf-8"))

    if d["state"] != "SEMANTIC_COMPACTION_PROJECTION__NO_NEW_PRIMITIVES_NO_CANON_NO_RUNTIME":
        fail("FAIL_STATE")

    declared = set(d["semantic_nucleus"]["primitive_roots"])
    if declared != PRIMITIVES:
        fail("FAIL_PRIMITIVE_ROOT_SET")

    terms = d["term_classification"]
    if len({x["term"] for x in terms}) != len(terms):
        fail("FAIL_DUPLICATE_TERM")

    for term in terms:
        if term["new_primitive"] is not False:
            fail("FAIL_NEW_PRIMITIVE:" + term["term"])
        roots = set(term["primitive_roots_used"])
        if not roots:
            fail("FAIL_TERM_WITHOUT_ROOTS:" + term["term"])
        if not roots.issubset(PRIMITIVES):
            fail("FAIL_UNKNOWN_ROOT:" + term["term"])
        if term["role"] in PRIMITIVES:
            fail("FAIL_ROLE_COLLAPSED_TO_PRIMITIVE:" + term["term"])

    source_ids = {x["id"] for x in source["scenarios"]}
    projection_ids = {x["scenario_id"] for x in d["scenario_projection"]}
    if projection_ids != source_ids:
        fail("FAIL_SCENARIO_COVERAGE")

    by_id = {x["scenario_id"]: x for x in d["scenario_projection"]}
    if "POSSIBILITY" not in by_id["W02_STORED_SHOE_AGING_WITHOUT_USE"]["required_roots"]:
        fail("FAIL_CAUSE_CANDIDATE_NOT_POSSIBILITY")
    if "PROJECTION" not in by_id["W07_PREDICTIVE_EOL_IS_A_WINDOW_NOT_CERTAINTY"]["required_roots"]:
        fail("FAIL_FORECAST_NOT_PROJECTION")
    if "UNCERTAINTY" not in by_id["W07_PREDICTIVE_EOL_IS_A_WINDOW_NOT_CERTAINTY"]["required_roots"]:
        fail("FAIL_FORECAST_NO_UNCERTAINTY")
    if "FORECAST_IMPLIES_STATE" not in by_id["W07_PREDICTIVE_EOL_IS_A_WINDOW_NOT_CERTAINTY"]["forbidden_inferences"]:
        fail("FAIL_FORECAST_STATE_RAIL")
    if "TRANSFORMATION" not in by_id["W03_MAINTENANCE_DOES_NOT_REWIND_HISTORY"]["required_roots"]:
        fail("FAIL_MAINTENANCE_NOT_TRANSFORMATION")
    if "PROVENANCE" not in by_id["W06_REPLACEMENT_NE_PROGRESS"]["required_roots"]:
        fail("FAIL_REPLACEMENT_NO_PROVENANCE")

    rules = set(d["compaction_rules"])
    if not REQUIRED_RULES.issubset(rules):
        fail("FAIL_COMPACTION_RULES")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    out = {
        "STATE": "PASS_COWEAR_RELIR_COMPACTION_R0",
        "checked_out_head_sha": head,
        "term_count": len(terms),
        "scenario_projection_count": len(d["scenario_projection"]),
        "primitive_root_count": len(PRIMITIVES),
        "new_primitive_count": sum(1 for x in terms if x["new_primitive"]),
        "fixture_semantic_sha256": canonical_sha(d),
        "source_fixture_semantic_sha256": canonical_sha(source),
        "canon_state": "UNPROVEN",
        "runtime_authority": False
    }
    print(json.dumps(out, separators=(",", ":")))

if __name__ == "__main__":
    main()
