import copy
import json
import unittest
from pathlib import Path
from CoDeviceVisiblePresenceR0 import project, validate, canonical, digest
FIXTURE = json.loads(Path(__file__).with_name('fixture.json').read_text(encoding='utf-8'))

class VisiblePresenceTest(unittest.TestCase):
    def case(self): return copy.deepcopy(FIXTURE)
    def test_eight_names(self): self.assertEqual(8,project(FIXTURE)['camera_count'])
    def test_names_unique(self): self.assertEqual(8,len({x['name'] for x in project(FIXTURE)['cards']}))
    def test_unknown_is_not_offline(self): self.assertEqual('UNKNOWN',project(FIXTURE)['cards'][-1]['status'])
    def test_known_quiet_is_not_dead(self): self.assertEqual('QUIET_REACHABLE',project(FIXTURE)['cards'][1]['status'])
    def test_fresh_person_is_observed_event(self): self.assertEqual('OBSERVED_EVENT',project(FIXTURE)['cards'][0]['status'])
    def test_expired_event_must_stale(self): self.assertEqual('STALE',project(FIXTURE)['cards'][2]['status'])
    def test_steady_light_proposal_only(self):
        c=project(FIXTURE)['cards'][0]
        self.assertEqual('REVIEW_STEADY_LOW_GLARE_LIGHT_ONLY',c['physical_proposal'])
        self.assertEqual('NONE',c['physical_effect'])
    def test_no_hardware_actions(self):
        r=project(FIXTURE);self.assertEqual(0,r['hardware_writes']);self.assertTrue(all(x['ptz']=='NEVER_MOVED' and x['siren']=='NEVER_SOUNDED' for x in r['cards']))
    def test_no_network(self): self.assertEqual(0,project(FIXTURE)['network_calls'])
    def test_no_av_capture(self):self.assertTrue(all(not x['image_or_audio_collected'] for x in project(FIXTURE)['cards']))
    def test_deterministic(self):self.assertEqual(canonical(project(FIXTURE)),canonical(project(self.case())))
    def test_source_hash(self):self.assertEqual(digest(FIXTURE),project(FIXTURE)['source_sha256'])
    def test_receiver_ack_unproven(self):self.assertEqual('UNPROVEN',project(FIXTURE)['real_receiver_ack'])
    def test_disabled_privacy_suppresses(self):
        d=self.case();d['cameras'][0]['privacy']='NO_PROJECTION'
        self.assertEqual('PRIVATE',project(d)['cards'][0]['status'])
        self.assertEqual('NONE',project(d)['cards'][0]['physical_proposal'])
    def test_unverified_capability_suppresses(self):
        d=self.case();d['cameras'][0]['capabilities']={"verified":False,"low_glare_light":False,"ptz":False}
        self.assertEqual('NONE',project(d)['cards'][0]['physical_proposal'])
    def test_daytime_suppresses_physical(self):
        d=self.case();d['cameras'][0]['night']=False
        self.assertEqual('NONE',project(d)['cards'][0]['physical_proposal'])
    def test_cooldown_suppresses_physical(self):
        d=self.case();d['cameras'][0]['last_ack_at']=d['as_of']
        self.assertEqual('NONE',project(d)['cards'][0]['physical_proposal'])
    def test_unreachable_no_ack(self):
        d=self.case();d['cameras'][0]['link']='OBSERVED_UNREACHABLE'
        self.assertEqual('UNREACHABLE',project(d)['cards'][0]['status'])
        self.assertEqual('NONE',project(d)['cards'][0]['physical_proposal'])
    def test_no_unsourced_health(self):
        d=self.case();d['cameras'][3]['link']='OBSERVED_REACHABLE'
        with self.assertRaisesRegex(ValueError,'HOLD_UNSOURCED_HEALTH'):validate(d)
    def test_no_future_observation(self):
        d=self.case();d['cameras'][0]['observed_at']='2026-11-04T00:00:00+00:00'
        with self.assertRaisesRegex(ValueError,'HOLD_FUTURE_AS_OBSERVED'):validate(d)
    def test_no_duplicate(self):
        d=self.case();d['cameras'][0]['name']=d['cameras'][1]['name']
        with self.assertRaisesRegex(ValueError,'HOLD_IDENTITY_COLLISION'):validate(d)
    def test_no_private_extra_fields(self):
        d=self.case();d['cameras'][0]['image_bytes']='rawframe'
        with self.assertRaisesRegex(ValueError,'HOLD_CAMERA_FIELDS'):validate(d)
    def test_no_audio_extra_fields(self):
        d=self.case();d['cameras'][0]['microphone']='on'
        with self.assertRaisesRegex(ValueError,'HOLD_CAMERA_FIELDS'):validate(d)
    def test_no_unauthorized_hardware(self):
        d=self.case();d['policy']['hardware_effects']=True
        with self.assertRaisesRegex(ValueError,'HOLD_HARDWARE_AND_NETWORK'):validate(d)
    def test_no_external_network(self):
        d=self.case();d['policy']['no_network']=False
        with self.assertRaisesRegex(ValueError,'HOLD_HARDWARE_AND_NETWORK'):validate(d)
    def test_bad_enum(self):
        d=self.case();d['cameras'][0]['event']='FACE_IDENTIFIED'
        with self.assertRaisesRegex(ValueError,'HOLD_ENUM'):validate(d)
    def test_null_time_is_not_current(self):
        d=self.case();d['cameras'][3]['observed_at']=None
        self.assertEqual('UNKNOWN',project(d)['cards'][3]['status'])
    def test_motion_doesnt_claim_person(self):
        d=self.case();d['cameras'][0]['event']='MOTION'
        self.assertEqual('OBSERVED_EVENT',project(d)['cards'][0]['status'])
        self.assertIn('no identity inferred',project(d)['cards'][0]['detail'])
    def test_no_unobserved_sensor_as_event(self):
        d=self.case();d['cameras'][1]['event']='PERSON';d['cameras'][1]['event_at']=d['as_of']
        with self.assertRaisesRegex(ValueError,'HOLD_EVENT_WITHOUT_SOURCE'):validate(d)
    def test_unknown_is_not_zero(self):
        self.assertTrue(all(x['status'] in {'UNKNOWN','STALE','OBSERVED_EVENT','QUIET_REACHABLE','PRIVATE','UNREACHABLE'} for x in project(FIXTURE)['cards']))
    def test_no_image_data_in_report(self):self.assertNotIn('image_bytes',canonical(project(FIXTURE)).decode())

if __name__=='__main__':unittest.main(verbosity=2)
