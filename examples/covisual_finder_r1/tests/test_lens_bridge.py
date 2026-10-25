import copy
import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import finder
import lens_bridge as bridge


class CoVisualLensBridgeR0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = finder.load()
        cls.lens = bridge.load_colens()
        cls.result = bridge.build()

    def altered_registry(self):
        return copy.deepcopy(self.registry)

    def altered_lens(self):
        return copy.deepcopy(self.lens)

    def altered_output(self):
        return copy.deepcopy(self.result)

    def test_01_schema(self):
        self.assertEqual(self.result["schema"], "CoCivium.CoVisual.CoLensSourceToViewBridge.R0")

    def test_02_four_fixed_public_sources(self):
        self.assertEqual(self.result["sample_size"], 4)

    def test_03_all_three_views(self):
        self.assertEqual(set(self.result["views"]), set(bridge.VIEW_NAMES))
        for obj in self.result["objects"]:
            self.assertEqual(set(obj["views"]), set(bridge.VIEW_NAMES))

    def test_04_cross_view_same_source_identity(self):
        for obj in self.result["objects"]:
            ids = {v["source_id"] for v in obj["views"].values()}
            digests = {v["source_digest"] for v in obj["views"].values()}
            self.assertEqual(ids, {obj["id"]})
            self.assertEqual(digests, {obj["source_digest"]})

    def test_05_cross_view_source_url_parity(self):
        for obj in self.result["objects"]:
            self.assertEqual({v["source_page"] for v in obj["views"].values()}, {obj["source_page"]})

    def test_06_cross_view_rights_parity(self):
        for obj in self.result["objects"]:
            self.assertEqual({v["rights_state"] for v in obj["views"].values()}, {obj["rights_state"]})

    def test_07_cross_view_epistemic_parity(self):
        for obj in self.result["objects"]:
            self.assertEqual({v["epistemic_class"] for v in obj["views"].values()}, {obj["epistemic_class"]})

    def test_08_work_identity_parity(self):
        for obj in self.result["objects"]:
            self.assertTrue(obj["work_id"].startswith("coal.visualprior."))
            self.assertEqual({v["work_id"] for v in obj["views"].values()}, {obj["work_id"]})

    def test_09_source_identity_changes_with_meaning(self):
        a = self.altered_registry()
        a["public_donors"][0]["motif"] += " (synthetic source change)"
        out = bridge.build(a, self.lens)
        self.assertNotEqual(out["objects"][0]["source_digest"], self.result["objects"][0]["source_digest"])

    def test_10_source_registry_fingerprint(self):
        self.assertEqual(self.result["source_registry_digest"], bridge.digest(self.registry))

    def test_11_colens_contract_fingerprint(self):
        self.assertEqual(self.result["colens_contract_digest"], bridge.digest(self.lens))

    def test_12_no_external_effects(self):
        self.assertEqual(self.result["actual_effects"], 0)
        self.assertEqual(self.result["actual_receivers"], 0)
        self.assertEqual(self.result["source_image_bytes_copied"], 0)

    def test_13_no_provider_worker_or_receiver(self):
        for obj in self.result["objects"]:
            self.assertEqual(obj["receiver_state"], "HELD_NOT_RENDERED_OR_READ_BY_INDEPENDENT_RECEIVER")
            for view in obj["views"].values():
                self.assertIsNone(view["receiver_ack"])
                self.assertEqual(view["authority"], "NONE")

    def test_14_plain_text_preserved_from_registry(self):
        for source, obj in zip(self.registry["public_donors"], self.result["objects"]):
            self.assertEqual(obj["views"]["Text"]["accessible_explanation"], source["accessible_twin"])
            self.assertEqual(obj["views"]["Orb"]["plain_text_fallback"], source["accessible_twin"])

    def test_15_inverse_not_promoted_to_fact(self):
        for source, obj in zip(self.registry["public_donors"], self.result["objects"]):
            self.assertEqual(obj["views"]["Text"]["inverse_question"], source["inverse_challenge"])
            self.assertEqual(obj["views"]["Orb"]["inverse_question"], source["inverse_challenge"])
            self.assertTrue(all(e["status"] == "PROPOSED" for e in obj["views"]["Map"]["edges"]))

    def test_16_map_arrows_not_causality(self):
        for obj in self.result["objects"]:
            self.assertTrue(all(e["type"] not in bridge.BANNED for e in obj["views"]["Map"]["edges"]))

    def test_17_orb_satellites_stay_bounded(self):
        for obj in self.result["objects"]:
            self.assertLessEqual(len(obj["views"]["Orb"]["satellites"]), 3)
            self.assertTrue(all(s["status"] == "PROPOSED_INTERNAL_VIEW_ONLY" for s in obj["views"]["Orb"]["satellites"]))

    def test_18_loss_recorded(self):
        for obj in self.result["objects"]:
            self.assertEqual(len(obj["semantic_loss"]), 3)

    def test_19_invalid_extra_private_field_rejected(self):
        reg = self.altered_registry()
        reg["public_donors"][0]["private_clipboard"] = "synthetic fixture not real content"
        with self.assertRaisesRegex(ValueError, "UNDECLARED_DONOR_METADATA"):
            bridge.build(reg, self.lens)

    def test_20_unqualified_image_byte_field_rejected(self):
        reg = self.altered_registry()
        reg["public_donors"][0]["raw_image"] = "synthetic fixture not real image"
        with self.assertRaises(ValueError):
            bridge.build(reg, self.lens)

    def test_21_unknown_colens_schema_held(self):
        lens = self.altered_lens()
        lens["schema"] = "UNTRUSTED_SCHEMA"
        with self.assertRaisesRegex(ValueError, "COLENS_UNKNOWN_SCHEMA"):
            bridge.build(self.registry, lens)

    def test_22_no_network_enabled_by_colens(self):
        lens = self.altered_lens()
        lens["privacy"]["external_network"] = True
        with self.assertRaisesRegex(ValueError, "COLENS_NETWORK_NOT_BOUNDED"):
            bridge.build(self.registry, lens)

    def test_23_untrusted_private_source_held(self):
        lens = self.altered_lens()
        lens["privacy"]["raw_private_source"] = "EMBEDDED"
        with self.assertRaisesRegex(ValueError, "COLENS_RAW_PRIVATE"):
            bridge.build(self.registry, lens)

    def test_24_missing_or_mismatched_view_held(self):
        lens = self.altered_lens()
        lens["views"] = ["Text", "Map"]
        with self.assertRaisesRegex(ValueError, "COLENS_THREE_VIEWS_REQUIRED"):
            bridge.build(self.registry, lens)

    def test_25_colens_authority_not_inherited(self):
        lens = self.altered_lens()
        lens["authority"] = "SEND_AND_ACT"
        with self.assertRaisesRegex(ValueError, "COLENS_EFFECT_AUTHORITY"):
            bridge.build(self.registry, lens)

    def test_26_intentional_source_rights_mismatch_rejected(self):
        obj = self.altered_output()
        obj["objects"][0]["views"]["Orb"]["rights_state"] = "APPROVED_COPY"
        with self.assertRaisesRegex(ValueError, "CROSS_VIEW_SOURCE_OR_RIGHTS_DRIFT"):
            bridge.assert_safe(obj)

    def test_27_source_pointer_mismatch_rejected(self):
        obj = self.altered_output()
        obj["objects"][1]["views"]["Text"]["source_page"] = "https://not-the-source.example"
        with self.assertRaisesRegex(ValueError, "CROSS_VIEW_SOURCE_OR_RIGHTS_DRIFT"):
            bridge.assert_safe(obj)

    def test_28_map_forged_causal_edge_rejected(self):
        obj = self.altered_output()
        obj["objects"][0]["views"]["Map"]["edges"][0]["type"] = "CAUSES"
        with self.assertRaisesRegex(ValueError, "UNQUALIFIED_GRAPH_EDGE"):
            bridge.assert_safe(obj)

    def test_29_map_dangling_edge_rejected(self):
        obj = self.altered_output()
        obj["objects"][0]["views"]["Map"]["edges"][0]["from"] = "missing"
        with self.assertRaisesRegex(ValueError, "UNQUALIFIED_GRAPH_EDGE"):
            bridge.assert_safe(obj)

    def test_30_orb_massive_fanout_rejected(self):
        obj = self.altered_output()
        obj["objects"][0]["views"]["Orb"]["satellites"].append({"role": "CoNoise", "status": "PROPOSED_INTERNAL_VIEW_ONLY"})
        with self.assertRaisesRegex(ValueError, "UNBOUNDED_ORB_SATELLITES"):
            bridge.assert_safe(obj)

    def test_31_structural_verifier_passes(self):
        self.assertTrue(bridge.assert_safe(self.result))

    def test_32_json_roundtrip_reconstructs_same_projection(self):
        a = json.loads(json.dumps(self.result, ensure_ascii=False))
        self.assertEqual(a, self.result)
        self.assertTrue(bridge.assert_safe(a))

    def test_33_no_automatic_media_license_or_renderer_claim(self):
        self.assertEqual(self.result["independent_renderers_qualified"], 0)
        for obj in self.result["objects"]:
            for view in obj["views"].values():
                self.assertIn("NOT_RENDERED", view["status"])

    def test_34_no_effects_in_literal_model(self):
        for obj in self.result["objects"]:
            self.assertEqual(len(obj["views"]["Map"]["edges"]), 2)
            self.assertEqual(len(obj["views"]["Map"]["nodes"]), 3)

    def test_35_source_page_links_unchanged(self):
        self.assertEqual(
            [obj["source_page"] for obj in self.result["objects"]],
            [x["source_page"] for x in self.registry["public_donors"]]
        )


if __name__ == "__main__":
    unittest.main()
