#!/usr/bin/env python3
"""CoGoAll R0 event-to-WorkID wake *proposal*, never an event dispatcher.

This pure source-only adapter reuses the existing #317 owner and #449 due-work
proof lane. It neither schedules, writes queues, executes tasks, nor creates
receiver credentials. Inputs/prior entries are caller claims, not attestations.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import re

SCHEMA = "CoAll.CoGoAll.WakeEventProposal.R0"
OUTPUT = "CoAll.CoGoAll.WakeAdmissionReview.R0"
FIELDS = {
    "schema", "event_id", "work_id", "source_path", "source_revision",
    "source_sha256", "observed_at_utc", "materiality",
    "materiality_evidence_sha256", "authority_ceiling", "confidentiality",
    "collision_domain", "idempotency_key", "predecessor_checkpoint_sha256",
    "receiver_class", "receiver_ready", "wake_condition", "stop_condition",
    "claimed_external_ack",
}
ID = re.compile(r"[A-Za-z0-9_.:-]{1,140}\Z")
SHA256 = re.compile(r"[a-f0-9]{64}\Z")
SHA1 = re.compile(r"[a-f0-9]{40}\Z")
TIME = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z\Z")
PRIOR_FIELDS = {"wake_id", "work_id", "collision_domain", "source_sha256",
                "checkpoint_sha256"}
NONCLAIMS = [
    "CANDIDATE_NE_ADMITTED_WORK",
    "CALLER_CLAIMED_HASH_NE_AUTHENTICATED_SOURCE",
    "CALLER_PRIOR_NE_AUTHENTICATED_JOURNAL",
    "WAKE_CONDITION_NE_EXECUTION_OR_PROVIDER_SESSION_CYCLE",
    "NO_NEW_SCHEDULER_OR_DEVICE_EFFECT",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
    "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
]


def _hold(reason: str, work_id=None, wake_id=None) -> dict:
    return {
        "schema": OUTPUT,
        "state": "HOLD_WAKE_ADMISSION",
        "reason": reason,
        "work_id": work_id,
        "wake_id": wake_id,
        "candidate_eligible_for_owner_review": False,
        "candidate_written": False,
        "task_dispatched": False,
        "external_receiver_ack": False,
        "runtime_accepted": False,
        "nonclaims": NONCLAIMS,
    }


def _valid_id(value) -> bool:
    return isinstance(value, str) and bool(ID.fullmatch(value))


def _valid_hash(value) -> bool:
    return isinstance(value, str) and bool(SHA256.fullmatch(value))


def _utc(value):
    if not isinstance(value, str) or not TIME.fullmatch(value):
        raise ValueError("HOLD_TIMESTAMP")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError as exc:
        raise ValueError("HOLD_TIMESTAMP") from exc


def _identity(event: dict) -> str:
    # Immutable deterministic *candidate* identity. Does not confer authority.
    selected = {
        k: event[k] for k in (
            "event_id", "work_id", "source_path", "source_revision",
            "source_sha256", "materiality_evidence_sha256", "collision_domain",
            "idempotency_key", "predecessor_checkpoint_sha256",
        )
    }
    raw = json.dumps(selected, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "CoWake." + hashlib.sha256(raw).hexdigest()[:32]


def review(event: dict, prior: list[dict], now: datetime) -> dict:
    """Return one proposal, explicit hold, duplicate, or quiet. Never writes."""
    wid = event.get("work_id") if isinstance(event, dict) else None
    try:
        if not isinstance(event, dict) or set(event) != FIELDS or event.get("schema") != SCHEMA:
            raise ValueError("HOLD_EVENT_SCHEMA")
        if not all(_valid_id(event[k]) for k in ("event_id", "work_id", "collision_domain",
                                                 "idempotency_key")):
            raise ValueError("HOLD_EVENT_OR_WORKID_SHAPE")
        if (not isinstance(event["source_path"], str)
                or not event["source_path"].startswith("ai/currentness/")
                or not event["source_path"].endswith(".json")
                or "\\" in event["source_path"] or ".." in event["source_path"].split("/")):
            raise ValueError("HOLD_SOURCE_PATH")
        if (not isinstance(event["source_revision"], str)
                or not SHA1.fullmatch(event["source_revision"])
                or not _valid_hash(event["source_sha256"])
                or not _valid_hash(event["materiality_evidence_sha256"])):
            raise ValueError("HOLD_SOURCE_IDENTITY")
        previous = event["predecessor_checkpoint_sha256"]
        if previous is not None and not _valid_hash(previous):
            raise ValueError("HOLD_PREDECESSOR")
        if (event["authority_ceiling"] != "PUBLIC_READ_ONLY_SOURCE_VALIDATION"
                or event["confidentiality"] != "PUBLIC_SYNTHETIC"
                or event["collision_domain"] != "CI_PUBLIC_SOURCE_REVIEW"
                or event["receiver_class"] != "EXISTING_COGOALL_CI_SOURCE_VALIDATOR"
                or event["claimed_external_ack"] is not False):
            raise ValueError("HOLD_AUTHORITY_PRIVACY_OR_CLAIM")
        if (event["wake_condition"] != "ON_QUALIFIED_MATERIAL_DELTA"
                or event["stop_condition"] != "STOP_ON_HOLD_OR_NO_DELTA"):
            raise ValueError("HOLD_WAKE_STOP_RULES")
        if type(now) is not datetime or now.tzinfo is None or now.utcoffset().total_seconds() != 0:
            raise ValueError("HOLD_REVIEW_CLOCK")
        when = _utc(event["observed_at_utc"])
        lag = (now - when).total_seconds()
        if not -300 <= lag <= 3600:
            raise ValueError("HOLD_STALE_OR_FUTURE_EVENT")
        if not isinstance(prior, list) or len(prior) > 8:
            raise ValueError("HOLD_PRIOR_BOUNDS")
        seen = set()
        for item in prior:
            if (not isinstance(item, dict) or set(item) != PRIOR_FIELDS
                    or not all(_valid_id(item[k]) for k in
                               ("wake_id", "work_id", "collision_domain"))
                    or not _valid_hash(item["source_sha256"])
                    or not _valid_hash(item["checkpoint_sha256"])
                    or item["wake_id"] in seen):
                raise ValueError("HOLD_UNVERIFIED_PRIOR_SHAPE")
            seen.add(item["wake_id"])
        if event["materiality"] not in ("NO_MATERIAL_DELTA", "MATERIAL_DELTA"):
            raise ValueError("HOLD_MATERIALITY_UNQUALIFIED")
        if event["materiality"] == "NO_MATERIAL_DELTA":
            return {**_hold("NO_MATERIAL_DELTA", wid),
                    "state": "QUIESCENT_NO_WAKE",
                    "reason": None}
        if event["receiver_ready"] is not True:
            raise ValueError("HOLD_RECEIVER_UNAVAILABLE")
        wake_id = _identity(event)
        exact = next((item for item in prior if item["wake_id"] == wake_id), None)
        if exact is not None:
            if (exact["work_id"] != wid
                    or exact["source_sha256"] != event["source_sha256"]
                    or exact["collision_domain"] != event["collision_domain"]):
                raise ValueError("HOLD_WAKE_IDENTITY_COLLISION")
            return {**_hold("DUPLICATE_SUPPRESSED", wid, wake_id),
                    "state": "QUIESCENT_DUPLICATE_NO_WAKE",
                    "reason": None}
        # Never silently nominate a second candidate in a collision domain.
        if any(item["collision_domain"] == event["collision_domain"] for item in prior):
            raise ValueError("HOLD_COLLISION_DOMAIN_ALREADY_OCCUPIED")
        if previous is not None and not any(
                item["checkpoint_sha256"] == previous for item in prior):
            raise ValueError("HOLD_PREDECESSOR_NOT_IN_PRIOR")
        return {
            "schema": OUTPUT,
            "state": "WAKE_ADMISSION_REVIEW_CANDIDATE",
            "reason": None,
            "work_id": wid,
            "wake_id": wake_id,
            "source_sha256": event["source_sha256"],
            "collision_domain": event["collision_domain"],
            "receiver_class": event["receiver_class"],
            "next_proof_gate": "OWNER_VERIFIED_SOURCE_AND_DURABLE_RECEIVER_READBACK",
            "candidate_eligible_for_owner_review": True,
            "candidate_written": False,
            "task_dispatched": False,
            "external_receiver_ack": False,
            "runtime_accepted": False,
            "prior_journal_authenticated": False,
            "nonclaims": NONCLAIMS,
        }
    except (ValueError, TypeError, AttributeError) as exc:
        reason = str(exc)
        if not reason.startswith("HOLD_"):
            reason = "HOLD_INVALID_INPUT"
        return _hold(reason, wid)
