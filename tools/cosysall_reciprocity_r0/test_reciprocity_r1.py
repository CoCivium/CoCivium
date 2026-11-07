import copy
import unittest
from reciprocity import Held
from reciprocity_r1 import graph_digest, projection_triplet, bounded_feedback
from test_reciprocity import GRAPH

class CrossSurface(unittest.TestCase):
 def setUp(self):
  self.g=copy.deepcopy(GRAPH);self.sha=graph_digest(self.g)
  self.args=(self.g,self.sha,'repo:CoCivium/MasterPlan','domain:CoStrategy+','repo:CoCivium/CoCivium',['e1','e2'],'cv:1','2026-11-07T03:00:54Z',{'reason':'Candidate source path appears confusing for readers','observation_scope':'LOCAL_FIXTURE'})
 def test_parity(self):
  x=projection_triplet(self.g,'domain:CoStrategy+',self.sha)
  v=x['views'];self.assertEqual(v['visual_manifest']['claims_sha256'],v['machine']['claims_sha256'])
  self.assertEqual(v['machine']['claims_sha256'],v['accessible_list']['claims_sha256'])
  self.assertTrue(v['accessible_list']['items'])
  self.assertTrue(all(not k['effect_authority'] for k in (v['machine']['claims'],v['visual_manifest']['claims'])))
 def test_source_direction_is_preserved(self):
  x=projection_triplet(self.g,'domain:CoStrategy+',self.sha)
  e=x['views']['machine']['claims']['edges']
  self.assertEqual([(r['id'],r['from'],r['to']) for r in e],[('e1','domain:CoStrategy+','repo:CoCivium/MasterPlan'),('e2','domain:CoStrategy+','repo:CoCivium/CoCivium')])
 def test_valid_candidate_is_not_authority(self):
  d=bounded_feedback(*self.args)
  self.assertEqual((d['mutation_class'],d['epistemic_class'],d['authority_ceiling']),('PROPOSE','HYPOTHESIS','NO_EXTERNAL_EFFECTS__REVIEW_ONLY'))
  self.assertIn('CANDIDATE_SHARED_NEIGHBOR',d['relation'])
  self.assertIn('e1:domain:CoStrategy+->repo:CoCivium/MasterPlan',d['tests'][0])
 def test_forged_edge_orientation_rejected_by_pin(self):
  g=copy.deepcopy(self.g);g['edges'][0]['from'],g['edges'][0]['to']=g['edges'][0]['to'],g['edges'][0]['from']
  with self.assertRaises(Held):bounded_feedback(g,*self.args[1:])
 def test_tampered_claim_rejected(self):
  g=copy.deepcopy(self.g);g['edges'][0]['relation']='GRANTS_AUTHORITY'
  with self.assertRaises(Held):projection_triplet(g,'domain:CoStrategy+',self.sha)
 def test_fake_extra_authority_rejected(self):
  args=list(self.args);args[-1]={**args[-1], 'mutation_class':'EFFECT_GATED'}
  with self.assertRaises(Held):bounded_feedback(*args)
 def test_explicitly_claimed_receiver_ack_rejected(self):
  args=list(self.args);args[-1]={**args[-1], 'receiver_ack':True}
  with self.assertRaises(Held):bounded_feedback(*args)
 def test_candidate_edge_cannot_authorize(self):
  g=copy.deepcopy(self.g);g['edges'][1]['state']='CANDIDATE';args=list(self.args);args[0]=g;args[1]=graph_digest(g)
  with self.assertRaises(Held):bounded_feedback(*args)
 def test_private_endpoint_rejected(self):
  g=copy.deepcopy(self.g);g['nodes'][1]['privacy']='PRIVATE';args=list(self.args);args[0]=g;args[1]=graph_digest(g)
  with self.assertRaises(Held):bounded_feedback(*args)
 def test_private_neighbor_not_in_views(self):
  g=copy.deepcopy(self.g);g['nodes'][1]['privacy']='PRIVATE';x=projection_triplet(g,'domain:CoStrategy+',graph_digest(g))
  self.assertEqual([e['id'] for e in x['views']['machine']['claims']['edges']],['e2'])
 def test_no_render_no_payload(self):
  x=projection_triplet(self.g,'domain:CoStrategy+',self.sha);self.assertEqual(x['views']['none']['edges'],[])
  self.assertEqual(x['views']['none']['draw_requests'],0)
 def test_zero_budget(self):
  x=projection_triplet(self.g,'domain:CoStrategy+',self.sha,limit=0)
  for k in ('visual_manifest','accessible_list','machine'):
   self.assertEqual(x['views'][k]['claims']['edges'],[])
 def test_invalid_hash(self):
  with self.assertRaises(Held):projection_triplet(self.g,'domain:CoStrategy+','abc')
 def test_untrusted_time(self):
  args=list(self.args);args[7]='2026-11-07'
  with self.assertRaises(Held):bounded_feedback(*args)
 def test_bad_path(self):
  args=list(self.args);args[2],args[3]=args[3],args[2]
  with self.assertRaises(Held):bounded_feedback(*args)
 def test_directional_claim_not_promoted(self):
  d=bounded_feedback(*self.args)
  self.assertNotIn('PATH_TO:',d['relation'])
  self.assertIn('not a directed path',d['contradictions'][0])

if __name__=='__main__':unittest.main()