#!/usr/bin/env python3
"""CoSpeedo+ R0: strict, offline evidence-ledger audit.

Reads only the two elected public JSONL evidence sources, without network,
scheduler, model, device, account, browser, or other effects.

Event counts are SOURCE ACTIVITY. They are not useful outcomes, receiver ACK,
CoEx, or evidence of exponential scaling. Unknown outcome metrics stay null.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

SCHEMA = "CoCivium.CoSpeedo.EvidenceAudit.R0"
SOURCE_SPECS = (
    ("ai/benchmark-evo.jsonl", "id", "observed_at", "status"),
    ("benchmarks/evo.jsonl", "wave", "ts", "state"),
)
MAX_FILE_BYTES = 5_000_000
MAX_RECORDS = 20_000
MAX_LINE_CHARS = 500_000


class LedgerError(ValueError):
    pass


def observed_day(value: object) -> str:
    if not isinstance(value, str):
        raise LedgerError("MISSING_OR_NONSTRING_OBSERVATION_TIME")
    try:
        if len(value) == 10:
            return date.fromisoformat(value).isoformat()
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if instant.tzinfo is None:
            raise LedgerError("OBSERVATION_TIMESTAMP_MISSING_TZ")
        return instant.astimezone(timezone.utc).date().isoformat()
    except ValueError as exc:
        if isinstance(exc, LedgerError):
            raise
        raise LedgerError("UNPARSEABLE_OBSERVATION_TIME") from exc


def read_source(root: Path, rel: str, identity: str, when: str, status: str) -> dict:
    path = root / rel
    try:
        if not path.is_file():
            raise LedgerError(f"MISSING_ELECTED_LEDGER:{rel}")
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            raise LedgerError(f"LEDGER_TOO_LARGE:{rel}")
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="strict")
    except OSError as exc:
        raise LedgerError(f"UNREADABLE_ELECTED_LEDGER:{rel}") from exc
    except UnicodeError as exc:
        raise LedgerError(f"INVALID_UTF8:{rel}") from exc

    rows = text.splitlines()
    if len(rows) > MAX_RECORDS:
        raise LedgerError(f"TOO_MANY_ROWS:{rel}")
    seen, parsed = set(), []
    states, days = Counter(), Counter()
    for line_no, line in enumerate(rows, start=1):
        if not line.strip():
            raise LedgerError(f"EMPTY_INTERIOR_JSONL_ROW:{rel}:{line_no}")
        if len(line) > MAX_LINE_CHARS:
            raise LedgerError(f"ROW_TOO_LARGE:{rel}:{line_no}")
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise LedgerError(f"INVALID_JSONL:{rel}:{line_no}:{exc.pos}") from exc
        if not isinstance(obj, dict):
            raise LedgerError(f"NOT_OBJECT:{rel}:{line_no}")
        key = obj.get(identity)
        if not isinstance(key, str) or not key:
            raise LedgerError(f"MISSING_RECORD_ID:{rel}:{line_no}")
        if key in seen:
            raise LedgerError(f"DUPLICATE_RECORD_ID:{rel}:{line_no}")
        seen.add(key)
        state = obj.get(status)
        if not isinstance(state, str) or not state:
            raise LedgerError(f"MISSING_STATE:{rel}:{line_no}")
        if rel.startswith("ai/") and state not in {"PASS", "HELD", "FAIL"}:
            raise LedgerError(f"INVALID_SCOPED_TEST_STATUS:{rel}:{line_no}")
        day = observed_day(obj.get(when))
        states[state] += 1
        days[day] += 1
        parsed.append({"identity": key, "day": day, "state": state})

    return {
        "path": rel,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "physical_jsonl_rows": len(parsed),
        "unique_record_ids": len(seen),
        "states": dict(sorted(states.items())),
        "observed_rows_by_utc_day": dict(sorted(days.items())),
        "_records": parsed,
    }


def build_report(root: Path, as_of: date) -> dict:
    sources = [read_source(root, *args) for args in SOURCE_SPECS]
    start = as_of - timedelta(days=6)
    window = []
    for n in range(7):
        day = (start + timedelta(days=n)).isoformat()
        per = {s["path"]: s["observed_rows_by_utc_day"].get(day, 0) for s in sources}
        count = sum(per.values())
        window.append({
            "utc_day": day,
            "sampled_evidence_records": count,
            "by_elected_ledger": per,
            "coverage": "ROWS_OBSERVED_IN_TWO_LEDGERS" if count else "NO_ROWS_OBSERVED_IN_TWO_LEDGERS_NOT_GLOBAL_ZERO",
        })
    for s in sources:
        s.pop("_records")
    return {
        "schema": SCHEMA,
        "as_of_utc_day": as_of.isoformat(),
        "window_start_utc_day": start.isoformat(),
        "window_end_utc_day": as_of.isoformat(),
        "source_checks": sources,
        "sampled_daily_activity": window,
        "sampled_total_rows": sum(s["physical_jsonl_rows"] for s in sources),
        "metrics": {
            "CoAtomicDebt": {"value": None, "state": "UNKNOWN", "reason": "No complete, stable unique-work/closure census"},
            "CoClosureYield": {"value": None, "state": "UNKNOWN", "reason": "No comparable independent receiver-accepted outcome windows"},
            "CoSpeedoBenefitAcceleration": {"value": None, "state": "NOT_ESTABLISHED", "reason": "Activity/test records are not outcome, cost or manual-touch time series"},
            "CoTurtleCompoundingGain": {"value": None, "state": "NOT_ESTABLISHED", "reason": "No comparable recursive improvement/cost measurements"},
            "InternalRecurringProductRatio": {"value": None, "state": "UNKNOWN", "reason": "Provider scheduled runs and productized receiver acceptance are separate evidence classes"},
        },
        "effects": {
            "network_calls": 0, "provider_tasks_started": 0,
            "local_workers_started": 0, "publications": 0,
            "device_effects": 0, "receiver_acks_asserted": 0,
        },
        "nonclaims": [
            "ROW_COUNT_NE_USEFUL_CLOSURE",
            "STATUS_PASS_NE_RECEIVER_ACK",
            "MISSING_WINDOW_NE_ZERO_PROGRESS",
            "GROWING_ARTIFACTS_NE_EXPONENTIAL_BENEFIT",
            "LOG_PARSE_PASS_NE_SEMANTIC_COVERAGE",
            "SOURCE_RECEIPT_NE_COEX",
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--as-of", type=date.fromisoformat, default=datetime.now(timezone.utc).date())
    args = parser.parse_args(argv)
    try:
        report = build_report(args.root, args.as_of)
    except (LedgerError, OSError) as exc:
        print(f"FAIL_CLOSED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
