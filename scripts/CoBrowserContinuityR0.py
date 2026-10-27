#!/usr/bin/env python3
"""CoBrowser/CoOrb continuity R0 deterministic local canary."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ALLOWED_STATES = {
    "HEALTHY",
    "BLANK_RENDER",
    "PARTIAL_RENDER",
    "STALE_RENDER",
    "AUTH_REQUIRED",
    "RATE_LIMITED",
    "NETWORK_ERROR",
    "PROVIDER_ERROR",
    "UNKNOWN",
}

RECOVERY = {
    "HEALTHY": "KEEP_SURFACE",
    "BLANK_RENDER": "PROJECT_COORB_FROM_CHECKPOINT",
    "PARTIAL_RENDER": "PROJECT_COORB_AND_COMPARE",
    "STALE_RENDER": "REHYDRATE_FROM_CHECKPOINT_AND_PULSES",
    "AUTH_REQUIRED": "HOLD_AUTH_AND_PROJECT_COORB",
    "RATE_LIMITED": "SUBSTITUTE_ADAPTER_OR_WAIT",
    "NETWORK_ERROR": "PROJECT_COORB_AND_RETRY_LATER",
    "PROVIDER_ERROR": "SUBSTITUTE_ADAPTER",
    "UNKNOWN": "HOLD_UNKNOWN_AND_PROJECT_COORB",
}


def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def run(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schema") == "CoBrowserContinuityFixture.R0", "wrong schema")
    work = payload.get("work_object")
    surfaces = payload.get("surfaces")
    require(isinstance(work, dict), "work_object required")
    require(isinstance(surfaces, list) and surfaces, "surfaces required")

    work_digest = digest(work)
    receipts = []

    for s in surfaces:
        require(isinstance(s, dict), "surface must be object")
        state = s.get("visual_state")
        require(state in ALLOWED_STATES, f"unknown state: {state}")
        require(s.get("work_object_id") == work.get("work_object_id"), "surface/work identity mismatch")

        action = RECOVERY[state]
        receipts.append({
            "surface_id": s["surface_id"],
            "work_object_id": s["work_object_id"],
            "visual_state": state,
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
                "VISUAL_BLANK_NE_CONTEXT_LOST",
                "SESSION_HEALTH_NE_SENTIENCE",
                "PROJECTION_NE_SOURCE",
            ],
        })

    blank = [r for r in receipts if r["visual_state"] == "BLANK_RENDER"]
    require(blank, "fixture must include BLANK_RENDER")
    require(
        all(r["recovery_action"] == "PROJECT_COORB_FROM_CHECKPOINT" for r in blank),
        "blank surface must elect CoOrb recovery",
    )

    return {
        "schema": "CoBrowserContinuityReport.R0",
        "state": "BOUNDED_LOCAL_FIXTURE_PASS__NO_RUNTIME_ADOPTION",
        "work_object_id": work["work_object_id"],
        "work_object_digest": work_digest,
        "surface_count": len(receipts),
        "receipts": receipts,
        "all_work_identity_preserved": all(r["work_identity_preserved"] for r in receipts),
        "all_outward_effects_zero": all(
            all(v == 0 for v in r["effects"].values()) for r in receipts
        ),
        "blank_surface_recovery_proved": all(
            r["recovery_action"] == "PROJECT_COORB_FROM_CHECKPOINT"
            for r in blank
        ),
        "nonclaims": [
            "LOCAL_FIXTURE_NE_X2_RUNTIME",
            "SIMULATED_BLANK_NE_PROVIDER_FAILURE_PROOF",
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
