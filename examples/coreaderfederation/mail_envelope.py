#!/usr/bin/env python3
"""CoMail R0: fixed historical message -> evolving public source, never auto-send.

A pure, synthetic-only projection donor for CoReaderFederation. No network,
account, device, token, recipient, publication, or tracking side effects.
Source hashes and source URLs are *declared*, not independently fetched.
"""
from __future__ import annotations
import json
import re
from copy import deepcopy

from route import fingerprint, safe_public_url, utc_datetime

SCHEMA = "CoCivium.CoMail.VersionedEnvelope.R0"
VERSION_CLASSES = {"DESIGN_PROPOSAL", "RESEARCH_HYPOTHESIS", "FICTION", "VERIFIED_CLAIM_CANDIDATE"}
VERSION_STATES = {"PUBLISHED", "CORRECTED", "RETRACTED"}
READ_MODES = {"PIN", "FOLLOW", "COMPARE"}
ZERO_EFFECTS = {
    "emails_sent": 0, "notifications_sent": 0, "source_mutations": 0,
    "tracking_events": 0, "workers_started": 0, "account_reads": 0
}
ENVELOPE_FIELDS = {"envelope_id", "message_sha256", "message_state", "composed_at",
                   "resource_id", "sent_version_id", "send_receipt", "effect_authority"}
VERSION_FIELDS = {"version_id", "parent_id", "source_sha256", "source_url", "issued_at",
                  "state", "epistemic_class", "change_summary", "privacy"}
ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.:-]{2,79}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def _id(value, field):
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise ValueError("INVALID_" + field.upper())
    return value


def _sha(value):
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        raise ValueError("INVALID_SHA256")
    return value


def _exact(record, fields, label):
    if not isinstance(record, dict) or set(record) != fields:
        raise ValueError("INVALID_" + label + "_FIELDS")


def validate(model):
    """Fail closed; no private recipient or unknown input fields allowed."""
    _exact(model, {"schema", "envelope", "versions", "current_version_id"}, "MODEL")
    if model["schema"] != SCHEMA:
        raise ValueError("INVALID_SCHEMA")
    env = model["envelope"]
    _exact(env, ENVELOPE_FIELDS, "ENVELOPE")
    _id(env["envelope_id"], "envelope_id")
    _id(env["resource_id"], "resource_id")
    _id(env["sent_version_id"], "sent_version_id")
    _sha(env["message_sha256"])
    utc_datetime(env["composed_at"])
    if env["message_state"] != "SYNTHETIC_NOT_SENT" or env["send_receipt"] is not None:
        raise ValueError("NO_REAL_SEND_RECEIPT_ACCEPTED")
    if env["effect_authority"] != "NONE":
        raise ValueError("NO_EFFECT_AUTHORITY")
    versions = model["versions"]
    if not isinstance(versions, list) or not 1 <= len(versions) <= 32:
        raise ValueError("BOUNDED_VERSION_COUNT_REQUIRED")
    by_id = {}
    roots = 0
    for v in versions:
        _exact(v, VERSION_FIELDS, "VERSION")
        vid = _id(v["version_id"], "version_id")
        if vid in by_id:
            raise ValueError("DUPLICATE_VERSION_ID")
        _sha(v["source_sha256"])
        if not safe_public_url(v["source_url"]):
            raise ValueError("SOURCE_URL_NOT_ALLOWED")
        if v["state"] not in VERSION_STATES or v["epistemic_class"] not in VERSION_CLASSES:
            raise ValueError("UNQUALIFIED_SOURCE_CLASS")
        if v["privacy"] != "DECLARED_PUBLIC_SAFE_NOT_RIGHTS_VERIFIED":
            raise ValueError("PRIVACY_OR_RIGHTS_UNQUALIFIED")
        if not isinstance(v["change_summary"], str) or not 1 <= len(v["change_summary"]) <= 180:
            raise ValueError("CHANGE_SUMMARY_REQUIRED")
        issued = utc_datetime(v["issued_at"])
        if v["parent_id"] is None:
            roots += 1
        else:
            parent = _id(v["parent_id"], "parent_id")
            if parent not in by_id:
                raise ValueError("PREDECESSOR_MUST_PRECEDE_SUCCESSOR")
            if issued <= utc_datetime(by_id[parent]["issued_at"]):
                raise ValueError("SUCCESSOR_TIME_MUST_ADVANCE")
        by_id[vid] = v
    if roots != 1:
        raise ValueError("EXACT_ONE_VERSION_ROOT")
    if env["sent_version_id"] not in by_id:
        raise ValueError("PINNED_SENT_VERSION_MISSING")
    current = _id(model["current_version_id"], "current_version_id")
    if current not in by_id:
        raise ValueError("CURRENT_VERSION_MISSING")
    return by_id


