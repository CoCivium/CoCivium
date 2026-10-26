#!/usr/bin/env python3
"""CoOutreach+ R0: fail-closed declared-envelope preflight (no send capability).

Checks a review packet's internal consistency. Cannot authenticate an email
provider, consent, human identity, source content, or actual mail delivery.
All references to private evidence must be opaque; keep PII in private custody.
"""
import argparse
import hashlib
import json
import re
import sys

MAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
KINDS = {"to", "cc", "bcc"}
ACTORS = {"HUMAN", "AI_ASSISTED_HUMAN", "AUTHORIZED_SERVICE"}


def recipient_digest(recipients):
    # Header kind matters; duplicates and casing must not disappear silently.
    rows = sorted(f"{r['kind'].lower()}:{r['address'].lower()}" for r in recipients)
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


def validate(packet):
    errors = []

    def require(ok, tag):
        if not ok:
            errors.append(tag)

    if not isinstance(packet, dict):
        return {"state": "HOLD", "reasons": ["PACKET_NOT_OBJECT"], "effect": "NONE"}
    sender = packet.get("sender") or {}
    message = packet.get("message") or {}
    review = packet.get("review") or {}
    recipients = packet.get("recipients") or []
    require(packet.get("intent") == "ONE_OUTBOUND_MESSAGE_REVIEW", "WRONG_INTENT")
    require(isinstance(sender, dict), "SENDER_MALFORMED")
    require(isinstance(message, dict), "MESSAGE_MALFORMED")
    require(isinstance(review, dict), "REVIEW_MALFORMED")
    require(isinstance(recipients, list) and len(recipients) > 0, "NO_RECIPIENTS")
    if not isinstance(sender, dict): sender = {}
    if not isinstance(message, dict): message = {}
    if not isinstance(review, dict): review = {}
    if not isinstance(recipients, list): recipients = []

    mailbox = sender.get("authenticated_mailbox")
    require(isinstance(mailbox, str) and bool(MAIL.fullmatch(mailbox)), "MAILBOX_IDENTITY_MISSING")
    require(mailbox == sender.get("from_header"), "FROM_MAILBOX_MISMATCH")
    require(bool(sender.get("mailbox_proof_ref")), "NO_MAILBOX_ACCOUNT_PROOF_POINTER")
    require(bool(sender.get("account_principal")), "UNBOUND_ACCOUNT_PRINCIPAL")
    require(bool(sender.get("actual_actor")), "UNBOUND_ACTOR")
    require(sender.get("actor_kind") in ACTORS, "ACTOR_KIND_UNVERIFIED")
    require(bool(sender.get("authoritative_actor_proof_ref")), "NO_ACTOR_PROOF_POINTER")
    if sender.get("actor_kind") != "HUMAN":
        require(bool(sender.get("delegation_proof_ref")), "NO_AGENT_DELEGATION_PROOF_POINTER")
    require(not sender.get("claims_ai_unaccountable_for_account"), "FALSE_AI_ACCOUNTABILITY_CLAIM")

    digest = message.get("body_sha256")
    require(isinstance(digest, str) and bool(SHA256.fullmatch(digest)), "BODY_HASH_MISSING")
    require(digest == review.get("reviewed_body_sha256"), "REVIEWED_BODY_CHANGED")
    require(bool(message.get("top_level_author")), "TOP_LEVEL_AUTHOR_MISSING")
    require(message.get("top_level_author") == sender.get("actual_actor"), "TOP_LEVEL_AUTHOR_ACTOR_MISMATCH")
    require(message.get("quotes_distinguished") is True, "QUOTE_AUTHORSHIP_NOT_SEPARATED")
    require(message.get("claims_reviewed") is True, "CLAIMS_NOT_REVIEWED")
    require(message.get("attachments_reviewed") is True, "ATTACHMENTS_NOT_REVIEWED")
    require(message.get("thread_context_checked") is True, "THREAD_CONTEXT_UNVERIFIED")
    require(message.get("message_mode") in ("new", "reply"), "MESSAGE_MODE_UNKNOWN")
    if message.get("message_mode") == "reply":
        require(bool(message.get("reply_parent_message_id")), "REPLY_PARENT_UNVERIFIED")
    require(review.get("headers_preflight_checked") is True, "HEADERS_NOT_REVIEWED")
    require(bool(review.get("reviewer_identity_proof_ref")), "HUMAN_REVIEWER_NOT_VERIFIED")
    require(review.get("human_approved") is True, "HUMAN_APPROVAL_MISSING")
    require(review.get("bcc_explicitly_reviewed") is True, "BCC_NOT_REVIEWED")

    seen = set()
    for i, recipient in enumerate(recipients):
        if not isinstance(recipient, dict):
            errors.append(f"RECIPIENT_{i}_MALFORMED")
            continue
        address = recipient.get("address")
        kind = recipient.get("kind")
        require(kind in KINDS, f"RECIPIENT_{i}_HEADER_KIND_UNKNOWN")
        require(isinstance(address, str) and bool(MAIL.fullmatch(address)), f"RECIPIENT_{i}_ADDRESS_UNKNOWN")
        if isinstance(address, str) and kind in KINDS:
            key = kind.lower() + ":" + address.lower()
            require(key not in seen, f"RECIPIENT_{i}_DUPLICATE")
            seen.add(key)
        require(recipient.get("identity_verified") is True, f"RECIPIENT_{i}_IDENTITY_UNVERIFIED")
        require(recipient.get("contact_state") == "CLEAR", f"RECIPIENT_{i}_CONTACT_NOT_CLEAR")
        require(recipient.get("explicit_stop_request") is False, f"RECIPIENT_{i}_OPT_OUT")
        require(bool(recipient.get("private_suppression_check_ref")), f"RECIPIENT_{i}_NO_SUPPRESSION_READPROOF")
        require(bool(recipient.get("contact_basis_ref")), f"RECIPIENT_{i}_NO_CONTACT_BASIS")
        require(recipient.get("content_fit_reviewed") is True, f"RECIPIENT_{i}_MESSAGE_FIT_UNREVIEWED")

    try:
        expected = recipient_digest(recipients)
    except (KeyError, AttributeError, TypeError):
        expected = None
    require(expected is not None and expected == review.get("reviewed_recipients_sha256"), "REVIEWED_RECIPIENTS_CHANGED")

    # Deliberately never returns SENT, DELIVERED, APPROVED_TO_SEND, or ACK.
    return {
        "state": "HOLD" if errors else "STRUCTURALLY_REVIEWABLE_ONLY",
        "reasons": errors,
        "effect": "NONE",
        "provider_identity_and_consent_cryptographic_verification": "NOT_PERFORMED",
        "real_world_send_authority": "SEPARATE_LIVE_GATE_REQUIRED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", help="Review packet JSON path")
    args = parser.parse_args()
    with open(args.packet, "r", encoding="utf-8") as f:
        packet = json.load(f)
    report = validate(packet)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["state"] == "STRUCTURALLY_REVIEWABLE_ONLY" else 1


if __name__ == "__main__":
    sys.exit(main())
