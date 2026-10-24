"""Synthetic stage-gate and negative/adversarial validation. No network or effects."""
import copy
import json
import unittest
from pathlib import Path
from gate import evaluate

BASE = json.loads((Path(__file__).parent / 'candidate.json').read_text(encoding='utf-8'))

class GateTests(unittest.TestCase):
    def setUp(self): self.r = copy.deepcopy(BASE)
    def status(self, expected): self.assertEqual(evaluate(self.r)['status'], expected)
    def hold(self, code): self.assertIn(code, evaluate(self.r)['hold'])
    def fail(self, code): self.assertIn(code, evaluate(self.r)['fail'])
    def test_candidate_design_declared_only(self): self.status('PASS_DECLARED_STRUCTURE_ONLY')
    def test_invalid_stage(self): self.r['stage']='AETHER'; self.fail('INVALID_STAGE')
    def test_invalid_risk(self): self.r['risk']='INFINITE'; self.fail('INVALID_RISK')
    def test_missing_exact_digest(self): self.r['source_sha256']='unknown'; self.fail('EXACT_SOURCE_IDENTITY_REQUIRED')
    def test_no_prior(self): self.r['priors']=[]; self.hold('PRIOR_EVIDENCE_UNBOUND')
    def test_false_prior(self): self.r['priors'][0]['source_ref']='X'; self.fail('MALFORMED_PRIOR')
    def test_no_falsifier(self): self.r['falsifier']=''; self.hold('FALSIFIER_NOT_DECLARED')
    def test_no_challenger(self): self.r['panel']=self.r['panel'][:1]; self.hold('MISSING_CHALLENGER')
    def test_duplicate_panel_identity(self): self.r['panel'][1]['reviewer_id']='fixture:proposer'; self.fail('DUPLICATE_REVIEWER_ID')
    def test_medium_requires_provenance(self): self.r['risk']='MEDIUM'; self.hold('MISSING_PROVENANCE_REVIEW')
    def test_high_requires_external_review(self): self.r['risk']='HIGH'; self.hold('HIGH_RISK_INDEPENDENT_ACCEPTANCE_REQUIRED')
    def test_high_requires_domain(self): self.r['risk']='HIGH'; self.hold('HIGH_RISK_DOMAIN_REVIEW_REQUIRED')
    def test_high_diversity(self): self.r['risk']='HIGH'; self.hold('HIGH_RISK_PANEL_DIVERSITY_REQUIRED')
    def test_budget_limit_depth(self): self.r['turtle_budget']['max_depth']=10; self.fail('TURTLE_BUDGET_UNBOUNDED')
    def test_budget_limit_workers(self): self.r['turtle_budget']['max_active_workers']=10**7; self.fail('TURTLE_BUDGET_UNBOUNDED')
    def test_budget_limit_rounds(self): self.r['turtle_budget']['max_rounds']=3; self.fail('TURTLE_BUDGET_UNBOUNDED')
    def test_bad_boolean_budget(self): self.r['turtle_budget']['max_depth']=True; self.fail('TURTLE_BUDGET_MISSING')
    def test_malformed_test(self): self.r['tests'][0]['status']='PROVED'; self.fail('MALFORMED_TEST')
    def test_test_failure_kept(self): self.r['tests'][0]['status']='FAIL'; self.hold('OBSERVED_TEST_FAILURE')
    def test_review_requires_receipt(self): self.r['stage']='REVIEW'; self.hold('STAGE_REQUIRES_TEST_RECEIPT')
    def test_release_needs_security(self): self.r['stage']='PUBLIC_PREVIEW'; self.hold('SECURITY_PRIVACY_REVIEW_NOT_BOUND')
    def test_public_needs_rollback(self): self.r['stage']='PUBLIC_PREVIEW'; self.hold('ROLLBACK_OR_EXIT_NOT_RECORDED')
    def test_operate_needs_receiver(self): self.r['stage']='OPERATE'; self.hold('INDEPENDENT_RECEIVER_READPROOF_REQUIRED')
    def test_operate_needs_outcome(self): self.r['stage']='OPERATE'; self.hold('RECEIVER_OUTCOME_NOT_BOUND')
    def test_unsupported_ack_fails(self): self.r['receiver_ack']=True; self.fail('ACK_WITHOUT_RECEIVER_PROOF')
    def test_unauthorized_effect_fails(self): self.r['real_effects_executed']=1; self.fail('READ_ONLY_CANARY_EFFECT_LIMIT')
    def test_false_approval_fails(self): self.r['review_state']='APPROVED'; self.fail('APPROVED_WITHOUT_ACCEPTANCE')
    def test_cannot_mutate_source(self): before=copy.deepcopy(self.r); evaluate(self.r); self.assertEqual(before,self.r)
    def test_malformed_input_fails(self): self.assertEqual(evaluate(None)['status'],'FAIL')
    def test_declared_receiver_does_not_certify(self):
        self.r.update(stage='OPERATE', receiver_ack=True, receiver_proof='fixture:self-asserted-ack',
                      external_user_outcome_ref='fixture:self-asserted-user', rollback_ref='fixture:rollback',
                      security_privacy_review_ref='fixture:privacy')
        self.r['tests'][0].update(status='PASS', receipt_ref='fixture:self-attested-test')
        self.assertEqual(evaluate(self.r)['status'],'PASS_DECLARED_STRUCTURE_ONLY')
        self.assertIn('NOT_SOURCE_AUTHENTICATION',evaluate(self.r)['scope'])

if __name__=='__main__': unittest.main()