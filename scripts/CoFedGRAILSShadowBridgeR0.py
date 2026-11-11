#!/usr/bin/env python3
"""CoFedGRAILS+ shadow bridge: two or more declared cells, zero effects.

This is a public-safe, synthetic compatibility test. Matching source hashes,
failure-domain labels and cursors neither authenticate a node nor establish a
receiver ACK. CoFuturePull+ is advisory; CoBF+ is a local shadow candidate.
"""
from __future__ import annotations

import re
from CoBestFaceFutureShadowR0 import shadow_select

CELL_KEYS = {
    "schema", "cell_id", "operator_id", "failure_domain_id", "work_id",
    "source_sha256", "privacy", "authority", "observed_at", "cursor",
    "ack_state", "claimed_state",
}
IDENT = re.compile(r"[A-Za-z][A-Za-z0-9_.:-]{2,79}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
EVENTS = {"MATERIAL_SOURCE_DELTA", "INDEPENDENT_RECEIVER_DELTA", "USER_COW_REVIEW", "FEDERATION_PEER_DIFF"}


def valid_cell(c: object, now_s: int, age_limit_s: int) -> bool:
    if not isinstance(c, dict) or set(c) != CELL_KEYS:
        return False
    if any(not isinstance(c[k], str) or not IDENT.fullmatch(c[k])
           for k in ("cell_id", "operator_id", "failure_domain_id", "work_id")):
        return False
    return (
        c["schema"] == "CoFedGRAILS.ShadowCellR0"
        and isinstance(c["source_sha256"], str)
        and bool(DIGEST.fullmatch(c["source_sha256"]))
        and c["privacy"] == "PUBLIC_SAFE"
        and c["authority"] == "OBSERVE_ONLY"
        and c["ack_state"] == "NOT_ESTABLISHED"
        and c["claimed_state"] == "DECLARED_SHADOW_ONLY"
        and type(c["observed_at"]) is int
        and 0 <= c["observed_at"] <= now_s
        and now_s - c["observed_at"] <= age_limit_s
        and type(c["cursor"]) is int and c["cursor"] >= 0
    )


def shadow_federate(local: object, peers: object, baseline: object,
                    candidates: object, *, event: str, now_s: int,
                    age_limit_s: int = 86400) -> dict:
    """Shadow-relate opt-in cells without granting shared control or release."""
    result = {
        "schema": "CoFedGRAILS.ShadowBridgeR0",
        "state": "HOLD", "holds": [], "effect": "NONE",
        "federation_authority": False, "release_authorized": False,
        "global_control_plane": False, "independent_receiver_ack": "NOT_ESTABLISHED",
        "selected_live_id": None, "candidate_ids": [],
        "received_from_peers": 0,
        "nonclaims": [
            "DISCOVERY_NE_CONSENT", "COMPATIBILITY_NE_TRUST",
            "DECLARED_FAILURE_DOMAINS_NE_INDEPENDENT_RESTORE",
            "MATCHING_HASH_NE_PICKUP", "FUTURE_PREFERENCE_NE_EXECUTION",
            "FEDERATION_NE_GLOBAL_CONTROL", "SHADOW_NE_PUBLIC_RELEASE",
        ],
    }
    if type(now_s) is not int or now_s < 0 or type(age_limit_s) is not int or age_limit_s < 1:
        return {**result, "holds": ["INVALID_TIME"]}
    if not valid_cell(local, now_s, age_limit_s):
        return {**result, "holds": ["INVALID_LOCAL_CELL"]}
    if not isinstance(peers, list) or not 1 <= len(peers) <= 4:
        return {**result, "holds": ["PEER_BUDGET_OR_TYPE"]}
    if event not in EVENTS:
        return {**result, "state": "QUIET_NO_MATERIAL_EVENT"}
    seen_cells = {local["cell_id"]}
    seen_operators = {local["operator_id"]}
    seen_failure_domains = {local["failure_domain_id"]}
    for peer in peers:
        if not valid_cell(peer, now_s, age_limit_s):
            return {**result, "holds": ["INVALID_PEER_CELL"]}
        if peer["cell_id"] in seen_cells:
            return {**result, "holds": ["DUPLICATE_CELL"]}
        seen_cells.add(peer["cell_id"])
        if peer["operator_id"] in seen_operators or peer["failure_domain_id"] in seen_failure_domains:
            return {**result, "holds": ["NONINDEPENDENT_DECLARED_DOMAINS"]}
        seen_operators.add(peer["operator_id"])
        seen_failure_domains.add(peer["failure_domain_id"])
        if peer["work_id"] != local["work_id"]:
            return {**result, "holds": ["WORK_ID_CONFLICT"]}
        if peer["source_sha256"] != local["source_sha256"]:
            return {**result, "holds": ["SOURCE_REVISION_CONFLICT"]}
        if peer["cursor"] < local["cursor"]:
            return {**result, "holds": ["PEER_CURSOR_BEHIND_SOURCE"]}
    if not isinstance(baseline, dict):
        return {**result, "holds": ["INVALID_COBF_BASELINE"]}
    if baseline.get("work_id") != local["work_id"] or baseline.get("source_sha256") != local["source_sha256"]:
        return {**result, "holds": ["COBF_SOURCE_IDENTITY_MISMATCH"]}
    # This remains purely local. It does not send work to peers.
    projection = shadow_select(
        baseline, candidates, event="MATERIAL_SOURCE_DELTA",
        now_s=now_s, max_age_s=age_limit_s
    )
    return {
        **result,
        "state": "FEDERATION_SHADOW_COMPATIBLE" if projection["state"].startswith("SHADOW_")
                 else "FEDERATION_SHADOW_NO_IMPROVEMENT",
        "holds": sorted(set(projection["holds"] + [
            "RECEIVER_READPROOF_UNPROVEN", "PEER_AUTHENTICATION_UNPROVEN",
            "LOCAL_AUTHORIZED_RELEASE_UNPROVEN",
        ])),
        "selected_live_id": projection["selected_live_id"],
        "candidate_ids": projection["shadow_candidate_ids"],
        "declared_peer_count": len(peers),
    }
