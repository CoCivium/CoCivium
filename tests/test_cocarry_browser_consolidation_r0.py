"""Adversarial public CoCarry contract tests; no provider, browser or X2 access."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from CoCarryBrowserConsolidationR0 import Hold, validate

CONTRACT = ROOT / "docs/Evolution/COCARRY_BROWSER_INDEPENDENT_RECOVERY_R0.json"
FRONTIER = ROOT / "docs/Evolution/FRONTIER_EVIDENCE_INDEX_R0.json"


class CoCarryBrowserContractTests(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.front = json.loads(FRONTIER.read_text(encoding="utf-8"))
        self.rec = self.doc["session_record"]

    def test_public_current_source_passes_without_false_runtime_claim(self):
        result = validate(self.doc, self.front)
        self.assertEqual(result["state"], "PASS_PUBLIC_SYNTHETIC_SOURCE_CONTRACT_ONLY")
        self.assertFalse(result["tab_closure_authorized"])
        self.assertFalse(result["firefox_reopen_verified"])
        self.assertEqual(result["x2_receiver_readproof"], "NOT_OBSERVED")
        self.assertEqual(result["live_session_inventory"], "NOT_OBSERVED")

    def test_missing_or_unknown_front_not_silent(self):
        self.rec["front_ids"].append("unknown-1984")
        with self.assertRaisesRegex(Hold, "HOLD_UNRESOLVED_FRONT_REF"):
            validate(self.doc, self.front)

    def test_duplicated_work_front_rejected(self):
        self.rec["front_ids"].append(self.rec["front_ids"][0])
        with self.assertRaisesRegex(Hold, "HOLD_FRONT_REFS"):
            validate(self.doc, self.front)

    def test_sleeping_without_wake_rejected(self):
        self.rec["next_trigger"] = None
        with self.assertRaisesRegex(Hold, "HOLD_NO_RECOVERY_WAKE"):
            validate(self.doc, self.front)

    def test_claimed_complete_from_tab_closure_rejected(self):
        self.rec["state"] = "completed"
        with self.assertRaisesRegex(Hold, "HOLD_LIVE_OR_FINISHED_STATUS_UNPROVEN"):
            validate(self.doc, self.front)

    def test_real_lease_cannot_be_implied(self):
        self.rec["lease"] = {"writer": "model-a"}
        with self.assertRaisesRegex(Hold, "HOLD_NO_REAL_AUTHORITY"):
            validate(self.doc, self.front)

    def test_fake_source_commit_cannot_promote_synthetic_fixture(self):
        self.rec["source_commit"] = "a"*40
        with self.assertRaisesRegex(Hold, "HOLD_SOURCE_VERIFICATION_NOT_PERFORMED"):
            validate(self.doc, self.front)

    def test_private_chat_url_field_must_never_enter_public_record(self):
        self.rec["chat_url"] = "https://chatgpt.com/c/private-chat-id"
        with self.assertRaisesRegex(Hold, "HOLD_RAW_PRIVATE_FIELD"):
            validate(self.doc, self.front)

    def test_hidden_private_chat_link_in_evidence_ref_is_rejected(self):
        self.rec["evidence_refs"].append("https://chatgpt.com/c/private-chat-id")
        with self.assertRaisesRegex(Hold, "HOLD_PRIVATE_LOCATOR_OR_TOKEN"):
            validate(self.doc, self.front)

    def test_gmail_draft_link_not_public_evidence(self):
        self.rec["evidence_refs"] = ["https://mail.google.com/mail/u/0/#drafts"]
        with self.assertRaisesRegex(Hold, "HOLD_PRIVATE_LOCATOR_OR_TOKEN"):
            validate(self.doc, self.front)

    def test_email_address_in_public_metadata_rejected(self):
        self.rec["objective"] = "Contact observer@example.com about the work"
        with self.assertRaisesRegex(Hold, "HOLD_PRIVATE_ADDRESS"):
            validate(self.doc, self.front)

    def test_public_github_url_with_token_query_rejected(self):
        self.rec["evidence_refs"] = [
            "https://github.com/CoCivium/CoCivium/blob/main/README.md?token=fake"
        ]
        with self.assertRaisesRegex(Hold, "HOLD_NONPUBLIC_EVIDENCE_REF"):
            validate(self.doc, self.front)

    def test_no_false_ack_added_to_record(self):
        self.rec["receiver_ack"] = True
        with self.assertRaisesRegex(Hold, "HOLD_RECORD_SHAPE"):
            validate(self.doc, self.front)

    def test_unverified_blocker_removal_rejected(self):
        self.rec["blocked_claims"].remove("LIVE_SESSION_RECOVERY")
        with self.assertRaisesRegex(Hold, "HOLD_BLOCKERS_UNPRESERVED"):
            validate(self.doc, self.front)

    def test_recovery_rail_cannot_disappear(self):
        self.doc["invariants"].remove(
            "Close-tab must not delete a durable work record"
        )
        with self.assertRaisesRegex(Hold, "HOLD_CONTINUITY_RAIL_MISSING"):
            validate(self.doc, self.front)

    def test_independent_reopen_gate_cannot_disappear(self):
        self.doc["migration_gates"].remove(
            "Reopen work in Firefox or another browser without manual context paste"
        )
        with self.assertRaisesRegex(Hold, "HOLD_REOPEN_PROOF_GATES_MISSING"):
            validate(self.doc, self.front)

    def test_browser_surface_not_new_authority(self):
        self.doc["browser_policy"]["coBrowserAdmin"] = "authority to send mail"
        with self.assertRaisesRegex(Hold, "HOLD_BROWSER_POLICY_DRIFT"):
            validate(self.doc, self.front)

    def test_private_custody_not_public_fixture(self):
        self.rec["custody"] = "private-cocivium"
        with self.assertRaisesRegex(Hold, "HOLD_NO_REAL_AUTHORITY"):
            validate(self.doc, self.front)

    def test_evidence_ref_not_external_receiver_ack(self):
        self.rec["evidence_refs"].append(
            "https://github.com/CoCivium/CoCivium/blob/main/SESSION_BOOTSTRAP.md"
        )
        r = validate(self.doc, self.front)
        self.assertTrue(r["public_pointer_ne_receiver_ack"])
        self.assertEqual(r["x2_receiver_readproof"], "NOT_OBSERVED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
