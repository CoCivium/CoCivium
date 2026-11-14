"""Offline CoBind Orb contract checks: browser examples must match router output."""
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "CoBindCandidateRouterR0.py"
HTML = ROOT / "examples" / "cobind" / "cobind-golden-braid-orb-r0.html"
spec = importlib.util.spec_from_file_location("cobind_orb_policy", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixtures():
    html = HTML.read_text(encoding="utf-8")
    match = re.search(r'<script id="cases" type="application/json">(.*?)</script>', html, re.S)
    if not match:
        raise AssertionError("Missing embedded fixture payload")
    return html, json.loads(match.group(1))


class OfflineCoBindOrbContract(unittest.TestCase):
    def test_all_fixture_outcomes_reproduced_by_python_router(self):
        html, d = fixtures()
        self.assertEqual(d["schema"], "CoBind.OfflineProjectionFixture.R0")
        self.assertEqual(len(d["cases"]), 10)
        self.assertEqual(len({c["id"] for c in d["cases"]}), len(d["cases"]))
        for c in d["cases"]:
            with self.subTest(case=c["id"]):
                out = module.route(c["claim"], c["anchors"])
                expected = c["expected"]
                self.assertEqual(out["state"], expected["state"])
                if "selected_id" in expected:
                    self.assertEqual(out["selected"]["id"], expected["selected_id"])
                if "reject_reason" in expected:
                    rejected = [s for a in out.get("rejected", []) for s in a["reasons"]]
                    self.assertIn(expected["reject_reason"], rejected)
                if "relation_semantics" in expected:
                    self.assertEqual(out["relation_semantics"], expected["relation_semantics"])
                self.assertNotIn("AUTHORIZED", out["state"])
        self.assertIn("SYNTHETIC FIXTURES ONLY", d["notice"])

    def test_offline_no_remote_scripts_tracking_or_network_calls(self):
        html, d = fixtures()
        self.assertNotRegex(html, r"<script\s+[^>]*src\s*=")
        self.assertNotRegex(html, r"\b(fetch|XMLHttpRequest|WebSocket|EventSource)\s*\(")
        self.assertNotIn("<iframe", html.lower())
        self.assertNotIn("navigator.sendBeacon", html)
        self.assertNotIn("localStorage", html)
        self.assertNotIn("sessionStorage", html)

    def test_every_case_has_question_reason_and_epistemic_class(self):
        _, d = fixtures()
        for c in d["cases"]:
            with self.subTest(case=c["id"]):
                self.assertTrue(c["question"])
                self.assertTrue(c["expected"]["reason"])
                self.assertIn(c["claim"]["epistemic"], module.CLAIM_TO_ANCHOR)
                self.assertEqual(c["claim"]["work_id"], d["work_id"])
                self.assertEqual(c["claim"]["receiver"], "research")

    def test_page_uses_text_only_for_fixture_content(self):
        html, _ = fixtures()
        self.assertIn("textContent", html)
        self.assertNotIn("innerHTML", html)
        self.assertIn('role="status"', html)
        self.assertIn('class="skip"', html)
        self.assertIn("prefers-reduced-motion", html)


    def test_braid_routes_are_exact_manifest_projection(self):
        html, _ = fixtures()
        match = re.search(r'<script id="braid" type="application/json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(match, "Missing embedded Golden Braid source projection")
        braid = json.loads(match.group(1))
        manifest = json.loads((ROOT / "ai" / "research" /
            "comindseed-cobind-golden-braid-cotheoryall-r0-20261110.json").read_text(encoding="utf-8"))
        self.assertEqual(braid["cross_front_routes"], manifest["cross_front_routes"])
        self.assertEqual(braid["anchors"], manifest["anchors"])
        self.assertEqual(len(braid["cross_front_routes"]), 7)
        self.assertEqual(len(braid["anchors"]), 6)
        self.assertTrue(all(edge["authority"] == "NONE" for edge in braid["cross_front_routes"]))
        self.assertIn("NOT_RECEIVER_ACCEPTANCE", braid["status"])
        self.assertIn("data-lens=\"braid\"", html)



if __name__ == "__main__":
    unittest.main()
