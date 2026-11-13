"""CoSeed/CoPath discovery is not CoEx, real sync or complete historical recovery."""
from pathlib import Path
import json
import unittest

DATA = json.loads((Path(__file__).resolve().parent /
                   "co_seed_path_registry_r0.json").read_text(encoding="utf-8"))


class CoSeedPathRegistryTests(unittest.TestCase):
    def test_public_candidate_is_not_runtime(self):
        self.assertEqual(DATA["scope"], "PUBLIC_SOURCE_CANDIDATE")
        self.assertFalse(DATA["proof_boundaries"]["independent_receiver_pickup"])
        self.assertFalse(DATA["proof_boundaries"]["semantic_integration"])
        self.assertFalse(DATA["proof_boundaries"]["merged_main"])

    def test_every_node_has_exact_provenance(self):
        for n in DATA["nodes"]:
            self.assertTrue(n["id"] and n["front"] and n["path"])
            self.assertTrue(n["path"].startswith("examples/cosurface_stitched_r0/"))
            self.assertEqual(len(n["git_blob_sha1"]), 40)
            int(n["git_blob_sha1"], 16)
            self.assertEqual(n["status"], "LANDED_SOURCE_CANDIDATE")

    def test_source_identity_unique(self):
        keys = [(n["path"], n["git_blob_sha1"]) for n in DATA["nodes"]]
        self.assertEqual(len(keys), len(set(keys)))

    def test_relations_use_existing_nodes(self):
        nodes = {n["id"] for n in DATA["nodes"]}
        for edge in DATA["edges"]:
            self.assertIn(edge["from"], nodes)
            self.assertIn(edge["to"], nodes)
            self.assertNotEqual(edge["from"], edge["to"])

    def test_synth_and_bio_have_distinct_projection(self):
        predicates = {(e["from"], e["to"], e["predicate"]) for e in DATA["edges"]}
        self.assertIn(("copre", "copre_machine", "MACHINE_PROJECTION"), predicates)
        self.assertIn(("copre", "megascroller", "HUMAN_PROJECTION"), predicates)

    def test_receiver_ack_is_not_faked(self):
        self.assertEqual(DATA["proven_receivers"], [])
        self.assertIn("receiver-owned exact digest ACK", " ".join(DATA["co_path_for_receiver"]))

    def test_private_fronts_are_held_and_not_published(self):
        held = {f["front"] for f in DATA["fronts_held"]}
        self.assertTrue({"CoStead", "X2", "MetaAI", "private_historical_sessions"} <= held)
        self.assertTrue(all(n["scope"] == "PUBLIC" for n in DATA["nodes"]))

    def test_required_nonclaims(self):
        for key in ("NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
                    "DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY",
                    "HASHING_IS_NOT_SEMANTIC_INGESTION"):
            self.assertIn(key, DATA["required_nonclaims"])

    def test_no_private_identifiers(self):
        text = json.dumps(DATA)
        for private in ("richardmballard@gmail.com", "rballard@inseed.com",
                        "D:\\CoCivium\\CoFarm", "C:\\Users\\Owner"):
            self.assertNotIn(private, text)

    def test_current_branch_must_be_pinned_by_receiver(self):
        self.assertIn("pin commit", DATA["version_policy"])
        self.assertIn("resolve exact repository and branch commit",
                      DATA["co_path_for_receiver"])


if __name__ == "__main__":
    unittest.main()
