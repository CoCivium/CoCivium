import json
import pathlib
import random
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import nexus
import cozombie_audit as zombie

class NexusTests(unittest.TestCase):
    def test_space_is_large_but_not_material(self):
        self.assertGreater(nexus.capacity(), 10 ** 12)

    def test_boundary_indices(self):
        for i in (0, 1, 12, nexus.capacity() // 2, nexus.capacity() - 1):
            self.assertEqual(i, nexus.rank(nexus.unrank(i)))

    def test_random_indices(self):
        rng = random.Random(551)
        for _ in range(1200):
            i = rng.randrange(nexus.capacity())
            self.assertEqual(i, nexus.rank(nexus.unrank(i)))

    def test_reject_invalid_indices(self):
        for v in (-1, nexus.capacity(), 5.4, True, '3'):
            with self.subTest(v=v), self.assertRaises(ValueError):
                nexus.unrank(v)

    def test_reject_mismatch(self):
        d = nexus.unrank(17)
        d.pop('glyph')
        with self.assertRaises(ValueError): nexus.rank(d)

    def test_reject_invalid_option(self):
        d = nexus.unrank(17)
        d['glyph'] = 'UNPROVEN_SUPERPOWER'
        with self.assertRaises(ValueError): nexus.rank(d)

    def test_deterministic(self):
        self.assertEqual(nexus.compile_shadow(), nexus.compile_shadow())

    def test_seed_differs(self):
        self.assertNotEqual(nexus.compile_shadow(seed=1)['candidates'], nexus.compile_shadow(seed=2)['candidates'])

    def test_bounds(self):
        for sample, selected in ((0, 1), (2049, 3), (200, 17), (1, 2)):
            with self.assertRaises(ValueError): nexus.compile_shadow(sample_count=sample, selected_count=selected)

    def test_no_raw_prompt(self):
        marker = 'PRIVATE_MARKER_DONT_PRINT_THIS_7c98'
        r = nexus.compile_shadow(marker)
        self.assertNotIn(marker, json.dumps(r))
        self.assertTrue(r['raw_input_stored'] is False)
        self.assertIn('input_sha256', r)

    def test_text_bounded(self):
        with self.assertRaises(ValueError): nexus.compile_shadow('X' * 20001)

    def test_public_only_output(self):
        r = nexus.compile_shadow()
        self.assertEqual(r['actual_experiments_run'], 0)
        self.assertEqual(r['live_agents_started'], 0)
        self.assertEqual(r['remote_receiver_acks'], 0)
        self.assertTrue(all(c['effect_authority'] == 'NONE' and not c['work_done'] for c in r['candidates']))

    def test_candidates_unique(self):
        r = nexus.compile_shadow(sample_count=2048, selected_count=16)
        self.assertEqual(len({c['id'] for c in r['candidates']}), 16)

    def test_private_and_unknown_held(self):
        d = nexus.unrank(0)
        d['scope'] = 'PRIVATE_LOCAL'
        self.assertEqual(nexus.classify(d), 'HELD_PRIVATE_CONTEXT')
        d['scope'] = 'UNKNOWN'
        self.assertEqual(nexus.classify(d), 'HELD_UNKNOWN_SOURCE')

    def test_revoked_held(self):
        d = nexus.unrank(0); d['scope'] = 'SYNTHETIC'; d['authority'] = 'REVOKED'
        self.assertEqual(nexus.classify(d), 'HELD_REVOKED')

    def test_remote_options_never_execute(self):
        d = nexus.unrank(1); d['scope'] = 'SYNTHETIC'; d['authority'] = 'NONE'
        d['substrate'] = 'REMOTE_MODEL_OPTION'
        self.assertTrue(nexus.classify(d).startswith('SHADOW_ONLY'))

    def test_compilation_namespace(self):
        r=nexus.compile_shadow()
        self.assertTrue(nexus.verify_compilation(r))
        r['manifest_hash']='0'*64
        with self.assertRaisesRegex(ValueError, 'SPEC_NAMESPACE_CHANGED'):
            nexus.verify_compilation(r)

    def test_relabel_drift_rejected(self):
        r=nexus.compile_shadow()
        r['candidates'][0]['dimensions']['relation']='OUT' if r['candidates'][0]['dimensions']['relation']!='OUT' else 'IN'
        with self.assertRaisesRegex(ValueError, 'CANDIDATE_DRIFT'):
            nexus.verify_compilation(r)

    def test_forged_execution_claim_rejected(self):
        r=nexus.compile_shadow();r['actual_experiments_run']=1
        with self.assertRaisesRegex(ValueError, 'FALSE_EXECUTION_CLAIM'):
            nexus.verify_compilation(r)

    def test_symbolic_vs_science(self):
        tags = nexus.tags_from('G_d, CoAura and Planck quantum')
        self.assertIn('SCIENCE_TERM', tags)
        self.assertIn('SYMBOLIC', tags)

    def test_no_decoding_unknown_input(self):
        r = nexus.compile_shadow('not-a-known-word-only')
        self.assertEqual(r['recognized_terms_only'], [])

class ZombieTests(unittest.TestCase):
    def test_recent_not_progress_proof(self):
        x = zombie.triage(zombie.DEMO[0])
        self.assertEqual(x['assessment'], 'RECENT_ACTIVITY_OBSERVED')
        self.assertEqual(x['receiver_ack'], 'NOT_VERIFIED')

    def test_unknown_owner_never_auto_reclaim(self):
        self.assertEqual(zombie.triage(zombie.DEMO[1])['assessment'], 'SUSPECTED_STALL')

    def test_manual_only_candidate(self):
        r = zombie.triage(zombie.DEMO[2]); self.assertEqual(r['assessment'], 'MANUAL_RECLAIM_CANDIDATE')
        self.assertFalse(r['automatic_wake']); self.assertFalse(r['lease_overwritten'])

    def test_revoked_blocks(self):
        self.assertEqual(zombie.triage(zombie.DEMO[3])['assessment'], 'BLOCKED_REVOKED')

    def test_rate_limit_holds(self):
        self.assertEqual(zombie.triage(zombie.DEMO[4])['assessment'], 'HELD_RATE_LIMIT')

    def test_conflict_holds(self):
        x = dict(zombie.DEMO[2], lease_contested=True)
        self.assertEqual(zombie.triage(x)['assessment'], 'ESCALATE_LEASE_CONFLICT')

    def test_privacy_preempts_stall(self):
        x = dict(zombie.DEMO[2], privacy_hold=True)
        self.assertEqual(zombie.triage(x)['assessment'], 'HELD_PRIVACY')

    def test_source_mismatch(self):
        x = dict(zombie.DEMO[2], source_valid=False)
        self.assertEqual(zombie.triage(x)['assessment'], 'HELD_BAD_SOURCE')

    def test_clock_skew(self):
        x = dict(zombie.DEMO[0], clock_skew=True)
        self.assertEqual(zombie.triage(x)['assessment'], 'HELD_UNFRESH_OBSERVATION')

    def test_old_observation(self):
        x = dict(zombie.DEMO[0], observation_age_s=400)
        self.assertEqual(zombie.triage(x)['assessment'], 'HELD_UNFRESH_OBSERVATION')

    def test_unknown_fields_rejected(self):
        x = dict(zombie.DEMO[0], kill_all=True)
        with self.assertRaises(ValueError): zombie.triage(x)

    def test_negative_ages_rejected(self):
        for col in ('heartbeat_age_s', 'observation_age_s'):
            x = dict(zombie.DEMO[0], **{col: -2})
            with self.assertRaises(ValueError): zombie.triage(x)

if __name__ == '__main__': unittest.main()
