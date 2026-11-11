"""Adversarial, isolated synthetic Narrative-to-WorkID replay proofs."""
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from CoNarrativeWorkIDR0 import Held, commit_once, connect, readback, revoke, source_packet

HEAD = 'a' * 40

class WorkIDTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.source = self.dir / 'CoPre.md'
        self.source.write_text('Synthetic public CoPre seed\n', encoding='utf-8')
        self.packet = source_packet(self.source, HEAD)
        self.db = self.dir / 'recover.sqlite'

    def test_ten_duplicate_assents_one_workid(self):
        results = [commit_once(self.db, self.packet) for _ in range(10)]
        self.assertEqual(sum(x['new_commits'] for x in results), 1)
        self.assertEqual(sum(x['duplicate'] for x in results), 9)
        self.assertEqual(readback(self.db)['committed_work_ids'], 1)

    def test_cold_reconstruction_from_only_db_and_source(self):
        commit_once(self.db, self.packet)
        result = readback(self.db, source_path=self.source)
        self.assertEqual(result['state'], 'COLD_SOURCE_RECONSTRUCTED')
        self.assertEqual(result['prior_decisions'], self.packet['prior_decisions'])
        self.assertEqual(result['open_blockers'], self.packet['open_blockers'])
        self.assertEqual(result['next_safe_deed'], self.packet['next_safe_deed'])
        self.assertFalse(result['external_receiver_ack'])

    def test_crash_before_commit_does_not_write(self):
        with self.assertRaisesRegex(Held, 'INJECTED_BEFORE_COMMIT'):
            commit_once(self.db, self.packet, fault='BEFORE_COMMIT')
        with self.assertRaisesRegex(Held, 'NOT_EXACTLY_ONE_WORKID'):
            readback(self.db)
        self.assertEqual(commit_once(self.db, self.packet)['new_commits'], 1)

    def test_ack_lost_after_commit_replays_without_double_actuation(self):
        with self.assertRaisesRegex(Held, 'INJECTED_AFTER_COMMIT_ACK_LOST'):
            commit_once(self.db, self.packet, fault='AFTER_COMMIT')
        self.assertEqual(commit_once(self.db, self.packet)['new_commits'], 0)
        self.assertEqual(readback(self.db)['committed_work_ids'], 1)

    def test_conflicting_source_revision_cannot_clobber_workid(self):
        commit_once(self.db, self.packet)
        changed = dict(self.packet, source_sha256='f' * 64)
        with self.assertRaisesRegex(Held, 'WORK_ID_REVISION_CONFLICT'):
            commit_once(self.db, changed)
        self.assertEqual(readback(self.db)['source_sha256'], self.packet['source_sha256'])

    def test_consent_and_privacy_fail_closed(self):
        for attr, value in [('consent', 'REAL_USER_APPROVED'), ('privacy', 'PRIVATE_LOCAL'),
                            ('consent_epoch', 0), ('lease_epoch', 0)]:
            with self.subTest(attr=attr):
                with self.assertRaises(Held):
                    commit_once(self.db, dict(self.packet, **{attr: value}))
        self.assertFalse(self.db.exists())

    def test_stale_fence_rejected(self):
        commit_once(self.db, self.packet)
        with self.assertRaisesRegex(Held, 'EPOCH_NOT_APPROVED'):
            commit_once(self.db, dict(self.packet, lease_epoch=2))

    def test_revoke_retains_proof_and_blocks_late_replay(self):
        commit_once(self.db, self.packet)
        revoke(self.db, self.packet)
        self.assertEqual(readback(self.db)['state'], 'HELD_REVOKED')
        self.assertIsNone(readback(self.db)['next_safe_deed'])
        with self.assertRaisesRegex(Held, 'HELD_REVOKED'):
            commit_once(self.db, self.packet)

    def test_tamper_detected_in_cold_readback(self):
        commit_once(self.db, self.packet)
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE work SET packet_sha256=?", ('0' * 64,))
        with self.assertRaisesRegex(Held, 'PACKET_DIGEST_MISMATCH'):
            readback(self.db)

    def test_changed_original_source_fails_cold_proof(self):
        commit_once(self.db, self.packet)
        self.source.write_text('Modified source\n', encoding='utf-8')
        with self.assertRaisesRegex(Held, 'SOURCE_NO_LONGER_MATCHES'):
            readback(self.db, source_path=self.source)

    def test_receiver_is_not_independent_provider(self):
        commit_once(self.db, self.packet)
        result = readback(self.db)
        self.assertFalse(result['independent_provider'])
        self.assertFalse(result['live_mouse_binding'])
        self.assertIn('NO_AUTONOMOUS_WORKER', result['nonclaims'])

if __name__ == '__main__':
    unittest.main()
