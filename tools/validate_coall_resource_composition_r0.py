#!/usr/bin/env python3
import hashlib
import itertools
import json
import subprocess
from pathlib import Path

P = Path("fixtures/cocivia/coall_resource_composition_r0.json")

def fail(code):
    raise SystemExit(code)

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()

def active_explicit(g):
    return g["state"] == "ACTIVE" and bool(g.get("explicit_accept", False))

def candidate(g, req, privacy_scope):
    return (
        active_explicit(g)
        and g["resource_class"] == req["resource_class"]
        and req["purpose"] in g["purposes"]
        and g["privacy_scope"] == privacy_scope
    )

def select_for_requirement(grants, req, privacy_scope):
    eligible = sorted(
        [g for g in grants if candidate(g, req, privacy_scope)],
        key=lambda g: g["grant_id"]
    )
    need = int(req["required_capacity_units"])
    best = None
    best_key = None
    for n in range(1, len(eligible) + 1):
        for combo in itertools.combinations(eligible, n):
            total = sum(int(g["capacity_units"]) for g in combo)
            if total < need:
                continue
            excess = total - need
            diversity = len({g["failure_domain"] for g in combo})
            key = (len(combo), excess, -diversity, tuple(g["grant_id"] for g in combo))
            if best_key is None or key < best_key:
                best_key = key
                best = list(combo)
    return best or []

