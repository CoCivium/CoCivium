import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from copre_path_query_r0 import GRAPH, discover, index_graph

class CoPreOmniQueryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph=json.loads(GRAPH.read_text(encoding="utf-8"))

    def test_existing_graph_integrity(self):
        f,r=index_graph(self.graph)
        self.assertGreater(len(f),10)
        self.assertEqual(set(f),set(r))

    def test_forward_discovery(self):
        x=discover(self.graph,"copre-entry","copre-package",direction="forward")
        self.assertEqual(x["path"],["copre-entry","copre-package"])

    def test_reverse_is_navigable_without_reciprocal_authority(self):
        x=discover(self.graph,"copre-entry","copre-draft",direction="reverse")
        self.assertEqual(x["status"],"NAVIGABLE_SOURCE_POINTER_ONLY")
        self.assertFalse(x["authority_granted"])
        self.assertFalse(x["recipient_ack"])
        self.assertFalse(x["source_verification"])

    def test_cross_audience_route_is_bounded(self):
        x=discover(self.graph,"mindspace","dual-projection",max_hops=8)
        self.assertEqual(x["status"],"NAVIGABLE_SOURCE_POINTER_ONLY")
        self.assertLessEqual(x["hops"],8)
        self.assertFalse(x["integration"])

    def test_quiet_hold_on_zero_budget(self):
        x=discover(self.graph,"copre-entry","retro-protocol",max_hops=0)
        self.assertEqual(x["status"],"HELD_NO_ROUTE_WITHIN_BUDGET")
        self.assertIsNone(x["path"])

    def test_invalid_node_is_not_auto_created(self):
        with self.assertRaisesRegex(ValueError,"UNKNOWN_NODE"):
            discover(self.graph,"copre-entry","future-spooky-node")

    def test_reject_dangling(self):
        o=copy.deepcopy(self.graph)
        o["nodes"][0]["relations"].append("missing-private-thing")
        with self.assertRaisesRegex(ValueError,"DANGLING_GRAPH_LINK"):
            index_graph(o)

    def test_reject_duplicate_id(self):
        o=copy.deepcopy(self.graph)
        o["nodes"].append(copy.deepcopy(o["nodes"][0]))
        with self.assertRaisesRegex(ValueError,"INVALID_OR_DUPLICATE_NODE_ID"):
            index_graph(o)

    def test_bounded_budget(self):
        with self.assertRaisesRegex(ValueError,"INVALID_TRAVERSAL"):
            discover(self.graph,"copre-entry","copre-package",max_hops=999)

    def test_reject_direction_injection(self):
        with self.assertRaisesRegex(ValueError,"INVALID_TRAVERSAL"):
            discover(self.graph,"copre-entry","copre-package",direction="authorize")

    def test_source_unchanged(self):
        prior=copy.deepcopy(self.graph)
        discover(self.graph,"copre-entry","copre-package")
        self.assertEqual(prior,self.graph)

    def test_no_automatic_effect_or_ack_even_on_same_node(self):
        x=discover(self.graph,"copre-entry","copre-entry")
        self.assertEqual(x["path"],["copre-entry"])
        self.assertFalse(x["recipient_ack"])
        self.assertFalse(x["integration"])
        self.assertFalse(x["authority_granted"])

if __name__=="__main__":
    unittest.main()
