"""Read-only synthetic CoMail staging and CoEv-of-CoEv requalification gate.

No Gmail, network, sender identity, credential, send or receipt authority.
All inputs are public-safe synthetic fixtures. Callers retain historical snapshots.
"""
from __future__ import annotations

import re
from typing import Any

from core import validate

SCHEMA = "CoCivium.CoMail.StageReview.R0"
FIELDS = {
    "schema", "stage_id", "resource_id", "pinned_resource_sha256",
    "pinned_message_sha256", "policy_revision", "current_policy_revision",
    "sender_qualified", "recipient_qualified", "thread_qualified",
    "claims_reviewed", "consent_checked", "delivery", "predecessor_stage_id",
}
HEX = re.compile(r"^[0-9a-f]{64}$")
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")


def evaluate(fixture: dict, stage: dict[str, Any]) -> dict[str, Any]:
    """Return a safe disposition, never authority to send an email."""
    validate(fixture)
    if not isinstance(stage, dict) or set(stage) != FIELDS or stage.get("schema") != SCHEMA:
        raise ValueError("STAGE_SCHEMA_MISMATCH")
    for key in ("stage_id", "policy_revision", "current_policy_revision"):
        if not isinstance(stage[key], str) or not ID.fullmatch(stage[key]):
            raise ValueError("INVALID_" + key.upper())
    parent = stage["predecessor_stage_id"]
    if parent is not None and (not isinstance(parent, str) or not ID.fullmatch(parent) or parent == stage["stage_id"]):
        raise ValueError("INVALID_PREDECESSOR")
    for key in ("pinned_resource_sha256", "pinned_message_sha256"):
        if not isinstance(stage[key], str) or not HEX.fullmatch(stage[key]):
            raise ValueError("INVALID_" + key.upper())
    for key in ("sender_qualified", "recipient_qualified", "thread_qualified",
                "claims_reviewed", "consent_checked"):
        if type(stage[key]) is not bool:
            raise ValueError("INVALID_" + key.upper())
    if stage["delivery"] != "NOT_SENT":
        raise ValueError("STAGE_CANNOT_CLAIM_DELIVERY")
    resource = fixture["resource"]
    message = fixture["fixed_message"]
    reasons = []
    if stage["resource_id"] != resource["resource_id"]:
        reasons.append("RESOURCE_ID_MISMATCH")
    if stage["pinned_message_sha256"] != message["sha256"]:
        reasons.append("HISTORICAL_MESSAGE_MISMATCH")
    if stage["pinned_resource_sha256"] != resource["current_sha256"]:
        reasons.append("SOURCE_REVISION_DRIFT")
    if stage["policy_revision"] != stage["current_policy_revision"]:
        reasons.append("REVIEW_POLICY_EVOLVED")
    for key in ("sender_qualified", "recipient_qualified", "thread_qualified",
                "claims_reviewed", "consent_checked"):
        if not stage[key]:
            reasons.append(key.upper() + "_MISSING")
    return {
        "schema": "CoCivium.CoMail.StageDisposition.R0",
        "stage_id": stage["stage_id"],
        "predecessor_stage_id": parent,
        "source_resource_id": resource["resource_id"],
        "source_current_sha256": resource["current_sha256"],
        "status": "HOLD_FOR_REQUALIFICATION" if reasons else "READY_FOR_EXPLICIT_HUMAN_REVIEW",
        "reasons": reasons,
        "effect": "NONE",
        "delivery": "NOT_SENT",
        "receiver_ack": "UNPROVEN",
        "sender_authority": "NOT_GRANTED",
        "next_wake": "SOURCE_OR_POLICY_CHANGE_OR_VERIFIED_REVIEW" if reasons else "EXPLICIT_HUMAN_SEND_DECISION",
    }
