"""Theme fronts must not increase privacy, authority or product capability claims."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "ai/product/repozipper-ai-history-theme-projections-r0.json"
EXPECTED = {"protect", "find", "continue", "freedom", "family", "teams", "create", "open"}
FORBIDDEN = {"network_access", "provider_credentials", "provider_chat_deletion",
             "account_creation", "auto_upload", "auto_provider_sync",
             "auto_share_private_data", "auto_scheduler_creation", "source_transcript_publication"}


class ThemeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))

    def test_all_themes_share_one_engine(self):
        d = self.spec
        self.assertEqual(d["engine_path"], "examples/repozipper/ai_history_intake_r0.py")
        self.assertEqual(d["default_mode"], "inspect")
        self.assertEqual({p["id"] for p in d["theme_profiles"]}, EXPECTED)
        self.assertEqual(len(d["theme_profiles"]), len(EXPECTED))
        self.assertTrue(all(p["mode"] in d["engine_modes"] for p in d["theme_profiles"]))

    def test_no_theme_can_grant_more_authority(self):
        d = self.spec
        self.assertTrue(all(d["controls"].get(k) is False for k in FORBIDDEN))
        for p in d["theme_profiles"]:
            self.assertNotIn("controls", p)
            self.assertNotIn("permissions", p)
            self.assertNotIn("cloud_upload", p)

    def test_future_features_are_explicitly_locked(self):
        d = self.spec
        self.assertEqual(d["state"], "SOURCE_TEST_CANDIDATE__NOT_DEPLOYED_OR_PUBLIC_SERVICE")
        self.assertTrue(all(p["next_locked"] for p in d["theme_profiles"]))
        self.assertIn("PUBLIC_SERVICE_AVAILABLE", d["prohibited_claims"])
        self.assertIn("AUTOMATIC_ALL_PROVIDER_BACKUP", d["prohibited_claims"])
        self.assertIn("ZIP_NE_INDEPENDENT_BACKUP", d["evidence_boundaries"])

    def test_temporary_storage_is_not_backup(self):
        d = self.spec
        self.assertIn("Downloads/CoTemp", d["default_working_root"])
        self.assertIn("temporary workspace only", d["default_working_root"])

    def test_first_use_does_not_require_account(self):
        d = self.spec
        self.assertFalse(d["controls"]["account_creation"])
        self.assertFalse(d["controls"]["auto_upload"])
        self.assertEqual(d["default_intake"], "USER_SELECTED_LOCAL_ZIP_ONLY")

    def test_measurement_is_required_per_theme(self):
        for p in self.spec["theme_profiles"]:
            self.assertTrue(p["metric"])
            self.assertTrue(p["visible_proof"])
            self.assertTrue(p["strategy_leg"])
            self.assertTrue(p["first_action"])

    def test_feedback_requires_review_before_cross_theme_adoption(self):
        d = self.spec["feedback_contract"]
        self.assertEqual(d["cross_theme_promotion"],
                         "REQUIRES_INDEPENDENT_TEST_AND_NO_PRIVACY_OR_AUTHORITY_EXPANSION")
        self.assertTrue(d["private_data_policy"].startswith("NEVER_ECHO"))
        self.assertIn("STOP_IF_NO_MEASURED_USER_BENEFIT", d["bounded_recursion"])


if __name__ == "__main__":
    unittest.main()
