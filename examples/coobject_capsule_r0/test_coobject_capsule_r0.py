#!/usr/bin/env python3
import contextlib
import hashlib
import io
import json
import pathlib
import tempfile
import unittest
from coobject_capsule_r0 import CapsuleError, pack, verify, restore, relate, manifest_for, main

class CapsuleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.src = self.root / 'source.txt'
        self.src.write_text('One small complete CoObject.\n', encoding='utf-8')
        self.cap = self.root / 'capsule'
        self.first = pack(self.src, self.cap, 'One source question', 'question', 'Read this one source')
    def change_manifest(self, **kwargs):
        p = self.cap / 'manifest.json'
        obj = json.loads(p.read_text())
        obj.update(kwargs)
        p.write_text(json.dumps(obj))
    def test_pack_both_copies_ready(self):
        self.assertEqual(self.first['status'], 'READY_LOCAL_TWO_COPIES')
    def test_hash_match(self):
        self.assertEqual(self.first['content_sha256'], hashlib.sha256(self.src.read_bytes()).hexdigest())
    def test_both_source_capsule_and_manifest(self):
        self.assertEqual(set(p.name for p in self.cap.iterdir()), {'manifest.json','payload.bin','recovery.bin'})
    def test_no_executable_authority(self):
        self.assertEqual(manifest_for(self.cap)['authority'], 'DATA_ONLY_NO_EXECUTION')
    def test_one_replica_loss_graceful_degradation(self):
        (self.cap/'payload.bin').unlink()
        self.assertEqual(verify(self.cap)['status'], 'DEGRADED_LOCAL_ONE_COPY')
    def test_one_replica_corruption_graceful_degradation(self):
        (self.cap/'payload.bin').write_text('tampered')
        self.assertEqual(verify(self.cap)['status'], 'DEGRADED_LOCAL_ONE_COPY')
    def test_restore_after_primary_loss(self):
        (self.cap/'payload.bin').unlink()
        result = restore(self.cap, self.root/'recover.txt')
        self.assertEqual(result['source_copy'], 'recovery.bin')
        self.assertEqual((self.root/'recover.txt').read_bytes(), self.src.read_bytes())
    def test_restore_never_clobbers(self):
        with self.assertRaisesRegex(CapsuleError,'RESTORE_NO_CLOBBER'):
            restore(self.cap, self.src)
        self.assertEqual(self.src.read_text(), 'One small complete CoObject.\n')
    def test_both_copies_loss_is_hold(self):
        (self.cap/'payload.bin').unlink(); (self.cap/'recovery.bin').unlink()
        self.assertEqual(verify(self.cap)['status'], 'HELD_NO_VALID_LOCAL_COPY')
        with self.assertRaisesRegex(CapsuleError,'HELD_NO_VALID_COPY'):
            restore(self.cap, self.root/'recover.txt')
    def test_both_copy_tamper_is_hold(self):
        for f in ('payload.bin','recovery.bin'):
            (self.cap/f).write_text('bad')
        self.assertEqual(verify(self.cap)['status'], 'HELD_NO_VALID_LOCAL_COPY')
    def test_digest_change_does_not_greenwash(self):
        self.change_manifest(content_sha256='a'*64)
        self.assertEqual(verify(self.cap)['status'], 'HELD_NO_VALID_LOCAL_COPY')
    def test_unknown_authority_fails(self):
        self.change_manifest(authority='NETWORK_WRITE_ALLOWED')
        with self.assertRaisesRegex(CapsuleError,'AUTHORITY_ESCALATION'):
            verify(self.cap)
    def test_changed_privacy_fails(self):
        self.change_manifest(privacy='PUBLIC_AUTO_PUSH')
        with self.assertRaisesRegex(CapsuleError,'UNEXPECTED_PRIVACY'):
            verify(self.cap)
    def test_no_path_traversal(self):
        self.change_manifest(copies=['../outside', 'recovery.bin'])
        with self.assertRaisesRegex(CapsuleError,'NONCANONICAL_COPY_PATHS'):
            verify(self.cap)
    def test_reject_payload_symlink(self):
        (self.cap/'payload.bin').unlink(); (self.cap/'payload.bin').symlink_to(self.src)
        r = verify(self.cap)
        self.assertEqual(r['status'], 'DEGRADED_LOCAL_ONE_COPY')
        self.assertEqual(r['copies']['payload.bin'],'UNSAFE_OR_UNREADABLE')
    def test_no_receiver_ack_or_authentication_claim(self):
        result = verify(self.cap)
        self.assertFalse(result['receiver_acceptance_verified'])
        self.assertFalse(result['independent_origin_authentication_verified'])
        self.assertFalse(result['independent_physical_fault_domains_verified'])
    def test_empty_source_is_valid(self):
        other=self.root/'empty.txt'; other.write_bytes(b'')
        out=pack(other,self.root/'emptycap','Zero','document','Observe emptiness')
        self.assertEqual(out['status'],'READY_LOCAL_TWO_COPIES')
    def test_reject_pack_into_existing(self):
        with self.assertRaisesRegex(CapsuleError,'CAPSULE_DEST_ALREADY_EXISTS'):
            pack(self.src,self.cap,'One','document','Read')
    def test_reject_symlink_source(self):
        s=self.root/'link'; s.symlink_to(self.src)
        with self.assertRaisesRegex(CapsuleError,'NOT_REGULAR_FILE_OR_SYMLINK'):
            pack(s,self.root/'linkcap','Link','document','Read')
    def test_reject_oversize(self):
        self.src.write_bytes(b'X'*(16*1024*1024+1))
        with self.assertRaisesRegex(CapsuleError,'OVERSIZE'):
            pack(self.src,self.root/'hugecap','Big','data','Read')
    def test_seren_deterministic(self):
        other=self.root/'other.txt'; other.write_text('Independent document')
        pack(other,self.root/'cap2','Repair guide','document','Read')
        a=relate(self.cap,self.root/'cap2',seed=12)
        b=relate(self.cap,self.root/'cap2',seed=12)
        self.assertEqual(a,b)
        self.assertEqual(a['state'], 'SERENDIPITY_CANDIDATE_ONLY')
        self.assertFalse(a['new_relation_granted'])
    def test_seren_same_object_hold(self):
        with self.assertRaisesRegex(CapsuleError,'SAME_OBJECT'):
            relate(self.cap,self.cap,seed=1)
    def test_seren_unverified_source_hold(self):
        other=self.root/'other.txt'; other.write_text('another')
        pack(other,self.root/'cap2','Repair guide','document','Read')
        (self.cap/'payload.bin').unlink(); (self.cap/'recovery.bin').unlink()
        with self.assertRaisesRegex(CapsuleError,'CANNOT_RELATE'):
            relate(self.cap,self.root/'cap2',seed=1)
    def test_check_cli_reports_real_status(self):
        with contextlib.redirect_stdout(io.StringIO()) as f:
            exit_code=main(['check',str(self.cap)])
        self.assertEqual(exit_code,0)
        self.assertEqual(json.loads(f.getvalue())['status'], 'READY_LOCAL_TWO_COPIES')
    def test_failed_check_cli_exit_nonzero(self):
        (self.cap/'payload.bin').unlink(); (self.cap/'recovery.bin').unlink()
        with contextlib.redirect_stdout(io.StringIO()) as f:
            exit_code=main(['check',str(self.cap)])
        self.assertEqual(exit_code,2)
        self.assertEqual(json.loads(f.getvalue())['status'], 'HELD_NO_VALID_LOCAL_COPY')

if __name__ == '__main__': unittest.main(verbosity=2)
