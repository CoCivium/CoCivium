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

class WorkIDTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.source = self.dir / 'CoPre.md'
        self.source.write_text('Synthetic public CoPre seed\n', encoding='utf-8')
        self.git('init', '--quiet')
        self.git('add', 'CoPre.md')
        self.git('-c', 'user.name=Synthetic Test', '-c', 'user.email=synthetic@example.invalid',
                 'commit', '--quiet', '-m', 'synthetic public fixture')
        self.head = self.git('rev-parse', 'HEAD').decode().strip()
        self.packet = source_packet(self.source, self.head)
        self.db = self.dir / 'recover.sqlite'

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.dir), *args],
                              capture_output=True, check=True, timeout=10).stdout

    def test_nonexistent_well_formed_commit_rejected(self):
        with self.assertRaisesRegex(Held, 'SOURCE_COMMIT_UNAVAILABLE'):
            source_packet(self.source, 'f' * 40)
        self.assertFalse(self.db.exists())

    def test_existing_commit_wrong_bytes_rejected(self):
        self.source.write_text('uncommitted different source\n', encoding='utf-8')
        with self.assertRaisesRegex(Held, 'SOURCE_COMMIT_BYTES_MISMATCH'):
            source_packet(self.source, self.head)

    def test_git_blob_cannot_impersonate_commit(self):
        blob = self.git('rev-parse', self.head + ':CoPre.md').decode().strip()
        with self.assertRaisesRegex(Held, 'SOURCE_OBJECT_NOT_COMMIT'):
            source_packet(self.source, blob)

    def test_source_outside_repository_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'CoPre.md'
            source.write_bytes(self.source.read_bytes())
            with self.assertRaisesRegex(Held, 'SOURCE_COMMIT_UNAVAILABLE'):
                source_packet(source, self.head)

    def test_historical_commit_valid_with_matching_bytes(self):
        self.git('-c', 'user.name=Synthetic Test', '-c', 'user.email=synthetic@example.invalid',
                 'commit', '--quiet', '--allow-empty', '-m', 'later commit')
        packet = source_packet(self.source, self.head)
        self.assertTrue(packet['source_ref'].endswith('@' + self.head))

    def test_cold_source_check_rejects_forged_commit(self):
        changed = dict(self.packet, source_ref='CoCivium/CoCivium:CoPre.md@' + 'f' * 40)
        commit_once(self.db, changed)  # Schema validation alone does not fetch source.
        report = self.dir / 'forged-readback.json'
        result = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] /
            'scripts' / 'CoNarrativeWorkIDR0.py'), 'verify', '--db', str(self.db),
            '--source', str(self.source), '--source-commit', 'f' * 40,
            '--report', str(report)], capture_output=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b'SOURCE_COMMIT_UNAVAILABLE', result.stderr)
        self.assertFalse(report.exists())

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
