import json, copy, unittest, pathlib, re
from urllib.parse import urlparse
M=json.loads((pathlib.Path(__file__).parent/'manifest-r0.json').read_text())
ALLOWED='https://github.com/CoCivium/CoCivium/blob/main/'

def validate(m):
    if m.get('state')!='PUBLIC_READ_ONLY_CANDIDATE_NOT_GLOBAL_ADOPTION': return False
    if m.get('authorized_effects_from_this_manifest')!=[]: return False
    if m.get('content_use',{}).get('training')!='NOT_GRANTED_BY_THIS_MANIFEST': return False
    if m.get('content_use',{}).get('fine_tuning')!='NOT_GRANTED_BY_THIS_MANIFEST': return False
    if m.get('content_use',{}).get('redistribution')!='CHECK_PER_WORK_LICENSE_AND_RIGHTS': return False
    if m.get('agent_interface',{}).get('endpoint_urls')!=[]: return False
    if m.get('agent_interface',{}).get('a2a_agent_card')!='NOT_DEPLOYED': return False
    if m.get('agent_interface',{}).get('mcp_resources')!='NOT_DEPLOYED': return False
    if m.get('default_verified_receiver_ladder')!='DISCOVERABLE_SOURCE_ONLY_NOT_REMOTE_RECEIVER_PICKUP': return False
    sources=m.get('source_index',[])
    if not sources or m.get('source_paths_count')!=len(sources): return False
    if len({s.get('path') for s in sources})!=len(sources): return False
    for s in sources:
        if not (s.get('url','').startswith(ALLOWED) and s['url']==ALLOWED+s['path']): return False
        if s['path'].startswith('/') or '..' in s['path'].split('/'): return False
        if not re.fullmatch('[0-9a-f]{40}', s.get('git_blob_sha1','')): return False
        if any(q in s['url'].lower() for q in ('token=','/private/','password')): return False
        if not s.get('source_state') or not s.get('description'): return False
    return True
class AdoptionTests(unittest.TestCase):
    def test_clean(self): self.assertTrue(validate(M))
    def test_exact_source_count(self): self.assertEqual(len(M['source_index']),7)
    def test_training_not_granted(self):
        d=copy.deepcopy(M);d['content_use']['training']='GRANTED';self.assertFalse(validate(d))
    def test_fine_tune_not_granted(self):
        d=copy.deepcopy(M);d['content_use']['fine_tuning']='GRANTED';self.assertFalse(validate(d))
    def test_redistribution_not_granted(self):
        d=copy.deepcopy(M);d['content_use']['redistribution']='ANY';self.assertFalse(validate(d))
    def test_external_authority(self):
        d=copy.deepcopy(M);d['authorized_effects_from_this_manifest']=['send'];self.assertFalse(validate(d))
    def test_fake_mcp(self):
        d=copy.deepcopy(M);d['agent_interface']['mcp_resources']='DEPLOYED';self.assertFalse(validate(d))
    def test_fake_a2a(self):
        d=copy.deepcopy(M);d['agent_interface']['a2a_agent_card']='DEPLOYED';self.assertFalse(validate(d))
    def test_fake_endpoint(self):
        d=copy.deepcopy(M);d['agent_interface']['endpoint_urls']=['https://example.com'];self.assertFalse(validate(d))
    def test_fake_receiver_ack(self):
        d=copy.deepcopy(M);d['default_verified_receiver_ladder']='INTEGRATED_IN_RECEIVER';self.assertFalse(validate(d))
    def test_source_path_escape(self):
        d=copy.deepcopy(M);d['source_index'][0]['path']='../../secret';self.assertFalse(validate(d))
    def test_source_spoof(self):
        d=copy.deepcopy(M);d['source_index'][0]['url']='https://attacker.example/x';self.assertFalse(validate(d))
    def test_source_tamper_blob(self):
        d=copy.deepcopy(M);d['source_index'][0]['git_blob_sha1']='bogus';self.assertFalse(validate(d))
    def test_missing_source_duplicated(self):
        d=copy.deepcopy(M);d['source_index'].append(copy.deepcopy(d['source_index'][0]));d['source_paths_count']=8;self.assertFalse(validate(d))
    def test_missing_source_count(self):
        d=copy.deepcopy(M);d['source_paths_count']=10;self.assertFalse(validate(d))
if __name__=='__main__': unittest.main()
