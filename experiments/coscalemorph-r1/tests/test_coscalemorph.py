"""CoScaleMorph R0 release gates. Isolated deterministic source only."""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from coscalemorph import ScaleError, canonical, planning_frontier, reduce_view, rehydrate, sha, validate_source

SOURCE=(ROOT/'source/CoMapPulse_graph_R0.json').read_bytes()
GRAPH=json.loads(SOURCE)


class ScaleTests(unittest.TestCase):
    def setUp(self):
        self.capsule=reduce_view(SOURCE,visible_budget=2)

    def rejects(self, code, fn):
        with self.assertRaises(ScaleError) as raised: fn()
        self.assertEqual(str(raised.exception),code)

    def test_source_hash_is_pinned(self):
        self.assertEqual(sha(SOURCE),'4eddc49ef5902673fa22af5ef969b60a74bbd3153bd5b493638c00230d963f27')

    def test_schema_and_public_policy(self):
        self.assertEqual(validate_source(SOURCE)['source_policy'],'PUBLIC_ONLY__NO_SECRETS__NO_REMOTE_EFFECT')

    def test_orb_is_smaller_than_source(self):
        self.assertLess(len(canonical(self.capsule)),len(SOURCE))

    def test_three_scales_preserve_source_identity(self):
        views=[reduce_view(SOURCE,visible_budget=n,view=view) for n,view in ((1,'ORB'),(3,'MAP'),(9,'DETAIL'))]
        self.assertEqual({v['source_sha256'] for v in views},{sha(SOURCE)})
        self.assertEqual([v['omitted_node_count'] for v in views],[8,6,0])

    def test_rehydration_exact_bytes(self):
        self.assertEqual(rehydrate(self.capsule,SOURCE),SOURCE)

    def test_rehydration_every_scale(self):
        for n in (1,3,9):
            with self.subTest(n=n):
                c=reduce_view(SOURCE,visible_budget=n)
                self.assertEqual(rehydrate(c,SOURCE),SOURCE)

    def test_no_source_no_restore(self):
        self.rejects('SOURCE_NOT_AVAILABLE',lambda: rehydrate(self.capsule,None))

    def test_tamper_capsule_rejected(self):
        c=dict(self.capsule); c['omitted_node_count']=987
        self.rejects('TAMPERED_CAPSULE',lambda: rehydrate(c,SOURCE))

    def test_mismatched_source_rejected(self):
        self.rejects('SOURCE_MISMATCH',lambda: rehydrate(self.capsule,SOURCE+b' '))

    def test_authority_revoked(self):
        self.rejects('AUTHORITY_GATE',lambda: rehydrate(self.capsule,SOURCE,authorization='NONE'))

    def test_erasure_gate_even_if_bytes_available(self):
        self.rejects('ERASURE_OR_RETENTION_GATE',lambda: rehydrate(self.capsule,SOURCE,tombstone=True))

    def test_lossy_summary_cannot_restore(self):
        c=dict(self.capsule); c['reduction_type']='LOSSY_SUMMARY_ONLY';c['capsule_sha256']=sha(canonical({k:v for k,v in c.items() if k!='capsule_sha256'}))
        self.rejects('INHERENTLY_LOSSY_OR_UNSUPPORTED',lambda: rehydrate(c,SOURCE))

    def test_bad_source_policy_rejected(self):
        x=dict(GRAPH);x['source_policy']='PRIVATE'
        self.rejects('SOURCE_NOT_PUBLIC_SAFE',lambda: reduce_view(canonical(x),visible_budget=1))

    def test_nonpublic_node_rejected(self):
        x=json.loads(SOURCE);x['nodes'][2]['privacy']='PRIVATE'
        self.rejects('NONPUBLIC_NODE_BLOCKED',lambda: reduce_view(canonical(x),visible_budget=2))

    def test_forged_receiver_ack_rejected(self):
        x=json.loads(SOURCE);x['edges'][0]['ack']='ACK_VERIFIED'
        self.rejects('UNVERIFIED_ACK_CLAIM',lambda: reduce_view(canonical(x),visible_budget=2))

    def test_missing_edge_endpoint(self):
        x=json.loads(SOURCE);x['edges'][0]['to']='UNREAL'
        self.rejects('EDGE_ENDPOINT_MISSING',lambda: reduce_view(canonical(x),visible_budget=2))

    def test_source_reordered_same_count_rejected(self):
        x=json.loads(SOURCE);x['nodes'][0],x['nodes'][1]=x['nodes'][1],x['nodes'][0]
        self.rejects('SOURCE_MISMATCH',lambda: rehydrate(self.capsule,canonical(x)))

    def test_bad_budget_rejected(self):
        for budget in (0,10,True,1.2):
            with self.subTest(budget=budget): self.rejects('BAD_VIEW_BUDGET',lambda: reduce_view(SOURCE,visible_budget=budget))

    def test_no_effect_and_no_ack(self):
        self.assertEqual(self.capsule['worker_processes_spawned'],0)
        self.assertEqual(self.capsule['receiver_ack'],'NOT_OBSERVED')

    def test_million_logical_one_active_budget(self):
        p=planning_frontier(10**12,10**6,max_workers=2,actual_tasks=10)
        self.assertEqual(p['eligible_worker_ceiling'],2)
        self.assertEqual(p['actual_workers_spawned_by_planner'],0)
        self.assertEqual(p['not_materialized_slots'],10**12-2)

    def test_no_external_effect_authority(self):
        self.rejects('AUTHORITY_GATE',lambda: planning_frontier(100,4,authority='BROADCAST'))

    def test_bound_workers(self):
        for width in (0,5,10**6):
            with self.subTest(width=width):
                if width==0:self.rejects('BAD_CEILING',lambda:planning_frontier(100,5,max_workers=width))
                elif width==5:self.rejects('BAD_CEILING',lambda:planning_frontier(100,5,max_workers=width))
                else:self.assertEqual(planning_frontier(100,width,max_workers=2)['eligible_worker_ceiling'],2)

    def test_reject_duplicate_json_keys(self):
        self.rejects('SOURCE_JSON_INVALID',lambda:validate_source(b'{"schema":1,"schema":2}'))

if __name__=='__main__': unittest.main()
