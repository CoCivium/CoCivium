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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projection", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    src_path = Path(args.projection)
    src_raw = src_path.read_bytes()
    src = json.loads(src_raw.decode("utf-8"))

    if src.get("STATE") != "PASS_COCIVIUM_RESOURCE_OBSERVER_PROJECTION_RECEIVER_R0":
        fail("SOURCE_PROJECTION_STATE")
    if src.get("visible_root_brand") != "CoCivium":
        fail("VISIBLE_ROOT_BRAND")
    if src.get("surface_target") != "CoBar":
        fail("SURFACE_TARGET")
    if src.get("surface_delivery_state") != "PENDING_COBAR_PICKUP":
        fail("DELIVERY_STATE")
    if src.get("ux_state") != "UX_ACCEPTANCE_UNPROVEN":
        fail("UX_STATE")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    commit_time = subprocess.check_output(
        ["git", "show", "-s", "--format=%cI", "HEAD"], text=True
    ).strip()

    source = src.get("source") or {}
    if source.get("head_sha") != head:
        fail("SOURCE_HEAD_NE_CURRENT_HEAD")
    if source.get("commit_time") != commit_time:
        fail("SOURCE_COMMIT_TIME_NE_CURRENT_HEAD")

    projection_sha256 = sha256(src_raw)

    capsule = {
        "schema": "CoCivium.CoBarDeliveryCapsule.R0",
        "STATE": "PASS_COBAR_RESOURCE_OBSERVER_DELIVERY_CAPSULE_R0",
        "visible_root_brand": "CoCivium",
        "target_surface": "CoBar",
        "target_receiver_class": "CURRENT_AUTHORIZED_LOCAL_COBAR_RECEIVER",
        "source_projection": {
            "sha256": projection_sha256,
            "head_sha": head,
            "commit_time": commit_time,
            "source_receiver_identity": source.get("source_receiver_identity"),
            "source_receipt_sha256": source.get("source_receipt_sha256")
        },
        "payload": {
            "CoHereNow": src["CoHereNow"],
            "Meaning": src["Meaning"],
            "NextSafeAction": src["NextSafeAction"],
            "Evidence": src["Evidence"]
        },
        "pickup_contract": {
            "minimum_receiver_evidence": [
                "receiver_identity",
                "exact_projection_sha256",
                "source_head_sha",
                "source_commit_time",
                "receiver_read_timestamp",
                "exact_payload_readback"
            ],
            "pickup_state_only_after_exact_readproof": "PICKED_UP_BY_CURRENT_COBAR_RECEIVER",
            "pointer_only_is_not_pickup": True,
            "artifact_visibility_is_not_pickup": True,
            "rick_visible_readback_required_for_ux_acceptance": True,
            "integration_requires_separate_acceptance": True
        },
        "delivery_policy": {
            "user_relay_required": False,
            "no_clobber_required": True,
            "latest_only_if_exact_head_matches": True,
            "stale_head_action": "HOLD_STALE_PROJECTION",
            "external_effect_authority": False
        },
        "lifecycle": {
            "source_projection": "LANDED_AS_CURRENT_GITHUB_ACTIONS_ARTIFACT_AFTER_UPLOAD",
            "cobar_pickup": "UNPROVEN",
            "rick_visible_readback": "UNPROVEN",
            "integration": "UNPROVEN",
            "coex": "UNPROVEN"
        },
        "ux_state": "UX_ACCEPTANCE_UNPROVEN",
        "nonclaims": [
            "CAPSULE_NE_COBAR_PICKUP",
            "ARTIFACT_VISIBLE_NE_LANDED_AT_LOCAL_COBAR",
            "POINTER_NE_ACK",
            "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
            "COBAR_PICKUP_NE_RICK_VISIBLE_READBACK",
            "VALIDATION_IS_NOT_ACCEPTANCE",
            "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE"
        ]
    }

    out = Path(args.output)
    if out.exists():
        fail("NO_CLOBBER_OUTPUT")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(capsule, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "STATE": capsule["STATE"],
        "checked_out_head_sha": head,
        "source_projection_sha256": projection_sha256,
        "target_surface": capsule["target_surface"],
        "target_receiver_class": capsule["target_receiver_class"],
        "user_relay_required": capsule["delivery_policy"]["user_relay_required"],
        "cobar_pickup": capsule["lifecycle"]["cobar_pickup"],
        "rick_visible_readback": capsule["lifecycle"]["rick_visible_readback"],
        "ux_state": capsule["ux_state"]
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
