import copy
import json
import unittest
from pathlib import Path
from touch_impact import propose

FIX = json.loads((Path(__file__).parent / "fixture.json").read_text())

class ImpactTests(unittest.TestCase):
    def test_expected_causal_impact(self):
        v = propose(FIX)
        self.assertEqual([(x['receiver'], x['subject']) for x in v['proposals']], [('co-private','memo:private'), ('co-proof','test:replay'), ('co-ux','view:map'), ('co-ux','view:text')])
    def test_only_2_hops(self):
        self.assertEqual(propose(FIX)['visited_count'], 5)
    def test_proposed_edge_not_wake(self):
        self.assertTrue(propose(FIX)['gates']['ungrounded_edges'] >= 1)
    def test_inspiration_not_wake(self):
        self.assertNotIn('prior:synthkind',str(propose(FIX)['proposals']))
    def test_inspiration_candidate_is_review_not_wake(self):
        v = propose(FIX)
        self.assertIn({'subject':'candidate:visual-look','relation':'INSPIRED_BY','state':'REVIEW_CANDIDATE_NOT_WAKE'},v['review_only'])
        self.assertNotIn('candidate:visual-look',str(v['proposals']))
    def test_counterexample_is_review_not_wake(self):
        v = propose(FIX)
        self.assertIn({'subject':'candidate:critic','relation':'CONTRADICTS','state':'REVIEW_CANDIDATE_NOT_WAKE'},v['review_only'])
    def test_private_inspiration_is_not_in_public_review(self):
        self.assertNotIn('prior:synthkind',str(propose(FIX)['review_only']))
    def test_hypothetical_inspiration_not_presented_as_grounded(self):
        f=copy.deepcopy(FIX)
        for edge in f['edges']:
            if edge['dependent']=='candidate:visual-look':edge['evidence']='PROPOSED'
        self.assertNotIn('candidate:visual-look',str(propose(f)['review_only']))
    def test_review_limit_truncation(self):
        f=copy.deepcopy(FIX); f['limits']['max_review']=1
        self.assertEqual(propose(f)['status'],'TRUNCATED_HELD')
        self.assertEqual(len(propose(f)['review_only']),1)
    def test_private_not_public(self):
        v=propose(FIX)
        self.assertNotIn('memo:private',str([p for p in v['proposals'] if p['receiver']=='co-public']))
    def test_full_private_receives_private(self):
        self.assertIn('memo:private',str(propose(FIX)['proposals']))
    def test_no_worker_or_remote_effects(self):
        self.assertTrue(all(v == 0 for v in propose(FIX)['effects'].values()))
    def test_deterministic_replay(self):
        self.assertEqual(propose(FIX),propose(FIX))
    def test_edge_order_irrelevant(self):
        f=copy.deepcopy(FIX); f['edges'].reverse()
        self.assertEqual(propose(f)['proposals'],propose(FIX)['proposals'])
    def test_duplicate_edge_ignored(self):
        f=copy.deepcopy(FIX); f['edges'].append(copy.deepcopy(f['edges'][0]))
        self.assertEqual(propose(f)['proposals'],propose(FIX)['proposals'])
    def test_ack_suppresses_repeat(self):
        f=copy.deepcopy(FIX); f['receivers'][0]['last_acked_event_id']=f['change']['event_id']
        self.assertFalse(any(x['receiver']=='co-ux' for x in propose(f)['proposals']))
    def test_hypothesis_suppresses_wakes(self):
        f=copy.deepcopy(FIX); f['change']['evidence']='HYPOTHESIS'
        self.assertEqual(propose(f)['proposals'],[])
        self.assertEqual(propose(f)['status'],'HYPOTHESIS_ONLY_HELD')
    def test_zero_hops(self):
        f=copy.deepcopy(FIX); f['limits']['max_hops']=0
        self.assertEqual(propose(f)['proposals'],[])
    def test_low_visit_budget_reports_truncation(self):
        f=copy.deepcopy(FIX); f['limits']['max_visits']=1
        self.assertEqual(propose(f)['status'],'TRUNCATED_HELD')
    def test_low_proposal_budget_reports_truncation(self):
        f=copy.deepcopy(FIX); f['limits']['max_proposals']=1
        self.assertEqual(len(propose(f)['proposals']),1)
        self.assertEqual(propose(f)['status'],'TRUNCATED_HELD')
    def test_receiver_budget_zero(self):
        f=copy.deepcopy(FIX); f['receivers'][0]['max_items']=0
        self.assertFalse(any(x['receiver']=='co-ux' for x in propose(f)['proposals']))
    def test_bad_schema_fails_closed(self):
        f=copy.deepcopy(FIX); f['schema']='other'
        with self.assertRaises(ValueError): propose(f)
    def test_bad_revision_fails(self):
        f=copy.deepcopy(FIX); f['change']['revision_sha256']='unknown'
        with self.assertRaises(ValueError): propose(f)
    def test_invalid_receiver_clearance_fails(self):
        f=copy.deepcopy(FIX); f['receivers'][0]['clearance']='ALL'
        with self.assertRaises(ValueError): propose(f)
    def test_unknown_relation_fails(self):
        f=copy.deepcopy(FIX); f['edges'][0]['relation']='MAGICAL_AUTOWAKE'
        with self.assertRaises(ValueError): propose(f)
    def test_unknown_endpoint_fails(self):
        f=copy.deepcopy(FIX); f['edges'][0]['dependency']='none'
        with self.assertRaises(ValueError): propose(f)
    def test_cycle_cannot_loop(self):
        f=copy.deepcopy(FIX)
        f['edges'].append(dict(dependent='source:colens',dependency='view:map',relation='DEPENDS_ON',evidence='GROUNDED'))
        self.assertLessEqual(propose(f)['visited_count'],len(f['nodes']))
    def test_private_origin_never_public(self):
        f=copy.deepcopy(FIX)
        f['change']['subject']='memo:private'
        f['edges'].append(dict(dependent='page:frontdoor',dependency='memo:private',relation='DEPENDS_ON',evidence='GROUNDED'))
        v=propose(f)
        self.assertFalse(any(p['receiver']=='co-public' for p in v['proposals']))
        self.assertEqual(v['gates']['privacy_barrier_edges'],1)
    def test_privacy_crossing_cannot_leak_indirectly(self):
        f=copy.deepcopy(FIX)
        f['change']['subject']='prior:synthkind'
        f['edges'].append(dict(dependent='view:map',dependency='prior:synthkind',relation='DEPENDS_ON',evidence='GROUNDED'))
        self.assertEqual(propose(f)['proposals'],[])
    def test_unknown_receiver_target_fails(self):
        f=copy.deepcopy(FIX); f['receivers'][0]['targets']=['fake']
        with self.assertRaises(ValueError): propose(f)
    def test_unknown_key_fails(self):
        f=copy.deepcopy(FIX); f['change']['auto_execute']=True
        with self.assertRaises(ValueError): propose(f)
    def test_no_receiver_targets_no_promotion(self):
        f=copy.deepcopy(FIX)
        for r in f['receivers']:r['targets']=[]
        self.assertEqual(propose(f)['proposals'],[])
    def test_no_subscriptions_no_promotion(self):
        f=copy.deepcopy(FIX); f['receivers']=[]
        self.assertEqual(propose(f)['proposals'],[])
    def test_classification_strict(self):
        f=copy.deepcopy(FIX); f['nodes'][0]['classification']='PUBLICISH'
        with self.assertRaises(ValueError): propose(f)
    def test_missing_node_fails(self):
        f=copy.deepcopy(FIX); f['nodes']=f['nodes'][1:]
        with self.assertRaises(ValueError): propose(f)

