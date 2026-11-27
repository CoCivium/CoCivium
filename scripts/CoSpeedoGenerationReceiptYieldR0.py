#!/usr/bin/env python3
"""Read-only CoSpeedo generation-aware receipt classifier.

No scheduler mutation, network, recursive scan or receiver-ACK inference.
A fresh local receipt is not an accepted useful product effect.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

UTC = dt.timezone.utc
SCHEMA = "CoSpeedo.GenerationReceiptYield.R0"


def parse_time(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timezone required")
    return parsed.astimezone(UTC)


def read_proof(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("receipt must be an object")
    return data, hashlib.sha256(raw).hexdigest()


def classify(
    *, observed_at: str, schedule_last_utc: str, schedule_exit: int,
    v04: dict | None, v04_written_utc: str | None, v05: dict | None,
    v05_written_utc: str | None, cursor: dict | None,
    freshness_minutes: int = 30,
) -> dict:
    now = parse_time(observed_at)
    if freshness_minutes <= 0:
        raise ValueError("freshness_minutes must be positive")
    scheduled = parse_time(schedule_last_utc)
    if scheduled > now:
        raise ValueError("future scheduler observation")
    if v04_written_utc and parse_time(v04_written_utc) > now:
        raise ValueError("future v0.4 receipt")
    if v05_written_utc and parse_time(v05_written_utc) > now:
        raise ValueError("future v0.5 receipt")
    fresh_v04 = bool(
        v04 and v04_written_utc and
        scheduled <= parse_time(v04_written_utc) and
        (now - parse_time(v04_written_utc)).total_seconds() <= 60 * freshness_minutes
    )
    fresh_v05 = bool(
        v05 and v05_written_utc and
        scheduled <= parse_time(v05_written_utc) and
        (now - parse_time(v05_written_utc)).total_seconds() <= 60 * freshness_minutes
    )
    bounded_v04_pass = bool(
        fresh_v04 and v04.get("STATE") == "PASS_COTIDAL_V04_BOUNDED_PARALLEL_EXECUTION_FANIN"
        and v04.get("LANES_HOLD") == 0 and v04.get("LANES_PASS", 0) >= 6
        and v04.get("EXTERNAL_NETWORK_ACTIONS") == 0
    )
    v05_semantic_pass = bool(
        fresh_v05 and str(v05.get("STATE", "")).startswith(
            "PASS_COTIDAL_V05_SEMANTIC_DRAIN_AND_BYTE_REHYDRATION_FANIN"
        )
    )
    if schedule_exit != 0:
        state = "SCHEDULER_FAILURE_REQUIRES_TRIAGE"
    elif bounded_v04_pass and v05_semantic_pass:
        state = "FRESH_V04_AND_V05_LOCAL_PROOF"
    elif bounded_v04_pass:
        state = "FRESH_V04_PROOF__V05_QUIET_OR_UNOBSERVED"
    elif fresh_v04:
        state = "FRESH_V04_NONPASS_OR_UNQUALIFIED"
    else:
        state = "NO_FRESH_QUALIFIED_RECEIPT__UNKNOWN_NOT_ZERO"
    unchanged_cursor_candidate = bool(
        cursor and cursor.get("candidate_byte_readproof") is True
        and not fresh_v05
    )
    return {
        "schema": SCHEMA,
        "state": state,
        "observed_at": now.isoformat(),
        "freshness_minutes": freshness_minutes,
        "schedule_last_utc": scheduled.isoformat(),
        "scheduler_exit": schedule_exit,
        "v04_fresh": fresh_v04,
        "v04_qualified_pass": bounded_v04_pass,
        "v05_fresh": fresh_v05,
        "v05_qualified_pass": v05_semantic_pass,
        "v05_no_change_hypothesis": "POSSIBLE_NOT_EXECUTION_PROVEN"
        if unchanged_cursor_candidate else "UNDETERMINED",
        "verified_receiver_relevant_delta_count": None,
        "receiver_ack": "NOT_OBSERVED",
        "rails": [
            "SCHEDULE_EXIT_ZERO_NE_USEFUL_DELTA",
            "V04_PASS_NE_PRODUCT_WORKID_COMPLETION",
            "MISSING_V05_RECEIPT_NE_STALL",
            "CURSOR_READPROOF_NE_EXACT_SKIP_EXECUTION",
            "LOCAL_RECEIPT_NE_RECEIVER_ACK",
            "UNKNOWN_NE_ZERO",
        ],
    }


def selftest() -> None:
    stamp = "2026-11-27T08:29:00Z"
    v04 = {"STATE": "PASS_COTIDAL_V04_BOUNDED_PARALLEL_EXECUTION_FANIN",
           "LANES_PASS": 6, "LANES_HOLD": 0, "EXTERNAL_NETWORK_ACTIONS": 0}
    base = dict(observed_at=stamp, schedule_last_utc="2026-11-27T08:23:15Z",
                schedule_exit=0, v04=v04, v04_written_utc="2026-11-27T08:24:34Z",
                v05=None, v05_written_utc=None,
                cursor={"candidate_byte_readproof": True})
    one = classify(**base)
    assert one["state"] == "FRESH_V04_PROOF__V05_QUIET_OR_UNOBSERVED"
    assert one["verified_receiver_relevant_delta_count"] is None
    assert one["v05_no_change_hypothesis"] == "POSSIBLE_NOT_EXECUTION_PROVEN"
    assert classify(**{**base, "schedule_exit": 1})["state"] == "SCHEDULER_FAILURE_REQUIRES_TRIAGE"
    assert classify(**{**base, "v04_written_utc": "2026-09-15T08:24:34Z"})["state"] == "NO_FRESH_QUALIFIED_RECEIPT__UNKNOWN_NOT_ZERO"
    assert classify(**{**base, "v04": {**v04, "LANES_HOLD": 1}})["state"] == "FRESH_V04_NONPASS_OR_UNQUALIFIED"
    assert classify(**{**base, "v04_written_utc": "2026-11-27T08:22:00Z"})["state"] == "NO_FRESH_QUALIFIED_RECEIPT__UNKNOWN_NOT_ZERO"
    assert classify(**{**base, "v05": {"STATE": "PASS_COTIDAL_V05_SEMANTIC_DRAIN_AND_BYTE_REHYDRATION_FANIN__DELETE_HARD_HELD"}, "v05_written_utc": "2026-11-27T08:22:00Z"})["v05_qualified_pass"] is False
    assert classify(**{**base, "v05": {"STATE": "PASS_COTIDAL_V05_SEMANTIC_DRAIN_AND_BYTE_REHYDRATION_FANIN__DELETE_HARD_HELD"},
                       "v05_written_utc": "2026-11-27T08:25:00Z"})["state"] == "FRESH_V04_AND_V05_LOCAL_PROOF"
    try:
        classify(**{**base, "v04_written_utc": "2026-11-28T00:00:00Z"})
        raise AssertionError("future receipt accepted")
    except ValueError:
        pass
    print("PASS_COSPEEDO_GENERATION_RECEIPT_EIGHT_FIXTURES")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--v04-receipt", type=Path)
    parser.add_argument("--v05-receipt", type=Path)
    parser.add_argument("--v05-cursor", type=Path)
    parser.add_argument("--v04-written-utc")
    parser.add_argument("--v05-written-utc")
    parser.add_argument("--schedule-last-utc")
    parser.add_argument("--schedule-exit", type=int)
    parser.add_argument("--observed-at")
    parser.add_argument("--freshness-minutes", type=int, default=30)
    args = parser.parse_args()
    if args.selftest:
        selftest()
        return 0
    if not args.v04_receipt or not args.schedule_last_utc or args.schedule_exit is None or not args.observed_at or not args.v04_written_utc:
        parser.error("v04 receipt, receipt write UTC, schedule last UTC, scheduler exit and observation UTC required")
    v04, sha04 = read_proof(args.v04_receipt)
    v05, sha05 = read_proof(args.v05_receipt) if args.v05_receipt else (None, None)
    cursor, cursor_sha = read_proof(args.v05_cursor) if args.v05_cursor else (None, None)
    result = classify(
        observed_at=args.observed_at, schedule_last_utc=args.schedule_last_utc,
        schedule_exit=args.schedule_exit, v04=v04, v04_written_utc=args.v04_written_utc,
        v05=v05, v05_written_utc=args.v05_written_utc, cursor=cursor,
        freshness_minutes=args.freshness_minutes,
    )
    result["source_receipts"] = {"v04_sha256": sha04, "v05_sha256": sha05, "cursor_sha256": cursor_sha}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
