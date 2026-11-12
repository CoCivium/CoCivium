#!/usr/bin/env python3
"""Isolated tests for an opt-in public CoMap evidence overlay (not X2)."""
import copy
import json
import unittest
from CoMapCoLocalConsumerR1 import build_projection, blob_sha1, validate_ci, SEED_NODE, CI_NODE, safe_read


def fake_base():
    ids = ['view:CoMap+', 'domain:CoNodeMesh+/GRAIL+', 'domain:CoAutoEvo+/CoEvo+']
    ids += [f'other:{i}' for i in range(53)]
    return {
        'schema': 'CoAll.CoMapProjection.R0',
        'state': 'PUBLIC_SOURCE_BOUND_PROJECTION_NOT_CANON_OR_RUNTIME',
        'sources': [{'id': 'existing:one', 'url': 'https://example.org'}],
        'nodes': [{'id': s, 'label': s, 'kind': 'domain', 'status': 'SOURCE_REGISTERED'} for s in ids],
        'edges': [{'id': 'e'+str(i), 'from': ids[i%56], 'to': ids[(i+1)%56], 'relation': 'REGISTERED_REPOSITORY', 'source':'existing:one'} for i in range(1,62)],
        'rails': ['MAP_NE_CANON'],
        'coverage': {'included': 'synthetic'},
    }


def fake_ci():
    return {
        'schema': 'CoAll.CoLocal.CurrentnessSourceCIReceipt.R0',
        'classification': 'PUBLIC_SOURCE_CI_EXECUTION_RECEIPT_NOT_DEVICE_RUNTIME',
        'state': 'PASS_SOURCE_REGRESSION_ONLY',
        'source': {'commit_sha': '995c10c96e91dc8fa7e4e7d26c1de2c3b462046b', 'evaluator_git_blob_sha1':'49089f20a3871a1315f47490d6e237320df0114b'},
        'execution': {'run_id':43128120567,'conclusion':'success','tests_passed':15,'tests_failed':0},
        'independent_review': {'independent_receiver_readproof': False},
        'gates': {'X2_LIVE_RECEIVER':'UNVERIFIED','PRODUCTION_GENERATOR_ADOPTION':'NOT_PERFORMED'},
    }


class TestConsumer(unittest.TestCase):
    def test_build_returns_opt_in_successor_without_editing_base(self):
        base=fake_base(); original=copy.deepcopy(base)
        got=build_projection(base,fake_ci())
        self.assertEqual((len(got['nodes']),len(got['edges'])),(58,66))
        self.assertEqual(base,original)
        self.assertEqual(got['nodes'][:56],base['nodes'])
        self.assertEqual(got['edges'][:61],base['edges'])
    def test_two_new_documents_are_not_runtime(self):
        got=build_projection(fake_base(),fake_ci())
        added={n['id']:n for n in got['nodes'][56:]}
        self.assertEqual(set(added),{SEED_NODE,CI_NODE})
        self.assertIn('NOT_RECEIVER',added[CI_NODE]['status'])
        self.assertFalse(got['overlay_evidence']['external_receiver_ack'])
        self.assertEqual(got['overlay_evidence']['x2_runtime'],'UNVERIFIED')
    def test_relations_resolve_and_are_bounded(self):
        got=build_projection(fake_base(),fake_ci())
        nodes={n['id'] for n in got['nodes']}
        self.assertEqual(len({e['id'] for e in got['edges']}),66)
        self.assertTrue(all(e['from'] in nodes and e['to'] in nodes for e in got['edges']))
        self.assertTrue(all('CANON' not in e['state'] and 'RUNTIME' not in e['state'] for e in got['edges'][61:]))
    def test_deterministic(self):
        self.assertEqual(json.dumps(build_projection(fake_base(),fake_ci()),sort_keys=True),json.dumps(build_projection(fake_base(),fake_ci()),sort_keys=True))
    def test_no_private_paths_or_user_content(self):
        serialized=json.dumps(build_projection(fake_base(),fake_ci()))
        for term in ('D:\\CoCivium','libfile_','file_00000000','@inseed.com','receiver_ack": true'):
            self.assertNotIn(term,serialized)
    def test_unknown_evidence_schema_holds(self):
        ci=fake_ci();ci['schema']='OTHER'
        with self.assertRaisesRegex(ValueError,'HOLD_UNKNOWN_RECEIPT_SCHEMA'):validate_ci(ci)
    def test_ci_success_ne_x2_pass(self):
        ci=fake_ci();ci['state']='PASS_X2_RUNTIME'
        with self.assertRaisesRegex(ValueError,'HOLD_UNQUALIFIED_CI_STATE'):build_projection(fake_base(),ci)
    def test_ack_relabel_holds(self):
        ci=fake_ci();ci['independent_review']['independent_receiver_readproof']=True
        with self.assertRaisesRegex(ValueError,'HOLD_ACK_INFERENCE'):build_projection(fake_base(),ci)
    def test_runtime_claim_holds(self):
        ci=fake_ci();ci['gates']['X2_LIVE_RECEIVER']='PASS'
        with self.assertRaisesRegex(ValueError,'HOLD_RUNTIME_CLAIM'):build_projection(fake_base(),ci)
    def test_run_identity_mismatch_holds(self):
        ci=fake_ci();ci['execution']['run_id']=5
        with self.assertRaisesRegex(ValueError,'HOLD_CI_RUN_UNQUALIFIED'):build_projection(fake_base(),ci)
    def test_counts_changed_holds(self):
        base=fake_base();base['nodes'].pop()
        with self.assertRaisesRegex(ValueError,'HOLD_BASE_COVERAGE'):build_projection(base,fake_ci())
    def test_duplicate_node_holds(self):
        base=fake_base();base['nodes'][4]['id']=base['nodes'][3]['id']
        with self.assertRaisesRegex(ValueError,'HOLD_BASE_COLLISION'):build_projection(base,fake_ci())
    def test_broken_edge_holds(self):
        base=fake_base();base['edges'][0]['to']='missing:target'
        with self.assertRaisesRegex(ValueError,'HOLD_BAD_BASE_EDGE'):build_projection(base,fake_ci())
    def test_pinned_blob_hash(self):
        self.assertEqual(blob_sha1(b'hi'),'32f95c0d1244a78b2be1bab8de17906fabb2c4a8')
    def test_bad_blob_holds(self):
        with self.assertRaises((ValueError,FileNotFoundError)):
            safe_read('/tmp','definitely_nonexistent_file','0'*40)


if __name__=='__main__':unittest.main()
