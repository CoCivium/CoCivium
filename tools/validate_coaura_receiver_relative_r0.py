#!/usr/bin/env python3
import copy
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/cotime/coaura_receiver_relative_r0.json")

def fail(code):
    raise SystemExit(code)

def git_blob(path):
    return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"],text=True).strip()

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def valid_relation(r):
    required = {
        "id","object_ref","observer_ref","context_ref","event_time","observation_time",
        "modality","epistemic_class","quality","mechanism_status",
        "interpretations","alternatives","authority_before","authority_after"
    }
    if not required.issubset(r):
        return False
    if r["authority_before"] is not False or r["authority_after"] is not False:
        return False
    if r["epistemic_class"] == "OBSERVED_EXPERIENCE" and r["mechanism_status"] == "PROVEN_FROM_EXPERIENCE":
        return False
    if r["epistemic_class"] == "MECHANISM_PROVEN" and r["modality"] == "CONCEPTUAL_PROJECTION":
        return False
    if "PARANORMAL_PROVEN" in r.get("interpretations", []):
        return False
    return True

def valid_prediction(p):
    return (
        p.get("epistemic_class") == "PREDICTED"
        and bool(p.get("claim"))
        and bool(p.get("horizon_end"))
        and bool(p.get("assumptions"))
        and bool(p.get("discriminating_observation"))
        and bool(p.get("calibration_due"))
        and p.get("authority_before") is False
        and p.get("authority_after") is False
    )

def same_scope(a,b):
    keys = ["object_ref","observer_ref","context_ref","event_time","epistemic_class"]
    return all(a.get(k) == b.get(k) for k in keys)

