import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import copayload_large_r0 as m


class LargePayloadTests(unittest.TestCase):
    def test_at_2gib_stage_boundary(self):
        self.assertTrue(m.plan([m.descriptor('x', 2*m.GIB, 'VIDEO')], 'STAGE_BYTES')['qualified'])

    def test_over_2gib_held(self):
        x = m.plan([m.descriptor('x', 2*m.GIB+1, 'VIDEO')], 'STAGE_BYTES')
        self.assertFalse(x['qualified'])
        self.assertIn('STAGING_LIMIT_2_GIB', x['hold_reasons'])

    def test_exact_16gib_reference(self):
        x = m.plan([m.descriptor('x', 16*m.GIB, 'ARCHIVE')], 'REFERENCE_ONLY')
        self.assertTrue(x['qualified'])
        self.assertEqual(x['items'][0]['actual_bytes_read'], 0)

    def test_over_16gib_held(self):
        self.assertFalse(m.plan([m.descriptor('x', 16*m.GIB+1, 'ARCHIVE')], 'REFERENCE_ONLY')['qualified'])

    def test_aggregate_limit(self):
        a = [m.descriptor('a', 8*m.GIB+1,'FILE'), m.descriptor('b',8*m.GIB,'FILE')]
        self.assertEqual(m.plan(a, 'REFERENCE_ONLY')['state'],'HOLD_LIMIT')

    def test_file_count(self):
        with self.assertRaises(ValueError): m.plan([m.descriptor(str(i),1,'FILE') for i in range(5)], 'REFERENCE_ONLY')

    def test_invalid_fields(self):
        with self.assertRaises(ValueError): m.plan([dict(m.descriptor('a', 1, 'FILE'),send=True)], 'REFERENCE_ONLY')

    def test_negative_and_bool(self):
        for n in (-1, True, 2.5):
            with self.subTest(n=n), self.assertRaises(ValueError): m.descriptor('x', n, 'FILE')

    def test_unknown_privacy_and_kind(self):
        with self.assertRaises(ValueError): m.descriptor('x', 1, 'MAGIC')
        with self.assertRaises(ValueError): m.descriptor('x', 1, 'VIDEO', privacy='SECRET_SEND_OK')

    def test_exact_chunk_count(self):
        x=m.plan([m.descriptor('x', m.CHUNK_BYTES+1, 'DATASET')], 'REFERENCE_ONLY')
        self.assertEqual(x['items'][0]['estimated_chunks_4mib'], 2)

    def test_no_external_or_hardware_authority(self):
        for name,items,mode,expected in m.fixtures():
            x=m.plan(items,mode)
            self.assertEqual(x['external_effects'],0)
            self.assertFalse(x['receiver_ack'])
            self.assertFalse(x['items'][0]['file_existed_or_was_staged'])
            self.assertEqual(x['native_thumb_binding'], 'NOT_TESTED')

    def test_bounded_cycles_and_replay(self):
        a=m.execute(3)
        self.assertEqual(a['status'],'PASS')
        self.assertEqual(len(a['history']),3)
        self.assertEqual(len({r['normalized_result_sha256'] for r in a['history']}),1)
        self.assertEqual(a, m.execute(3))
        self.assertEqual(a['history'][1]['previous_event_sha256'],m.sha(m.canonical(a['history'][0])))

    def test_excess_cycles_rejected(self):
        for n in (0, 4, True):
            with self.subTest(n=n),self.assertRaises(ValueError):m.execute(n)

    def test_actual_small_file_streaming_readproof(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"explicit.bin"
            payload=b"CoThumb real local readproof|" * 125000
            p.write_bytes(payload)
            before=p.read_bytes()
            res=m.inspect_real_file(p)
            self.assertEqual(res["bytes_read"],len(payload))
            self.assertEqual(res["sha256"],m.sha(payload))
            self.assertEqual(res["chunks_read"],1)
            self.assertEqual(res["staged_bytes"],0)
            self.assertEqual(p.read_bytes(),before)

    def test_symlink_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"source.bin";p.write_bytes(b"test")
            link=Path(temp)/"link.bin"
            link.symlink_to(p)
            with self.assertRaises(ValueError): m.inspect_real_file(link)

    def test_actual_file_not_exposed_as_path_in_summary(self):
        with tempfile.TemporaryDirectory() as temp:
            src=Path(temp)/"safe-unique-name.bin";src.write_bytes(b"x"*1048577)
            out=Path(temp)/"evo.jsonl";summary=Path(temp)/"summary.json"
            args=[sys.executable,str(Path(m.__file__)),"--cycles","2","--output",str(out),"--summary",str(summary),"--sample-file",str(src)]
            done=subprocess.run(args,capture_output=True,text=True)
            self.assertEqual(done.returncode,0,done.stderr)
            record=json.loads(summary.read_text())
            self.assertEqual(record["real_file_readproof"]["bytes_read"],1048577)
            self.assertNotIn("safe-unique-name",summary.read_text())
            self.assertFalse(record["real_file_readproof"]["path_disclosed"])

    def test_cli_no_clobber(self):
        with tempfile.TemporaryDirectory() as t:
            out,summary=Path(t)/'evo.jsonl',Path(t)/'summary.json'
            args=[sys.executable,str(Path(m.__file__)), '--cycles','3','--output',str(out),'--summary',str(summary)]
            first=subprocess.run(args,capture_output=True,text=True)
            self.assertEqual(first.returncode,0,first.stderr)
            rows=[json.loads(v) for v in out.read_text().splitlines()]
            self.assertEqual([x['status'] for x in rows],['PASS']*3)
            before=(out.read_bytes(),summary.read_bytes())
            second=subprocess.run(args,capture_output=True,text=True)
            self.assertNotEqual(second.returncode,0)
            self.assertEqual(before,(out.read_bytes(),summary.read_bytes()))


if __name__=='__main__': unittest.main()
