"""CoFocus+ inverse triage of EXISTING CoRunner startup snapshot, no OS effects.

This module never proves a popup, window-focus theft, X2 liveness, or a repair.
A Task Scheduler action event is not a process/window/foreground event.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import re
from typing import Any, Mapping

SOURCE = "CoAll.CoRunnerStartupInventory.R0"
SCHEMA = "CoAll.CoFocusCausalChallenge.R0"
IDENTITY = re.compile(r"^other-sha256-[0-9a-f]{16}$")
ALLOWED = {"POWERSHELL7", "WINDOWS_POWERSHELL", "CMD", "PYTHON"}
STATES = {
    "OBSERVED_TASK_ACTION_HISTORY_ONLY",
    "PARTIAL_BOUNDED_HISTORY",
    "UNAVAILABLE_OR_EMPTY_UNQUALIFIED",
}
NO_CLAIMS = (
    "TASK_ACTION_NE_VISIBLE_WINDOW",
    "TASK_FREQUENCY_NE_FOCUS_THEFT_CAUSALITY",
    "TASK_END_EVENT_NE_WINDOW_CLOSED",
    "NO_SCHEDULER_EVENTS_NE_NO_POPUPS",
    "SNAPSHOT_NE_CONTINUOUS_MONITOR",
    "CI_NE_X2_OR_RUNTIME",
    "ALIVE_PROCESS_NE_USABLE_INPUT",
    "LOCAL_IS_NOT_LANDED",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
)


def utc(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, OverflowError):
        return None
    return dt.astimezone(timezone.utc) if dt.tzinfo else None


def natural(value: Any, ceiling: int) -> bool:
    return type(value) is int and 0 <= value <= ceiling


def base(state: str, why: str) -> dict:
    return {
        "schema": SCHEMA,
        "state": state,
        "reason": why,
        "scope": "READ_ONLY_SOURCE_SNAPSHOT_CLASSIFICATION",
        "popup_source_attributed": False,
        "focus_theft_confirmed": False,
        "x2_runtime_repaired": False,
        "receiver_ack": False,
        "candidate_launchers": [],
        "inverse_challenges": [],
        "relation_chain": [
            {"from": "SCHEDULED_TASK_ACTION", "to": "PROCESS_CREATION", "evidence": "NOT_JOINED"},
            {"from": "PROCESS_CREATION", "to": "VISIBLE_WINDOW", "evidence": "NOT_OBSERVED"},
            {"from": "VISIBLE_WINDOW", "to": "FOREGROUND_ACTIVATION", "evidence": "NOT_OBSERVED"},
            {"from": "FOREGROUND_ACTIVATION", "to": "INPUT_INTERRUPTION", "evidence": "USER_REPORT_ONLY_NOT_CORRELATED"},
        ],
        "next_safe_probe": "AUTHORIZE_EXACT_LOCAL_WINDOW_FOCUS_CORRELATION_USING_EXISTING_HOST_TOOLS_NO_WATCHER",
        "nonclaims": list(NO_CLAIMS),
    }


def classify(source: Mapping[str, Any], *, at_utc: datetime) -> dict:
    """Return a bounded decision from one already-collected source dictionary."""
    fail = lambda why: base("HOLD_UNQUALIFIED_EVIDENCE", why)
    if not isinstance(source, Mapping):
        return fail("MISSING_OR_NONOBJECT_SOURCE")
    if source.get("schema") != SOURCE or source.get("state") != "READ_ONLY_LOCAL_WINDOWS_SNAPSHOT":
        return fail("SOURCE_SCHEMA_OR_STATE_UNQUALIFIED")
    if source.get("raw_command_lines_emitted") is not False or source.get("credentials_or_tokens_emitted") is not False:
        return fail("SOURCE_PRIVACY_OR_AUTHORITY_UNQUALIFIED")
    if source.get("no_registry_or_task_writes") is not True or source.get("no_network_or_external_effect") is not True:
        return fail("SOURCE_EFFECTS_UNQUALIFIED")
    if not isinstance(at_utc, datetime) or at_utc.tzinfo is None:
        return fail("REVIEW_TIME_UNQUALIFIED")
    captured = utc(source.get("observed_at_utc"))
    if captured is None:
        return fail("SOURCE_TIME_UNQUALIFIED")
    age = (at_utc.astimezone(timezone.utc) - captured).total_seconds()
    if age < -5 or age > 600:
        return base("HOLD_STALE_OR_FUTURE_SNAPSHOT", "SOURCE_TIMESTAMP_OUTSIDE_TTL")
    history = source.get("existing_scheduler_action_history")
    if not isinstance(history, Mapping) or history.get("state") not in STATES:
        return fail("HISTORY_MISSING_OR_UNKNOWN")
    if history.get("raw_event_xml_task_names_paths_arguments_or_instance_ids_emitted") is not False:
        return fail("RAW_TASK_EVENT_PRIVACY_UNQUALIFIED")
    groups = history.get("candidate_groups")
    if not isinstance(groups, list) or len(groups) > 32:
        return fail("CANDIDATE_LIST_NOT_BOUNDED")
    if not natural(history.get("events_read"), 512):
        return fail("EVENT_COUNT_UNQUALIFIED")
    if history.get("max_events") != 512 or history.get("window_minutes") != 60:
        return fail("HISTORY_WINDOW_UNQUALIFIED")
    if type(history.get("truncated")) is not bool:
        return fail("TRUNCATION_FLAG_UNQUALIFIED")

    candidates = []
    seen = set()
    for g in groups:
        if not isinstance(g, Mapping):
            return fail("CANDIDATE_ROW_UNQUALIFIED")
        ref = g.get("task_identity")
        if not isinstance(ref, str) or not IDENTITY.fullmatch(ref) or ref in seen:
            return fail("CANDIDATE_IDENTITY_UNQUALIFIED")
        seen.add(ref)
        if g.get("launcher_class") not in ALLOWED:
            return fail("LAUNCHER_CLASS_UNQUALIFIED")
        if g.get("task_category") not in ("COALL_RELATED_CANDIDATE", "UNRELATED_OR_UNKNOWN"):
            return fail("TASK_CATEGORY_UNQUALIFIED")
        if g.get("console_flash_possible") is not True or g.get("popup_attributed") is not False:
            return fail("UNSUPPORTED_POPUP_CLAIM")
        n60, n15, prev, short = (
            g.get("starts_last_60m"), g.get("starts_last_15m"),
            g.get("starts_previous_15m"), g.get("paired_actions_le_3s"),
        )
        if not all(natural(n, 512) for n in (n60, n15, prev, short)):
            return fail("COUNTS_UNQUALIFIED")
        if n15 + prev > n60 or short > n60 or n60 > history["events_read"]:
            return fail("COUNT_RELATIONS_INCONSISTENT")
        candidates.append({
            "opaque_task_ref": ref,
            "launcher_class": g["launcher_class"],
            "task_category": g["task_category"],
            "starts_last_15m": n15,
            "starts_previous_15m": prev,
            "short_actions_last_60m": short,
            "evidence": "SCHEDULER_ACTION_ONLY",
            "popup_attributed": False,
        })

    if history["state"] == "UNAVAILABLE_OR_EMPTY_UNQUALIFIED":
        return base("HOLD_SCHEDULER_HISTORY_UNAVAILABLE", "DISABLED_EMPTY_OR_INACCESSIBLE_NOT_CLEAN")
    if history["state"] == "PARTIAL_BOUNDED_HISTORY" or history["truncated"]:
        return base("HOLD_PARTIAL_SCHEDULER_HISTORY", "HISTORY_TRUNCATED")
    if "TASK_ACTION_HISTORY_PARTIAL_PARSE" in source.get("observation_errors", []):
        return base("HOLD_PARTIAL_SCHEDULER_HISTORY", "HISTORY_PARSE_INCOMPLETE")
    result = base("CANDIDATES_ONLY_CAUSALITY_UNPROVEN", "SCHEDULER_LAUNCHES_NOT_WINDOW_WITNESS")
    candidates.sort(key=lambda g: (-g["starts_last_15m"], -g["short_actions_last_60m"], g["opaque_task_ref"]))
    result["candidate_launchers"] = candidates[:8]
    result["candidate_count"] = len(candidates)
    result["inverse_challenges"] = [
        "POPUP_WITHOUT_SCHEDULER_EVENT_IMPLICATES_DIFFERENT_OR_UNLOGGED_LAUNCH_PATH",
        "TASK_EVENT_WITHOUT_POPUP_SHOWS_EVENT_IS_NOT_SUFFICIENT_CAUSE",
        "POPUP_BEFORE_R5_LAUNCH_CHALLENGES_R5_AS_NECESSARY_CAUSE",
        "MATCHED_TIMES_WITHOUT_PID_WINDOW_FOCUS_JOIN_ARE_CORRELATION_ONLY",
    ]
    if not candidates:
        result["reason"] = "NO_CONSOLE_ACTION_IN_HISTORY_NOT_NO_POPUP"
    return result
