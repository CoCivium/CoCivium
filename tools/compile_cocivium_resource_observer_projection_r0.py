#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def fail(code):
    raise SystemExit("FAIL:" + code)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest().upper()


def git_blob(path):
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{path}"], text=True
    ).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-receipt", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    src_path = Path(args.source_receipt)
    src_raw = src_path.read_bytes()
    src = json.loads(src_raw.decode("utf-8"))

    if src.get("STATE") != "PASS_COALL_RESOURCE_GRANT_LEASE_INTERFACE_RECEIVER_READPROOF_R0":
        fail("SOURCE_RECEIPT_STATE")
    if src.get("receiver_identity") != "github-actions:PR137_RESOURCE_INTERFACE_RECEIVER_R0":
        fail("SOURCE_RECEIVER_IDENTITY")
    if src.get("receiver_exact_object_readproof") != "PASS":
        fail("SOURCE_EXACT_OBJECT_READPROOF")
    if src.get("bounded_lifecycle_interpretation") != "PICKED_UP_BY_PR137_RESOURCE_INTERFACE_RECEIVER":
        fail("SOURCE_LIFECYCLE_INTERPRETATION")
    if src.get("integration_state") != "UNPROVEN":
        fail("SOURCE_INTEGRATION_STATE")
    if src.get("runtime_adoption") is not False:
        fail("SOURCE_RUNTIME_ADOPTION")
    if src.get("real_resource_execution_count") != 0:
        fail("SOURCE_RESOURCE_EXECUTION")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    commit_time = subprocess.check_output(
        ["git", "show", "-s", "--format=%cI", "HEAD"], text=True
    ).strip()
    if src.get("checked_out_head_sha") != head:
        fail("SOURCE_HEAD_NE_CURRENT_HEAD")

    exact_objects = src.get("exact_objects")
    if not isinstance(exact_objects, list) or len(exact_objects) != 3:
        fail("SOURCE_EXACT_OBJECT_SET")

    checked_objects = []
    for obj in exact_objects:
        path = obj.get("path")
        expected = obj.get("git_blob_sha")
        if not path or not expected:
            fail("SOURCE_OBJECT_FIELDS")
        actual = git_blob(path)
        if actual != expected:
            fail("SOURCE_OBJECT_BLOB_DRIFT:" + path)
        checked_objects.append({
            "path": path,
            "git_blob_sha": actual,
            "readproof": "PASS_EXACT_OBJECT_HEAD_BIND"
        })

    source_receipt_sha256 = sha256(src_raw)

    projection = {
        "schema": "CoCivium.ObserverProjection.R0",
        "STATE": "PASS_COCIVIUM_RESOURCE_OBSERVER_PROJECTION_RECEIVER_R0",
        "visible_root_brand": "CoCivium",
        "surface_target": "CoBar",
        "surface_delivery_state": "PENDING_COBAR_PICKUP",
        "source": {
            "repository": "CoCivium/CoCivium",
            "pull_request": 137,
            "branch": "candidate/cocivia-ambient-correspondence-r0-20260930",
            "head_sha": head,
            "commit_time": commit_time,
            "source_receiver_identity": src["receiver_identity"],
            "source_receipt_sha256": source_receipt_sha256
        },
        "receiver": {
            "identity": "github-actions:PR137_COCIVIUM_OBSERVER_PROJECTION_RECEIVER_R0",
            "source_receipt_readproof": "PASS_EXACT_RECEIPT_READBACK",
            "source_exact_object_count": len(checked_objects),
            "source_exact_objects": checked_objects
        },
        "CoHereNow": "CoCivium has a validated candidate ResourceGrant/ResourceLease interface with exact GitHub receiver pickup; runtime adoption and CoBar delivery are still unproven.",
        "Meaning": "The resource-field exploration has contracted into two reusable interfaces and a receiver proof. This observer payload makes that state legible without promoting the interfaces into runtime or asking Rick to inspect receipt machinery.",
        "NextSafeAction": "DELIVER_THIS_EXACT_PROJECTION_TO_CURRENT_COBAR_RECEIVER_AND_REQUIRE_RICK_VISIBLE_READBACK_WHEN_AN_AUTHORIZED_LOCAL_ROUTE_IS_AVAILABLE",
        "Evidence": {
            "source_receipt_state": src["STATE"],
            "source_bounded_lifecycle": src["bounded_lifecycle_interpretation"],
            "source_integration_state": src["integration_state"],
            "grant_source_object": src["grant_source_object"],
            "energet_projection": src["energet_projection"],
            "coops_projection": src["coops_projection"],
            "negative_case_count": src["negative_case_count"],
            "source_receipt_sha256": source_receipt_sha256
        },
        "lifecycle": {
            "source_receipt": "PICKED_UP_BY_PR137_COCIVIUM_OBSERVER_PROJECTION_RECEIVER",
            "observer_projection_before_artifact_upload": "VERIFIED_LOCAL_IN_GITHUB_ACTIONS_JOB",
            "cobar_pickup": "UNPROVEN",
            "integration": "UNPROVEN",
            "coex": "UNPROVEN"
        },
        "ux_state": "UX_ACCEPTANCE_UNPROVEN",
        "nonclaims": [
            "OBSERVER_PROJECTION_NE_NEW_RESOURCE_ONTOLOGY",
            "SOURCE_RECEIPT_PICKUP_NE_RESOURCE_RUNTIME_ADOPTION",
            "PROJECTION_ARTIFACT_NE_COBAR_PICKUP",
            "COBAR_POINTER_NE_RICK_VISIBLE_READBACK",
            "VALIDATION_IS_NOT_ACCEPTANCE",
            "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE"
        ]
    }

    out = Path(args.output)
    if out.exists():
        fail("NO_CLOBBER_OUTPUT")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(projection, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "STATE": projection["STATE"],
        "checked_out_head_sha": head,
        "source_receipt_sha256": source_receipt_sha256,
        "source_exact_object_count": len(checked_objects),
        "visible_root_brand": projection["visible_root_brand"],
        "surface_target": projection["surface_target"],
        "surface_delivery_state": projection["surface_delivery_state"],
        "ux_state": projection["ux_state"]
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
