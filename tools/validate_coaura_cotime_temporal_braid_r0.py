#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/cotime/coaura_cotime_temporal_braid_r0.json")

def fail(code):
    raise SystemExit(code)

def git_blob(path):
    return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"], text=True).strip()

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]
    binds = [
        ("coaura_fixture_path","coaura_fixture_blob_sha"),
        ("precommitment_fixture_path","precommitment_fixture_blob_sha"),
        ("probabilistic_skill_fixture_path","probabilistic_skill_fixture_blob_sha")
    ]
    for pkey, skey in binds:
        if git_blob(src[pkey]) != src[skey]:
            fail("FAIL_SOURCE_BIND:" + src[pkey])

    obs = d["observations"]
    hyps = d["hypotheses"]
    forecasts = d["forecast_lineage"]

    if len(obs) != d["expected"]["observation_count"]:
        fail("FAIL_OBSERVATION_COUNT")
    if len(forecasts) != d["expected"]["forecast_count"]:
        fail("FAIL_FORECAST_COUNT")

    if any(o["epistemic_class"] != "OBSERVED_EXPERIENCE" for o in obs):
        fail("FAIL_OBSERVATION_EPISTEMIC_CLASS")
    if any(o["mechanism_status"] != "UNKNOWN" for o in obs):
        fail("FAIL_OBSERVATION_MECHANISM_PROMOTION")

    resolved = [f for f in forecasts if f["outcome_observed_at"] is not None]
    unresolved = [f for f in forecasts if f["outcome_observed_at"] is None]
    if len(resolved) != d["expected"]["resolved_forecast_count"]:
        fail("FAIL_RESOLVED_FORECAST_COUNT")
    if len(unresolved) != d["expected"]["unresolved_forecast_count"]:
        fail("FAIL_UNRESOLVED_FORECAST_COUNT")

    for f in resolved:
        if not (f["registered_at"] < f["outcome_observed_at"]):
            fail("FAIL_POSTDICTION:" + f["id"])
        if f["disposition"] != "HIT":
            fail("FAIL_RESOLVED_DISPOSITION:" + f["id"])
    if len([f for f in resolved if f["disposition"] == "HIT"]) != d["expected"]["hit_count"]:
        fail("FAIL_HIT_COUNT")

    if any(h["mechanism_status"] == "PROVEN" for h in hyps):
        fail("FAIL_MECHANISM_PROVEN")
    if d["expected"]["mechanism_proven_count"] != 0:
        fail("FAIL_EXPECTED_MECHANISM_COUNT")

    braid = d["relation_braid"]
    required_relations = {
        "GENERATES_CANDIDATE_HYPOTHESIS",
        "CALIBRATED_BY",
        "SUPPORTS_CANDIDATE",
        "DOES_NOT_ELIMINATE"
    }
    if not required_relations.issubset({r["relation"] for r in braid}):
        fail("FAIL_BRAID_RELATION_COVERAGE")

    ib = d["coinbet_state"]
    if ib["resolved"] is not False or ib["binary_collapse_allowed"] is not False:
        fail("FAIL_COINBET_COLLAPSE")

    donor = d["metaphorical_donor"]
    if donor["mechanism_transfer_allowed"] is not False:
        fail("FAIL_METAPHOR_MECHANISM_TRANSFER")
    if donor["physical_equivalence_claimed"] is not False:
        fail("FAIL_METAPHOR_PHYSICAL_EQUIVALENCE")

    qc = d["question_compiler"]
    maxp = max(q["information_priority"] for q in qc["candidate_questions"])
    selected = sorted(q["id"] for q in qc["candidate_questions"] if q["information_priority"] == maxp)
    if selected != sorted(qc["expected_next_question_ids"]):
        fail("FAIL_QUESTION_SELECTION")
    if selected != sorted(d["expected"]["next_question_ids"]):
        fail("FAIL_EXPECTED_QUESTION_IDS")

    if d["expected"]["paranormal_promotions"] != 0:
        fail("FAIL_PARANORMAL_PROMOTION_EXPECTATION")
    if d["expected"]["neurological_promotions"] != 0:
        fail("FAIL_NEURO_PROMOTION_EXPECTATION")
    if d["expected"]["medical_diagnosis_promotions"] != 0:
        fail("FAIL_MEDICAL_PROMOTION_EXPECTATION")
    if d["expected"]["effect_authority_changes"] != 0:
        fail("FAIL_EFFECT_AUTHORITY_EXPECTATION")
    if d["expected"]["real_predictive_skill_claimed"] is not False:
        fail("FAIL_REAL_SKILL_CLAIM")

    required_rails = {
        "OBSERVATION_TRAJECTORY_NE_DIAGNOSIS",
        "FELT_ASYMMETRY_NE_HEMISPHERE_STATE_PROOF",
        "REPEATED_PATTERN_NE_CAUSAL_MECHANISM",
        "PREDICTIVE_HIT_NE_MECHANISM_PROOF",
        "TWO_HITS_NE_CALIBRATED_GENERAL_SKILL",
        "SURPRISING_RELATION_NE_PARANORMAL_CAUSATION",
        "METAPHORICAL_DONOR_NE_BIOLOGICAL_MODEL",
        "COINBET_STATE_NE_CAUSAL_CONCLUSION",
        "QUESTION_SELECTION_NE_EFFECT_AUTHORITY"
    }
    if not required_rails.issubset(set(d["rails"])):
        fail("FAIL_REQUIRED_RAILS")

    head = subprocess.check_output(["git","rev-parse","HEAD"], text=True).strip()
    out = {
        "STATE": "PASS_COAURA_COTIME_TEMPORAL_BRAID_R0",
        "checked_out_head_sha": head,
        "fixture_semantic_sha256": canonical_sha(d),
        "observation_count": len(obs),
        "forecast_count": len(forecasts),
        "resolved_forecast_count": len(resolved),
        "hit_count": len([f for f in resolved if f["disposition"] == "HIT"]),
        "unresolved_forecast_count": len(unresolved),
        "mechanism_proven_count": 0,
        "paranormal_promotions": 0,
        "neurological_promotions": 0,
        "medical_diagnosis_promotions": 0,
        "effect_authority_changes": 0,
        "real_predictive_skill_claimed": False,
        "next_question_ids": selected
    }
    print(json.dumps(out, separators=(",", ":")))

if __name__ == "__main__":
    main()
