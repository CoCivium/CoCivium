#!/usr/bin/env python3
"""Verify the public CoStretch R1 synthetic ledger against a pinned expected head.

Integrity with a pinned head is NOT a signature, author authentication, or
scientific claim validation. Python standard library only; no network access.
"""
import hashlib
import json
from pathlib import Path

EXPECTED_HEAD = "58df0b6c89b5b7b7db3ab2d3c96bd9fd5fcd9bf41138fab00acec0182f2984a7"
PATH = Path(__file__).with_name("benchmark_evo.jsonl")


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def canonical_hash(row):
    encoded = json.dumps(row, ensure_ascii=True, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def main():
    prior = "0" * 64
    lines = PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 9, "UNEXPECTED_EVENT_COUNT"
    for number, line in enumerate(lines, 1):
        row = json.loads(line, object_pairs_hook=unique_keys)
        assert row.get("schema") == "CoBenchmarkEvoEvent/1", "BAD_SCHEMA"
        assert row.get("seq") == number, "BAD_SEQUENCE"
        assert row.get("prev_hash") == prior, "BROKEN_LINK"
        payload = {k: v for k, v in row.items() if k != "event_hash"}
        assert row.get("event_hash") == canonical_hash(payload), "BAD_HASH"
        prior = row["event_hash"]
    assert prior == EXPECTED_HEAD, "HEAD_MISMATCH"
    print("PASS 9 synthetic ledger events verified with pinned head:", prior)


if __name__ == "__main__":
    main()
