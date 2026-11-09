"""Source-only CoLUE negative controls, using synthetic IDs and digest."""
from dataclasses import replace
import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from outreach_stage_gate_r0 import DraftEvidence, evaluate


def dig(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class GateTests(unittest.TestCase):
    def setUp(self):
        digest = dig("private-message-is-NOT-part-of-this-public-fixture")
        self.item = DraftEvidence(
            work_id="synthetic-work-A", draft_id="draft-A",
            draft_mailbox_id="account-A", connected_mailbox_id="account-A",
            source_revision="source-1", current_source_revision="source-1",
            content_sha256=digest, recipient_route_ref="recipient:fixture",
            recipient_route_verified=True, relationship_provenance_ref="relation:fixture",
            sender_authorized_for_mailbox=True,
            thread_or_new_route_verified=True, latest_thread_and_sent_checked=True,
            duplicate_outreach_checked=True,
            consent_or_lawful_basis_ref="basis:explicit-reviewed-fixture",
            factual_claims_reviewed=True, reviewed_content_sha256=digest,
            approved_content_sha256=digest,
            specific_send_authority_ref="authorization:separate-effect-gate-fixture",
        )

    def holds(self, reason, **kwargs):
        result = evaluate(replace(self.item, **kwargs))
        self.assertEqual(result["state"], "STAGED_HELD")
        self.assertIn(reason, result["holds"])
        self.assertEqual(result["observed_effect"], "NONE")

    def test_ready_is_still_unsent_and_unverified(self):
        result = evaluate(self.item)
        self.assertEqual(result["state"], "PROVIDER_SEND_CANDIDATE_NOT_SENT")
        self.assertIsNone(result["sender_provider_receipt"])
        self.assertFalse(result["receiver_acceptance_verified"])

    def test_inseed_draft_cannot_be_sent_by_other_mailbox(self):
        self.holds("HOLD_WRONG_MAILBOX", draft_mailbox_id="inseed:synthetic",
                   connected_mailbox_id="other-mail:synthetic")

    def test_changed_source_must_requalify(self):
        self.holds("HOLD_SOURCE_REVISION_CHANGED", current_source_revision="source-2")

    def test_route_absent(self):
        self.holds("HOLD_RECIPIENT_ROUTE", recipient_route_ref=None)

    def test_unverified_route(self):
        self.holds("HOLD_RECIPIENT_ROUTE", recipient_route_verified=False)

    def test_relationship_absent(self):
        self.holds("HOLD_RELATION_PROVENANCE", relationship_provenance_ref=None)

    def test_wrong_sender_authority(self):
        self.holds("HOLD_SENDER_AUTHORITY", sender_authorized_for_mailbox=False)

    def test_unbound_thread(self):
        self.holds("HOLD_THREAD_CONTEXT", thread_or_new_route_verified=False)

    def test_unread_newest_thread(self):
        self.holds("HOLD_THREAD_CONTEXT", latest_thread_and_sent_checked=False)

    def test_duplicate_outreach_not_checked(self):
        self.holds("HOLD_DUPLICATE_CHECK", duplicate_outreach_checked=False)

    def test_opt_out_blocks_even_with_approval(self):
        self.holds("HOLD_OPTOUT", opt_out=True)

    def test_no_consent_or_lawful_basis(self):
        self.holds("HOLD_CONSENT_OR_LAWFUL_BASIS", consent_or_lawful_basis_ref=None)

    def test_unreviewed_claims(self):
        self.holds("HOLD_FACTUAL_CLAIMS", factual_claims_reviewed=False)

    def test_review_invalidated_after_edit(self):
        self.holds("HOLD_REVIEW_STALE_OR_ABSENT", reviewed_content_sha256=dig("old draft"))

    def test_approval_invalidated_after_edit(self):
        self.holds("HOLD_APPROVAL_STALE_OR_ABSENT", approved_content_sha256=dig("old draft"))

    def test_missing_effect_authorization(self):
        self.holds("HOLD_SPECIFIC_SEND_AUTHORITY", specific_send_authority_ref=None)

    def test_no_personal_recipients_in_result(self):
        result = str(evaluate(self.item))
        self.assertNotIn("recipient:fixture", result)
        self.assertNotIn("basis:explicit-reviewed-fixture", result)

    def test_order_and_replay_deterministic(self):
        self.assertEqual(evaluate(self.item), evaluate(self.item))
        self.assertEqual(evaluate(replace(self.item, connected_mailbox_id="B"))["next_safe_action"],
                         "HOLD_WRONG_MAILBOX")

    def test_looks_like_false_is_not_boolean(self):
        with self.assertRaises(ValueError):
            evaluate(replace(self.item, duplicate_outreach_checked="false"))

    def test_malformed_digest_not_approved(self):
        with self.assertRaises(ValueError):
            evaluate(replace(self.item, content_sha256="not-a-hash"))

    def test_provided_authorization_does_not_mutate_provider(self):
        result = evaluate(self.item)
        self.assertEqual(result["observed_effect"], "NONE")
        self.assertEqual(result["next_safe_action"], "REQUIRE_SEPARATE_PROVIDER_EFFECT_AND_RECEIPT")


if __name__ == "__main__":
    unittest.main(verbosity=2)
