#!/usr/bin/env python3
"""Bounded, read-only source-metadata gap detector for CoLivingHighlight+.

No network access, effect privileges, source changes, recipient inference,
background work, physical sensing, or claim of independent receiver adoption.
A gap in this flat registry does not establish absence elsewhere.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = "ai/highlight-assets.json"
PILOT_PATH = "docs/Architecture/COHIGHLIGHT_REGENERATIVE_CANARY_R0_20261026.json"
# Each entry is a metadata declaration slot, NOT a verified success signal.
FIELD_KEYS = (
    ("source_binding", "source_refs"),
    ("source_currentness", "source_currentness_receipt"),
    ("receiver_route", "qualified_receiver_ref"),
    ("receiver_use_case", "receiver_use_case"),
    ("independent_receiver_result", "receiver_origin_receipt"),
    ("return_route", "return_route"),
    ("challenge_route", "challenge_ref"),
    ("wake_condition", "wake_triggers"),
    ("stop_condition", "stop_rule"),
    ("successor_binding", "successor_ref"),
    ("recovery_proof", "recovery_receipt"),
    ("resource_cost", "resource_cost"),
    ("maintenance_owner", "maintenance_owner"),
)
MAX_ASSETS = 128


def _filled(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple)):
        return bool(value) and all(isinstance(v, str) and v.strip() for v in value)
    if isinstance(value, dict):
        return bool(value) and all(isinstance(k, str) and k.strip() for k in value)
    return False


def _validate_registry(reg: dict) -> list[dict]:
    if reg.get("schema") != "CoAll.HighlightRegistry.v0.1-candidate":
        raise ValueError("unrecognized highlight registry")
    assets = reg.get("assets")
    if not isinstance(assets, list) or not 1 <= len(assets) <= MAX_ASSETS:
        raise ValueError("empty or unbounded registry")
    ids = []
    for asset in assets:
        if not isinstance(asset, dict):
            raise ValueError("asset record is not an object")
        for key in ("id", "name", "status", "readiness"):
            if not _filled(asset.get(key)) or not isinstance(asset[key], str):
                raise ValueError("missing required asset identifier or state")
        ids.append(asset["id"])
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate asset identities")
    return sorted(assets, key=lambda x: x["id"])


def _validate_pilot(pilot: dict) -> list[dict]:
    if pilot.get("schema") != "CoCivium.CoHighlightRegenerativeCanary.v0.1":
        raise ValueError("unrecognized 3-role regenerative canary")
    assets = pilot.get("assets")
    if not isinstance(assets, list) or not 1 <= len(assets) <= MAX_ASSETS:
        raise ValueError("empty or unbounded canary")
    ids = [a.get("id") for a in assets if isinstance(a, dict)]
    if len(ids) != len(assets) or not all(isinstance(i, str) and i.strip() for i in ids):
        raise ValueError("invalid pilot identity")
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate pilot identities")
    return sorted(assets, key=lambda x: x["id"])


def build_report(registry: dict, pilot: dict, registry_digest: str = "",
                 pilot_digest: str = "") -> dict:
    """Account for *fields in the two named files*, never system-wide truth."""
    assets = _validate_registry(registry)
    pilots = _validate_pilot(pilot)
    declared_counts = {name: 0 for name, _ in FIELD_KEYS}
    gaps = []
    for asset in assets:
        declared = [name for name, key in FIELD_KEYS if _filled(asset.get(key))]
        missing = [name for name, _ in FIELD_KEYS if name not in declared]
        for name in declared:
            declared_counts[name] += 1
        gaps.append({
            "asset_id": asset["id"],
            "original_readiness_label": asset["readiness"],
            "original_status_label": asset["status"],
            "declared_metadata": declared,
            "missing_from_flat_registry": missing,
            "not_a_global_absence_claim": True,
            "source_currentness_verified": False,
            "receiver_origin_accepted": False,
            "runtime_control_granted": False,
        })
    role_views = []
    for a in pilots:
        role_views.append({
            "canary_id": a["id"],
            "role": a.get("role", "UNKNOWN"),
            "receiver_role_named_not_consent": _filled(a.get("receiver")),
            "source_basis_narrative_not_exact_binding": _filled(a.get("source_basis")),
            "challenge_proposed": _filled(a.get("challenge_path")),
            "requalification_candidates": _filled(a.get("expiry_or_requalification")),
            "return_signal_categories_not_receipts": _filled(a.get("return_signal")),
            "successor_rule_not_elected_successor": _filled(a.get("successor_condition")),
            "real_receiver_accepted": False,
            "verified_external_effect": False,
        })
    return {
        "schema": "CoCivium.CoHighlight.ReturnGap.ReadOnlyR0",
        "state": "PASS_METADATA_COVERAGE_PROBE__REAL_RENEWAL_AND_RECEIVER_HELD",
        "scope": "ONLY_TWO_PINNED_PUBLIC_REPOSITORY_FILES__NOT_FLEET_CENSUS",
        "input_refs": [
            {"path": REGISTRY_PATH, "sha256": registry_digest},
            {"path": PILOT_PATH, "sha256": pilot_digest},
        ],
        "flat_registry_updated_utc": registry.get("updated_utc", "UNKNOWN"),
        "flat_registry_asset_count": len(assets),
        "pilot_declared_role_count": len(pilots),
        "metadata_fields_per_asset": len(FIELD_KEYS),
        "flat_registry_field_declaration_counts": declared_counts,
        "flat_registry_asset_gaps": gaps,
        "pilot_role_declarations": role_views,
        "next_safe_probe": (
            "Qualify ONE existing public-safe highlight against exact source/"
            "currentness, receiver need, permission, consented first-use, "
            "negative feedback, successor/recovery and cost. Record receiver-"
            "origin evidence before promoting regenerative benefit."
        ),
        "future_wake_rule": (
            "GitHub workflow runs on bounded source-file changes; this "
            "tool does not poll, autonomously recruit, or wake other systems."
        ),
        "external_effects": 0,
        "new_autonomous_workers": 0,
        "real_reader_receipts": 0,
        "nonclaims": [
            "MISSING_FIELD_IN_INDEX_NE_ABSENT_SOMEWHERE_ELSE",
            "SOURCE_BASIS_PROSE_NE_EXACT_SOURCE_READPROOF",
            "DECLARED_RECEIVER_ROLE_NE_RECEIVER_CONSENT",
            "PROPOSED_RETURN_SIGNAL_NE_OBSERVED_RETURN",
            "WAKE_RULE_TEXT_NE_SCHEDULER_INSTALLED",
            "FRESHNESS_TIMESTAMP_NE_SOURCE_CURRENTNESS",
            "LARGER_CATALOG_NE_MORE_VALUE",
            "CANDIDATE_RENEWAL_NE_AUTOMATED_RUNTIME",
            "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
        ],
    }


def build_from_root(root: Path = ROOT) -> dict:
    registry_raw = (root / REGISTRY_PATH).read_bytes()
    pilot_raw = (root / PILOT_PATH).read_bytes()
    return build_report(
        json.loads(registry_raw),
        json.loads(pilot_raw),
        hashlib.sha256(registry_raw).hexdigest(),
        hashlib.sha256(pilot_raw).hexdigest(),
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--compact", action="store_true", help="single-line JSON output")
    args = ap.parse_args()
    result = build_from_root()
    print(json.dumps(result, ensure_ascii=True, sort_keys=True,
                     indent=None if args.compact else 2))
    # A source coverage gap is useful evidence, not a failing CI test.
    # Only invalid/malformed source input fails closed in validation.


if __name__ == "__main__":
    main()
