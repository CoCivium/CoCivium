#!/usr/bin/env python3
"""CoStretch R3: immutable-spec, fail-closed logical experiment checkpoints.

Python standard library. No network, inference, provider sessions, or subprocesses.
This tool only describes/advances a bounded logical index. It executes nothing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from math import prod

SPACE_SCHEMA = 'CoEvoSpace/1'
CHECKPOINT_SCHEMA = 'CoTurtleCheckpoint/3'
MAX_SPACE_BYTES = 1024 * 1024
MAX_CHECKPOINT_BYTES = 16 * 1024
MAX_PEEK = 16
POLICY = 'LOGICAL_ONLY_NO_EXTERNAL_EFFECTS'
KNOWN_EFFECTS = {'OBSERVE', 'PROPOSE', 'REVIEW_CHALLENGE', 'EXTERNAL_ACTION'}
KNOWN_AUTHORITY = {'READONLY', 'ADVISORY', 'WRITE', 'UNKNOWN'}
KNOWN_CONF = {'PUBLIC', 'PRIVATE', 'RESTRICTED'}


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(',', ':'), allow_nan=False).encode('ascii')


def no_duplicate_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('DUPLICATE_JSON_KEY')
        obj[key] = value
    return obj


def strict_json(raw: bytes):
    return json.loads(raw.decode('utf-8'), object_pairs_hook=no_duplicate_keys,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('NONFINITE')))


def read_bounded(path: Path, limit: int) -> bytes:
    if not path.is_file():
        raise ValueError('FILE_NOT_FOUND')
    if path.stat().st_size > limit:
        raise ValueError('INPUT_TOO_LARGE')
    raw = path.read_bytes()
    if len(raw) > limit:
        raise ValueError('INPUT_TOO_LARGE')
    return raw


def integer(value, label: str, minimum: int = 0, maximum: int = 10**24) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError('INVALID_' + label)
    return value


def validate_space(space):
    if not isinstance(space, dict) or set(space) != {'schema', 'description', 'dimensions'}:
        raise ValueError('INVALID_SPACE_SHAPE')
    if space.get('schema') != SPACE_SCHEMA or not isinstance(space['description'], str):
        raise ValueError('INVALID_SPACE_SCHEMA')
    dims = space['dimensions']
    if not isinstance(dims, list) or not 1 <= len(dims) <= 32:
        raise ValueError('INVALID_DIMENSIONS')
    seen = set()
    for dim in dims:
        if not isinstance(dim, dict) or set(dim) != {'name', 'options'}:
            raise ValueError('INVALID_DIMENSION')
        name, options = dim['name'], dim['options']
        if not isinstance(name, str) or not name.isascii() or not name.isidentifier() or len(name) > 48 or name in seen:
            raise ValueError('INVALID_NAME')
        seen.add(name)
        if not isinstance(options, list) or not 2 <= len(options) <= 64:
            raise ValueError('INVALID_OPTIONS')
        if any(not isinstance(opt, str) or not opt or len(opt) > 100 or '\x00' in opt for opt in options):
            raise ValueError('INVALID_OPTION_TEXT')
        if len(set(options)) != len(options):
            raise ValueError('DUPLICATE_OPTION')
    required = {'effect': KNOWN_EFFECTS, 'authority': KNOWN_AUTHORITY, 'confidentiality': KNOWN_CONF}
    by_name = {d['name']: set(d['options']) for d in dims}
    for name, accepted in required.items():
        if name not in by_name or not by_name[name].issubset(accepted):
            raise ValueError('UNKNOWN_OR_MISSING_POLICY_DIMENSION:' + name)


def load_space(path: Path):
    raw = read_bounded(path, MAX_SPACE_BYTES)
    space = strict_json(raw)
    validate_space(space)
    return space, digest(raw)


def capacity(space) -> int:
    return prod(len(d['options']) for d in space['dimensions'])


def unrank(space, index: int) -> dict:
    cap = capacity(space)
    integer(index, 'INDEX', 0, cap - 1)
    values = {}
    for d in reversed(space['dimensions']):
        index, digit = divmod(index, len(d['options']))
        values[d['name']] = d['options'][digit]
    return {d['name']: values[d['name']] for d in space['dimensions']}


def rank(space, point: dict) -> int:
    if not isinstance(point, dict) or set(point) != {d['name'] for d in space['dimensions']}:
        raise ValueError('DIMENSIONS_MISMATCH')
    index = 0
    for d in space['dimensions']:
        v = point[d['name']]
        try:
            digit = d['options'].index(v)
        except ValueError as exc:
            raise ValueError('BAD_OPTION') from exc
        index = index * len(d['options']) + digit
    return index


def disclosure(point) -> list[str]:
    """Warnings, not execution permissions or sufficient authorization."""
    holds = []
    if point.get('effect') not in {'OBSERVE', 'PROPOSE', 'REVIEW_CHALLENGE'}:
        holds.append('EXTERNAL_EFFECT_NOT_ALLOWED')
    if point.get('authority') not in {'READONLY', 'ADVISORY'}:
        holds.append('MISSING_AUTHORITY')
    if point.get('confidentiality') != 'PUBLIC':
        holds.append('NONPUBLIC_UNVERIFIED')
    if point.get('substrate') not in {'python', 'node'}:
        holds.append('NONDETERMINISTIC_OR_PROVIDER_SUBSTRATE_UNVERIFIED')
    return holds


def make_checkpoint(space, spec_hash, next_index=0, revision=0, parent_digest=None):
    cap = capacity(space)
    integer(next_index, 'NEXT_INDEX', 0, cap)
    integer(revision, 'REVISION', 0, 10**9)
    if parent_digest is not None and (not isinstance(parent_digest, str) or len(parent_digest) != 64 or any(c not in '0123456789abcdef' for c in parent_digest)):
        raise ValueError('INVALID_PARENT_DIGEST')
    payload = {
        'schema': CHECKPOINT_SCHEMA, 'spec_sha256': spec_hash,
        'capacity': cap, 'next_index': next_index, 'revision': revision,
        'parent_checkpoint_sha256': parent_digest,
        'effect_ceiling': POLICY, 'actual_executed_experiments': 0,
        'actual_live_sessions': 0,
    }
    return {**payload, 'checkpoint_sha256': digest(canonical(payload))}


def validate_checkpoint(space, spec_hash: str, checkpoint: dict):
    if not isinstance(checkpoint, dict):
        raise ValueError('INVALID_CHECKPOINT')
    if set(checkpoint) != {
        'schema', 'spec_sha256', 'capacity', 'next_index', 'revision',
        'parent_checkpoint_sha256', 'effect_ceiling', 'actual_executed_experiments',
        'actual_live_sessions', 'checkpoint_sha256'
    }:
        raise ValueError('CHECKPOINT_SCHEMA_MISMATCH')
    if checkpoint.get('schema') != CHECKPOINT_SCHEMA:
        raise ValueError('CHECKPOINT_SCHEMA_MISMATCH')
    recorded_hash = checkpoint['checkpoint_sha256']
    payload = {k: v for k, v in checkpoint.items() if k != 'checkpoint_sha256'}
    if not isinstance(recorded_hash, str) or recorded_hash != digest(canonical(payload)):
        raise ValueError('CHECKPOINT_TAMPERED')
    if checkpoint['spec_sha256'] != spec_hash:
        raise ValueError('SPEC_NAMESPACE_CHANGED')
    if checkpoint['capacity'] != capacity(space):
        raise ValueError('CAPACITY_CHANGED')
    if checkpoint['effect_ceiling'] != POLICY:
        raise ValueError('EFFECT_POLICY_CHANGED')
    if type(checkpoint['actual_executed_experiments']) is not int or type(checkpoint['actual_live_sessions']) is not int or checkpoint['actual_executed_experiments'] != 0 or checkpoint['actual_live_sessions'] != 0:
        raise ValueError('FALSE_EXECUTION_STATUS')
    integer(checkpoint['next_index'], 'NEXT_INDEX', 0, capacity(space))
    integer(checkpoint['revision'], 'REVISION', 0, 10**9)
    parent = checkpoint['parent_checkpoint_sha256']
    if parent is not None and (not isinstance(parent, str) or len(parent) != 64 or any(c not in '0123456789abcdef' for c in parent)):
        raise ValueError('INVALID_PARENT_DIGEST')
    return checkpoint


def load_checkpoint(path: Path):
    return strict_json(read_bounded(path, MAX_CHECKPOINT_BYTES))


def peek(space, checkpoint, count=3):
    count = integer(count, 'PEEK_COUNT', 1, MAX_PEEK)
    start = checkpoint['next_index']
    stop = min(start + count, capacity(space))
    records = []
    for idx in range(start, stop):
        point = unrank(space, idx)
        records.append({'index': idx, 'point': point, 'holds': disclosure(point),
                        'status': 'DESCRIBED_NOT_EXECUTED'})
    return records


def advance(space, spec_hash, cp, count):
    validate_checkpoint(space, spec_hash, cp)
    records = peek(space, cp, count)
    if not records:
        raise ValueError('SPACE_EXHAUSTED_NO_ADVANCE')
    successor = make_checkpoint(space, spec_hash,
                                next_index=cp['next_index'] + len(records),
                                revision=cp['revision'] + 1,
                                parent_digest=cp['checkpoint_sha256'])
    return successor, records


def exclusive_json(path, data):
    # No-clobber is best-effort for a single file; not an atomic distributed lease.
    with path.open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    for action in ('init', 'verify', 'peek', 'advance'):
        sp = sub.add_parser(action)
        sp.add_argument('--space', type=Path, required=True)
        if action != 'init':
            sp.add_argument('--checkpoint', type=Path, required=True)
        if action in ('init', 'advance'):
            sp.add_argument('--out', type=Path, required=True)
        if action in ('peek', 'advance'):
            sp.add_argument('--count', type=int, default=3)
    args = parser.parse_args()
    try:
        space, spec_hash = load_space(args.space)
        if args.action == 'init':
            cp = make_checkpoint(space, spec_hash)
            exclusive_json(args.out, cp)
            print(json.dumps({'result':'PASS_INITIALIZED', 'file':str(args.out),
                              'spec_sha256':spec_hash, 'capacity':cp['capacity']}))
        else:
            cp = validate_checkpoint(space, spec_hash, load_checkpoint(args.checkpoint))
            if args.action == 'verify':
                print(json.dumps({'result':'PASS_NAMESPACE_AND_CHECKPOINT',
                                  'spec_sha256':spec_hash, 'next_index':cp['next_index'],
                                  'remaining':cp['capacity']-cp['next_index']}))
            elif args.action == 'peek':
                print(json.dumps({'result':'PASS_DESCRIPTIONS_ONLY', 'descriptions':peek(space, cp, args.count),
                                  'provider_requests':0, 'actual_experiments':0},indent=2))
            else:
                successor, records = advance(space, spec_hash, cp, args.count)
                exclusive_json(args.out, successor)
                print(json.dumps({'result':'PASS_LOGICAL_ADVANCE_ONLY', 'file':str(args.out),
                                  'descriptions_examined':len(records),
                                  'next_index':successor['next_index'],
                                  'checkpoint_sha256':successor['checkpoint_sha256'],
                                  'provider_requests':0, 'actual_experiments':0}))
    except (ValueError, OSError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
        parser.exit(2, 'FAIL ' + str(exc) + '\n')


if __name__ == '__main__':
    main()