if __name__ == '__main__': unittest.main()

class BoundedFrontierTests(unittest.TestCase):
    def test_wide_frontier_explicit_truncation(self):
        f=copy.deepcopy(FIX)
        for i in range(150):
            sid=f'view:synthetic-{i:03d}'
            f['nodes'].append({'id':sid,'classification':'PUBLIC'})
            f['edges'].append({'dependent':sid,'dependency':'source:colens','relation':'DEPENDS_ON','evidence':'GROUNDED'})
        f['receivers'][1]['targets'].extend(f'view:synthetic-{i:03d}' for i in range(35))
        f['limits']['max_visits']=12
        v=propose(f)
        self.assertEqual(v['visited_count'],12)
        self.assertEqual(v['status'],'TRUNCATED_HELD')
        self.assertTrue(all(x == 0 for x in v['effects'].values()))
    def test_wrong_relation_never_makes_a_worker(self):
        f=copy.deepcopy(FIX)
        f['edges'][0]['relation']='SYMBOLIZES'
        r=propose(f)
        self.assertNotIn('view:map',str(r['proposals']))
        self.assertEqual(r['effects']['worker_starts'],0)
    def test_nonrelated_receiver_never_promoted(self):
        f=copy.deepcopy(FIX)
        f['receivers'].append({'id':'unrelated:viewer','clearance':'PUBLIC','mode':'WAKE_ONLY','targets':['page:frontdoor'],'last_acked_event_id':None,'max_items':1})
        r=propose(f)
        self.assertFalse(any(x['receiver']=='unrelated:viewer' for x in r['proposals']))
    def test_restricted_to_private_cannot_cascade(self):
        f=copy.deepcopy(FIX)
        f['nodes'].append({'id':'secret:origin','classification':'RESTRICTED'})
        f['edges'].append({'dependent':'memo:private','dependency':'secret:origin','relation':'DEPENDS_ON','evidence':'GROUNDED'})
        f['change']['subject']='secret:origin'
        r=propose(f)
        self.assertEqual(r['proposals'],[])
        self.assertTrue(r['gates']['privacy_barrier_edges']>=1)
