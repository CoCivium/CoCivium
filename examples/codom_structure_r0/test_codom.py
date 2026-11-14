import copy
import importlib.util
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).parent
spec=importlib.util.spec_from_file_location('codom',ROOT/'CoDOMStructureR0.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
DATA=json.loads((ROOT/'fixture.json').read_text())['snapshots']
class CoDOMTests(unittest.TestCase):
 def test_count(self):self.assertEqual(len(m.mine(DATA[0])['relations']),4)
 def test_semantic_parity(self):self.assertEqual(m.mine(DATA[1])['relations_sha256'],m.mine(DATA[2])['relations_sha256'])
 def test_delta(self):self.assertEqual(m.delta(m.mine(DATA[0]),m.mine(DATA[1]))['changed'],['b-next'])
 def test_hidden_excluded(self):self.assertNotIn('b-hidden',str(m.mine(DATA[0])))
 def test_no_secret(self):self.assertNotIn('SENSITIVE_CANARY',str(m.mine(DATA[2])))
 def test_no_url(self):self.assertNotIn('example.invalid',str(m.mine(DATA[0])))
 def test_unknown(self):self.assertEqual(m.mine(DATA[0])['currentness'],'UNKNOWN')
 def test_no_effects(self):self.assertTrue(all(v==0 for v in m.mine(DATA[1])['effects'].values()))
 def test_hold_authority(self):
  x=copy.deepcopy(DATA[0]);x['observer_scope']['authority']='EXECUTE'
  with self.assertRaisesRegex(ValueError,'SCOPE'):m.mine(x)
 def test_hold_private(self):
  x=copy.deepcopy(DATA[0]);x['observer_scope']['privacy']='PRIVATE'
  with self.assertRaisesRegex(ValueError,'SCOPE'):m.mine(x)
 def test_hold_adapter(self):
  x=copy.deepcopy(DATA[0]);x['kind']='LIVE_CHROME'
  with self.assertRaisesRegex(ValueError,'ADAPTER'):m.mine(x)
 def test_hold_extra_fields(self):
  x=copy.deepcopy(DATA[0]);x['credential']='forbidden'
  with self.assertRaisesRegex(ValueError,'SCHEMA'):m.mine(x)
 def test_hold_dupes(self):
  x=copy.deepcopy(DATA[2]);x['payload'].append({'id':'h-main','role':'heading','name':'Another'})
  with self.assertRaisesRegex(ValueError,'DUPLICATES'):m.mine(x)
 def test_hold_delta_across_work(self):
  x=copy.deepcopy(DATA[1]);x['work_id']='unrelated'
  with self.assertRaisesRegex(ValueError,'UNBOUND'):m.delta(m.mine(DATA[0]),m.mine(x))
 def test_script_excluded(self):
  x=copy.deepcopy(DATA[0]);x['payload']="<main><script>PRIVATE_PASSWORD</script><h1 data-coid='safe'>Public</h1></main>"
  self.assertEqual(m.mine(x)['relations'],[{'id':'safe','role':'heading','name':'Public'}])
 def test_hidden_aria(self):
  x=copy.deepcopy(DATA[0]);x['payload']="<main aria-hidden='true'><h1 data-coid='ghost'>Private</h1></main>"
  self.assertEqual(m.mine(x)['relations'],[])
 def test_oversize(self):
  x=copy.deepcopy(DATA[0]);x['payload']='z'*50001
  with self.assertRaisesRegex(ValueError,'SIZE'):m.mine(x)
 def test_broken_html(self):
  x=copy.deepcopy(DATA[0]);x['payload']="<main><h1 data-coid='h'>Broken</main>"
  with self.assertRaisesRegex(ValueError,'BAD_HTML'):m.mine(x)
 def test_native_extra_fields(self):
  x=copy.deepcopy(DATA[2]);x['payload'][0]['send']=True
  with self.assertRaisesRegex(ValueError,'NATIVE_FIELDS'):m.mine(x)
 def test_null_ne_absent(self):self.assertTrue(m.delta(m.mine(DATA[0]),m.mine(DATA[1]))['not_observed_ne_absent'])
 def test_no_truth_promotion(self):self.assertEqual(m.mine(DATA[2])['evidence'],'SNAPSHOT_STRUCTURE_ONLY')
if __name__=='__main__':unittest.main()
