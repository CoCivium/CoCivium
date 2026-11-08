"""Bounded synthetic CoGoldenBraid relation and falsifier tests."""
import unittest
from recursive_braid import Edge, Node, query, compare_fixture


class RecursiveBraidTest(unittest.TestCase):
    def test_two_hops_find_unrepresented_need(self):
        observed = compare_fixture()
        self.assertFalse(observed["flat_retrieves_unheard_need"])
        self.assertTrue(observed["braid_retrieves_unheard_need"])
        self.assertFalse(observed["braid_false_positive"])
        self.assertFalse(observed["braid"]["runtime_authority"])

    def test_intentionally_false_edge_is_not_truth(self):
        negative = compare_fixture(include_false_edge=True)
        self.assertTrue(negative["braid_false_positive"])
        self.assertEqual(negative["braid"]["evidence_warning"],
                         "REACHABILITY_NOT_CAUSATION_OR_VALUE")

    def test_cycle_terminates(self):
        nodes = [Node("a", "supply", "proof:a"), Node("b", "demand", "proof:b")]
        edges = [Edge("a", "b", "enables", "proof:e"),
                 Edge("b", "a", "needs", "proof:f")]
        result = query(nodes, edges, roots={"a"}, max_depth=3)
        self.assertEqual(result["nodes"], ["a", "b"])

    def test_unbound_relation_holds(self):
        with self.assertRaisesRegex(ValueError, "UNBOUND"):
            query([Node("a", "supply", "s")],
                  [Edge("a", "missing", "enables", "s")],
                  roots={"a"}, max_depth=1)

    def test_invalid_depth_and_budget_hold(self):
        n = [Node("a", "supply", "s")]
        for depth, budget in ((-1, 3), (4, 3), (1, 0), (1, 100)):
            with self.subTest(depth=depth, budget=budget):
                with self.assertRaisesRegex(ValueError, "BOUNDED"):
                    query(n, [], roots={"a"}, max_depth=depth, budget=budget)

    def test_missing_provenance_holds(self):
        with self.assertRaisesRegex(ValueError, "INVALID_NODE"):
            query([Node("a", "supply", "")], [], roots={"a"}, max_depth=1)

    def test_duplicate_nodes_hold(self):
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            query([Node("a", "supply", "s"), Node("a", "demand", "s")],
                  [], roots={"a"}, max_depth=1)


if __name__ == "__main__":
    unittest.main()
