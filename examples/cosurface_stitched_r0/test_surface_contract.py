"""CoSurface R0 static fail-closed contract tests; NOT desktop runtime tests."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

HTML = Path(__file__).with_name("index.html").read_text(encoding="utf-8")

class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.labels = {}
        self.sections = set()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            assert a["id"] not in self.ids, f"Duplicate DOM ID: {a['id']}"
            self.ids.add(a["id"])
            self.labels[a["id"]] = a
            if tag == "section":
                self.sections.add(a["id"])

class UXContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dom = Elements()
        cls.dom.feed(HTML)
        match = re.search(r"const routes=\[(.*?)\];", HTML, re.DOTALL)
        if not match:
            raise AssertionError("No shared routing registry found")
        cls.routes = re.findall(r'\["([^"]+)","([^"]+)"\]', match.group(1))

    def test_exactly_one_orb_anchor(self):
        self.assertEqual(HTML.count('id="orb"'), 1)
        self.assertIn("orb", self.dom.ids)

    def test_shared_routes_have_real_unique_destinations(self):
        ids = [dest for _, dest in self.routes]
        self.assertTrue(ids)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(set(ids).issubset(self.dom.sections))

    def test_two_navigation_surfaces_use_same_registry(self):
        self.assertIn('document.getElementById("orbnav").append(navButton(label,id))', HTML)
        self.assertIn('document.getElementById("navbuttons").append(navButton(label,id))', HTML)
        self.assertIn("legacy.append(navButton(label,id))", HTML)

    def test_legacy_right_click_and_keyboard_escape(self):
        self.assertIn('orb.addEventListener("contextmenu"', HTML)
        self.assertIn('e.key==="Escape"', HTML)

    def test_hover_only_opens_preview(self):
        hover = re.search(r'orb.addEventListener\("pointerenter".*?\}\);', HTML, re.DOTALL)
        self.assertIsNotNone(hover)
        self.assertIn("showPanel(true)", hover.group(0))
        self.assertNotIn("navigate(", hover.group(0))

    def test_no_external_network_or_autorun(self):
        self.assertNotRegex(HTML, r"\bfetch\s*\(|\bXMLHttpRequest\b|\bWebSocket\s*\(")
        self.assertNotRegex(HTML, r"<script[^>]+src=|<iframe|<form[^>]+action=")

    def test_synthetic_state_not_claimed_verified(self):
        self.assertIn("EVIDENCE: SYNTHETIC", HTML)
        self.assertIn("X2: UNKNOWN", HTML)
        self.assertIn("Not installed on X2", HTML)

    def test_host_status_not_inferred_from_remote_transport(self):
        # Proof status has three distinct fields, never one omnibus offline flag.
        for ident in ("host-signal", "link-signal", "ux-signal", "signal-source"):
            with self.subTest(field=ident):
                self.assertIn('id="' + ident + '"', HTML)
        self.assertIn('host:"REPORTED RUNNING"', HTML)
        self.assertIn('link:"UNREACHABLE"', HTML)
        self.assertIn('ux:"UNKNOWN"', HTML)
        self.assertIn("No host power inference", HTML)
        self.assertIn("No source is allowed to infer host state", HTML)

    def test_signal_demo_is_local_reversible_and_not_live(self):
        self.assertIn('id="show-signal-case"', HTML)
        self.assertIn('id="reset-signals"', HTML)
        self.assertIn('renderSignalCase("demonstration")', HTML)
        self.assertIn('renderSignalCase("unknown")', HTML)
        self.assertIn("SYNTHETIC EXAMPLE:", HTML)
        self.assertIn("No live telemetry connected", HTML)
        self.assertNotIn("X2 OFFLINE", HTML)

    def test_future_pull_is_explicitly_revisable_and_constrained(self):
        self.assertIn('id="future"', HTML)
        self.assertIn('["Future","future"]', HTML)
        self.assertIn("Research hypothesis, not a divine instruction", HTML)
        for term in ("flourishing", "truth", "resilience", "optionality", "Rights, consent, recovery and Stop"):
            with self.subTest(term=term):
                self.assertIn(term, HTML)

    def test_operator_escape_and_accessible_orb(self):
        self.assertIn('aria-label="Open CoOrb;', HTML)
        self.assertIn('id="close"', HTML)
        self.assertIn('orb.focus()', HTML)

if __name__ == "__main__":
    unittest.main()
