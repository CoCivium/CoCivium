"""CoOmniPath guards: bidirectional discoverability != inferred semantics."""
import unittest
from co_omnipath_r0 import load_registry, neighbors, hypothesis_link


class CoOmniPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = load_registry()

    def test_outbound_follows_declared_relation(self):
        found = neighbors(self.r, "copre", directions=("out",), max_hops=1)
        self.assertIn("copre_machine", {x["node_id"] for x in found["paths"]})

    def test_inbound_finds_reference_without_reversing_predicate(self):
        found = neighbors(self.r, "copre_machine", directions=("in",), max_hops=1)
        entry = next(x for x in found["paths"] if x["node_id"] == "copre")
        trail = entry["relation_trail"][0]
        self.assertEqual(trail["source_predicate"], "MACHINE_PROJECTION")
        self.assertEqual(trail["traversal_role"], "INBOUND_REFERENCE_ONLY")

    def test_both_directions_reach_historical_contributor(self):
        found = neighbors(self.r, "copre", directions=("in", "out"), max_hops=1)
        self.assertIn("retro", {x["node_id"] for x in found["paths"]})

    def test_two_hops_reach_developer_feedback(self):
        found = neighbors(self.r, "copre", max_hops=2)
        self.assertIn("feedback", {x["node_id"] for x in found["paths"]})

    def test_unknown_seed_is_held(self):
        self.assertEqual(neighbors(self.r, "made-up")["status"], "UNKNOWN_SEED")

    def test_no_hops_is_no_reach(self):
        self.assertEqual(neighbors(self.r, "copre", max_hops=0)["paths"], [])

    def test_bounded_results_disclose_possible_unvisited(self):
        found = neighbors(self.r, "copre", max_hops=3, max_results=1)
        self.assertEqual(len(found["paths"]), 1)
        self.assertEqual(found["unvisited"], "POSSIBLE")

    def test_scope_fence_works_on_destination(self):
        altered = dict(self.r)
        altered["nodes"] = [dict(n, scope="RESTRICTED") if n["id"] == "thumb"
                            else n for n in self.r["nodes"]]
        found = neighbors(altered, "copre")
        self.assertNotIn("thumb", {x["node_id"] for x in found["paths"]})

    def test_scope_fence_works_on_source(self):
        altered = dict(self.r)
        altered["nodes"] = [dict(n, scope="RESTRICTED") if n["id"] == "copre"
                            else n for n in self.r["nodes"]]
        self.assertEqual(neighbors(altered, "copre")["status"], "SCOPE_HELD")

    def test_invalid_direction_rejected(self):
        with self.assertRaises(ValueError):
            neighbors(self.r, "copre", directions=("telepathy",))

    def test_source_graph_never_claims_receiver_pickup(self):
        found = neighbors(self.r, "copre")
        self.assertFalse(found["receiver_pickup_proven"])
        self.assertFalse(found["semantic_integration_proven"])
        self.assertFalse(found["full_history_covered"])
        self.assertTrue(all(not x["verified_receiver_accepted"] for x in found["paths"]))

    def test_hypothesis_must_have_falsifier(self):
        h = hypothesis_link("CoTime", "G_dSide", rationale="oscillatory bias",
                            falsifier="")
        self.assertEqual(h["status"], "HELD")

    def test_gdside_hypothesis_not_auto_elevated(self):
        h = hypothesis_link("CoTime", "G_dSide", rationale="speculative phase coupling",
                            falsifier="controls explain observations")
        self.assertEqual(h["kind"], "HYPOTHESIS")
        self.assertFalse(h["promote_to_verified_edge"])
        self.assertEqual(h["authority"], "NONE")


if __name__ == "__main__":
    unittest.main()
