"""Offline adversarial acceptance for CoSituation R0 and issue #185."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from CoSituationR0 import validate, wake_preview, SCHEMA

FIXTURES = json.loads(Path(__file__).with_name('fixtures.json').read_text(encoding='utf-8'))['fixtures']


def event(x, **changes):
    e = {
        'kind': x['sit']['wake_on'], 'situation_id': x['situation_id'],
        'source_sha256': x['source']['sha256'], 'observed_at': '2026-10-25T06:20:00Z',
    }
    e.update(changes)
    return e


def synthetic_proof(e):
    return {'kind': 'SYNTHETIC_SOURCE_READBACK', 'source_sha256': e['source_sha256'],
            'observed_at': e['observed_at']}


class SituationTests(unittest.TestCase):
    def setUp(self):
        self.data = deepcopy(FIXTURES)
        self.software, self.device, self.session, self.future, self.mythic = self.data

    def assert_no_effect(self, result):
        self.assertEqual(result['authority'], 'NONE')
        self.assertTrue(all(value == 0 for value in result['effects'].values()))
        self.assertFalse(result.get('can_execute', False))

    def test_schema(self):
        self.assertEqual(SCHEMA, 'CoAll.CoSituation.R0')

    def test_five_substrates_one_envelope(self):
        expected = {'SOFTWARE': 'DIGITAL_EXECUTABLE', 'DEVICE': 'PHYSICAL_DEVICE',
                    'SESSION': 'LOGICAL_WORK', 'FUTURE_BRANCH': 'COUNTERFACTUAL',
                    'MYTHIC_OBJECT': 'SYMBOLIC'}
        got = {r['kind']: r['substrate'] for r in map(validate, self.data)}
        self.assertEqual(got, expected)
        for x in self.data:
            self.assert_no_effect(validate(x))

    def test_candidates_include_evolution_without_execution(self):
        x = validate(self.software)
        self.assertTrue(x['evolution_allowed_as_candidate'])
        self.assertEqual(x['meta_relation_count'], 1)
        self.assert_no_effect(x)

    def test_declared_hash_not_source_readproof(self):
        for x in self.data:
            self.assertEqual(validate(x)['source_readproof'], 'UNVERIFIED')

    def test_privacy_not_flattened(self):
        self.assertEqual([validate(x)['privacy'] for x in self.data],
                         ['PUBLIC', 'PRIVATE_LOCAL', 'PRIVATE_LOCAL', 'PUBLIC', 'PUBLIC'])

    def test_known_kind_required(self):
        self.device['subject']['kind'] = 'ALIEN_AGENCY'
        with self.assertRaisesRegex(ValueError, 'SUBSTRATE_KIND_MISMATCH'): validate(self.device)

    def test_kind_and_substrate_must_match(self):
        self.device['subject']['substrate'] = 'SYMBOLIC'
        with self.assertRaisesRegex(ValueError, 'SUBSTRATE_KIND_MISMATCH'): validate(self.device)

    def test_mythic_cannot_be_observed(self):
        self.mythic['subject']['epistemic'] = 'SOURCE_REPORT'
        with self.assertRaisesRegex(ValueError, 'MYTHIC_CANNOT_PROMOTE_TO_OBSERVED'): validate(self.mythic)

    def test_future_cannot_be_present_fact(self):
        self.future['subject']['epistemic'] = 'SOURCE_REPORT'
        with self.assertRaisesRegex(ValueError, 'FUTURE_CANNOT_PROMOTE_TO_PRESENT_FACT'): validate(self.future)

    def test_pseudoproven_source_ref_is_rejected(self):
        self.software['source']['readproof'] = 'INDEPENDENT_OBSERVER_VERIFIED'
        with self.assertRaisesRegex(ValueError, 'SOURCE_READPROOF_CANNOT_BE_ASSERTED'): validate(self.software)

    def test_invalid_hash_rejected(self):
        self.software['source']['sha256'] = 'sha256:FAKE'
        with self.assertRaisesRegex(ValueError, 'INVALID_DECLARED_SOURCE_SHA'): validate(self.software)

    def test_invalid_observer_assertion_rejected(self):
        self.device['observer']['proof'] = 'SENSORS_ON_X2'
        with self.assertRaisesRegex(ValueError, 'UNVERIFIED_OBSERVER_EVIDENCE'): validate(self.device)

    def test_effect_authority_never_allowed(self):
        self.software['authority']['effect'] = 'DEVICE_ADMIN'
        self.software['authority']['granted'] = True
        with self.assertRaisesRegex(ValueError, 'NO_EFFECT_AUTHORITY'): validate(self.software)

    def test_missing_effect_grant_rejected(self):
        self.software['authority'].pop('granted')
        with self.assertRaisesRegex(ValueError, 'NO_EFFECT_AUTHORITY'): validate(self.software)

    def test_sit_lifecycle_not_independent_crown(self):
        self.device['sit']['lifecycle_mode'] = 'ACTIVE'
        with self.assertRaisesRegex(ValueError, 'COSIT_CANNOT_REPLACE_LIFECYCLE'): validate(self.device)

    def test_sit_active_not_eligible(self):
        self.device['lifecycle'] = 'ACTIVE'
        self.device['sit']['lifecycle_mode'] = 'ACTIVE'
        with self.assertRaisesRegex(ValueError, 'COSIT_EXPECTS_QUIESCENCE'): validate(self.device)

    def test_missing_revalidation_disallowed(self):
        self.software['sit']['revalidate_before_effect'] = False
        with self.assertRaisesRegex(ValueError, 'MISSING_REVALIDATION_GATE'): validate(self.software)

    def test_temporal_order(self):
        self.software['time']['source_at'] = '2026-10-26T00:00:00Z'
        with self.assertRaisesRegex(ValueError, 'INCONSISTENT_TEMPORAL_ORDER'): validate(self.software)

    def test_invalid_calendar_date(self):
        self.software['time']['observed_at'] = '2026-02-30T06:00:00Z'
        with self.assertRaisesRegex(ValueError, 'INVALID_OBSERVED_AT'): validate(self.software)

    def test_invalid_zone(self):
        self.software['time']['observed_at'] = '2026-10-25T06:00:00-04:00'
        with self.assertRaisesRegex(ValueError, 'INVALID_OBSERVED_AT'): validate(self.software)

    def test_bad_privacy(self):
        self.software['privacy'] = 'WORLD_READ_ANYTHING'
        with self.assertRaisesRegex(ValueError, 'INVALID_PRIVACY'): validate(self.software)

    def test_unknown_privacy_preserved(self):
        self.software['privacy'] = 'UNKNOWN'
        self.assertEqual(validate(self.software)['privacy'], 'UNKNOWN')

    def test_unbound_meta_relation_rejected(self):
        self.software['relations'][2]['target_id'] = 'rel:not-local'
        with self.assertRaisesRegex(ValueError, 'UNGROUNDED_META_RELATION'): validate(self.software)

    def test_duplicate_relation_rejected(self):
        self.software['relations'][1]['id'] = 'rel:dependency'
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_RELATION_ID'): validate(self.software)

    def test_bad_relation_epistemic_rejected(self):
        self.mythic['relations'][0]['epistemic'] = 'G_D_CONFIRMED'
        with self.assertRaisesRegex(ValueError, 'INVALID_RELATION_EPISTEMIC'): validate(self.mythic)

    def test_relation_budget_is_finite(self):
        self.device['relations'] *= 33
        with self.assertRaisesRegex(ValueError, 'INVALID_RELATIONS'): validate(self.device)

    def test_reverence_not_effect_authority(self):
        self.mythic['reverence']['effect_authority'] = 'SEND_WORLDWIDE'
        with self.assertRaisesRegex(ValueError, 'REVERENCE_CANNOT_GRANT_AUTHORITY'): validate(self.mythic)

    def test_reverence_requires_named_basis(self):
        self.mythic['reverence']['basis'] = '   '
        with self.assertRaisesRegex(ValueError, 'INVALID_REVERENCE_BASIS'): validate(self.mythic)

    def test_no_event_dormant_no_effect(self):
        x = wake_preview(self.software)
        self.assertEqual(x['state'], 'DORMANT_AWAIT_WAKE')
        self.assert_no_effect(x)

    def test_wrong_situation_event_held(self):
        x = wake_preview(self.software, event(self.software, situation_id='other'))
        self.assertEqual(x['state'], 'HELD_UNBOUND_WAKE_EVENT')
        self.assert_no_effect(x)

    def test_unrelated_event_quiet(self):
        x = wake_preview(self.software, event(self.software, kind='EXPLICIT_INTENT'))
        self.assertEqual(x['state'], 'DORMANT_UNRELATED_EVENT')

    def test_old_event_held(self):
        x = wake_preview(self.software, event(self.software, observed_at='2026-10-24T03:00:00Z'))
        self.assertEqual(x['state'], 'HELD_EVENT_OLDER_THAN_SNAPSHOT')

    def test_changed_source_hold_before_any_acceptance(self):
        x = wake_preview(self.software, event(self.software, source_sha256='sha256:'+'9'*64))
        self.assertEqual(x['state'], 'HELD_SOURCE_REVISION_CHANGED_REBIND_REQUIRED')
        self.assert_no_effect(x)

    def test_stale_dormant_event_needs_revalidation(self):
        x = wake_preview(self.software, event(self.software))
        self.assertEqual(x['state'], 'HELD_STALE_REVALIDATION_REQUIRED')
        self.assert_no_effect(x)

    def test_mismatched_synthetic_readproof_held(self):
        e = event(self.software)
        e['readproof'] = {'kind':'SYNTHETIC_SOURCE_READBACK', 'source_sha256':'sha256:'+'1'*64, 'observed_at':e['observed_at']}
        x = wake_preview(self.software, e)
        self.assertEqual(x['state'], 'HELD_READPROOF_NOT_BOUND')

    def test_old_synthetic_readproof_held(self):
        e = event(self.software)
        e['readproof'] = synthetic_proof(e)
        e['readproof']['observed_at'] = '2026-10-25T06:00:00Z'
        x = wake_preview(self.software, e)
        self.assertEqual(x['state'], 'HELD_READPROOF_NOT_CURRENT')

    def test_invalid_appearance_of_independent_proof_held(self):
        e = event(self.device)
        e['readproof'] = synthetic_proof(e)
        e['readproof']['kind'] = 'INDEPENDENT_DEVICE_PROOF'
        x = wake_preview(self.device, e)
        self.assertEqual(x['state'], 'HELD_READPROOF_NOT_BOUND')

    def test_matching_synthetic_proof_cannot_authorize_effect(self):
        e = event(self.software)
        e['readproof'] = synthetic_proof(e)
        x = wake_preview(self.software, e)
        self.assertEqual(x['state'], 'SHADOW_REVALIDATION_CANDIDATE_EFFECTS_HELD')
        self.assertEqual(x['source_readproof'], 'SYNTHETIC_ONLY_NOT_INDEPENDENT')
        self.assertFalse(x['receiver_ack'])
        self.assert_no_effect(x)

    def test_all_five_potential_wakes_still_no_effect(self):
        for fixture in self.data:
            with self.subTest(kind=fixture['subject']['kind']):
                e = event(fixture)
                e['readproof'] = synthetic_proof(e)
                x = wake_preview(fixture, e)
                self.assertEqual(x['state'], 'SHADOW_REVALIDATION_CANDIDATE_EFFECTS_HELD')
                self.assert_no_effect(x)

    def test_no_mutation_of_inputs(self):
        original = deepcopy(self.software)
        e = event(self.software)
        before_e = deepcopy(e)
        validate(self.software)
        wake_preview(self.software, e)
        self.assertEqual(self.software, original)
        self.assertEqual(e, before_e)

    def test_self_referential_meta_relation_rejected(self):
        self.software['relations'][2]['target_id'] = 'rel:meta'
        with self.assertRaisesRegex(ValueError, 'CYCLIC_META_RELATION'): validate(self.software)

    def test_two_node_meta_cycle_rejected(self):
        self.software['relations'][1]['type'] = 'ABOUT_RELATION'
        self.software['relations'][1]['target_id'] = 'rel:meta'
        with self.assertRaisesRegex(ValueError, 'CYCLIC_META_RELATION'): validate(self.software)

    def test_meta_chain_depth_two_permitted(self):
        self.software['relations'][1]['type'] = 'ABOUT_RELATION'
        self.software['relations'][1]['target_id'] = 'rel:dependency'
        self.assertEqual(validate(self.software)['meta_relation_count'], 2)

    def test_meta_chain_depth_three_rejected(self):
        self.software['relations'][1]['type'] = 'ABOUT_RELATION'
        self.software['relations'][1]['target_id'] = 'rel:dependency'
        self.software['relations'].append({'id':'rel:outer', 'type':'ABOUT_RELATION',
                                           'target_id':'rel:meta', 'epistemic':'HYPOTHESIS'})
        with self.assertRaisesRegex(ValueError, 'META_RELATION_DEPTH_EXCEEDED'): validate(self.software)

    def test_untrusted_list_in_enum_is_rejected_not_crash(self):
        for location,key in [('subject','kind'), ('subject','epistemic'), ('sit','wake_on')]:
            x = deepcopy(self.software)
            x[location][key] = ['invalid']
            with self.subTest(field=key), self.assertRaises(ValueError): validate(x)
        for key in ['lifecycle','privacy']:
            x = deepcopy(self.software)
            x[key] = ['invalid']
            with self.subTest(field=key), self.assertRaises(ValueError): validate(x)
        for key in ['type','epistemic']:
            x = deepcopy(self.software)
            x['relations'][0][key] = ['invalid']
            with self.subTest(field=key), self.assertRaises(ValueError): validate(x)

    def test_no_stale_declared_proof_creates_coex(self):
        e = event(self.mythic)
        e['readproof'] = synthetic_proof(e)
        out = wake_preview(self.mythic,e)
        self.assertNotIn('COEX', out['state'])
        self.assertNotIn('INTEGRATED', out['state'])
        self.assert_no_effect(out)


if __name__ == '__main__':
    unittest.main()