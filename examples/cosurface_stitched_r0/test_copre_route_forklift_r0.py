"""CoPre Gateway R0: user-selected URLs are not three verified mirrors."""
import json
from pathlib import Path
import unittest
DATA=json.loads((Path(__file__).parent/"copre_route_forklift_r0.json").read_text(encoding="utf-8"))

class RouteForkliftTests(unittest.TestCase):
    def test_user_selected_three_routes_retained(self):
        urls=[r["url"] for r in DATA["intended_routes"]]
        self.assertEqual(urls,["https://github.com/CoCivium/CoPreGeneric",
                               "https://CoCivium.org/CoPre",
                               "https://InSeed.com/Stead"])
    def test_mouse_uses_one_pointer_not_three_payloads(self):
        self.assertEqual(DATA["pointer_policy"]["mouse_paste_target"],
                         "https://CoCivium.org/CoPre")
        self.assertFalse(DATA["pointer_policy"]["mouse_hardware_configuration_verified"])
    def test_unverified_routes_cannot_be_promoted_to_mirrors(self):
        for route in DATA["intended_routes"]:
            self.assertNotEqual(route["verification"], "VERIFIED")
            self.assertFalse(route["identical_content_proven"])
        self.assertIn("NO_MIRROR_HASH_EQUALITY_PROVEN",DATA["recoverability"]["nonclaims"])
    def test_actual_branch_fallback_source_is_preserved(self):
        source=DATA["verified_candidate"]
        self.assertEqual(source["repo"],"CoCivium/CoCivium")
        self.assertIn("candidate/cosurface",source["branch"])
        self.assertEqual(len(source["source_blob_sha"]),40)
        self.assertEqual(len(source["source_blob_machine_sha"]),40)
    def test_unscanned_priors_remain_held_not_omitted(self):
        self.assertIn("CoFarm/NAS/X2 unseen data",
                      DATA["recoverability"]["left_behind"])
        self.assertFalse(DATA["recoverability"]["private_transcript_publication_authorized"])
    def test_existing_source_not_automatic_receiver_pickup(self):
        self.assertFalse(DATA["pointer_policy"]["remote_receiver_verified"])
        self.assertIn("GITHUB_SOURCE_NOT_RECEIVER_PICKUP",DATA["recoverability"]["nonclaims"])

if __name__=="__main__":
    unittest.main()
