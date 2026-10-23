#!/usr/bin/env python3
"""Standalone strict verifier for CoBenchmarkEvoEvent/1 JSONL. No network or key access.

A matching hash chain only shows integrity relative to the supplied independent head.
It does NOT authenticate a person, execution environment, or scientific result.
"""
import argparse
import hashlib
import json
import pathlib
import sys


def no_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('DUPLICATE_JSON_KEY')
        value[key] = item
    return value


def digest(value):
    body = json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(body).hexdigest()


def verify(path, expected_head):
    if not isinstance(expected_head, str) or len(expected_head) != 64 or any(c not in '0123456789abcdef' for c in expected_head):
        raise ValueError('INVALID_EXPECTED_HEAD')
    if path.stat().st_size > 1_000_000:
        raise ValueError('LEDGER_TOO_LARGE_FOR_DEMO')
    previous = '0' * 64
    count = 0
    for line in path.read_text('utf-8').splitlines():
        if not line.strip():
            raise ValueError('BLANK_EVENT_LINE')
        row = json.loads(line, object_pairs_hook=no_duplicate_keys,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError('NONFINITE')))
        count += 1
        if not isinstance(row, dict) or row.get('schema') != 'CoBenchmarkEvoEvent/1' or row.get('seq') != count:
            raise ValueError('SCHEMA_OR_SEQUENCE_ERROR')
        if row.get('prev_hash') != previous or row.get('event_hash') != digest({k: v for k, v in row.items() if k != 'event_hash'}):
            raise ValueError('HASH_CHAIN_MISMATCH')
        previous = row['event_hash']
    if not count or previous != expected_head:
        raise ValueError('HEAD_MISMATCH_OR_EMPTY')
    return count


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('jsonl', type=pathlib.Path)
    parser.add_argument('head', type=pathlib.Path)
    args = parser.parse_args()
    try:
        head = args.head.read_text('ascii').strip()
        events = verify(args.jsonl, head)
        print(f'PASS python hash-chain events={events} head={head}')
    except Exception as exc:
        print(f'FAIL {type(exc).__name__}: {exc}', file=sys.stderr)
        raise SystemExit(1)
