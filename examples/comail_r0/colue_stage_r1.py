"""CoLUE/CoMail outreach staging gate, R1, public-safe and send-disabled.

Decision only.  This module never reads Gmail, creates drafts, sends mail,
contacts recipients, schedules follow-ups, or infers consent. Inputs must be
supplied by an independently authorized mailbox observer.
"""
from __future__ import annotations

from hashlib import sha256
from json import dumps
from re import fullmatch
from typing import Any

HEX = r"[0-9a-f]{64}"
BOOLS = ("route_verified", "thread_verified", "claims_verified", "consent_current",
         "opt_out", "approver_authorized", "inbound_reply_readproof", "outcome_verified",
         "collision_inventory_verified")
FIELDS = ("work_id", "sender_mailbox_id", "connected_mailbox_id", "recipient_ref",
          "thread_ref", "purpose_id", "versions", "approval_sha256", "sent_receipt")


def _id(value: Any) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise ValueError("HOLD_BAD_IDENTITY")
    return value


def _hash(value: Any) -> bool:
    return isinstance(value, str) and fullmatch(HEX, value) is not None


def content_sha256(body: str) -> str:
    """Hash content locally. Never embed bodies in public receipts."""
    if not isinstance(body, str):
        raise ValueError("HOLD_BODY_TYPE")
    return sha256(body.encode("utf-8")).hexdigest()


def validate_versions(versions: Any) -> str:
    if not isinstance(versions, list) or not 1 <= len(versions) <= 100:
        raise ValueError("HOLD_VERSION_HISTORY")
    before = None
    for expected, entry in enumerate(versions):
        if not isinstance(entry, dict) or set(entry) != {
            "revision", "content_sha256", "predecessor_sha256"
        }:
            raise ValueError("HOLD_VERSION_SCHEMA")
        if type(entry["revision"]) is not int or entry["revision"] != expected:
            raise ValueError("HOLD_REVISION_ORDER")
        if not _hash(entry["content_sha256"]):
            raise ValueError("HOLD_CONTENT_HASH")
        if entry["predecessor_sha256"] != before:
            raise ValueError("HOLD_BROKEN_PREDECESSOR")
        if before is not None and entry["content_sha256"] == before:
            raise ValueError("HOLD_NONMATERIAL_REVISION")
        before = entry["content_sha256"]
    return before


