import copy
import json
import unittest
from pathlib import Path
from conod_rebind_r0 import classify_message, validate_manifest, rebind

M = json.loads((Path(__file__).parent / 'conod_rebind_candidate_r0.json').read_text(encoding='utf-8'))
NOW = '2026-11-20T23:23:32Z'
OBS = {r['path']: {'git_blob_sha1': r['git_blob_sha1'],
                   'observed_utc': '2026-11-20T23:20:00Z'}
       for r in M['public_source_roots']}

def decide(message="'", manifest=M, obs=OBS, now=NOW,
           work_id='w1', role='REVIEWER', receiver='SESSION_OWNED'):
    return rebind(manifest, message, work_id=work_id, role=role,
                  receiver=receiver, observations=obs, now_utc=now)

class RebindTests(unittest.TestCase):
    def test_manifest_pins_and_no_authority(self):
        self.assertTrue(validate_manifest(M))
        self.assertEqual('NONE_FROM_ALIAS', M['default_authority'])
    def test_apostrophe_exact(self):
        self.assertEqual('REBIND_REQUEST', classify_message("'"))
    def test_whitespace_apostrophe_exact(self):
        self.assertEqual('REBIND_REQUEST', classify_message("  '  \n"))
    def test_explicit_conod(self):
        self.assertEqual('REBIND_REQUEST', classify_message('CoNod'))
    def test_full_user_rail_is_not_swallowed(self):
        self.assertEqual('EXPLICIT_TEXT_NOT_ALIAS', classify_message("' CoPre9.3+|CoGo+"))
    def test_apostrophe_inside_prose_is_not_trigger(self):
        self.assertEqual('EXPLICIT_TEXT_NOT_ALIAS', classify_message("that's good"))
    def test_quoted_code_is_not_trigger(self):
        self.assertEqual('EXPLICIT_TEXT_NOT_ALIAS', classify_message("print(\"'\")"))
    def test_non_string_does_not_trigger(self):
        self.assertEqual('NO_ALIAS', classify_message(None))
    def test_blank_does_not_trigger(self):
        self.assertEqual('NO_ALIAS', classify_message('  '))
    def test_good_observation_only_readonly_proposal(self):
        r = decide()
        self.assertEqual('QUALIFIED_READ_ONLY_REBIND_PROPOSAL', r['state'])
        self.assertEqual('NONE', r['effect_authority'])
        self.assertEqual(0, r['effect_executions'])
        self.assertFalse(r['receiver_ack'])
        self.assertEqual(4, r['source_pin_count'])
    def test_missing_workid_holds(self):
        self.assertEqual('HOLD_UNBOUND_WORKID', decide(work_id='')['state'])
    def test_missing_role_holds(self):
        self.assertEqual('HOLD_UNBOUND_ROLE', decide(role=None)['state'])
    def test_missing_receiver_holds(self):
        self.assertEqual('HOLD_UNBOUND_RECEIVER', decide(receiver='')['state'])
    def test_no_source_holds(self):
        self.assertEqual('HOLD_MISSING_SOURCE_OBSERVATIONS', decide(obs=None)['state'])
    def test_missing_one_pin_holds(self):
        x=copy.deepcopy(OBS); x.pop('CoPre.md')
        self.assertEqual('HOLD_MISSING_SOURCE_OBSERVATIONS', decide(obs=x)['state'])
    def test_mismatched_pin_holds(self):
        x=copy.deepcopy(OBS); x['CoPre.md']['git_blob_sha1']='0'*40
        self.assertEqual('HOLD_SOURCE_HASH_MISMATCH', decide(obs=x)['state'])
    def test_stale_observation_holds(self):
        x=copy.deepcopy(OBS); x['CoPre.md']['observed_utc']='2026-11-18T00:00:00Z'
        self.assertEqual('HOLD_STALE_SOURCE_OBSERVATION', decide(obs=x)['state'])
    def test_future_observation_holds(self):
        x=copy.deepcopy(OBS); x['CoPre.md']['observed_utc']='2027-01-01T00:00:00Z'
        self.assertEqual('HOLD_INVALID_OBSERVATION_TIME', decide(obs=x)['state'])
    def test_no_time_holds(self):
        self.assertEqual('HOLD_MISSING_SOURCE_OBSERVATIONS', decide(now=None)['state'])
    def test_duplicate_source_paths_holds(self):
        x=copy.deepcopy(M); x['public_source_roots'][1]['path']='CoPre.md'
        self.assertEqual('HOLD_INVALID_OR_AMBIGUOUS_MANIFEST', decide(manifest=x)['state'])
    def test_forged_manifest_authority_holds(self):
        x=copy.deepcopy(M); x['default_authority']='PUBLISH_ALL'
        self.assertEqual('HOLD_INVALID_OR_AMBIGUOUS_MANIFEST', decide(manifest=x)['state'])
    def test_no_unqualified_latest(self):
        x=copy.deepcopy(M); x['public_source_roots'][0]['git_blob_sha1']='main'
        self.assertEqual('HOLD_INVALID_OR_AMBIGUOUS_MANIFEST', decide(manifest=x)['state'])
    def test_explicit_full_rail_passthrough(self):
        r=decide("' CoPre9.3+|CoGo+")
        self.assertEqual('EXPLICIT_TEXT_NOT_ALIAS', r['state'])
        self.assertIsNone(r['one_next'])
        self.assertFalse(r['receiver_ack'])
    def test_no_source_cred_from_prose(self):
        r=decide("'", obs={})
        self.assertEqual('HOLD_MISSING_SOURCE_OBSERVATIONS', r['state'])
        self.assertEqual('NONE',r['effect_authority'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
