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


# Exact-byte synthetic receipt fan-in: NEVER a session-provider or Vault reader.
# This optional review gate complements session-source metadata reconciliation.
# It cannot authenticate senders or underlying source bytes by itself.
import hashlib
import json

RECEIPT_FIELDS = {
    "schema", "receipt_id", "source_claim_id", "work_id", "source_sha256",
    "privacy", "state", "effect_count", "receiver_ack", "master_authorized",
}
RECEIPT_SCHEMA = "CoAll.FanIn.SourceOnlyReceipt.R0"
RECEIPT_TARGET = 30


def _object_without_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("HOLD_DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _bounded_receipt(raw):
    if not isinstance(raw, bytes) or not (2 <= len(raw) <= 4096):
        raise ValueError("HOLD_RECEIPT_BYTES_OR_SIZE")
    try:
        data = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_object_without_duplicate_keys,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("HOLD_INVALID_RECEIPT_JSON") from exc
    if not isinstance(data, dict) or set(data) != RECEIPT_FIELDS:
        raise ValueError("HOLD_RECEIPT_SCHEMA_FIELDS")
    if data["schema"] != RECEIPT_SCHEMA:
        raise ValueError("HOLD_RECEIPT_SCHEMA_ID")
    for key in ("receipt_id", "source_claim_id", "work_id"):
        if not isinstance(data[key], str) or not ID.fullmatch(data[key]):
            raise ValueError("HOLD_RECEIPT_IDENTITY")
    if not isinstance(data["source_sha256"], str) or not DIGEST.fullmatch(
        data["source_sha256"]
    ):
        raise ValueError("HOLD_SOURCE_HASH_HINT")
    if (data["privacy"] != "SYNTHETIC_PUBLIC_SAFE"
            or data["state"] != "OBSERVED_SOURCE_ONLY"
            or type(data["effect_count"]) is not int
            or data["effect_count"] != 0
            or data["receiver_ack"] is not False
            or data["master_authorized"] is not False):
        raise ValueError("HOLD_UNQUALIFIED_EFFECT_OR_AUTHORITY")
    return data


def reconcile_receipt_blobs(receipt_blobs: list[bytes]) -> dict:
    """Thirty exact synthetic receipts -> at most ONE review candidate, no master.

    Duplicate receipt *bytes* do not earn extra votes.  Session/source IDs are
    self-asserted metadata, not authentication.  The source hash is a hint,
    not proof that the corresponding underlying source was fetched.
    """
    if not isinstance(receipt_blobs, list) or len(receipt_blobs) > 1000:
        raise ValueError("HOLD_RECEIPT_SCAN_BUDGET")
    by_digest = {}
    for raw in receipt_blobs:
        data = _bounded_receipt(raw)
        digest = hashlib.sha256(raw).hexdigest()
        by_digest.setdefault(digest, data)

    by_receipt_id = {}
    by_claim_id = {}
    work_ids, source_hints = set(), set()
    holds = set()
    for digest, data in sorted(by_digest.items()):
        rid, sid = data["receipt_id"], data["source_claim_id"]
        if rid in by_receipt_id and by_receipt_id[rid] != digest:
            holds.add("HOLD_RECEIPT_ID_REUSED_WITH_DIFFERENT_BYTES")
        if sid in by_claim_id and by_claim_id[sid] != digest:
            holds.add("HOLD_SOURCE_CLAIM_HAS_MULTIPLE_RECEIPTS")
        by_receipt_id[rid] = digest
        by_claim_id[sid] = digest
        work_ids.add(data["work_id"])
        source_hints.add(data["source_sha256"])

    if len(by_digest) != RECEIPT_TARGET:
        holds.add("HOLD_NOT_30_UNIQUE_RECEIPT_BYTES")
    if len(by_claim_id) != RECEIPT_TARGET:
        holds.add("HOLD_NOT_30_DISTINCT_SELF_ASSERTED_CLAIMS")
    if len(work_ids) != 1:
        holds.add("HOLD_WORKID_FORK_OR_MISSING")
    if len(source_hints) != 1:
        holds.add("HOLD_SOURCE_REVISION_FORK_OR_MISSING")

    candidate = not holds
    return {
        "schema": "CoAll.ReceiptFanIn.SourceOnlyReview.R0",
        "state": (
            "ONE_REVIEW_CANDIDATE_NO_MASTER_COMMIT" if candidate
            else "HOLD"
        ),
        "observed_receipt_inputs": len(receipt_blobs),
        "unique_receipt_bytes": len(by_digest),
        "duplicate_receipt_inputs_collapsed": len(receipt_blobs) - len(by_digest),
        "self_asserted_source_claims": len(by_claim_id),
        "sender_authentication": "NOT_ESTABLISHED",
        "source_bytes_independently_read": False,
        "unique_workids": len(work_ids),
        "source_revision_hint_variants": len(source_hints),
        "work_id_hint": next(iter(work_ids)) if len(work_ids) == 1 else None,
        "receipt_sha256s": sorted(by_digest),
        "review_candidates": int(candidate),
        "committed_masters": 0,
        "vault_master_readproof": False,
        "ledger_writes": 0,
        "effect_count": 0,
        "fanout": "HOLD",
        "receiver_ack": "NOT_ESTABLISHED",
        "three_independent_witnesses": "HOLD_DIM",
        "global_session_completeness": "UNKNOWN",
        "holds": sorted(holds),
        "nonclaims": [
            "30_SELF_ASSERTED_SOURCE_CLAIMS_NE_30_AUTHENTICATED_SESSIONS",
            "EXACT_RECEIPT_HASH_NE_SIGNED_RECEIVER_ACK",
            "SOURCE_HASH_HINT_NE_FETCHED_VERIFIED_SOURCE",
            "SINGLE_REVIEW_CANDIDATE_NE_VAULT_OR_LEDGER_MASTER",
            "SYNTHETIC_FANIN_NE_PROVIDER_SESSION_ACCESS",
            "RECEIPT_DEDUP_NE_SOURCE_MERGE_OR_FANOUT",
        ],
    }
