#!/usr/bin/env python3
"""Adversarial CoAsset valency and source loss/overlap recovery test."""
import base64
import copy
import json
import unittest
from pathlib import Path
from coasset_valency_recovery_r0 import adjacency, orphan_nodes, encode_recovery_bundle, recover_from_partners

ROOT = Path(__file__).resolve().parents[1]
GRAPH = json.loads((ROOT / 'ai/repo-field-projection-graph-r0.json').read_text('utf-8'))
CONTENT = b'\x00CoLex history 2026\nCoTermable and CoMeaning\xff' * 3 + b'!'
CARRIERS = [{'id': f'fixture:partner-{i}', 'failure_domain': f'synthetic-{i}'} for i in range(3)]

class Tests(unittest.TestCase):
    def setUp(self):
        self.b = encode_recovery_bundle(CONTENT, CARRIERS)
    def failcode(self, code, action):
        with self.assertRaisesRegex(ValueError, code):
            action()
    def test_graph_nodes_connected_for_scoped_sample(self):
        self.assertEqual(orphan_nodes(GRAPH), [])
        self.assertEqual(len(adjacency(GRAPH)), 22)
    def test_reverse_navigation_not_reverse_fact(self):
        index = adjacency(GRAPH)
        self.assertEqual(len(index['CoAll']['in']), 21)
        self.assertEqual(index['CoAll']['out'], [])
        self.assertEqual(len(index['CoCivium/CoCivium']['out']), 1)
        self.assertEqual(index['CoCivium/CoCivium']['in'], [])
    def test_missing_relation_exposes_orphan(self):
        g = copy.deepcopy(GRAPH)
        g['relations'] = [e for e in g['relations'] if e['subject'] != 'CoCivium/CoSteward']
        self.assertIn('CoCivium/CoSteward', orphan_nodes(g))
    def test_missing_target_fails(self):
        g = copy.deepcopy(GRAPH)
        g['relations'][0]['object'] = 'unknown:asset'
        self.failcode('DANGLING_LINK', lambda: adjacency(g))
    def test_selflink_fails_as_only_partner(self):
        g = copy.deepcopy(GRAPH)
        g['relations'][0]['object'] = g['relations'][0]['subject']
        self.failcode('SELF_LINK', lambda: adjacency(g))
    def test_duplicate_edge_fails(self):
        g = copy.deepcopy(GRAPH)
        g['relations'].append(copy.deepcopy(g['relations'][0]))
        self.failcode('DUPLICATE_RELATION', lambda: adjacency(g))
    def test_rebuild_with_data_halves_without_original(self):
        self.assertEqual(recover_from_partners(self.b,['data0','data1']),CONTENT)
    def test_rebuild_without_data0(self):
        self.assertEqual(recover_from_partners(self.b,['data1','xor_parity']),CONTENT)
    def test_rebuild_without_data1(self):
        self.assertEqual(recover_from_partners(self.b,['data0','xor_parity']),CONTENT)
    def test_rebuild_with_all(self):
        self.assertEqual(recover_from_partners(self.b,['data0','data1','xor_parity']),CONTENT)
    def test_one_shard_insufficient(self):
        self.failcode('INSUFFICIENT_SURVIVORS', lambda: recover_from_partners(self.b,['data0']))
    def test_pointer_only_insufficient(self):
        x = copy.deepcopy(self.b)
        for item in x['shards'].values(): item.pop('base64')
        self.failcode('INVALID_SHARD_ENCODING', lambda: recover_from_partners(x,['data0','data1']))
    def test_one_corrupt_shard_fails(self):
        x = copy.deepcopy(self.b)
        x['shards']['data1']['base64'] = base64.b64encode(b'X'*len(base64.b64decode(x['shards']['data1']['base64']))).decode('ascii')
        self.failcode('SHARD_HASH_MISMATCH', lambda: recover_from_partners(x,['data0','data1']))
    def test_modified_manifest_hash_fails(self):
        x = copy.deepcopy(self.b)
        x['original_sha256'] = '0' * 64
        self.failcode('RECOVERY_HASH_MISMATCH', lambda: recover_from_partners(x,['data0','data1']))
    def test_incorrect_length_fails(self):
        x = copy.deepcopy(self.b)
        x['original_size'] -= 1
        self.failcode('RECOVERY_HASH_MISMATCH', lambda: recover_from_partners(x,['data0','data1']))
    def test_duplicate_failure_domain_fails_encode(self):
        c = copy.deepcopy(CARRIERS)
        c[2]['failure_domain'] = c[0]['failure_domain']
        self.failcode('CARRIER_ID_OR_FAILURE_DOMAIN_NOT_DIVERSE', lambda: encode_recovery_bundle(CONTENT,c))
    def test_duplicate_survivor_role_fails(self):
        self.failcode('DUPLICATE_ROLE', lambda: recover_from_partners(self.b,['data0','data0']))
    def test_corrupted_parity_fails(self):
        x = copy.deepcopy(self.b)
        x['shards']['xor_parity']['base64'] = base64.b64encode(b'\x00'*len(base64.b64decode(x['shards']['xor_parity']['base64']))).decode('ascii')
        self.failcode('SHARD_HASH_MISMATCH', lambda: recover_from_partners(x,['data0','data1','xor_parity']))
    def test_unknown_model_rejected(self):
        x = copy.deepcopy(self.b)
        x['recovery_threshold']['k'] = 1
        self.failcode('UNKNOWN_RECOVERY_MODEL', lambda: recover_from_partners(x,['data0','data1']))
    def test_empty_payload(self):
        b=encode_recovery_bundle(b'',CARRIERS)
        self.assertEqual(recover_from_partners(b,['data1','xor_parity']),b'')
    def test_single_byte(self):
        b=encode_recovery_bundle(b'Q',CARRIERS)
        self.assertEqual(recover_from_partners(b,['data1','xor_parity']),b'Q')
    def test_no_source_mutation(self):
        original=copy.deepcopy(self.b)
        recover_from_partners(self.b,['data1','xor_parity'])
        self.assertEqual(self.b,original)
    def test_no_runtime_claim(self):
        self.assertEqual(self.b['carrier_independence'],'DECLARED_ONLY_NOT_PROVEN')
        self.assertIn('RECONSTRUCTION_NE_RECEIVER_ACK_OR_CANON',self.b['nonclaims'])
    def test_source_is_synthetic(self):
        self.assertEqual(self.b['authority'],'READ_ONLY_SYNTHETIC_TEST')

if __name__=='__main__':
    unittest.main()
