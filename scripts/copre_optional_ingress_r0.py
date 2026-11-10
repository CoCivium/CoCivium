#!/usr/bin/env python3
"""CoPre Optional-Ingress R0: a pure, source-only input adapter.

No chat parsing, telemetry, OS hooks, network access, workers, timers, or
authority grant. Caller-supplied classifications are only candidate claims.
A no-user-input state is legitimate; qualified external events may be reviewed
without another phrase from Rick. Emergency stop still requires real runtime ACK.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "CoAll.CoPre.OptionalIngress.R0"
KINDS = frozenset((
    "NO_INPUT", "SCHEDULED_DUE", "SOURCE_CHANGED", "DEVICE_OBSERVED_RECOVERY",
    "RECEIVER_READBACK", "USER_ASSENT", "USER_IDEA", "USER_CORRECTION",
    "USER_STOP",
))
REQUESTED = frozenset(("NONE", "READ_ONLY", "LOCAL_REVERSIBLE", "CONSEQUENTIAL_GATED"))
PRIVACY = frozenset(("PUBLIC", "PRIVATE", "RESTRICTED", "UNKNOWN"))
EVENT_KEYS = frozenset((
    "schema", "kind", "event_id", "source_ref", "source_sha256",
    "observed_at_utc", "requested_authority", "privacy_class"
))
NONCLAIMS = (
    "TEXT_RITUAL_NE_PERMISSION",
    "INCOMING_KIND_IS_UNVERIFIED_CALLER_CLAIM",
    "NO_INPUT_NE_BACKGROUND_WORK_PROOF",
    "ELIGIBILITY_NE_EXECUTION",
    "SOURCE_SHA_STRING_NE_INDEPENDENT_BYTE_READBACK",
    "EXPLICIT_STOP_NE_HOST_STOP_WITHOUT_ACK",
    "ONE_PROVIDER_NE_SESSION_MAJORITY",
    "ADAPTER_NE_INSTALLED_UNIVERSAL_INTERFACE",
    "DRAFT_NE_CANON",
)

class Held(ValueError):
    pass

def _validated(obj):
    if not isinstance(obj, dict) or set(obj) != EVENT_KEYS:
        raise Held("HELD_UNKNOWN_OR_MISSING_FIELDS")
    if obj["schema"] != SCHEMA or obj["kind"] not in KINDS:
        raise Held("HELD_INVALID_SCHEMA_OR_KIND")
    if obj["requested_authority"] not in REQUESTED or obj["privacy_class"] not in PRIVACY:
        raise Held("HELD_UNQUALIFIED_AUTHORITY_OR_PRIVACY")
    if not isinstance(obj["event_id"], str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}",obj["event_id"]):
        raise Held("HELD_INVALID_EVENT_ID")
    try:
        raw=obj["observed_at_utc"]
        if not isinstance(raw,str) or not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ",raw):
            raise ValueError("time")
        dt.datetime.strptime(raw,"%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        raise Held("HELD_INVALID_OBSERVATION_CLOCK")
    ref=obj["source_ref"];sha=obj["source_sha256"]
    if ref is not None and (not isinstance(ref,str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}",ref)):
        raise Held("HELD_INVALID_SOURCE_REFERENCE")
    if sha is not None and (not isinstance(sha,str) or not re.fullmatch(r"[0-9a-f]{64}",sha)):
        raise Held("HELD_INVALID_SOURCE_DIGEST")
    if obj["kind"]=="NO_INPUT" and (ref is not None or sha is not None or obj["requested_authority"]!="NONE"):
        raise Held("HELD_NO_INPUT_CANNOT_REQUEST_EFFECT_OR_CLAIM_SOURCE")
    return obj

def stable_key(obj):
    """Identifier for an observation, not for an approved external effect."""
    _validated(obj)
    k=obj["kind"]
    if k=="SOURCE_CHANGED":
        # Repeated notifications of identical bytes are observations, not new
        # independent work. Preserve event-specific identity for real receivers.
        fingerprint=[k,obj["source_ref"],obj["source_sha256"]]
    elif k=="RECEIVER_READBACK":
        # Different receiver observations of the same object must remain
        # separately challengeable; event_id alone is NOT proof of distinct
        # hosts or actual reader ACK.
        fingerprint=[k,obj["source_ref"],obj["source_sha256"],obj["event_id"]]
    elif k=="SCHEDULED_DUE":
        fingerprint=[k,obj["source_ref"],obj["event_id"]]
    else:
        fingerprint=[k,obj["source_ref"],obj["source_sha256"],obj["event_id"]]
    canonical=json.dumps(fingerprint,ensure_ascii=True,separators=(",",":")).encode("ascii")
    return "copre:ingress:"+hashlib.sha256(canonical).hexdigest()

def preview(obj, seen_keys=()):
    """Sole output is a review preview. No instructions are executed."""
    obj=_validated(obj)
    if seen_keys is None or not isinstance(seen_keys,(set,tuple,list)) or len(seen_keys)>10000:
        raise Held("HELD_UNQUALIFIED_DEDUPE_VIEW")
    if any(not isinstance(k,str) or not re.fullmatch(r"copre:ingress:[0-9a-f]{64}",k) for k in seen_keys):
        raise Held("HELD_UNQUALIFIED_DEDUPE_KEYS")
    key=stable_key(obj)
    kind=obj["kind"]
    urgent=kind in {"USER_STOP","USER_CORRECTION"}
    duplicate=key in seen_keys
    lacks_proof = kind!="NO_INPUT" and (obj["source_ref"] is None or obj["source_sha256"] is None)
    # The adapter cannot certify bytes, consent, app state or cross-provider uptake.
    if kind=="NO_INPUT":
        state="NO_USER_MESSAGE_REQUIRED"
        eligible=False
    elif urgent:
        state=("STOP_REQUEST_REQUIRES_RUNTIME_ACK" if kind=="USER_STOP"
               else "CORRECTION_REQUIRES_REVIEW_ACK")
        eligible=False
    elif lacks_proof:
        state="HELD_SOURCE_POINTER_OR_HASH_ABSENT"
        eligible=False
    elif duplicate:
        state="EXACT_DUPLICATE_OBSERVATION"
        eligible=False
    elif kind=="USER_ASSENT":
        # Upstream must explicitly classify pure assent. A rant with novel
        # content must become USER_IDEA or USER_CORRECTION, not be discarded.
        state="STANDING_INTENT_ALREADY_PRESENT"
        eligible=False
    elif kind=="USER_IDEA":
        state="IDEA_CANDIDATE_FOR_QUALIFICATION"
        eligible=False
    else:
        state="SOURCE_BOUND_REVIEW_CANDIDATE"
        eligible=True
    return {
        "schema":"CoAll.CoPre.OptionalIngressReceipt.R0",
        "source_event_kind":kind,
        "work_pointer":key,
        "decision":state,
        "eligible_for_further_qualification":eligible,
        "raw_user_text_stored":False,
        "user_prompt_required_to_start_review":False,
        "human_effect_authority_granted":False,
        "external_effect_count":0,
        "receiver_ack":False,
        "stop_effect_ack":False,
        "stop_or_correction_attention_required":urgent,
        "prior_seen":duplicate,
        "independent_session_adoption":"UNMEASURED",
        "actual_actor_or_runtime":"NONE_THIS_ADAPTER",
        "proof_boundary":"CALLER_SUPPLIED_SOURCE_REF_AND_DIGEST_NOT_REFETCHED",
        "nonclaims":NONCLAIMS,
    }

def main():
    ap=argparse.ArgumentParser(description="Read-only optional CoPre ingress preview")
    ap.add_argument("--event",type=Path,required=True)
    args=ap.parse_args()
    try:
        p=args.event
        if p.is_symlink() or not p.is_file() or p.stat().st_size>4096:
            raise Held("HELD_BAD_EVENT_FILE")
        event=json.loads(p.read_text(encoding="utf-8"))
        result=preview(event)
        # No original event or private text printed.
        print(json.dumps(result,sort_keys=True))
    except (Held,TypeError,ValueError,OSError,UnicodeError) as exc:
        msg=str(exc) if isinstance(exc,Held) else "HELD_INVALID_EVENT"
        print(json.dumps({"decision":msg,"external_effect_count":0,"receiver_ack":False}))
        raise SystemExit(2)

if __name__=="__main__":
    main()