def collision_key(case: dict[str, Any]) -> str:
    """Scope dedupe to exact sender/recipient/thread or new-thread purpose."""
    sender, recipient = _id(case["sender_mailbox_id"]), _id(case["recipient_ref"])
    thread = case["thread_ref"]
    purpose = _id(case["purpose_id"])
    if thread is not None:
        target = ("reply", _id(thread))
    else:
        target = ("new", purpose)
    encoded = dumps((sender, recipient, target), separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()


def decision(state: str, next_event: str, case: dict[str, Any], *, revision: str | None = None) -> dict:
    """No private recipient/thread/body bytes in decision output."""
    return {
        "schema": "CoLUE.CoMail.StagedOutreach.R1",
        "state": state,
        "work_sha256": sha256(_id(case["work_id"]).encode("utf-8")).hexdigest(),
        "revision_sha256": revision,
        "collision_sha256": collision_key(case),
        "next_event": next_event,
        "effect": "NONE",
        "authorized_send": False,
        "receiver_ack": False,
        "nonclaims": ["DRAFT_NE_SENT", "SENT_NE_DELIVERED", "REPLY_NE_ADOPTION",
                      "CONNECTED_MAILBOX_NE_OTHER_MAILBOX_AUTHORITY",
                      "PREFLIGHT_PASS_NE_SEND_AUTHORITY"],
    }


def assess(case: dict[str, Any], peers: tuple[dict[str, Any], ...] = ()) -> dict:
    """Choose one fail-closed step. Only metadata; no effects or implicit sends.

    A draft may be advanced by an authorized external effect executor, but the
    returned decision is never an authorization or a send instruction itself.
    """
    if not isinstance(case, dict) or not all(k in case for k in FIELDS + BOOLS):
        raise ValueError("HOLD_PACKET_SCHEMA")
    for field in BOOLS:
        if type(case[field]) is not bool:
            raise ValueError("HOLD_BOOLEAN_FLAG")
    for field in ("work_id", "sender_mailbox_id", "connected_mailbox_id",
                  "recipient_ref", "purpose_id"):
        _id(case[field])
    if case["thread_ref"] is not None:
        _id(case["thread_ref"])
    current = validate_versions(case["versions"])
    if case["approval_sha256"] is not None and not _hash(case["approval_sha256"]):
        raise ValueError("HOLD_APPROVAL_HASH")
    receipt = case["sent_receipt"]
    if receipt is not None:
        if not isinstance(receipt, dict) or set(receipt) != {
            "provider_message_ref", "sender_mailbox_id", "thread_ref", "content_sha256"
        }:
            raise ValueError("HOLD_RECEIPT_SCHEMA")
        if not (_id(receipt["provider_message_ref"])
                and _id(receipt["sender_mailbox_id"]) and _hash(receipt["content_sha256"])):
            raise ValueError("HOLD_RECEIPT_ID")
    if case["opt_out"]:
        return decision("CLOSED_OPT_OUT", "QUIESCE", case, revision=current)
    # Native account identity must be bound before considering a provider receipt.
    if case["sender_mailbox_id"] != case["connected_mailbox_id"]:
        return decision("HOLD_WRONG_MAILBOX", "BIND_CORRECT_ACCOUNT", case, revision=current)
    key = collision_key(case)
    for peer in peers:
        if not isinstance(peer, dict) or any(field not in peer for field in (
            "work_id", "sender_mailbox_id", "recipient_ref", "thread_ref", "purpose_id")):
            raise ValueError("HOLD_PEER_SCHEMA")
        try:
            _id(peer["work_id"])
            if peer["work_id"] == case["work_id"]:
                continue
            peer_key = collision_key(peer)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("HOLD_PEER_SCHEMA") from exc
        if peer_key == key:
            return decision("HOLD_COLLISION", "RECONCILE_PRIOR_THREAD", case, revision=current)
    if receipt is not None:
        # A historical sent snapshot is immutable even after a new unsent
        # successor is created. Do not rewrite it to the latest draft revision.
        historical_hashes = [v["content_sha256"] for v in case["versions"]]
        if (receipt["sender_mailbox_id"] != case["sender_mailbox_id"]
            or receipt["thread_ref"] != case["thread_ref"]
            or receipt["content_sha256"] not in historical_hashes):
            return decision("HOLD_RECEIPT_MISMATCH", "RECONCILE_PROVIDER_SOURCE", case, revision=current)
        if receipt["content_sha256"] != current:
            return decision("SENT_HISTORY_WITH_UNSENT_SUCCESSOR", "REVIEW_NEW_REVISION", case, revision=current)
        if case["outcome_verified"]:
            return decision("OUTCOME_ASSERTED_REQUIRES_INDEPENDENT_PROOF", "VERIFY_OUTCOME", case, revision=current)
        if case["inbound_reply_readproof"]:
            return decision("REPLY_READPROOF_ASSERTED_NOT_INDEPENDENT", "VERIFY_REPLY_THEN_REVIEW", case, revision=current)
        return decision("SENT_RECEIPT_ASSERTED_UNVERIFIED", "VERIFY_PROVIDER_SEND_RECEIPT", case, revision=current)
    if not case["collision_inventory_verified"]:
        return decision("HOLD_COLLISION_INVENTORY", "READ_ACCOUNT_SENT_AND_DRAFTS", case, revision=current)
    if not case["route_verified"]:
        return decision("HOLD_RECIPIENT_ROUTE", "VERIFY_RECIPIENT", case, revision=current)
    if case["thread_ref"] is not None and not case["thread_verified"]:
        return decision("HOLD_LATEST_THREAD", "READ_NATIVE_THREAD", case, revision=current)
    if not case["consent_current"]:
        return decision("HOLD_RELATION_PERMISSION", "VERIFY_PERMISSION", case, revision=current)
    if not case["claims_verified"]:
        return decision("HOLD_EVIDENCE", "VERIFY_CLAIMS", case, revision=current)
    if case["approval_sha256"] != current:
        return decision("REVIEW_REQUIRED_OR_STALE", "REVIEW_EXACT_REVISION", case, revision=current)
    if not case["approver_authorized"]:
        return decision("HOLD_APPROVER_AUTHORITY", "VERIFY_REVIEW_AUTHORITY", case, revision=current)
    return decision("PREFLIGHT_PASS_NO_SEND", "EXTERNAL_SEND_GATE_ONLY", case, revision=current)
