#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/relations/cosneak_pass_pickup_source_bound_r0j.json")


def fail(code):
    raise SystemExit(code)


def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()


def valid_sha256(value):
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
        return True
    except ValueError:
        return False


def producer_pass(d):
    states = [d.get("state"), d.get("result_state")]
    result = d.get("result")
    if isinstance(result, dict):
        states.append(result.get("state"))
    return any(isinstance(x, str) and x.startswith("PASS") for x in states)


def classify(rule, d):
    if rule == "COENCOUNTER_R0C2_POSITIVE_REPLAY_READPROOFS":
        for key in ["positive_replay_a", "positive_replay_b"]:
            x = d.get(key) or {}
            if not valid_sha256(x.get("receiver_readproof_sha256")):
                fail("FAIL_R0C2_READPROOF:" + key)
            if x.get("bounded_pickups") != 1:
                fail("FAIL_R0C2_PICKUP_COUNT:" + key)
        checks = d.get("checks") or {}
        if checks.get("semantic_acceptance_inferred") is not False:
            fail("FAIL_R0C2_ACCEPTANCE_OVERCLAIM")
        if checks.get("integration_inferred") is not False:
            fail("FAIL_R0C2_INTEGRATION_OVERCLAIM")
        return "PICKUP_PROVEN_BOUNDED_SYNTHETIC", False, False

    if rule == "COPULSE_R0C_PACKET_PICKUP_AND_RECEIVER_READPROOFS":
        life = d.get("lifecycle_and_currentness") or {}
        if life.get("packet_pickup") != "PROVEN_FOR_BOUNDED_SYNTHETIC_RECEIVER_PACKETS":
            fail("FAIL_R0C_PACKET_PICKUP")
        receivers = ((d.get("result") or {}).get("receivers") or [])
        if len(receivers) != 2:
            fail("FAIL_R0C_RECEIVER_COUNT")
        if any(not valid_sha256(r.get("round2_readproof_sha256")) for r in receivers):
            fail("FAIL_R0C_RECEIVER_READPROOF")
        if life.get("integration") != "UNPROVEN" or life.get("coex") != "UNPROVEN":
            fail("FAIL_R0C_LIFECYCLE_OVERCLAIM")
        return "PICKUP_PROVEN_BOUNDED_SYNTHETIC", False, False

    if rule == "COPULSE_R0F_EXPLICIT_NO_PICKUP_INFERENCE":
        nonclaims = set(d.get("nonclaims") or [])
        if "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF" not in nonclaims:
            fail("FAIL_R0F_NONCLAIM_MISSING")
        if "LOCAL_IS_NOT_LANDED" not in nonclaims:
            fail("FAIL_R0F_LOCAL_BOUNDARY_MISSING")
        return "PASS_WITH_PICKUP_UNPROVEN_FOR_THIS_RESULT", False, False

    if rule == "COENCOUNTER_R0B_LIFECYCLE_PICKUP_UNPROVEN":
        life = d.get("lifecycle_evidence") or {}
        if life.get("receiver_pickup_of_match_packet") != "UNPROVEN":
            fail("FAIL_R0B_PICKUP_STATE")
        if life.get("integration") != "UNPROVEN" or life.get("coex") != "UNPROVEN":
            fail("FAIL_R0B_LIFECYCLE_OVERCLAIM")
        return "PASS_WITH_PICKUP_UNPROVEN", False, False

    if rule == "COENCOUNTER_YIELD_R0A_NO_READPROOF_NONCLAIM":
        nonclaims = set(d.get("nonclaims") or [])
        if "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF" not in nonclaims:
            fail("FAIL_YIELD_NONCLAIM_MISSING")
        return "PASS_WITH_PICKUP_UNPROVEN", False, False

    fail("FAIL_UNKNOWN_RULE:" + rule)


def main():
    cfg = json.loads(P.read_text(encoding="utf-8"))
    observed = []
    pickup_proven = 0
    pickup_unproven = 0
    semantic_acceptance = 0
    integration = 0

    for item in cfg["source_audit"]:
        actual_blob = git_blob(item["path"])
        if actual_blob != item["blob_sha"]:
            fail("FAIL_SOURCE_BLOB_DRIFT:" + item["id"] + ":" + actual_blob)
        d = json.loads(Path(item["path"]).read_text(encoding="utf-8"))
        if not producer_pass(d):
            fail("FAIL_NOT_PASS_SOURCE:" + item["id"])

        pickup_state, sem, integ = classify(item["rule"], d)
        if pickup_state != item["expected_pickup_state"]:
            fail("FAIL_CLASSIFICATION:" + item["id"] + ":" + pickup_state)

        pickup_proven += int(pickup_state.startswith("PICKUP_PROVEN"))
        pickup_unproven += int("PICKUP_UNPROVEN" in pickup_state)
        semantic_acceptance += int(sem)
        integration += int(integ)
        observed.append({
            "id": item["id"],
            "path": item["path"],
            "blob_sha": actual_blob,
            "pickup_state": pickup_state,
            "source_evidence_checked": True
        })

    exp = cfg["expected"]
    if len(observed) != exp["sample_size"]:
        fail("FAIL_SAMPLE_SIZE")
    if pickup_proven != exp["pickup_proven"]:
        fail("FAIL_PICKUP_PROVEN_COUNT")
    if pickup_unproven != exp["pickup_unproven"]:
        fail("FAIL_PICKUP_UNPROVEN_COUNT")
    if semantic_acceptance != exp["semantic_acceptance_proven"]:
        fail("FAIL_SEMANTIC_ACCEPTANCE_COUNT")
    if integration != exp["integration_proven"]:
        fail("FAIL_INTEGRATION_COUNT")
    if exp["sampled_scope_closed"] is not True or exp["global_census_complete"] is not False:
        fail("FAIL_SCOPE_BOUNDARY")
    if exp["runtime_effect"] or exp["public_effect"]:
        fail("FAIL_EFFECT_BOUNDARY")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    fixture_sha = hashlib.sha256(
        json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()
    print(json.dumps({
        "STATE": "PASS_COSNEAK_SOURCE_BOUND_PASS_PICKUP_AUDIT_R0J",
        "checked_out_head_sha": head,
        "fixture_semantic_sha256": fixture_sha,
        "sample_size": len(observed),
        "pickup_proven": pickup_proven,
        "pickup_unproven": pickup_unproven,
        "semantic_acceptance_proven": semantic_acceptance,
        "integration_proven": integration,
        "sampled_scope_disposition": "CLOSED_CLASSIFIED",
        "global_census_complete": False,
        "runtime_effect": False,
        "public_effect": False,
        "observed": observed,
        "rails": cfg["rails"]
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
