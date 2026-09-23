#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def parse_time(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError("FAIL_CLOSED__TIMEZONE_REQUIRED")
    return dt.astimezone(timezone.utc)


def load_object(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    obj = json.loads(raw.decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("FAIL_CLOSED__PRESSURE_NOT_OBJECT")
    return obj, raw


def evaluate(
    pressure: dict[str, Any],
    pressure_raw: bytes,
    evaluated_at: str,
    max_age_seconds: int,
    max_future_skew_seconds: int,
) -> dict[str, Any]:
    required = ("sample_id", "receiver_id", "sampled_at")
    missing = [k for k in required if not pressure.get(k)]
    if missing:
        raise ValueError("FAIL_CLOSED__PRESSURE_MISSING_FIELDS=" + ",".join(missing))
    if max_age_seconds < 0 or max_future_skew_seconds < 0:
        raise ValueError("FAIL_CLOSED__NEGATIVE_FRESHNESS_BOUND")

    sampled_dt = parse_time(str(pressure["sampled_at"]))
    evaluated_dt = parse_time(evaluated_at)
    age_seconds = int((evaluated_dt - sampled_dt).total_seconds())

    if age_seconds < -max_future_skew_seconds:
        state = "HOLD_FUTURE_PRESSURE_SAMPLE"
        nxt = "REACQUIRE_OR_REBIND_PRESSURE_SAMPLE_TIME"
    elif age_seconds > max_age_seconds:
        state = "HOLD_STALE_PRESSURE_SAMPLE"
        nxt = "REACQUIRE_RECEIVER_PRESSURE_BEFORE_BUDGET_ELECTION"
    else:
        state = "PASS_FRESH_PRESSURE_SAMPLE"
        nxt = "ELIGIBLE_FOR_R0E_DIGEST_BUDGET_ELECTION"

    result = {
        "schema": "CoPulsePressureFreshness.R0F.v0.1-candidate",
        "state": state,
        "receiver_id": str(pressure["receiver_id"]),
        "sample_id": str(pressure["sample_id"]),
        "pressure_input_sha256": sha256_bytes(pressure_raw),
        "sampled_at": str(pressure["sampled_at"]),
        "evaluated_at": evaluated_at,
        "age_seconds": age_seconds,
        "max_age_seconds": max_age_seconds,
        "max_future_skew_seconds": max_future_skew_seconds,
        "effects": {
            "capacity_mutation": 0,
            "receiver_context_mutation": 0,
            "ack_cursor_mutation": 0,
            "authority_change": 0,
        },
        "next": nxt,
        "nonclaims": [
            "FRESHNESS_NE_TRUTH",
            "FRESH_SAMPLE_NE_CAPACITY_ACCURACY_PROOF",
            "STALE_SAMPLE_NE_ZERO_CAPACITY",
            "PRESSURE_SAMPLE_NE_AUTHORITY",
            "OBSERVER_TIME_NE_GLOBAL_TIME",
        ],
    }
    result["freshness_sha256"] = sha256_bytes(canonical(result))
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pressure", required=True)
    ap.add_argument("--evaluated-at", required=True)
    ap.add_argument("--max-age-seconds", type=int, required=True)
    ap.add_argument("--max-future-skew-seconds", type=int, default=0)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    output = Path(args.output).resolve()
    if output.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={output}")

    try:
        pressure, raw = load_object(Path(args.pressure).resolve())
        result = evaluate(
            pressure,
            raw,
            args.evaluated_at,
            args.max_age_seconds,
            args.max_future_skew_seconds,
        )
    except (ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc))

    output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    output.write_bytes(encoded)
    print(json.dumps({
        "STATE": result["state"],
        "OUTPUT": str(output),
        "OUTPUT_SHA256": sha256_bytes(encoded),
        "AGE_SECONDS": result["age_seconds"],
        "ACK_CURSOR_MUTATION": 0,
        "NEXT": result["next"],
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
