#!/usr/bin/env python3
"""CoShoAn+/CoShoulderAngel+ deterministic shadow contract R0.

Offline synthetic-only test harness; never captures keystrokes or microphones,
opens the clipboard, sends messages, pairs earbuds, or changes external state.
"""
import hashlib
import json
import sys

SUGGESTIONS = {
    "Broadcast to": " qualified, consented subscribers only",
    "What else": " would falsify this proposal?",
    "CoMap": " show sources and unproved relations",
}
KINDS = {"OBSERVED", "PREDICTED", "PREFERRED", "COUNTERFACTUAL", "UNKNOWN"}

def raw_digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def prediction(raw, context):
    """Returns a ghost overlay; never inserts into the raw user's text."""
    if not context.get("local_explicit_input"):
        return {"state": "HOLD_NO_EXPLICIT_INPUT"}
    if context.get("revoked"):
        return {"state": "HOLD_REVOKED"}
    if context.get("focus") != "TRUSTED_EDITOR":
        return {"state": "HOLD_UNTRUSTED_EDITOR"}
    if context.get("sensitive"):
        return {"state": "HOLD_SENSITIVE_CONTEXT"}
    if not isinstance(raw, str) or len(raw) > 1024:
        return {"state": "HOLD_INVALID_INPUT"}
    suffix = SUGGESTIONS.get(raw.strip())
    if suffix is None:
        return {"state": "ABSTAIN_NO_USEFUL_PREDICTION"}
    cursor = context.get("ack_cursor")
    if not isinstance(cursor, int) or isinstance(cursor, bool) or cursor < 0:
        return {"state": "HOLD_UNKNOWN_CURSOR"}
    return {
        "state": "GHOST_PREVIEW_ONLY",
        "epistemic_class": "PREDICTED",
        "last_acked_cursor": cursor,
        "candidate_cursor": cursor + 1,
        "source_sha256": raw_digest(raw),
        "ghost_suffix": suffix,
        "raw_unchanged": raw,
        "source_scope": "EXPLICIT_USER_SUPPLIED_TEXT_ONLY",
        "effects": [],
    }

def acknowledge(preview, current_raw, user_ack, current_cursor, revision=None):
    """Acknowledgement of a proposal is not execution or receiver pickup."""
    if preview.get("state") != "GHOST_PREVIEW_ONLY":
        return "HOLD_NO_PROPOSAL"
    if not user_ack:
        return "HOLD_NO_EXPLICIT_ACK"
    if raw_digest(current_raw) != preview["source_sha256"]:
        return "HOLD_RAW_CHANGED"
    if current_cursor != preview["last_acked_cursor"]:
        return "HOLD_CURSOR_DRIFT"
    if revision is not None and (not isinstance(revision, str) or len(revision) > 1024):
        return "HOLD_INVALID_REVISION"
    return "ACKNOWLEDGED_PREVIEW_ONLY_NO_SEND"

def route(event, receiver):
    """Selects a candidate receiver; does not deliver or create an ACK."""
    if event.get("epistemic_class") not in KINDS:
        return "HOLD_UNKNOWN_EPISTEMIC_CLASS"
    if receiver.get("revoked"):
        return "HOLD_REVOKED"
    if not receiver.get("subscription_verified"):
        return "HOLD_NO_SUBSCRIPTION"
    if receiver.get("rate_limited"):
        return "DEFER_BACKPRESSURE"
    if event.get("visibility") != "PUBLIC":
        return "HOLD_NO_PUBLIC_PRIVATE_FANOUT"
    if receiver.get("confidentiality_ceiling") != "PUBLIC":
        return "HOLD_SCOPE_MISMATCH"
    topics = receiver.get("topics", ())
    if event.get("topic") not in topics:
        return "HOLD_UNSUBSCRIBED_TOPIC"
    if event.get("cursor", 0) <= receiver.get("last_acked_cursor", 0):
        return "HOLD_NOT_NEWER_THAN_ACK"
    return "ROUTE_PREVIEW_NOT_SENT"

def shoulderangel(mode="QUIET", enabled=False):
    if not enabled:
        return {"state": "SILENT_BY_DEFAULT"}
    prompts = {
        "QUESTION": "What evidence would change your mind?",
        "CHALLENGE": "Which interpretation could be wrong?",
        "RECOVER": "Preserve the previous state before revising.",
        "VOICE": "Pairing is a device function. Companion speech requires a user-chosen voice and verified audio route.",
        "SYMBOLIC": "A symbolic G_d perspective is not proof of an external speaker or authority.",
    }
    if mode not in prompts:
        return {"state": "QUIET_NO_MATCH"}
    return {"state": "OPTIONAL_TEXT_ONLY", "text": prompts[mode],
            "mic_stream_active": False, "audio_played": False,
            "device_pairing_performed": False, "external_actions": []}

