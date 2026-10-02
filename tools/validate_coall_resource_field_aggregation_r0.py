#!/usr/bin/env python3
import hashlib
import itertools
import json
import subprocess
from pathlib import Path

P = Path("fixtures/cocivia/coall_resource_field_aggregation_r0.json")

def fail(code):
    raise SystemExit(code)

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def active_explicit(g):
    return g["state"] == "ACTIVE" and bool(g.get("explicit_accept", False))

def eligible(g, task):
    return (
        active_explicit(g)
        and g["resource_class"] == task["resource_class"]
        and task["purpose"] in g["purposes"]
        and g["privacy_scope"] == task["privacy_scope"]
    )

def participant_view(grants, participants):
    p = set(participants)
    return [g for g in grants if g["participant_id"] in p]

def ids(gs):
    return sorted(g["grant_id"] for g in gs)

def capacity(gs):
    return sum(int(g["capacity_units"]) for g in gs)

def select_under_cap(candidates, cap):
    best = []
    best_key = (-1, -1, ())
    ordered = sorted(candidates, key=lambda g: g["grant_id"])
    for n in range(len(ordered) + 1):
        for combo in itertools.combinations(ordered, n):
            total = capacity(combo)
            if total > cap:
                continue
            diversity = len({g["failure_domain"] for g in combo})
            key = (total, diversity, tuple(g["grant_id"] for g in combo))
            if key > best_key:
                best_key = key
                best = list(combo)
    return best

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    grants = d["grants"]

    if len({g["grant_id"] for g in grants}) != len(grants):
        fail("FAIL_DUPLICATE_GRANT_ID")

    active = [g for g in grants if active_explicit(g)]
    if len(active) != d["expected"]["active_explicit_grant_count_all"]:
        fail("FAIL_ACTIVE_COUNT")

    excluded = [g for g in grants if not active_explicit(g)]
    if len(excluded) != d["expected"]["offered_or_revoked_excluded_count"]:
        fail("FAIL_EXCLUDED_COUNT")

    if any(g["governance_weight"] != 0 for g in grants):
        fail("FAIL_RESOURCE_CONTRIBUTION_CHANGED_GOVERNANCE_WEIGHT")

    baseline = participant_view(grants, d["snapshots"]["baseline_participants"])
    expanded = participant_view(grants, d["snapshots"]["expanded_participants"])
    tasks = {t["task_id"]: t for t in d["task_requests"]}

    compute = tasks["T-COMP-PUBLIC"]
    b_comp = [g for g in baseline if eligible(g, compute)]
    e_comp = [g for g in expanded if eligible(g, compute)]

    if capacity(b_comp) != compute["expected_baseline_eligible_capacity"]:
        fail("FAIL_BASELINE_COMPUTE_CAPACITY")
    if capacity(e_comp) != compute["expected_expanded_eligible_capacity"]:
        fail("FAIL_EXPANDED_COMPUTE_CAPACITY")
    if ids(e_comp) != sorted(compute["expected_expanded_eligible_grants"]):
        fail("FAIL_EXPANDED_COMPUTE_GRANTS")
    if not (capacity(e_comp) > capacity(b_comp)):
        fail("FAIL_RESOURCE_FIELD_DID_NOT_EXPAND")

    selected = select_under_cap(e_comp, compute["max_capacity_to_select"])
    if ids(selected) != sorted(compute["expected_selected_grants"]):
        fail("FAIL_COMPUTE_SELECTION")
    if capacity(selected) != compute["expected_selected_capacity"]:
        fail("FAIL_SELECTED_CAPACITY")
    if capacity(selected) > compute["max_capacity_to_select"]:
        fail("FAIL_TASK_SELECTION_CAP")
    if compute["execution_authorized"] is not False:
        fail("FAIL_COMPUTE_EXECUTION_AUTHORITY")

    storage = tasks["T-STORAGE-PUBLIC"]
    e_storage = [g for g in expanded if eligible(g, storage)]
    if ids(e_storage) != sorted(storage["expected_expanded_eligible_grants"]):
        fail("FAIL_STORAGE_GRANTS")
    if capacity(e_storage) != storage["expected_expanded_eligible_capacity"]:
        fail("FAIL_STORAGE_CAPACITY")

    local = tasks["T-LOCAL-PRIVATE"]
    all_local = [g for g in grants if eligible(g, local)]
    if ids(all_local) != sorted(local["expected_all_eligible_grants"]):
        fail("FAIL_LOCAL_MODEL_GRANTS")
    if capacity(all_local) != local["expected_all_eligible_capacity"]:
        fail("FAIL_LOCAL_MODEL_CAPACITY")

    forbidden_ids = {"G-E-COMP-REVOKED", "G-F-STOR-REFERRAL", "G-G-COMP-VISIBLE"}
    if any(g["grant_id"] in forbidden_ids for g in e_comp + e_storage + all_local):
        fail("FAIL_INELIGIBLE_GRANT_LEAKED_INTO_FIELD")

    bundle = d["recommended_default_bundle"]
    if bundle["preview_required"] is not True:
        fail("FAIL_DEFAULT_PREVIEW_REQUIRED")
    if bundle["grants_remain_individually_inspectable"] is not True:
        fail("FAIL_DEFAULT_GRANT_INSPECTABILITY")
    if bundle["grants_remain_individually_revocable"] is not True:
        fail("FAIL_DEFAULT_GRANT_REVOCABILITY")
    forbidden = {
        "BACKGROUND_COMPUTE", "PRIVATE_MESSAGES", "CREDENTIALS",
        "SENSORS", "FINANCIAL_EFFECTS", "AUTONOMOUS_EXTERNAL_POSTING"
    }
    if not forbidden.issubset(set(bundle["excludes"])):
        fail("FAIL_DEFAULT_EXCLUSION_SET")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "STATE": "PASS_COALL_RESOURCE_FIELD_AGGREGATION_R0",
        "checked_out_head_sha": head,
        "fixture_semantic_sha256": canonical_sha(d),
        "active_explicit_grant_count_all": len(active),
        "excluded_offered_or_revoked_count": len(excluded),
        "baseline_compute_eligible_capacity": capacity(b_comp),
        "expanded_compute_eligible_capacity": capacity(e_comp),
        "expanded_compute_eligible_grants": ids(e_comp),
        "selected_compute_grants_under_task_cap": ids(selected),
        "selected_compute_capacity_under_task_cap": capacity(selected),
        "compute_task_cap": compute["max_capacity_to_select"],
        "storage_eligible_capacity": capacity(e_storage),
        "private_local_model_eligible_capacity": capacity(all_local),
        "governance_weight_total": sum(g["governance_weight"] for g in grants),
        "real_resource_execution_count": 0,
        "resource_field_expanded": capacity(e_comp) > capacity(b_comp),
        "current_runtime_authority": False,
        "rails": d["rails"]
    }
    print(json.dumps(receipt, separators=(",", ":")))

if __name__ == "__main__":
    main()
