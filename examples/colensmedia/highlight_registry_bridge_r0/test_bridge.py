"""Adversarial offline tests for a pinned, non-mutating legacy registry adapter."""
import copy
import hashlib
import json
import re
import unittest
from pathlib import Path

import bridge

SOURCE = bridge.SOURCE


class LegacyCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = SOURCE.read_bytes()
        cls.doc, cls.sha, cls.blob = bridge.decode_registry(cls.raw)
        cls.model = bridge.model_from_registry(cls.doc, cls.sha, cls.blob)
        cls.html = bridge.render_html(cls.model)

    def altered(self, edit):
        doc = copy.deepcopy(self.doc)
        edit(doc)
        return json.dumps(doc, ensure_ascii=False).encode("utf-8")

    def reject(self, edit, pattern):
        with self.assertRaisesRegex(ValueError, pattern):
            bridge.decode_registry(self.altered(edit), expected_blob=None)

    def test_01_source_is_exact_real_legacy_registry(self):
        self.assertEqual(self.blob, bridge.EXPECTED_GIT_BLOB)
        self.assertEqual(len(self.doc["assets"]), 10)

    def test_02_raw_sha256_exact(self):
        self.assertEqual(self.sha, hashlib.sha256(self.raw).hexdigest())

    def test_03_registry_declares_not_release(self):
        self.assertEqual(self.doc["state"], bridge.EXPECTED_STATE)
        self.assertEqual(self.model["rendered_freshness"], "NOT_VERIFIED_CURRENT")

    def test_04_three_separate_views_share_exact_source_hash(self):
        for name in ["map", "orb", "text"]:
            self.assertIn('id="' + name + '" data-source-sha256="' + self.sha + '"', self.html)

    def test_05_all_asset_ids_text_available_in_all_views(self):
        regions = [
            self.html.split('<section id="' + name + '"', 1)[1].split('</section>', 1)[0]
            for name in ["map", "orb", "text"]
        ]
        for row in self.doc["assets"]:
            for view in regions:
                self.assertIn(row["id"], view)

    def test_06_no_unsupported_interasset_edges(self):
        self.assertEqual(len(self.model["edges"]), 10)
        self.assertTrue(all(x["from"] == "REGISTRY" and x["type"] == "LISTS_ENTRY"
                            and x["evidence_class"] == "DECLARED_REGISTRY_ONLY"
                            for x in self.model["edges"]))

    def test_07_count_not_worker_or_health(self):
        self.assertEqual(self.model["asset_count"], 10)
        self.assertIn("not live health", self.html.lower())
        self.assertIn("NOT_VERIFIED_CURRENT", self.html)

    def test_08_one_declared_status_is_not_promotion(self):
        self.assertEqual(self.model["status_counts"]["PUBLIC_HIGHLIGHT"], 1)
        self.assertEqual(self.model["status_counts"]["CANDIDATE_HIGHLIGHT"], 9)
        self.assertEqual(self.model["receiver_ack"], None)

    def test_09_zero_effects(self):
        self.assertEqual(self.model["authority"], "READ_ONLY_NONE")
        self.assertTrue(all(n == 0 for n in self.model["effects"].values()))
        self.assertEqual(self.model["native_fallback"], "OPEN_ORIGINAL_LEGACY_JSON")

    def test_10_loss_accounting_explicit(self):
        self.assertEqual(len(self.model["translation_losses"]), 4)
        self.assertIn("No imported media bytes", " ".join(self.model["translation_losses"]))

    def test_11_deterministic_render(self):
        self.assertEqual(self.html.encode(), bridge.render_html(self.model).encode())

    def test_12_no_external_fetch_or_dynamic_script(self):
        self.assertIn("connect-src 'none'", self.html)
        self.assertNotIn("<script", self.html)
        self.assertNotIn("<iframe", self.html)

    def test_13_fixed_source_not_user_selected_private_path(self):
        self.assertEqual(SOURCE, bridge.ROOT / "ai" / "highlight-assets.json")
        self.assertEqual(bridge.OUT.parent, bridge.HERE)

    def test_14_unknown_root_field_rejected(self):
        self.reject(lambda d: d.__setitem__("authorization", "ALL"), "UNKNOWN_REGISTRY_ENVELOPE")

    def test_15_missing_source_state_rejected(self):
        self.reject(lambda d: d.__setitem__("state", "CANON_READY"), "RELEASE_STATE_CHANGED")

    def test_16_unknown_asset_field_rejected(self):
        self.reject(lambda d: d["assets"][0].__setitem__("secret", "synthetic"), "UNKNOWN_ASSET_FIELDS")

    def test_17_duplicate_asset_id_rejected(self):
        self.reject(lambda d: d["assets"][1].__setitem__("id", d["assets"][0]["id"]),
                    "INVALID_OR_DUPLICATE_ASSET_ID")

    def test_18_duplicate_json_object_keys_rejected(self):
        raw = b'{"schema":"a","schema":"b"}'
        with self.assertRaisesRegex(ValueError, "DUPLICATE_JSON_KEY"):
            bridge.decode_registry(raw, expected_blob=None)

    def test_19_private_or_unknown_highlight_status_rejected(self):
        self.reject(lambda d: d["assets"][0].__setitem__("status", "PRIVATE_CONTENT"),
                    "UNSUPPORTED_HIGHLIGHT_STATUS")

    def test_20_numeric_readiness_rejected(self):
        self.reject(lambda d: d["assets"][0].__setitem__("readiness", 1),
                    "INVALID_READINESS_TOKEN")

    def test_21_control_character_name_rejected(self):
        self.reject(lambda d: d["assets"][0].__setitem__("name", "abc\npassword"),
                    "CONTROL_CHAR")

    def test_22_oversized_registry_rejected(self):
        with self.assertRaisesRegex(ValueError, "SOURCE_BYTES_OUT_OF_BOUNDS"):
            bridge.decode_registry(b"x" * (bridge.MAX_SOURCE + 1), expected_blob=None)

    def test_23_source_byte_drift_requires_review(self):
        changed = self.raw.replace(b"CoTheoryAll", b"CoTheoryAlt", 1)
        with self.assertRaisesRegex(ValueError, "SOURCE_GIT_BLOB_CHANGED"):
            bridge.decode_registry(changed)

    def test_24_html_name_injection_is_escaped_as_text(self):
        raw = self.altered(lambda d: d["assets"][0].__setitem__(
            "name", '<img src=x onerror=alert(1)>'))
        doc, sha, blob = bridge.decode_registry(raw, expected_blob=None)
        out = bridge.render_html(bridge.model_from_registry(doc, sha, blob))
        self.assertNotIn("<img", out)
        self.assertIn("&lt;img", out)
        self.assertNotIn('onerror="', out)

    def test_25_pinned_nonclaim_rails_are_not_optional(self):
        self.reject(lambda d: d["rails"].pop(), "NONCLAIM_RAIL_DRIFT")

    def test_26_reject_assets_array_shortcut(self):
        self.reject(lambda d: d.__setitem__("assets", []), "ASSET_COUNT_INVALID")

    def test_27_malformed_utf8_fails(self):
        with self.assertRaisesRegex(ValueError, "NOT_UTF8"):
            bridge.decode_registry(b"\xff", expected_blob=None)

    def test_28_readable_plain_text_alternative(self):
        self.assertIn('aria-label="Map node text alternatives"', self.html)
        self.assertIn('aria-label="Orb membership text alternative"', self.html)
        self.assertIn("<caption>Registry metadata, not product certification</caption>", self.html)

    def test_29_removed_overlay_falls_back_to_source(self):
        self.assertIn("Open the original unmodified", self.html)
        self.assertIn("Delete this generated page", self.html)

    def test_30_unsupported_schema_rejected(self):
        self.reject(lambda d: d.__setitem__("schema", "CoAll.Canon"), "RELEASE_STATE_CHANGED")


if __name__ == "__main__":
    unittest.main()