def test():
    ctx = dict(local_explicit_input=True,focus="TRUSTED_EDITOR",
               sensitive=False,revoked=False,ack_cursor=7)
    preview = prediction("Broadcast to", ctx)
    tests = []
    def check(name,actual,expected):
        tests.append(dict(id=name,actual=actual,expected=expected,pass_test=actual==expected))
    check("ghost_state", preview["state"], "GHOST_PREVIEW_ONLY")
    check("ghost_only", preview["effects"], [])
    check("raw_unchanged", preview["raw_unchanged"], "Broadcast to")
    check("advanced_candidate_not_ack", (preview["candidate_cursor"],preview["last_acked_cursor"]), (8,7))
    check("source_digest", preview["source_sha256"], raw_digest("Broadcast to"))
    check("no_explicit", prediction("Broadcast to", dict(ctx,local_explicit_input=False))["state"],"HOLD_NO_EXPLICIT_INPUT")
    check("no_focus", prediction("Broadcast to", dict(ctx,focus="UNKNOWN"))["state"],"HOLD_UNTRUSTED_EDITOR")
    check("password", prediction("Broadcast to", dict(ctx,sensitive=True))["state"],"HOLD_SENSITIVE_CONTEXT")
    check("revoked", prediction("Broadcast to", dict(ctx,revoked=True))["state"],"HOLD_REVOKED")
    check("abstain", prediction("some new phrase", ctx)["state"],"ABSTAIN_NO_USEFUL_PREDICTION")
    check("no_cursor", prediction("Broadcast to", dict(ctx,ack_cursor=None))["state"],"HOLD_UNKNOWN_CURSOR")
    check("no_ack", acknowledge(preview, "Broadcast to",False,7),"HOLD_NO_EXPLICIT_ACK")
    check("ack_mismatch", acknowledge(preview,"changed",True,7),"HOLD_RAW_CHANGED")
    check("cursor_mismatch", acknowledge(preview,"Broadcast to",True,8),"HOLD_CURSOR_DRIFT")
    check("ack_preview_not_sent", acknowledge(preview,"Broadcast to",True,7),"ACKNOWLEDGED_PREVIEW_ONLY_NO_SEND")
    check("ack_invalid_revision", acknowledge(preview,"Broadcast to",True,7,"x"*1025),"HOLD_INVALID_REVISION")
    event=dict(epistemic_class="PREDICTED",visibility="PUBLIC",topic="CoMap",cursor=9)
    receiver=dict(subscription_verified=True,revoked=False,rate_limited=False,
                  confidentiality_ceiling="PUBLIC",topics=["CoMap"],last_acked_cursor=7)
    check("qualified_route", route(event,receiver),"ROUTE_PREVIEW_NOT_SENT")
    check("no_blast", route(event,dict(receiver,subscription_verified=False)),"HOLD_NO_SUBSCRIPTION")
    check("privacy", route(dict(event,visibility="PRIVATE"),receiver),"HOLD_NO_PUBLIC_PRIVATE_FANOUT")
    check("no_topic", route(event,dict(receiver,topics=["Other"])),"HOLD_UNSUBSCRIBED_TOPIC")
    check("backpressure", route(event,dict(receiver,rate_limited=True)),"DEFER_BACKPRESSURE")
    check("stale_event", route(dict(event,cursor=7),receiver),"HOLD_NOT_NEWER_THAN_ACK")
    check("unknown_class", route(dict(event,epistemic_class="UNCLASSIFIED"),receiver),"HOLD_UNKNOWN_EPISTEMIC_CLASS")
    check("muted_default", shoulderangel()["state"],"SILENT_BY_DEFAULT")
    check("symbolic_boundary", "not proof" in shoulderangel("SYMBOLIC",True)["text"],True)
    check("no_unconsented_audio", shoulderangel("VOICE",True)["audio_played"],False)
    check("no_earbud_pairing", shoulderangel("VOICE",True)["device_pairing_performed"],False)
    out={"schema":"CoShoAn.PredictiveCursor.ShadowTest.R0",
         "state":"PASS_SYNTHETIC_ONLY" if all(x["pass_test"] for x in tests) else "FAIL_SYNTHETIC",
         "tests":len(tests),"pass_count":sum(x["pass_test"] for x in tests),
         "failures":[x for x in tests if not x["pass_test"]],
         "effects":{"mic":0,"clipboard":0,"input_injection":0,"network":0,
                    "pairing":0,"send":0,"public_broadcast":0,"runtime":0},
         "nonclaims":["NO_MODEL_CALL","NO_REAL_USER_FORECAST","NO_REAL_RECEIVER_ACK",
                      "NO_DIVINE_AUTHORITY","NO_EARBUD_FIRMWARE_CONTROL",
                      "NO_GRAIL_RUNTIME","NO_COEX_CANON"]}
    return out

if __name__ == "__main__":
    r=test()
    print(json.dumps(r,sort_keys=True,indent=2))
    sys.exit(0 if r["state"]=="PASS_SYNTHETIC_ONLY" else 2)
