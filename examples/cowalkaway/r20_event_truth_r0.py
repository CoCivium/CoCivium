#!/usr/bin/env python3
"""CoWalkAway R20 read-only event truth classifier.

Consumes a supplied receipt dict; never invokes a task, writes a file, or trusts
self-reported runtime health or receiver ACK. All outcomes are candidate evidence.
"""
from __future__ import annotations
import json
import re
from datetime import datetime

SHA256 = re.compile(r'[0-9a-f]{64}\Z')
EVENT_ID = re.compile(r'[0-9a-f]{32}\Z')


def _utc(s):
    if not isinstance(s, str):
        return None
    try:
        d = datetime.fromisoformat(s.replace('Z', '+00:00'))
        return d if d.tzinfo and d.utcoffset().total_seconds() == 0 else None
    except (ValueError, TypeError, OverflowError):
        return None


def classify(event):
    base = {
        'schema': 'CoWalkAway.R20.EventTruthProjection.R0',
        'state': 'HOLD_INVALID_OR_INCOMPLETE_EVENT',
        'effect_authority': 'NONE',
        'new_jobs_proven': False,
        'receiver_ack': False,
        'reboot_recovery_proven': False,
        'os_task_restart_proven': False,
        'source_identity_authentication': 'NOT_PERFORMED',
        'nonclaims': ['EVENT_RECEIPT_NE_INDEPENDENT_ACK', 'NORMAL_COMPLETION_NE_CRASH_RECOVERY',
                      'EVENT_TIMESTAMP_NE_BOOT_PROOF', 'READ_ONLY_CLASSIFICATION_NE_RUNTIME_ADOPTION']
    }
    if not isinstance(event, dict):
        return base
    if event.get('schema') != 'CoWalkAway.R20.NativeSupervisorEvent' or \
       event.get('native_task') != 'CoWalkAwayR2_LocalEvent' or \
       event.get('result') != 'BOUNDED_PARENT_AUTORECOVERY_PASS':
        return base
    if not isinstance(event.get('event_id'), str) or not EVENT_ID.fullmatch(event['event_id']):
        return base
    if not isinstance(event.get('child_script_sha256'), str) or not SHA256.fullmatch(event['child_script_sha256']):
        return base
    if event.get('effects') != 'LOCAL_SQLITE_AND_RECEIPTS_ONLY':
        return base
    started, finished = _utc(event.get('started_utc')), _utc(event.get('finished_utc'))
    if started is None or finished is None or finished < started:
        return base
    attempts = event.get('attempts')
    if not isinstance(attempts, list) or not 1 <= len(attempts) <= 2:
        return base
    for a in attempts:
        if not isinstance(a, dict) or type(a.get('exit')) is not int or type(a.get('fault_injected')) is not bool:
            return base
        t0, t1 = _utc(a.get('start_utc')), _utc(a.get('end_utc'))
        if t0 is None or t1 is None or not (started <= t0 <= t1 <= finished):
            return base
    fault = event.get('child_fault_canary_consumed')
    if type(fault) is not bool:
        return base
    out = dict(base)
    out['event_id'] = event['event_id']
    out['reported_started_utc'] = event['started_utc']
    out['reported_finished_utc'] = event['finished_utc']
    out['source_bound_scope'] = 'SUPPLIED_EVENT_CONTENT_ONLY'
    if not fault and len(attempts) == 1 and attempts[0]['exit'] == 0 and \
       not attempts[0]['fault_injected'] and event.get('lease_recovery') is None:
        out['state'] = 'NORMAL_LOCAL_TASK_COMPLETION_ONLY'
        return out
    lease = event.get('lease_recovery')
    if fault and len(attempts) == 2 and attempts[0]['exit'] == 77 and attempts[1]['exit'] == 0 and \
       attempts[0]['fault_injected'] and not attempts[1]['fault_injected'] and \
       isinstance(lease, dict) and type(lease.get('seconds_waited')) is int and \
       0 <= lease['seconds_waited'] <= 36 and lease.get('lease_owner_observed') is True:
        out['state'] = 'BOUNDED_CHILD_RECOVERY_WITHIN_SURVIVING_PARENT'
        return out
    return base


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        raise SystemExit('usage: r20_event_truth_r0.py <existing-event-receipt.json> (read only)')
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        obj = json.load(f)
    print(json.dumps(classify(obj), sort_keys=True))
