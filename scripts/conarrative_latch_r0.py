"""CoNarrativeLatch R0: explicit gesture -> portable intent receipt (synthetic).
No OS input hooks, audio recording, network sends, or background processes.
"""
from __future__ import annotations
import hashlib
import json

WORK_ID = "copregeneric:handoff:public-seed-path:r0:20261109"
ALLOWED_GESTURES = {"co-thumb-explicit", "voice-confirmed", "keyboard-confirmed"}
ALLOWED_SCOPE = {"local-private", "review-only"}

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def latch(event, prior=None):
    """Fail closed unless user explicitly invoked the capture and approved scope.
    Returns a stable proposal receipt, not an executed/accepted action.
    """
    if event.get("gesture") not in ALLOWED_GESTURES:
        return {"state": "PASS_THROUGH_NATIVE", "receipt": None}
    if event.get("permission") is not True:
        return {"state": "HOLD_CONSENT", "receipt": None}
    if event.get("scope") not in ALLOWED_SCOPE:
        return {"state": "HOLD_SCOPE", "receipt": None}
    if event.get("contains_bystander_capture"):
        return {"state": "HOLD_PRIVACY", "receipt": None}
    intent = event.get("intent", "")
    if not isinstance(intent, str) or not intent.strip() or len(intent)>500:
        return {"state": "HOLD_INTENT", "receipt": None}
    object_id = event.get("object_id")
    if not isinstance(object_id, str) or not object_id.strip() or len(object_id)>160:
        return {"state": "HOLD_OBJECT", "receipt": None}
    record = {
        "schema": "CoNarrativeLatch.R0",
        "work_id": WORK_ID,
        "object_id": object_id.strip(),
        "intent": intent.strip(),
        "scope": event["scope"],
        "gesture": event["gesture"],
        "prior_digest": prior.get("digest") if prior else None,
        "effect": "PROPOSAL_ONLY_NOT_EXECUTED",
    }
    digest = hashlib.sha256(canonical(record).encode("utf-8")).hexdigest()
    return {"state": "LATCHED_LOCAL_PROPOSAL", "receipt": {**record, "digest": digest}}

def continue_from(receipt, provided_digest):
    if not isinstance(receipt, dict):
        return {"state": "HOLD_MISSING"}
    data = {k:v for k,v in receipt.items() if k!="digest"}
    expected = hashlib.sha256(canonical(data).encode("utf-8")).hexdigest()
    if expected != receipt.get("digest") or expected != provided_digest:
        return {"state": "HOLD_CORRUPT_OR_WRONG_VERSION"}
    if data.get("work_id") != WORK_ID or data.get("effect") != "PROPOSAL_ONLY_NOT_EXECUTED":
        return {"state": "HOLD_UNKNOWN_SCOPE"}
    return {"state": "RECOVERED_INTENT_ONLY", "intent": data["intent"], "object_id": data["object_id"], "effect": "NOT_EXECUTED"}

