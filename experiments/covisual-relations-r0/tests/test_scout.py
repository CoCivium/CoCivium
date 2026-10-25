import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import scout

class CoVisualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((scout.ROOT/'sources.json').read_text())
    def test_1_schema_and_count(self):
        self.assertEqual(len(scout.validate(self.data)),7)
    def test_2_rank_deterministic(self):
        entries=self.data['entries'];self.assertEqual(scout.rank(entries),scout.rank(list(reversed(entries))))
    def test_3_rank_budget(self):
        for count in (-1,0,4,True):
            with self.subTest(count=count), self.assertRaises(ValueError):scout.rank(self.data['entries'],count)
    def test_4_network_guards(self):
        for url in ('http://reactflow.dev/','https://localhost/','https://10.0.0.1/','https://github.com:80/test','https://github.com/x?token=private','file:///secret','https://evil.com/'):
            with self.subTest(url=url), self.assertRaises(ValueError):scout.canonical_url(url)
    def test_5_tracking_removed_not_tolerated(self):
        with self.assertRaises(ValueError):scout.canonical_url('https://openverse.org/?utm_source=copy')
    def test_6_no_unknown_fields(self):
        x=copy.deepcopy(self.data);x['entries'][0]['secret']='x'
        with self.assertRaises(ValueError):scout.validate(x)
    def test_7_duplicate_id(self):
        x=copy.deepcopy(self.data);x['entries'][1]['id']=x['entries'][0]['id']
        with self.assertRaises(ValueError):scout.validate(x)
    def test_8_duplicate_url(self):
        x=copy.deepcopy(self.data);x['entries'][1]['url']=x['entries'][0]['url']
        with self.assertRaises(ValueError):scout.validate(x)
    def test_9_invalid_score(self):
        x=copy.deepcopy(self.data);x['entries'][0]['fit']=True
        with self.assertRaises(ValueError):scout.validate(x)
    def test_10_missing_media_rights(self):
        self.assertFalse(scout.eligible_to_embed({'asset_rights':'CATALOG_LIKELY_CC'}))
    def test_11_no_auto_embeds(self):
        self.assertFalse(scout.eligible_to_embed({'asset_rights':'EXACT_ITEM_VERIFIED','privacy':'PUBLIC','allowed_use':'EXPLICITLY_PERMITTED','exact_source':'sha256:abc','reviewed_by':'human'}))
    def test_12_explicit_release_required(self):
        a={'asset_rights':'EXACT_ITEM_VERIFIED','privacy':'PUBLIC','allowed_use':'EXPLICITLY_PERMITTED','exact_source':'sha256:abc','reviewed_by':'license_reviewer','external_effect_authority':'SPECIFIC_PUBLIC_RELEASE_GRANTED'}
        self.assertTrue(scout.eligible_to_embed(a));a['external_effect_authority']='NO_PUBLICATION';self.assertFalse(scout.eligible_to_embed(a))
    def test_13_no_remote_effects_reported(self):
        r=scout.make_report();self.assertEqual((r['network_requests'],r['image_assets_reused'],r['recipient_acks']), (0,0,0))
    def test_14_ledger_roundtrip(self):
        a,b=scout.ledger_events(scout.make_report());self.assertTrue(scout.verify_ledger(a,b))
    def test_15_tamper_rejected(self):
        a,b=scout.ledger_events(scout.make_report());a=a.replace('NOT_RUN','PASS',1)
        with self.assertRaises(ValueError):scout.verify_ledger(a,b)
    def test_16_truncated_rejected(self):
        a,b=scout.ledger_events(scout.make_report());a='\n'.join(a.splitlines()[:-1])+'\n'
        with self.assertRaises(ValueError):scout.verify_ledger(a,b)
    def test_17_unsanctioned_kind_rejected(self):
        a=copy.deepcopy(self.data);a['entries'][0]['kind']='PERSON_PRIVATE_IMAGE'
        with self.assertRaises(ValueError):scout.validate(a)
    def test_18_source_rights_separate_from_asset_rights(self):
        self.assertTrue(all(e['rights'] and e['url'] for e in scout.validate(self.data)))
        self.assertEqual(scout.make_report()['image_assets_reused'],0)

if __name__ == '__main__':unittest.main()
