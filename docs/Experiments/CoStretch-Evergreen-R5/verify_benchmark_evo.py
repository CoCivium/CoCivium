#!/usr/bin/env python3
"""Validate public-safe CoStretch experiment records; no network or effects."""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

SCHEMA = "CoStretch.BenchmarkEvo.Record.v1"
STATES = {"PASS", "FAIL", "HOLD", "NOT_RUN"}
KINDS = {"LOCAL_RETEST", "SYNTHETIC", "X2_SINGLE_HOST_TIMING", "X2_HASH_READBACK", "VIRTUAL_MAPPING", "LOCAL_MODEL_CATALOG", "PENDING_REAL_TEST"}
NEEDED = {"schema", "event_id", "status", "evidence_class", "claim", "source", "scope", "metrics", "limitations", "promotion_eligible", "external_effects", "privacy"}
HEX64 = re.compile(r"^[a-f0-9]{64}$")
IDENT = re.compile(r"^[A-Z0-9_]{3,96}$")
MAX_BYTES = 500_000
MAX_ROWS = 10_000


def unique_pairs(pairs):
    out = {}
    for key, val in pairs:
        if key in out:
            raise ValueError("duplicate JSON key: " + key)
        out[key] = val
    return out


def validate_record(rec):
    if not isinstance(rec, dict) or set(rec) != NEEDED:
        raise ValueError("record fields differ from contract")
    if rec["schema"] != SCHEMA or rec["status"] not in STATES or rec["evidence_class"] not in KINDS:
        raise ValueError("schema, state or evidence class invalid")
    if not isinstance(rec["event_id"], str) or not IDENT.fullmatch(rec["event_id"]):
        raise ValueError("invalid event identity")
    for key in ("claim", "scope", "privacy"):
        if not isinstance(rec[key], str) or not rec[key]:
            raise ValueError("missing text: " + key)
    if rec["privacy"] != "PUBLIC_SAFE":
        raise ValueError("public ledger cannot hold private records")
    source = rec["source"]
    if not isinstance(source, dict) or set(source) != {"id", "sha256"}:
        raise ValueError("source identity/hash required")
    if not isinstance(source["id"], str) or not source["id"] or not isinstance(source["sha256"], str) or not HEX64.fullmatch(source["sha256"]):
        raise ValueError("source hash malformed")
    if not isinstance(rec["metrics"], dict):
        raise ValueError("metrics must be a dictionary")
    if not isinstance(rec["limitations"], list) or not rec["limitations"] or not all(isinstance(x, str) and x for x in rec["limitations"]):
        raise ValueError("limitations must be explicit")
    if type(rec["promotion_eligible"]) is not bool or rec["promotion_eligible"]:
        raise ValueError("no real policy promotion authorized by this wave")
    if type(rec["external_effects"]) is not int or rec["external_effects"] != 0:
        raise ValueError("this benchmark cannot assert external actions")
    if rec["status"] == "NOT_RUN" and rec["metrics"]:
        raise ValueError("not-run work cannot have performance metrics")
    if rec["evidence_class"] in ("SYNTHETIC", "VIRTUAL_MAPPING"):
        if any(k in rec["metrics"] for k in ("measured_joules", "actual_model_calls", "independently_validated")):
            raise ValueError("virtual/synthetic measurements overclaimed")
    if rec["evidence_class"] == "X2_SINGLE_HOST_TIMING":
        keys = {"duplicate_percent", "uncached_median_ms", "memoized_median_ms", "same_host_ratio", "repetitions_each", "exact_outputs_equal"}
        if set(rec["metrics"]) != keys or type(rec["metrics"]["exact_outputs_equal"]) is not bool:
            raise ValueError("X2 controls metrics incomplete")
        for k in keys - {"exact_outputs_equal"}:
            v = rec["metrics"][k]
            if type(v) not in (int, float) or v < 0:
                raise ValueError("invalid measurement")
        if rec["metrics"]["repetitions_each"] != 3 or not rec["metrics"]["exact_outputs_equal"]:
            raise ValueError("X2 exactness or sample count contradiction")
    if rec["evidence_class"] == "VIRTUAL_MAPPING":
        metrics = rec["metrics"]
        if metrics.get("executed_physical_jobs", -1) != 0 or metrics.get("sampled_rank_roundtrips", 0) > 1024 or str(metrics.get("logical_options")) != str(16 ** 10):
            raise ValueError("virtual spaces cannot be confused with physical experiments")
    return True


def load_ledger(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("ledger missing or oversized")
    rows = []
    seen = set()
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise ValueError("blank line " + str(index))
        if index > MAX_ROWS:
            raise ValueError("too many rows")
        record = json.loads(line, object_pairs_hook=unique_pairs, parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
        validate_record(record)
        if record["event_id"] in seen:
            raise ValueError("duplicate event id")
        seen.add(record["event_id"])
        rows.append(record)
    if not rows:
        raise ValueError("empty ledger")
    return rows


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).with_name("benchmark_evo.jsonl"))
    records = load_ledger(path)
    print(json.dumps({"schema": SCHEMA, "validated_rows": len(records), "states": dict(Counter(x["status"] for x in records)), "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(), "promotion_eligible": False}, sort_keys=True))


if __name__ == "__main__":
    main()