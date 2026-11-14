#!/usr/bin/env python3
"""CoEyes Reality/CoOpportunity R0: deterministic, no-actuation evidence adjudicator.

Consumes privacy-filtered source observations. Video/animation and desktop text
never prove a process, interaction, causal effect, receiver or device health.
Windows inventory is a separate, read-only adapter; this script makes no OS calls.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

SCHEMA = "CoAll.CoEyes.RealityAndOpportunity.R0.SYNTHETIC"
HEX256 = re.compile(r"^[0-9a-f]{64}$")
MAX_AGE_SECONDS = 120
NOCLAIMS = [
    "VISUAL_MOTION_NE_LIVE_RUNTIME",
    "APP_PROCESS_NE_APP_RESPONSIVE",
    "RESPONSIVE_NE_USEFUL_EFFECT",
    "TEMPORAL_CORRELATION_NE_CAUSATION",
    "RECEIPT_CONSISTENCY_NE_SIGNED_AUTHENTICITY",
    "SOURCE_ID_NE_TRUSTED_OBSERVER",
    "SIMULATED_OBSERVER_NE_INDEPENDENT_PROVIDER",
    "FORECAST_NE_FACT_OR_ACTION_AUTHORITY",
    "USER_REPORT_NE_OS_PROCESS_ATTRIBUTION",
    "RESTART_REQUEST_NE_RESTART_AUTHORITY",
    "PRODUCTIZED_PROBE_NE_DEPLOYMENT",
]

def at(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("INVALID_TIMESTAMP")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError("INVALID_TIMESTAMP") from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("NAIVE_TIMESTAMP")
    return dt.astimezone(timezone.utc)

def observed(ob: dict | None, now: datetime) -> bool:
    if ob is None:
        return False
    if not isinstance(ob, dict) or not isinstance(ob.get("observer_id"), str) or not ob["observer_id"]:
        raise ValueError("SOURCE_OBSERVER_REQUIRED")
    time = at(ob.get("observed_at"))
    delta = (now - time).total_seconds()
    if delta < -2:
        raise ValueError("CLOCK_FUTURE_HELD")
    return 0 <= delta <= MAX_AGE_SECONDS

def checked_sha(s: str | None) -> bool:
    return isinstance(s, str) and HEX256.fullmatch(s) is not None

def reality(p: dict, now: datetime) -> dict:
    visual = p.get("visual")
    process = p.get("process")
    response = p.get("response")
    receiver = p.get("receiver")
    effect = p.get("effect")
    valid = {name: observed(v, now) for name, v in
             (("visual", visual), ("process", process),
              ("response", response), ("receiver", receiver), ("effect", effect))}
    appearance = "UNKNOWN"
    if valid["visual"]:
        if visual.get("kind") == "STATIC_WALLPAPER":
            appearance = "STATIC_ARTWORK"
        elif visual.get("kind") == "VIDEO_OR_ANIMATION":
            appearance = "MOTION_DEPICTED_NOT_LIVENESS"
        elif visual.get("kind") == "WINDOW_VIEW":
            appearance = "WINDOW_APPEARANCE_ONLY"
        else:
            raise ValueError("UNKNOWN_VISUAL_SOURCE_KIND")
    state = "UNKNOWN"
    evidence = []
    if appearance != "UNKNOWN":
        state = "APPEARANCE_ONLY"
        evidence.append("VISUAL_ONLY")
    if process is not None and valid["process"]:
        if process.get("present") is not True:
            if process.get("present") is False and process.get("coverage") == "COMPLETE_FOR_DECLARED_SCOPE":
                state = "PROCESS_NOT_FOUND_IN_SCOPE"
                evidence.append("COMPLETE_DECLARED_SCOPE")
            else:
                state = "UNKNOWN"
        else:
            if not isinstance(process.get("process_id"), int) or isinstance(process.get("process_id"), bool) or process["process_id"] <= 0:
                raise ValueError("INVALID_PID")
            state = "PROCESS_PRESENT_UNPROVEN_RESPONSIVE"
            evidence.append("PROCESS_OBSERVED")
    qualified_response = False
    if valid["response"] and valid["process"] and process.get("present") is True:
        qualified_response = (
            response.get("ok") is True and
            response.get("process_id") == process.get("process_id") and
            response.get("challenge_id") not in (None, "") and
            checked_sha(response.get("source_sha256")) and
            at(response["observed_at"]) >= at(process["observed_at"])
        )
        if qualified_response:
            state = "RESPONSIVE_FOR_DECLARED_SCOPE"
            evidence.append("CORRELATED_RESPONSE")
    if valid["receiver"] and qualified_response:
        if (receiver.get("challenge_id") == response.get("challenge_id") and
            receiver.get("source_sha256") == response.get("source_sha256") and
            receiver.get("observer_id") != response.get("observer_id") and
            at(receiver["observed_at"]) >= at(response["observed_at"])):
            state = "RECEIVER_READBACK_CONSISTENT"
            evidence.append("RECEIVER_ORIGIN_DIFFERENT_LABEL")
    if valid["effect"] and state == "RECEIVER_READBACK_CONSISTENT":
        if (effect.get("challenge_id") == response.get("challenge_id") and
            effect.get("source_sha256") == response.get("source_sha256") and
            effect.get("effect_class") == "BOUNDED_TEST_DELTA" and
            at(effect["observed_at"]) >= at(receiver["observed_at"])):
            state = "EFFECT_RECEIPT_CONSISTENT"
            evidence.append("EFFECT_REPORTED_NOT_CAUSAL_PROOF")
    if process and valid["process"] and process.get("present") is False and valid["response"] and response.get("ok") is True:
        state = "CONFLICT_HELD"
        evidence.append("PROCESS_RESPONSE_CONTRADICTION")
    if (visual or process or response or receiver or effect) and not any(valid.values()):
        state = "STALE_OR_UNOBSERVED"
    return {"state": state, "appearance": appearance, "evidence": evidence,
            "scope": "DECLARED_FIXTURE_ONLY", "source_authenticity": "NOT_CHECKED",
            "effect_proven_in_real_world": False}

def opportunity(events: list[dict], now: datetime, route: str) -> dict:
    if route not in ("CONNECTED", "OFFLINE", "UNKNOWN"):
        raise ValueError("UNKNOWN_ROUTE")
    if not isinstance(events, list) or len(events) > 256:
        raise ValueError("EVENT_BUDGET_EXCEEDED")
    ids = set()
    valid = []
    for e in events:
        if not isinstance(e, dict) or not isinstance(e.get("event_id"), str) or not e["event_id"]:
            raise ValueError("EVENT_ID_REQUIRED")
        if e["event_id"] in ids:
            continue
        ids.add(e["event_id"])
        if e.get("kind") != "FOREGROUND_CONSOLE_INTRUSION":
            continue
        if e.get("source_type") not in ("USER_REPORT", "OS_WINDOW_METADATA"):
            raise ValueError("UNTRUSTED_EVENT_CLASS")
        if not isinstance(e.get("owner_ref"), str):
            raise ValueError("OWNER_REF_REQUIRED")
        when = at(e.get("observed_at"))
        age = (now - when).total_seconds()
        if age < -2:
            raise ValueError("CLOCK_FUTURE_HELD")
        if 0 <= age <= 1800:
            valid.append((e, when))
    valid.sort(key=lambda x: x[1])
    if not valid:
        return {"state": "NO_FRESH_VERIFIED_EVENT_SERIES",
                "count": 0, "next": "DORMANT_UNTIL_MATERIAL_OBSERVATION",
                "forecast": "UNAVAILABLE", "measured_human_savings": None}
    groups = {}
    for e, t in valid:
        groups.setdefault(e["owner_ref"] or "UNKNOWN_OWNER", []).append((e, t))
    owner, series = max(groups.items(), key=lambda item: (len(item[1]), item[0]))
    trust = all(e["source_type"] == "OS_WINDOW_METADATA" for e, _ in series)
    owner_ok = owner != "UNKNOWN_OWNER" and trust and all(e.get("ownership") == "ATTRIBUTED_FOR_SCOPE" for e, _ in series)
    num = len(series)
    if num >= 3 and owner_ok:
        state = "REVIEW_BOUNDED_LAUNCHER_REPAIR"
    elif num >= 3:
        state = "TRACE_REPEAT_INTERRUPTIONS"
    else:
        state = "CAPTURE_OWNER_READ_ONLY"
    next_step = ("HOLD_REMOTE_OFFLINE_NO_RESTART" if route != "CONNECTED" else
                 "READ_ONLY_PROCESS_TASK_WINDOW_ATTRIBUTION")
    if state == "REVIEW_BOUNDED_LAUNCHER_REPAIR" and route == "CONNECTED":
        next_step = "REVIEW_OWNED_LAUNCHER_HEADLESS_CANARY_NO_AUTOMATIC_CHANGE"
    forecast = "UNAVAILABLE"
    if len(series) >= 3 and trust:
        intervals = [(series[i][1]-series[i-1][1]).total_seconds() for i in range(1, len(series))]
        avg = sum(intervals) / len(intervals)
        if 30 <= avg <= 1200 and all(abs(x-avg) <= 0.2*avg for x in intervals):
            forecast = {
                "epistemic_class": "SHORT_HORIZON_UNCALIBRATED_PREDICTION",
                "predicted_at": (series[-1][1] + timedelta(seconds=avg)).isoformat(),
                "period_seconds": round(avg, 2),
                "action_authority": "NONE",
                "alternative": "SHARED_TIMER_OR_OTHER_CAUSE_UNTESTED",
            }
    return {"state": state, "count": num, "next": next_step,
            "owner_class": "ATTRIBUTED_LOCAL" if owner_ok else "UNRESOLVED",
            "forecast": forecast, "measured_human_savings": None,
            "actual_popup_cause": "NOT_ESTABLISHED"}

def assess(data: dict) -> dict:
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError("INVALID_SCHEMA")
    now = at(data.get("as_of"))
    if not isinstance(data.get("surface"), dict):
        raise ValueError("SURFACE_OBJECT_REQUIRED")
    return {
        "schema": "CoAll.CoEyes.RealityAndOpportunity.Decision.R0",
        "source_schema": SCHEMA,
        "as_of": now.isoformat(),
        "surface": reality(data["surface"], now),
        "popup_opportunity": opportunity(data.get("events", []), now, data.get("remote_route", "UNKNOWN")),
        "decision_authority": "READ_ONLY_SIMULATION",
        "actual_process_restart": "NOT_ATTEMPTED",
        "camera_audio_screen_capture": "NOT_PERFORMED",
        "actual_X2_acceptance": "NOT_OBSERVED",
        "live_automation_installed": False,
        "nonclaims": list(NOCLAIMS),
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("fixture", help="Synthetic privacy-filtered JSON input")
    args = p.parse_args()
    with open(args.fixture, encoding="utf-8") as handle:
        data = json.load(handle)
    print(json.dumps(assess(data), sort_keys=True, indent=2))

if __name__ == "__main__":
    main()
