#!/usr/bin/env python3
"""Stdlib-only, synthetic, no effects. Run: python -m unittest -v test_shadow_allocator."""
import copy
import hashlib
import json
import unittest

import shadow_allocator as a


class ShadowAllocatorTests(unittest.TestCase):
    def setUp(self):
        self.fixture = a.load_fixture()

    def test_six_policies(self):
        self.assertEqual(len(a.POLICIES), 6)
        self.assertEqual(len({a.run_shadow(self.fixture, p)['policy'] for p in a.POLICIES}), 6)

    def test_unknown_policy_fails(self):
        with self.assertRaises(ValueError):
            a.run_shadow(self.fixture, 'infinite_optimality')

    def test_repeatability_all_policies(self):
        for policy in a.POLICIES:
            self.assertEqual(a.run_shadow(self.fixture, policy), a.run_shadow(self.fixture, policy))

    def test_receipt_hash_commits_to_contents(self):
        p = a.run_shadow(self.fixture, 'evidence')
        digest = p.pop('plan_sha256')
        self.assertEqual(digest, a.compact_hash(p))

    def test_synthetic_never_claims_real_benefit(self):
        p = a.run_shadow(self.fixture, 'evidence')
        self.assertIn('PROXY_NE_REAL_BENEFIT', p['nonclaims'])
        self.assertIn('SHADOW_NE_EXECUTION', p['nonclaims'])

    def test_no_effect_beyond_shadow(self):
        for p in a.POLICIES:
            result = a.run_shadow(self.fixture, p)
            self.assertEqual(result['effect_ceiling'], 'ZERO_EXTERNAL_EFFECTS')
            self.assertNotIn('G', [x['task'] for x in result['selected']])

    def test_high_value_outreach_held(self):
        self.assertEqual(a.run_shadow(self.fixture, 'first_n')['held']['G'], 'HELD_EFFECT_NOT_SHADOW')

    def test_high_value_unconsented_held(self):
        self.assertEqual(a.run_shadow(self.fixture, 'evidence')['held']['F'], 'HELD_CONSENT_OR_AUTHORITY')

    def test_physical_energy_claim_held(self):
        for p in a.POLICIES:
            self.assertEqual(a.run_shadow(self.fixture, p)['held']['H'], 'HELD_REQUIRES_INDEPENDENT_PHYSICAL_MEASUREMENT')

    def test_symbolic_and_speculative_retained_as_candidates(self):
        r = a.run_shadow(self.fixture, 'novelty')
        self.assertNotIn('D', r['held'])
        self.assertNotIn('M', r['held'])
        self.assertIn('D', [s['task'] for s in r['selected']])

    def test_exact_duplicates_do_not_double_spend(self):
        r = a.run_shadow(self.fixture, 'first_n')
        self.assertEqual(r['held']['B'], 'DEDUPED_EXACT_WORK_OF:A')
        self.assertNotIn('B', [x['task'] for x in r['selected']])

    def test_distinct_source_not_deduped(self):
        f = copy.deepcopy(self.fixture)
        t = f['tasks'][1]
        t['source_sha256'] = hashlib.sha256(b'dissenting-source').hexdigest()
        r = a.run_shadow(f, 'first_n')
        self.assertNotIn('B', r['held'])
        self.assertEqual([x['task'] for x in r['selected']][:2], ['A', 'B'])

    def test_other_receiver_not_admitted(self):
        self.assertEqual(a.run_shadow(self.fixture, 'first_n')['held']['I'], 'HELD_RECEIVER_OR_PRIVACY')

    def test_private_not_admitted(self):
        self.assertEqual(a.run_shadow(self.fixture, 'first_n')['held']['P'], 'HELD_RECEIVER_OR_PRIVACY')

    def test_wrong_tenant_does_not_route(self):
        r = a.run_shadow(self.fixture, 'evidence')
        self.assertEqual(r['held']['O'], 'HELD_NO_QUALIFIED_RESOURCE_WITH_RESERVE')

    def test_missing_source_not_eligible(self):
        self.assertEqual(a.run_shadow(self.fixture, 'evidence')['held']['Q'], 'HELD_NO_EXACT_SOURCE_PIN')

    def test_invalid_source_digest_rejected(self):
        t = copy.deepcopy(self.fixture['tasks'][0])
        t['source_sha256'] = 'Z' * 64
        self.assertEqual(a.gate(t, self.fixture['receiver']), 'HELD_NO_EXACT_SOURCE_PIN')

    def test_no_material_wake_is_dormant(self):
        self.assertEqual(a.run_shadow(self.fixture, 'evidence')['held']['J'], 'DORMANT_NO_MATERIAL_WAKE')

    def test_stale_source_is_dormant(self):
        self.assertEqual(a.run_shadow(self.fixture, 'evidence')['held']['L'], 'DORMANT_NO_MATERIAL_WAKE')

    def test_capacity_and_attention_reserve_never_spent(self):
        f = self.fixture
        r = a.run_shadow(f, 'evidence')
        for node in f['resources']:
            for unit in a.UNITS:
                self.assertGreaterEqual(r['residual'][node['id']][unit], 0)

    def test_unavailable_candidate_not_selected(self):
        r = a.run_shadow(self.fixture, 'evidence')
        self.assertNotIn('unavailable_candidate_C', [x['node'] for x in r['selected']])

    def test_all_candidates_offline_yields_no_selection(self):
        r = a.run_shadow(self.fixture, 'evidence', offline=('candidate_A', 'candidate_B'))
        self.assertEqual(r['selected'], [])

    def test_failover_preserves_scope_identity(self):
        before = a.run_shadow(self.fixture, 'first_n')
        after = a.run_shadow(self.fixture, 'first_n', offline=('candidate_A',))
        before_a = next(x for x in before['selected'] if x['task'] == 'A')
        after_a = next(x for x in after['selected'] if x['task'] == 'A')
        self.assertEqual(before_a['scope_ref'], after_a['scope_ref'])
        self.assertNotEqual(before_a['node'], after_a['node'])

    def test_scope_reference_is_source_version_bound(self):
        f = copy.deepcopy(self.fixture['tasks'][0])
        a1 = a.identity(f)
        f['revision'] = 'v2'
        self.assertNotEqual(a1, a.identity(f))
        self.assertTrue(a1.startswith('candidate-ref:'))

    def test_hard_wave_cap(self):
        p = a.run_shadow(self.fixture, 'first_n', max_wave=1000000)
        self.assertLessEqual(len(p['selected']), self.fixture['max_wave'])

    def test_zero_wave_creates_no_work(self):
        p = a.run_shadow(self.fixture, 'evidence', max_wave=0)
        self.assertFalse(p['selected'])

    def test_negative_wave_rejected(self):
        with self.assertRaises(ValueError):
            a.run_shadow(self.fixture, 'first_n', max_wave=-2)

    def test_large_task_cannot_deplete_budget(self):
        p = a.run_shadow(self.fixture, 'evidence')
        self.assertEqual(p['held']['K'], 'HELD_NO_QUALIFIED_RESOURCE_WITH_RESERVE')

    def test_invalid_reserve_node_is_disabled(self):
        f = copy.deepcopy(self.fixture)
        f['resources'][0]['reserve']['cpu_units'] = 1000
        p = a.run_shadow(f, 'first_n')
        self.assertTrue(all(x['node'] != 'candidate_A' for x in p['selected']))

    def test_group_routing_optin_and_cap(self):
        e = {'topic': 'frontier', 'privacy': 'PUBLIC', 'authority': 'VIEW'}
        self.assertEqual(a.route_event(e, self.fixture['subscribers']), ['a_public', 'b_public'])

    def test_group_routing_never_leaks_private(self):
        e = {'topic': 'frontier', 'privacy': 'PRIVATE', 'authority': 'VIEW'}
        self.assertEqual(a.route_event(e, self.fixture['subscribers']), [])

    def test_group_routing_rejects_effect_permission(self):
        e = {'topic': 'frontier', 'privacy': 'PUBLIC', 'authority': 'EXTERNAL_SEND'}
        self.assertEqual(a.route_event(e, self.fixture['subscribers']), [])

    def test_group_routing_zero_fanout(self):
        e = {'topic': 'frontier', 'privacy': 'PUBLIC', 'authority': 'VIEW'}
        self.assertEqual(a.route_event(e, self.fixture['subscribers'], fanout_limit=0), [])

    def test_source_fixture_not_mutated(self):
        f = copy.deepcopy(self.fixture)
        before = json.dumps(f, sort_keys=True)
        a.run_shadow(f, 'novelty')
        self.assertEqual(before, json.dumps(f, sort_keys=True))

    def test_distinct_policies_change_ranking(self):
        names = []
        for p in a.POLICIES:
            names.append(tuple(x['task'] for x in a.run_shadow(self.fixture, p)['selected']))
        self.assertGreaterEqual(len(set(names)), 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
