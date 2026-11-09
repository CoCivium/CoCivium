"""CoAll source-bound CoSeed/CoPath public discovery consistency."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REG=json.loads((ROOT/"coall_seed_path_discovery_r0.json").read_text(encoding="utf-8"))

class SeedPathDiscoveryTests(unittest.TestCase):
    def test_every_seed_has_unique_id_and_qualified_source(self):
        seeds=REG["seeds"]
        self.assertGreaterEqual(len(seeds),8)
        self.assertEqual(len({s["id"] for s in seeds}),len(seeds))
        for s in seeds:
            self.assertIn("SOURCE_LANDED_CANDIDATE",s["stage"])
            self.assertEqual(s["privacy"],"PUBLIC")
            self.assertEqual(len(s["blob_sha"]),40)
            int(s["blob_sha"],16)
            self.assertTrue((ROOT.parent.parent/s["path"].removeprefix("examples/cosurface_stitched_r0/")).exists() or
                            (ROOT/s["path"].removeprefix("examples/cosurface_stitched_r0/")).exists())

    def test_typed_paths_reference_existing_seed_ids(self):
        ids={s["id"] for s in REG["seeds"]}
        for path in REG["paths"]:
            self.assertIn(path["from"],ids)
            self.assertIn(path["to"],ids)
            self.assertNotIn("VERIFIED_INTEGRATED",path["status"])

    def test_critical_scopes_remain_unproven(self):
        self.assertEqual(REG["root"]["receiver_readback"],"NOT_PROVEN")
        self.assertEqual(REG["root"]["cross_front_integration"],"NOT_PROVEN")
        self.assertEqual(REG["mouse_gateway"],"INTENDED_NOT_DEPLOYED")
        self.assertFalse(REG["canonical_approval"]=="PROVEN")

    def test_wakes_keep_unintegrated_fronts_visible(self):
        self.assertGreaterEqual(len(REG["front_wake"]),5)
        self.assertTrue(all(x["next"] and x["source"] for x in REG["front_wake"]))

    def test_no_false_history_completeness_or_coex(self):
        self.assertTrue(REG["unknown_history"])
        self.assertIn("DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY",
                      REG["contract"]["nonclaims"])
        self.assertEqual(REG["root"]["coex"],"NOT_PROVEN")

    def test_public_manifest_cannot_leak_private_paths_or_recipients(self):
        value=json.dumps(REG)
        for secret in ("richardmballard@gmail.com","rballard@inseed.com",
                       "C:\\Users\\Owner","D:\\CoCivium\\"):
            self.assertNotIn(secret,value)

    def test_readable_html_is_not_mirrored_deployment(self):
        self.assertEqual(REG["privacy_gate"],"PUBLIC_SAFE_ONLY")
        self.assertTrue(any(p["status"].startswith("POTENTIAL")
                            for p in REG["paths"]))

if __name__=="__main__":
    unittest.main()
