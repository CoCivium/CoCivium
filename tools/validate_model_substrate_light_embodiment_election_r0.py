#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

FIXTURE = Path("fixtures/substrate/model_substrate_light_embodiment_election_r0.json")

AUTHORITY_RANK = {
    "NONE": 0,
    "READONLY_TEST": 1,
    "ADVISORY_ONLY": 2,
    "BOUNDED_LOCAL_WRITE": 3
}

CONF_RANK = {
    "PUBLIC": 0,
    "PRIVATE": 1
}

def fail(code):
    raise SystemExit(code)

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def rejection_reasons(route, req):
    reasons = []
    if not set(req["required_capabilities"]).issubset(set(route["capabilities"])):
        reasons.append("CAPABILITY_FIT")
    if AUTHORITY_RANK[route["authority_ceiling"]] < AUTHORITY_RANK[req["authority_ceiling"]]:
        reasons.append("AUTHORITY_FIT")
    if CONF_RANK[route["confidentiality_max"]] < CONF_RANK[req["confidentiality"]]:
        reasons.append("CONFIDENTIALITY_FIT")
    if not route["live"]:
        reasons.append("LIVENESS")
    if not route["current"]:
        reasons.append("CURRENTNESS")
    if req["exact_model_bind_required"] and not route["exact_model_bound"]:
        reasons.append("EXACT_MODEL_BIND_WHEN_REQUIRED")
    return reasons

def elect(scenario):
    req = scenario["requirements"]
    if not req["materialization_required"]:
        return {
            "state": "DORMANT_OPTION",
            "route_id": None,
            "rejected": {},
            "preserved_logical_lane_id": scenario["logical_lane_id"],
            "replayed_completed_step_ids": []
        }

    by_id = {r["route_id"]: r for r in scenario["routes"]}
    rejected = {}
    for rid in scenario["preference_order"]:
        route = by_id[rid]
        reasons = rejection_reasons(route, req)
        if reasons:
            rejected[rid] = reasons
            continue
        return {
            "state": "ELECTED",
            "route_id": rid,
            "rejected": rejected,
            "preserved_logical_lane_id": scenario["logical_lane_id"],
            "replayed_completed_step_ids": []
        }
    return {
        "state": "HOLD_NO_ADMISSIBLE_EMBODIMENT",
        "route_id": None,
        "rejected": rejected,
        "preserved_logical_lane_id": scenario["logical_lane_id"],
        "replayed_completed_step_ids": []
    }

def main():
    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    observed = []
    for scenario in doc["scenarios"]:
        got = elect(scenario)
        exp = scenario["expected"]
        if got["state"] != exp["state"]:
            fail("FAIL_STATE:" + scenario["id"])
        if got["route_id"] != exp["route_id"]:
            fail("FAIL_ROUTE:" + scenario["id"])
        for rid, expected_reasons in exp.get("rejected", {}).items():
            if got["rejected"].get(rid) != expected_reasons:
                fail("FAIL_REJECTION:" + scenario["id"] + ":" + rid)
        if exp.get("preserved_logical_lane_id") is not None:
            if got["preserved_logical_lane_id"] != exp["preserved_logical_lane_id"]:
                fail("FAIL_LANE_IDENTITY:" + scenario["id"])
        if exp.get("replayed_completed_step_ids") is not None:
            if got["replayed_completed_step_ids"] != exp["replayed_completed_step_ids"]:
                fail("FAIL_COMPLETED_WORK_REPLAY:" + scenario["id"])
        observed.append({
            "id": scenario["id"],
            "state": got["state"],
            "route_id": got["route_id"],
            "rejected": got["rejected"]
        })

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "STATE": "PASS_SUBSTRATE_LIGHT_EMBODIMENT_ELECTION_R0",
        "checked_out_head_sha": head,
        "scenario_count": len(observed),
        "observed": observed,
        "fixture_semantic_sha256": canonical_sha(doc),
        "rails": [
            "HARD_GATES_BEFORE_PREFERENCE",
            "PRIVACY_NE_TRADEABLE_FOR_CONVENIENCE",
            "AUTHORITY_NE_TRADEABLE_FOR_AVAILABILITY",
            "NO_ROUTE_NE_DEGRADE_REQUIREMENTS",
            "MATERIALIZATION_NOT_REQUIRED_NE_MATERIALIZE_ANYWAY",
            "ROUTE_CHANGE_NE_REPLAY_COMPLETED_WORK",
            "LOGICAL_LANE_NE_EXECUTION_ROUTE"
        ]
    }
    print(json.dumps(receipt, separators=(",", ":")))

if __name__ == "__main__":
    main()
