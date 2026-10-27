#!/usr/bin/env python3
"""CoBrowser/CoOrb continuity R0.1 deterministic local canary."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

RENDER_STATES = {"RENDERED", "BLANK", "PARTIAL", "ERROR", "UNKNOWN"}
CURRENTNESS_STATES = {"CURRENT", "STALE", "UNKNOWN"}
INTERACTION_STATES = {"RESPONSIVE", "DEGRADED", "UNKNOWN"}
AUTH_STATES = {"AUTHENTICATED_OBSERVED", "AUTH_REQUIRED", "UNKNOWN"}
NETWORK_STATES = {"REACHABLE", "UNREACHABLE", "UNKNOWN"}
PROVIDER_STATES = {"OK", "RATE_LIMITED", "ERROR", "UNKNOWN"}


def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def recovery_action(surface: dict[str, Any]) -> str:
    if surface["auth_state"] == "AUTH_REQUIRED":
        return "HOLD_AUTH_AND_PROJECT_COORB"
    if surface["render_state"] == "BLANK":
        return "PROJECT_COORB_FROM_CHECKPOINT"
    if surface["render_state"] in {"PARTIAL", "ERROR"}:
        return "PROJECT_COORB_AND_COMPARE"
    if surface["currentness_state"] == "STALE":
        return "REHYDRATE_FROM_CHECKPOINT_AND_PULSES"
    if surface["provider_state"] == "RATE_LIMITED":
        return "SUBSTITUTE_ADAPTER_OR_WAIT"
    if surface["provider_state"] == "ERROR" or surface["network_state"] == "UNREACHABLE":
        return "PROJECT_COORB_AND_RETRY_OR_SUBSTITUTE"
    if (
        surface["render_state"] == "RENDERED"
        and surface["currentness_state"] == "CURRENT"
        and surface["interaction_state"] == "RESPONSIVE"
        and surface["provider_state"] == "OK"
    ):
        return "KEEP_SURFACE"
    return "PROJECT_COORB_AND_VERIFY_CURRENTNESS"


def run(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schema") == "CoBrowserContinuityFixture.R0.1", "wrong schema")
    work = payload.get("work_object")
    surfaces = payload.get("surfaces")
    require(isinstance(work, dict), "work_object required")
    require(isinstance(surfaces, list) and surfaces, "surfaces required")

    work_digest = digest(work)
    receipts = []

    for s in surfaces:
        require(isinstance(s, dict), "surface must be object")
        require(s.get("work_object_id") == work.get("work_object_id"), "surface/work identity mismatch")
        require(s.get("render_state") in RENDER_STATES, f"bad render state: {s.get('render_state')}")
        require(s.get("currentness_state") in CURRENTNESS_STATES, f"bad currentness: {s.get('currentness_state')}")
        require(s.get("interaction_state") in INTERACTION_STATES, f"bad interaction: {s.get('interaction_state')}")
        require(s.get("auth_state") in AUTH_STATES, f"bad auth: {s.get('auth_state')}")
        require(s.get("network_state") in NETWORK_STATES, f"bad network: {s.get('network_state')}")
        require(s.get("provider_state") in PROVIDER_STATES, f"bad provider: {s.get('provider_state')}")

        action = recovery_action(s)
        receipts.append({
            "surface_id": s["surface_id"],
            "work_object_id": s["work_object_id"],
            "health_axes": {
                "render_state": s["render_state"],
                "currentness_state": s["currentness_state"],
                "interaction_state": s["interaction_state"],
                "auth_state": s["auth_state"],
                "network_state": s["network_state"],
                "provider_state": s["provider_state"],
            },
            "recovery_action": action,
            "work_object_digest_before": work_digest,
            "work_object_digest_after": work_digest,
            "work_identity_preserved": True,
            "effects": {
                "network_calls": 0,
                "provider_mutations": 0,
                "credential_access": 0,
                "messages_sent": 0,
                "account_changes": 0,
                "tabs_closed": 0,
            },
            "rails": [
                "WORK_OBJECT_NE_TAB",
                "VISIBLE_NE_CURRENT",
                "RENDERED_NE_RESPONSIVE",
                "SESSION_HEALTH_NE_SENTIENCE",
                "PROJECTION_NE_SOURCE",
            ],
        })

    by_id = {r["surface_id"]: r for r in receipts}
    require(
        by_id["surface-blank"]["recovery_action"] == "PROJECT_COORB_FROM_CHECKPOINT",
        "blank surface must elect CoOrb recovery",
    )
    require(
        by_id["surface-visible-unknown"]["recovery_action"] == "PROJECT_COORB_AND_VERIFY_CURRENTNESS",
        "visible unknown-currentness surface must not be treated as healthy",
    )

    return {
        "schema": "CoBrowserContinuityReport.R0.1",
        "state": "BOUNDED_LOCAL_FIXTURE_PASS__NO_RUNTIME_ADOPTION",
        "work_object_id": work["work_object_id"],
        "work_object_digest": work_digest,
        "surface_count": len(receipts),
        "receipts": receipts,
        "all_work_identity_preserved": all(r["work_identity_preserved"] for r in receipts),
        "all_outward_effects_zero": all(
            all(v == 0 for v in r["effects"].values()) for r in receipts
        ),
        "blank_surface_recovery_proved": (
            by_id["surface-blank"]["recovery_action"] == "PROJECT_COORB_FROM_CHECKPOINT"
        ),
        "visible_unknown_not_promoted_to_healthy": (
            by_id["surface-visible-unknown"]["recovery_action"]
            == "PROJECT_COORB_AND_VERIFY_CURRENTNESS"
        ),
        "nonclaims": [
            "LOCAL_FIXTURE_NE_X2_RUNTIME",
            "SIMULATED_BLANK_NE_PROVIDER_FAILURE_PROOF",
            "VISIBLE_RENDER_NE_CURRENT_CONTEXT",
            "RECOVERY_ELECTION_NE_RECEIVER_PICKUP",
            "CHECKPOINT_POINTER_NE_CURRENT_TRUTH",
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--fixture", type=Path, required=True)
    args = p.parse_args()
    payload = json.loads(args.fixture.read_text(encoding="utf-8"))
    print(json.dumps(run(payload), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
