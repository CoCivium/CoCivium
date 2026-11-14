"""Privacy-negative controls for CoAll public session derivative R0.

No user transcript, personal data, provider access or publication takes place.
"""
from __future__ import annotations
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from CoAllSessionPublicProjectionGateR0 import review_candidate

REF = "https://github.com/CoCivium/CoCivium/blob/main/SESSION_BOOTSTRAP.md"

def candidate():
    return {
        "schema": "CoAll.SessionPublicDerivative.CandidateR0",
        "public_work_id": "cow:public-001",
        "title": "Portable source recovery",
        "summary": "A source-bound design candidate, not a recovered transcript.",
        "evidence_urls": [REF],
        "candidate_scope": "SYNTHETIC_CI_ONLY",
        "history_coverage": "BOUNDED_PARTIAL",
    }

class PublicDerivativeGateTests(unittest.TestCase):
    def assert_hold(self, item, expected):
        result = review_candidate(item)
        self.assertEqual(result["state"], "HOLD_UNQUALIFIED_INPUT")
        self.assertIn(expected, result["holds"])
        self.assertIsNone(result["local_preview"])
        self.assertEqual(result["effect"], "NONE")
        self.assertFalse(result["publication_authorized"])

    def test_valid_curated_still_requires_independent_review(self):
        x = review_candidate(candidate())
        self.assertEqual(x["state"], "HOLD_INDEPENDENT_PRIVACY_RIGHTS_CONSENT_REVIEW", x["holds"])
        self.assertFalse(x["publication_authorized"])
        self.assertEqual(x["receiver_ack"], "NOT_ESTABLISHED")
        self.assertEqual(x["cold_restore"], "NOT_TESTED")
        self.assertEqual(x["history_completeness"], "UNKNOWN")
        self.assertEqual(x["local_preview"]["work_id"], "cow:public-001")

    def test_email_in_summary(self):
        x = candidate(); x["summary"] = "A private person: somebody@example.org"
        self.assert_hold(x, "HELD_SUMMARY_RISK")

    def test_embedded_secret_word(self):
        x = candidate(); x["summary"] = "Contains an API key or other secret."
        self.assert_hold(x, "HELD_SUMMARY_RISK")

    def test_personal_paths(self):
        x = candidate(); x["summary"] = "Look in C:\\Users\\Person\\Downloads"
        self.assert_hold(x, "HELD_SUMMARY_RISK")

    def test_provider_chat_locator(self):
        x = candidate(); x["summary"] = "https://chatgpt.com/c/abcdef1234567890"
        self.assert_hold(x, "HELD_SUMMARY_RISK")

    def test_input_no_raw_transcript_fields(self):
        x = candidate(); x["messages"] = [{"role": "user", "content": "PRIVATE"}]
        self.assert_hold(x, "HELD_UNKNOWN_OR_MISSING_FIELDS")

    def test_input_no_original_session_id(self):
        x = candidate(); x["session_id"] = "private-original-id"
        self.assert_hold(x, "HELD_UNKNOWN_OR_MISSING_FIELDS")

    def test_no_private_source_digest(self):
        x = candidate(); x["source_sha256"] = "a"*64
        self.assert_hold(x, "HELD_UNKNOWN_OR_MISSING_FIELDS")

    def test_no_assumed_complete_history(self):
        x = candidate(); x["history_coverage"] = "COMPLETE"
        self.assert_hold(x, "HELD_UNSUPPORTED_COMPLETENESS")

    def test_no_auto_public_scope(self):
        x = candidate(); x["candidate_scope"] = "PUBLIC_RELEASE"
        self.assert_hold(x, "HELD_SCOPE")

    def test_no_external_evidence_link(self):
        x = candidate(); x["evidence_urls"] = ["https://example.org/private"]
        self.assert_hold(x, "HELD_PUBLIC_EVIDENCE_REFS")

    def test_no_git_issue_query(self):
        x = candidate(); x["evidence_urls"] = [REF + "?token=a"]
        self.assert_hold(x, "HELD_PUBLIC_EVIDENCE_REFS")

    def test_no_private_account_github_url(self):
        x = candidate(); x["evidence_urls"] = ["https://github.com/CoCivium/CoSteward/blob/main/secret"]
        self.assert_hold(x, "HELD_PUBLIC_EVIDENCE_REFS")

    def test_no_github_credentials_in_url(self):
        x = candidate(); x["evidence_urls"] = ["https://user:token@github.com/CoCivium/CoCivium/blob/main/README.md"]
        self.assert_hold(x, "HELD_PUBLIC_EVIDENCE_REFS")

    def test_no_markup_in_text(self):
        x = candidate(); x["summary"] = "Here is <script>evil</script>"
        self.assert_hold(x, "HELD_SUMMARY_RISK")

    def test_no_zero_width_injection(self):
        x = candidate(); x["title"] = "Safe\u200btitle"
        self.assert_hold(x, "HELD_TITLE_RISK")

    def test_empty_title_rejected(self):
        x = candidate(); x["title"] = ""
        self.assert_hold(x, "HELD_TITLE_RISK")

    def test_missing_evidence_rejected(self):
        x = candidate(); x["evidence_urls"] = []
        self.assert_hold(x, "HELD_PUBLIC_EVIDENCE_REFS")

    def test_no_duplicate_evidence(self):
        x = candidate(); x["evidence_urls"] = [REF, REF]
        self.assert_hold(x, "HELD_PUBLIC_EVIDENCE_REFS")

    def test_invalid_shape_never_echoes_payload(self):
        x = {"summary": "private payload"}
        r = review_candidate(x)
        self.assertNotIn("private payload", str(r))
        self.assertIsNone(r["local_preview"])

    def test_not_a_background_executor(self):
        src = (Path(__file__).resolve().parents[3] / "scripts" /
               "CoAllSessionPublicProjectionGateR0.py").read_text(encoding="utf-8")
        for forbidden in ("subprocess.", "os.system", "requests.", "urllib.request", "DELETE FROM", "git push"):
            self.assertNotIn(forbidden, src)

if __name__ == "__main__":
    unittest.main()
