import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from CoStageReviewGateR0 import (
    STAGES, SEATS, ReviewError, assess_scorecard, git_blob_sha1,
    panel_independence_claim, validate_policy, validate_turtle_proposal,
    verify_source_bindings,
)

POLICY_PATH = Path(__file__).resolve().parents[1] / 'ai/review/stage-review-policy-r0.json'


def declared_scorecard():
    state = {
        'G01':'PASS_BOUNDED','G02':'FAIL_OBSERVED','G03':'HELD',
        'G04':'HELD','G05':'HELD','G06':'UNKNOWN','G07':'REVIEW_REQUIRED',
        'G08':'HELD','G09':'PARTIAL_BOUNDED','G10':'HELD','G11':'HELD',
        'G12':'HELD','G13':'HELD','G14':'HELD',
    }
    return {'schema':'CoCivium.CoSpiffSurvivabilityFireworks.R1',
        'gates':[{'id':id,'state':state[id],'next_proof':'one separate named proof',
            'nonclaim':'SOURCE_NE_ADOPTION'} for id in sorted(state)]}


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy=json.loads(POLICY_PATH.read_text())
        self.score=declared_scorecard()

    def assertRejectPolicy(self,change):
        p=copy.deepcopy(self.policy); change(p)
        with self.assertRaises(ReviewError): validate_policy(p)

    def test_01_valid_machine_policy(self):
        self.assertTrue(validate_policy(self.policy))

    def test_02_nine_lifecycle_stages(self):
        self.assertEqual([x['stage'] for x in self.policy['stages']],list(STAGES))

    def test_03_seven_seats_are_descriptive(self):
        self.assertEqual(self.policy['seats'],list(SEATS))
        self.assertEqual(self.policy['lifecycle_state'],'DESIGN_ONLY_NOT_ENFORCED_RUNTIME')

    def test_04_no_automatic_release_flag(self):
        self.assertTrue(all(x['promotion_boundary']=='HELD_UNTIL_EXTERNAL_EVIDENCE_AND_AUTHORITY' for x in self.policy['stages']))

    def test_05_no_stage_without_priors_or_negative_evidence(self):
        self.assertTrue(all({'PRIOR_WORK_REVIEW','NEGATIVE_RESULT_PRESERVATION'} <= set(x['required_evidence']) for x in self.policy['stages']))

    def test_06_missing_stage_rejected(self):
        self.assertRejectPolicy(lambda p:p['stages'].pop())

    def test_07_duplicate_stage_rejected(self):
        self.assertRejectPolicy(lambda p:p['stages'].__setitem__(2,p['stages'][1]))

    def test_08_unrecognized_seat_rejected(self):
        self.assertRejectPolicy(lambda p:p['stages'][0]['review_seats'].append('SUPERUSER'))

    def test_09_repeated_seat_rejected(self):
        self.assertRejectPolicy(lambda p:p['stages'][0]['review_seats'].append('PROVENANCE_CHECK'))

    def test_10_minted_recursion_rejected(self):
        self.assertRejectPolicy(lambda p:p['turtle_limits'].__setitem__('max_depth',3))

    def test_11_too_many_rounds_rejected(self):
        self.assertRejectPolicy(lambda p:p['turtle_limits'].__setitem__('max_rounds',3))

    def test_12_child_budget_source_rejected(self):
        self.assertRejectPolicy(lambda p:p['turtle_limits'].__setitem__('budget_inheritance','NEW_PER_CHILD'))

    def test_13_child_authority_gain_rejected(self):
        self.assertRejectPolicy(lambda p:p['turtle_limits'].__setitem__('authority_inheritance','INHERIT_PLUS'))

    def test_14_missing_nonclaim_rejected(self):
        self.assertRejectPolicy(lambda p:p['nonclaims'].remove('PANEL_SEAT_NE_INDEPENDENT_REVIEWER'))

    def test_15_missing_prior_review_rejected(self):
        self.assertRejectPolicy(lambda p:p['stages'][1]['required_evidence'].remove('PRIOR_WORK_REVIEW'))

    def test_16_missing_negative_result_rejected(self):
        self.assertRejectPolicy(lambda p:p['stages'][5]['required_evidence'].remove('NEGATIVE_RESULT_PRESERVATION'))

    def test_17_relaxed_promotion_rejected(self):
        self.assertRejectPolicy(lambda p:p['stages'][5].__setitem__('promotion_boundary','AUTO_PASS'))

    def test_18_duplicate_gate_rejected(self):
        self.assertRejectPolicy(lambda p:p['stages'][6]['required_gates'].append('G05'))

    def test_19_unsafe_source_path_rejected(self):
        self.assertRejectPolicy(lambda p:p['source_bindings'][0].__setitem__('path','../secrets.txt'))

    def test_20_source_binding_repeated_rejected(self):
        self.assertRejectPolicy(lambda p:p['source_bindings'].append(dict(p['source_bindings'][0])))

    def test_21_source_byte_readback_passes_when_pinned(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for bind in self.policy['source_bindings']:
                target=root / bind['path']
                target.parent.mkdir(parents=True,exist_ok=True)
                raw=(bind['role']+' synthetic fixture\n').encode('utf-8')
                target.write_bytes(raw)
                bind['git_blob_sha1']=git_blob_sha1(raw)
            result=verify_source_bindings(self.policy,root)
            self.assertEqual(len(result),4)

    def test_22_changed_source_is_held(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for bind in self.policy['source_bindings']:
                target=root / bind['path']
                target.parent.mkdir(parents=True,exist_ok=True)
                raw=(bind['role']+' local synthetic\n').encode()
                target.write_bytes(raw)
                bind['git_blob_sha1']=git_blob_sha1(raw)
            p=root / self.policy['source_bindings'][0]['path']
            p.write_bytes(p.read_bytes()+b'change')
            with self.assertRaises(ReviewError):verify_source_bindings(self.policy,root)

    def test_23_scorecard_matches_fourteen_gate_ids(self):
        report=assess_scorecard(self.policy,self.score)
        self.assertEqual(report['stage_count'],9)
        self.assertEqual(report['held_stages'],9)
        self.assertFalse(report['eligible_for_release'])

    def test_24_one_passing_source_gate_not_a_release(self):
        report=assess_scorecard(self.policy,self.score)
        self.assertEqual(report['stage_assessments'][0]['decision'],'HELD_UNQUALIFIED_GATE')

    def test_25_all_declared_gates_green_no_review_not_approved(self):
        for gate in self.score['gates']:
            gate['state']='PASS_BOUNDED'
        report=assess_scorecard(self.policy,self.score,source_verification=True)
        self.assertTrue(all(row['decision']=='HELD_UNASSIGNED_UNAUTHENTICATED_REVIEW' for row in report['stage_assessments']))
        self.assertFalse(report['eligible_for_release'])

    def test_26_duplicated_scorecard_gate_rejected(self):
        self.score['gates'][1]['id']='G01'
        with self.assertRaises(ReviewError):assess_scorecard(self.policy,self.score)

    def test_27_unknown_gate_state_rejected(self):
        self.score['gates'][0]['state']='THE_FIREWORKS_HAPPENED'
        with self.assertRaises(ReviewError):assess_scorecard(self.policy,self.score)

    def test_28_missing_named_gate_rejected(self):
        self.score['gates'].pop()
        with self.assertRaises(ReviewError):assess_scorecard(self.policy,self.score)

    def test_29_missing_gate_nonclaim_rejected(self):
        self.score['gates'][0].pop('nonclaim')
        with self.assertRaises(ReviewError):assess_scorecard(self.policy,self.score)

    def test_30_missing_next_proof_rejected(self):
        self.score['gates'][0]['next_proof']=''
        with self.assertRaises(ReviewError):assess_scorecard(self.policy,self.score)

    def test_31_unlisted_gate_dependency_rejected(self):
        self.policy['stages'][0]['required_gates'].append('G88')
        with self.assertRaises(ReviewError):assess_scorecard(self.policy,self.score)

    def test_32_zero_effects_in_report(self):
        report=assess_scorecard(self.policy,self.score)
        self.assertEqual(report['reviewer_assignments_created'],0)
        self.assertEqual(report['workers_started'],0)
        self.assertEqual(report['external_messages_sent'],0)
        self.assertFalse(report['independent_receiver_ack'])

    def test_33_no_turtle_authority_expansion(self):
        p={'depth':2,'rounds':2,'parent_budget':4,'allocated_children':[2,1,1],
            'parent_effects':['READ'],'child_effects':['READ']}
        self.assertTrue(validate_turtle_proposal(p))
        p['child_effects']=['READ','EMAIL_SEND']
        with self.assertRaises(ReviewError):validate_turtle_proposal(p)

    def test_34_no_turtle_budget_increase(self):
        p={'depth':1,'rounds':1,'parent_budget':4,'allocated_children':[3,2],
            'parent_effects':['READ'],'child_effects':['READ']}
        with self.assertRaises(ReviewError):validate_turtle_proposal(p)

    def test_35_no_turtle_oversubscription_by_bool(self):
        p={'depth':True,'rounds':1,'parent_budget':4,'allocated_children':[1],
            'parent_effects':[],'child_effects':[]}
        with self.assertRaises(ReviewError):validate_turtle_proposal(p)

    def test_36_no_turtle_recursive_infinity(self):
        p={'depth':10**12,'rounds':1,'parent_budget':1,'allocated_children':[1],
            'parent_effects':[],'child_effects':[]}
        with self.assertRaises(ReviewError):validate_turtle_proposal(p)

    def test_37_review_duplicate_actor(self):
        x=[{'actor_id':'same','model_family':'model','source_domain':'github'},
           {'actor_id':'same','model_family':'model','source_domain':'github'}]
        self.assertEqual(panel_independence_claim(x)['state'],'HELD_DUPLICATED_ACTOR')

    def test_38_same_source_and_model_not_independent(self):
        x=[{'actor_id':'a','model_family':'same','source_domain':'common'},
           {'actor_id':'b','model_family':'same','source_domain':'common'}]
        self.assertEqual(panel_independence_claim(x)['state'],'HELD_SHARED_MODEL_AND_SOURCE')

    def test_39_declared_diversity_not_authenticated(self):
        x=[{'actor_id':'a','model_family':'X','source_domain':'hostA'},
           {'actor_id':'b','model_family':'Y','source_domain':'hostB'}]
        y=panel_independence_claim(x)
        self.assertEqual(y['state'],'DECLARED_DIVERSE_NOT_AUTHENTICATED')
        self.assertFalse(y['independent_review_proven'])

    def test_40_empty_panel_held(self):
        self.assertEqual(panel_independence_claim([])['state'],'HELD_NO_REVIEWERS')


if __name__=='__main__':
    unittest.main()