def compile_task(all_grants, participants, task):
    allowed = set(participants) if participants is not None else None
    grants = [
        g for g in all_grants
        if allowed is None or g["participant_id"] in allowed
    ]
    selected = []
    missing = []
    requirement_rows = []
    for req in task["requirements"]:
        picks = select_for_requirement(grants, req, task["privacy_scope"])
        total = sum(int(g["capacity_units"]) for g in picks)
        complete = total >= int(req["required_capacity_units"])
        if not complete:
            missing.append(req["resource_class"] + ":" + req["purpose"])
        selected.extend(picks)
        requirement_rows.append({
            "resource_class": req["resource_class"],
            "purpose": req["purpose"],
            "required_capacity_units": req["required_capacity_units"],
            "selected_grants": sorted(g["grant_id"] for g in picks),
            "selected_capacity_units": total,
            "complete": complete
        })
    dedup = {g["grant_id"]: g for g in selected}
    selected = [dedup[k] for k in sorted(dedup)]
    return {
        "complete": len(missing) == 0,
        "missing_requirements": sorted(missing),
        "selected_grants": sorted(g["grant_id"] for g in selected),
        "selected_participants": sorted({g["participant_id"] for g in selected}),
        "selected_failure_domains": sorted({g["failure_domain"] for g in selected}),
        "requirements": requirement_rows
    }

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]
    if git_blob(src["resource_field_fixture_path"]) != src["resource_field_fixture_blob_sha"]:
        fail("FAIL_RESOURCE_FIELD_SOURCE_DRIFT")

    source = json.loads(Path(src["resource_field_fixture_path"]).read_text(encoding="utf-8"))
    grants = source["grants"]

    tasks = {t["task_id"]: t for t in d["tasks"]}
    baseline = d["snapshots"]["baseline_participants"]
    expanded = d["snapshots"]["expanded_participants"]

    public_task = tasks["C01_PUBLIC_CORRESPONDENCE_PIPELINE"]
    base_result = compile_task(grants, baseline, public_task)
    expanded_result = compile_task(grants, expanded, public_task)
    if base_result["complete"] is not public_task["expected_baseline_complete"]:
        fail("FAIL_BASELINE_PIPELINE_STATE")
    if expanded_result["complete"] is not public_task["expected_expanded_complete"]:
        fail("FAIL_EXPANDED_PIPELINE_STATE")
    if expanded_result["selected_grants"] != sorted(public_task["expected_expanded_selected_grants"]):
        fail("FAIL_EXPANDED_PIPELINE_SELECTION")

    private_task = tasks["C02_PRIVATE_LOCAL_DRAFT_WITH_PRIVATE_REVIEW"]
    private_result = compile_task(grants, None, private_task)
    if private_result["complete"] is not private_task["expected_all_complete"]:
        fail("FAIL_PRIVATE_TASK_STATE")
    if private_result["missing_requirements"] != sorted(private_task["expected_missing_requirements"]):
        fail("FAIL_PRIVATE_TASK_MISSING")
    if any(gid in private_result["selected_grants"] for gid in ["G-A-ATTN", "G-D-ATTN"]):
        fail("FAIL_PUBLIC_ATTENTION_LEAKED_INTO_PRIVATE_TASK")

    mirror_task = tasks["C03_PUBLIC_MIRROR_200"]
    mirror_result = compile_task(grants, None, mirror_task)
    if mirror_result["complete"] is not mirror_task["expected_all_complete"]:
        fail("FAIL_MIRROR_TASK_STATE")
    if mirror_result["missing_requirements"] != sorted(mirror_task["expected_missing_requirements"]):
        fail("FAIL_MIRROR_TASK_MISSING")
    if any(gid in mirror_result["selected_grants"] for gid in mirror_task["must_not_use_grants"]):
        fail("FAIL_REFERRAL_OFFER_USED_AS_ACTIVE_GRANT")

    compute_task = tasks["C04_DISTRIBUTED_COMPUTE_800"]
    compute_result = compile_task(grants, None, compute_task)
    if compute_result["complete"] is not compute_task["expected_all_complete"]:
        fail("FAIL_DISTRIBUTED_COMPUTE_STATE")
    if compute_result["selected_grants"] != sorted(compute_task["expected_selected_grants"]):
        fail("FAIL_DISTRIBUTED_COMPUTE_SELECTION")
    if len(compute_result["selected_failure_domains"]) != compute_task["expected_distinct_failure_domains"]:
        fail("FAIL_DISTRIBUTED_FAILURE_DOMAIN_DIVERSITY")

    forbidden = {"G-E-COMP-REVOKED", "G-F-STOR-REFERRAL", "G-G-COMP-VISIBLE"}
    all_selected = set(
        base_result["selected_grants"]
        + expanded_result["selected_grants"]
        + private_result["selected_grants"]
        + mirror_result["selected_grants"]
        + compute_result["selected_grants"]
    )
    if all_selected & forbidden:
        fail("FAIL_INELIGIBLE_GRANT_SELECTED")

    if any(t["execution_authorized"] is not False for t in d["tasks"]):
        fail("FAIL_EXECUTION_AUTHORITY")
    if any(g["governance_weight"] != 0 for g in grants):
        fail("FAIL_GOVERNANCE_WEIGHT")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "STATE": "PASS_COALL_RESOURCE_COMPOSITION_R0",
        "checked_out_head_sha": head,
        "fixture_semantic_sha256": canonical_sha(d),
        "baseline_public_pipeline_complete": base_result["complete"],
        "expanded_public_pipeline_complete": expanded_result["complete"],
        "expanded_public_pipeline_selected_grants": expanded_result["selected_grants"],
        "expanded_public_pipeline_participant_count": len(expanded_result["selected_participants"]),
        "private_task_complete": private_result["complete"],
        "private_task_missing_requirements": private_result["missing_requirements"],
        "public_to_private_scope_leak_count": 0,
        "mirror_task_complete": mirror_result["complete"],
        "distributed_compute_complete": compute_result["complete"],
        "distributed_compute_selected_grants": compute_result["selected_grants"],
        "distributed_compute_failure_domain_count": len(compute_result["selected_failure_domains"]),
        "offered_or_revoked_grant_use_count": 0,
        "real_resource_execution_count": 0,
        "governance_authority_changed": False,
        "current_runtime_authority": False,
        "rails": d["rails"]
    }
    print(json.dumps(receipt, separators=(",", ":")))

if __name__ == "__main__":
    main()
