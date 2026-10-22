#!/usr/bin/env python3
"""Adversarial checks of declared readback consistency; no live effects."""
import copy
import json
import unittest
from pathlib import Path
from validate_coresearch_evidence_r0 import validate
ROOT = Path(__file__).resolve().parents[1]

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.d = json.loads((ROOT / 'examples/coresearch-recovery.example.json').read_text())
    def reject(self, code):
        with self.assertRaisesRegex(ValueError, code):
            validate(self.d, require_recovery=True)
    def test_legacy_compatible_but_strict_rejects(self):
        legacy = json.loads((ROOT / 'examples/coresearch-evidence-v0.1.example.json').read_text())
        validate(legacy)
        with self.assertRaisesRegex(ValueError, 'RECOVERY_REQUIRED'):
            validate(legacy, True)
    def test_unresolved_search_is_valid(self):
        validate(self.d, True)
    def test_search_miss_cannot_be_absence(self):
        self.d['research_recovery']['finding'] = 'SCOPED_ABSENCE'
        self.reject('ABSENCE_REQUIRES_INVENTORY')
    def test_observer_failure_cannot_be_absence(self):
        self.d['research_recovery'].update(finding='SCOPED_ABSENCE', basis='OBSERVER_UNAVAILABLE')
        self.reject('ABSENCE_REQUIRES_INVENTORY')
    def test_scoped_inventory_can_support_absence(self):
        r = self.d['research_recovery']
        r.update(finding='SCOPED_ABSENCE', basis='AUTHORITATIVE_BOUNDED_INVENTORY')
        r['inventory'] = dict(r['sources_read'][0], coverage='Synthetic exact one-record set only')
        validate(self.d, True)
        r['inventory']['ref'] = 'fixture:not-read'
        self.reject('ABSENCE_INVENTORY_NOT_READ')
    def test_inventory_version_must_match_read(self):
        r = self.d['research_recovery']
        r.update(finding='SCOPED_ABSENCE', basis='AUTHORITATIVE_BOUNDED_INVENTORY')
        r['inventory'] = dict(r['sources_read'][0], version='unread-v2', coverage='fixture')
        self.reject('ABSENCE_INVENTORY_NOT_READ')
    def test_extraordinary_gate_can_be_required(self):
        self.d.pop('extraordinary_gate')
        with self.assertRaisesRegex(ValueError, 'EXTRAORDINARY_GATE_REQUIRED'):
            validate(self.d, True, True)
    def test_read_version_required(self):
        self.d['research_recovery']['sources_read'][0]['version'] = ''
        self.reject('RECOVERY_SOURCE_BINDING')
    def test_resource_must_be_inspected(self):
        self.d['research_recovery']['resource_options'][0]['inspection'] = 'LISTED'
        self.reject('SELECTED_RESOURCE_NOT_INSPECTED')
    def test_resource_reason_required(self):
        self.d['research_recovery']['resource_options'][0]['reason'] = ''
        self.reject('RESOURCE_REASON_AND_COST')
    def test_reuse_option_required(self):
        self.d['research_recovery']['resource_options'][0]['id'] = 'new-worker'
        self.reject('RESOURCE_REUSE_OPTION')
    def test_retention_pointer_required(self):
        self.d['research_recovery']['continuation']['state'] = 'RECORDED'
        self.reject('CONTINUATION_EXACT_POINTER')
    def test_retention_unavailable_must_be_explicit(self):
        self.d['research_recovery']['continuation']['reason'] = ''
        self.reject('CONTINUATION_UNAVAILABLE_REASON')
    def test_candidate_names_missing_verification(self):
        self.d['extraordinary_gate']['missing_verification'] = []
        self.reject('EXTRAORDINARY_CANDIDATE_GAPS')
    def test_promotion_rejects_each_missing_check(self):
        g = self.d['extraordinary_gate']
        g.update(disposition='PROMOTION_REQUESTED', receipts=['fixture:receipt'], uncertainty='All evidence is synthetic, no scientific promotion established.')
        names = ('primary_observations','independent_corroboration','prior_art_review','adversarial_review','replication','prospective_falsifiers','domain_verification')
        for name in names:
            g[name] = {'state':'PASS','source_refs':['fixture:evidence'],'observed_at':'2026-10-22T00:00:00Z'}
        g['domain_verification']['verifier'] = 'fixture:verifier'
        validate(self.d, True)
        for name in names:
            with self.subTest(name=name):
                item = g.pop(name)
                self.reject('EXTRAORDINARY_CHECK_' + name.upper())
                g[name] = item
    def test_verifier_required(self):
        g = self.d['extraordinary_gate']
        g.update(disposition='PROMOTION_REQUESTED', receipts=['fixture:receipt'], uncertainty='synthetic')
        for name in ('primary_observations','independent_corroboration','prior_art_review','adversarial_review','replication','prospective_falsifiers','domain_verification'):
            g[name] = {'state':'PASS','source_refs':['fixture:evidence'],'observed_at':'2026-10-22T00:00:00Z'}
        self.reject('EXTRAORDINARY_VERIFIER')
    def test_no_mutation_during_validation(self):
        before = copy.deepcopy(self.d)
        validate(self.d, True)
        self.assertEqual(before, self.d)
    def test_malformed_recovery_is_rejected(self):
        self.d['research_recovery'] = 'pass'
        self.reject('RECOVERY_OBJECT')

if __name__ == '__main__':
    unittest.main()
