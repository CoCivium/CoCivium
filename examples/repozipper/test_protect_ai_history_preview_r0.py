"""Static safety and accessibility contract for the synthetic HTML first-use preview.

These checks are deliberately not represented as an interactive browser or
screen-reader acceptance test. The JavaScript behavior is additionally tested
with Node against the real inline model code.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

PAGE = Path(__file__).with_name("protect_ai_history_preview_r0.html")


class Nodes(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag,dict(attrs)))


class PreviewContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PAGE.read_text(encoding="utf-8")
        cls.nodes = Nodes()
        cls.nodes.feed(cls.source)

    def test_offline_csp_and_no_remote_dependencies(self):
        c = self.source
        self.assertIn("default-src 'none'",c)
        self.assertIn("connect-src 'none'",c)
        self.assertIn("form-action 'none'",c)
        self.assertIn("img-src 'none'",c)
        self.assertNotIn('src="https:',c)
        self.assertNotIn('href="https:',c)
        self.assertNotIn("fetch(",c)
        self.assertNotIn("XMLHttpRequest",c)

    def test_no_provider_credentials_or_file_picker(self):
        self.assertNotIn('<input type="file"',self.source)
        self.assertNotIn("localStorage",self.source)
        self.assertNotIn("navigator.credentials",self.source)
        self.assertNotIn("getUserMedia",self.source)

    def test_single_call_to_action(self):
        ids = [attrs.get("id") for tag,attrs in self.nodes.tags if tag == "button"]
        self.assertEqual(ids.count("try-sample"),1)
        self.assertEqual(ids.count("reset-sample"),1)
        self.assertEqual(ids.count("sample-report"),1)

    def test_result_is_held_until_user_action(self):
        element = re.search(r'<div id="results"[^>]+>',self.source)
        self.assertIsNotNone(element)
        self.assertIn("hidden",element.group(0))
        self.assertIn('button.addEventListener("click"',self.source)
        self.assertIn("reset.addEventListener",self.source)

    def test_accessible_live_status_and_focus(self):
        self.assertIn('role="status" aria-live="polite"',self.source)
        self.assertIn('tabindex="-1" id="results-title"',self.source)
        self.assertIn('document.getElementById("results-title").focus()',self.source)
        self.assertIn("prefers-reduced-motion",self.source)
        self.assertIn(":focus-visible",self.source)
        self.assertIn('scope="col"',self.source)

    def test_not_a_backup_claim(self):
        self.assertIn("This is an inventory preview, not a backup",self.source)
        self.assertIn("No real files are opened",self.source)
        self.assertIn("This is not a backup",self.source)
        self.assertIn("Planned · not available",self.source)

    def test_sample_report_carries_synthetic_evidence_class(self):
        self.assertIn('evidence_class:"SYNTHETIC_ONLY"',self.source)
        self.assertIn('independent_backup_verified:false',self.source)
        self.assertIn('provider_sessions_modified:0',self.source)
        self.assertIn('delete_safe:false',self.source)


if __name__ == "__main__":
    unittest.main()
