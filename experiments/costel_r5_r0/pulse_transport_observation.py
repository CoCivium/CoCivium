"""Read-only adapter for *transport* metadata from existing Automations runs.

Not a source census, receipt verifier, automation client or execution adapter.
Never emits private task/run IDs, raw prompts or alleged receiver results.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

SCHEMA = "CoPulseTransportObservation.R0"


def _utc(text):
    if not isinstance(text, str) or not text:
        raise ValueError("timestamp missing")
    try:
        instant = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except (ValueError, OverflowError) as exc:
        raise ValueError("invalid timestamp") from exc
    if instant.tzinfo is None or instant.utcoffset() != timedelta(0):
        raise ValueError("timestamp must be UTC")
    return instant.astimezone(timezone.utc)


def _iso(instant):
    return instant.isoformat(timespec="microseconds").replace("+00:00", "Z")


def observe_automation_run(task_record, *, sampled_at_utc):
    """Convert sampled connector metadata to a privacy-minimized truth envelope.

    Provider run metadata MAY prove a run was recorded, NEVER eligibility,
    actual useful effects, current WorkID, or receiver-origin ACK by itself.
    Caller must authenticate and preserve the original source separately.
    """
    now = _utc(sampled_at_utc)
    base = {
        "schema": SCHEMA,
        "sampled_at_utc": _iso(now),
        "transport_state": "UNOBSERVED",
        "recorded_status_class": "UNKNOWN",
        "run_identity_present": False,
        "scheduled_for_utc": None,
        "started_at_utc": None,
        "completed_at_utc": None,
        "start_lag_seconds": None,
        "execution_duration_seconds": None,
        "source_work_id": None,
        "source_revision": None,
        "eligibility_census_complete": None,
        "pending_work_count": None,
        "action_reason": None,
        "receiver_readback": None,
        "verified_useful_effect": None,
        "work_result_class": "NOT_EVIDENCED",
        "missing_work_proofs": [
            "SOURCE_BOUND_WORK_ID", "SOURCE_REVISION", "ELIGIBILITY_CENSUS",
            "CAPABILITY_AND_AUTHORITY_PROBE", "ACTION_OR_REASON",
            "INDEPENDENT_RECEIVER_READPROOF", "NEXT_QUALIFIED_WAKE",
        ],
        "private_identifiers_retained": False,
        "nonclaims": ["RUN_RECORD_NE_ELIGIBILITY_CENSUS", "NO_UPDATE_NE_HEALTHY_IDLE",
                      "PROVIDER_RUN_NE_USEFUL_EFFECT", "CHAT_REF_NE_RECEIVER_ACK"],
    }
    if not isinstance(task_record, dict):
        base["transport_state"] = "INVALID_TASK_METADATA"
        return base
    details = task_record.get("run_details")
    if not isinstance(details, dict):
        base["transport_state"] = "NO_RUN_DETAIL_AVAILABLE"
        return base
    record = details.get("last_run")
    if record is None:
        base["transport_state"] = "NO_RUN_RECORD_AVAILABLE"
        return base
    if not isinstance(record, dict):
        base["transport_state"] = "INVALID_RUN_RECORD"
        return base
    base["run_identity_present"] = isinstance(record.get("id"), str) and bool(record.get("id"))
    if not base["run_identity_present"]:
        base["transport_state"] = "INVALID_RUN_IDENTITY"
        return base
    try:
        scheduled = _utc(record.get("scheduled_for"))
        started = _utc(record.get("started_at"))
        completed = _utc(record.get("completed_at"))
    except ValueError:
        base["transport_state"] = "INVALID_RUN_TIME"
        return base
    if not started <= completed <= now:
        base["transport_state"] = "CONTRADICTORY_RUN_TIME"
        return base
    base["scheduled_for_utc"] = _iso(scheduled)
    base["started_at_utc"] = _iso(started)
    base["completed_at_utc"] = _iso(completed)
    base["start_lag_seconds"] = round((started - scheduled).total_seconds(), 3)
    base["execution_duration_seconds"] = round((completed - started).total_seconds(), 3)
    status = record.get("recorded_status")
    if status == "no_update":
        base["transport_state"] = "RECORDED_NO_UPDATE__CAUSE_UNKNOWN"
        base["recorded_status_class"] = "NO_UPDATE"
    elif status == "completed":
        base["transport_state"] = "RECORDED_COMPLETED__WORK_UNVERIFIED"
        base["recorded_status_class"] = "COMPLETED"
    elif status in ("failed", "cancelled"):
        base["transport_state"] = "RECORDED_NON_SUCCESS_RUN"
        base["recorded_status_class"] = status.upper()
    else:
        base["transport_state"] = "UNKNOWN_RECORDED_STATUS"
    return base
