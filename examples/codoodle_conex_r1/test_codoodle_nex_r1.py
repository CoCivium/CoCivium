"""Stdlib regression tests. No credentials, network, accounts, cameras, or OS hooks."""
import contextlib
import copy
import io
import json
import pathlib
import tempfile
import unittest
from CoDoodleNexR1 import (
    AXES, OPERATORS, LOGICAL_TOTAL, ROUTES, SCENARIOS, MUST_EXERCISE,
    MAX_FRONTIER, MAX_BENCHMARK, NONCLAIMS, TURTLE_TEMPLATE,
    benchmark, canonical, decode, encode, indices, micro_canary,
    route_choice, run, score_candidate, select_candidates, sha,
    turtle_admission, validate_fixture,
)
ROOT = pathlib.Path(__file__).parent

class CoDoodleSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((ROOT / 'synthetic_source.json').read_text())
        cls.frontier = select_candidates(cls.source, 'unit-seed', 16)

    def test_fixture_valid(self): self.assertEqual(validate_fixture(self.source), self.source)
    def test_schema_reject(self):
        with self.assertRaises(ValueError): validate_fixture({**self.source, 'schema': 'BAD'})
    def test_private_reject(self):
        with self.assertRaises(ValueError): validate_fixture({**self.source, 'privacy': 'PRIVATE'})
    def test_authority_reject(self):
        with self.assertRaises(ValueError): validate_fixture({**self.source, 'authority': 'SEND'})
    def test_credential_reject(self):
        with self.assertRaises(ValueError): validate_fixture({**self.source, 'credential_material': 'test-secret'})
    def test_raw_input_reject(self):
        with self.assertRaises(ValueError): validate_fixture({**self.source, 'raw_input': 'bad'})
    def test_unknown_source_field_reject(self):
        with self.assertRaises(ValueError): validate_fixture({**self.source, 'password': 'bad'})
    def test_source_effect_reject(self):
        with self.assertRaises(ValueError): validate_fixture({**self.source, 'promised_effects': 1})
    def test_empty_summary_reject(self):
        with self.assertRaises(ValueError): validate_fixture({**self.source, 'summary': 'x'})
    def test_oversized_summary_reject(self):
        with self.assertRaises(ValueError): validate_fixture({**self.source, 'summary': 'x' * 1201})
    def test_nonstr_unverified_reject(self):
        with self.assertRaises(ValueError): validate_fixture({**self.source, 'unverified_references': 'not-list'})
    def test_all_operators_exactly_eighteen(self): self.assertEqual(len(OPERATORS), 18)
    def test_operators_unique(self): self.assertEqual(len(set(OPERATORS)), len(OPERATORS))
    def test_trillion_syntactic_population(self): self.assertGreater(LOGICAL_TOTAL, 10**12)
    def test_zero_index_roundtrip(self): self.assertEqual(encode(decode(0)), 0)
    def test_last_index_roundtrip(self): self.assertEqual(encode(decode(LOGICAL_TOTAL - 1)), LOGICAL_TOTAL - 1)
    def test_middle_index_roundtrip(self):
        i = LOGICAL_TOTAL // 2
        self.assertEqual(encode(decode(i)), i)
    def test_negative_index_rejected(self):
        with self.assertRaises(ValueError): decode(-1)
    def test_overflow_index_rejected(self):
        with self.assertRaises(ValueError): decode(LOGICAL_TOTAL)
    def test_axis_missing_rejected(self):
        v = decode(0); v.pop('scale')
        with self.assertRaises(ValueError): encode(v)
    def test_invalid_axis_choice_rejected(self):
        v = decode(0); v['observer'] = 'ET_AUTHORITY'
        with self.assertRaises(ValueError): encode(v)
    def test_seeded_indices_reproducible(self): self.assertEqual(indices('a', 32), indices('a', 32))
    def test_different_seed_indices(self): self.assertNotEqual(indices('a', 32), indices('b', 32))
    def test_seeded_indices_no_duplicates(self): self.assertEqual(len(set(indices('a', 32))), 32)
    def test_limit_negative_rejected(self):
        with self.assertRaises(ValueError): select_candidates(self.source, 's', -1)
    def test_limit_over_32_rejected(self):
        with self.assertRaises(ValueError): select_candidates(self.source, 's', 33)
    def test_zero_limit_empty(self): self.assertEqual(select_candidates(self.source, 's', 0)['selected'], [])
    def test_selected_frontier_bounded(self): self.assertLessEqual(len(self.frontier['selected']), 32)
    def test_source_sha_matches(self): self.assertEqual(self.frontier['source_sha256'], sha(canonical(self.source)))
    def test_selected_id_unique(self):
        items = self.frontier['selected']; self.assertEqual(len(items), len({x['candidate_id'] for x in items}))
    def test_forced_scenarios_present(self):
        found = {x['axes']['scenario'] for x in self.frontier['selected']}
        for s in SCENARIOS: self.assertIn(s, found)
    def test_forced_negative_lanes_present(self):
        ops = {x['axes']['operator'] for x in self.frontier['selected']}
        for o in ('NULL', 'INVERSE', 'FALSIFIER', 'COUNTERFACTUAL'): self.assertIn(o, ops)
    def test_seeded_replay_same_bytes(self): self.assertEqual(canonical(self.frontier), canonical(select_candidates(self.source, 'unit-seed', 16)))
    def test_different_seed_different_candidate(self): self.assertNotEqual(self.frontier['selected'], select_candidates(self.source, 'another-seed', 16)['selected'])
    def test_no_execution_in_frontier(self): self.assertTrue(self.frontier['no_execution'])
    def test_zero_workers(self): self.assertEqual(self.frontier['active_workers'], 0)
    def test_zero_effects(self):
        self.assertTrue(all(all(v == 0 for v in c['effects'].values()) for c in self.frontier['selected']))
    def test_no_authority(self): self.assertTrue(all(x['authority'] == 'NONE' for x in self.frontier['selected']))
    def test_et_branch_held(self):
        x = next(x for x in self.frontier['selected'] if x['axes']['scenario'] == 'ET_TECHNOSIGNATURE')
        self.assertTrue(x['review_state'].startswith('HELD')); self.assertEqual(x['epistemic_class'], 'EMPIRICAL_HYPOTHESIS')
    def test_g_d_branch_nonempirical(self):
        x = next(x for x in self.frontier['selected'] if x['axes']['scenario'] == 'G_D_PHILOSOPHY')
        self.assertTrue(x['review_state'].startswith('HELD')); self.assertIn('NOT_AN_EMPIRICAL', x['proof_boundary'])
    def test_story_branch_unverified(self):
        x = next(x for x in self.frontier['selected'] if x['axes']['scenario'] == 'SYNTHKIND_FICTION')
        self.assertTrue(x['review_state'].startswith('HELD')); self.assertEqual(x['epistemic_class'], 'SPECULATIVE_STORY')
    def test_policy_microchecks_pass(self): self.assertTrue(all(micro_canary(self.frontier).values()))
    def test_eligible_only_local_deterministic(self):
        self.assertTrue(all(not x['micro_canary_eligible'] or x['axes']['substrate'] == 'DETERMINISTIC_LOCAL' for x in self.frontier['selected']))
    def test_eligible_exists_in_forced(self): self.assertTrue(any(x['micro_canary_eligible'] for x in self.frontier['selected']))
    def test_routes_zero_calls(self): self.assertTrue(all(route_choice(x)['requested_calls'] == 0 for x in ROUTES))
    def test_unsupported_route_rejected(self):
        with self.assertRaises(ValueError): route_choice('SIGNED_IN_AS_COCIVIA')
    def test_claude_held(self): self.assertTrue(route_choice('CLAUDE_API')['connection'].startswith('HELD'))
    def test_ollama_held(self): self.assertTrue(route_choice('OLLAMA_LOCAL')['connection'].startswith('HELD'))
    def test_pi_held(self): self.assertTrue(route_choice('PI_ADAPTER')['connection'].startswith('HELD'))
    def test_route_no_credentials(self): self.assertFalse(route_choice('CLAUDE_API')['credentials_inspected'])
    def test_score_is_bounded(self):
        self.assertTrue(all(0 <= x['score'] <= 100 for x in self.frontier['selected']))
    def test_turtle_cap(self): self.assertEqual(TURTLE_TEMPLATE['max_depth'], 2)
    def test_turtle_valid_budget(self): self.assertEqual(turtle_admission(2, 2, 3, 2)['granted'], 2)
    def test_turtle_depth_reject(self): self.assertEqual(turtle_admission(3, 1, 3, 1)['status'], 'HELD')
    def test_turtle_round_reject(self): self.assertEqual(turtle_admission(1, 3, 3, 1)['status'], 'HELD')
    def test_turtle_budget_reject(self): self.assertEqual(turtle_admission(1, 1, 1, 2)['status'], 'HELD')
    def test_turtle_authority_reject(self): self.assertEqual(turtle_admission(1, 1, 2, 1, 'SEND')['status'], 'HELD')
    def test_turtle_unknown_budget_reject(self): self.assertEqual(turtle_admission('a', 1, 2, 1)['status'], 'HELD')
    def test_benchmark_too_large_reject(self):
        with self.assertRaises(ValueError): benchmark(MAX_BENCHMARK + 1)
    def test_benchmark_too_short_reject(self):
        with self.assertRaises(ValueError): benchmark(1)
    def test_benchmark_scope_measured(self):
        rec = benchmark(32)
        self.assertEqual(rec['rounds'], 32)
        self.assertGreater(rec['median_ns'], 0)
        self.assertIn('human_wall_time', rec['not_measuring'])
    def test_null_has_no_runtime_authority(self):
        item = next(x for x in self.frontier['selected'] if x['axes']['operator'] == 'NULL')
        self.assertEqual(item['effects']['workers'], 0)
    def test_nonclaims_et_and_identity(self):
        self.assertIn('ET_CANDIDATE_NE_ET_DETECTION', NONCLAIMS)
        self.assertIn('CLAUDE_ACCOUNT_NE_ASSISTANT_IDENTITY', NONCLAIMS)
    def test_run_creates_exact_local_receipt(self):
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()):
            out = run(ROOT / 'synthetic_source.json', 'for-test', 6, pathlib.Path(d), 16)
            p = json.loads((out / '90_receipt.json').read_text())
            frontier = json.loads((out / '20_frontier.json').read_text())
            self.assertEqual(p['frontier_sha256'], sha((out / '20_frontier.json').read_bytes()))
            self.assertEqual(frontier['selected_count'], 6)
            self.assertFalse(p['receiver_ack']); self.assertFalse(p['CoStead_landed'])
            self.assertEqual(p['passes'], p['total'])
            self.assertEqual((out / 'benchmark_evo.jsonl').read_text().count('\n'), 3)

# Test all transformation operators without generating workers, to avoid gaps.
def make_operator_test(op):
    def test(self):
        v = decode(0); v['operator'] = op
        self.assertEqual(decode(encode(v))['operator'], op)
    return test
for _op in OPERATORS:
    setattr(CoDoodleSmoke, 'test_operator_' + _op.lower(), make_operator_test(_op))

if __name__ == '__main__': unittest.main(verbosity=2)
