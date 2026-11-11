"""CoMediaFabric synthetic change propagation regression.

No email provider, browser, or production state is touched.
"""
import unittest


def affected(changed_id, edges):
    """Return dependent projections in breadth-first order, avoiding cycles."""
    found, pending, seen = [], [changed_id], {changed_id}
    while pending:
        current = pending.pop(0)
        for edge in edges:
            if edge["target_id"] != current or edge["relation"] not in ("derived_from", "depicts", "projects", "explains"):
                continue
            child = edge["source_id"]
            if child not in seen:
                seen.add(child)
                found.append(child)
                pending.append(child)
    return found


def invalidation(changed_id, nodes, edges):
    affected_ids = affected(changed_id, edges)
    results = {}
    for ident in affected_ids:
        node = nodes[ident]
        if node["type"] == "email_sent":
            results[ident] = "IMMUTABLE_SENT_RECORD"
        elif node["custody_scope"] == "private":
            results[ident] = "PRIVATE_REVIEW_REQUIRED"
        else:
            results[ident] = "STALE_REVIEW_REQUIRED"
    return results


class MediaEvolutionTests(unittest.TestCase):
    def setUp(self):
        self.nodes = {
            "claim": {"type": "claim", "custody_scope": "public"},
            "diagram": {"type": "diagram", "custody_scope": "public"},
            "draft": {"type": "email_draft", "custody_scope": "private"},
            "sent": {"type": "email_sent", "custody_scope": "private"},
        }
        self.edges = [
            {"source_id": "diagram", "target_id": "claim", "relation": "depicts"},
            {"source_id": "draft", "target_id": "claim", "relation": "derived_from"},
            {"source_id": "sent", "target_id": "claim", "relation": "derived_from"},
        ]

    def test_change_marks_dependent_diagram_stale(self):
        self.assertEqual(invalidation("claim", self.nodes, self.edges)["diagram"], "STALE_REVIEW_REQUIRED")

    def test_private_draft_requires_review_not_send(self):
        self.assertEqual(invalidation("claim", self.nodes, self.edges)["draft"], "PRIVATE_REVIEW_REQUIRED")

    def test_sent_record_is_not_rewritten(self):
        self.assertEqual(invalidation("claim", self.nodes, self.edges)["sent"], "IMMUTABLE_SENT_RECORD")

    def test_unrelated_change_does_not_propagate(self):
        self.assertEqual(invalidation("other", self.nodes, self.edges), {})

    def test_cycles_terminate(self):
        edges = self.edges + [{"source_id": "claim", "target_id": "diagram", "relation": "derived_from"}]
        self.assertEqual(set(affected("claim", edges)), {"diagram", "draft", "sent"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
