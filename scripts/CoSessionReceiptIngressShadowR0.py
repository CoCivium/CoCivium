#!/usr/bin/env python3
"""CoFanIn R0 shadow intake: type-check, pin, quarantine. Never admit.

This adapter is not connected to an operational receiver. The supplied
manifest is an ASSERTION by the caller, not an authenticated authority grant.
All candidates remain held pending independently verified authorization,
origin, collision-domain and receiver-origin pickup.
"""
import hashlib
import json
import re

from CoSessionTypedReceiptPreflightR0 import Hold, preflight

SHA256 = re.compile(r"[0-9a-f]{64}\Z")
RECEIPT_SOURCE_ROLE = "SESSION_EFFECT_RECEIPT"
AUDIT_ROLES = {"GUARDIAN_AUDIT", "LEDGER_PROJECTION", "COMPILER_OUTPUT", "CHAT_COPY"}


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _require(condition, code):
    if not condition:
        raise Hold(code)


def shadow_ingress_one(item):
    """Return a source-bound candidate with no authority and zero effects.

    item: {'source_bytes':bytes, 'receipt_bytes':bytes, 'manifest':dict}.
    Manifest pins are independently *required* but not independently verified.
    """
    _require(type(item) is dict, "HOLD_INPUT_ENVELOPE")
    src, raw, manifest = (item.get(k) for k in ("source_bytes", "receipt_bytes", "manifest"))
    _require(type(src) is bytes and type(raw) is bytes and type(manifest) is dict,
             "HOLD_ENVELOPE_TYPES")
    _require(manifest.get("source_role") == RECEIPT_SOURCE_ROLE,
             "HOLD_SOURCE_ROLE_NOT_EFFECT_RECEIPT")
    for field in ("source_sha256", "receipt_sha256"):
        value = manifest.get(field)
        _require(type(value) is str and SHA256.fullmatch(value) is not None,
                 "HOLD_MANIFEST_PIN_" + field.upper())
    _require(_hash(src) == manifest["source_sha256"], "HOLD_MANIFEST_SOURCE_MISMATCH")
    _require(_hash(raw) == manifest["receipt_sha256"], "HOLD_MANIFEST_RECEIPT_MISMATCH")
    try:
        receipt = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise Hold("HOLD_RECEIPT_JSON") from exc
    _require(type(receipt) is dict, "HOLD_RECEIPT_TYPE")
    # The caller must provide a source role *outside* the receipt body.
    # A self-described receipt/audit cannot qualify its own role.
    _require(receipt.get("source_role") == RECEIPT_SOURCE_ROLE,
             "HOLD_RECEIPT_ROLE_MISMATCH")
    for field in ("work_id", "effect_id", "issuer_id", "failure_domain",
                  "authority_ref", "epoch"):
        _require(type(manifest.get(field)) is type(receipt.get(field)) and
                 manifest.get(field) == receipt.get(field),
                 "HOLD_MANIFEST_IDENTITY_" + field.upper())
    out = preflight(src, raw, manifest["receipt_sha256"])
    _require(out["source_sha256"] == manifest["source_sha256"],
             "HOLD_SOURCE_BINDING")
    _require(out["typed_preflight"] == "PASS_SOURCE_BOUND_CANDIDATE_ONLY" and
             out["admission"] == "HOLD_INDEPENDENT_AUTHORITY_AND_RECEIVER",
             "HOLD_UNEXPECTED_PREFLIGHT_STATE")
    return {
        "key": out["identity_key"],
        "effect_key": [receipt["work_id"], receipt["effect_id"], receipt["epoch"]],
        "source_sha256": out["source_sha256"],
        "receipt_sha256": out["receipt_sha256"],
        "state": "TYPED_SOURCE_BOUND_UNAUTHENTICATED_CANDIDATE",
    }


def shadow_ingress_batch(items):
    """Preserve every arrival, collapse exact replay, quarantine collisions.

    Two DIFFERENT receipt identities for the same work/effect/epoch require
    review, even if they claim independent issuers. All counts are preflight
    candidates, never qualified or admitted receipts.
    """
    _require(type(items) is list and 1 <= len(items) <= 30, "HOLD_BATCH_BOUND_1_TO_30")
    observed = []
    by_receipt = {}
    by_effect = {}
    conflicts = set()
    for index, item in enumerate(items):
        try:
            candidate = shadow_ingress_one(item)
        except (Hold, TypeError, KeyError, ValueError) as exc:
            state = str(exc) if isinstance(exc, Hold) else "HOLD_UNEXPECTED_INPUT"
            observed.append({"index": index, "state": state})
            continue
        rid = tuple(candidate["key"])
        ekey = tuple(candidate["effect_key"])
        prior = by_receipt.get(rid)
        identity = (candidate["source_sha256"], candidate["receipt_sha256"])
        if prior is not None:
            if prior == identity:
                state = "EXACT_RECEIPT_REPLAY_NO_NEW_CANDIDATE"
            else:
                conflicts.add(ekey)
                state = "HOLD_RECEIPT_BODY_COLLISION"
        else:
            by_receipt[rid] = identity
            first_for_effect = by_effect.get(ekey)
            if first_for_effect is not None and first_for_effect != rid:
                conflicts.add(ekey)
                state = "HOLD_SAME_EFFECT_DIFFERENT_RECEIPT"
            else:
                by_effect[ekey] = rid
                state = "NEW_TYPED_REVIEW_CANDIDATE"
        observed.append({"index": index, "state": state,
                         "effect_key": list(ekey), "receipt_sha256": candidate["receipt_sha256"]})
    no_conflict = sum(ekey not in conflicts for ekey in by_effect)
    return {
        "schema": "CoSession.ShadowIngressResult.R0",
        "observations": observed,
        "distinct_receipt_identifiers_seen": len(by_receipt),
        "unconflicted_effect_candidates": no_conflict,
        "conflicting_effect_groups": len(conflicts),
        "qualified_receipts": 0,
        "independent_receiver_acks": 0,
        "master_elections": 0,
        "fanout": "HOLD",
        "authority": "NONE_RESEARCH_ONLY",
        "external_effects": 0,
        "nonclaims": [
            "MANIFEST_ASSERTION_NE_AUTHENTICATED_ISSUER",
            "SOURCE_ROLE_LABEL_NE_SOURCE_PROVENANCE",
            "PRECHECK_NE_RECEIVER_ACK",
            "TYPED_CANDIDATE_NE_QUALIFIED_RECEIPT",
            "TWO_CLAIMED_ISSUERS_NE_INDEPENDENT_VALIDATORS",
            "CONFLICT_QUARANTINE_NE_ERASED_DISSENT",
            "ONE_LOGICAL_EFFECT_NE_ELECTED_MASTER",
        ],
    }
