#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/architecture/cofield_self_regulation_r0h.json")

def fail(code):
    raise SystemExit(code)

def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def retirement_ready(o):
    return all([
        o["exact_donor_manifest"],
        o["receiver_pickup"],
        o["lineage_preserved"],
        o["negative_knowledge_preserved"],
        o["wake_conditions_preserved"],
        not o["unique_proof_lane"],
    ])

def classify(o):
    if o["revoked"]:
        return "QUIESCENT_RETAIN_PROVENANCE"
    if o["currentness"] == "STALE":
        return "ACTION_REFRESH_CURRENTNESS"
    if o["proof"] != "PROVEN":
        return "WATCH_UNPROVEN"
    if o["effect_candidate"]:
        return "ACTION_EFFECT_GATE_NO_EXECUTION"
    if o["unique_proof_lane"]:
        return "KEEP_ACTIVE_UNIQUE_PROOF_LANE"
    if o["kind"] == "CONCEPTUAL_BRANCH" and o["overlap"] == "HIGH":
        if retirement_ready(o):
            return "PREVIEW_RETIREMENT_ELIGIBLE"
        if o["exact_donor_manifest"] and not o["receiver_pickup"]:
            return "HOLD_RECEIVER_PICKUP_REQUIRED"
        return "COMPACT_DONOR_MANIFEST_REQUIRED"
    if o["kind"] == "SURFACE" and o["overlap"] == "HIGH" and o["attention_need"] == "NONE":
        return "QUIET_HIDE_DUPLICATE_PROJECTION"
    return "QUIET_KEEP_IN_FIELD"

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]
    checks = [
        ("field_mesh_doc_path", "field_mesh_doc_blob_sha"),
        ("field_mesh_fixture_path", "field_mesh_fixture_blob_sha"),
        ("branch_disposition_doc_path", "branch_disposition_doc_blob_sha"),
    ]
    for path_key, sha_key in checks:
        if git_blob(src[path_key]) != src[sha_key]:
            fail("FAIL_SOURCE_BIND:" + src[path_key])

    observed = []
    for o in d["objects"]:
        got = classify(o)
        if got != o["expected_disposition"]:
            fail(f"FAIL_DISPOSITION:{o['id']}:got={got}:expected={o['expected_disposition']}")
        observed.append({"id": o["id"], "disposition": got})

    action_priority = {
        "ACTION_EFFECT_GATE_NO_EXECUTION": 0,
        "ACTION_REFRESH_CURRENTNESS": 1,
        "HOLD_RECEIVER_PICKUP_REQUIRED": 2,
        "KEEP_ACTIVE_UNIQUE_PROOF_LANE": 3,
        "WATCH_UNPROVEN": 4,
        "PREVIEW_RETIREMENT_ELIGIBLE": 5,
        "QUIESCENT_RETAIN_PROVENANCE": 6,
        "QUIET_HIDE_DUPLICATE_PROJECTION": 7,
        "QUIET_KEEP_IN_FIELD": 8,
    }
    primary_candidates = sorted(
        observed,
        key=lambda x: (action_priority[x["disposition"]], x["id"])
    )
    budget = d["policy"]["primary_attention_budget"]
    primary = [x["id"] for x in primary_candidates[:budget]]

    exp = d["expected"]
    if len(d["objects"]) != exp["object_count"]:
        fail("FAIL_OBJECT_COUNT")
    if len(primary) != exp["primary_visible_count"]:
        fail("FAIL_PRIMARY_VISIBLE_COUNT")
    if primary != exp["primary_visible_ids"]:
        fail("FAIL_PRIMARY_VISIBLE_IDS:" + json.dumps(primary))
    retirement_preview_count = sum(
        x["disposition"] == "PREVIEW_RETIREMENT_ELIGIBLE" for x in observed
    )
    if retirement_preview_count != exp["retirement_preview_count"]:
        fail("FAIL_RETIREMENT_PREVIEW_COUNT")

    actual_retirement_count = 0
    if actual_retirement_count != exp["actual_retirement_count"]:
        fail("FAIL_ACTUAL_RETIREMENT_COUNT")

    new_git_branch_authorized_count = 0
    if new_git_branch_authorized_count != exp["new_git_branch_authorized_count"]:
        fail("FAIL_NEW_BRANCH_AUTHORITY_COUNT")

    quiet_hidden = sum(
        x["disposition"] in {
            "QUIET_KEEP_IN_FIELD",
            "QUIESCENT_RETAIN_PROVENANCE",
            "QUIET_HIDE_DUPLICATE_PROJECTION"
        }
        for x in observed
    )
    if quiet_hidden != exp["quiet_or_hidden_count"]:
        fail("FAIL_QUIET_HIDDEN_COUNT")

    watch_count = sum(x["disposition"] == "WATCH_UNPROVEN" for x in observed)
    if watch_count != exp["watch_count"]:
        fail("FAIL_WATCH_COUNT")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "STATE": "PASS_COFIELD_SELF_REGULATION_R0H",
        "checked_out_head_sha": head,
        "fixture_semantic_sha256": canonical_sha(d),
        "object_count": len(d["objects"]),
        "primary_visible_ids": primary,
        "primary_attention_budget": budget,
        "retirement_preview_count": retirement_preview_count,
        "actual_retirement_count": actual_retirement_count,
        "new_git_branch_authorized_count": new_git_branch_authorized_count,
        "real_close_or_merge_authority": False,
        "observed": observed,
        "rails": d["rails"]
    }
    print(json.dumps(receipt, separators=(",", ":")))

if __name__ == "__main__":
    main()
