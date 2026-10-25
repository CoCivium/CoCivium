#!/usr/bin/env python3
"""CoZombie R0: read-only triage of *supplied* status records, never live process access.

NO killing, waking, polling, scheduling, provider login, lease overwrite or
network access. Each classification is a suggestion, not a process fact.
"""
import argparse
import json
from pathlib import Path

ALLOWED = {'session_id', 'observation_age_s', 'heartbeat_age_s', 'owner_observed_alive',
           'lease_expired', 'lease_contested', 'grant', 'source_valid', 'checkpoint_valid',
           'privacy_hold', 'quota_state', 'clock_skew', 'receiver_ack'}
NEXT = {
    'BLOCKED_REVOKED': 'Keep suspended; require a new explicit grant',
    'HELD_PRIVACY': 'Request a narrow permission review; do not inspect private content',
    'HELD_BAD_SOURCE': 'Revalidate source and checkpoint hashes without mutation',
    'ESCALATE_LEASE_CONFLICT': 'Inspect owner and lease evidence; do not reclaim automatically',
    'HELD_RATE_LIMIT': 'Respect provider cooldown; prefer safe unrelated local work',
    'HELD_UNFRESH_OBSERVATION': 'Refresh observation through an authorized, read-only path',
    'SUSPECTED_STALL': 'Verify owner independently, then consider supervised recovery',
    'MANUAL_RECLAIM_CANDIDATE': 'Supervisor must confirm owner death and compare exact checkpoint',
    'RECENT_ACTIVITY_OBSERVED': 'Observe only; recent heartbeat does not prove progress',
    'UNDETERMINED': 'Gather more evidence before restart or shutdown',
}

def triage(row, stale_after=120):
    if not isinstance(row, dict) or not isinstance(row.get('session_id'), str):
        raise ValueError('BAD_STATUS_RECORD')
    if not set(row).issubset(ALLOWED):
        raise ValueError('UNKNOWN_STATUS_FIELD')
    age = row.get('heartbeat_age_s')
    if age is not None and (isinstance(age, bool) or not isinstance(age, (int, float)) or age < 0):
        raise ValueError('BAD_HEARTBEAT_AGE')
    observed_age = row.get('observation_age_s')
    if observed_age is not None and (isinstance(observed_age, bool) or not isinstance(observed_age, (int, float)) or observed_age < 0):
        raise ValueError('BAD_OBSERVATION_AGE')
    if row.get('grant') in ('REVOKED', 'EXPIRED'):
        state = 'BLOCKED_REVOKED'
    elif row.get('privacy_hold') is True:
        state = 'HELD_PRIVACY'
    elif row.get('source_valid') is False or row.get('checkpoint_valid') is False:
        state = 'HELD_BAD_SOURCE'
    elif row.get('lease_contested') is True:
        state = 'ESCALATE_LEASE_CONFLICT'
    elif row.get('quota_state') == 'RATE_LIMITED':
        state = 'HELD_RATE_LIMIT'
    elif row.get('clock_skew') is True or observed_age is None or observed_age > stale_after:
        state = 'HELD_UNFRESH_OBSERVATION'
    elif age is not None and age > stale_after:
        if row.get('owner_observed_alive') is False and row.get('lease_expired') is True:
            state = 'MANUAL_RECLAIM_CANDIDATE'
        else:
            state = 'SUSPECTED_STALL'
    elif age is not None:
        state = 'RECENT_ACTIVITY_OBSERVED'
    else:
        state = 'UNDETERMINED'
    return {
        'session_id': row['session_id'], 'assessment': state,
        'next_safe_action': NEXT[state], 'receiver_ack': 'NOT_VERIFIED',
        'process_killed': False, 'automatic_wake': False, 'lease_overwritten': False,
        'note': 'Input is a supplied observation; no live X2/provider inspection performed.',
    }

DEMO = [
    {'session_id': 'synthetic-recent', 'observation_age_s': 4, 'heartbeat_age_s': 3,
     'owner_observed_alive': True, 'grant': 'CURRENT', 'source_valid': True},
    {'session_id': 'synthetic-unknown-owner', 'observation_age_s': 2, 'heartbeat_age_s': 480,
     'owner_observed_alive': None, 'lease_expired': True, 'grant': 'CURRENT'},
    {'session_id': 'synthetic-owner-confirmed-dead', 'observation_age_s': 2, 'heartbeat_age_s': 480,
     'owner_observed_alive': False, 'lease_expired': True, 'grant': 'CURRENT'},
    {'session_id': 'synthetic-revoked', 'observation_age_s': 1, 'heartbeat_age_s': 200,
     'owner_observed_alive': False, 'lease_expired': True, 'grant': 'REVOKED'},
    {'session_id': 'synthetic-rate-limit', 'observation_age_s': 1, 'heartbeat_age_s': 300,
     'quota_state': 'RATE_LIMITED', 'grant': 'CURRENT'},
]

def main():
    parser = argparse.ArgumentParser(description='No-effects CoZombie status audit')
    parser.add_argument('--input', type=Path, help='Explicit JSON list of status snapshots')
    parser.add_argument('--out', type=Path, default=Path('output/cozombie_triage.json'))
    args = parser.parse_args()
    snapshots = json.loads(args.input.read_text(encoding='utf-8')) if args.input else DEMO
    if not isinstance(snapshots, list) or not 1 <= len(snapshots) <= 500:
        raise ValueError('INVALID_SNAPSHOT_COUNT')
    result = {'schema': 'CoZombie.ReadOnlyTriage.R0', 'actual_device_observations': 0,
              'agents_restarted': 0, 'nonclaims': ['SUPPLIED_SNAPSHOT_NE_LIVE_PROCESS',
              'STALE_HEARTBEAT_NE_DEAD_WORKER', 'RESTART_CANDIDATE_NE_AUTHORITY'],
              'assessments': [triage(s) for s in snapshots]}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS_READ_ONLY_TRIAGE', 'sessions_assessed': len(snapshots),
                      'live_devices_probed': 0, 'restarts': 0, 'output': str(args.out)}))

if __name__ == '__main__':
    main()
