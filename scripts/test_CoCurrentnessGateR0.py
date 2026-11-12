#!/usr/bin/env python3
"""Deterministic synthetic tests; no X2 access or runtime effect."""
import copy
import unittest
from datetime import datetime, timedelta, timezone

from CoCurrentnessGateR0 import assess

BASE = datetime(2026, 11, 11, 18, 0, tzinfo=timezone.utc)
BIN = r'D:\CoCivium\CoReceiver.exe'
HASH = 'a' * 64


def iso(dt):
    return dt.isoformat()


def fixture(at=BASE, seq=15, pid=4321, stamp_offset=0, process_start=None):
    start = process_start or BASE - timedelta(hours=1)
    return {
        'evaluated_at_utc': iso(at),
        'status': {
            'utc': iso(at + timedelta(seconds=stamp_offset)),
            'state': 'ALIVE_LOCAL',
            'heartbeat_period_seconds': 5,
            'heartbeat_seq': seq,
            'components': {
                'CoBarCurrentReceiver_v0_5': {
                    'pid': pid,
                    'path': BIN,
                    'expected_sha256': HASH,
                    'running': True,
                }
            },
        },
        'probe': {
            'captured_at_utc': iso(at),
            'pid': pid,
            'process_exists': True,
            'executable_path': BIN,
            'executable_sha256': HASH,
            'process_start_utc': iso(start),
        },
    }


class GateTests(unittest.TestCase):
    def test_first_sample_alone_is_held(self):
        self.assertEqual(assess(fixture())['state'], 'HELD_SINGLE_SAMPLE_PROGRESS_UNPROVEN')

    def test_two_fresh_advancing_samples_pass(self):
        first = fixture(at=BASE - timedelta(minutes=2), seq=15)
        second = fixture(at=BASE, seq=35)
        self.assertEqual(assess(second, first)['state'], 'PASS_BOUNDED_HEARTBEAT_PROGRESS')

    def test_stale_even_with_matching_running_pid(self):
        sample = fixture(stamp_offset=-3600)
        out = assess(sample)
        self.assertEqual(out['state'], 'FAIL_CLOSED_RECEIVER_CURRENTNESS')
        self.assertIn('STATUS_EXPIRED', out['reasons'])

    def test_stale_and_missing_process_like_x2(self):
        sample = fixture(stamp_offset=-295456)
        sample['probe']['process_exists'] = False
        out = assess(sample)
        self.assertIn('STATUS_EXPIRED', out['reasons'])
        self.assertIn('RECEIVER_PROCESS_NOT_OBSERVED', out['reasons'])

    def test_future_dated_source_fails(self):
        self.assertIn('STATUS_FROM_FUTURE', assess(fixture(stamp_offset=30))['reasons'])

    def test_missing_pid_fails(self):
        sample = fixture()
        sample['probe']['pid'] = 1234
        self.assertIn('RECEIVER_PID_NOT_BOUND', assess(sample)['reasons'])

    def test_pid_reuse_wrong_executable_fails(self):
        sample = fixture()
        sample['probe']['executable_path'] = 'D:\\other.exe'
        self.assertIn('RECEIVER_EXECUTABLE_PATH_MISMATCH', assess(sample)['reasons'])

    def test_executable_hash_mismatch_fails(self):
        sample = fixture()
        sample['probe']['executable_sha256'] = 'b' * 64
        self.assertIn('RECEIVER_EXECUTABLE_HASH_MISMATCH', assess(sample)['reasons'])

    def test_probe_staleness_fails(self):
        sample = fixture()
        sample['probe']['captured_at_utc'] = iso(BASE - timedelta(seconds=45))
        self.assertIn('PROCESS_PROBE_NOT_CURRENT', assess(sample)['reasons'])

    def test_nonadvancing_seq_fails_after_window(self):
        first = fixture(at=BASE - timedelta(minutes=2), seq=15)
        second = fixture(at=BASE, seq=15)
        self.assertIn('HEARTBEAT_NOT_ADVANCING', assess(second, first)['reasons'])

    def test_short_window_is_held(self):
        first = fixture(at=BASE - timedelta(seconds=10), seq=15)
        self.assertEqual(assess(fixture(seq=16), first)['state'], 'HELD_WINDOW_TOO_SHORT')

    def test_changed_process_epoch_requires_new_window(self):
        first = fixture(at=BASE - timedelta(minutes=2), seq=15)
        second = fixture(seq=16, process_start=BASE - timedelta(minutes=1))
        self.assertEqual(assess(second, first)['state'], 'HELD_PROCESS_EPOCH_CHANGED')

    def test_malformed_evidence_fails_closed(self):
        sample = fixture()
        del sample['status']['components']
        self.assertEqual(assess(sample)['state'], 'FAIL_CLOSED_RECEIVER_CURRENTNESS')

    def test_invalid_previous_cannot_yield_pass(self):
        first = fixture(at=BASE - timedelta(minutes=2), seq=15)
        first['probe']['process_exists'] = False
        self.assertIn('PREVIOUS_SAMPLE_UNQUALIFIED', assess(fixture(seq=25), first)['reasons'])

    def test_no_receiver_ack_in_success(self):
        first = fixture(at=BASE - timedelta(minutes=2), seq=15)
        out = assess(fixture(seq=25), first)
        self.assertFalse(out['receiver_pickup_ack'])
        self.assertFalse(out['physical_receiver_inspection_performed'])


if __name__ == '__main__':
    unittest.main()