def contradiction_candidate(a,b):
    return same_scope(a,b) and a.get("quality") != b.get("quality")

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]
    if git_blob(src["coinbet_doc_path"]) != src["coinbet_doc_blob_sha"]:
        fail("FAIL_COINBET_SOURCE_DRIFT")
    if git_blob(src["cotime_doc_path"]) != src["cotime_doc_blob_sha"]:
        fail("FAIL_COTIME_SOURCE_DRIFT")

    rels = d["relations"]
    if len(rels) != 6:
        fail("FAIL_RELATION_COUNT")
    if any(not valid_relation(r) for r in rels):
        fail("FAIL_VALID_RELATION")

    by_id = {r["id"]: r for r in rels}
    if contradiction_candidate(by_id["A01_OBSERVER_A"], by_id["A02_OBSERVER_B"]):
        fail("FAIL_DIFFERENT_OBSERVER_COLLAPSED_TO_CONTRADICTION")
    if contradiction_candidate(by_id["A01_OBSERVER_A"], by_id["A03_SAME_OBSERVER_LATER"]):
        fail("FAIL_DIFFERENT_TIME_CONTEXT_COLLAPSED_TO_CONTRADICTION")

    if by_id["A04_METAPHOR"]["epistemic_class"] != "METAPHORICAL_PROJECTION":
        fail("FAIL_METAPHOR_TYPE")
    if by_id["A05_SPOOKY_UNKNOWN"]["mechanism_status"] != "UNKNOWN":
        fail("FAIL_SPOOKY_MECHANISM_PROMOTION")
    forbidden = set(by_id["A05_SPOOKY_UNKNOWN"].get("forbidden_promotions", []))
    if not {"PARANORMAL_PROVEN","QUANTUM_CAUSATION_PROVEN","NONMATERIAL_CAUSATION_PROVEN"}.issubset(forbidden):
        fail("FAIL_FORBIDDEN_PROMOTIONS")
    if by_id["A06_INBET"].get("coinbet_state") != "UNRESOLVED_INTERMEDIATE":
        fail("FAIL_INBET_STATE")

    if not valid_prediction(d["prediction"]):
        fail("FAIL_VALID_PREDICTION")

    for n in d["negative_cases"]:
        rel_copy = copy.deepcopy(by_id["A01_OBSERVER_A"])
        metaphor = copy.deepcopy(by_id["A04_METAPHOR"])
        spooky = copy.deepcopy(by_id["A05_SPOOKY_UNKNOWN"])
        pred = copy.deepcopy(d["prediction"])
        if n["mutation"] == "set_mechanism_status_PROVEN_FROM_EXPERIENCE":
            rel_copy["mechanism_status"] = "PROVEN_FROM_EXPERIENCE"
            got = valid_relation(rel_copy)
        elif n["mutation"] == "set_metaphor_epistemic_class_MECHANISM_PROVEN":
            metaphor["epistemic_class"] = "MECHANISM_PROVEN"
            got = valid_relation(metaphor)
        elif n["mutation"] == "drop_calibration_due":
            pred.pop("calibration_due", None)
            got = valid_prediction(pred)
        elif n["mutation"] == "promote_unknown_to_PARANORMAL_PROVEN":
            spooky["interpretations"].append("PARANORMAL_PROVEN")
            got = valid_relation(spooky)
        elif n["mutation"] == "set_authority_after_true":
            rel_copy["authority_after"] = True
            got = valid_relation(rel_copy)
        else:
            fail("FAIL_UNKNOWN_NEGATIVE_MUTATION")
        if got is not n["expected_valid"]:
            fail("FAIL_NEGATIVE_CASE:" + n["id"])

    if len(d["question_compiler"]) != 8:
        fail("FAIL_QUESTION_COMPILER_COUNT")

    donor = d.get("specialization_donor", {})
    if donor.get("source_pattern") != "PARTIAL_LATERALIZATION_WITH_CROSS_COMMUNICATION":
        fail("FAIL_SPECIALIZATION_DONOR")
    required_abstraction = {
        "SPECIALIZED_SUBSYSTEMS",
        "DENSE_CROSS_COMMUNICATION",
        "PARTIAL_ASYMMETRY",
        "SHARED_SYSTEM_FUNCTION"
    }
    if not required_abstraction.issubset(set(donor.get("abstraction", []))):
        fail("FAIL_SPECIALIZATION_ABSTRACTION")
    forbidden = set(donor.get("forbidden_inferences", []))
    if not {
        "SUBSYSTEM_SEPARATION",
        "SUBSYSTEM_IDENTITY_FROM_FUNCTION",
        "SOVEREIGN_AUTHORITY_FROM_SPECIALIZATION",
        "PHYSICAL_EQUIVALENCE_FROM_METAPHOR"
    }.issubset(forbidden):
        fail("FAIL_SPECIALIZATION_FORBIDDEN_INFERENCE")
    for ex in donor.get("cross_domain_examples", []):
        if ex.get("specialization") is not True:
            fail("FAIL_SPECIALIZATION_EXAMPLE")
        if any(ex.get(k) is True for k in (
            "separation","sovereign_authority","identity_transfer","truth_monopoly","principal_identity"
        )):
            fail("FAIL_SPECIALIZATION_COLLAPSE")

    required_rails = {
        "COAURAREL_NE_PHYSICAL_AURA_CLAIM",
        "FELT_ASYMMETRY_NE_HEMISPHERE_STATE_PROOF",
        "EXPERIENCE_NE_MECHANISM",
        "METAPHOR_NE_MECHANISM",
        "UNKNOWN_MECHANISM_NE_NONMATERIAL_MECHANISM",
        "PREDICTION_NE_EVIDENCE",
        "RELATION_PROJECTION_NE_EFFECT_AUTHORITY",
        "SPECIALIZATION_NE_SEPARATION",
        "LATERALIZED_FUNCTION_NE_LATERALIZED_IDENTITY",
        "RELATIONAL_ISOMORPHISM_NE_CAUSAL_EQUIVALENCE",
        "METAPHORICAL_ISOMORPHISM_NE_PHYSICAL_EQUIVALENCE"
    }
    if not required_rails.issubset(set(d["rails"])):
        fail("FAIL_REQUIRED_RAILS")

    head = subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    out = {
        "STATE": "PASS_COAURAREL_RECEIVER_RELATIVE_R0",
        "checked_out_head_sha": head,
        "relation_count": len(rels),
        "negative_case_count": len(d["negative_cases"]),
        "question_count": len(d["question_compiler"]),
        "different_observer_is_contradiction": False,
        "different_context_time_is_contradiction": False,
        "prediction_calibration_path_present": True,
        "effect_authority_changes": 0,
        "fixture_semantic_sha256": canonical_sha(d)
    }
    print(json.dumps(out, separators=(",", ":")))

if __name__ == "__main__":
    main()
