#!/usr/bin/env python3
"""Pure, offline pre-send identity/attribution gate. No transport operations."""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone

SCHEMA = "CoAll.CoReach.PreSendIdentityGate.R0"
EMAIL = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,63}$")
MAX_INPUT = 131072
MAX_RECIPIENTS = 64
IDENTITY_PROOFS = {"RECIPIENT_CONFIRMED", "DIRECT_REPLY_BOUND", "OWNER_APPROVED_EXACT_ROUTE"}
ROUTE_STATES = {"QUALIFIED", "UNKNOWN", "BOUNCED", "BLOCKED", "EXPIRED"}
AUTHORITY_STATES = {"NONE", "DRAFT_ONLY", "RECIPIENT_SCOPED", "EXPLICIT_SEND"}

class InvalidInput(ValueError):
    pass

def norm_email(value):
    if not isinstance(value, str) or len(value) > 254 or value != value.strip() or not EMAIL.fullmatch(value):
        raise InvalidInput("INVALID_ADDRESS_SYNTAX")
    return value.lower()

def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def iso(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})", value):
        raise InvalidInput("INVALID_TIMESTAMP")
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if dt.utcoffset() is None:
            raise ValueError('missing timezone')
        return dt.astimezone(timezone.utc)
    except ValueError as e:
        raise InvalidInput("INVALID_TIMESTAMP") from e

