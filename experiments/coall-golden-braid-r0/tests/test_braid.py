"""Offline independent-process and failure-state tests for issue #317."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import coall_braid as braid


class BraidTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'work'
        self.ids = braid.init(self.root, ROOT / 'fixture' / 'task_packet.json')

    def test_task_packet_has_provenance_and_wise_words(self):
        p, sha = braid.load_packet(self.root)
        self.assertEqual(sha, self.ids['task_sha256'])
        self.assertEqual(p['source']['git_blob'], '3bc1785a8381d607ae69804c587a191385d41429')
        self.assertEqual(p['insights'][0]['epistemic_state'], 'PROPOSAL_NOT_VALIDATED')

    def test_one_intake_event(self):
        rows, head = braid.read_journal(self.root)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['kind'], 'INTAKE')
        self.assertEqual(head, self.ids['head'])

    def test_refuse_clobber(self):
        with self.assertRaisesRegex(ValueError, 'NONEMPTY_ROOT_REFUSES_CLOBBER'):
            braid.init(self.root, ROOT / 'fixture' / 'task_packet.json')

    def test_reject_broader_authority(self):
        p, _ = braid.load_packet(self.root)
        p['scope']['external_effects_authorized'] = True
        with self.assertRaisesRegex(ValueError, 'AUTHORITY_REJECTED'):
            braid.check_packet(p)

    def test_reject_unsourced_insight(self):
        p, _ = braid.load_packet(self.root)
        p['insights'][0]['source_ref'] = ''
        with self.assertRaisesRegex(ValueError, 'INSIGHT_WITHOUT_PROVENANCE_OR_TEST'):
            braid.check_packet(p)

    def test_reject_unsupported_epistemic_promotion(self):
        p, _ = braid.load_packet(self.root)
        p['insights'][0]['epistemic_state'] = 'VERIFIED_FACT'
        with self.assertRaisesRegex(ValueError, 'INSIGHT_STATE_NOT_ALLOWED'):
            braid.check_packet(p)

    def test_pointer_rejects_changed_task_bytes(self):
        with open(self.root/'task.json', 'ab') as fh:
            fh.write(b' ')
        with self.assertRaisesRegex(ValueError, 'TASK_BYTES_CHANGED'):
            braid.load_packet(self.root)

    def test_external_expected_sha_check(self):
        with self.assertRaisesRegex(ValueError, 'TASK_BYTES_CHANGED'):
            braid.load_packet(self.root, expected_task_sha='0'*64)

    def test_changed_journal_rejected(self):
        journal = self.root/'events.jsonl'
        raw = journal.read_bytes()
        journal.write_bytes(raw.replace(b'INTAKE', b'INFAKE'))
        with self.assertRaisesRegex(ValueError, 'HASH_MISMATCH'):
            braid.read_journal(self.root)

    def test_wrong_head_rejected(self):
        with self.assertRaisesRegex(ValueError, 'HEAD_MISMATCH'):
            braid.read_journal(self.root, expected_head='f'*64)

    def test_two_receivers_success_and_distinct_pids(self):
        outcomes = braid.dispatch(self.root)
        self.assertEqual(outcomes, {'alpha':'VERIFIED_LOCAL_RECEIVER', 'beta':'VERIFIED_LOCAL_RECEIVER'})
        result = braid.reconcile(self.root, self.ids['task_sha256'])
        self.assertTrue(result['all_local_acked'])
        self.assertNotEqual(json.loads((self.root/'receivers/alpha/ack.json').read_text())['receiver_pid'],
                            json.loads((self.root/'receivers/beta/ack.json').read_text())['receiver_pid'])

    def test_failure_retry_and_idempotent_skip(self):
        first = braid.dispatch(self.root, fail_once_beta=True)
        self.assertEqual(first['alpha'], 'VERIFIED_LOCAL_RECEIVER')
        self.assertEqual(first['beta'], 'FAILED_PENDING_RETRY')
        middle = braid.reconcile(self.root)
        self.assertFalse(middle['all_local_acked'])
        self.assertEqual(middle['destinations']['beta'], 'FAILED_QUEUED')
        alpha_ack = (self.root/'receivers/alpha/ack.json').read_bytes()
        second = braid.dispatch(self.root, fail_once_beta=True)
        self.assertEqual(second['alpha'], 'SKIP_COMPLETED')
        self.assertEqual(second['beta'], 'VERIFIED_LOCAL_RECEIVER')
        self.assertTrue(braid.reconcile(self.root)['all_local_acked'])
        self.assertEqual((self.root/'receivers/alpha/ack.json').read_bytes(), alpha_ack)
        third = braid.dispatch(self.root, fail_once_beta=True)
        self.assertEqual(third, {'alpha':'SKIP_COMPLETED', 'beta':'SKIP_COMPLETED'})
        events, _ = braid.read_journal(self.root)
        acks = [e['destination'] for e in events if e['kind'] == 'ACK_VERIFIED']
        self.assertEqual(acks, ['alpha','beta'])

    def test_fresh_process_recovers_from_files(self):
        braid.dispatch(self.root, fail_once_beta=True)
        braid.dispatch(self.root, fail_once_beta=True)
        final = braid.reconcile(self.root)
        p = subprocess.run([sys.executable, str(ROOT/'coall_braid.py'),'reconcile',
                 '--root',str(self.root),'--expect-task-sha', self.ids['task_sha256'],
                 '--expect-head', final['journal_head']],capture_output=True,text=True,check=False)
        self.assertEqual(p.returncode,0, p.stderr)
        self.assertEqual(json.loads(p.stdout),final)

    def test_ack_file_recovered_after_supervisor_gap(self):
        first = braid.dispatch(self.root, skip_ack_log_for='alpha')
        self.assertEqual(first['alpha'],'ACK_FILE_EXISTS_BUT_NOT_RECORDED')
        self.assertEqual(braid.reconcile(self.root)['destinations']['alpha'],'ACK_EXISTS_PENDING_LEDGER_RECOVERY')
        before=(self.root/'receivers/alpha/ack.json').read_bytes()
        second=braid.dispatch(self.root)
        self.assertEqual(second['alpha'],'ACK_RECOVERED_NO_REDUPLICATION')
        self.assertEqual((self.root/'receivers/alpha/ack.json').read_bytes(),before)
        self.assertTrue(braid.reconcile(self.root)['all_local_acked'])

    def test_supervisor_lock_blocks_concurrent_dispatcher(self):
        with braid.supervisor_lock(self.root):
            with self.assertRaisesRegex(ValueError, 'DISPATCH_LOCK_HELD_REQUIRES_OWNER_REVIEW'):
                braid.dispatch(self.root)
        self.assertEqual(braid.dispatch(self.root)['alpha'], 'VERIFIED_LOCAL_RECEIVER')

    def test_crash_between_delivery_and_ack_recovers_without_rewrite(self):
        first=braid.dispatch(self.root, fail_after_delivery_beta=True)
        self.assertEqual(first['beta'],'FAILED_PENDING_RETRY')
        delivery=self.root/'receivers/beta/delivery.json'
        self.assertTrue(delivery.is_file())
        first_bytes=delivery.read_bytes()
        self.assertFalse((self.root/'receivers/beta/ack.json').exists())
        second=braid.dispatch(self.root, fail_after_delivery_beta=True)
        self.assertEqual(second['alpha'],'SKIP_COMPLETED')
        self.assertEqual(second['beta'],'VERIFIED_LOCAL_RECEIVER')
        self.assertEqual(delivery.read_bytes(),first_bytes)
        self.assertTrue(braid.reconcile(self.root)['all_local_acked'])

    def test_wrong_partial_delivery_fails_closed(self):
        braid.dispatch(self.root, fail_after_delivery_beta=True)
        delivery=self.root/'receivers/beta/delivery.json'
        delivery.write_text('{"malicious":true}',encoding='utf-8')
        out=braid.dispatch(self.root, fail_after_delivery_beta=True)
        self.assertEqual(out['beta'],'FAILED_PENDING_RETRY')
        self.assertFalse((self.root/'receivers/beta/ack.json').exists())
        self.assertFalse(braid.reconcile(self.root)['all_local_acked'])

    def test_ack_without_delivery_rejected(self):
        braid.dispatch(self.root)
        (self.root/'receivers/alpha/delivery.json').unlink()
        with self.assertRaisesRegex(ValueError,'ACK_WITHOUT_DELIVERY'):
            braid.reconcile(self.root)

    def test_forged_ack_detected(self):
        braid.dispatch(self.root)
        ack=self.root/'receivers/alpha/ack.json'
        obj=json.loads(ack.read_bytes())
        obj['receiver']='beta'
        ack.write_bytes(braid.canonical(obj))
        with self.assertRaisesRegex(ValueError,'RECEIVER_READBACK_MISMATCH'):
            braid.reconcile(self.root)

    def test_missing_ack_cannot_be_assumed_from_journal(self):
        braid.dispatch(self.root)
        (self.root/'receivers/beta/ack.json').unlink()
        with self.assertRaisesRegex(ValueError,'DURABLE_ACK_PROOF_LOST'):
            braid.reconcile(self.root)

    def test_stop_blocks_dispatch_and_worker(self):
        braid.stop(self.root)
        self.assertTrue(braid.reconcile(self.root)['revoked'])
        with self.assertRaisesRegex(ValueError,'REVOKED_STOP'):
            braid.dispatch(self.root)
        p=subprocess.run([sys.executable, str(ROOT/'coall_braid.py'),'worker','--root',str(self.root),
                          '--destination','alpha'],capture_output=True,text=True,check=False)
        self.assertEqual(p.returncode,3)
        self.assertIn('REVOKED_STOP',p.stderr)

    def test_stop_idempotent(self):
        braid.stop(self.root)
        before=(self.root/'events.jsonl').read_bytes()
        braid.stop(self.root)
        self.assertEqual((self.root/'events.jsonl').read_bytes(),before)

    def test_receiver_rejects_unknown_name(self):
        with self.assertRaisesRegex(ValueError,'RECEIVER_UNAUTHORIZED'):
            braid.worker(self.root,'charlie')

    def test_unverified_receiver_is_not_delivery_ack(self):
        summary=braid.reconcile(self.root)
        self.assertFalse(summary['all_local_acked'])
        self.assertEqual(summary['destinations'],{'alpha':'PENDING','beta':'PENDING'})
        self.assertEqual(summary['external_delivery_or_adoption'],'NOT_TESTED')

    def test_duplicate_json_key_rejected(self):
        j=self.root/'events.jsonl'
        line=j.read_bytes().splitlines()[0]
        j.write_bytes(line[:-1]+b',"seq":1}\n')
        with self.assertRaises(ValueError):
            braid.read_journal(self.root)


if __name__ == '__main__':
    unittest.main()
