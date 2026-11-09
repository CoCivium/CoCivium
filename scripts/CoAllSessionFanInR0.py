#!/usr/bin/env python3
"""Privacy-minimized, zero-effect session-source fan-in candidate for #317.

This module does not browse provider sessions, transmit payloads, contact a
receiver or assert a durable landing. Inputs must be explicitly supplied by an
authorized upstream observer. Only non-sensitive synthetic IDs are acceptable.
"""
from __future__ import annotations

import re
from collections import defaultdict

ID = re.compile(r"^[A-Za-z0-9_.:-]{1,100}$")
DIGEST = re.compile(r"^[a-f0-9]{64}$")
FIELDS = {"session_id", "work_id", "source_sha256", "scope", "state", "material_delta"}
STATES = {"OBSERVED", "HELD", "DORMANT"}
SCOPE = {"PUBLIC_SAFE_SYNTHETIC", "PRIVATE_METADATA_ONLY"}


def _check(record: dict) -> None:
    if not isinstance(record, dict) or set(record) != FIELDS:
        raise ValueError("INVALID_SOURCE_SHAPE")
    for key in ("session_id", "work_id"):
        if not isinstance(record[key], str) or not ID.fullmatch(record[key]):
            raise ValueError("INVALID_ID")
    if record["source_sha256"] is not None and (
        not isinstance(record["source_sha256"], str)
        or not DIGEST.fullmatch(record["source_sha256"])
    ):
        raise ValueError("INVALID_SOURCE_HASH")
    if record["scope"] not in SCOPE or record["state"] not in STATES:
        raise ValueError("INVALID_SCOPE_OR_STATE")
    if type(record["material_delta"]) is not bool:
        raise ValueError("INVALID_DELTA_TYPE")


def reconcile_sources(records: list[dict], *, scanned_scope: str,
                      unscanned_sources: int | None = None) -> dict:
    """Report unresolved/duplicate WorkIDs; no external effect or ACK."""
    if not isinstance(records, list) or len(records) > 1000:
        raise ValueError("INVALID_SCAN_BUDGET")
    if scanned_scope not in {"BOUNDED_SYNTHETIC", "BOUNDED_AUTHORIZED_METADATA"}:
        raise ValueError("INVALID_SCAN_SCOPE")
    if unscanned_sources is not None and (
        type(unscanned_sources) is not int or unscanned_sources < 0
    ):
        raise ValueError("INVALID_UNSCANNED_COUNT")

    sessions = set()
    groups = defaultdict(list)
    for record in records:
        _check(record)
        # Reject duplicated session identities, including non-identical records.
        if record["session_id"] in sessions:
            raise ValueError("DUPLICATE_SESSION_ID")
        sessions.add(record["session_id"])
        groups[record["work_id"]].append(record)

    work = []
    for work_id, rows in sorted(groups.items()):
        known = {x["source_sha256"] for x in rows if x["source_sha256"] is not None}
        missing = any(x["source_sha256"] is None for x in rows)
        held = any(x["state"] == "HELD" for x in rows)
        if len(known) > 1:
            disposition = "HOLD_CONFLICTING_SOURCE_REVISIONS"
        elif missing:
            disposition = "HOLD_MISSING_SOURCE"
        elif held:
            disposition = "HOLD_SOURCE_HELD"
        elif not any(x["material_delta"] for x in rows):
            disposition = "QUIET_NO_MATERIAL_DELTA"
        else:
            disposition = "CANDIDATE_FOR_AUTHORIZED_RECEIVER"
        work.append({
            "work_id": work_id,
            "session_count": len(rows),
            "duplicate_session_sources_collapsed": max(0, len(rows) - 1),
            "disposition": disposition,
            "exact_source_hash": next(iter(known)) if len(known) == 1 and not missing else None,
            "next_safe_action": (
                "VERIFY_SOURCE_AND_REVIEW_CONFLICT" if disposition.startswith("HOLD")
                else "SLEEP_UNTIL_MATERIAL_CHANGE" if disposition.startswith("QUIET")
                else "SEND_ONLY_THROUGH_SEPARATE_AUTHORIZED_RECEIVER"
            ),
            "receiver_readproof": None,
        })
    return {
        "schema": "CoAll.SessionFanIn.BoundedR0",
        "coverage": scanned_scope,
        "observed_session_count": len(sessions),
        "observed_unique_workids": len(work),
        "unscanned_source_count": unscanned_sources,
        "global_session_completeness": "UNKNOWN",
        "work": work,
        "effect": "NONE",
        "external_receivers_contacted": 0,
        "receiver_ack": "NOT_ESTABLISHED",
        "nonclaims": [
            "SOURCE_DUPLICATES_NE_DUPLICATED_WORK",
            "SOURCE_MATCH_NE_CURRENTNESS",
            "CANDIDATE_NE_DISPATCH",
            "LOCAL_RECONCILIATION_NE_RECEIVER_ACK",
            "OBSERVED_SET_NE_COMPLETE_HISTORY",
        ],
    }
