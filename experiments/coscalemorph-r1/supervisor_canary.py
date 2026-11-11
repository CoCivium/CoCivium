#!/usr/bin/env python3
"""Explicit one-controller kill-and-resume proof; no daemon or external I/O.

A subprocess is killed by OS termination, its durable checkpoint verified, and
another independent process resumes. The PID-based stale-lock check is local and
is NOT a durable distributed ownership scheme.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from coscalemorph import sha
from process_recovery import (
    RecoveryError, digest_prefix, reclaim_dead_lock, read_json,
    setup_workspace, validate_checkpoint,
)

ROOT = Path(__file__).resolve().parent
PUBLIC_SOURCE = ROOT / 'source/CoMapPulse_graph_R0.json'


def full_canary(*, state: Path | None = None, task_count: int = 32,
                slow_ms: int = 110, timeout_seconds: float = 12) -> dict:
    owned_tmp = tempfile.TemporaryDirectory(prefix='coscalemorph-r1-') if state is None else None
    try:
        state = Path(owned_tmp.name) / 'state' if owned_tmp else Path(state)
        source = PUBLIC_SOURCE
        m = setup_workspace(state, source.read_bytes(), task_count=task_count)
        first = subprocess.Popen([sys.executable, str(ROOT/'process_recovery.py'), 'run',
                                  '--state', str(state), '--source', str(source),
                                  '--delay-ms', str(slow_ms)],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        progressed = None
        try:
            deadline = time.monotonic() + timeout_seconds
            while time.monotonic() < deadline:
                if (state/'checkpoint.json').exists():
                    try:
                        cp = read_json(state/'checkpoint.json')
                        validate_checkpoint(cp, m)
                        if 3 <= cp['completed'] <= task_count-3 and first.poll() is None:
                            progressed = cp
                            break
                    except RecoveryError:
                        pass
                if first.poll() is not None:
                    raise RecoveryError('WORKER_EXITED_BEFORE_KILL_CANARY')
                time.sleep(.02)
            if progressed is None:
                raise RecoveryError('WORKER_DID_NOT_REACH_KILL_GATE')
            first.kill()  # genuine OS process termination, no Python cleanup
            first.wait(timeout=5)
            first.communicate(timeout=3)
        finally:
            if first.poll() is None:
                first.kill()
                first.wait(timeout=5)
                first.communicate(timeout=3)
        assert first.returncode != 0
        dead_cp = read_json(state/'checkpoint.json')
        validate_checkpoint(dead_cp, m)
        if not 3 <= dead_cp['completed'] < task_count:
            raise RecoveryError('INVALID_DEATH_PROGRESS')
        if dead_cp['last_writer_pid'] != first.pid:
            raise RecoveryError('CHECKPOINT_WRITER_NOT_KILLED_PROCESS')
        if not (state/'worker.lock').exists():
            raise RecoveryError('MISSING_CRASH_LOCK_WITNESS')
        # The same task must not start while the stale lock is unresolved.
        blocked = subprocess.run([sys.executable,str(ROOT/'process_recovery.py'), 'run',
                                  '--state',str(state),'--source',str(source)],
                                 capture_output=True,text=True,timeout=5)
        if blocked.returncode != 2 or 'LOCK_HELD' not in blocked.stderr:
            raise RecoveryError('CRASH_LOCK_DID_NOT_FAIL_CLOSED')
        reclaim_dead_lock(state, first.pid)  # explicit one-controller decision
        resumed = subprocess.run([sys.executable, str(ROOT/'process_recovery.py'),'run',
                                  '--state',str(state),'--source',str(source)],
                                 capture_output=True,text=True,timeout=10)
        if resumed.returncode:
            raise RecoveryError('RESTART_FAILED:'+resumed.stderr[:180])
        status = json.loads(resumed.stdout)
        end_cp = read_json(state/'checkpoint.json')
        validate_checkpoint(end_cp, m)
        if status['status'] != 'COMPLETE' or end_cp['completed'] != task_count:
            raise RecoveryError('DID_NOT_FINISH')
        if status['pid'] == first.pid or end_cp['restart_count'] != 1:
            raise RecoveryError('NOT_AN_INDEPENDENT_SUCCESSOR')
        if end_cp['rolling_digest'] != digest_prefix(m['source_sha256'], task_count):
            raise RecoveryError('WRONG_WORK_OUTPUT')
        if end_cp['external_effects'] != 0 or end_cp['receiver_ack'] != 'NOT_OBSERVED':
            raise RecoveryError('UNAUTHORIZED_EFFECT_CLAIM')
        return {
            'schema':'CoScaleMorph.KillRestartCanary/R1',
            'proof':'ACTUAL_PROCESS_KILL_AND_INDEPENDENT_LOCAL_SUCCESSOR',
            'source_sha256':m['source_sha256'],
            'mission_sha256':sha(json.dumps(m,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()),
            'task_count':task_count,
            'completed_at_kill':dead_cp['completed'],
            'kill_nonzero_exit':first.returncode != 0,
            'stale_lock_blocked_attempt':True,
            'explicit_lock_reclaim':True,
            'successor_different_pid':True,
            'replay_exact_digest':True,
            'result_digest_sha256':end_cp['rolling_digest'],
            'completed':end_cp['completed'],
            'restart_count':end_cp['restart_count'],
            'real_subprocesses_launched':3,
            'live_worker_width':1,
            'external_model_calls':0,
            'remote_receivers':0,
            'external_effects':0,
            'receiver_ack':'NOT_OBSERVED',
            'nonclaims':[
                'SINGLE_CONTROLLER_NE_DISTRIBUTED_LEASE',
                'PROCESS_DEATH_REPLAY_NE_MODEL_SESSION_RESTORED',
                'LOCAL_CHECKPOINT_NE_INDEPENDENT_REMOTE_CUSTODY',
                'HASH_NE_SIGNATURE_OR_REAL_WORLD_CORRECTNESS',
                'ONE_RUN_NE_SUSTAINED_RELIABILITY',
            ],
        }
    finally:
        if owned_tmp is not None:
            owned_tmp.cleanup()


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,default=ROOT/'output/kill_restart_receipt.json')
    a=p.parse_args()
    result=full_canary()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=='__main__':
    main()
