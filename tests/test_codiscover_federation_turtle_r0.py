"""CoFed/CoTurtle/CoInverse synthetic discovery contract tests.

All statements are manifest fixtures, NOT live federation membership, peer
consent, remote source readback or security/privacy certification.
"""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "CoDiscoverFederationTurtleProbeR0.py"
spec = importlib.util.spec_from_file_location("codiscover_fedturtle", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def view(depth=3, limit=12, root="fed:root", graph=None):
    return mod.discover(mod.fixture() if graph is None else graph,
                        root, depth, limit)


class CoFedTurtleInverseTests(unittest.TestCase):
    def test_01_root_is_federation(self):
        self.assertEqual(view()["nodes"][0]["class"], "FEDERATION")

    def test_02_nested_federation_is_visible(self):
        self.assertIn("fed:nested", {x["id"] for x in view()["nodes"]})

    def test_03_substrate_inside_nested_federation(self):
        nodes = {x["id"]: x for x in view()["nodes"]}
        self.assertEqual(nodes["substrate:edge"]["class"], "SUBSTRATE")
        self.assertEqual(nodes["substrate:edge"]["minimum_discovery_hops"], 3)

    def test_04_zero_depth_is_root_only(self):
        x = view(depth=0)
        self.assertEqual([n["id"] for n in x["nodes"]], ["fed:root"])
        self.assertEqual(x["edges"], [])

    def test_05_one_hop_excludes_nested(self):
        ids = {n["id"] for n in view(depth=1)["nodes"]}
        self.assertEqual(ids, {"fed:root", "fed:regional",
                               "fed:mirror", "system:local"})

    def test_06_two_hops_includes_nested_not_leaf(self):
        ids = {n["id"] for n in view(depth=2)["nodes"]}
        self.assertIn("fed:nested", ids)
        self.assertNotIn("substrate:edge", ids)

    def test_07_large_depth_is_explicitly_capped(self):
        with self.assertRaisesRegex(mod.Hold, "INVALID_DEPTH_BUDGET"):
            view(depth=9000)

    def test_08_negative_depth_rejected(self):
        with self.assertRaisesRegex(mod.Hold, "INVALID_DEPTH_BUDGET"):
            view(depth=-1)

    def test_09_boolean_depth_rejected(self):
        with self.assertRaisesRegex(mod.Hold, "INVALID_DEPTH_BUDGET"):
            view(depth=True)

    def test_10_small_node_budget_is_held(self):
        x = view(limit=2)
        self.assertTrue(x["budget_held"])
        self.assertEqual(len(x["nodes"]), 2)

    def test_11_invalid_node_budget_rejected(self):
        with self.assertRaisesRegex(mod.Hold, "INVALID_OUTPUT_BUDGET"):
            view(limit=0)

    def test_12_cycle_does_not_loop_or_count_new_system(self):
        ids = [n["id"] for n in view()["nodes"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 6)

    def test_13_two_paths_to_root_not_independent_witnesses(self):
        x = view()
        self.assertEqual(sum(n["id"] == "fed:root" for n in x["nodes"]), 1)
        self.assertEqual(x["actual_independent_failure_domains"], "NOT_TESTED")

    def test_14_private_child_and_its_descendant_are_absent(self):
        public = json.dumps(view(), sort_keys=True)
        self.assertNotIn("system:private", public)
        self.assertNotIn("even-more-private", public)

    def test_15_private_tree_mutation_does_not_change_public_hash(self):
        a = mod.fixture()
        b = deepcopy(a)
        b["nodes"][-1]["source_sha256"] = "b" * 64
        b["nodes"][-2]["edges"].append({
            "to": "fed:root", "relation": "DISCOVERS"})
        self.assertEqual(view(graph=a)["public_view_sha256"],
                         view(graph=b)["public_view_sha256"])

    def test_16_private_edge_removed_does_not_change_public_view(self):
        a = mod.fixture()
        b = deepcopy(a)
        b["nodes"][0]["edges"] = [
            e for e in b["nodes"][0]["edges"]
            if e["to"] != "system:private"]
        self.assertEqual(view(graph=a)["public_view_sha256"],
                         view(graph=b)["public_view_sha256"])

    def test_17_private_root_refused(self):
        with self.assertRaisesRegex(mod.Hold, "ROOT_NOT_PUBLIC"):
            view(root="system:private")

    def test_18_plain_discovery_has_no_inferred_reverse(self):
        edges = view()["edges"]
        e = next(e for e in edges
                 if e["from"] == "fed:root" and e["to"] == "system:local")
        self.assertEqual(e["inverse_evidence"], "REVERSE_NOT_DECLARED")
        self.assertEqual(e["inverse_required_for_reciprocity"], "DISCOVERED_BY")

    def test_19_declared_inversion_still_not_verified(self):
        e = next(e for e in view()["edges"]
                 if e["from"] == "fed:root" and e["to"] == "fed:regional")
        self.assertEqual(e["inverse_evidence"],
                         "REVERSE_DECLARED_ONLY_UNVERIFIED")

    def test_20_explicit_peer_reverse_still_not_consent(self):
        e = next(e for e in view()["edges"]
                 if e["from"] == "fed:root" and e["to"] == "fed:mirror")
        self.assertEqual(e["inverse_evidence"],
                         "REVERSE_DECLARED_ONLY_UNVERIFIED")
        self.assertFalse(e["trust_granted"])
        self.assertFalse(e["effect_authority_granted"])

    def test_21_membership_inverted_relation_never_grants_authority(self):
        edges = view()["edges"]
        e = next(e for e in edges
                 if e["from"] == "fed:regional" and e["to"] == "fed:nested")
        self.assertEqual(e["inverse_required_for_reciprocity"], "MEMBER_OF")
        self.assertEqual(e["inverse_evidence"],
                         "REVERSE_DECLARED_ONLY_UNVERIFIED")
        self.assertFalse(e["membership_granted"])

    def test_22_reverse_view_is_scope_relative(self):
        root_view = {x["id"] for x in view(root="fed:root", depth=1)["nodes"]}
        regional_view = {x["id"] for x in view(root="fed:regional", depth=1)["nodes"]}
        self.assertIn("system:local", root_view)
        self.assertNotIn("system:local", regional_view)
        self.assertIn("fed:root", regional_view)

    def test_23_all_edges_are_visible_public_endpoints(self):
        x = view()
        visible = {n["id"] for n in x["nodes"]}
        self.assertTrue(all(e["from"] in visible and e["to"] in visible
                            for e in x["edges"]))

    def test_24_cannot_use_id_without_source(self):
        g = mod.fixture()
        g["nodes"][0]["source_ref"] = ""
        with self.assertRaisesRegex(mod.Hold, "UNBOUND_SOURCE_REF"):
            view(graph=g)

    def test_25_wrong_source_digest_refused(self):
        g = mod.fixture()
        g["nodes"][0]["source_sha256"] = "claim"
        with self.assertRaisesRegex(mod.Hold, "INVALID_SOURCE_DIGEST"):
            view(graph=g)

    def test_26_duplicate_node_id_refused(self):
        g = mod.fixture()
        g["nodes"].append(deepcopy(g["nodes"][0]))
        with self.assertRaisesRegex(mod.Hold, "DUPLICATE_NODE_ID"):
            view(graph=g)

    def test_27_unknown_edge_target_refused(self):
        g = mod.fixture()
        g["nodes"][0]["edges"].append({
            "to": "fed:nonexistent", "relation": "DISCOVERS"})
        with self.assertRaisesRegex(mod.Hold, "UNKNOWN_EDGE_TARGET"):
            view(graph=g)

    def test_28_duplicate_edge_refused(self):
        g = mod.fixture()
        g["nodes"][0]["edges"].append(deepcopy(g["nodes"][0]["edges"][0]))
        with self.assertRaisesRegex(mod.Hold, "DUPLICATE_EDGE"):
            view(graph=g)

    def test_29_unknown_relation_refused(self):
        g = mod.fixture()
        g["nodes"][0]["edges"][0]["relation"] = "CONTROLS"
        with self.assertRaisesRegex(mod.Hold, "UNKNOWN_EDGE_RELATION"):
            view(graph=g)

    def test_30_node_class_mismatch_refused(self):
        g = mod.fixture()
        g["nodes"][0]["class"] = "SYSTEM"
        with self.assertRaisesRegex(mod.Hold, "NODE_CLASS_MISMATCH"):
            view(graph=g)

    def test_31_extra_fields_refused(self):
        g = mod.fixture()
        g["nodes"][0]["private_access_token"] = "should-not-serialize"
        with self.assertRaisesRegex(mod.Hold, "INVALID_NODE_FIELDS"):
            view(graph=g)

    def test_32_turtle_input_budget_enforced(self):
        g = mod.fixture()
        for i in range(mod.MAX_INPUT_NODES):
            g["nodes"].append({
                "id": "system:extra" + str(i),
                "class": "SYSTEM", "visibility": "PUBLIC",
                "source_ref": "fixture:system:extra" + str(i),
                "source_sha256": "b" * 64, "edges": [],
            })
        with self.assertRaisesRegex(mod.Hold, "INPUT_NODE_BUDGET"):
            view(graph=g)

    def test_33_output_declares_zero_effects(self):
        x = view()
        self.assertEqual(x["runtime_workers"], 0)
        self.assertEqual(x["provider_requests"], 0)
        self.assertEqual(x["effects"], 0)
        self.assertEqual(x["membership_election"], "NONE")

    def test_34_output_never_claims_remote_receipt(self):
        x = view()
        self.assertEqual(x["receiver_ack"], "NOT_OBSERVED")
        self.assertEqual(x["actual_remote_discovery"], "NOT_TESTED")
        self.assertTrue(all(not n["source_bytes_independently_read"]
                            for n in x["nodes"]))

    def test_35_input_order_not_discovery_authority(self):
        a = mod.fixture()
        b = deepcopy(a)
        b["nodes"].reverse()
        for node in b["nodes"]:
            node["edges"].reverse()
        self.assertEqual(view(graph=a), view(graph=b))

    def test_36_data_not_converted_to_member_or_right(self):
        self.assertTrue(all(not e["membership_granted"]
                            and not e["effect_authority_granted"]
                            for e in view()["edges"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
