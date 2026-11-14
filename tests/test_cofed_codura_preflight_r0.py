"""Synthetic, bounded negative controls. Same-host tests are NOT remote custody proof."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
# Repository layout: scripts/ implementation, tests/ test module.
ROOT = Path(__file__).resolve().parents[1] if Path(__file__).resolve().parent.name == 'tests' else Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts' if (ROOT / 'scripts').exists() else ROOT))
from cofed_codura_preflight_r0 import SCHEMA, review

BYTES = b'# Rights-cleared synthetic article\n\nNo real personal or publisher content.\n'
SHA = hashlib.sha256(BYTES).hexdigest()


def domain(n):
    return {k: f'{k}-domain-{n}' for k in ('provider', 'account', 'site', 'power', 'credential_domain', 'key_custodian', 'operator')}


def packet():
    return {
        'schema': SCHEMA, 'source_origin_copy_id': 'c1', 'work_id': 'test-public-article', 'edition_id': 'r1', 'classification': 'PUBLIC_SAFE',
        'source': {'sha256': SHA, 'provenance_ref': 'test-only/fixture'},
        'rights': {'rightsholder': 'Synthetic fixture author', 'license': 'CC0-1.0-test-fixture', 'scope': 'synthetic', 'review_ref': 'test-review', 'review_state': 'APPROVED', 'third_party_cleared': True, 'privacy_approved': True, 'public_distribution_allowed': True},
        'assets': [{'id': 'logo', 'sha256': 'a' * 64}],
        'custody': [
            {'copy_id': 'c1', 'sha256': SHA, 'exact_readback': True, 'receipt_ref': 'proof1', 'readback_actor': 'actor1', 'failure_domain': domain('1')},
            {'copy_id': 'c2', 'sha256': SHA, 'exact_readback': True, 'receipt_ref': 'proof2', 'readback_actor': 'actor2', 'failure_domain': domain('2')},
        ],
        'restore': {
            'cold_test': True, 'origin_device_unavailable': True, 'origin_provider_unavailable': True, 'key_recovery_independent': True,
            'work_id': 'test-public-article', 'edition_id': 'r1', 'sha256': SHA,
            'restored_assets': {'logo': 'a' * 64}, 'rights_metadata_restored': True, 'lineage_restored': True,
            'receiver': {'receiver_id': 'c2', 'origin_ref': 'test-receiver', 'readproof_ref': 'receiver-assertion', 'observed_at': '2026-11-14T20:00:00Z', 'exact_readback': True, 'sha256': SHA},
            'duplicate_effects_observed': 0, 'recovery_without_human_relay': True,
        },
    }


class GateCases(unittest.TestCase):
    def assess(self, mutate=None, data=BYTES):
        p = packet()
        if mutate:
            mutate(p)
        return review(p, data)

    def held(self, code, mutate=None, data=BYTES):
        result = self.assess(mutate, data)
        self.assertEqual(result['state'], 'HOLD')
        self.assertIn(code, result['failure_codes'])
        self.assertFalse(result['durable_claim_accepted'])
        self.assertFalse(result['publication_authorized'])
        self.assertEqual(result['live_effects'], 0)

    def test_01_structurally_complete_is_not_durable(self):
        r = self.assess()
        self.assertEqual(r['state'], 'EVIDENCE_FIELDS_READY__EXTERNAL_AUTHENTICATION_PENDING')
        self.assertFalse(r['receiver_claim_accepted'])
        self.assertFalse(r['durable_claim_accepted'])
        self.assertFalse(r['publication_authorized'])
    def test_02_wrong_schema(self): self.held('HOLD_SCHEMA', lambda p: p.update(schema='old'))
    def test_03_missing_work_id(self): self.held('HOLD_IDENTITY', lambda p: p.pop('work_id'))
    def test_04_missing_edition(self): self.held('HOLD_IDENTITY', lambda p: p.pop('edition_id'))
    def test_05_unknown_classification(self): self.held('HOLD_CLASSIFICATION', lambda p: p.update(classification='UNKNOWN'))
    def test_06_missing_hash(self): self.held('HOLD_SOURCE_IDENTITY', lambda p: p['source'].pop('sha256'))
    def test_07_wrong_source_bytes(self): self.held('HOLD_SOURCE_HASH_MISMATCH', data=BYTES+b'changed')
    def test_08_unread_source(self): self.held('HOLD_SOURCE_BYTES_UNCHECKED', data=None)
    def test_09_rights_unreviewed(self): self.held('HOLD_RIGHTS', lambda p: p['rights'].update(review_state='PENDING'))
    def test_10_not_public_rights(self): self.held('HOLD_PUBLIC_RIGHTS', lambda p: p['rights'].update(public_distribution_allowed=False))
    def test_11_missing_privacy(self): self.held('HOLD_PRIVACY', lambda p: p['rights'].update(privacy_approved=False))
    def test_12_missing_asset_list(self): self.held('HOLD_ASSET_MANIFEST', lambda p: p.pop('assets'))
    def test_13_duplicate_asset_id(self): self.held('HOLD_DUPLICATE_ASSET_IDS', lambda p: p['assets'].append(p['assets'][0].copy()))
    def test_14_one_copy_only(self): self.held('HOLD_COPIES', lambda p: p.update(custody=p['custody'][:1]))
    def test_15_fake_second_copy_id(self): self.held('HOLD_COPY_IDENTITIES', lambda p: p['custody'][1].update(copy_id='c1'))
    def test_16_wrong_copy_hash(self): self.held('HOLD_COPY_READBACK', lambda p: p['custody'][1].update(sha256='b'*64))
    def test_17_missing_copy_readback(self): self.held('HOLD_COPY_READBACK', lambda p: p['custody'][1].update(exact_readback=False))
    def test_18_same_provider(self): self.held('HOLD_SHARED_OR_UNKNOWN_FAILURE_DOMAIN', lambda p: p['custody'][1]['failure_domain'].update(provider='provider-domain-1'))
    def test_19_same_account(self): self.held('HOLD_SHARED_OR_UNKNOWN_FAILURE_DOMAIN', lambda p: p['custody'][1]['failure_domain'].update(account='account-domain-1'))
    def test_20_same_site(self): self.held('HOLD_SHARED_OR_UNKNOWN_FAILURE_DOMAIN', lambda p: p['custody'][1]['failure_domain'].update(site='site-domain-1'))
    def test_21_same_power(self): self.held('HOLD_SHARED_OR_UNKNOWN_FAILURE_DOMAIN', lambda p: p['custody'][1]['failure_domain'].update(power='power-domain-1'))
    def test_22_same_credential(self): self.held('HOLD_SHARED_OR_UNKNOWN_FAILURE_DOMAIN', lambda p: p['custody'][1]['failure_domain'].update(credential_domain='credential_domain-domain-1'))
    def test_23_same_key_custodian(self): self.held('HOLD_SHARED_OR_UNKNOWN_FAILURE_DOMAIN', lambda p: p['custody'][1]['failure_domain'].update(key_custodian='key_custodian-domain-1'))
    def test_24_same_operator(self): self.held('HOLD_SHARED_OR_UNKNOWN_FAILURE_DOMAIN', lambda p: p['custody'][1]['failure_domain'].update(operator='operator-domain-1'))
    def test_25_unknown_domain_field(self): self.held('HOLD_SHARED_OR_UNKNOWN_FAILURE_DOMAIN', lambda p: p['custody'][1]['failure_domain'].update(site='UNKNOWN'))
    def test_26_missing_cold_restore(self): self.held('HOLD_COLD_RESTORE', lambda p: p['restore'].update(cold_test=False))
    def test_27_origin_device_not_removed(self): self.held('HOLD_COLD_RESTORE', lambda p: p['restore'].update(origin_device_unavailable=False))
    def test_28_origin_provider_not_removed(self): self.held('HOLD_COLD_RESTORE', lambda p: p['restore'].update(origin_provider_unavailable=False))
    def test_29_no_key_recovery(self): self.held('HOLD_COLD_RESTORE', lambda p: p['restore'].update(key_recovery_independent=False))
    def test_30_wrong_restored_edition(self): self.held('HOLD_RESTORED_EDITION', lambda p: p['restore'].update(edition_id='r2'))
    def test_31_corrupted_restored_assets(self): self.held('HOLD_RESTORED_ASSETS', lambda p: p['restore'].update(restored_assets={'logo': 'c'*64}))
    def test_32_rights_metadata_missing(self): self.held('HOLD_RESTORED_RIGHTS_METADATA', lambda p: p['restore'].update(rights_metadata_restored=False))
    def test_33_predecessor_missing(self): self.held('HOLD_RESTORED_RIGHTS_METADATA', lambda p: p['restore'].update(lineage_restored=False))
    def test_34_receiver_origin_missing(self): self.held('HOLD_RECEIVER_READPROOF', lambda p: p['restore']['receiver'].pop('origin_ref'))
    def test_35_receiver_claim_wrong_hash(self): self.held('HOLD_RECEIVER_READPROOF', lambda p: p['restore']['receiver'].update(sha256='f'*64))
    def test_36_unrelated_receiver_claim(self): self.held('HOLD_RESTORE_INDEPENDENCE', lambda p: p['restore']['receiver'].update(receiver_id='outsider'))
    def test_37_duplicate_effects(self): self.held('HOLD_RESTORE_RECONCILIATION', lambda p: p['restore'].update(duplicate_effects_observed=2))
    def test_38_requires_human_relay(self): self.held('HOLD_RESTORE_RECONCILIATION', lambda p: p['restore'].update(recovery_without_human_relay=False))
    def test_39_non_dict(self): self.held('HOLD_SCHEMA', lambda p: p.update(schema=None))
    def test_40_payload_unknown_rights_private(self):
        self.held('HOLD_RIGHTS', lambda p: (p.update(classification='PRIVATE'), p['rights'].update(review_state='PENDING')))
    def test_41_diff_names_same_domain(self):
        self.held('HOLD_SHARED_OR_UNKNOWN_FAILURE_DOMAIN', lambda p: (p['custody'][1].update(copy_id='different-name'), p['custody'][1].update(failure_domain=copy.deepcopy(p['custody'][0]['failure_domain']))))
    def test_42_three_copies_one_distinct_pair(self):
        p=packet();clone=copy.deepcopy(p['custody'][0]);clone['copy_id']='c3';p['custody'].append(clone)
        r=review(p,BYTES)
        self.assertEqual(r['qualified_pair_count'],2)
        self.assertFalse(r['durable_claim_accepted'])
    def test_43_cli_exit_hold_and_no_source_write(self):
        with tempfile.TemporaryDirectory() as td:
            p=packet();p['custody']=p['custody'][:1]
            payload=Path(td)/'packet.json';src=Path(td)/'article.md'
            payload.write_text(json.dumps(p),encoding='utf-8');src.write_bytes(BYTES)
            prog=ROOT / 'scripts' / 'cofed_codura_preflight_r0.py' if (ROOT / 'scripts').exists() else ROOT / 'cofed_codura_preflight_r0.py'
            run=subprocess.run([sys.executable,str(prog),str(payload),'--source',str(src)],capture_output=True,text=True)
            self.assertEqual(run.returncode,2)
            self.assertEqual(src.read_bytes(),BYTES)
            self.assertIn('HOLD_COPIES',json.loads(run.stdout)['failure_codes'])
    def test_44_cli_structural_pass_not_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            payload=Path(td)/'packet.json';src=Path(td)/'article.md'
            payload.write_text(json.dumps(packet()),encoding='utf-8');src.write_bytes(BYTES)
            prog=ROOT / 'scripts' / 'cofed_codura_preflight_r0.py' if (ROOT / 'scripts').exists() else ROOT / 'cofed_codura_preflight_r0.py'
            run=subprocess.run([sys.executable,str(prog),str(payload),'--source',str(src)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0)
            self.assertFalse(json.loads(run.stdout)['durable_claim_accepted'])
            self.assertEqual(src.read_bytes(),BYTES)
    def test_45_bad_json_rejected_without_raw_leak(self):
        with tempfile.TemporaryDirectory() as td:
            payload=Path(td)/'bad.json';src=Path(td)/'article.md'
            payload.write_text('{some private junk',encoding='utf-8');src.write_bytes(BYTES)
            prog=ROOT / 'scripts' / 'cofed_codura_preflight_r0.py' if (ROOT / 'scripts').exists() else ROOT / 'cofed_codura_preflight_r0.py'
            run=subprocess.run([sys.executable,str(prog),str(payload),'--source',str(src)],capture_output=True,text=True)
            self.assertEqual(run.returncode,2)
            self.assertNotIn('private junk',run.stdout)
    def test_46_receiver_must_not_be_origin(self):
        self.held('HOLD_RESTORE_INDEPENDENCE', lambda p: p['restore']['receiver'].update(receiver_id='c1'))
    def test_47_origin_copy_must_be_identified(self):
        self.held('HOLD_ORIGIN_COPY_ID', lambda p: p.pop('source_origin_copy_id'))
    def test_48_unhashable_copy_id_hold_no_crash(self):
        self.held('HOLD_COPY_IDENTITIES', lambda p: p['custody'][1].update(copy_id=['not-a-string']))
    def test_49_unhashable_asset_id_hold_no_crash(self):
        self.held('HOLD_ASSET_MANIFEST', lambda p: p['assets'][0].update(id=['not-a-string']))
    def test_50_empty_assets_valid_if_complete(self):
        p=packet();p['assets']=[];p['restore']['restored_assets']={}
        self.assertEqual(review(p,BYTES)['state'],'EVIDENCE_FIELDS_READY__EXTERNAL_AUTHENTICATION_PENDING')

if __name__ == '__main__':
    unittest.main(verbosity=2)
