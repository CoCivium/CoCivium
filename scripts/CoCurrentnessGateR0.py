#!/usr/bin/env python3
"""Fail-closed CoLocal/CoSpeedo currentness evidence gate. Python stdlib only.

Pure evaluation of supplied observations. It does not inspect a machine, run a
receiver, authorize recovery, or independently attest the supplying observer.
"""
import argparse
import json
import ntpath
import re
from datetime import datetime, timezone
from pathlib import Path

COMPONENT = 'CoBarCurrentReceiver_v0_5'
SHA256 = re.compile(r'^[0-9a-fA-F]{64}$')
NONCLAIMS = [
    'HEARTBEAT_NE_WORK_OUTCOME',
    'GATE_RESULT_NE_RECEIVER_ACK',
    'FIXTURE_NE_X2_RUNTIME',
    'PUBLIC_SOURCE_NE_COALL_INTEGRATION',
]


def when(value):
    if not isinstance(value, str):
        raise ValueError('timestamp must be a string')
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('timestamp needs a timezone')
    return dt.astimezone(timezone.utc)


def normalized_windows_path(value):
    if not isinstance(value, str) or not value.strip():
        return None
    return ntpath.normcase(ntpath.normpath(value))


def sample_faults(sample):
    """Check a single supplied status + independent process-probe observation."""
    faults = []
    try:
        captured = when(sample['evaluated_at_utc'])
        status = sample['status']
        probe = sample['probe']
        source_time = when(status['utc'])
        probe_time = when(probe['captured_at_utc'])
        period = float(status['heartbeat_period_seconds'])
        if not 0 < period <= 3600:
            raise ValueError('bad period')
        max_age = max(60.0, period * 3)
        if (captured - source_time).total_seconds() < -5:
            faults.append('STATUS_FROM_FUTURE')
        if (captured - source_time).total_seconds() > max_age:
            faults.append('STATUS_EXPIRED')
        if abs((captured - probe_time).total_seconds()) > 20:
            faults.append('PROCESS_PROBE_NOT_CURRENT')
        if status.get('state') != 'ALIVE_LOCAL':
            faults.append('STATUS_NOT_ALIVE_LOCAL')
        receiver = status['components'][COMPONENT]
        pid = receiver['pid']
        if type(pid) is not int or pid < 1:
            faults.append('INVALID_RECEIVER_PID')
        if probe.get('process_exists') is not True:
            faults.append('RECEIVER_PROCESS_NOT_OBSERVED')
        if probe.get('pid') != pid or type(probe.get('pid')) is not int:
            faults.append('RECEIVER_PID_NOT_BOUND')
        expected_path = normalized_windows_path(receiver.get('path'))
        observed_path = normalized_windows_path(probe.get('executable_path'))
        if not expected_path or observed_path != expected_path:
            faults.append('RECEIVER_EXECUTABLE_PATH_MISMATCH')
        expected_hash = receiver.get('expected_sha256')
        observed_hash = probe.get('executable_sha256')
        if not isinstance(expected_hash, str) or not SHA256.fullmatch(expected_hash) or not isinstance(observed_hash, str) or observed_hash.lower() != expected_hash.lower():
            faults.append('RECEIVER_EXECUTABLE_HASH_MISMATCH')
        start_time = when(probe['process_start_utc'])
        if start_time > source_time:
            faults.append('PROCESS_BEGAN_AFTER_REPORTED_HEARTBEAT')
        seq = status.get('heartbeat_seq')
        if type(seq) is not int or seq < 0:
            faults.append('INVALID_HEARTBEAT_SEQUENCE')
    except (KeyError, ValueError, TypeError, OverflowError, AttributeError):
        faults.append('MALFORMED_OR_MISSING_EVIDENCE')
    return sorted(set(faults))


def assess(current, previous=None):
    faults = sample_faults(current)
    if faults:
        state = 'FAIL_CLOSED_RECEIVER_CURRENTNESS'
    elif previous is None:
        state = 'HELD_SINGLE_SAMPLE_PROGRESS_UNPROVEN'
    else:
        prior_faults = sample_faults(previous)
        if prior_faults:
            faults.append('PREVIOUS_SAMPLE_UNQUALIFIED')
            state = 'FAIL_CLOSED_RECEIVER_CURRENTNESS'
        else:
            elapsed = (when(current['evaluated_at_utc']) - when(previous['evaluated_at_utc'])).total_seconds()
            period = float(current['status']['heartbeat_period_seconds'])
            prior_pid = previous['probe']['pid']
            current_pid = current['probe']['pid']
            prior_start = when(previous['probe']['process_start_utc'])
            current_start = when(current['probe']['process_start_utc'])
            if elapsed <= 0:
                faults.append('NON_MONOTONIC_OBSERVATION_TIME')
                state = 'FAIL_CLOSED_RECEIVER_CURRENTNESS'
            elif prior_pid != current_pid or prior_start != current_start:
                state = 'HELD_PROCESS_EPOCH_CHANGED'
            elif when(current['status']['utc']) <= when(previous['status']['utc']):
                # Counter increments alone cannot establish a new heartbeat
                # event if the reported event timestamp is frozen or reversed.
                faults.append('STATUS_TIMESTAMP_NOT_ADVANCING')
                state = 'FAIL_CLOSED_RECEIVER_CURRENTNESS'
            elif elapsed < max(60.0, 3 * period):
                state = 'HELD_WINDOW_TOO_SHORT'
            elif current['status']['heartbeat_seq'] <= previous['status']['heartbeat_seq']:
                faults.append('HEARTBEAT_NOT_ADVANCING')
                state = 'FAIL_CLOSED_RECEIVER_CURRENTNESS'
            else:
                state = 'PASS_BOUNDED_HEARTBEAT_PROGRESS'
    return {
        'schema': 'CoLocal.CoCurrentnessGate.R0',
        'state': state,
        'reasons': sorted(set(faults)),
        'scope': 'SUPPLIED_EVIDENCE_CONTRACT_ONLY',
        'physical_receiver_inspection_performed': False,
        'receiver_pickup_ack': False,
        'nonclaims': NONCLAIMS,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--current', type=Path, required=True, help='Current status+probe JSON')
    parser.add_argument('--previous', type=Path, help='Earlier status+probe JSON')
    args = parser.parse_args()
    try:
        current = json.loads(args.current.read_text(encoding='utf-8'))
        previous = json.loads(args.previous.read_text(encoding='utf-8')) if args.previous else None
        result = assess(current, previous)
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        result = {'schema': 'CoLocal.CoCurrentnessGate.R0', 'state': 'FAIL_CLOSED_MALFORMED_INPUT', 'reasons': [type(exc).__name__], 'scope': 'SUPPLIED_EVIDENCE_CONTRACT_ONLY', 'receiver_pickup_ack': False, 'nonclaims': NONCLAIMS}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['state'] == 'PASS_BOUNDED_HEARTBEAT_PROGRESS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
