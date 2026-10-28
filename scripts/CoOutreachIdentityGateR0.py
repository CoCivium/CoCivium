#!/usr/bin/env python3
"""CoOutreach R0: offline, send-free identity and audience review.

Every positive result means a draft may be reviewed, NOT that its contacts,
sender credentials, consent, thread membership, or claimed approvals are true.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "CoOutreach.IdentityRouteEnvelope.R0"
EMAIL = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+$")
PERMISSION_BASES = {"OPT_IN", "EXISTING_THREAD", "APPROVED_ONE_OFF"}
ROLES = ("to", "cc", "bcc")
REPLY_MODES = {"NEW", "REPLY", "REPLY_ALL", "FORWARD", "GROUP"}
PRIVACY_CLASSES = {"PUBLIC", "PRIVATE", "RESTRICTED"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def field(value, key, default=None):
    return value.get(key, default) if isinstance(value, dict) else default


def nonblank(value):
    return isinstance(value, str) and bool(value.strip()) and value == value.strip()


def address(value):
    return bool(isinstance(value, str) and EMAIL.fullmatch(value) and len(value) <= 254)


def validate(envelope):
    """No outgoing calls or file writes. Returns fail-closed observations."""
    issues = set()
    if not isinstance(envelope, dict):
        return {"state": "HELD", "issue_codes": ["ENVELOPE_NOT_OBJECT"],
                "send_status": "NOT_SENT", "external_effects": 0}

    if field(envelope, "schema") != SCHEMA:
        issues.add("SCHEMA_MISMATCH")
    if field(envelope, "channel") != "EMAIL":
        issues.add("UNSUPPORTED_CHANNEL")
    if not nonblank(field(envelope, "message_id")):
        issues.add("MISSING_MESSAGE_ID")
    if not nonblank(field(envelope, "purpose")):
        issues.add("MISSING_PURPOSE")
    sender = field(envelope, "sender", {})
    sender_id = field(sender, "person_id")
    sending_address = field(sender, "from_address")
    account = field(sender, "authenticated_account")
    if not all(nonblank(field(sender, k)) for k in
               ("person_id", "display_name", "identity_source_ref", "account_source_ref")):
        issues.add("SENDER_IDENTITY_UNBOUND")
    if not address(sending_address) or not address(account):
        issues.add("SENDER_ADDRESS_INVALID")
    elif sending_address.casefold() != account.casefold() and not nonblank(
            field(sender, "send_as_proof_ref")):
        issues.add("UNVERIFIED_SEND_AS")
    if not isinstance(field(sender, "reply_to_address", None), (str, type(None))):
        issues.add("REPLY_TO_INVALID")
    elif field(sender, "reply_to_address") is not None:
        reply_to = field(sender, "reply_to_address")
        if not address(reply_to) or not nonblank(field(sender, "reply_to_authority_ref")):
            issues.add("UNVERIFIED_REPLY_TO")

    audience = field(envelope, "audience", {})
    if not isinstance(audience, dict):
        audience = {}
        issues.add("AUDIENCE_INVALID")
    recipients = []
    for group in ROLES:
        entries = field(audience, group, None)
        if not isinstance(entries, list):
            issues.add("AUDIENCE_GROUP_INVALID")
            continue
        for person in entries:
            if not isinstance(person, dict):
                issues.add("RECIPIENT_INVALID")
                continue
            recipients.append((group, person))
            if not all(nonblank(field(person, k)) for k in
                       ("person_id", "display_name", "identity_source_ref",
                        "route_source_ref", "permission_source_ref")):
                issues.add("RECIPIENT_IDENTITY_UNBOUND")
            if not address(field(person, "address")):
                issues.add("RECIPIENT_ADDRESS_INVALID")
            if field(person, "permission_basis") not in PERMISSION_BASES:
                issues.add("RECIPIENT_PERMISSION_UNBOUND")
            if nonblank(sender_id) and field(person, "person_id") == sender_id:
                issues.add("SELF_ROUTING_REQUIRES_SEPARATE_REVIEW")
    if not recipients:
        issues.add("NO_RECIPIENTS")
    if not field(audience, "to", []):
        issues.add("NO_TO_RECIPIENT")
    actual_ids = [field(p, "person_id") for _, p in recipients if nonblank(field(p, "person_id"))]
    declared = field(envelope, "intended_recipient_ids", None)
    if not isinstance(declared, list) or not all(nonblank(p) for p in declared):
        issues.add("INTENDED_AUDIENCE_INVALID")
    elif set(declared) != set(actual_ids) or len(declared) != len(actual_ids):
        issues.add("INTENDED_ACTUAL_AUDIENCE_MISMATCH")
    if len(actual_ids) != len(set(actual_ids)):
        issues.add("DUPLICATE_PERSON_ACROSS_RECIPIENTS")
    valid_addresses = [field(p, "address").casefold() for _, p in recipients
                       if address(field(p, "address"))]
    if len(valid_addresses) != len(set(valid_addresses)):
        issues.add("DUPLICATE_ADDRESS_ACROSS_RECIPIENTS")
    # One display name can refer to different people. A human must disambiguate.
    names = {}
    for _, p in recipients:
        name, pid = field(p, "display_name"), field(p, "person_id")
        if nonblank(name) and nonblank(pid):
            names.setdefault(name.casefold(), set()).add(pid)
    if any(len(ids) > 1 for ids in names.values()):
        issues.add("AMBIGUOUS_SHARED_DISPLAY_NAME")

    thread = field(envelope, "thread", {})
    mode = field(thread, "mode")
    if mode not in REPLY_MODES:
        issues.add("THREAD_MODE_INVALID")
    participants = field(thread, "participant_ids")
    if not isinstance(participants, list) or any(not nonblank(x) for x in participants):
        issues.add("THREAD_PARTICIPANTS_INVALID")
        participants = []
    if mode == "NEW":
        if field(thread, "thread_id") is not None or participants:
            issues.add("NEW_MESSAGE_HAS_EXISTING_THREAD")
    elif mode in REPLY_MODES - {"NEW"}:
        if not nonblank(field(thread, "thread_id")) or not nonblank(
                field(thread, "thread_source_ref")):
            issues.add("THREAD_SOURCE_UNBOUND")
        if not set(actual_ids).issubset(set(participants)):
            issues.add("RECIPIENT_OUTSIDE_VERIFIED_THREAD")
    if mode in {"REPLY_ALL", "FORWARD", "GROUP"} and not nonblank(
            field(thread, "audience_change_review_ref")):
        issues.add("MULTIPARTY_OR_FORWARD_SCOPE_UNREVIEWED")

    content = field(envelope, "content", {})
    if not all(nonblank(field(content, k)) for k in ("subject", "body")):
        issues.add("EMPTY_SUBJECT_OR_BODY")
    if any("\r" in field(content, k, "") or "\n" in field(content, k, "")
           for k in ("subject",) if isinstance(field(content, k), str)):
        issues.add("SUBJECT_HEADER_INJECTION")
    claims = field(content, "attributed_claims", [])
    if not isinstance(claims, list):
        issues.add("CLAIMS_INVALID")
    else:
        for c in claims:
            if not all(nonblank(field(c, k)) for k in
                       ("subject_person_id", "claim_text", "evidence_ref", "review_state")):
                issues.add("ATTRIBUTED_CLAIM_UNBOUND")
            elif field(c, "review_state") != "CHECKED":
                issues.add("ATTRIBUTED_CLAIM_NOT_CHECKED")
    files = field(content, "attachments", [])
    if not isinstance(files, list):
        issues.add("ATTACHMENTS_INVALID")
    else:
        for f in files:
            if not all(nonblank(field(f, k)) for k in ("name", "sha256", "source_ref")):
                issues.add("ATTACHMENT_NOT_SOURCE_BOUND")
            elif sorted(field(f, "approved_person_ids", [])) != sorted(actual_ids):
                issues.add("ATTACHMENT_AUDIENCE_NOT_APPROVED")
    privacy = field(envelope, "privacy_class")
    if privacy not in PRIVACY_CLASSES:
        issues.add("PRIVACY_UNCLASSIFIED")
    if privacy == "RESTRICTED" and not nonblank(field(envelope, "privacy_review_ref")):
        issues.add("RESTRICTED_DATA_REVIEW_MISSING")

    # Only intended content binds the approval; no plaintext is echoed in results.
    route_fingerprint = digest({
        "schema": field(envelope, "schema"),
        "channel": field(envelope, "channel"),
        "message_id": field(envelope, "message_id"),
        "sender": sender, "audience": audience,
        "intended_recipient_ids": declared,
        "thread": thread, "content": content,
        "privacy_class": privacy, "purpose": field(envelope, "purpose")})
    approval = field(envelope, "review", {})
    if not all(nonblank(field(approval, k)) for k in
               ("human_reviewer_id", "human_review_evidence_ref",
                "sender_route_review_ref", "semantic_content_review_ref")):
        issues.add("HUMAN_REVIEW_MISSING")
    if field(approval, "reviewed_fingerprint") != route_fingerprint:
        issues.add("REVIEW_FINGERPRINT_MISMATCH")
    return {
        "schema": "CoOutreach.IdentityRoutingAssessment.R0",
        "state": "HELD" if issues else "REVIEW_READY_ONLY",
        "issue_codes": sorted(issues),
        "bound_fingerprint_sha256": route_fingerprint,
        "recipient_count": len(recipients),
        "send_status": "NOT_SENT",
        "external_effects": 0,
        "nonclaims": [
            "SELF_DECLARED_RECORDS_NE_INDEPENDENT_IDENTITY_PROOF",
            "STRUCTURAL_REVIEW_NE_SEMANTIC_TRUTH",
            "REVIEW_READY_NE_SEND_AUTHORITY",
            "DRAFT_NE_SENT_NE_DELIVERED_NE_ACKED",
            "NO_EMAIL_OR_PROVIDER_CALLS",
        ]
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("envelope", type=Path)
    args = parser.parse_args()
    result = validate(json.loads(args.envelope.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["state"] == "REVIEW_READY_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
