#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ALLOWED = {"PASS", "FAIL", "HELD"}


def validate(path: Path) -> dict:
    ids = set()
    counts = {key: 0 for key in sorted(ALLOWED)}
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError("benchmark evo log is empty")

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            raise ValueError(f"blank line at {line_number}")
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON at line {line_number}: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"line {line_number} must be a JSON object")

        for field in ("observed_at", "id", "status", "artifact", "test", "result"):
            value = row.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"line {line_number}: {field} must be nonblank")

        if row["status"] not in ALLOWED:
            raise ValueError(f"line {line_number}: unsupported status {row['status']}")
        if row["id"] in ids:
            raise ValueError(f"line {line_number}: duplicate id {row['id']}")
        ids.add(row["id"])

        if row["status"] in {"PASS", "FAIL"}:
            ref = row.get("evidence_ref")
            if not isinstance(ref, str) or not ref.strip():
                raise ValueError(f"line {line_number}: PASS/FAIL requires evidence_ref")
        else:
            reason = row.get("hold_reason")
            if not isinstance(reason, str) or not reason.strip():
                raise ValueError(f"line {line_number}: HELD requires hold_reason")

        nonclaims = row.get("nonclaims")
        if not isinstance(nonclaims, list) or not nonclaims:
            raise ValueError(f"line {line_number}: nonclaims must be nonempty")
        if any(not isinstance(item, str) or not item.strip() for item in nonclaims):
            raise ValueError(f"line {line_number}: nonclaim must be nonblank")

        counts[row["status"]] += 1

    return {"records": len(lines), "counts": counts}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path", type=Path, nargs="?", default=Path("ai/benchmark-evo.jsonl")
    )
    args = parser.parse_args()
    try:
        result = validate(args.path)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
