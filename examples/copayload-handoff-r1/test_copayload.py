#!/usr/bin/env python3
"""Offline tests: no online dependency and no OS hooks."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from copayload import prepare, verify, write_new, consume_file, Hold, CHUNK_MAX


class CoPayloadTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.payload=self.root/"synthetic_video.mp4"
        # Deterministic non-secret fixture, >300 KB, not a playable video.
        seed=(b"CoPayload synthetic public fixture; not real media\n"*8192)
        self.payload.write_bytes(seed)
        self.out=self.root/"manifest.json"
        self.m=prepare(self.payload,"PUBLIC_SAFE_FIXTURE",1024**3,CHUNK_MAX)
    def test_exact_sha(self):
        self.assertEqual(self.m['source_sha256'], hashlib.sha256(self.payload.read_bytes()).hexdigest())
    def test_large_fixture(self):
        self.assertGreater(self.m['byte_count'], 300000)
    def test_not_fake_ffprobe(self):
        self.assertEqual(self.m['type_evidence'], 'FILENAME_EXTENSION_ONLY_NOT_MEDIA_DECODER')
    def test_public_manifest_does_not_include_source_paths(self):
        s=json.dumps(self.m)
        self.assertNotIn(str(self.root),s)
        self.assertNotIn(self.payload.name,s)
    def test_no_implicit_authority(self):
        self.assertEqual(self.m['authority_ceiling'],'NONE')
        self.assertFalse(self.m['receiver_ack'])
        self.assertEqual(self.m['outbound_effects'],0)
    def test_no_source_mutation(self):
        before=self.payload.read_bytes()
        write_new(self.out,self.m)
        self.assertEqual(self.payload.read_bytes(),before)
    def test_no_clobber(self):
        write_new(self.out,self.m)
        with self.assertRaises(Hold):write_new(self.out,self.m)
    def test_exact_readback(self):
        write_new(self.out,self.m)
        result=verify(self.payload,self.out,1024**3)
        self.assertEqual(result['status'],'PASS_EXACT_BYTES_ONLY')
        self.assertFalse(result['independent_receiver_ack'])
    def test_source_tamper_is_held(self):
        write_new(self.out,self.m)
        self.payload.write_bytes(self.payload.read_bytes()+b'x')
        with self.assertRaises(Hold):verify(self.payload,self.out,1024**3)
    def test_manifest_tamper_is_held(self):
        other=self.root/'evil.json';v=dict(self.m);v['authority_ceiling']='SEND';other.write_text(json.dumps(v))
        with self.assertRaises(Hold):verify(self.payload,other,1024**3)
    def test_chunk_digests_tamper_is_held(self):
        other=self.root/'evil.json';v=json.loads(json.dumps(self.m));v['chunk_hashes'][0]['sha256']='0'*64;other.write_text(json.dumps(v))
        with self.assertRaises(Hold):verify(self.payload,other,1024**3)
    def test_large_file_chunk_cap(self):
        # Larger than max_chunks * 1 MiB, still bounded manifest entries.
        big=self.root/'huge.dat'
        with big.open('wb') as f:
            for i in range(40): f.write(bytes([i])*1024**2)
        r=prepare(big,'PRIVATE',100*1024**2,CHUNK_MAX)
        self.assertLessEqual(len(r['chunk_hashes']),CHUNK_MAX)
        out=self.root/'huge.json';write_new(out,r)
        self.assertEqual(verify(big,out,100*1024**2)['status'],'PASS_EXACT_BYTES_ONLY')
    def test_source_over_budget_held(self):
        with self.assertRaises(Hold):prepare(self.payload,'PRIVATE',500,CHUNK_MAX)
    def test_missing_source_held(self):
        with self.assertRaises(Hold):prepare(self.root/'missing','PRIVATE',500,CHUNK_MAX)
    def test_symlink_source_held(self):
        if not hasattr(os,'symlink'):self.skipTest('symlink unsupported')
        link=self.root/'link'
        try:link.symlink_to(self.payload)
        except OSError:self.skipTest('symlink cannot be created')
        with self.assertRaises(Hold):prepare(link,'PRIVATE',1024**3,CHUNK_MAX)
    def test_manifest_missing_parent_held(self):
        with self.assertRaises(Hold):write_new(self.root/'absent'/'manifest.json',self.m)
    def test_empty_file(self):
        e=self.root/'empty.bin';e.write_bytes(b'')
        r=prepare(e,'PRIVATE',1024**3,CHUNK_MAX);self.assertEqual(r['chunk_hashes'],[])
        out=self.root/'empty.json';write_new(out,r)
        self.assertEqual(verify(e,out,1024**3)['bytes_read'],0)
    def test_exact_bytes_not_semantic_validation(self):
        write_new(self.out,self.m)
        self.assertEqual(verify(self.payload,self.out,1024**3)['semantic_validation'],'NOT_PERFORMED')
    def test_no_untrusted_recipient(self):
        self.assertEqual(self.m['receiver_candidates'],[])
        self.assertEqual(self.m['status'],'LOCAL_CANDIDATE_PREVIEW_ONLY')

if __name__=='__main__':unittest.main()
