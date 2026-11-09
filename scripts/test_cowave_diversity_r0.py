"""CoWave novelty is a bounded selector, not proof of autonomous sessions."""
from __future__ import annotations
from dataclasses import replace
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from CoWaveDiversityR0 import choose, distance, axes_for, PROFILES

STAMP = '2026-11-09T21:23:40Z'

def fixture():
    return {"schema":"cocivium.frontier-index.r0", "fronts":[
        {"id":fid,"status":"proposed","next_gate":"Verify a source-bound useful receiver effect"}
        for fid in PROFILES]}

class Tests(unittest.TestCase):
    def test_four_waves_have_meaningfully_different_axes(self):
        plan=choose(fixture(), STAMP, limit=4)
        self.assertEqual(len(plan['proposals']),4)
        for a,b in zip(plan['proposals'],plan['proposals'][1:]):
            self.assertGreaterEqual(distance(a['axes'],b['axes']),3)
            self.assertNotEqual(a['front_id'],b['front_id'])
        self.assertEqual(plan['effects_performed'],0)
        self.assertEqual(plan['sessions_drained'],0)

    def test_all_known_fronts_never_silently_dropped(self):
        plan=choose(fixture(),STAMP,limit=len(PROFILES))
        self.assertEqual(set(PROFILES),set(plan['held_fronts'])|{p['front_id'] for p in plan['proposals']})
        self.assertEqual(len(plan['proposals'])+len(plan['held_fronts']),len(PROFILES))

    def test_replay_is_stable_not_falsely_novel(self):
        self.assertEqual(choose(fixture(),STAMP),choose(fixture(),STAMP))

    def test_source_change_moves_source_hash(self):
        obj=fixture();original=choose(obj,STAMP)
        obj['fronts'][0]['next_gate']='Changed recovery test'
        self.assertNotEqual(original['source_sha256'],choose(obj,STAMP)['source_sha256'])

    def test_new_front_preserved_without_profile_claim(self):
        obj=fixture();obj['fronts'].append({'id':'newly-observed-front','status':'proposed','next_gate':'Investigate'})
        plan=choose(obj,STAMP)
        self.assertIn('newly-observed-front',plan['unknown_profile_fronts'])
        self.assertIn('newly-observed-front',plan['held_fronts'])

    def test_new_public_front_profiles_remain_eligible(self):
        newer={'comap-megascroller','colue-outreach','colensmedia-lineage','cobrowser-cocarry'}
        self.assertTrue(newer.issubset(PROFILES))
        plan=choose(fixture(),STAMP,limit=len(PROFILES))
        self.assertTrue(newer.issubset({p['front_id'] for p in plan['proposals']}))

    def test_no_candidate_is_executed_just_by_election(self):
        for proposal in choose(fixture(),STAMP)['proposals']:
            self.assertIsNone(proposal['independent_readproof'])
            self.assertEqual(proposal['external_effect'],'NONE')

    def test_unverified_readproof_in_history_rejected(self):
        p=choose(fixture(),STAMP)['proposals'][0]
        with self.assertRaisesRegex(ValueError,'HOLD_EXTERNAL_READPROOF_UNSUPPORTED'):
            choose(fixture(),STAMP,prior=[{**p,'state':'RECEIVER_EFFECT_VERIFIED'}])

    def test_forged_readproof_string_is_not_accepted(self):
        p=choose(fixture(),STAMP)['proposals'][0]
        with self.assertRaisesRegex(ValueError,'HOLD_EXTERNAL_READPROOF_UNSUPPORTED'):
            choose(fixture(),STAMP,prior=[{**p,'state':'RECEIVER_EFFECT_VERIFIED',
                                        'independent_readproof':'fake:yes'}])

    def test_proposed_history_not_replayed(self):
        first=choose(fixture(),STAMP,limit=1)['proposals'][0]
        later=choose(fixture(),STAMP,limit=1,prior=[first])
        self.assertNotEqual(first['front_id'],later['proposals'][0]['front_id'])

    def test_bogus_axes_cannot_manufacture_difference(self):
        p=choose(fixture(),STAMP)['proposals'][0]
        with self.assertRaisesRegex(ValueError,'HOLD_UNBOUND_WAVE_AXES'):
            choose(fixture(),STAMP,prior=[{**p,'axes':{**p['axes'],'horizon':'invented'}}])

    def test_source_must_be_actual_frontier_schema(self):
        bad=fixture();bad['schema']='invented';
        with self.assertRaisesRegex(ValueError,'HOLD_SOURCE_FRONT_INDEX'):
            choose(bad,STAMP)

    def test_duplicate_front_or_missing_gate_rejected(self):
        bad=fixture();bad['fronts'].append(copy.deepcopy(bad['fronts'][0]));
        with self.assertRaisesRegex(ValueError,'HOLD_DUPLICATE_FRONT'):choose(bad,STAMP)
        bad=fixture();bad['fronts'][0]['next_gate']=''
        with self.assertRaisesRegex(ValueError,'HOLD_UNQUALIFIED_NEXT_GATE'):choose(bad,STAMP)

    def test_invalid_time_and_limit_rejected(self):
        for t in ('2026-11-09T21:23:40-05:00','2026-02-30T12:00:00Z','unknown'):
            with self.subTest(t=t),self.assertRaisesRegex(ValueError,'HOLD_OBSERVATION_TIME'):choose(fixture(),t)
        for n in (True,0,len(PROFILES)+1,-1):
            with self.subTest(n=n),self.assertRaisesRegex(ValueError,'HOLD_WAVE_LIMIT'):choose(fixture(),STAMP,limit=n)

    def test_empty_frontier_and_oversized_history_rejected(self):
        with self.assertRaisesRegex(ValueError,'HOLD_SOURCE_FRONT_SET'):choose({'schema':'cocivium.frontier-index.r0','fronts':[]},STAMP)
        with self.assertRaisesRegex(ValueError,'HOLD_PRIOR_WAVE_HISTORY'):choose(fixture(),STAMP,prior=[{}]*129)

    def test_all_previously_proposed_waves_quiesce(self):
        first=choose(fixture(),STAMP,limit=len(PROFILES))
        second=choose(fixture(),STAMP,limit=len(PROFILES),prior=first['proposals'])
        self.assertEqual(second['state'],'HOLD_NO_ADMISSIBLE_DISTINCT_WAVE')
        self.assertEqual(second['proposals'],[])
        self.assertEqual(len(second['held_fronts']),len(PROFILES))

    def test_read_only_cli_no_clobber(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'index.json';out=root/'one.json'
            source.write_text(json.dumps(fixture()))
            call=[sys.executable,str(Path(__file__).with_name('CoWaveDiversityR0.py')),
                  '--index',str(source),'--as-of',STAMP,'--output',str(out)]
            one=subprocess.run(call,capture_output=True,text=True,timeout=8)
            self.assertEqual(one.returncode,0,one.stderr)
            old=out.read_bytes()
            two=subprocess.run(call,capture_output=True,text=True,timeout=8)
            self.assertNotEqual(two.returncode,0)
            self.assertEqual(out.read_bytes(),old)

    def test_method_fingerprints_refuse_equivalence_by_text_only(self):
        p=choose(fixture(),STAMP,limit=1)['proposals'][0]
        self.assertIn('semantic_fingerprint_sha256',p)
        self.assertGreaterEqual(len(p['semantic_fingerprint_sha256']),64)
        self.assertEqual(p['axes'],axes_for(p['front_id']))

if __name__=='__main__':unittest.main(verbosity=2)
