"""Adversarial CoMedia/CoSilo checks against exact typed graph state."""
import unittest
from dataclasses import replace
from media_relation_graph_r0 import Artifact, Relation, audit, diagram, fixture


class CoMediaRelationsTests(unittest.TestCase):
    def test_fixture_has_linked_research_test_diagram_and_draft(self):
        a, e = fixture()
        result = audit(a, e)
        self.assertEqual(result["verdict"], "STRUCTURALLY_VALID")
        self.assertEqual(result["orphans"], [])
        self.assertEqual(result["receiver_ack"], "NOT_PROVEN")
        self.assertIn("test1", diagram(a, e))

    def test_orphan_detected_without_inventing_relation(self):
        a, e = fixture()
        a += (Artifact("video1", "video", "r1", "sha-video"),)
        self.assertEqual(audit(a, e)["orphans"], ["video1"])

    def test_dangling_target_fails_closed(self):
        a, e = fixture()
        e += (Relation("draft1", "REFERENCES", "missing", "r1", "r1", ""),)
        self.assertIn(("DANGLING_EDGE", "draft1"), audit(a, e)["errors"])

    def test_stale_diagram_revision_not_silent(self):
        a, e = fixture()
        a = tuple(replace(v, revision="r2") if v.artifact_id == "diagram1" else v for v in a)
        self.assertIn(("STALE_RELATION", "diagram1"), audit(a, e)["errors"])

    def test_verified_link_requires_actual_evidence_reference(self):
        a, e = fixture()
        e += (Relation("diagram1", "DEMONSTRATES", "research1",
                       "r1", "r1", "", "VERIFIED"),)
        self.assertIn(("UNRECEIPTED_RELATION", "diagram1"), audit(a, e)["errors"])

    def test_public_projection_from_private_is_a_gate(self):
        a, e = fixture()
        a += (Artifact("public1", "coorb_view", "r1", "sha", "PUBLIC"),)
        e += (Relation("draft1", "PROJECTS", "public1", "r1", "r1", "ok"),)
        self.assertIn(("SCOPE_LEAK_CANDIDATE", "draft1"), audit(a, e)["errors"])

    def test_private_draft_reference_not_publication(self):
        a, e = fixture()
        self.assertIn("draft1", diagram(a, e))
        self.assertEqual(audit(a, e)["receiver_ack"], "NOT_PROVEN")
        self.assertNotIn("email_sent", [x.kind for x in a])

    def test_duplicate_identity_fails(self):
        a, e = fixture()
        a += (a[0],)
        self.assertIn(("DUPLICATE_OR_MISSING_ID", "research1"), audit(a, e)["errors"])

    def test_unknown_edge_rejected(self):
        a, e = fixture()
        e += (Relation("diagram1", "MAGICALLY_PROVES", "test1",
                       "r1", "r1", ""),)
        self.assertIn(("UNTYPED_RELATION", "diagram1"), audit(a, e)["errors"])

    def test_graph_generation_is_deterministic(self):
        a, e = fixture()
        self.assertEqual(diagram(a, e), diagram(tuple(reversed(a)), tuple(reversed(e))))

    def test_graph_cannot_render_dangling_edge_as_truth(self):
        a, e = fixture()
        with self.assertRaises(ValueError):
            diagram(a, e + (Relation("draft1", "REFERENCES", "missing",
                                      "r1", "r1", ""),))


if __name__ == "__main__":
    unittest.main()
