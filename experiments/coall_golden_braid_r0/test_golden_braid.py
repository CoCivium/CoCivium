import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import golden_braid as b


class GoldenBraidTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'out'
        self.packet = Path(self.tmp.name) / 'packet.json'
        self.packet.write_bytes((ROOT / 'packet.json').read_bytes())

    def cli(self, *args, ok=True):
        cmd = [sys.executable, '-B', str(ROOT / 'golden_braid.py'), *args,
               '--packet', str(self.packet), '--root', str(self.root)]
        cp = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if ok:
            self.assertEqual(cp.returncode, 0, cp.stderr)
            return json.loads(cp.stdout)
        self.assertNotEqual(cp.returncode, 0)
        return cp.stderr

    def test_requires_exact_packet_fields(self):
        p = json.loads(self.packet.read_text())
        del p['task_id']
        self.packet.write_text(json.dumps(p))
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            b.load_packet(self.packet)

    def test_reject_non_synthetic_scope(self):
        p = json.loads(self.packet.read_text())
        p['scope'] = 'SEND_TO_REAL_GMAIL'
        self.packet.write_text(json.dumps(p))
        with self.assertRaisesRegex(ValueError, 'authority'):
            b.load_packet(self.packet)

    def test_reject_outside_destination(self):
        with self.assertRaises(ValueError):
            b.base(self.root, '../somewhere')

    def test_initial_state_queued_no_ack(self):
        result = self.cli('status')
        self.assertEqual([s['state'] for s in result['destinations'].values()], ['QUEUED', 'QUEUED'])
        self.assertFalse(result['all_local_ack'])
        self.assertEqual(result['actual_external_receivers'], 0)

    def test_failure_is_preserved_and_retryable(self):
        initial = self.cli('dispatch', '--fail', 'test-beta')
        self.assertEqual(initial['status']['destinations']['test-beta']['state'], 'FAILED_RETRYABLE')
        self.assertTrue((self.root / 'test-beta' / 'attempt_failed.json').exists())
        recovered = self.cli('dispatch')
        self.assertEqual(recovered['status']['destinations']['test-beta']['state'], 'LANDED_UNACKNOWLEDGED')
        self.assertTrue(recovered['status']['destinations']['test-beta']['failure_attempt_preserved'])

    def test_delivery_attempt_receipts_are_separate_and_source_bound(self):
        result = self.cli('dispatch')
        for name in b.DESTS:
            attempt = json.loads((self.root / name / 'attempt_landed.json').read_text())
            self.assertEqual(attempt['source_sha256'], result['source_sha256'])
            self.assertEqual(attempt['destination'], name)
            self.assertTrue(result['status']['destinations'][name]['delivery_attempt_sha256'])

    def test_failed_delivery_has_no_success_attempt(self):
        self.cli('dispatch', '--fail', 'test-beta')
        self.assertFalse((self.root / 'test-beta' / 'payload.json').exists())
        self.assertFalse((self.root / 'test-beta' / 'attempt_landed.json').exists())
        self.assertTrue((self.root / 'test-beta' / 'attempt_failed.json').exists())

    def test_fresh_process_ack_and_reconstruction(self):
        self.cli('dispatch', '--fail', 'test-beta')
        first = self.cli('receive', '--dest', 'test-alpha')
        self.assertEqual(first['decision'], 'ACK_LOCAL_READ_ONLY')
        phase = self.cli('status')
        self.assertFalse(phase['all_local_ack'])
        self.cli('dispatch')
        second = self.cli('receive', '--dest', 'test-beta')
        self.assertNotEqual(first['ack_sha256'], second['ack_sha256'])
        recovered = self.cli('status')
        self.assertTrue(recovered['all_local_ack'])
        self.assertEqual(recovered['actual_external_receivers'], 0)
        self.assertEqual(recovered['destinations']['test-beta']['state'], 'ACKED_LOCAL_PROCESS')

    def test_already_completed_payload_is_not_rewritten(self):
        self.cli('dispatch', '--fail', 'test-beta')
        self.cli('receive', '--dest', 'test-alpha')
        before = (self.root / 'test-alpha' / 'payload.json').read_bytes()
        ackbefore = (self.root / 'test-alpha' / 'readproof.json').read_bytes()
        result = self.cli('dispatch')
        self.assertEqual(result['dispatch_results']['test-alpha'], 'UNCHANGED_EXISTING')
        self.assertEqual(before, (self.root / 'test-alpha' / 'payload.json').read_bytes())
        self.assertEqual(ackbefore, (self.root / 'test-alpha' / 'readproof.json').read_bytes())

    def test_duplicate_ack_is_noop(self):
        self.cli('dispatch')
        self.cli('receive', '--dest', 'test-alpha')
        before = (self.root / 'test-alpha' / 'readproof.json').read_bytes()
        second = self.cli('receive', '--dest', 'test-alpha')
        self.assertEqual(second['decision'], 'DUPLICATE_NOOP')
        self.assertEqual(before, (self.root / 'test-alpha' / 'readproof.json').read_bytes())

    def test_cannot_ack_missing_payload(self):
        err = self.cli('receive', '--dest', 'test-beta', ok=False)
        self.assertIn('cannot ACK absent', err)
        self.assertFalse((self.root / 'test-beta' / 'readproof.json').exists())

    def test_payload_mutation_blocks_recovery(self):
        self.cli('dispatch')
        (self.root / 'test-beta' / 'payload.json').write_text('{"changed":true}')
        result = self.cli('status')
        self.assertEqual(result['destinations']['test-beta']['state'], 'BLOCKED_INTEGRITY')
        err = self.cli('dispatch', ok=False)
        self.assertIn('integrity violation', err)

    def test_ack_tamper_is_detected(self):
        self.cli('dispatch')
        self.cli('receive', '--dest', 'test-alpha')
        p = self.root / 'test-alpha' / 'readproof.json'
        d = json.loads(p.read_text())
        d['payload_sha256'] = 'FORGED'
        p.write_text(json.dumps(d))
        result = self.cli('status')
        self.assertEqual(result['destinations']['test-alpha']['state'], 'BLOCKED_INTEGRITY')

    def test_changed_source_packet_does_not_inherit_old_receipt(self):
        self.cli('dispatch')
        self.cli('receive', '--dest', 'test-alpha')
        packet = json.loads(self.packet.read_text())
        packet['intent'] = 'a changed intent'
        self.packet.write_text(json.dumps(packet))
        result = self.cli('status')
        self.assertEqual(result['destinations']['test-alpha']['state'], 'BLOCKED_INTEGRITY')

    def test_stop_blocks_dispatch_and_ack(self):
        self.cli('dispatch')
        (self.root / 'STOP').write_text('revoked by fixture')
        self.assertTrue(self.cli('status')['stop'])
        self.assertIn('STOP is active', self.cli('receive', '--dest', 'test-alpha', ok=False))
        self.assertIn('STOP is active', self.cli('dispatch', ok=False))

    def test_destination_symlink_rejected(self):
        target = Path(self.tmp.name) / 'outsider'
        target.mkdir()
        self.root.mkdir()
        try:
            (self.root / 'test-alpha').symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('symlinks not permitted on this platform')
        self.assertIn('no symlink', self.cli('dispatch', ok=False))

    def test_local_receipts_never_claim_external_receiver(self):
        self.cli('dispatch')
        self.cli('receive', '--dest', 'test-alpha')
        self.cli('receive', '--dest', 'test-beta')
        result = self.cli('status')
        self.assertEqual(result['actual_external_receivers'], 0)
        self.assertIn('NO_LIVE_SESSION_SYNC', result['nonclaims'])
        self.assertEqual(result['next'], 'VERIFY_REAL_AUTHORIZED_RECEIVERS')


if __name__ == '__main__':
    unittest.main()
