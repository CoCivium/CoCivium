#!/usr/bin/env python3
"""Issue #317: synthetic, two-destination, local-only receipt/recovery canary.

One semantic input, two fixed test sinks.  'Receive' must run as a separate
invocation and only makes a local-process ACK, never a real remote receiver ACK.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

SCHEMA = 'CoAll.GoldenBraidLocalFanout.R0'
DESTS = ('test-alpha', 'test-beta')


def canon(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n').encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest().upper()


def load_packet(path):
    raw = Path(path).read_bytes()
    packet = json.loads(raw)
    required = ('schema', 'task_id', 'source', 'intent', 'scope', 'owner',
                'next_action', 'acceptance', 'timestamp', 'status', 'destinations')
    if not isinstance(packet, dict) or any(k not in packet for k in required):
        raise ValueError('incomplete canonical packet')
    if packet['schema'] != SCHEMA or packet['scope'] != 'SYNTHETIC_LOCAL_TEST_ONLY':
        raise ValueError('wrong schema or authority scope')
    if packet['destinations'] != list(DESTS) or not packet['task_id']:
        raise ValueError('unexpected destination or identity')
    if packet['status'] != 'TEST_PENDING' or packet['owner'] != 'UNASSIGNED_TEST_FIXTURE':
        raise ValueError('unexpected initial state or identity')
    return packet, raw


def base(root, destination):
    if destination not in DESTS:
        raise ValueError('destination not authorized for test')
    root = Path(root)
    if root.is_symlink() or (root / destination).is_symlink():
        raise ValueError('no symlink destinations')
    return root / destination


def write_once(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as fh:
        fh.write(canon(value))
        fh.flush()
        os.fsync(fh.fileno())
    return sha(path.read_bytes())


def status(packet_file, root):
    packet, raw = load_packet(packet_file)
    if (Path(root) / 'STOP').exists():
        stop = True
    else:
        stop = False
    expected = canon(packet)
    expected_sha = sha(expected)
    out = {}
    for dest in DESTS:
        folder = base(root, dest)
        payload_file = folder / 'payload.json'
        ack_file = folder / 'readproof.json'
        failure_file = folder / 'attempt_failed.json'
        delivery_file = folder / 'attempt_landed.json'
        state = 'QUEUED'
        problem = None
        if payload_file.exists():
            data = payload_file.read_bytes()
            if data != expected or sha(data) != expected_sha:
                state, problem = 'BLOCKED_INTEGRITY', 'payload mismatch'
            else:
                state = 'LANDED_UNACKNOWLEDGED'
        if ack_file.exists():
            try:
                ack = json.loads(ack_file.read_bytes())
                if state != 'LANDED_UNACKNOWLEDGED' or (
                    ack.get('destination') != dest or
                    ack.get('payload_sha256') != expected_sha or
                    ack.get('source_sha256') != sha(raw) or
                    ack.get('reader') != 'FRESH_LOCAL_CLI_PROCESS' or
                    ack.get('decision') != 'ACK_LOCAL_READ_ONLY'
                ):
                    raise ValueError('bad ack')
                state = 'ACKED_LOCAL_PROCESS'
            except (ValueError, TypeError, OSError):
                state, problem = 'BLOCKED_INTEGRITY', 'invalid or inconsistent ACK'
        if state == 'QUEUED' and failure_file.exists():
            state = 'FAILED_RETRYABLE'
        out[dest] = {'state': state, 'problem': problem,
                     'failure_attempt_preserved': failure_file.exists(),
                     'delivery_attempt_sha256': sha(delivery_file.read_bytes()) if delivery_file.exists() else None,
                     'ack_sha256': sha(ack_file.read_bytes()) if ack_file.exists() else None}
    return {'schema': 'CoAll.GoldenBraidLocalStatus.R0', 'source_sha256': sha(raw),
            'task_id': packet['task_id'], 'stop': stop, 'destinations': out,
            'all_local_ack': all(x['state'] == 'ACKED_LOCAL_PROCESS' for x in out.values()),
            'actual_external_receivers': 0, 'next': ('STOPPED' if stop else 'VERIFY_REAL_AUTHORIZED_RECEIVERS'),
            'nonclaims': ['LOCAL_PROCESS_NE_EXTERNAL_RECEIVER', 'ATTEMPT_NE_DELIVERY',
                          'FILE_LANDING_NE_ACK', 'ACK_NE_INTEGRATION', 'NO_LIVE_SESSION_SYNC']}


def dispatch(packet_file, root, fail=None):
    packet, raw = load_packet(packet_file)
    current = status(packet_file, root)
    if current['stop']:
        raise ValueError('STOP is active')
    if any(x['state'] == 'BLOCKED_INTEGRITY' for x in current['destinations'].values()):
        raise ValueError('integrity violation: do not continue')
    results = {}
    for dest in DESTS:
        folder = base(root, dest)
        existing = current['destinations'][dest]['state']
        if existing in ('LANDED_UNACKNOWLEDGED', 'ACKED_LOCAL_PROCESS'):
            results[dest] = 'UNCHANGED_EXISTING'; continue
        if dest == fail:
            failure = folder / 'attempt_failed.json'
            if not failure.exists():
                write_once(failure, {'task_id': packet['task_id'],
                                     'source_sha256': sha(raw), 'destination': dest,
                                     'state': 'SIMULATED_TRANSPORT_FAILURE'})
            results[dest] = 'FAILED_INJECTED'; continue
        write_once(folder / 'payload.json', packet)
        write_once(folder / 'attempt_landed.json', {
            'task_id': packet['task_id'], 'destination': dest,
            'source_sha256': sha(raw), 'payload_sha256': sha(canon(packet)),
            'state': 'LANDED_LOCAL_TEST_BYTES', 'external_effects': 0})
        results[dest] = 'LANDED_LOCAL_TEST_BYTES'
    return {'source_sha256': sha(raw), 'dispatch_results': results,
            'status': status(packet_file, root), 'external_effects': 0}


def receive(packet_file, root, dest):
    packet, raw = load_packet(packet_file)
    state = status(packet_file, root)
    if state['stop']:
        raise ValueError('STOP is active')
    current = state['destinations'][dest]['state']
    if current == 'ACKED_LOCAL_PROCESS':
        return {'decision': 'DUPLICATE_NOOP', 'destination': dest}
    if current != 'LANDED_UNACKNOWLEDGED':
        raise ValueError('cannot ACK absent or invalid payload')
    payload = base(root, dest) / 'payload.json'
    digest = sha(payload.read_bytes())
    if payload.read_bytes() != canon(packet):
        raise ValueError('readback payload mismatch')
    ack = {'schema': 'CoAll.GoldenBraidLocalReadproof.R0',
           'task_id': packet['task_id'], 'destination': dest,
           'source_sha256': sha(raw), 'payload_sha256': digest,
           'reader': 'FRESH_LOCAL_CLI_PROCESS', 'decision': 'ACK_LOCAL_READ_ONLY',
           'scope': 'SYNTHETIC_LOCAL_TEST_ONLY', 'external_effects': 0,
           'nonclaims': ['LOCAL_PROCESS_NE_INDEPENDENT_HOST', 'ACK_NE_INTEGRATION']}
    receipt_hash = write_once(base(root, dest) / 'readproof.json', ack)
    return {'decision': 'ACK_LOCAL_READ_ONLY', 'destination': dest,
            'ack_sha256': receipt_hash}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['dispatch', 'receive', 'status'])
    p.add_argument('--packet', required=True)
    p.add_argument('--root', required=True)
    p.add_argument('--fail', choices=DESTS)
    p.add_argument('--dest', choices=DESTS)
    args = p.parse_args()
    try:
        if args.command == 'dispatch':
            output = dispatch(args.packet, args.root, args.fail)
        elif args.command == 'receive':
            if args.dest is None:
                raise ValueError('--dest required')
            output = receive(args.packet, args.root, args.dest)
        else:
            output = status(args.packet, args.root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.error(str(exc))
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
