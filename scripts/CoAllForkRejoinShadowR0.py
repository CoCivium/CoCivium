#!/usr/bin/env python3
"""Provider-agnostic, metadata-only CoFork/Rejoin R0 shadow review.

Accepts only bounded, explicitly synthetic public-safe evidence manifests.
Does not query or manipulate any provider, read transcripts, send messages,
merge source histories, control devices, publish data, or assert receiver ACK.
Provider, CoCivium branding and UI status are NEVER sources of effect authority.
"""
from __future__ import annotations

import re

ID = re.compile(r"[A-Za-z][A-Za-z0-9_.:-]{1,79}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
VIEW_KEYS = {
    "surface_id", "provider_id", "work_id", "base_sha256",
    "visible_sha256", "head_sha256", "deltas", "privacy",
    "observed_at", "source_access", "receipt_state",
}
DELTA_KEYS = {"delta_id", "sha256", "kind", "effect_key"}
EVENTS = {"SOURCE_VERSION_CHANGED", "USER_COW_REVIEW", "VISIBLE_REJOIN_OBSERVED"}
KINDS = {"SOURCE_NOTE", "PROPOSAL", "EFFECT_INTENT"}
MAX_DELTAS = 16

BASE = {
    "schema": "CoAll.ForkRejoin.ShadowR0",
    "effect": "NONE",
    "provider_action": "NONE",
    "merged_transcript": False,
    "source_bytes_recovered": False,
    "global_completeness": "UNKNOWN",
    "provider_independence": "SCHEMA_ONLY_NO_LIVE_ADAPTER",
    "coCivium_brand_grants_authority": False,
    "public_release_authorized": False,
    "provider_delete_safe": False,
    "receiver_readproof": "NOT_ESTABLISHED",
    "independent_cold_restore": "NOT_TESTED",
    "actuator_elected": False,
    "duplicate_effects_executed": 0,
    "portable_format": "JSON_COMPATIBLE_METADATA_ONLY",
    "anti_capture_proven": False,
    "next_wake": "NEW_QUALIFIED_SOURCE_OR_RECEIVER_EVIDENCE",
    "nonclaims": [
        "BRAND_NE_OWNERSHIP_OR_AUTHORITY",
        "VISIBLE_REJOIN_NE_EXACT_HISTORY_RECONCILIATION",
        "MATCHING_HASH_NE_INDEPENDENT_RECEIVER_READPROOF",
        "SOURCE_MANIFEST_NE_TRANSCRIPT_CAPTURE",
        "SOURCE_POINTERS_NE_PRESERVED_PRIVATE_BYTES",
        "MERGE_PROPOSAL_NE_MERGE_EFFECT",
        "PROVIDER_AGNOSTIC_SCHEMA_NE_PROVIDER_INTEGRATION",
        "PORTABLE_FORMAT_NE_VERIFIED_EXIT",
        "COW_NE_PROVIDER_DELETE_AUTHORITY",
    ],
}


def _id(value: object) -> bool:
    return isinstance(value, str) and bool(ID.fullmatch(value))


def _sha(value: object) -> bool:
    return isinstance(value, str) and bool(SHA.fullmatch(value))


def _valid_view(v: object, now: int, max_age: int) -> bool:
    if not isinstance(v, dict) or set(v) != VIEW_KEYS:
        return False
    if not all(_id(v[k]) for k in ("surface_id", "provider_id", "work_id")):
        return False
    if not all(_sha(v[k]) for k in ("base_sha256", "visible_sha256", "head_sha256")):
        return False
    if (v["privacy"] != "SYNTHETIC_PUBLIC_SAFE"
            or v["source_access"] != "MANIFEST_ONLY"
            or v["receipt_state"] != "NOT_ESTABLISHED"
            or type(v["observed_at"]) is not int
            or v["observed_at"] > now
            or v["observed_at"] < 0
            or now - v["observed_at"] > max_age):
        return False
    if not isinstance(v["deltas"], list) or len(v["deltas"]) > MAX_DELTAS:
        return False
    ids = set()
    for d in v["deltas"]:
        if not isinstance(d, dict) or set(d) != DELTA_KEYS:
            return False
        if not _id(d["delta_id"]) or not _sha(d["sha256"]) or d["kind"] not in KINDS:
            return False
        if d["delta_id"] in ids:
            return False
        ids.add(d["delta_id"])
        if d["kind"] == "EFFECT_INTENT":
            if not _id(d["effect_key"]):
                return False
        elif d["effect_key"] is not None:
            return False
    return True


def inspect_pair(left: object, right: object, *, event: str,
                 now: int, max_age: int = 86400) -> dict:
    """Source-bound, non-destructive metadata crosswalk, never actuation."""
    result = {
        **BASE,
        "state": "HOLD",
        "holds": [],
        "work_id": None,
        "surface_count": 0,
        "visible_views_match": None,
        "heads_match": None,
        "shared_delta_count": 0,
        "unique_left_delta_count": 0,
        "unique_right_delta_count": 0,
        "delta_conflict_count": 0,
        "candidate_delta_refs": [],
        "effect_intent_collisions": 0,
    }
    if type(now) is not int or now < 0 or type(max_age) is not int or max_age < 1:
        return {**result, "holds": ["INVALID_TIME"]}
    if not _valid_view(left, now, max_age) or not _valid_view(right, now, max_age):
        return {**result, "holds": ["MISSING_OR_UNQUALIFIED_SOURCE_MANIFEST"]}
    if left["surface_id"] == right["surface_id"]:
        return {**result, "holds": ["SAME_SURFACE_NOT_INDEPENDENT_VIEW"]}
    if left["work_id"] != right["work_id"]:
        return {**result, "holds": ["WORK_ID_CONFLICT"]}
    if left["base_sha256"] != right["base_sha256"]:
        return {**result, "holds": ["COMMON_ANCESTOR_NOT_ESTABLISHED"]}
    result.update({
        "work_id": left["work_id"],
        "surface_count": 2,
        "visible_views_match": left["visible_sha256"] == right["visible_sha256"],
        "heads_match": left["head_sha256"] == right["head_sha256"],
    })
    if event not in EVENTS:
        return {**result, "state": "QUIET_NO_QUALIFIED_CHANGE", "holds": [
            "TIMER_ALONE_CANNOT_TRIGGER_HANDOFF"
        ]}
    a = {d["delta_id"]: d for d in left["deltas"]}
    b = {d["delta_id"]: d for d in right["deltas"]}
    shared = set(a) & set(b)
    conflicts = {key for key in shared if a[key] != b[key]}
    ids = sorted(set(a) | set(b))
    effects_a = {d["effect_key"] for d in left["deltas"] if d["kind"] == "EFFECT_INTENT"}
    effects_b = {d["effect_key"] for d in right["deltas"] if d["kind"] == "EFFECT_INTENT"}
    result.update({
        "shared_delta_count": len(shared) - len(conflicts),
        "unique_left_delta_count": len(set(a) - set(b)),
        "unique_right_delta_count": len(set(b) - set(a)),
        "delta_conflict_count": len(conflicts),
        # Synthetic metadata tokens, NEVER raw conversation content.
        "candidate_delta_refs": ids,
        "effect_intent_collisions": len(effects_a & effects_b),
    })
    if conflicts:
        state, holds = "HOLD_CONFLICTING_DELTA_REVISIONS", ["NEVER_LAST_WRITER_WINS"]
    elif (not result["heads_match"] or len(set(a) ^ set(b)) > 0):
        state, holds = "SHADOW_FORK_DIFF_REQUIRES_SOURCE_READBACK", [
            "PRESERVE_BOTH_SOURCE_BRANCHES",
            "MATCHED_UI_DOES_NOT_REMOVE_UNIQUE_DELTAS",
        ]
    else:
        state, holds = "SHADOW_VIEWS_MATCH_SOURCE_COVERAGE_UNKNOWN", [
            "MANIFEST_MATCH_DOES_NOT_PROVE_COMPLETE_HISTORY",
        ]
    if result["effect_intent_collisions"]:
        holds.append("DUPLICATE_EFFECT_INTENT_MUST_BE_FENCED_EXTERNALLY")
    if result["visible_views_match"] and (not result["heads_match"] or len(set(a) ^ set(b)) > 0):
        holds.append("VISIBLE_SYNC_ONLY_WITH_UNRESOLVED_CONTENT_DIFF")
    return {**result, "state": state, "holds": sorted(set(holds))}
