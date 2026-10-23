from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "examples" / "coandrewfirst" / "index.html"
README = ROOT / "examples" / "coandrewfirst" / "README.md"
SPEC = ROOT / "examples" / "co-evidence-bundle-r0.spec.json"
REPORT = ROOT / "docs" / "Operations" / "fixtures" / "coevidence-bundle-r0-20261022.json"


class CoAndrewFirstStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")
        cls.readme = README.read_text(encoding="utf-8")

    def test_required_inputs_exist(self):
        self.assertTrue(SPEC.is_file())
        self.assertTrue(REPORT.is_file())

    def test_five_onboarding_steps_are_present(self):
        for step in range(1, 6):
            self.assertIn(f'id="step{step}"', self.html)
            self.assertIn(f'data-step="{step}"', self.html)

    def test_evidence_urls_are_repository_relative(self):
        self.assertIn('const SPEC_URL = "../co-evidence-bundle-r0.spec.json";', self.html)
        self.assertIn(
            'const REPORT_URL = "../../docs/Operations/fixtures/coevidence-bundle-r0-20261022.json";',
            self.html,
        )
        external_fetches = re.findall(r'fetch\(\s*["\']https?://', self.html)
        self.assertEqual(external_fetches, [])

    def test_explicit_boundary_language_is_present(self):
        required = [
            "TEST_ONLY role bindings",
            "TEST_ONLY claims / relations",
            "live_session_sync: NOT_TESTED",
            "receiver_adoption: UNOBSERVED",
            "model_call_performed: false",
            "external_write_performed: false",
            "LOCAL_BROWSER_READ_AND_INTERACTION_ONLY",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.html)

    def test_provider_targets_are_nonexecuting_in_r0(self):
        for value in (
            "claude",
            "open_source",
            "openai_compatible",
            "historical_replay",
        ):
            self.assertIn(f'value="{value}"', self.html)
        self.assertIn("No model is called.", self.html)
        self.assertIn("Selecting another lane changes the receipt, not execution.", self.html)

    def test_challenge_mode_is_bounded(self):
        for challenge in ("live", "storage", "trust"):
            self.assertIn(f'data-challenge="{challenge}"', self.html)
        self.assertIn("Custom text is stored only in your local browser receipt.", self.html)

    def test_run_instructions_are_local_and_dependency_free(self):
        self.assertIn("python -m http.server 8000", self.readme)
        self.assertIn("No backend, account, model API, telemetry, cookies, or external write action is implemented.", self.readme)


if __name__ == "__main__":
    unittest.main()
