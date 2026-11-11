"""CoLUE+ public-safe outreach staging gate.

This module only evaluates a snapshot supplied by an authorized observer.
It never reads Gmail, sends, subscribes, posts, or infers recipient consent.
Personal identifiers should not be supplied to public fixture data.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

SHA256 = re.compile(r"[0-9a-f]{64}\Z")


@dataclass(frozen=True)
class DraftEvidence:
    work_id: str
    draft_id: str
    draft_mailbox_id: str
    connected_mailbox_id: str
    source_revision: str
    current_source_revision: str
    content_sha256: str
    recipient_route_ref: str | None = None
    recipient_route_verified: bool = False
    relationship_provenance_ref: str | None = None
    sender_authorized_for_mailbox: bool = False
    thread_or_new_route_verified: bool = False
    latest_thread_and_sent_checked: bool = False
    duplicate_outreach_checked: bool = False
    consent_or_lawful_basis_ref: str | None = None
    opt_out: bool = False
    factual_claims_reviewed: bool = False
    reviewed_content_sha256: str | None = None
    approved_content_sha256: str | None = None
    specific_send_authority_ref: str | None = None


def evaluate(draft: DraftEvidence) -> dict:
    """Return a bounded, privacy-minimal gate, never a provider action.

    Approvals and even a separately asserted send authority remain candidates
    until a distinct authorized provider action/receipt occurs.
    """
    if not isinstance(draft, DraftEvidence):
        raise TypeError("DraftEvidence required")
    text_ids = (draft.work_id, draft.draft_id, draft.draft_mailbox_id,
                draft.connected_mailbox_id, draft.source_revision,
                draft.current_source_revision)
    if not all(isinstance(v, str) and v.strip() for v in text_ids):
        raise ValueError("bound work/draft/account/source IDs required")
    if not isinstance(draft.content_sha256, str) or not SHA256.fullmatch(draft.content_sha256):
        raise ValueError("canonical content SHA-256 required")
    truth_fields = (
        "recipient_route_verified", "sender_authorized_for_mailbox",
        "thread_or_new_route_verified", "latest_thread_and_sent_checked",
        "duplicate_outreach_checked", "opt_out", "factual_claims_reviewed",
    )
    if any(type(getattr(draft, name)) is not bool for name in truth_fields):
        raise ValueError("invalid boolean evidence assertion")

    holds = []
    if draft.draft_mailbox_id != draft.connected_mailbox_id:
        holds.append("HOLD_WRONG_MAILBOX")
    if draft.source_revision != draft.current_source_revision:
        holds.append("HOLD_SOURCE_REVISION_CHANGED")
    if not draft.recipient_route_ref or not draft.recipient_route_verified:
        holds.append("HOLD_RECIPIENT_ROUTE")
    if not draft.relationship_provenance_ref:
        holds.append("HOLD_RELATION_PROVENANCE")
    if not draft.sender_authorized_for_mailbox:
        holds.append("HOLD_SENDER_AUTHORITY")
    if not draft.thread_or_new_route_verified or not draft.latest_thread_and_sent_checked:
        holds.append("HOLD_THREAD_CONTEXT")
    if not draft.duplicate_outreach_checked:
        holds.append("HOLD_DUPLICATE_CHECK")
    if draft.opt_out:
        holds.append("HOLD_OPTOUT")
    if not draft.consent_or_lawful_basis_ref:
        holds.append("HOLD_CONSENT_OR_LAWFUL_BASIS")
    if not draft.factual_claims_reviewed:
        holds.append("HOLD_FACTUAL_CLAIMS")
    if draft.reviewed_content_sha256 != draft.content_sha256:
        holds.append("HOLD_REVIEW_STALE_OR_ABSENT")
    if draft.approved_content_sha256 != draft.content_sha256:
        holds.append("HOLD_APPROVAL_STALE_OR_ABSENT")
    if not draft.specific_send_authority_ref:
        holds.append("HOLD_SPECIFIC_SEND_AUTHORITY")

    return {
        "schema": "CoLUE.OutreachStageGate.R0",
        "work_id": draft.work_id,
        "draft_id": draft.draft_id,
        "state": "STAGED_HELD" if holds else "PROVIDER_SEND_CANDIDATE_NOT_SENT",
        "holds": holds,
        "next_safe_action": holds[0] if holds else "REQUIRE_SEPARATE_PROVIDER_EFFECT_AND_RECEIPT",
        "content_sha256": draft.content_sha256,
        "observed_effect": "NONE",
        "sender_provider_receipt": None,
        "delivery_verified": False,
        "read_verified": False,
        "receiver_acceptance_verified": False,
        "input_evidence_status": "CALLER_ASSERTIONS_NOT_INDEPENDENTLY_READ_BACK",
        "nonclaims": [
            "DRAFT_NE_SENT", "APPROVAL_NE_PROVIDER_SEND",
            "SENT_NE_DELIVERED", "DELIVERED_NE_READ",
            "READ_NE_AGREED", "SCREENSHOT_NE_NATIVE_MAILBOX_BINDING",
            "CONNECTED_ACCOUNT_NE_OTHER_ACCOUNT_AUTHORITY",
        ],
    }


def propose_evolution(draft: DraftEvidence, *, proposed_content_sha256: str,
                      change_kind: str, depth: int, budget: int = 4) -> tuple[DraftEvidence, dict]:
    """Produce one *unapplied* bounded Turtle successor, never a provider draft edit.

    The predecessor remains immutable. A proposed change invalidates editorial
    review, approval and any specific authority for that exact content. Reuse
    the old WorkID/source revision; a changed external source must be rebound
    independently before candidate evolution can resume.
    """
    from dataclasses import replace
    from hashlib import sha256

    evaluate(draft)  # Validate snapshot shape and evidence flags, no effects.
    if type(depth) is not int or type(budget) is not int or not (0 <= depth <= budget <= 8):
        raise ValueError("bounded nonnegative Turtle depth required")
    if change_kind not in {"CLAIM_CORRECTION", "ACCESSIBILITY", "CONTEXT_UPDATE",
                           "CHALLENGE", "RETRACTION", "PROJECTION_EXPERIMENT"}:
        raise ValueError("typed change purpose required")
    if not isinstance(proposed_content_sha256, str) or not SHA256.fullmatch(proposed_content_sha256):
        raise ValueError("new exact content digest required")
    basis = {
        "schema": "CoLUE.BoundedEvolution.R0",
        "work_sha256": sha256(draft.work_id.encode("utf-8")).hexdigest(),
        "parent_content_sha256": draft.content_sha256,
        "source_revision": draft.source_revision,
        "candidate_sha256": proposed_content_sha256,
        "reason": change_kind,
        "depth": depth,
        "budget": budget,
        "effect": "NONE",
        "provider_draft_edited": False,
        "recipient_contacted": False,
        "receiver_ack": False,
        "nonclaims": ["PROPOSAL_NE_PROVIDER_DRAFT", "TURTLE_NE_AUTHORITY",
                      "SOURCE_REVISION_NE_RECEIVER_CURRENTNESS"],
    }
    if draft.source_revision != draft.current_source_revision:
        return draft, {**basis, "state": "HOLD_UPSTREAM_SOURCE_DRIFT", "next_event": "REBIND_SOURCE"}
    if proposed_content_sha256 == draft.content_sha256:
        return draft, {**basis, "state": "QUIESCE_NO_MATERIAL_CHANGE", "next_event": "WAIT_FOR_NEW_EVIDENCE"}
    if depth >= budget:
        return draft, {**basis, "state": "QUIESCE_TURTLE_BUDGET", "next_event": "REVIEW_BUDGET"}
    successor = replace(draft, content_sha256=proposed_content_sha256,
                        reviewed_content_sha256=None, approved_content_sha256=None,
                        specific_send_authority_ref=None)
    # No mutation or authorization is performed by this function.
    return successor, {
        **basis,
        "state": "SUCCESSOR_PROPOSED_UNAPPLIED",
        "depth": depth + 1,
        "next_event": "REVIEW_EXACT_SUCCESSOR_DIGEST",
        "approval_reset": True,
    }
