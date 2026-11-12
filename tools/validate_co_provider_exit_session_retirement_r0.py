#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/substrate/co_provider_exit_session_retirement_r0.json")

def fail(code):
    raise SystemExit(code)

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def decide(c):
    if c["effect_obligations_pending"]:
        return "HOLD_PENDING_EFFECT_OBLIGATION"

    if c["object_class"] == "OPTIONAL_LOCAL_EMBODIMENT":
        if (
            c["unique_state_externalized"]
            and c["receiver_pickup_proven"]
            and c["reconstruction_canary_pass"]
            and c["independent_failure_domain_count"] >= 2
            and c["alternative_execution_route_count"] >= 1
        ):
            return "OPTIONAL_LOCAL_OFFLINE_ACCEPTABLE"

    if c["object_class"] == "LOCAL_CUSTODY_ROOT_CANDIDATE":
        if c["independent_failure_domain_count"] < 2:
            return "HOLD_SINGLE_FAILURE_DOMAIN"

    if c["object_class"] == "LOCAL_SERVICE":
        if c["independent_failure_domain_count"] < 2 or c["alternative_execution_route_count"] < 2:
            return "HOLD_SERVICE_REDUNDANCY_UNPROVEN"

    if not c["unique_state_externalized"] or not c["receiver_pickup_proven"]:
        return "HOLD_UNIQUE_STATE_OR_PICKUP_UNPROVEN"

    if not c["reconstruction_canary_pass"]:
        return "HOLD_RECONSTRUCTION_UNPROVEN"

    if c["object_class"] == "PROVIDER_ACCOUNT":
        if not c["private_state_coverage_complete"]:
            return "HOLD_ACCOUNT_CLOSURE_COVERAGE_UNPROVEN"
        if c["independent_failure_domain_count"] < 2:
            return "HOLD_SINGLE_FAILURE_DOMAIN"
        if c["alternative_execution_route_count"] < 2:
            return "HOLD_ALTERNATIVE_ROUTE_UNPROVEN"
        return "ACCOUNT_EXIT_ELIGIBLE_FOR_DECLARED_SCOPE"

    if c["object_class"] == "PROVIDER_SESSION":
        if c["durable_destination_count"] < 1:
            return "HOLD_NO_DURABLE_DESTINATION"
        if c["alternative_execution_route_count"] < 1:
            return "HOLD_ALTERNATIVE_ROUTE_UNPROVEN"
        return "RETIRE_SESSION_ELIGIBLE"

    return "HOLD_UNCLASSIFIED"

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    observed = []
    for c in d["scenarios"]:
        got = decide(c)
        if got != c["expected"]:
            fail(f"FAIL:{c['id']}:got={got}:expected={c['expected']}")
        observed.append({"id": c["id"], "decision": got})

    obs = d["current_project_observation"]
    if obs["all_chatgpt_session_unique_state_coverage_proven"] is not False:
        fail("FAIL_FALSE_GLOBAL_CHAT_COVERAGE")
    if obs["all_private_state_receiver_pickup_proven"] is not False:
        fail("FAIL_FALSE_PRIVATE_PICKUP")
    if obs["chatgpt_account_closure_safe_proven"] is not False:
        fail("FAIL_FALSE_ACCOUNT_CLOSE_SAFE")
    if obs["single_local_power_domain_is_not_sufficient_continuity_root"] is not True:
        fail("FAIL_LOCAL_FAILURE_DOMAIN_RULE")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({
        "STATE": "PASS_PROVIDER_EXIT_SESSION_RETIREMENT_GATE_R0",
        "checked_out_head_sha": head,
        "scenario_count": len(observed),
        "fixture_semantic_sha256": canonical_sha(d),
        "current_chatgpt_account_close_safe": False,
        "current_global_chat_drain_complete": False,
        "current_private_receiver_pickup_complete": False,
        "observed": observed,
        "rails": d["rails"]
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
