"""CoLUE R0 synthetic revisions: history survives editing; none sends mail."""
from dataclasses import replace
import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from outreach_stage_gate_r0 import DraftEvidence
from revision_lineage_r0 import DraftRevision, analyze


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class RevisionLineageTests(unittest.TestCase):
    def setUp(self):
        self.first = DraftRevision(
            work_id="synthetic-work-A", mailbox_id="account-A", draft_id="draft-A",
            revision_id="r1", predecessor_id=None, content_sha256=digest("first"),
            change_reason_ref="synthetic:initial", evidence_ref="synthetic:source1")
        self.second = DraftRevision(
            work_id="synthetic-work-A", mailbox_id="account-A", draft_id="draft-A",
            revision_id="r2", predecessor_id="r1", content_sha256=digest("second"),
            change_reason_ref="synthetic:revised", evidence_ref="synthetic:source2")
        self.revisions = (self.first, self.second)
        self.gate = DraftEvidence(
            work_id="synthetic-work-A", draft_id="draft-A",
            draft_mailbox_id="account-A", connected_mailbox_id="account-A",
            source_revision="r2", current_source_revision="r2",
            content_sha256=digest("second"),
            recipient_route_ref="synthetic:recipient",
            recipient_route_verified=True,
            relationship_provenance_ref="synthetic:relationship",
            sender_authorized_for_mailbox=True,
            thread_or_new_route_verified=True,
            latest_thread_and_sent_checked=True,
            duplicate_outreach_checked=True,
            consent_or_lawful_basis_ref="synthetic:consent",
            factual_claims_reviewed=True,
            reviewed_content_sha256=digest("second"),
            approved_content_sha256=digest("second"),
            specific_send_authority_ref="synthetic:effect-gate")

    def holds(self, expected, revisions=None, gate=None):
        with self.assertRaisesRegex(ValueError, expected):
            analyze(self.revisions if revisions is None else revisions,
                    self.gate if gate is None else gate)

    def test_valid_head_preserves_both_revisions_but_never_sends(self):
        record = analyze(self.revisions, self.gate)
        self.assertEqual(record["revision_count"], 2)
        self.assertEqual(record["head_revision"], "r2")
        self.assertEqual(record["state"], "SOURCE_STAGE_ELIGIBLE_NOT_SENT")
        self.assertEqual(record["provider_effect"], "NONE")
        self.assertFalse(record["recipient_acceptance_verified"])
        self.assertEqual(record["evidence_status"], "CALLER_SUPPLIED_SOURCE_ONLY")

    def test_content_change_is_not_quality_improvement(self):
        record = analyze(self.revisions, self.gate)
        self.assertEqual(record["recursion_result"], "CONTENT_CHANGED_QUALITY_NOT_PROVEN")
        self.assertIn("CONTENT_CHANGE_NE_IMPROVEMENT", record["nonclaims"])

    def test_same_content_new_revision_is_idempotent_not_a_gain(self):
        second = replace(self.second, content_sha256=self.first.content_sha256)
        gate = replace(self.gate,
                       content_sha256=self.first.content_sha256,
                       reviewed_content_sha256=self.first.content_sha256,
                       approved_content_sha256=self.first.content_sha256)
        record = analyze((self.first, second), gate)
        self.assertEqual(record["recursion_result"], "IDEMPOTENT_NO_CONTENT_CHANGE")
        self.assertEqual(record["provider_effect"], "NONE")

    def test_latest_content_invalidates_old_review_and_approval(self):
        gate = replace(self.gate, reviewed_content_sha256=self.first.content_sha256,
                       approved_content_sha256=self.first.content_sha256)
        record = analyze(self.revisions, gate)
        self.assertEqual(record["state"], "STAGED_HELD")
        self.assertIn("HOLD_REVIEW_STALE_OR_ABSENT", record["holds"])
        self.assertIn("HOLD_APPROVAL_STALE_OR_ABSENT", record["holds"])

    def test_gate_revision_stale_fails_closed(self):
        gate = replace(self.gate, current_source_revision="r3")
        record = analyze(self.revisions, gate)
        self.assertIn("HOLD_UNBOUND_CURRENT_REVISION", record["holds"])
        self.assertIn("HOLD_SOURCE_REVISION_CHANGED", record["holds"])

    def test_gate_digest_unbound_fails_closed(self):
        gate = replace(self.gate, content_sha256=digest("unseen-edit"))
        record = analyze(self.revisions, gate)
        self.assertIn("HOLD_UNBOUND_CURRENT_CONTENT", record["holds"])

    def test_no_consent_never_eligible_to_send(self):
        gate = replace(self.gate, consent_or_lawful_basis_ref=None)
        record = analyze(self.revisions, gate)
        self.assertIn("HOLD_CONSENT_OR_LAWFUL_BASIS", record["holds"])
        self.assertEqual(record["provider_effect"], "NONE")

    def test_wrong_connected_mailbox_never_eligible(self):
        gate = replace(self.gate, connected_mailbox_id="account-B")
        record = analyze(self.revisions, gate)
        self.assertIn("HOLD_WRONG_MAILBOX", record["holds"])
        self.assertEqual(record["provider_effect"], "NONE")

    def test_root_must_have_no_predecessor(self):
        first = replace(self.first, predecessor_id="unknown")
        self.holds("HOLD_ROOT_HAS_PREDECESSOR", (first, self.second))

    def test_missing_intermediate_revision_is_not_silently_superseded(self):
        second = replace(self.second, predecessor_id="r0")
        self.holds("HOLD_GAP_CYCLE_OR_SILENT_SUPERSESSION", (self.first, second))

    def test_cycle_is_not_accepted(self):
        second = replace(self.second, predecessor_id="r2")
        self.holds("HOLD_GAP_CYCLE_OR_SILENT_SUPERSESSION", (self.first, second))

    def test_duplicate_revision_id_is_not_accepted(self):
        second = replace(self.second, revision_id="r1")
        self.holds("HOLD_DUPLICATE_REVISION", (self.first, second))

    def test_cross_mailbox_revision_rejected(self):
        second = replace(self.second, mailbox_id="account-B")
        self.holds("HOLD_MIXED_WORK_MAILBOX_OR_DRAFT", (self.first, second))

    def test_cross_work_object_revision_rejected(self):
        second = replace(self.second, work_id="synthetic-work-B")
        self.holds("HOLD_MIXED_WORK_MAILBOX_OR_DRAFT", (self.first, second))

    def test_cross_draft_revision_rejected(self):
        second = replace(self.second, draft_id="draft-B")
        self.holds("HOLD_MIXED_WORK_MAILBOX_OR_DRAFT", (self.first, second))

    def test_malformed_sha_rejected(self):
        second = replace(self.second, content_sha256="self-verified")
        self.holds("HOLD_BAD_CONTENT_DIGEST", (self.first, second))

    def test_missing_provenance_rejected(self):
        second = replace(self.second, evidence_ref="")
        self.holds("HOLD_BAD_PROVENANCE_REF", (self.first, second))

    def test_empty_lineage_rejected(self):
        self.holds("HOLD_REVISION_BUDGET_OR_TYPE", ())

    def test_excessive_recursion_fails_closed(self):
        revisions = [self.first]
        for i in range(2, 35):
            revisions.append(replace(self.second, revision_id="r"+str(i),
                                     predecessor_id=revisions[-1].revision_id))
        self.holds("HOLD_REVISION_BUDGET_OR_TYPE", tuple(revisions))

    def test_metadata_digest_is_deterministic(self):
        a = analyze(self.revisions, self.gate)
        b = analyze(self.revisions, self.gate)
        self.assertEqual(a, b)
        self.assertEqual(len(a["lineage_metadata_sha256"]), 64)

    def test_changed_reason_changes_metadata_digest_not_content(self):
        a = analyze(self.revisions, self.gate)
        edited = replace(self.second, change_reason_ref="synthetic:counterexample")
        b = analyze((self.first, edited), self.gate)
        self.assertNotEqual(a["lineage_metadata_sha256"], b["lineage_metadata_sha256"])
        self.assertEqual(a["head_content_sha256"], b["head_content_sha256"])

    def test_fully_staged_is_still_not_a_provider_receipt(self):
        a = analyze(self.revisions, self.gate)
        self.assertEqual(a["next_safe_action"], "REQUIRE_INDEPENDENT_PROVIDER_EFFECT_AND_RECEIPT")
        self.assertIn("SENT_RECORDS_ARE_SEPARATE_IMMUTABLE_EVENTS", a["nonclaims"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
