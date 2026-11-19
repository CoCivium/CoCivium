"""CoStel R5: pure, bounded bridge-independent post-boot evidence classifier.

This is NOT a bridge, native agent, process launcher, remote shell, daemon,
Windows startup registration, network client, or external receiver. It turns
one already-observed, privacy-minimized cohort into an honest HOLD or narrow
reported-time observation. Its output is NOT authorization to run anything.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import sys
from typing import Any, Mapping

INPUT_SCHEMA = "CoStel.BridgeRecoveryCohort.Input.R0"
OUTPUT_SCHEMA = "CoStel.BridgeRecoveryCohort.Decision.R0"
LOCAL_SOURCES = frozenset({"USER_RETURNED_PS7", "AUTHENTICATED_LOCAL_READBACK", "NONE"})
ROUTE_KINDS = frozenset({
    "DESKTOP_COMMANDER", "COPING_TRUSTED_DROP", "COSTEAD_NATIVE_RECEIVER",
    "COBAR_LOCAL", "COALL_DESKTOP", "OTHER_REDACTED"
})
ROUTE_STATES = frozenset({"ONLINE", "OFFLINE", "DEGRADED", "UNKNOWN"})
MAX_ROUTES = 12
MAX_LOCAL_AGE = timedelta(minutes=10)
MAX_REMOTE_AGE = timedelta(minutes=20)


def _timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or len(value) > 48:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _required_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("HOLD_EXPECTED_MAPPING_" + label)
    return value


def classify(source: Mapping[str, Any], *, at_utc: datetime | None = None) -> dict[str, Any]:
    """No side effects. Unknown fields are ignored, never re-emitted.

    Distinct named adapters are NOT independently authenticated trust roots.
    Data can be claimed by a caller, so no number of reports qualifies 3ind.
    """
    source = _required_mapping(source, "ROOT")
    if source.get("schema") != INPUT_SCHEMA:
        raise ValueError("HOLD_SOURCE_SCHEMA")
    now = at_utc if at_utc is not None else datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None:
        raise ValueError("HOLD_NOW_MUST_BE_AWARE")
    now = now.astimezone(timezone.utc)

    local = _required_mapping(source.get("local_observation"), "LOCAL")
    task = _required_mapping(source.get("task"), "TASK")
    local_source = local.get("kind")
    if local_source not in LOCAL_SOURCES or type(local.get("read_only")) is not bool:
        raise ValueError("HOLD_LOCAL_SOURCE_ROLE_OR_SCOPE")

    observed = _timestamp(source.get("observed_at_utc"))
    boot = _timestamp(source.get("boot_time_utc"))
    if observed is None or boot is None or boot > observed:
        cohort = "BOOT_COHORT_UNQUALIFIED"
    else:
        cohort = "BOOT_TIME_REPORTED_IN_SAME_SNAPSHOT"
    freshness = bool(observed and timedelta(0) <= now - observed <= MAX_LOCAL_AGE)
    local_observed = bool(
        local_source != "NONE" and local["read_only"] is True
        and cohort == "BOOT_TIME_REPORTED_IN_SAME_SNAPSHOT" and freshness
    )

    if type(task.get("registered")) is not bool or type(task.get("runner_matches_pin")) is not bool:
        raise ValueError("HOLD_TASK_REGISTRATION_MALFORMED")
    if task.get("state") not in ("READY", "RUNNING", "DISABLED", "NOT_FOUND", "UNKNOWN"):
        raise ValueError("HOLD_TASK_STATE_MALFORMED")
    last_result = task.get("last_result")
    if last_result is not None and (type(last_result) is not int or not -2147483648 <= last_result <= 2147483647):
        raise ValueError("HOLD_TASK_EXIT_MALFORMED")

    last_run_raw = task.get("last_run_utc")
    last_run = _timestamp(last_run_raw)
    if last_run_raw is None:
        last_run_state = "NOT_REPORTED"
    elif last_run is None or observed is None or boot is None:
        last_run_state = "INVALID_OR_UNQUALIFIED_TIMESTAMP"
    elif last_run > observed or last_run > now:
        last_run_state = "CONFLICTING_FUTURE_TIMESTAMP"
    elif last_run <= boot:
        last_run_state = "NOT_AFTER_REPORTED_BOOT"
    else:
        last_run_state = "AFTER_BOOT_TIMESTAMP_REPORTED_ONLY"

    if not local_observed:
        postboot = "HOLD_LOCAL_BOOT_COHORT_UNQUALIFIED"
    elif not task["registered"] or not task["runner_matches_pin"]:
        postboot = "HOLD_TASK_OWNER_OR_SOURCE_NOT_BOUND"
    elif last_run_state == "AFTER_BOOT_TIMESTAMP_REPORTED_ONLY":
        postboot = "REPORTED_TASK_RUN_AFTER_BOOT_NOT_EFFECT_PROOF"
    else:
        postboot = "HOLD_POSTBOOT_EXECUTION_NOT_PROVEN"

    routes = source.get("routes")
    if not isinstance(routes, list) or len(routes) > MAX_ROUTES:
        raise ValueError("HOLD_ROUTE_COUNT_OR_TYPE")
    route_latest: dict[str, tuple[str, datetime | None]] = {}
    for item in routes:
        r = _required_mapping(item, "ROUTE")
        kind, state = r.get("adapter"), r.get("state")
        if kind not in ROUTE_KINDS or state not in ROUTE_STATES:
            raise ValueError("HOLD_UNKNOWN_ROUTE_OR_STATE")
        when = _timestamp(r.get("observed_at_utc"))
        if when is None or when > now:
            raise ValueError("HOLD_UNQUALIFIED_ROUTE_TIME")
        # Conflicts at the same timestamp are held, not newest-status-wins.
        prior = route_latest.get(kind)
        if prior is not None and prior[1] == when and prior[0] != state:
            raise ValueError("HOLD_CONFLICTING_SAME_TIME_ROUTE")
        if prior is None or prior[1] < when:
            route_latest[kind] = (state, when)

    def effective(name: str) -> str:
        data = route_latest.get(name)
        if data is None:
            return "UNOBSERVED"
        state, when = data
        return state if timedelta(0) <= now - when <= MAX_REMOTE_AGE else "STALE_UNQUALIFIED"

    desktop_commander = effective("DESKTOP_COMMANDER")
    if local_observed and desktop_commander == "OFFLINE":
        independence = "LOCAL_HOST_OBSERVED_WHILE_REMOTE_BRIDGE_OFFLINE"
        summary = "Local X2 diagnostic observed; Desktop Commander offline; post-boot useful work not yet proved."
    elif local_observed:
        independence = "LOCAL_HOST_OBSERVED_REMOTE_ROUTE_NOT_ESTABLISHED"
        summary = "Local X2 diagnostic observed; automatic post-boot recovery still unproven."
    else:
        independence = "HOST_LIVENESS_NOT_QUALIFIED_BY_THIS_SNAPSHOT"
        summary = "Current host observation unqualified; no autonomous recovery conclusion."

    if not local_observed:
        next_safe_probe = "RECOVER_FRESH_READ_ONLY_HOST_BOOT_OBSERVATION_USING_EXISTING_ROUTE"
    elif last_run_state != "AFTER_BOOT_TIMESTAMP_REPORTED_ONLY":
        next_safe_probe = "READ_NATIVE_LAST_RUN_UTC_AND_MATCH_R20_RECEIPT_TO_BOOT_COHORT"
    else:
        next_safe_probe = "VERIFY_NEW_WORKID_RECEIPT_AND_INDEPENDENT_POSTBOOT_RECEIVER_READPROOF"

    return {
        "schema": OUTPUT_SCHEMA,
        "state": "HOLD_AUTONOMOUS_WALKAWAY_NOT_PROVEN",
        "source_class": "CLAIMED_OR_USER_RETURNED_READ_ONLY_OBSERVATIONS",
        "cohort": cohort,
        "fresh_local_snapshot": freshness,
        "local_host_observed": local_observed,
        "task_registration_reported": bool(local_observed and task["registered"] and task["runner_matches_pin"]),
        "task_last_result_zero_reported": bool(task["registered"] and last_result == 0),
        "last_run_time_state": last_run_state,
        "postboot_task_state": postboot,
        "desktop_commander_adapter": desktop_commander,
        "bridge_independence_observation": independence,
        "claimed_route_adapters_observed": len(route_latest),
        "authenticated_independent_failure_domains": "NOT_VERIFIED",
        "parent_failure_recovery": "NOT_TESTED",
        "new_work_autonomous_intake": "NOT_TESTED",
        "human_first_use": "NOT_ATTESTED",
        "public_release": "HOLD",
        "human_summary": summary,
        "next_safe_probe": next_safe_probe,
        "effects": {"process_starts": 0, "network_calls": 0, "file_writes": 0,
                    "scheduler_changes": 0, "registry_changes": 0, "authority_grants": 0},
        "nonclaims": [
            "BRIDGE_OFFLINE_NE_HOST_OFF",
            "TASK_READY_NE_POSTBOOT_EXECUTION",
            "LAST_RESULT_ZERO_NE_USEFUL_WORK",
            "SAME_PROVIDER_CLAIMS_NE_3IND",
            "OBSERVATION_NE_COMMAND_AUTHORITY",
            "NO_REBOOT_RECOVERY_ACCEPTANCE",
            "NO_X2_EXECUTION_BY_THIS_CLASSIFIER",
            "NO_COEX_OR_RECEIVER_ACK"
        ],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Read-only CoStel bridge recovery cohort classifier")
    p.add_argument("--input", default="-", help="Local redacted JSON input or '-' for stdin")
    args = p.parse_args(argv)
    try:
        if args.input == "-":
            raw = sys.stdin.buffer.read(65537)
        else:
            with open(args.input, "rb") as inp:
                raw = inp.read(65537)
        if len(raw) > 65536:
            raise ValueError("HOLD_INPUT_TOO_LARGE")
        result = classify(json.loads(raw))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as e:
        print(json.dumps({"schema": OUTPUT_SCHEMA, "state": "HOLD_INVALID_SOURCE",
                          "error_class": type(e).__name__}, sort_keys=True))
        return 4
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