def review(request):
    if not isinstance(request, dict) or request.get("schema") != SCHEMA:
        raise InvalidInput("INVALID_SCHEMA")
    if request.get("mode") != "REVIEW_ONLY":
        raise InvalidInput("INVALID_MODE")
    if not isinstance(request.get("work_id"), str) or not 1 <= len(request["work_id"]) <= 100:
        raise InvalidInput("INVALID_WORK_ID")
    review_time = iso(request.get("review_at"))
    sender = request.get("sender")
    if not isinstance(sender, dict):
        raise InvalidInput("INVALID_SENDER")
    raw_from = sender.get("selected_from")
    from_addr = norm_email(raw_from) if raw_from else None
    connected_addr = norm_email(sender.get("authenticated_account"))
    people = request.get("recipients")
    if not isinstance(people, list) or len(people) > MAX_RECIPIENTS:
        raise InvalidInput("INVALID_RECIPIENTS")
    if not isinstance(request.get("content"), dict) or not isinstance(request.get("thread"), dict):
        raise InvalidInput("INVALID_CONTENT_OR_THREAD")
    if not isinstance(request.get("authority"), dict) or not isinstance(request.get("suppressions"), dict):
        raise InvalidInput("INVALID_AUTHORITY_OR_SUPPRESSIONS")

    content, thread, authority, suppressions = request["content"], request["thread"], request["authority"], request["suppressions"]
    if content.get("privacy") not in ("PUBLIC", "PRIVATE"): raise InvalidInput("INVALID_PRIVACY")
    if not isinstance(content.get("sha256"), str) or not re.fullmatch(r"sha256:[a-f0-9]{64}", content["sha256"]):
        raise InvalidInput("INVALID_CONTENT_SHA")
    if thread.get("kind") not in ("NEW", "REPLY", "FORWARD", "UNKNOWN"):
        raise InvalidInput("INVALID_THREAD_KIND")
    if authority.get("level") not in AUTHORITY_STATES:
        raise InvalidInput("INVALID_AUTHORITY_LEVEL")
    if not isinstance(request.get("draft_id"), str) or len(request["draft_id"]) > 128:
        raise InvalidInput("INVALID_DRAFT_ID")

    holds = set()
    warnings = set()
    if not content.get("body_digest_verified", False) or content["sha256"] == ("sha256:" + "0"*64):
        holds.add("HOLD_BODY_DIGEST_NOT_VERIFIED")
    if not sender.get("account_observed_by_connector", False):
        holds.add("HOLD_UNVERIFIED_AUTHENTICATED_ACCOUNT")
    if not from_addr:
        holds.add("HOLD_SELECTED_FROM_HEADER_MISSING")
    if not sender.get("selected_from_verified", False):
        holds.add("HOLD_UNVERIFIED_SELECTED_FROM_HEADER")
    requested = sender.get("requested_sender_address")
    if requested:
        requested = norm_email(requested)
        if requested != connected_addr and (sender.get("verified_send_as_alias") is not True or sender.get("verified_alias_address") != requested):
            holds.add("HOLD_REQUESTED_SENDER_NOT_VERIFIED")
    if from_addr and from_addr != connected_addr:
        if sender.get("verified_send_as_alias") is not True or sender.get("verified_alias_address") != from_addr:
            holds.add("HOLD_UNVERIFIED_FROM_ALIAS")
        else:
            proof_time = sender.get("alias_verified_at")
            if not proof_time or (review_time - iso(proof_time)).total_seconds() > 30*86400 or iso(proof_time) > review_time:
                holds.add("HOLD_STALE_FROM_ALIAS_PROOF")
    if not sender.get("signatory_disclosed", False):
        holds.add("HOLD_SIGNATORY_NOT_DISCLOSED")
    if sender.get("writer_kind") not in ("HUMAN", "AI_ASSISTANT"):
        holds.add("HOLD_WRITER_KIND_UNVERIFIED")
    if sender.get("writer_kind") == "AI_ASSISTANT" and sender.get("represented_principal") and not sender.get("principal_authorization_evidenced"):
        holds.add("HOLD_UNVERIFIED_ON_BEHALF_OF")
    if sender.get("visible_signatory") != content.get("signatory_claim"):
        holds.add("HOLD_SIGNATORY_CONTENT_MISMATCH")
    if not content.get("claims_reviewed", False):
        holds.add("HOLD_CLAIMS_AND_ADDRESSEE_NOT_REVIEWED")
    if not content.get("audience_matches_recipients", False):
        holds.add("HOLD_AUDIENCE_MISMATCH")
    if content.get("quotes_or_forwards") and not content.get("speaker_attribution_verified", False):
        holds.add("HOLD_UNVERIFIED_QUOTED_SPEAKERS")
    if content.get("private_third_party_material") and not content.get("disclosure_authorized", False):
        holds.add("HOLD_UNAUTHORIZED_THIRD_PARTY_DISCLOSURE")
    if authority.get("level") not in ("RECIPIENT_SCOPED", "EXPLICIT_SEND"):
        holds.add("HOLD_NO_SCOPED_SEND_AUTHORITY")
    if not authority.get("recipient_set_confirmed", False):
        holds.add("HOLD_RECIPIENT_SET_NOT_APPROVED")
    if suppressions.get("opt_out") or suppressions.get("do_not_contact"):
        holds.add("HOLD_RECIPIENT_SUPPRESSED")
    if suppressions.get("duplicate_recent"):
        holds.add("HOLD_DUPLICATE_FOLLOWUP")
    if suppressions.get("route_bounced"):
        holds.add("HOLD_BOUNCED_ROUTE")
    if not suppressions.get("checked", False):
        holds.add("HOLD_SUPPRESSION_NOT_CHECKED")
    if request.get("state") != "DRAFT":
        holds.add("HOLD_NOT_AN_UNSENT_DRAFT")

    addresses = set()
    to_count=0
    counts={"TO":0,"CC":0,"BCC":0}
    recipient_digests=[]
    for entry in people:
        if not isinstance(entry, dict):
            raise InvalidInput("INVALID_RECIPIENT_RECORD")
        address = norm_email(entry.get("address"))
        field = entry.get("field")
        if field not in counts:
            raise InvalidInput("INVALID_RECIPIENT_FIELD")
        counts[field] += 1
        to_count += int(field == "TO")
        # No plaintext names, addresses or body content in a receipt.
        recipient_digests.append({"field":field,"address_sha256": "sha256:"+digest(address)})
        if address in addresses:
            holds.add("HOLD_DUPLICATE_ADDRESS_ACROSS_HEADERS")
        addresses.add(address)
        if entry.get("identity_proof") not in IDENTITY_PROOFS or not entry.get("person_or_org_id"):
            holds.add("HOLD_UNRESOLVED_RECIPIENT_IDENTITY")
        status = entry.get("route_state")
        if status not in ROUTE_STATES:
            raise InvalidInput("INVALID_ROUTE_STATE")
        if status != "QUALIFIED":
            holds.add("HOLD_RECIPIENT_ROUTE_NOT_QUALIFIED")
        if entry.get("identity_proof_at"):
            evidence_time=iso(entry["identity_proof_at"])
            if evidence_time > review_time or (review_time-evidence_time).total_seconds() > 30*86400:
                holds.add("HOLD_STALE_RECIPIENT_IDENTITY")
        else:
            holds.add("HOLD_MISSING_RECIPIENT_IDENTITY_TIME")
        if field == "BCC" and not authority.get("bcc_specifically_approved", False):
            holds.add("HOLD_BCC_UNAUTHORIZED")
        if field == "CC" and not authority.get("cc_visibility_approved", False):
            holds.add("HOLD_CC_DISCLOSURE_NOT_APPROVED")
        if not entry.get("recipient_aware_of_purpose", False):
            warnings.add("WARN_RECIPIENT_PURPOSE_UNCONFIRMED")
    if to_count == 0:
        holds.add("HOLD_NO_PRIMARY_RECIPIENT")
    if len(people)==0:
        holds.add("HOLD_NO_RECIPIENTS")
    if thread["kind"] == "UNKNOWN":
        holds.add("HOLD_THREAD_KIND_UNRESOLVED")
    if thread["kind"] == "REPLY":
        if not thread.get("original_message_id") or not thread.get("thread_id"):
            holds.add("HOLD_REPLY_WITHOUT_SOURCE_THREAD")
        if not thread.get("reply_to_checked"):
            holds.add("HOLD_REPLY_TO_NOT_VERIFIED")
        if thread.get("audience_changed") and not thread.get("audience_change_approved"):
            holds.add("HOLD_CHANGED_THREAD_AUDIENCE")
    if thread["kind"] == "FORWARD":
        if not thread.get("original_message_id") or not thread.get("forward_disclosure_checked"):
            holds.add("HOLD_FORWARD_CONTEXT_NOT_APPROVED")
    if thread.get("message_target_mode") == "DIRECT_TO_REFERENCED_PERSON":
        targeted=set(thread.get("direct_target_addresses", []))
        if not targeted or not all(norm_email(a) in {norm_email(e["address"]) for e in people if e["field"]=="TO"} for a in targeted):
            holds.add("HOLD_DIRECT_RECIPIENT_CLAIM_MISMATCH")
    elif thread.get("message_target_mode") not in ("INTERMEDIARY_CONTACT", "NORMAL"):
        holds.add("HOLD_UNKNOWN_DIRECTNESS_OF_ADDRESS")

    result={
      "schema":"CoAll.CoReach.PreSendIdentityGateReceipt.R0",
      "work_id":request["work_id"],
      "draft_id_sha256":"sha256:"+digest(request["draft_id"]),
      "review_at":request["review_at"],
      "state":"HELD" if holds else "READY_FOR_HUMAN_REVIEW_ONLY",
      "holds":sorted(holds),
      "warnings":sorted(warnings),
      "recipient_counts":counts,
      "recipient_address_digests":recipient_digests,
      "send_authority":"NONE_FROM_THIS_VALIDATOR",
      "effects":{"network":0,"email_sent":0,"draft_updated":0,"provider_call":0,"file_write":0},
      "nonclaims":["CONTACT_ENTRY_NE_IDENTITY_PROOF","WRITER_NE_SENDER_ACCOUNT","SIGNATURE_NE_SEND_AS_AUTHORITY","TO_INTERMEDIARY_NE_TO_REFERENCED_PERSON","THREAD_NE_PERSON","DRAFT_NE_SENT","SENT_NE_DELIVERED","DELIVERED_NE_READ","REVIEW_PASS_NE_SEND_AUTHORITY","NO_SEMANTIC_BODY_VERIFICATION_BY_THIS_GATE","DECLARED_BODY_SHA_NE_INDEPENDENT_READPROOF"]
    }
    return result

