import copy
import json
import pathlib
import tempfile
import unittest
from cross_job_handoff_r0 import produce, consume, Held, LITERAL, digest

class TestCrossJobHandoff(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.pkg = self.root / "pkg"
        self.record = produce(self.pkg)
        self.receipt = self.root / "readback.json"
    def rewrite(self, **changes):
        fp = self.pkg / 'handoff.json'
        j = json.loads(fp.read_text()); j.update(changes)
        fp.write_text(json.dumps(j))
    def test_fresh_process_equivalent(self):
        out=consume(self.pkg,self.receipt)
        self.assertTrue(out['receiver_restored_bytes_match_literal'])
        self.assertEqual(out['content_sha256'],digest(LITERAL))
        self.assertFalse(out['third_party_independent_receiver_ack'])
    def test_refuse_producer_clobber(self):
        with self.assertRaisesRegex(Held,'NO_PRODUCER_OVERWRITE'): produce(self.pkg)
    def test_missing_primary_copy_fail_closed(self):
        (self.pkg/'capsule'/'payload.bin').unlink()
        with self.assertRaisesRegex(Held,'CAPSULE_FILESET_MISMATCH'): consume(self.pkg,self.receipt)
    def test_corrupted_primary_copy_fail_closed(self):
        (self.pkg/'capsule'/'payload.bin').write_bytes(b'wrong')
        with self.assertRaisesRegex(Held,'INCOMPLETE_TRANSFER'): consume(self.pkg,self.receipt)
    def test_corrupted_recovery_copy_fail_closed(self):
        (self.pkg/'capsule'/'recovery.bin').write_bytes(b'wrong')
        with self.assertRaisesRegex(Held,'INCOMPLETE_TRANSFER'): consume(self.pkg,self.receipt)
    def test_forged_sha_in_envelope(self):
        self.rewrite(source_sha256='0'*64)
        with self.assertRaisesRegex(Held,'UNEXPECTED_SOURCE_CONTENT'):consume(self.pkg,self.receipt)
    def test_modified_manifest(self):
        fp=self.pkg/'capsule'/'manifest.json';fp.write_text(fp.read_text().replace('document','source',1))
        with self.assertRaisesRegex(Held,'MANIFEST_TRANSFER_TAMPER'): consume(self.pkg,self.receipt)
    def test_fake_receiver_ack(self):
        self.rewrite(receiver_ack=True)
        with self.assertRaisesRegex(Held,'FABRICATED_PROOF'):consume(self.pkg,self.receipt)
    def test_fake_independent_storage(self):
        self.rewrite(independent_storage_verified=True)
        with self.assertRaisesRegex(Held,'FABRICATED_PROOF'):consume(self.pkg,self.receipt)
    def test_extra_artifact_contents(self):
        (self.pkg/'extra').write_text('x')
        with self.assertRaisesRegex(Held,'ARTIFACT_ROOT_MISMATCH'):consume(self.pkg,self.receipt)
    def test_unsanctioned_effect_class(self):
        self.rewrite(authority='PUBLISH')
        with self.assertRaisesRegex(Held,'AUTHORITY_ESCALATION'): consume(self.pkg,self.receipt)
    def test_no_overwrite_readback(self):
        self.receipt.write_text('preserve')
        with self.assertRaisesRegex(Held,'RECEIPT_DEST_NOT_CLEAN'): consume(self.pkg,self.receipt)
        self.assertEqual(self.receipt.read_text(),'preserve')
    def test_unknown_metadata_field_rejected(self):
        self.rewrite(remote_ack=True)
        with self.assertRaisesRegex(Held,'ENVELOPE_FIELDS_DIVERGED'):consume(self.pkg,self.receipt)

if __name__=='__main__': unittest.main(verbosity=2)