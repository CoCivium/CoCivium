#!/usr/bin/env python3
"""Validate the append-only CoBenchmarkEvo ledger without flattening evidence scope.

R1 compatible with R0 rows and three legacy compact publication-only rows.
The CI check validates record integrity, not whether experiments succeeded.
FAIL and FAIL_SCOPED are preserved as recorded evidence rather than hidden.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path

# Explicit, fail-closed vocabulary. Other statuses need a reviewed schema change.
ALLOWED = {"PASS", "FAIL", "HELD", "FAIL_SCOPED", "PASS_PUBLICATION_ONLY"}

# These two immutable existing records preceded explicit hold_reason conventions.
# This compatibility exception is exact-ID-scoped, never a blanket waiver.
LEGACY_INLINE_HELD = {
    "benchmark-evo:cofireworks-frontdoor-rc1:held-effects-20261024",
    "benchmark-evo:comiddle-relationalgebra-r2:x2-media-provider-receivers",
}


def require_text(row: dict, field: str, line_number: int) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"line {line_number}: {field} must be nonblank")
    return value


def require_nonclaims(row: dict, line_number: int) -> None:
    nonclaims = row.get("nonclaims")
    if not isinstance(nonclaims, list) or not nonclaims:
        raise ValueError(f"line {line_number}: nonclaims must be nonempty")
    if any(not isinstance(item, str) or not item.strip() for item in nonclaims):
        raise ValueError(f"line {line_number}: nonclaim must be nonblank")


def validate(path: Path) -> dict:
    ids: set[str] = set()
    counts = {key: 0 for key in sorted(ALLOWED)}
    legacy_inline_holds: list[str] = []
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

        ident = require_text(row, "id", line_number)
        status = require_text(row, "status", line_number)
        if status not in ALLOWED:
            raise ValueError(f"line {line_number}: unsupported status {status}")
        if ident in ids:
            raise ValueError(f"line {line_number}: duplicate id {ident}")
        ids.add(ident)
        require_nonclaims(row, line_number)

        # Older publication-only records are deliberately narrower than generic PASS.
        # Their held gates are not permitted to silently become measured successes.
        compact_publication = (
            status == "PASS_PUBLICATION_ONLY" and "observed_at" not in row
        )
        if compact_publication:
            day = require_text(row, "date", line_number)
            try:
                if date.fromisoformat(day).isoformat() != day:
                    raise ValueError("noncanonical date")
            except ValueError as exc:
                raise ValueError(f"line {line_number}: invalid compact date {day}") from exc
            require_text(row, "scope", line_number)
            gates = row.get("gates")
            if not isinstance(gates, dict) or not gates:
                raise ValueError(f"line {line_number}: compact publication needs explicit gates")
            for gate_name, gate_state in gates.items():
                if not isinstance(gate_name, str) or not gate_name.strip():
                    raise ValueError(f"line {line_number}: gate name must be nonblank")
                if gate_state != "NOT_RUN_HELD":
                    raise ValueError(
                        f"line {line_number}: compact publication cannot promote gate {gate_name}"
                    )
        else:
            for field in ("observed_at", "artifact", "test", "result"):
                require_text(row, field, line_number)

        if status in {"PASS", "FAIL", "FAIL_SCOPED", "PASS_PUBLICATION_ONLY"}:
            require_text(row, "evidence_ref", line_number)
        else:
            reason = row.get("hold_reason")
            if not isinstance(reason, str) or not reason.strip():
                if ident not in LEGACY_INLINE_HELD:
                    raise ValueError(f"line {line_number}: HELD requires hold_reason")
                require_text(row, "evidence_ref", line_number)
                require_text(row, "result", line_number)
                legacy_inline_holds.append(ident)

        counts[status] += 1

    return {
        "records": len(lines),
        "counts": counts,
        "legacy_inline_hold_reasons": sorted(legacy_inline_holds),
        "nonclaims": [
            "LEDGER_VALID_NE_RUNTIME_PASS",
            "FAIL_SCOPED_REMAINS_NEGATIVE_EVIDENCE",
            "PASS_PUBLICATION_ONLY_NE_DEVICE_OR_RECEIVER_PASS",
            "CI_CHECK_NE_INDEPENDENT_REPRODUCTION",
        ],
    }


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
