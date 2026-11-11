"""CoGoAll scheduled-wake coverage observer R0.

Read-only retrospective audit of GitHub Actions run metadata. It never
self-certifies a scheduler, claims a real WorkID effect, spawns sessions,
or creates a receiver ACK. Missed observations are not failure attribution.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

UTC = dt.timezone.utc
NAME = "CoGoAll unattended proof pulse"
SCHEMA = "CoGoAll.ScheduleCoverage.R0"
SOURCE = "https://api.github.com/repos/CoCivium/CoCivium/actions/runs?event=schedule&per_page=100"


def instant(text: str) -> dt.datetime:
    if not isinstance(text, str):
        raise ValueError("TIMESTAMP_REQUIRED")
    try:
        result = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("INVALID_TIMESTAMP") from exc
    if result.tzinfo is None:
        raise ValueError("TIMEZONE_REQUIRED")
    return result.astimezone(UTC)


def coverage(runs: list[dict], *, observed_at: str,
             since: str = "2026-11-08T22:32:40Z",
             lookback_hours: int = 10, grace_minutes: int = 60,
             reported_total: int | None = None) -> dict:
    now, first = instant(observed_at), instant(since)
    if not 1 <= lookback_hours <= 24 or not 0 <= grace_minutes <= 180:
        raise ValueError("BOUNDED_LOOKBACK_REQUIRED")
    if not isinstance(runs, list) or len(runs) > 100:
        raise ValueError("INVALID_RUN_PAGE")
    start = max(first, now - dt.timedelta(hours=lookback_hours))
    eligible_deadline = now - dt.timedelta(minutes=grace_minutes)
    if eligible_deadline < start:
        ticks = []
    else:
        t = start.replace(minute=17, second=0, microsecond=0)
        if t < start:
            t += dt.timedelta(hours=1)
        ticks = []
        while t <= eligible_deadline:
            ticks.append(t)
            t += dt.timedelta(hours=1)
    seen_ids = set()
    observations = []
    for r in runs:
        if not isinstance(r, dict) or r.get("name") != NAME or r.get("event") != "schedule":
            continue
        identity = r.get("id")
        if not isinstance(identity, int) or identity <= 0 or identity in seen_ids:
            raise ValueError("INVALID_OR_DUPLICATE_RUN_ID")
        seen_ids.add(identity)
        timestamp = instant(r.get("created_at"))
        if timestamp > now:
            raise ValueError("FUTURE_RUN_OBSERVATION")
        if timestamp >= start:
            observations.append((timestamp, identity, r.get("conclusion")))
    observations.sort()
    matches = []
    missed = []
    used = set()
    for tick in ticks:
        possibilities = [
            (time, identity, state) for time, identity, state in observations
            if identity not in used and tick <= time <= tick + dt.timedelta(minutes=grace_minutes)
        ]
        if possibilities:
            timestamp, identity, state = min(possibilities)
            used.add(identity)
            matches.append({"tick": tick.isoformat(), "run_id": identity,
                            "created_at": timestamp.isoformat(), "conclusion": state})
        else:
            missed.append(tick.isoformat())
    # The API page can truncate older runs. Never infer gaps from a page
    # that does not cover the beginning of the requested lookback.
    censored = (reported_total is not None and reported_total > len(runs)
                and bool(runs) and
                min((instant(r["created_at"]) for r in runs if isinstance(r, dict)
                     and r.get("created_at")), default=now) > start)
    if censored:
        state = "HISTORY_CENSORED"
    elif missed:
        state = "SCHEDULE_TICKS_UNOBSERVED"
    elif not ticks:
        state = "INSUFFICIENT_MATURED_TICKS"
    elif any(m["conclusion"] != "success" for m in matches):
        state = "SCHEDULE_RUNS_NOT_ALL_SUCCESSFUL"
    else:
        state = "SCHEDULE_COVERAGE_OBSERVED"
    next_tick = now.replace(minute=17, second=0, microsecond=0)
    if next_tick <= now:
        next_tick += dt.timedelta(hours=1)
    return {
        "schema": SCHEMA, "state": state, "observed_at": now.isoformat(),
        "since": start.isoformat(), "expected_cron": "17 * * * *",
        "grace_minutes": grace_minutes, "expected_matured_ticks": len(ticks),
        "matched_scheduled_runs": matches, "unobserved_tick_times": missed,
        "next_expected_tick": next_tick.isoformat(),
        "source_uri": SOURCE, "source_readback": "GITHUB_API_RUN_METADATA",
        "confidence_boundary": "UNOBSERVED_TICK_NOT_PROOF_OF_PROVIDER_FAILURE",
        "independent_receiver_ack": False, "actual_work_effect": False,
        "native_x2_proof": False, "self_certified_continuity": False,
    }


def main() -> int:
    current = dt.datetime.now(UTC).isoformat()
    result = {"schema": SCHEMA, "state": "RUN_HISTORY_UNAVAILABLE",
              "observed_at": current, "source_uri": SOURCE,
              "actual_work_effect": False, "independent_receiver_ack": False}
    try:
        workflow = Path(".github/workflows/cogoall-unattended-proof-pulse.yml").read_text()
        if "- cron: '17 * * * *'" not in workflow:
            raise ValueError("WORKFLOW_CRON_MISMATCH")
        headers = {"Accept": "application/vnd.github+json",
                   "User-Agent": "CoCivium-CoGoAll-schedule-observer"}
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = "Bearer " + token
        with urlopen(Request(SOURCE, headers=headers), timeout=10) as response:
            data = json.load(response)
        if not isinstance(data, dict) or not isinstance(data.get("workflow_runs"), list):
            raise ValueError("MISSING_RUN_METADATA")
        result = coverage(data["workflow_runs"], observed_at=current,
                          reported_total=data.get("total_count"))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result["error_class"] = type(exc).__name__
        result["reason"] = str(exc)[:110] if isinstance(exc, ValueError) else "SOURCE_UNAVAILABLE"
        # No sensitive network data or bearer token returned.
    Path("schedule-audit.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("SCHEDULE_COVERAGE " + json.dumps({
        "state": result["state"], "expected": result.get("expected_matured_ticks"),
        "matched": len(result.get("matched_scheduled_runs", [])),
        "unobserved": len(result.get("unobserved_tick_times", [])),
        "next": result.get("next_expected_tick")
    }, sort_keys=True))
    return 0 if result["state"] != "RUN_HISTORY_UNAVAILABLE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
