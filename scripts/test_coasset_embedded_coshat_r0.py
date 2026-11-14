#!/usr/bin/env python3
"""Negative and positive self-contained CoSHAT / overlap recovery checks."""
import base64
import copy
import json
import tempfile
import unittest
from pathlib import Path

from coasset_embedded_coshat_r0 import (
    CARRIERS, HASH_SCOPE, NONCLAIMS, SCHEMA, build_capsules, canonical_bytes,
    read_capsule, reconstruct, scoped_envelope_bytes, seal, sha,
    verify_capsule, write_capsules,
)

PAYLOAD = b'CoSeed\0coObject-coTime-coSHAT\xff' * 7 + b'\n'


class EmbeddedAsset(unittest.TestCase):
    def setUp(self):
        self.records = build_capsules(PAYLOAD)

    def reject(self, code, fn):
        with self.assertRaisesRegex(ValueError, code):
            fn()

    def test_three_distinct_containers_and_two_link_floor(self):
        self.assertEqual(len(self.records), 3)
        for c in self.records:
            self.assertEqual(len(c['coValence']['partner_ids']), 2)
            self.assertNotIn(c['coValence']['self_id'], c['coValence']['partner_ids'])
            self.assertEqual(c['schema'], SCHEMA)

    def test_every_two_of_three_restores_exact_content(self):
        for i, j in ((0, 1), (0, 2), (1, 2)):
            with self.subTest(pair=(i, j)):
                self.assertEqual(reconstruct([self.records[i], self.records[j]]), PAYLOAD)

    def test_all_three_restores_exact_content(self):
        self.assertEqual(reconstruct(self.records), PAYLOAD)

    def test_empty_content_supported(self):
        self.assertEqual(reconstruct(build_capsules(b'')[1:]), b'')

    def test_odd_byte_content_supported(self):
        self.assertEqual(reconstruct(build_capsules(b'X')[:2]), b'X')

    def test_disk_restoration_with_original_deleted(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            original = root / 'original.bin'
            original.write_bytes(PAYLOAD)
            paths = write_capsules(build_capsules(original.read_bytes()), root)
            original.unlink()
            self.assertFalse(original.exists())
            self.assertEqual(len(paths), 3)
            for i, j in ((0, 1), (0, 2), (1, 2)):
                recovered = reconstruct([read_capsule(paths[i]), read_capsule(paths[j])])
                self.assertEqual(sha(recovered), sha(PAYLOAD))

    def test_no_overwrite_existing_capsule(self):
        with tempfile.TemporaryDirectory() as d:
            write_capsules(self.records, Path(d))
            with self.assertRaises(FileExistsError):
                write_capsules(self.records, Path(d))

    def test_canonical_hash_has_exact_exclusion(self):
        for c in self.records:
            self.assertEqual(c['coSHAT']['scope'], HASH_SCOPE)
            self.assertEqual(c['coSHAT']['envelope_sha256'], sha(scoped_envelope_bytes(c)))

    def test_insertion_order_does_not_change_canonical_hash(self):
        a = self.records[0]
        reordered = dict(reversed(list(a.items())))
        self.assertEqual(sha(scoped_envelope_bytes(reordered)), a['coSHAT']['envelope_sha256'])

    def test_source_content_not_mutated_by_restoration(self):
        before = copy.deepcopy(self.records)
        reconstruct(self.records[:2])
        self.assertEqual(before, self.records)

    def test_single_survivor_insufficient(self):
        self.reject('REQUIRES_TWO_OR_THREE', lambda: reconstruct([self.records[0]]))

    def test_pointer_only_cannot_rebuild(self):
        c = copy.deepcopy(self.records[0])
        c['fragment_base64'] = ''
        self.reject('FRAGMENT_DIGEST_MISMATCH', lambda: reconstruct([seal(c), self.records[1]]))

    def test_corrupt_metadata_without_rehash(self):
        c = copy.deepcopy(self.records[0]); c['nonclaims'][-1] = 'REWRITTEN'
        self.reject('ENVELOPE_DIGEST_MISMATCH', lambda: verify_capsule(c))

    def test_corrupt_fragment_without_rehash(self):
        c = copy.deepcopy(self.records[0]); c['fragment_base64'] = 'WA=='
        self.reject('ENVELOPE_DIGEST_MISMATCH', lambda: verify_capsule(c))

    def test_resealed_bad_fragment_rejected(self):
        c = copy.deepcopy(self.records[0]); c['fragment_base64'] = 'WA=='
        self.reject('FRAGMENT_DIGEST_MISMATCH', lambda: verify_capsule(seal(c)))

    def test_resealed_authority_escalation_rejected(self):
        c = copy.deepcopy(self.records[0]); c['coMeta']['authority'] = 'ALL'
        self.reject('AUTHORITY_BOUNDARY_BROKEN', lambda: verify_capsule(seal(c)))

    def test_resealed_trainability_escalation_rejected(self):
        c = copy.deepcopy(self.records[0]); c['coMetaTrainable']['state'] = 'LEARN_UNBOUNDED'
        self.reject('TRAINABILITY_BOUNDARY_BROKEN', lambda: verify_capsule(seal(c)))

    def test_resealed_scope_mismatch_rejected(self):
        c = copy.deepcopy(self.records[0]); c['coSHAT']['scope'] = 'WHOLE_SELF_HASH'
        self.reject('INVALID_HASH_SCOPE', lambda: verify_capsule(seal(c)))

    def test_resealed_false_partner_links_rejected(self):
        c = copy.deepcopy(self.records[0]); c['coValence']['partner_ids'] = ['bogus1', 'bogus2']
        self.reject('UNQUALIFIED_OR_MISSING_PARTNERS', lambda: verify_capsule(seal(c)))

    def test_resealed_false_domain_rejected(self):
        c = copy.deepcopy(self.records[0]); c['coValence']['failure_domain'] = 'shared'
        self.reject('UNQUALIFIED_OR_MISSING_PARTNERS', lambda: verify_capsule(seal(c)))

    def test_resealed_version_rewrite_rejected(self):
        c = copy.deepcopy(self.records[0]); c['coObject']['version'] = 'r1'
        self.reject('ASSET_IDENTITY_MISMATCH', lambda: verify_capsule(seal(c)))

    def test_resealed_source_digest_conflict_rejected(self):
        c = copy.deepcopy(self.records[0]); c['coSHAT']['source_payload_sha256'] = '0' * 64
        self.reject('SOURCE_VERSION_CONFLICT', lambda: reconstruct([seal(c), self.records[1]]))

    def test_resealed_source_length_conflict_rejected(self):
        c = copy.deepcopy(self.records[0]); c['recovery']['original_size'] += 1
        self.reject('SOURCE_VERSION_CONFLICT', lambda: reconstruct([seal(c), self.records[1]]))

    def test_resealed_wrong_threshold_rejected(self):
        c = copy.deepcopy(self.records[0]); c['recovery']['threshold_k'] = 1
        self.reject('INVALID_RECOVERY_MODEL', lambda: verify_capsule(seal(c)))

    def test_missing_embedded_bytes_rejected(self):
        c = copy.deepcopy(self.records[0]); c.pop('fragment_base64')
        self.reject('INVALID_CAPSULE_FIELDS', lambda: verify_capsule(c))

    def test_invalid_base64_rejected(self):
        c = copy.deepcopy(self.records[0]); c['fragment_base64'] = '@@@'
        self.reject('INVALID_EMBEDDED_FRAGMENT', lambda: verify_capsule(seal(c)))

    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'capsule.coasset.json'
            p.write_text('{"schema":"x","schema":"y"}', encoding='ascii')
            self.reject('DUPLICATE_JSON_KEY', lambda: read_capsule(p))

    def test_wrong_schema_rejected(self):
        c = copy.deepcopy(self.records[0]); c['schema'] = 'wrong'
        self.reject('INVALID_SCHEMA', lambda: verify_capsule(seal(c)))

    def test_extra_unreviewed_field_rejected(self):
        c = copy.deepcopy(self.records[0]); c['device_admin'] = True
        self.reject('INVALID_CAPSULE_FIELDS', lambda: verify_capsule(seal(c)))

    def test_no_authenticity_claim(self):
        self.assertIn('SELF_HASH_NE_AUTHENTICITY', NONCLAIMS)
        self.assertIn('DECLARED_DOMAINS_NE_INDEPENDENT_PROVIDERS', NONCLAIMS)
        for c in self.records:
            self.assertEqual(c['coValence']['independence'], 'DECLARED_NOT_VERIFIED')
            self.assertEqual(c['coMeta']['effect'], 'NONE')

    def test_sha256_verifies_bytes_not_future_files(self):
        for c in self.records:
            self.assertEqual(c['coSHAT']['source_payload_sha256'], sha(PAYLOAD))
            self.assertEqual(len(c['coSHAT']['envelope_sha256']), 64)

    def test_canonical_json_roundtrip(self):
        c = self.records[0]
        self.assertEqual(json.loads(canonical_bytes(c)), c)


if __name__ == '__main__':
    unittest.main()
