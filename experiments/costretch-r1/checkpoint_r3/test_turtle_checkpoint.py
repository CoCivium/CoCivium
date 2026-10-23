"""Fail-closed, offline CoStretch R3 reproducibility suite."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import turtle_checkpoint as t

HERE = Path(__file__).resolve().parent
SPACE, BASE_HASH = t.load_space(HERE / 'space_manifest.json')


class CheckpointTests(unittest.TestCase):
    def cp(self, index=0):
        return t.make_checkpoint(SPACE, BASE_HASH, next_index=index)

    def test_capacity_exact_unchanged(self):
        self.assertEqual(t.capacity(SPACE), 50_164_531_200_000)

    def test_manifest_content_identity(self):
        self.assertEqual(BASE_HASH, hashlib.sha256((HERE/'space_manifest.json').read_bytes()).hexdigest())

    def test_checkpoint_verifies(self):
        self.assertEqual(t.validate_checkpoint(SPACE, BASE_HASH, self.cp())['revision'], 0)

    def test_r1_bare_index_drift_reproduced(self):
        altered = copy.deepcopy(SPACE)
        altered['dimensions'][0]['options'][:2] = altered['dimensions'][0]['options'][1::-1]
        self.assertEqual(t.capacity(altered), t.capacity(SPACE))
        self.assertNotEqual(t.unrank(SPACE, 0), t.unrank(altered, 0))

    def test_r3_guards_same_cardinality_drift(self):
        altered = copy.deepcopy(SPACE)
        altered['dimensions'][0]['options'][:2] = altered['dimensions'][0]['options'][1::-1]
        with tempfile.TemporaryDirectory() as directory:
            modified = Path(directory)/'changed.json'
            modified.write_text(json.dumps(altered, indent=2)+'\n',encoding='utf-8')
            changed_space, changed_hash = t.load_space(modified)
            self.assertEqual(t.capacity(changed_space), t.capacity(SPACE))
            with self.assertRaisesRegex(ValueError, 'SPEC_NAMESPACE_CHANGED'):
                t.validate_checkpoint(changed_space, changed_hash, self.cp())

    def test_label_replace_same_size_rejected(self):
        altered = copy.deepcopy(SPACE)
        altered['dimensions'][0]['options'][0] = 'investigator-morphed'
        with tempfile.TemporaryDirectory() as directory:
            f = Path(directory)/'changed.json'
            f.write_text(json.dumps(altered),encoding='utf-8')
            s, h = t.load_space(f)
            with self.assertRaisesRegex(ValueError, 'SPEC_NAMESPACE_CHANGED'):
                t.validate_checkpoint(s, h, self.cp())

    def test_manifest_whitespace_change_conservatively_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            f = Path(directory)/'changed.json'
            f.write_bytes((HERE/'space_manifest.json').read_bytes() + b' ')
            s, h = t.load_space(f)
            with self.assertRaisesRegex(ValueError, 'SPEC_NAMESPACE_CHANGED'):
                t.validate_checkpoint(s, h, self.cp())

    def test_advance_bounded_and_lineaged(self):
        cp = self.cp()
        nxt, records = t.advance(SPACE, BASE_HASH, cp, count=5)
        self.assertEqual(len(records), 5)
        self.assertEqual(nxt['revision'], 1)
        self.assertEqual(nxt['next_index'], 5)
        self.assertEqual(nxt['parent_checkpoint_sha256'], cp['checkpoint_sha256'])
        self.assertEqual(t.validate_checkpoint(SPACE, BASE_HASH, nxt), nxt)
        self.assertTrue(all(r['status'] == 'DESCRIBED_NOT_EXECUTED' for r in records))

    def test_no_exec_count_always_zero(self):
        nxt, _ = t.advance(SPACE, BASE_HASH, self.cp(), count=2)
        self.assertEqual(nxt['actual_executed_experiments'],0)
        self.assertEqual(nxt['actual_live_sessions'],0)

    def test_disallowed_effect_has_hold(self):
        point = t.unrank(SPACE, 0)
        point.update(effect='EXTERNAL_ACTION')
        self.assertIn('EXTERNAL_EFFECT_NOT_ALLOWED',t.disclosure(point))

    def test_unknown_authority_has_hold(self):
        point = t.unrank(SPACE, 0)
        point.update(authority='UNKNOWN')
        self.assertIn('MISSING_AUTHORITY', t.disclosure(point))

    def test_nonpublic_has_hold(self):
        point = t.unrank(SPACE, 0)
        point.update(confidentiality='PRIVATE')
        self.assertIn('NONPUBLIC_UNVERIFIED', t.disclosure(point))

    def test_provider_substrate_has_hold(self):
        point = t.unrank(SPACE, 0)
        point.update(substrate='claude-hosted')
        self.assertIn('NONDETERMINISTIC_OR_PROVIDER_SUBSTRATE_UNVERIFIED', t.disclosure(point))

    def test_exhausted_space_does_not_emit_zombie_checkpoint(self):
        cp=self.cp(index=t.capacity(SPACE))
        with self.assertRaisesRegex(ValueError,'SPACE_EXHAUSTED_NO_ADVANCE'):
            t.advance(SPACE,BASE_HASH,cp,1)

    def test_boolean_false_is_not_accepted_as_execution_counter(self):
        cp=self.cp(); cp['actual_live_sessions']=False
        cp['checkpoint_sha256']=t.digest(t.canonical({k:v for k,v in cp.items() if k!='checkpoint_sha256'}))
        with self.assertRaisesRegex(ValueError,'FALSE_EXECUTION_STATUS'):
            t.validate_checkpoint(SPACE,BASE_HASH,cp)

    def test_corrupt_cursor_detected(self):
        cp=self.cp(); cp['next_index']=100
        with self.assertRaisesRegex(ValueError,'CHECKPOINT_TAMPERED'):
            t.validate_checkpoint(SPACE,BASE_HASH,cp)

    def test_corrupt_effect_policy_detected(self):
        cp=self.cp(); cp['effect_ceiling']='EXTERNAL_ACTION'
        cp['checkpoint_sha256']=t.digest(t.canonical({k:v for k,v in cp.items() if k!='checkpoint_sha256'}))
        with self.assertRaisesRegex(ValueError,'EFFECT_POLICY_CHANGED'):
            t.validate_checkpoint(SPACE,BASE_HASH,cp)

    def test_forged_execution_status_detected(self):
        cp=self.cp(); cp['actual_executed_experiments']=1
        cp['checkpoint_sha256']=t.digest(t.canonical({k:v for k,v in cp.items() if k!='checkpoint_sha256'}))
        with self.assertRaisesRegex(ValueError,'FALSE_EXECUTION_STATUS'):
            t.validate_checkpoint(SPACE,BASE_HASH,cp)

    def test_extra_checkpoint_field_rejected(self):
        cp=self.cp(); cp['secret_extra']='oops'
        with self.assertRaisesRegex(ValueError,'CHECKPOINT_SCHEMA_MISMATCH'):
            t.validate_checkpoint(SPACE,BASE_HASH,cp)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaisesRegex(ValueError,'DUPLICATE_JSON_KEY'):
            t.strict_json(b'{"role":1,"role":2}')

    def test_out_of_range_and_bool(self):
        for value in (-1,True,False,t.capacity(SPACE),3.4):
            with self.subTest(value=value), self.assertRaises(ValueError):
                t.unrank(SPACE,value)

    def test_rank_roundtrip_mixed_sample(self):
        cap=t.capacity(SPACE)
        for i in [0,1,100,cap//2,cap-1]:
            self.assertEqual(t.rank(SPACE,t.unrank(SPACE,i)),i)

    def test_bounded_peek(self):
        with self.assertRaisesRegex(ValueError,'INVALID_PEEK_COUNT'):
            t.peek(SPACE,self.cp(),1000)
        with self.assertRaisesRegex(ValueError,'INVALID_PEEK_COUNT'):
            t.peek(SPACE,self.cp(),True)

    def test_no_clobber_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'cp.json'
            t.exclusive_json(output,self.cp())
            before=output.read_bytes()
            with self.assertRaises(FileExistsError):
                t.exclusive_json(output,self.cp())
            self.assertEqual(output.read_bytes(),before)

    def test_cli_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            a=Path(directory)/'original.json'
            b=Path(directory)/'successor.json'
            cmd=[sys.executable,str(HERE/'turtle_checkpoint.py')]
            def run(*options):
                return subprocess.run(cmd+list(options),capture_output=True,text=True,check=True)
            run('init','--space',str(HERE/'space_manifest.json'),'--out',str(a))
            r=run('verify','--space',str(HERE/'space_manifest.json'),'--checkpoint',str(a))
            self.assertEqual(json.loads(r.stdout)['result'],'PASS_NAMESPACE_AND_CHECKPOINT')
            p=run('peek','--space',str(HERE/'space_manifest.json'),'--checkpoint',str(a),'--count','2')
            self.assertEqual(len(json.loads(p.stdout)['descriptions']),2)
            run('advance','--space',str(HERE/'space_manifest.json'),'--checkpoint',str(a),'--count','2','--out',str(b))
            q=run('verify','--space',str(HERE/'space_manifest.json'),'--checkpoint',str(b))
            self.assertEqual(json.loads(q.stdout)['next_index'],2)
            self.assertEqual(t.load_checkpoint(a)['next_index'],0)


if __name__=='__main__':
    unittest.main()