"""Nested CoMap and media-inspiration fail-closed regression fixtures."""
import unittest
from dataclasses import replace
from media_relation_graph_r0 import Artifact, fixture
from nested_nav_r0 import (MapNode, Inspiration, validate_map,
                           nested_projection, classify_inspiration)


class NestedNavigationTests(unittest.TestCase):
    def setup_data(self):
        artifacts, edges = fixture()
        nodes = (
            MapNode("all", "CoAll overview", child_ids=("research", "outreach")),
            MapNode("research", "Evidence and tests", artifact_ids=("research1", "test1", "diagram1")),
            MapNode("outreach", "Outreach privacy gate", artifact_ids=("draft1",),
                    scope="RESTRICTED"),
        )
        return artifacts, edges, nodes

    def test_private_branch_blocks_public_root(self):
        a, e, n = self.setup_data()
        self.assertIn(("PRIVATE_CHILD_IN_PUBLIC_MAP", "all"), validate_map(n, a, e)["errors"])

    def test_private_root_can_contain_restricted_branch(self):
        a, e, n = self.setup_data()
        n = (replace(n[0], scope="RESTRICTED"),) + n[1:]
        self.assertEqual(validate_map(n, a, e)["verdict"], "STRUCTURALLY_VALID")

    def test_nested_map_drills_into_real_nodes(self):
        a, e, n = self.setup_data()
        n = (replace(n[0], scope="RESTRICTED"),) + n[1:]
        p = nested_projection(n, a, e, root_id="all")
        self.assertEqual(p["root"]["children"][0]["label"], "Evidence and tests")
        self.assertEqual(p["evidence"], "STRUCTURAL_ONLY_NOT_X2_RUNTIME")

    def test_unknown_child_is_rejected(self):
        a, e, n = self.setup_data()
        changed = (replace(n[0], child_ids=("absent",)),) + n[1:]
        self.assertIn(("MISSING_CHILD_MAP", "all"), validate_map(changed, a, e)["errors"])

    def test_unknown_artifact_is_rejected(self):
        a, e, n = self.setup_data()
        changed = (n[0], replace(n[1], artifact_ids=("missing",)), n[2])
        self.assertIn(("MISSING_ARTIFACT", "research"), validate_map(changed, a, e)["errors"])

    def test_recursive_diagram_cycle_is_rejected(self):
        a, e, n = self.setup_data()
        changed = (replace(n[0], scope="RESTRICTED"),
                   replace(n[1], child_ids=("all",)), n[2])
        self.assertTrue(any(error[0] == "RECURSIVE_CYCLE"
                            for error in validate_map(changed, a, e)["errors"]))

    def test_duplicate_map_identity_fails(self):
        a, e, n = self.setup_data()
        self.assertIn(("DUPLICATE_OR_MISSING_MAP_NODE", "research"),
                      validate_map(n + (n[1],), a, e)["errors"])

    def test_public_map_cannot_include_private_draft(self):
        a, e, n = self.setup_data()
        changed = (n[0], n[1], replace(n[2], scope="PUBLIC"))
        self.assertIn(("PRIVATE_ARTIFACT_IN_PUBLIC_MAP", "outreach"),
                      validate_map(changed, a, e)["errors"])

    def test_unfound_image_is_not_inspiration(self):
        a, _e, _n = self.setup_data()
        self.assertEqual(classify_inspiration(Inspiration("missing", "candidate", "form"), a),
                         "SOURCE_MISSING")

    def test_unapproved_render_is_private_proposal(self):
        a, _e, _n = self.setup_data()
        i = Inspiration("diagram1", "new-video", "visual metaphor")
        self.assertEqual(classify_inspiration(i, a), "PRIVATE_INSPIRATION_PROPOSED")

    def test_restricted_draft_never_auto_publishes(self):
        a, _e, _n = self.setup_data()
        i = Inspiration("draft1", "public-post", "reply concept",
                        authorized=True, evidence_ref="review1")
        self.assertEqual(classify_inspiration(i, a), "RESTRICTED_SOURCE_REVIEW")

    def test_public_art_requires_evidence_and_review(self):
        a, _e, _n = self.setup_data()
        i = Inspiration("diagram1", "new-video", "lineage", authorized=True)
        self.assertEqual(classify_inspiration(i, a), "NO_PROVENANCE")
        self.assertEqual(classify_inspiration(replace(i, evidence_ref="source1"), a),
                         "ELIGIBLE_FOR_REVIEW_NOT_PUBLISHED")


if __name__ == "__main__":
    unittest.main()
