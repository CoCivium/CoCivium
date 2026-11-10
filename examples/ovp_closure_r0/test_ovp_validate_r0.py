"""Source-only OVP closure adversarial fixtures. No host effect or external receiver."""
import copy
import json
import unittest
from pathlib import Path
from ovp_validate_r0 import evaluate

FIXTURE=Path(__file__).with_name('fixture_rickbar_x2_source_only.json')

class TestOVPContract(unittest.TestCase):
    def setUp(self):
        self.base=json.loads(FIXTURE.read_text(encoding='utf-8'))

    def run_bad(self, m, code):
        outcome=evaluate(m)
        self.assertEqual(outcome['closure_class'],'SOURCE_INCOMPLETE_HELD')
        self.assertIn(code,outcome['errors'])
        self.assertFalse(outcome['live_effect_authorized'])
        self.assertFalse(outcome['receiver_proof_verified'])

    def test_valid_source_closure_not_receiver(self):
        r=evaluate(self.base)
        self.assertEqual(r['closure_class'],'SOURCE_BOUND_CLOSURE')
        self.assertEqual(r['real_product_class'],'AWAITING_INDEPENDENT_RECEIVER_PROOF')
        self.assertEqual(len(r['required_roles_present']),8)
        self.assertFalse(r['live_effect_authorized'])
        self.assertFalse(r['receiver_proof_verified'])

    def test_missing_mandatory_role(self):
        self.base['nodes']=[x for x in self.base['nodes'] if x['role']!='permission']
        self.assertIn('MISSING_REQUIRED_ROLES:permission', evaluate(self.base)['errors'])

    def test_duplicate_identity_fails(self):
        self.base['nodes'].append(copy.deepcopy(self.base['nodes'][0]))
        self.run_bad(self.base,'DUPLICATE_NODE_ID')

    def test_version_mismatch_fails(self):
        self.base['nodes'][0]['depends_on'][0]['revision']='r9'
        self.run_bad(self.base,'INCOMPATIBLE_DEPENDENCY_REVISION')

    def test_missing_dependency_fails(self):
        self.base['nodes'][0]['depends_on'].append({'id':'ghost','revision':'r0'})
        self.run_bad(self.base,'MISSING_PINNED_DEPENDENCY')

    def test_critical_stale_fails(self):
        self.base['nodes'][0]['currentness']='STALE'
        self.run_bad(self.base,'REQUIRED_NODE_STALE_OR_UNKNOWN')

    def test_effect_authority_not_inferred(self):
        self.base['effect_request']='LOCAL_EXECUTION'
        self.run_bad(self.base,'EFFECT_REQUEST_NOT_PERMITTED_BY_SOURCE_VALIDATOR')

    def test_source_metadata_cannot_mint_authority(self):
        self.base['nodes'][0]['authority']='DEPLOY_GRANT'
        self.run_bad(self.base,'SOURCE_ATTEMPTS_AUTHORITY_ESCALATION')

    def test_native_exit_mandatory(self):
        self.base['native_escape_declared']=False
        self.run_bad(self.base,'NO_NATIVE_ESCAPE_CONTRACT')

    def test_text_fallback_mandatory(self):
        self.base['read_only_text_fallback']=False
        self.run_bad(self.base,'NO_READ_ONLY_TEXT_FALLBACK')

    def test_cycle_fails(self):
        permission=next(x for x in self.base['nodes'] if x['role']=='permission')
        permission['depends_on'].append({'id':'rickbar-input','revision':'r0'})
        self.run_bad(self.base,'DEPENDENCY_CYCLE')

    def test_required_role_disconnected(self):
        self.base['nodes'][0]['depends_on']=[d for d in self.base['nodes'][0]['depends_on'] if d['id']!='receiver-feedback']
        self.run_bad(self.base,'REQUIRED_ROLE_NOT_IN_ENTRY_CLOSURE:return')

    def test_optional_stale_degrades_with_fallback(self):
        self.base['nodes'][-1]['currentness']='STALE'
        r=evaluate(self.base)
        self.assertEqual(r['closure_class'],'SOURCE_DEGRADED_READ_ONLY')
        self.assertFalse(r['errors'])
        self.assertFalse(r['receiver_proof_verified'])

    def test_optional_stale_missing_fallback_blocks(self):
        self.base['nodes'][-1]['currentness']='STALE'
        self.base['nodes'][-1].pop('fallback')
        self.run_bad(self.base,'DEGRADED_NODE_WITHOUT_FALLBACK')

    def test_bad_digest_format_fails(self):
        self.base['nodes'][0]['source_digest']='sha256:pretend'
        self.run_bad(self.base,'INVALID_SHA256_FORMAT')

    def test_untrusted_receiver_ack_does_not_verify(self):
        self.base['receiver_evidence']='TRUST_ME_INDEPENDENT'
        r=evaluate(self.base)
        self.assertEqual(r['closure_class'],'SOURCE_BOUND_CLOSURE')
        self.assertIn('RECEIVER_ASSERTION_UNAUTHENTICATED',r['holds'])
        self.assertFalse(r['receiver_proof_verified'])

    def test_determinism_under_node_reorder(self):
        a=evaluate(self.base)
        self.base['nodes'].reverse()
        self.assertEqual(a,evaluate(self.base))

    def test_unknown_schema_fails(self):
        self.base['schema']='malicious'
        self.run_bad(self.base,'SCHEMA_INVALID')

if __name__=='__main__':
    unittest.main()
