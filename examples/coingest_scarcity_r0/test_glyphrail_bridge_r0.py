"""CoGlyphRail R0: static, bilingual, permission, provenance and culture QA.

Checks source shape only, not actual reader comprehension or browser rendering.
"""
import json
import pathlib
import re
import unittest

HERE=pathlib.Path(__file__).resolve().parent
HTML=(HERE/"glyphrail-bridge-r0.html").read_text("utf-8")
match=re.search(r'<script id="rail-contract" type="application/json">([\s\S]*?)</script>',HTML)
CONTRACT=json.loads(match.group(1)) if match else {}

class TestGlyphRail(unittest.TestCase):
    def test_contract_exists_and_identity_is_stable(self):
        self.assertEqual(CONTRACT["seed_id"],"COINGEST_SCARCITY_R0_GLYPHBRIDGE")
        self.assertEqual(CONTRACT["interaction_edge"],"NO_ACTION_EXECUTION")
    def test_no_authority(self):
        self.assertEqual(CONTRACT["one_authority_ceiling"],"READ_ONLY_PREVIEW")
        self.assertTrue(CONTRACT["no_auto_telemetry"])
        for t in CONTRACT["terms"]:
            self.assertTrue(t["source"])
    def test_six_anchored_terms(self):
        self.assertEqual({x["term"] for x in CONTRACT["terms"]},
          {"CoHereNow","CoBoogie+","CoRegroup+","CI+","CoDeed","ExState"})
        self.assertEqual(len({x["id"] for x in CONTRACT["terms"]}),6)
    def test_source_parents_and_nonclaims(self):
        self.assertEqual(len(CONTRACT["source_refs"]),4)
        self.assertIn("GLYPH_NE_AUTHORITY",CONTRACT["nonclaims"])
        self.assertIn("CI_PASS_NE_TRUTH",CONTRACT["nonclaims"])
        self.assertIn("TRANSLATION_NE_SEMANTIC_EQUIVALENCE_PROOF",CONTRACT["nonclaims"])
        self.assertIn("TERM_EXPOSURE_NE_LEARNING_PROOF",CONTRACT["nonclaims"])
    def test_language_coverage(self):
        for t in CONTRACT["terms"]:
            for field in ("name","meaning","not"):
                self.assertEqual(set(t[field]),set(CONTRACT["languages"]))
                self.assertTrue(all(t[field][lang].strip() for lang in ("en","fr")))
    def test_accessible_navigation_and_dynamic_text(self):
        for marker in ('lang="en"','<main>','</main>','<nav','aria-label="CoGlyphRail learning and status"',
            'aria-live="polite"','focus-visible','prefers-reduced-motion','aria-pressed',
            'document.createElement("button")','b.type="button"'):
            self.assertIn(marker,HTML)
    def test_glyph_optional_word_modes(self):
        self.assertEqual(CONTRACT["modes"],["plain","mixed","glyph"])
        self.assertIn('body[data-density="plain"] .glyph{display:none}',HTML)
        self.assertIn('body[data-density="glyph"] .glyph-label{display:none}',HTML)
        self.assertIn("Plain words",HTML)
    def test_visible_cultural_boundary(self):
        self.assertIn("CoVibeTru+",HTML)
        self.assertIn("does not have a verified, fixed dictionary definition",HTML)
        self.assertIn("translation",HTML.lower())
    def test_no_network_or_data_collection_logic(self):
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage", "navigator.mediaDevices",
                          "navigator.geolocation", "<form", "<iframe", "sendBeacon(", "WebSocket("):
            self.assertNotIn(forbidden,HTML)
    def test_no_script_content_induced_authority(self):
        self.assertIn("Selecting this educational glyph executes nothing.",CONTRACT["terms"][4]["not"]["en"])
        self.assertIn("NO EXECUTION",HTML)
    def test_provenance_not_language_variant(self):
        for t in CONTRACT["terms"]:
            self.assertIsInstance(t["source"],str)
            self.assertNotIn(t["source"], t["name"].values())
    def test_status_mode_not_falsely_promoted(self):
        self.assertEqual(CONTRACT["state"],"STATIC_PRIVATE_DRAFT_PUBLIC_SAFE_SIMULATION_NO_RUNTIME")
        self.assertIn("VISUAL_UX_NE_HUMAN_ACCEPTANCE",CONTRACT["nonclaims"])
    def test_distinct_check_vs_regroup(self):
        terms={x["term"]:x for x in CONTRACT["terms"]}
        self.assertNotEqual(terms["CI+"]["role"],terms["CoRegroup+"]["role"])
        self.assertNotEqual(terms["CoBoogie+"]["role"],terms["CoRegroup+"]["role"])
    def test_default_mode(self):
        self.assertEqual(CONTRACT["default_mode"],"mixed")
        self.assertEqual(CONTRACT["default_language"],"en")

if __name__=="__main__":
    unittest.main()
