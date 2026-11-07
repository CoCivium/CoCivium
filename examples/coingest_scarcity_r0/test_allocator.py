import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from allocator import plan, qualified, feasible, validate_candidate

HERE = Path(__file__).resolve().parent

class SyntheticAllocatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads((HERE / 'fixture.json').read_text('utf-8'))
        cls.candidates = cls.fixture['candidates']
        cls.budget = cls.fixture['budget']

    def test_pinned_fixture_is_parsable(self):
        self.assertEqual(self.fixture['schema'], 'CoAll.CoIngestSyntheticFixture.R0')
        self.assertEqual(len(self.candidates), 10)

    def test_expected_held_count(self):
        good, bad = qualified(self.candidates)
        self.assertEqual((len(good), len(bad)), (6, 4))

    def test_private_intake_requires_gate(self):
        c = copy.deepcopy(self.candidates[8])
        self.assertIn('HUMAN_OR_PRIVACY_GATE', validate_candidate(c))

    def test_outreach_cannot_run(self):
        self.assertIn('EFFECT_OR_AUTHORITY_HELD', validate_candidate(self.candidates[6]))

    def test_real_money_investment_cannot_run(self):
        self.assertIn('EFFECT_OR_AUTHORITY_HELD', validate_candidate(self.candidates[7]))

    def test_unknown_source_does_not_allocate(self):
        self.assertIn('SOURCE_DIGEST_MISMATCH', validate_candidate(self.candidates[9]))

    def test_source_poison_rejected(self):
        c = copy.deepcopy(self.candidates[1])
        c['evidence_text'] += ' injection'
        self.assertIn('SOURCE_DIGEST_MISMATCH', validate_candidate(c))

    def test_unsafe_authority_rejected(self):
        c = copy.deepcopy(self.candidates[1])
        c['authority'] = 'ALLOW_ALL'
        self.assertIn('EFFECT_OR_AUTHORITY_HELD', validate_candidate(c))

    def test_unknown_budget_rejected(self):
        budget = copy.deepcopy(self.budget)
        budget.pop('reviewer_minutes')
        with self.assertRaises(ValueError):
            plan(self.candidates, budget)

    def test_boolean_money_budget_rejected(self):
        budget = copy.deepcopy(self.budget)
        budget['cash_cents'] = True
        with self.assertRaises(ValueError):
            plan(self.candidates, budget)

    def test_duplicate_work_deduped(self):
        good, bad = qualified([self.candidates[1], self.candidates[1]])
        self.assertEqual(len(good), 1)
        self.assertIn('DUPLICATE_WORK_ID', bad[0]['reasons'])

    def test_shared_collision_domain_cannot_double_allocate(self):
        self.assertFalse(feasible([self.candidates[2], self.candidates[5]],
                                  {k: 1000 for k in self.budget}))

    def test_rare_workers_cap_limits_selection(self):
        budget = copy.deepcopy(self.budget)
        budget['worker_slots'] = 1
        self.assertEqual(len(plan(self.candidates, budget)['selected']), 1)

    def test_no_human_loop_permitted_when_safe(self):
        result = plan(self.candidates, self.budget)
        self.assertEqual(result['used']['human_minutes'], 0)
        self.assertGreater(result['human_free_candidate_count'], 0)
        self.assertGreater(result['projected_unattended_minutes'], 0)
        self.assertEqual(result['actual_unattended_duration'], 'NOT_MEASURED')

    def test_not_using_division_by_zero_for_human_minutes(self):
        result = plan(self.candidates, self.budget)
        self.assertNotIn('value_per_human_minute', result)
        self.assertIn('projected_human_minutes_avoided', result)

    def test_frontier_utility_exceeds_first_fit_on_fixture(self):
        first = plan(self.candidates, self.budget, 'first_fit')
        best = plan(self.candidates, self.budget, 'frontier')
        self.assertGreater(best['projected_utility_score_pctpoints'], first['projected_utility_score_pctpoints'])
        self.assertGreater(best['projected_human_minutes_avoided'], first['projected_human_minutes_avoided'])

    def test_no_dollars_spent_and_no_external_effects(self):
        r = plan(self.candidates, self.budget)
        self.assertEqual(r['used']['cash_cents'], 0)
        self.assertEqual((r['external_actions'], r['financial_actions']), (0, 0))

    def test_outcomes_are_not_claimed_as_real(self):
        r = plan(self.candidates, self.budget)
        self.assertEqual(r['actual_beneficiary_value'], 'NOT_MEASURED')
        self.assertEqual(r['independent_receiver_ack'], 'NOT_OBSERVED')

    def test_reversibility_is_required(self):
        c = copy.deepcopy(self.candidates[1]); c['reversible'] = False
        self.assertIn('PROOF_OR_REVERSIBILITY_HELD', validate_candidate(c))

    def test_unqualified_source_not_promoted(self):
        c = copy.deepcopy(self.candidates[1]); c['evidence_class'] = 'UNKNOWN'
        self.assertIn('UNQUALIFIED_EVIDENCE_CLASS', validate_candidate(c))

    def test_negative_resource_rejected(self):
        c = copy.deepcopy(self.candidates[1]); c['resources']['cpu_units'] = -1
        self.assertIn('BAD_RESOURCE_cpu_units', validate_candidate(c))

    def test_unselected_qualified_options_are_retained(self):
        r = plan(self.candidates, self.budget)
        good, _ = qualified(self.candidates)
        self.assertEqual(set(r['selected']) | set(r['deferred_qualified_options']),
                         {c['work_id'] for c in good})
        self.assertFalse(set(r['selected']) & set(r['deferred_qualified_options']))

    def test_dormant_option_may_become_selected_after_constraint_change(self):
        before = plan(self.candidates, self.budget, 'frontier')
        enlarged = {k: 1000 for k in self.budget}
        enlarged['cash_cents'] = 0
        after = plan(self.candidates, enlarged, 'frontier')
        self.assertTrue(set(before['deferred_qualified_options']) & set(after['selected']))
        self.assertEqual(after['materialized_executor_count'], 0)

    def test_option_space_is_not_executor_population(self):
        r = plan(self.candidates, self.budget)
        self.assertGreater(r['candidate_count'], len(r['selected']))
        self.assertEqual(r['materialized_executor_count'], 0)
        self.assertIn('OPEN_OPTION_SPACE_NE_INFINITE_THROUGHPUT', r['nonclaims'])

    def test_results_repeat(self):
        a = plan(self.candidates, self.budget, 'frontier')
        b = plan(self.candidates, self.budget, 'frontier')
        self.assertEqual(a, b)

if __name__ == '__main__':
    unittest.main()
