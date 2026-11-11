#!/usr/bin/env python3
"""Offline, bounded, single-controller CoScaleMorph R1 death-and-restart canary.

This is not a distributed task lease, an OS daemon, an auth system, or a model
provider. A crash leaves a lock, requiring an explicit live-PID check before
recovery. One independently started successor rechecks source, mission, grant,
checkpoint and task prefix before advancing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import sys
import time
from datetime import datetime, timezone
from typing import Any

from coscalemorph import canonical, sha, validate_source

SCHEMA_MISSION = 'CoScaleMorph.Mission/R1'
SCHEMA_GRANT = 'CoScaleMorph.LocalGrant/R1'
SCHEMA_CP = 'CoScaleMorph.Checkpoint/R1'
SCHEMA_LOCK = 'CoScaleMorph.LocalLock/R1'
ZERO = '0' * 64


class RecoveryError(ValueError):
    pass


def unique_pairs(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise RecoveryError('DUPLICATE_JSON_KEY')
        out[k] = v
    return out


def read_json(path: Path) -> dict:
    try:
        data = path.read_bytes()
        if len(data) > 1_000_000:
            raise RecoveryError('OVERSIZE_CONTROL')
        out = json.loads(data, object_pairs_hook=unique_pairs)
        if type(out) is not dict:
            raise RecoveryError('CONTROL_NOT_OBJECT')
        return out
    except FileNotFoundError as e:
        raise RecoveryError('MISSING_CONTROL:' + path.name) from e
    except (ValueError, UnicodeDecodeError) as e:
        if isinstance(e, RecoveryError):
            raise
        raise RecoveryError('INVALID_CONTROL:' + path.name) from e


def write_once(path: Path, obj: dict) -> None:
    # Only a fresh, empty test workspace may be initialized.
    with path.open('xb') as f:
        f.write(canonical(obj) + b'\n')
        f.flush()
        os.fsync(f.fileno())


def atomic_write(path: Path, obj: dict) -> None:
    tmp = path.with_name('.' + path.name + '.' + str(os.getpid()) + '.' + secrets.token_hex(4) + '.tmp')
    try:
        with tmp.open('xb') as f:
            f.write(canonical(obj) + b'\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def setup_workspace(state: Path, source: bytes, task_count: int = 32,
                    work_id: str = 'coscalemorph_r1_public_recovery') -> dict:
    validate_source(source)
    if type(task_count) is not int or not 8 <= task_count <= 64:
        raise RecoveryError('UNSUPPORTED_TASK_BUDGET')
    if not isinstance(work_id, str) or not work_id or len(work_id) > 100:
        raise RecoveryError('INVALID_WORK_ID')
    state.mkdir(parents=True, exist_ok=True)
    if any(state.iterdir()):
        raise RecoveryError('WORKSPACE_NOT_EMPTY')
    mission = {
        'schema': SCHEMA_MISSION, 'work_id': work_id,
        'source_sha256': sha(source), 'source_bytes': len(source),
        'task_count': task_count, 'task_algorithm': 'SHA256_INDEX_CHAIN_R1',
        'maximum_active_workers': 1,
        'authority_ceiling': 'LOCAL_DETERMINISTIC_ONLY',
        'external_effects_allowed': False,
    }
    grant = {
        'schema': SCHEMA_GRANT, 'work_id': work_id,
        'state': 'AUTHORIZED', 'scope': 'LOCAL_DETERMINISTIC_ONLY',
        'valid_until_utc': '2099-01-01T00:00:00Z',
        'external_effects_allowed': False,
    }
    write_once(state / 'mission.json', mission)
    write_once(state / 'grant.json', grant)
    return mission


def validate_mission(m: dict) -> None:
    if m.get('schema') != SCHEMA_MISSION or m.get('task_algorithm') != 'SHA256_INDEX_CHAIN_R1':
        raise RecoveryError('MISSION_SCHEMA_DRIFT')
    if m.get('maximum_active_workers') != 1 or m.get('authority_ceiling') != 'LOCAL_DETERMINISTIC_ONLY' or m.get('external_effects_allowed') is not False:
        raise RecoveryError('MISSION_AUTHORITY_LIMIT')
    if type(m.get('task_count')) is not int or not 8 <= m['task_count'] <= 64:
        raise RecoveryError('MISSION_TASK_LIMIT')
    if type(m.get('source_bytes')) is not int or not 0 < m['source_bytes'] <= 1_000_000:
        raise RecoveryError('MISSION_SOURCE_LIMIT')
    if not isinstance(m.get('work_id'), str) or not m['work_id'] or len(m['work_id']) > 100:
        raise RecoveryError('MISSION_WORK_ID')
    if not isinstance(m.get('source_sha256'), str) or len(m['source_sha256']) != 64:
        raise RecoveryError('MISSION_SOURCE_HASH')


def validate_grant(g: dict, m: dict, asof: datetime | None = None) -> None:
    if g.get('schema') != SCHEMA_GRANT or g.get('work_id') != m['work_id']:
        raise RecoveryError('AUTHORIZATION_WRONG_IDENTITY')
    if g.get('state') != 'AUTHORIZED' or g.get('scope') != 'LOCAL_DETERMINISTIC_ONLY' or g.get('external_effects_allowed') is not False:
        raise RecoveryError('AUTHORIZATION_REVOKED_OR_OUT_OF_SCOPE')
    try:
        expiry = datetime.strptime(g['valid_until_utc'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except (KeyError, TypeError, ValueError) as e:
        raise RecoveryError('INVALID_GRANT_EXPIRY') from e
    if expiry <= (asof or datetime.now(timezone.utc)):
        raise RecoveryError('AUTHORIZATION_EXPIRED')


def load_source(source_path: Path, m: dict) -> bytes:
    try:
        source = source_path.read_bytes()
    except OSError as e:
        raise RecoveryError('SOURCE_UNAVAILABLE') from e
    if len(source) != m['source_bytes'] or sha(source) != m['source_sha256']:
        raise RecoveryError('SOURCE_IDENTITY_MISMATCH')
    validate_source(source)
    return source


def task_digest(source_hash: str, index: int) -> str:
    return hashlib.sha256(('CoScaleMorph:R1:' + source_hash + ':' + str(index)).encode('ascii')).hexdigest()


def digest_prefix(source_hash: str, count: int) -> str:
    acc = ZERO
    for i in range(count):
        acc = sha((acc + ':' + str(i) + ':' + task_digest(source_hash, i)).encode('ascii'))
    return acc


def cp_body(m: dict, completed: int, *, pid: int, restart_count: int) -> dict:
    return {
        'schema': SCHEMA_CP, 'work_id': m['work_id'],
        'mission_sha256': sha(canonical(m)),
        'source_sha256': m['source_sha256'],
        'completed': completed,
        'rolling_digest': digest_prefix(m['source_sha256'], completed),
        'last_writer_pid': pid,
        'restart_count': restart_count,
        'external_effects': 0,
        'receiver_ack': 'NOT_OBSERVED',
    }


def sealed_body(body: dict) -> dict:
    return {**body, 'checkpoint_sha256': sha(canonical(body))}


def validate_checkpoint(cp: dict, m: dict) -> None:
    if cp.get('schema') != SCHEMA_CP or cp.get('work_id') != m['work_id']:
        raise RecoveryError('CHECKPOINT_SCHEMA_OR_IDENTITY')
    if cp.get('mission_sha256') != sha(canonical(m)) or cp.get('source_sha256') != m['source_sha256']:
        raise RecoveryError('CHECKPOINT_NAMESPACE_CHANGED')
    n = cp.get('completed')
    if type(n) is not int or not 0 <= n <= m['task_count']:
        raise RecoveryError('BAD_CHECKPOINT_PROGRESS')
    if type(cp.get('restart_count')) is not int or not 0 <= cp['restart_count'] <= 16:
        raise RecoveryError('BAD_RESTART_COUNT')
    if type(cp.get('last_writer_pid')) is not int or cp['last_writer_pid'] <= 0:
        raise RecoveryError('BAD_CHECKPOINT_WRITER')
    if cp.get('receiver_ack') != 'NOT_OBSERVED' or cp.get('external_effects') != 0:
        raise RecoveryError('FORGED_EXTERNAL_EFFECT')
    body = {k: v for k, v in cp.items() if k != 'checkpoint_sha256'}
    if cp.get('checkpoint_sha256') != sha(canonical(body)):
        raise RecoveryError('CHECKPOINT_HASH_MISMATCH')
    if cp.get('rolling_digest') != digest_prefix(m['source_sha256'], n):
        raise RecoveryError('CHECKPOINT_TASK_PREFIX_MISMATCH')


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def acquire_lock(state: Path, m: dict) -> dict:
    lock = {
        'schema': SCHEMA_LOCK, 'work_id': m['work_id'],
        'pid': os.getpid(), 'nonce': secrets.token_hex(16),
    }
    try:
        write_once(state / 'worker.lock', lock)
    except FileExistsError as e:
        raise RecoveryError('LOCK_HELD_OR_STALE_REQUIRES_EXPLICIT_RECLAIM') from e
    return lock


def release_lock(state: Path, lock: dict) -> None:
    path = state / 'worker.lock'
    try:
        if read_json(path) == lock:
            path.unlink()
    except RecoveryError:
        pass


def reclaim_dead_lock(state: Path, expected_pid: int) -> None:
    """Single-controller recovery after confirmed process exit, not a distributed lease."""
    l = read_json(state / 'worker.lock')
    m = read_json(state / 'mission.json')
    validate_mission(m)
    if l.get('schema') != SCHEMA_LOCK or l.get('work_id') != m['work_id']:
        raise RecoveryError('UNTRUSTED_STALE_LOCK')
    if type(l.get('pid')) is not int or l['pid'] != expected_pid:
        raise RecoveryError('WRONG_LOCK_OWNER')
    if not isinstance(l.get('nonce'), str) or len(l['nonce']) != 32:
        raise RecoveryError('MALFORMED_LOCK_NONCE')
    if pid_alive(expected_pid):
        raise RecoveryError('OWNER_STILL_LIVE')
    l2 = read_json(state / 'worker.lock')
    if l2 != l:
        raise RecoveryError('LOCK_CHANGED_DURING_RECLAIM')
    (state / 'worker.lock').unlink()


def run_worker(state: Path, source_path: Path, *, delay_ms: int = 0, max_steps: int = 64) -> dict:
    if type(delay_ms) is not int or not 0 <= delay_ms <= 1000 or type(max_steps) is not int or not 1 <= max_steps <= 64:
        raise RecoveryError('INVALID_WORK_BOUNDS')
    m = read_json(state / 'mission.json')
    validate_mission(m)
    validate_grant(read_json(state / 'grant.json'), m)
    load_source(source_path, m)
    lock = acquire_lock(state, m)
    try:
        cp_path = state / 'checkpoint.json'
        if cp_path.exists():
            cp = read_json(cp_path)
            validate_checkpoint(cp, m)
            restart = cp['restart_count'] + (cp['last_writer_pid'] != os.getpid())
        else:
            cp = sealed_body(cp_body(m, 0, pid=os.getpid(), restart_count=0))
            restart = 0
            atomic_write(cp_path, cp)
        n = cp['completed']
        for _ in range(min(max_steps, m['task_count'] - n)):
            validate_grant(read_json(state / 'grant.json'), m)
            load_source(source_path, m)
            n += 1
            cp = sealed_body(cp_body(m, n, pid=os.getpid(), restart_count=restart))
            atomic_write(cp_path, cp)
            if delay_ms:
                time.sleep(delay_ms / 1000)
        return {'status':'COMPLETE' if n == m['task_count'] else 'PAUSED',
                'completed':n, 'task_count':m['task_count'], 'pid':os.getpid(),
                'restart_count':restart, 'digest':cp['rolling_digest'],
                'external_effects':0, 'receiver_ack':'NOT_OBSERVED'}
    finally:
        release_lock(state, lock)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=['run'])
    p.add_argument('--state', required=True, type=Path)
    p.add_argument('--source', required=True, type=Path)
    p.add_argument('--delay-ms', type=int, default=0)
    p.add_argument('--max-steps', type=int, default=64)
    args = p.parse_args()
    try:
        print(json.dumps(run_worker(args.state,args.source,delay_ms=args.delay_ms,max_steps=args.max_steps),sort_keys=True),flush=True)
    except (RecoveryError, OSError) as e:
        print('HOLD: '+str(e), file=sys.stderr, flush=True)
        raise SystemExit(2)


if __name__ == '__main__':
    main()
