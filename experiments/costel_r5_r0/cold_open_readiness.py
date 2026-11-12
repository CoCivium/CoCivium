"""CoStel R0 cold-open classification from the existing read-only Windows inventory.

One source snapshot -> one small human summary + typed machine report.
No OS calls, launch, network, storage, credentials, UI focus, or external effects.
An inventory never by itself proves human experience or independent receiver ACK.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import sys
from typing import Any, Mapping

SOURCE_SCHEMA = "CoAll.CoRunnerStartupInventory.R0"
RESULT_SCHEMA = "CoAll.CoColdOpenDecision.R0"
MAX_OBSERVATION_AGE = timedelta(minutes=10)


def _utc(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc) if parsed.tzinfo else None


def _role_present(source: Mapping[str, Any], role: str) -> bool:
    candidates = source.get("peripheral_utility_process_candidates", [])
    return (isinstance(candidates, list) and any(
        isinstance(item, dict) and item.get("process_role") == role
        for item in candidates
    ))


def _audio_services(source: Mapping[str, Any]) -> bool:
    entries = source.get("audio_service_readback", [])
    if not isinstance(entries, list):
        return False
    running = {
        item.get("service_role")
        for item in entries
        if isinstance(item, dict) and item.get("status") == "RUNNING"
    }
    return {"Audiosrv", "AudioEndpointBuilder"} <= running


def _display_driver(source: Mapping[str, Any]) -> bool:
    modes = source.get("display_driver_modes", [])
    if not isinstance(modes, list):
        return False
    return any(
        isinstance(item, dict)
        and type(item.get("width_px")) is int and item["width_px"] > 0
        and type(item.get("height_px")) is int and item["height_px"] > 0
        for item in modes
    )



# Invert the desired first-use outcome into finite, inspectable prerequisites.
# This is a proof-plan, not a runtime supervisor, OS inventory, or permission.
ARRIVAL_PREREQUISITES: dict[str, tuple[str, ...]] = {
    "COARRIVAL_USABLE_DESKTOP": (
        "BOOT_COHORT_QUALIFIED", "INPUT_USABLE", "AUDIO_INTENT_RESPECTED",
        "DESKTOP_USABLE", "LOCAL_TASK_USABLE", "AUTO_RECOVERY_CONFIRMED",
    ),
    "INPUT_USABLE": ("MOUSE_UTILITY_PRESENT", "MOUSE_MAPPING_TESTED"),
    "AUDIO_INTENT_RESPECTED": ("AUDIO_SERVICES_PRESENT", "AUDIO_CHOICE_TESTED"),
    "DESKTOP_USABLE": (
        "VIDEO_MODE_PRESENT", "SCALE_AND_ALIGNMENT_TESTED",
        "NO_FOREGROUND_FOCUS_THEFT", "COBAR_INTERACTION_TESTED",
        "AMBIENT_BACKGROUND_PROJECTION_TESTED",
    ),
    "LOCAL_TASK_USABLE": ("LOCAL_MODEL_PROCESS_PRESENT", "LOCAL_MODEL_TASK_TESTED"),
    "AUTO_RECOVERY_CONFIRMED": (
        "PRESESSION_WAKE_PROVEN", "SAME_BOOT_RECEIVER_READPROOF",
        "NO_HUMAN_SESSION_CYCLING",
    ),
}


def trace_inverse_requirements(
    source_gates: Mapping[str, str],
    *,
    graph: Mapping[str, tuple[str, ...]] | None = None,
    root: str = "COARRIVAL_USABLE_DESKTOP",
    max_visits: int = 64,
    max_depth: int = 8,
) -> dict[str, Any]:
    """Fail-closed, bounded inverse traversal; never interprets data as authority.

    Explicit leaf evidence states: REPORTED_IN_SNAPSHOT, STALE_SNAPSHOT,
    UNKNOWN. Even all reported leaves cannot establish human UX acceptance.
    """
    selected = graph if graph is not None else ARRIVAL_PREREQUISITES
    if not isinstance(selected, Mapping) or not isinstance(source_gates, Mapping):
        raise ValueError("HOLD_INVALID_INVERSE_GRAPH")
    if type(max_visits) is not int or type(max_depth) is not int or max_visits < 1 or max_depth < 1:
        raise ValueError("HOLD_INVALID_INVERSE_BUDGET")

    visited = 0
    leaves: list[dict[str, Any]] = []

    def visit(gate: str, path: tuple[str, ...]) -> None:
        nonlocal visited
        if not isinstance(gate, str) or not gate or len(gate) > 100:
            raise ValueError("HOLD_INVALID_GATE_ID")
        if gate in path:
            raise ValueError("HOLD_CYCLIC_REQUIREMENT")
        if len(path) >= max_depth or visited >= max_visits:
            raise ValueError("HOLD_INVERSE_BUDGET_EXCEEDED")
        visited += 1
        next_path = (*path, gate)
        children = selected.get(gate)
        if children is None:
            state = source_gates.get(gate, "UNKNOWN")
            if state not in ("REPORTED_IN_SNAPSHOT", "STALE_SNAPSHOT", "UNKNOWN"):
                raise ValueError("HOLD_UNRECOGNIZED_GATE_EVIDENCE")
            leaves.append({"gate": gate, "evidence": state, "inverse_path": list(next_path)})
            return
        if not isinstance(children, (tuple, list)) or len(children) < 1 or len(children) > 16:
            raise ValueError("HOLD_INVALID_DEPENDENCIES")
        for child in children:
            visit(child, next_path)

    visit(root, ())
    missing = [entry for entry in leaves if entry["evidence"] != "REPORTED_IN_SNAPSHOT"]
    return {
        "root": root,
        "state": "REVERSE_REQUIREMENTS_ONLY_NOT_X2_RUNTIME_ACCEPTANCE",
        "visited_nodes": visited,
        "leaf_count": len(leaves),
        "inventory_indicated_count": len(leaves) - len(missing),
        "unverified_count": len(missing),
        "unverified_dependencies": missing,
        "all_paths": leaves,
        "actual_user_acceptance": "NOT_ATTESTED",
        "first_missing_dependency": missing[0]["gate"] if missing else None,
        "success_claim": False,
        "nonclaims": [
            "RECURSIVE_REQUIREMENT_NE_EXECUTED_RECOVERY",
            "INVENTORY_INDICATION_NE_FUNCTIONAL_INPUT_OUTPUT",
            "INVERSE_PATH_NE_AGENT_PERMISSION",
            "ALL_LEAVES_LISTED_NE_REAL_USER_ACCEPTANCE",
            "CYCLE_OR_BUDGET_FAILURE_NE_DEFAULT_PASS",
        ],
    }


def classify(source: Mapping[str, Any], *, at_utc: datetime | None = None) -> dict[str, Any]:
    """Conservative pure decision, reporting only whitelisted observations.

    The report deliberately cannot emit RUNTIME_PASS: process existence,
    service status and bootstrap timestamps do not prove post-reboot UX.
    """
    if not isinstance(source, dict) or source.get("schema") != SOURCE_SCHEMA:
        raise ValueError("HOLD_UNEXPECTED_SOURCE_SCHEMA")
    if source.get("state") != "READ_ONLY_LOCAL_WINDOWS_SNAPSHOT":
        raise ValueError("HOLD_UNQUALIFIED_SOURCE_STATE")
    now = at_utc or datetime.now(timezone.utc)
    if not isinstance(now, datetime) or now.tzinfo is None:
        raise ValueError("HOLD_NOW_REQUIRES_TIMEZONE")
    now = now.astimezone(timezone.utc)

    observed = _utc(source.get("observed_at_utc"))
    boot = _utc(source.get("boot_time_utc"))
    fresh = bool(observed and timedelta(0) <= now - observed <= MAX_OBSERVATION_AGE)
    boot_observed = bool(boot and observed and boot <= observed)
    reported_uptime = source.get("uptime_seconds_at_observation")
    uptime_qualified = bool(
        boot_observed and type(reported_uptime) is int and reported_uptime >= 0
        and abs((observed - boot).total_seconds() - reported_uptime) <= 300
    )

    services_running = _audio_services(source)
    mouse_present = _role_present(source, "MOUSE_UTILITY_CANDIDATE")
    local_model_present = _role_present(source, "LOCAL_MODEL_CANDIDATE")
    coall_exe_present = _role_present(source, "COALL_SURFACE_CANDIDATE")
    driver_mode = _display_driver(source)

    if not uptime_qualified:
        observation_state = "BOOT_INVENTORY_UNQUALIFIED"
        next_probe = "REQUALIFY_WINDOWS_BOOT_TIMESTAMP_AND_UPTIME_ON_AUTHORIZED_X2"
    elif not fresh:
        observation_state = "BOOT_INVENTORY_STALE"
        next_probe = "REFRESH_EXISTING_READ_ONLY_INVENTORY_ON_AUTHORIZED_X2"
    else:
        observation_state = "FRESH_BOOT_INVENTORY_ONLY"
        next_probe = "INDEPENDENT_POST_LOGIN_X2_UX_AND_RECEIVER_READBACK"

    # A snapshot can indicate low-level prerequisites, not lived usability.
    def indicated(condition: bool) -> str:
        if not condition:
            return "UNKNOWN"
        return "REPORTED_IN_SNAPSHOT" if fresh and uptime_qualified else "STALE_SNAPSHOT"

    inverse_gate_evidence = {
        "BOOT_COHORT_QUALIFIED": indicated(uptime_qualified),
        "MOUSE_UTILITY_PRESENT": indicated(mouse_present),
        "AUDIO_SERVICES_PRESENT": indicated(services_running),
        "VIDEO_MODE_PRESENT": indicated(driver_mode),
        "LOCAL_MODEL_PROCESS_PRESENT": indicated(local_model_present),
    }
    inverse = trace_inverse_requirements(inverse_gate_evidence)

    # Machine classes, never assertions that a human is comfortable or audio works.
    report = {
        "schema": RESULT_SCHEMA,
        "state": "HOLD_USABLE_DESKTOP_UNPROVEN",
        "source_schema": SOURCE_SCHEMA,
        "source_evidence_class": "PRODUCER_REPORTED_LOCAL_INVENTORY",
        "work_id": "CoDesktopPresence:ColdOpen:R0",
        "inverse_proof_tree": inverse,
        "observation_state": observation_state,
        "snapshot_fresh": fresh,
        "boot_timestamp_qualified": uptime_qualified,
        "boot_time_utc": boot.isoformat().replace("+00:00", "Z") if boot else None,
        "audio_services": "REPORTED_RUNNING" if services_running else "UNVERIFIED_OR_NOT_RUNNING",
        "actual_audio_mute_state": "UNKNOWN",
        "mouse_software": "PROCESS_CANDIDATE_PRESENT" if mouse_present else "NOT_ESTABLISHED",
        "mouse_mapping_functional": "UNKNOWN",
        "local_model": "PROCESS_CANDIDATE_PRESENT" if local_model_present else "NOT_ESTABLISHED",
        "local_model_response_tested": False,
        "coall_surface": "PROCESS_CANDIDATE_PRESENT" if coall_exe_present else "NOT_ESTABLISHED",
        "surface_functional": False,
        "display_driver_mode": "REPORTED" if driver_mode else "NOT_ESTABLISHED",
        "per_monitor_dpi_and_alignment": "UNKNOWN",
        "cocivium_owned_desktop_background": "NOT_ATTESTED",
        "post_login_automatic_recovery": "NOT_ATTESTED",
        "independent_receiver_readproof": "NOT_ATTESTED",
        "human_summary": (
            "Windows boot was sampled, but the usable CoCivium desktop was not verified."
            if uptime_qualified and fresh else
            "Desktop recovery is unverified; the Windows boot observation is missing or stale."
        ),
        "next_safe_probe": next_probe,
        "human_keyboard_action_required_by_this_classifier": False,
        "effects": {"process_started": 0, "startup_changed": 0,
                    "volume_changed": 0, "wallpaper_changed": 0,
                    "external_messages_sent": 0},
        "nonclaims": [
            "BOOT_TIMESTAMP_NE_AUTOMATIC_RESTORATION",
            "PROCESS_PRESENT_NE_FUNCTIONAL",
            "AUDIO_SERVICES_RUNNING_NE_UNMUTED",
            "MOUSE_PROCESS_NE_MAPPING_READY",
            "VIDEO_DRIVER_MODE_NE_DPI_OR_ALIGNMENT",
            "BRIDGE_OFFLINE_NE_HOST_OFF",
            "INVENTORY_NE_INDEPENDENT_RECEIVER_ACK",
            "SYNTHETIC_CI_NE_X2_RUNTIME_PASS",
            "VISIBLE_SURFACE_NE_USABLE_EXPERIENCE",
        ],
    }
    return report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Read one preexisting CoRunner inventory from stdin")
    p.add_argument("--at-utc", default=None, help="Test-only observation time, UTC ISO 8601")
    args = p.parse_args(argv)
    now = _utc(args.at_utc) if args.at_utc is not None else None
    if args.at_utc is not None and now is None:
        p.error("--at-utc must be timezone-aware UTC")
    try:
        data = json.load(sys.stdin)
        report = classify(data, at_utc=now)
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema": RESULT_SCHEMA, "state": "HOLD_INVALID_INPUT",
                          "error_class": type(exc).__name__}, sort_keys=True))
        return 2
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
