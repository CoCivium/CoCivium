"""Machine-facing CoPreGeneric packet is source-bound and fail-closed."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "copre_generic_contribution_r0.json").read_text(encoding="utf-8"))
HUMAN = (ROOT / "COPRE_GENERIC_CONTRIBUTION_R0.md").read_text(encoding="utf-8")


class CoPreGenericContributionTests(unittest.TestCase):
    def test_machine_packet_is_exactly_named(self):
        self.assertEqual(DATA["schema"], "CoPreGeneric.ContributionIndex.R0")
        self.assertEqual(DATA["scope"], "PUBLIC_SAFE_CANDIDATE")

    def test_proof_boundary_never_green_by_source_landing(self):
        self.assertTrue(DATA["claims"]["public_candidate_landed"])
        for name in ("merged_main", "meta_ai_readback", "x2_runtime",
                     "cross_provider_sync", "governing_canon",
                     "agi_or_awareness_proven"):
            self.assertFalse(DATA["claims"][name], name)

    def test_includes_pointers_and_known_source_blob_hashes(self):
        self.assertGreaterEqual(len(DATA["fronts"]), 10)
        for item in DATA["fronts"]:
            self.assertTrue(item.get("ref") or item.get("uri"))
            self.assertTrue(item["qualification"])
            if "blob_sha" in item:
                self.assertEqual(len(item["blob_sha"]), 40)
                int(item["blob_sha"], 16)

    def test_machine_and_human_views_share_source_id(self):
        self.assertEqual(DATA["human_projection"], "COPRE_GENERIC_CONTRIBUTION_R0.md")
        self.assertIn("CoSynthVerse+", HUMAN)
        self.assertIn("CoBioVerse+", HUMAN)
        self.assertIn("CoPre Thumb R1", HUMAN)

    def test_machine_surface_is_not_human_speech_clone(self):
        self.assertIn("typed_relations", DATA["surface_contract"]["synth_facing"])
        self.assertIn("accessible_navigation", DATA["surface_contract"]["bio_facing"])
        self.assertTrue(DATA["surface_contract"]["shared_source_graph"])
        self.assertTrue(DATA["surface_contract"]["distinct_presentations"])

    def test_hypotheses_not_proven_sentience(self):
        self.assertIn("COAGI_NOT_PROVEN", DATA["research_lanes"])
        self.assertIn("CoAGI+ / awareness", HUMAN)
        self.assertIn("not a property established", HUMAN)

    def test_receiver_evidence_requirement_retained(self):
        self.assertIn("NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
                      DATA["required_nonclaims"])
        self.assertIn("Meta AI/WhatsApp has not independently read", HUMAN)

    def test_public_source_has_no_private_recipients(self):
        text = HUMAN + json.dumps(DATA)
        for address in ("richardmballard@gmail.com", "rballard@inseed.com",
                        "ndizeyeelix@gmail.com"):
            self.assertNotIn(address, text)


if __name__ == "__main__":
    unittest.main()
