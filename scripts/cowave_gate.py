"""CoWave R0: deterministic, dependency-free wave qualification. No live orchestration."""
import json
import sys
import unittest

REQUIRED = ('seed_id', 'orb_ref', 'gauge', 'thumb', 'observed_at', 'evidence')
TARGETS = ('sync', 'survival_24h', 'handoff')

def qualify(wave):
    problems = []
    for field in REQUIRED:
        if not wave.get(field):
            problems.append('missing:' + field)
    if not isinstance(wave.get('gauge'), dict) or not {'name', 'value', 'unit'} <= wave['gauge'].keys():
        problems.append('invalid:gauge')
    for target in TARGETS:
        claim = wave.get('targets', {}).get(target, {})
        if claim.get('state') == 'PASS' and not (claim.get('independent_receipt') and claim.get('source_sha')):
            problems.append('unsupported_PASS:' + target)
    if wave.get('placeholders', 0) != 0:
        problems.append('placeholders_nonzero')
    return {'qualified': not problems, 'problems': problems}

class Tests(unittest.TestCase):
    def setUp(self):
        self.wave = {'seed_id':'s1','orb_ref':'public:orb1','gauge':{'name':'latency','value':2,'unit':'s'},'thumb':'up','observed_at':'2026-11-09T00:00:00Z','evidence':['public:receipt1'],'placeholders':0,'targets':{'sync':{'state':'UNVERIFIED'},'survival_24h':{'state':'UNVERIFIED'},'handoff':{'state':'UNVERIFIED'}}}
    def test_baseline(self):
        self.assertTrue(qualify(self.wave)['qualified'])
    def test_false_pass(self):
        self.wave['targets']['sync']={'state':'PASS'}
        self.assertIn('unsupported_PASS:sync', qualify(self.wave)['problems'])
    def test_missing_orb(self):
        del self.wave['orb_ref']
        self.assertIn('missing:orb_ref', qualify(self.wave)['problems'])
    def test_placeholder(self):
        self.wave['placeholders']=1
        self.assertIn('placeholders_nonzero', qualify(self.wave)['problems'])
    def test_proof_is_scoped(self):
        self.wave['targets']['handoff']={'state':'PASS','independent_receipt':'public:receipt','source_sha':'abc'}
        self.assertTrue(qualify(self.wave)['qualified'])
        self.assertEqual(self.wave['targets']['sync']['state'],'UNVERIFIED')

if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--test':
        unittest.main(argv=[sys.argv[0]], verbosity=2)
    elif len(sys.argv)>1:
        print(json.dumps(qualify(json.load(open(sys.argv[1],encoding='utf-8'))), indent=2))
    else:
        print('Usage: python cowave_gate.py --test | wave.json')
