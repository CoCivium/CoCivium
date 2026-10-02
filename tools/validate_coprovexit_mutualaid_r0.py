#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/resilience/coprovexit_mutualaid_r0.json")

def fail(code):
    raise SystemExit(code)

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    pe = d["provider_exit"]

    required = {
        "UNIQUE_STATE_CENSUS",
        "INDEPENDENT_BOOTSTRAP",
        "PRIVATE_CUSTODY",
        "PUBLIC_BOOTSTRAP",
        "RECEIVER_PICKUP",
        "CREDENTIAL_INDEPENDENCE",
        "FAILURE_DOMAIN_DIVERSITY",
        "HUMAN_ACCESS_FALLBACK",
        "REVOCATION_MAP",
        "EXCEPTION_REGISTER",
    }
    if set(pe["required_gates"]) != required:
        fail("FAIL_PROVIDER_EXIT_GATE_SET")

    if pe["current_exit_authority"] is not False:
        fail("FAIL_CURRENT_EXIT_AUTHORITY")
    if pe["account_deletion_allowed"] is not False:
        fail("FAIL_ACCOUNT_DELETE_AUTHORITY")
    if pe["provider_tab_closure_allowed"] is not False:
        fail("FAIL_PROVIDER_TAB_CLOSE_AUTHORITY")
    if pe["no_ups_policy"] != "ASSUME_ABRUPT_POWER_LOSS":
        fail("FAIL_NO_UPS_POLICY")

    minimum = pe["minimum_critical_failure_domains"]
    if minimum < 2:
        fail("FAIL_MIN_FAILURE_DOMAINS")

    observed = []
    for case in d["failure_domain_cases"]:
        got = case["independent_domains"] >= minimum
        if got is not case["expected_resilient"]:
            fail("FAIL_FAILURE_DOMAIN_CASE:" + case["id"])
        observed.append({
            "id": case["id"],
            "independent_domains": case["independent_domains"],
            "resilient": got,
        })

    ma = d["mutual_aid"]
    if ma["simulation_only"] is not True:
        fail("FAIL_MUTUAL_AID_SIMULATION_ONLY")
    for key in [
        "real_emergency_command",
        "device_required",
        "central_server_required",
        "friendship_obligation",
        "human_worth_scoring",
        "real_service_supersession",
    ]:
        if ma[key] is not False:
            fail("FAIL_MUTUAL_AID_RAIL:" + key)

    required_rails = {
        "DRAINED_NE_DELETE_SAFE",
        "COPY_COUNT_NE_FAILURE_DOMAIN_COUNT",
        "NO_UPS_REQUIRES_CRASH_TOLERANCE",
        "ACCOUNT_RETIREMENT_REQUIRES_EXPLICIT_AUTHORITY",
        "SIMULATION_NE_REAL_EMERGENCY",
        "DEVICE_NE_PARTICIPATION_REQUIREMENT",
        "COOPERATION_NE_FRIENDSHIP_OBLIGATION",
        "CENTRAL_SERVER_NE_GAME_CONTINUITY_ROOT",
        "VALIDATION_IS_NOT_ACCEPTANCE",
    }
    if not required_rails.issubset(set(d["rails"])):
        fail("FAIL_REQUIRED_RAILS")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({
        "STATE": "PASS_COPROVIDER_EXIT_RESILIENCE_MUTUAL_AID_R0",
        "checked_out_head_sha": head,
        "fixture_semantic_sha256": canonical_sha(d),
        "failure_domain_case_count": len(observed),
        "minimum_critical_failure_domains": minimum,
        "current_exit_authority": False,
        "account_deletion_allowed": False,
        "provider_tab_closure_allowed": False,
        "mutual_aid_simulation_only": True,
        "real_emergency_command": False,
        "observed": observed,
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
