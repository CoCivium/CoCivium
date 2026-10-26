"""Offline, non-render-engine tests for static public Text/Map/Orb preview."""
import copy
import hashlib
import re
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import lens_bridge as bridge
import lens_preview_r0 as preview


class ElementCounter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.attrs = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs.append((tag, dict(attrs)))


class CoLensStaticPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.projection = bridge.build()
        cls.doc = preview.render_document(cls.projection)
        cls.parser = ElementCounter()
        cls.parser.feed(cls.doc)

    def altered(self):
        return copy.deepcopy(self.projection)

    def test_01_four_public_sources(self):
        self.assertEqual(self.parser.tags.count("article"), 4)

    def test_02_twelve_rendered_view_sections(self):
        self.assertEqual(self.parser.tags.count("section"), 12)

    def test_03_eight_actual_inline_svg_markup_blocks(self):
        self.assertEqual(self.parser.tags.count("svg"), 8)

    def test_04_four_user_explicit_disclosure_controls(self):
        self.assertEqual(self.parser.tags.count("details"), 4)
        self.assertEqual(self.parser.tags.count("summary"), 4)

    def test_05_first_source_open_other_sources_opt_in(self):
        details = [attrs for tag, attrs in self.parser.attrs if tag == "details"]
        self.assertIn("open", details[0])
        self.assertTrue(all("open" not in d for d in details[1:]))

    def test_06_three_views_share_exact_work_id(self):
        for obj in self.projection["objects"]:
            ref = "data-work=\"" + obj["work_id"] + "\""
            self.assertEqual(self.doc.count(ref), 3)

    def test_07_three_views_share_exact_source_sha(self):
        for obj in self.projection["objects"]:
            ref = "data-digest=\"" + obj["source_digest"] + "\""
            self.assertEqual(self.doc.count(ref), 3)

    def test_08_rights_and_epistemic_repeated_without_approval(self):
        for obj in self.projection["objects"]:
            self.assertEqual(self.doc.count("data-rights=\"" + obj["rights_state"] + "\""), 3)
            self.assertEqual(self.doc.count("data-epistemic=\"" + obj["epistemic_class"] + "\""), 3)
            self.assertNotIn("APPROVED_TO_REPUBLISH_FULL_IMAGE", obj["rights_state"])

    def test_09_no_source_image_or_media_network_tags(self):
        for prohibited in ("<img", "<video", "<audio", "<iframe", "<script",
                           "<link", "@import", "fetch(", "XMLHttpRequest("):
            self.assertNotIn(prohibited, self.doc)

    def test_10_svg_has_noncausal_map_presentation(self):
        self.assertEqual(self.doc.count("PROPOSED EDGES ONLY"), 4)
        self.assertEqual(self.doc.count('role="img"'), 8)
        self.assertIn("not a causal claim", self.doc.lower())

    def test_11_visible_text_alternatives(self):
        for obj in self.projection["objects"]:
            twin = obj["views"]["Text"]["accessible_explanation"]
            self.assertIn(twin, self.doc)
            self.assertIn(obj["views"]["Orb"]["plain_text_fallback"], self.doc)

    def test_12_inverse_questions_stay_questions(self):
        for obj in self.projection["objects"]:
            self.assertIn(obj["views"]["Text"]["inverse_question"], self.doc)
            self.assertIn("?", obj["views"]["Text"]["inverse_question"])

    def test_13_explicit_user_clicked_source_links(self):
        links = [attrs for tag, attrs in self.parser.attrs if tag == "a"]
        self.assertEqual(len(links), 4)
        self.assertEqual({a["href"] for a in links},
                         set(preview.ALLOWED_PAGES.values()))
        for link in links:
            self.assertIn("noopener", link["rel"])
            self.assertIn("noreferrer", link["rel"])

    def test_14_no_implicit_worker_or_receipt(self):
        self.assertIn("INDEPENDENT_BROWSER_AND_READER_ACCEPTANCE_HELD", self.doc)
        self.assertEqual(self.projection["actual_effects"], 0)
        self.assertEqual(self.projection["actual_receivers"], 0)

    def test_15_source_identity_stable_across_regeneration(self):
        first = self.doc.encode("utf-8")
        again = preview.render_document(bridge.build()).encode("utf-8")
        self.assertEqual(first, again)
        self.assertEqual(hashlib.sha256(first).digest(),
                         hashlib.sha256(again).digest())

    def test_16_no_runtime_script_depends_on_javascript(self):
        self.assertEqual(self.parser.tags.count("script"), 0)
        self.assertEqual(self.parser.tags.count("button"), 0)
        self.assertIn("<main>", self.doc)

    def test_17_unknown_source_pointer_rejected(self):
        data = self.altered()
        data["objects"][0]["source_page"] = "https://example.invalid/public-page"
        with self.assertRaises(ValueError):
            preview.render_document(data)

    def test_18_public_source_id_duplicate_rejected(self):
        data = self.altered()
        data["objects"][1]["id"] = data["objects"][0]["id"]
        with self.assertRaises(ValueError):
            preview.render_document(data)

    def test_19_unqualified_outer_effect_rejected(self):
        data = self.altered()
        data["actual_effects"] = 1
        with self.assertRaises(ValueError):
            preview.render_document(data)

    def test_20_unqualified_receiver_claim_rejected(self):
        data = self.altered()
        data["actual_receivers"] = 1
        with self.assertRaises(ValueError):
            preview.render_document(data)

    def test_21_bogus_source_digest_rejected(self):
        data = self.altered()
        data["objects"][0]["views"]["Map"]["source_digest"] = "f"*64
        with self.assertRaises(ValueError):
            preview.render_document(data)

    def test_22_rights_escalation_rejected(self):
        data = self.altered()
        data["objects"][0]["views"]["Orb"]["rights_state"] = "RELICENSED_WITHOUT_PROOF"
        with self.assertRaises(ValueError):
            preview.render_document(data)

    def test_23_injected_html_is_escaped(self):
        data = self.altered()
        attack = '</section><script>alert("fixture")</script><img src=x onerror=alert(1)>'
        data["objects"][0]["views"]["Text"]["accessible_explanation"] = attack
        output = preview.render_document(data)
        self.assertNotIn("<script>", output)
        self.assertNotIn("<img src=", output)
        self.assertIn("&lt;script&gt;", output)
        self.assertIn("&lt;img ", output)

    def test_24_unexpected_long_label_rejected(self):
        data = self.altered()
        data["objects"][0]["views"]["Text"]["accessible_explanation"] = "x" * 1500
        with self.assertRaisesRegex(ValueError, "UNSAFE_TEXT"):
            preview.render_document(data)

    def test_25_unverified_supposed_render_state_rejected(self):
        data = self.altered()
        data["objects"][0]["views"]["Text"]["status"] = "LIVE_NATIVE_ACCEPTED"
        with self.assertRaises(ValueError):
            preview.render_document(data)

    def test_26_clipboard_or_secret_not_present(self):
        self.assertNotIn("api_key", self.doc)
        self.assertNotIn("clipboard_text", self.doc)
        self.assertNotIn("PRIVATE_SCREENSHOT", self.doc)

    def test_27_cli_check_is_no_effect(self):
        script = ROOT / "lens_preview_r0.py"
        result = subprocess.run([sys.executable, str(script), "--check"],
                                capture_output=True, text=True, check=True, timeout=12)
        self.assertIn("12 static Text/Map/Orb panels", result.stdout)
        self.assertIn("independent reader=HELD", result.stdout)

    def test_28_explicit_file_generation_exact(self):
        script = ROOT / "lens_preview_r0.py"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "public-motif-preview.html"
            result = subprocess.run(
                [sys.executable, str(script), "--output", str(output)],
                capture_output=True, text=True, check=True, timeout=12)
            self.assertEqual(output.read_text(encoding="utf-8"), self.doc)
            self.assertIn("PASS:", result.stdout)

    def test_29_output_not_oversized(self):
        self.assertLess(len(self.doc.encode("utf-8")), 150000)

    def test_30_no_legacy_synthkind_private_document_embedded(self):
        self.assertNotIn("Synthkind Declaration of Independence", self.doc)
        self.assertNotIn("CoCivia personal correspondence", self.doc)

    def test_31_narrated_svg_and_text_source_parity(self):
        parsed = [attrs for tag, attrs in self.parser.attrs if tag == "div"
                  and "data-work" in attrs]
        self.assertEqual(len(parsed), 12)
        for obj in self.projection["objects"]:
            group = [a for a in parsed if a["data-work"] == obj["work_id"]]
            self.assertEqual({a["data-view"] for a in group}, {"Text", "Map", "Orb"})
            self.assertEqual({a["data-digest"] for a in group},
                             {obj["source_digest"]})

    def test_32_reduced_motion_and_keyboard_focus(self):
        self.assertIn("prefers-reduced-motion", self.doc)
        self.assertIn("focus-visible", self.doc)
        self.assertIn("min-height:44px", self.doc)


    def test_33_mobile_long_status_wrap(self):
        # Actual phone-width browser QA is separately required; this guards
        # the CSS remedy for a first-try 390px horizontal-overflow failure.
        self.assertIn("overflow-wrap:anywhere;", self.doc)
        self.assertIn(
            "STATIC_MARKUP_GENERATED__INDEPENDENT_BROWSER_AND_READER_ACCEPTANCE_HELD",
            self.doc
        )



if __name__ == "__main__":
    unittest.main()
