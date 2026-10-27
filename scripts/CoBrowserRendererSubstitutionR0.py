#!/usr/bin/env python3
"""CoBrowser renderer substitution R0 deterministic canary."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def stable_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def run(payload: dict[str, Any]) -> dict[str, Any]:
    require(payload.get("schema") == "CoBrowserRendererSubstitutionFixture.R0", "wrong schema")
    work = payload.get("work_object")
    projections = payload.get("projections")
    require(isinstance(work, dict), "work_object required")
    require(isinstance(projections, list) and len(projections) >= 3, "three projections required")

    work_digest = stable_digest(work)
    receipts = []

    for p in projections:
        require(p.get("work_object_id") == work.get("work_object_id"), "work identity mismatch")
        require(isinstance(p.get("renderer_id"), str) and p["renderer_id"], "renderer_id required")

        projected = {
            "work_object_id": work["work_object_id"],
            "intent": work["intent"],
            "currentness_cursor": work["currentness_cursor"],
            "evidence_refs": work["evidence_refs"],
            "authority": work["authority"],
            "renderer_id": p["renderer_id"],
            "renderer_family": p["renderer_family"],
            "host": p["host"],
        }

        invariant_view = {
            "work_object_id": projected["work_object_id"],
            "intent": projected["intent"],
            "currentness_cursor": projected["currentness_cursor"],
            "evidence_refs": projected["evidence_refs"],
            "authority": projected["authority"],
        }

        receipts.append({
            "renderer_id": p["renderer_id"],
            "renderer_family": p["renderer_family"],
            "host": p["host"],
            "work_object_digest": work_digest,
            "invariant_projection_digest": stable_digest(invariant_view),
            "effects": {
                "browser_install": 0,
                "browser_uninstall": 0,
                "default_browser_change": 0,
                "provider_mutation": 0,
                "credential_access": 0,
                "network_calls": 0,
                "messages_sent": 0,
                "account_changes": 0,
            },
            "rails": [
                "RENDERER_NE_WORK_IDENTITY",
                "ENGINE_NE_CONTINUITY_ROOT",
                "PROJECTION_NE_SOURCE",
            ],
        })

    invariant_digests = {r["invariant_projection_digest"] for r in receipts}
    require(len(invariant_digests) == 1, "renderer changed invariant work projection")

    families = {r["renderer_family"] for r in receipts}
    require("chromium" in families, "chromium-family projection required")
    require("gecko" in families, "independent gecko-family projection required")
    require("renderer_independent" in families, "typed recovery-floor projection required")

    return {
        "schema": "CoBrowserRendererSubstitutionReport.R0",
        "state": "BOUNDED_SYNTHETIC_SUBSTITUTION_PASS__NO_RUNTIME_ADOPTION",
        "work_object_id": work["work_object_id"],
        "work_object_digest": work_digest,
        "projection_count": len(receipts),
        "renderer_families": sorted(families),
        "receipts": receipts,
        "same_invariant_projection_across_renderers": True,
        "all_outward_effects_zero": all(
            all(v == 0 for v in r["effects"].values()) for r in receipts
        ),
        "retirement_eligible": False,
        "retirement_hold_reason": (
            "Synthetic renderer substitution does not prove X2 inventory, actual cross-engine rendering, "
            "provider-flow compatibility, export completeness, or rollback."
        ),
        "nonclaims": [
            "SYNTHETIC_LABEL_NE_INSTALLED_RENDERER",
            "SUBSTITUTION_PASS_NE_PROVIDER_COMPATIBILITY",
            "NO_BROWSER_REMOVAL_AUTHORIZED",
            "NO_DEFAULT_BROWSER_CHANGE_AUTHORIZED",
            "NO_X2_RUNTIME_ADOPTION",
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