def _lineage(by_id, version_id):
    path = []
    seen = set()
    while version_id is not None:
        if version_id in seen or version_id not in by_id:
            raise ValueError("INVALID_LINEAGE")
        seen.add(version_id)
        v = by_id[version_id]
        path.append(v)
        version_id = v["parent_id"]
    return list(reversed(path))


def project(model, mode="PIN"):
    """Read-only, audience-selected, no content or recipient identifiers."""
    by_id = validate(model)
    if mode not in READ_MODES:
        raise ValueError("READER_MUST_CHOOSE_VALID_MODE")
    src = model["envelope"]["sent_version_id"]
    current = model["current_version_id"]
    original = by_id[src]
    latest = by_id[current]
    ancestry = _lineage(by_id, current)
    related_to_original = any(v["version_id"] == src for v in ancestry)
    if not related_to_original:
        raise ValueError("ELECTED_VERSION_NOT_IN_SENT_LINEAGE")
    selected = original if mode == "PIN" else latest
    children = {v["parent_id"] for v in model["versions"] if v["parent_id"] is not None}
    branch_tips = sorted(v["version_id"] for v in model["versions"] if v["version_id"] not in children)
    changed_versions = [
        {"version_id": v["version_id"], "state": v["state"],
         "declared_change": v["change_summary"], "verified_diff": False}
        for v in ancestry if v["version_id"] != src and
        _lineage(by_id, v["version_id"])[-1]["version_id"] == v["version_id"] and
        any(item["version_id"] == src for item in _lineage(by_id, v["version_id"]))
    ]
    warning = ("CORRECTION_OR_RETRACTION_AVAILABLE"
               if any(v["state"] in {"CORRECTED", "RETRACTED"} for v in ancestry)
               else None)
    if latest["state"] == "RETRACTED":
        warning = "SOURCE_WITHDRAWN__HISTORICAL_MESSAGE_NOT_RECALLED"
    env = model["envelope"]
    return {
        "schema": "CoCivium.CoMail.ReaderProjection.R0",
        "state": "SYNTHETIC_READ_ONLY_PREVIEW",
        "envelope_id": env["envelope_id"],
        "historical_message_sha256": env["message_sha256"],
        "historical_message_state": env["message_state"],
        "composed_at": env["composed_at"],
        "resource_id": env["resource_id"],
        "reader_selected_mode": mode,
        "sent_version_id": src,
        "selected_version_id": selected["version_id"],
        "selected_source_sha256": selected["source_sha256"],
        "selected_source_url": (None if selected["state"] == "RETRACTED"
                                else selected["source_url"]),
        "elected_current_version_id": current,
        "version_currentness": "DECLARED_ONLY__NOT_FETCH_VERIFIED",
        "sent_version_is_still_selectable": True,
        "change_notice": warning,
        "declared_changes_on_elected_lineage": changed_versions if mode == "COMPARE" else [],
        "unpromoted_branch_tips": [tip for tip in branch_tips if tip != current],
        "source_rights_state": selected["privacy"],
        "epistemic_class": selected["epistemic_class"],
        "effects": deepcopy(ZERO_EFFECTS),
        "send_authority": "NONE",
        "recipient_ack": None,
        "source_fingerprint": fingerprint(model),
        "nonclaims": [
            "STATIC_SENT_BYTES_NE_LIVING_DESTINATION",
            "DECLARED_SOURCE_SHA_NE_VERIFIED_PUBLIC_READPROOF",
            "PIN_NE_SILENT_REWRITE",
            "FOLLOW_NE_AUTO_NOTIFICATION",
            "RETRACTION_NE_RECALL_OF_DELIVERED_MESSAGE",
            "PUBLIC_SAFE_DECLARATION_NE_RIGHTS_CLEARANCE",
            "MESSAGE_PREVIEW_NE_EMAIL_DELIVERY_OR_READ",
            "BRANCH_NE_AUTOMATIC_CANON"
        ]
    }


if __name__ == "__main__":
    from pathlib import Path
    fixture = Path(__file__).with_name("mail_fixture.json")
    print(json.dumps(project(json.loads(fixture.read_text(encoding="utf-8")), "COMPARE"),
                     indent=2, sort_keys=True))
