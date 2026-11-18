#!/usr/bin/env python3
"""Offline typed *preflight* for source-bound candidate receipts.

Never admits a receiver, elects a master, publishes, or authorizes effects.
Its result can only be HOLD or a typed candidate requiring independent proof.
"""
import hashlib
import json
import re
from datetime import datetime

from CoSessionRelationalFanIn import expand_payload, validate_delta

HEX64 = re.compile(r"[0-9a-f]{64}\Z")
IDENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/+-]{0,127}\Z")
AUTHORITY_CEILINGS = {"CANDIDATE_ONLY", "READ_ONLY", "PRIVATE_ONLY", "LOCAL_ZERO_EFFECT_CANARY"}


class Hold(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise Hold(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(value):
    return type(value) is str and IDENT.fullmatch(value) is not None


def utc(value):
    require(type(value) is str and value.endswith("Z"), "HOLD_TIME_NOT_UTC")
    try:
        dt = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise Hold("HOLD_TIME_INVALID") from exc
    require(dt.tzinfo is not None and dt.utcoffset().total_seconds() == 0, "HOLD_TIME_NOT_UTC")
    return dt


def preflight(source_bytes, receipt_bytes, expected_receipt_sha256):
    """Bind exact source bytes to an exact candidate receipt, then HOLD authority.

    The expected receipt digest must be independently pinned by the caller;
    matching it is integrity evidence, not authentic signer/receiver evidence.
    """
    require(type(source_bytes) is bytes and type(receipt_bytes) is bytes,
            "HOLD_BYTES_REQUIRED")
    require(type(expected_receipt_sha256) is str and HEX64.fullmatch(expected_receipt_sha256),
            "HOLD_RECEIPT_PIN_FORMAT")
    receipt_hash = digest(receipt_bytes)
    require(receipt_hash == expected_receipt_sha256, "HOLD_RECEIPT_BYTES_CHANGED")
    try:
        receipt = json.loads(receipt_bytes.decode("utf-8"))
        records = expand_payload(json.loads(source_bytes.decode("utf-8")))
    except (ValueError, UnicodeDecodeError, TypeError) as exc:
        raise Hold("HOLD_SOURCE_OR_RECEIPT_JSON") from exc
    require(type(receipt) is dict and type(records) is list, "HOLD_RECORD_SHAPE")
    require(receipt.get("schema") == "CoSession.TypedReceiptCandidate.R0", "HOLD_RECEIPT_SCHEMA")
    for field in ("work_id", "effect_id", "receipt_id", "issuer_id", "failure_domain",
                  "source_revision", "authority_ref", "source_delta_id"):
        require(identity(receipt.get(field)), "HOLD_IDENTITY_" + field.upper())
    require(type(receipt.get("epoch")) is int and receipt["epoch"] > 0, "HOLD_EPOCH")
    idx = receipt.get("source_record_index")
    require(type(idx) is int and 0 <= idx < len(records), "HOLD_SOURCE_RECORD_INDEX")
    expected_source = receipt.get("source_sha256")
    require(type(expected_source) is str and HEX64.fullmatch(expected_source), "HOLD_SOURCE_PIN_FORMAT")
    require(expected_source == digest(source_bytes), "HOLD_SOURCE_BYTES_CHANGED")
    delta = records[idx]
    try:
        reason = validate_delta(delta)
    except (ValueError, TypeError, KeyError) as exc:
        raise Hold("HOLD_BASE_COMPILER_VALIDATION") from exc
    require(reason is None, "HOLD_BASE_COMPILER_VALIDATION")
    require(type(delta.get("delta_id")) is str and identity(delta["delta_id"]), "HOLD_DELTA_ID")
    require(receipt["source_delta_id"] == delta["delta_id"], "HOLD_DELTA_SOURCE_BINDING")
    require(identity(delta.get("source_session")), "HOLD_SOURCE_SESSION")
    created = utc(delta.get("created_at"))
    observed = utc(receipt.get("observed_at"))
    require(observed >= created, "HOLD_RECORDED_BEFORE_SOURCE")
    require(type(delta.get("target_domains")) is list and
            all(identity(v) for v in delta["target_domains"]), "HOLD_DOMAIN_TYPES")
    for op in delta["operations"]:
        require(type(op) is dict and identity(op.get("subject")) and identity(op.get("relation")),
                "HOLD_OPERATION_IDENTITY")
        refs = op.get("evidence_refs", [])
        require(type(refs) is list and all(type(r) is str and r for r in refs),
                "HOLD_OPERATION_EVIDENCE_REFS")
    require(type(delta.get("authority_ceiling")) is str and
            delta["authority_ceiling"] in AUTHORITY_CEILINGS, "HOLD_AUTHORITY_CEILING")
    nc = delta.get("nonclaims")
    require(type(nc) is list and bool(nc) and all(type(x) is str and x for x in nc),
            "HOLD_NONCLAIMS")
    require(identity(delta.get("next_gate")), "HOLD_NEXT_GATE")
    require(receipt.get("receiver_origin_ack") == "NOT_ESTABLISHED" and
            receipt.get("master_elected") is False and
            receipt.get("publish_authorized") is False, "HOLD_FORGED_EFFECT_OR_ACK")
    key = (receipt["work_id"], receipt["effect_id"], receipt["receipt_id"],
           receipt["issuer_id"], receipt["epoch"])
    return {
        "identity_key": list(key),
        "source_sha256": expected_source,
        "receipt_sha256": receipt_hash,
        "typed_preflight": "PASS_SOURCE_BOUND_CANDIDATE_ONLY",
        "admission": "HOLD_INDEPENDENT_AUTHORITY_AND_RECEIVER",
        "receiver_origin_ack": False,
        "master_elected": False,
        "public_release": False,
        "external_effects": 0,
    }


def batch_preflight(items):
    """Retain all observations; replay-count once, collision-count zero.

    items: iterable of (source_bytes, receipt_bytes, expected_receipt_digest).
    Never mutates either input or external state.
    """
    seen = {}
    observations = []
    collisions = set()
    effect_receipt_identities = {}
    for source_bytes, receipt_bytes, pin in items:
        try:
            candidate = preflight(source_bytes, receipt_bytes, pin)
        except Hold as exc:
            observations.append({"state": str(exc), "receipt_sha256": digest(receipt_bytes)
                                 if type(receipt_bytes) is bytes else None})
            continue
        key = tuple(candidate["identity_key"])
        # A distinct receipt or issuer for an identical WorkID/effect/epoch
        # is different evidence, not independently approved extra effect.
        effect_key = (key[0], key[1], key[4])
        effect_receipt_identities.setdefault(effect_key, set()).add((key[2], key[3]))
        prior = seen.get(key)
        if prior is None:
            seen[key] = candidate
            state = "NEW_TYPED_CANDIDATE"
        elif (prior["source_sha256"], prior["receipt_sha256"]) == (
                candidate["source_sha256"], candidate["receipt_sha256"]):
            state = "EXACT_REPLAY_NO_NEW_RECEIPT"
        else:
            collisions.add(key)
            state = "HOLD_RECEIPT_IDENTITY_COLLISION"
        observations.append({"state": state, "identity_key": list(key),
                             "receipt_sha256": candidate["receipt_sha256"]})
    # Final adjudication is order-independent: late receipts can downgrade
    # earlier candidates. Preserve original arrival states for audit.
    effect_collisions = {
        effect_key for effect_key, receipts in effect_receipt_identities.items()
        if len(receipts) > 1
    }
    for observation in observations:
        identity_key = observation.get("identity_key")
        if identity_key is None:
            continue
        if (identity_key[0], identity_key[1], identity_key[4]) in effect_collisions:
            observation["pre_effect_review_state"] = observation["state"]
            observation["state"] = "HOLD_UNADJUDICATED_EFFECT_MULTI_RECEIPT"
    return {
        "source_observations": observations,
        "typed_candidates_unconflicted": sum(
            key not in collisions and (key[0], key[1], key[4]) not in effect_collisions
            for key in seen
        ),
        "collision_groups": len(collisions),
        "effect_collision_groups": len(effect_collisions),
        "qualified_receipts": 0,
        "receiver_origin_acks": 0,
        "elected_masters": 0,
        "fanout": "HOLD",
        "external_effects": 0,
        "nonclaims": ["TYPED_NE_AUTHENTICATED", "EXACT_REPLAY_NE_INDEPENDENT_RECEIPT",
                      "REVIEW_NE_ADMISSION", "SOURCE_HASH_NE_RECEIVER_ACK",
                      "MULTI_RECEIPT_SAME_EFFECT_NE_QUORUM_OR_MASTER"],
    }
