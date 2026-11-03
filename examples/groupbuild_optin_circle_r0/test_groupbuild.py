import copy
import json
import unittest
from pathlib import Path
from groupbuild_club import propose,validate,canonical,sha
BASE=json.loads(Path(__file__).with_name('fixture.json').read_text(encoding='utf-8'))
class GroupBuildTests(unittest.TestCase):
    def test_shadow_ready_exactly_one(self):
        r=propose(BASE);self.assertEqual(1,r['ready_for_review']);self.assertEqual(0,r['sent'])
    def test_no_real_members(self):self.assertEqual(propose(BASE)['real_members'],0)
    def test_no_staffed_reviewers(self):self.assertEqual(propose(BASE)['staffed_reviewers'],0)
    def test_zero_effects(self):self.assertEqual(propose(BASE)['external_effects'],0)
    def test_determinism(self):self.assertEqual(canonical(propose(BASE)),canonical(propose(copy.deepcopy(BASE))))
    def test_suppressed_not_ready(self):
        r=propose(BASE);self.assertTrue(all(x['state']=='HELD' for x in r['pairs'] if 'test-cam' in x['member_ids']))
    def test_no_identity_disclosure(self):self.assertTrue(all(not x['identities_revealed'] for x in propose(BASE)['pairs']))
    def test_one_side_revoked(self):
        d=copy.deepcopy(BASE);d['members'][0]['intro_consents'][0]['revoked']=True
        self.assertEqual(0,propose(d)['ready_for_review'])
    def test_expiry(self):
        d=copy.deepcopy(BASE);d['members'][0]['intro_consents'][0]['expires_on']='2026-11-02'
        self.assertEqual(0,propose(d)['ready_for_review'])
    def test_a_club_opt_out(self):
        d=copy.deepcopy(BASE);d['members'][1]['club_opt_in']=False
        self.assertEqual(0,propose(d)['ready_for_review'])
    def test_no_project_topic(self):
        d=copy.deepcopy(BASE);d['members'][0]['topics']=['different-topic']
        self.assertEqual(0,propose(d)['ready_for_review'])
    def test_a_unilateral_intro(self):
        d=copy.deepcopy(BASE);d['members'][1]['intro_consents']=[]
        self.assertEqual(0,propose(d)['ready_for_review'])
    def test_suppression_override(self):
        d=copy.deepcopy(BASE);d['suppressions'].append('test-ada')
        self.assertEqual(0,propose(d)['ready_for_review'])
    def test_wrong_scope(self):
        d=copy.deepcopy(BASE);d['members'][0]['intro_consents'][0]['scope']='ALL_PRIVATE_DATA'
        with self.assertRaises(ValueError):validate(d)
    def test_invalid_real_member(self):
        d=copy.deepcopy(BASE);d['members'][0]['synthetic']=False
        with self.assertRaises(ValueError):validate(d)
    def test_cannot_claim_club_open(self):
        d=copy.deepcopy(BASE);d['circle']['status']='LIVE'
        with self.assertRaises(ValueError):validate(d)
    def test_no_private_fields(self):
        d=copy.deepcopy(BASE);d['members'][0]['email']='test@example.com'
        with self.assertRaises(ValueError):validate(d)
    def test_duplicate_member_id(self):
        d=copy.deepcopy(BASE);d['members'][0]['id']=d['members'][1]['id']
        with self.assertRaises(ValueError):validate(d)
    def test_nonexistent_intro_target(self):
        d=copy.deepcopy(BASE);d['members'][0]['intro_consents'][0]['partner_id']='test-unknown'
        with self.assertRaises(ValueError):validate(d)
    def test_bad_tag_rejected(self):
        d=copy.deepcopy(BASE);d['members'][0]['offers']=['someone@example.com']
        with self.assertRaises(ValueError):validate(d)
    def test_no_inference_from_one_way_help(self):
        d=copy.deepcopy(BASE);d['members'][1]['needs']=['unrelated']
        self.assertEqual(0,propose(d)['ready_for_review'])
    def test_minimal_receipt(self):
        r=propose(BASE);self.assertEqual(r['source_sha256'],sha(BASE));self.assertIn('MATCH_NE_INTRODUCTION',r['rails'])
if __name__=='__main__':unittest.main()
