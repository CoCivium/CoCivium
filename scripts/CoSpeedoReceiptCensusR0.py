#!/usr/bin/env python3
"""Build a bounded CoSpeedo receipt census from benchmark-evo.jsonl.

The census counts exact ledger rows only. It does not infer useful closure,
receiver impact, adoption, cost, or exponential growth from PASS/FAIL/HELD
activity counts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, timedelta
from pathlib import Path

ALLOWED = {"PASS", "FAIL", "HELD", "NOT_RUN"}


def parse_date(value: str) -> str:
    if not isinstance(value, str) or len(value) < 10:
        raise ValueError("observed_at must begin with YYYY-MM-DD")
    return value[:10]


def daterange(start: str, end: str):
    a = date.fromisoformat(start)
    b = date.fromisoformat(end)
    if b < a:
        raise ValueError("end before start")
    cur = a
    while cur <= b:
        yield cur.isoformat()
        cur += timedelta(days=1)


def canonical_row_hash(rows: list[dict]) -> str:
    raw = "\n".join(
        json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        for r in rows
    ).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def build(path: Path, start: str, end: str) -> dict:
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        obj = json.loads(line)
        status = obj.get("status")
        if status not in ALLOWED:
            raise ValueError(f"line {i}: unsupported status {status!r}")
        d = parse_date(obj.get("observed_at"))
        if start <= d <= end:
            rows.append(obj)

    by_date = {}
    for d in daterange(start, end):
        day = [r for r in rows if parse_date(r["observed_at"]) == d]
        counts = {k: 0 for k in sorted(ALLOWED)}
        for r in day:
            counts[r["status"]] += 1
        by_date[d] = {
            "ledger_rows": len(day),
            "status_counts": counts,
            "coverage_state": (
                "EXACT_LEDGER_ROWS_PRESENT"
                if day
                else "NO_LEDGER_ROWS__UNKNOWN_NE_ZERO"
            ),
        }

    return {
        "schema": "CoSpeedo.ReceiptCensus.R0.v0.1",
        "state": "EXACT_LEDGER_ACTIVITY_CENSUS__NOT_OUTCOME_METRICS",
        "source": str(path).replace("\\", "/"),
        "window": {"start": start, "end": end},
        "selected_row_count": len(rows),
        "selected_rows_sha256": canonical_row_hash(rows),
        "days": by_date,
        "rails": [
            "UNKNOWN_NE_ZERO",
            "PASS_COUNT_NE_USEFUL_CLOSURE",
            "LEDGER_ROW_NE_RECEIVER_EFFECT",
            "ACTIVITY_COUNT_NE_GROWTH_RATE",
            "MORE_ARTIFACTS_NE_EXPONENTIAL_USEFULNESS",
        ],
        "nonclaims": [
            "NO_EXPONENTIAL_CLAIM",
            "NO_CLOSURE_YIELD_INFERENCE",
            "NO_RECEIVER_RETURN_INFERENCE",
            "NO_COST_NORMALIZATION",
            "NO_ADOPTION_INFERENCE",
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("path", type=Path)
    p.add_argument("--start", default="2026-10-20")
    p.add_argument("--end", default="2026-10-26")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = build(args.path, args.start, args.end)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
