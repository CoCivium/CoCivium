import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from media_gate import SCHEMA, editorial_holds, inspect, probe_media, validate_spec

class MediaGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads((ROOT / 'manifest.json').read_text())
        cls.temp = tempfile.TemporaryDirectory(prefix='comedia_r1_')
        cls.tmp = Path(cls.temp.name)
        cls.with_media = shutil.which('ffmpeg') and shutil.which('ffprobe')
        if cls.with_media:
            commands = {
                'good.mp4': ['-f','lavfi','-i','testsrc2=size=720x1280:rate=24:duration=3','-f','lavfi','-i','sine=frequency=440:duration=3','-t','3','-c:v','mpeg4','-q:v','3','-c:a','aac','-b:a','128k'],
                'black.mp4': ['-f','lavfi','-i','color=c=black:s=720x1280:r=24:d=2','-f','lavfi','-i','sine=frequency=440:duration=2','-t','2','-c:v','mpeg4','-q:v','3','-c:a','aac','-b:a','128k'],
                'landscape.mp4': ['-f','lavfi','-i','testsrc2=size=1280x720:rate=24:duration=2','-f','lavfi','-i','sine=frequency=440:duration=2','-t','2','-c:v','mpeg4','-q:v','3','-c:a','aac','-b:a','128k'],
                'mute.mp4': ['-f','lavfi','-i','testsrc2=size=720x1280:rate=24:duration=2','-t','2','-c:v','mpeg4','-q:v','3','-an']
            }
            for name, args in commands.items():
                cp = subprocess.run(['ffmpeg','-y','-nostdin','-loglevel','error',*args,str(cls.tmp/name)],capture_output=True,text=True,timeout=50)
                if cp.returncode != 0:
                    raise RuntimeError(name+':'+cp.stderr[:300])
    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()
    def changed(self, path, value):
        item = copy.deepcopy(self.fixture)
        cur = item
        for key in path[:-1]: cur = cur[key]
        cur[path[-1]] = value
        return item
    def test_01_baseline_valid(self): self.assertEqual(validate_spec(self.fixture), [])
    def test_02_baseline_wip(self): self.assertEqual(inspect(self.fixture)['state'],'HELD_PREPUBLICATION')
    def test_03_zero_external_effects(self):
        r=inspect(self.fixture)
        self.assertEqual([r['publication_effects'],r['network_calls'],r['provider_sessions']],[0,0,0]);self.assertIsNone(r['receiver_ack'])
    def test_04_no_premature_release(self): self.assertFalse(inspect(self.fixture)['release_eligible'])
    def test_05_unknown_schema(self): self.assertTrue(validate_spec(self.changed(['schema'], 'other')))
    def test_06_missing_source(self): self.assertTrue(validate_spec(self.changed(['source_revision'], None)))
    def test_07_invalid_asset(self): self.assertTrue(validate_spec(self.changed(['asset_id'], 10)))
    def test_08_invalid_status(self): self.assertTrue(validate_spec(self.changed(['status'], 'PUBLISHED')))
    def test_09_invalid_shape(self): self.assertTrue(validate_spec(self.changed(['shape'], 'EVERYTHING')))
    def test_10_no_publication_authority(self): self.assertTrue(validate_spec(self.changed(['publication_effect_authorized'], True)))
    def test_11_no_fake_receiver_ack(self): self.assertTrue(validate_spec(self.changed(['receiver_ack'], 'ACK'))) 
    def test_12_no_fake_published_url(self): self.assertTrue(validate_spec(self.changed(['publication_url'], 'https://example.com'))) 
    def test_13_wip_label_required(self): self.assertTrue(validate_spec(self.changed(['public_note'], 'Coming soon'))) 
    def test_14_storyboard_min(self): self.assertTrue(validate_spec(self.changed(['storyboard'], [])))
    def test_15_storyboard_indexes(self): self.assertTrue(validate_spec(self.changed(['storyboard',0,'shot'], 7)))
    def test_16_typed_evidence(self): self.assertTrue(validate_spec(self.changed(['storyboard',0,'evidence_class'],'PROVEN'))) 
    def test_17_invalid_rights(self): self.assertTrue(validate_spec(self.changed(['rights','music'],'FREE_FROM_INTERNET'))) 
    def test_18_a11y_missing(self): self.assertTrue(validate_spec(self.changed(['accessibility','captions_prepared'], 'maybe'))) 
    def test_19_ai_use_boolean(self): self.assertTrue(validate_spec(self.changed(['ai_use_declared'], 'yes'))) 
    def test_20_wip_not_ready(self): self.assertIn('WIP_NOT_RELEASE_CANDIDATE', editorial_holds(self.fixture))
    def test_21_rights_hold(self): self.assertIn('RIGHTS_NOT_QUALIFIED', editorial_holds(self.fixture))
    def test_22_a11y_hold(self): self.assertIn('ACCESSIBILITY_TWIN_INCOMPLETE', editorial_holds(self.fixture))
    def test_23_editorial_held(self): self.assertIn('NO_EDITORIAL_REVIEW_RECEIPT', editorial_holds(self.fixture))
    def test_24_realistic_ai_disclosure(self):
        x=self.changed(['realistic_ai_alteration'],True)
        x['ai_use_declared']=False
        self.assertIn('PLATFORM_AI_USE_DISCLOSURE_MISSING',editorial_holds(x))
    def test_25_missing_file(self): self.assertEqual(probe_media(self.tmp/'missing.mp4')['state'], 'FAIL_MEDIA_MISSING')
    def test_26_invalid_zero_file(self):
        f=self.tmp/'empty.mp4';f.write_bytes(b'');self.assertEqual(probe_media(f)['state'],'FAIL_MEDIA_SIZE_BOUND')
    def test_27_tool_probe_valid(self):
        if not self.with_media:self.skipTest('ffmpeg not installed')
        p=probe_media(self.tmp/'good.mp4')
        self.assertEqual(p['state'],'PASS_SCOPED_MEDIA_DECODE')
        self.assertEqual((p['width'],p['height']),(720,1280))
        self.assertTrue(p['has_audio'])
        self.assertEqual(len(p['sha256']),64)
    def test_28_black_clip_requires_review(self):
        if not self.with_media:self.skipTest('ffmpeg not installed')
        r=inspect(self.fixture,self.tmp/'black.mp4')
        self.assertIn('BLACK_SEGMENTS_REQUIRE_EDITORIAL_REVIEW',r['holds'])
    def test_29_landscape_wrong_target(self):
        if not self.with_media:self.skipTest('ffmpeg not installed')
        r=inspect(self.fixture,self.tmp/'landscape.mp4')
        self.assertIn('WRONG_ASPECT_FOR_TARGET',r['holds'])
    def test_30_silent_clip_requires_review(self):
        if not self.with_media:self.skipTest('ffmpeg not installed')
        r=inspect(self.fixture,self.tmp/'mute.mp4')
        self.assertIn('AUDIO_OR_MUTE_INTENT_NOT_VERIFIED',r['holds'])
    def test_31_good_video_still_not_release_eligible(self):
        if not self.with_media:self.skipTest('ffmpeg not installed')
        r=inspect(self.fixture,self.tmp/'good.mp4')
        self.assertFalse(r['release_eligible'])
        self.assertTrue(r['media']['state'].startswith('PASS_SCOPED'))
    def test_32_black_hold_is_scoped_not_failed_content(self):
        if not self.with_media:self.skipTest('ffmpeg not installed')
        r=inspect(self.fixture,self.tmp/'black.mp4')
        self.assertEqual(r['state'],'HELD_PREPUBLICATION')
        self.assertTrue(r['media']['black_intervals_first_60s']>=1)

if __name__ == '__main__': unittest.main()