def main():
    data = sys.stdin.buffer.read(MAX_INPUT+1)
    if len(data)>MAX_INPUT:
        print("HELD_INPUT_TOO_LARGE",file=sys.stderr)
        sys.exit(2)
    try:
        def no_duplicate_keys(pairs):
            d = {}
            for key, value in pairs:
                if key in d:
                    raise InvalidInput("INVALID_DUPLICATE_JSON_KEY")
                d[key] = value
            return d
        x=json.loads(data,object_pairs_hook=no_duplicate_keys)
        print(json.dumps(review(x),sort_keys=True,ensure_ascii=True,separators=(',',':')))
    except (InvalidInput,ValueError,TypeError,json.JSONDecodeError) as e:
        # Never reflect untrusted raw user content into stderr.
        code=str(e)
        if code not in {"INVALID_SCHEMA","INVALID_MODE","INVALID_WORK_ID","INVALID_TIMESTAMP","INVALID_SENDER","INVALID_ADDRESS_SYNTAX","INVALID_RECIPIENTS","INVALID_CONTENT_OR_THREAD","INVALID_AUTHORITY_OR_SUPPRESSIONS","INVALID_PRIVACY","INVALID_CONTENT_SHA","INVALID_THREAD_KIND","INVALID_AUTHORITY_LEVEL","INVALID_DRAFT_ID","INVALID_RECIPIENT_RECORD","INVALID_RECIPIENT_FIELD","INVALID_ROUTE_STATE","INVALID_DUPLICATE_JSON_KEY"}:
            code="HELD_INVALID_INPUT"
        print(code,file=sys.stderr)
        sys.exit(2)

if __name__=="__main__":
    main()
