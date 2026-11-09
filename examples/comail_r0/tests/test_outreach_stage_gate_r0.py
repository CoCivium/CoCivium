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




class BoundedEvolutionTests(unittest.TestCase):
    """One candidate successor per call; never a provider side effect."""

    def setUp(self):
        GateTests.setUp(self)

    def test_evolution_distinct_content_clears_approval(self):
        from outreach_stage_gate_r0 import propose_evolution
        new, receipt = propose_evolution(self.item, proposed_content_sha256=dig('v2'),
                                          change_kind='CLAIM_CORRECTION', depth=0)
        self.assertEqual(receipt['state'], 'SUCCESSOR_PROPOSED_UNAPPLIED')
        self.assertEqual(new.content_sha256, dig('v2'))
        self.assertIsNone(new.reviewed_content_sha256)
        self.assertIsNone(new.approved_content_sha256)
        self.assertIsNone(new.specific_send_authority_ref)
        self.assertEqual(evaluate(new)['state'], 'STAGED_HELD')
        self.assertEqual(self.item.approved_content_sha256, self.item.content_sha256)
        self.assertFalse(receipt['provider_draft_edited'])

    def test_evolution_unchanged_digest_quiesces(self):
        from outreach_stage_gate_r0 import propose_evolution
        new, receipt = propose_evolution(self.item, proposed_content_sha256=self.item.content_sha256,
                                          change_kind='CONTEXT_UPDATE', depth=0)
        self.assertIs(new, self.item)
        self.assertEqual(receipt['state'], 'QUIESCE_NO_MATERIAL_CHANGE')

    def test_evolution_turtle_budget_quiesces(self):
        from outreach_stage_gate_r0 import propose_evolution
        new, receipt = propose_evolution(self.item, proposed_content_sha256=dig('proposal'),
                                          change_kind='CHALLENGE', depth=4, budget=4)
        self.assertIs(new, self.item)
        self.assertEqual(receipt['state'], 'QUIESCE_TURTLE_BUDGET')

    def test_stale_source_holds_without_generating(self):
        from outreach_stage_gate_r0 import propose_evolution
        stale = replace(self.item, current_source_revision='source-2')
        new, receipt = propose_evolution(stale, proposed_content_sha256=dig('proposal'),
                                          change_kind='CHALLENGE', depth=0)
        self.assertIs(new, stale)
        self.assertEqual(receipt['state'], 'HOLD_UPSTREAM_SOURCE_DRIFT')

    def test_evolution_rejects_unknown_reason(self):
        from outreach_stage_gate_r0 import propose_evolution
        with self.assertRaises(ValueError):
            propose_evolution(self.item, proposed_content_sha256=dig('proposal'),
                              change_kind='AUTO_SEND', depth=0)

    def test_evolution_rejects_boolean_depth_and_huge_budget(self):
        from outreach_stage_gate_r0 import propose_evolution
        for depth, budget in ((False, 4), (-1, 4), (1, 9), (5, 4)):
            with self.subTest(depth=depth, budget=budget):
                with self.assertRaises(ValueError):
                    propose_evolution(self.item, proposed_content_sha256=dig('proposal'),
                                      change_kind='ACCESSIBILITY', depth=depth, budget=budget)

    def test_recursion_terminates_at_budget(self):
        from outreach_stage_gate_r0 import propose_evolution
        base = self.item
        for depth in range(3):
            base, receipt = propose_evolution(base, proposed_content_sha256=dig('v'+str(depth)),
                                              change_kind='CHALLENGE', depth=depth, budget=3)
            self.assertEqual(receipt['depth'], depth+1)
            self.assertEqual(receipt['state'], 'SUCCESSOR_PROPOSED_UNAPPLIED')
        unchanged, hold = propose_evolution(base, proposed_content_sha256=dig('v3'),
                                             change_kind='CHALLENGE', depth=3, budget=3)
        self.assertIs(unchanged, base)
        self.assertEqual(hold['state'], 'QUIESCE_TURTLE_BUDGET')

    def test_competing_successors_do_not_clobber_parent(self):
        from outreach_stage_gate_r0 import propose_evolution
        left, l = propose_evolution(self.item, proposed_content_sha256=dig('left'),
                                     change_kind='CHALLENGE', depth=0)
        right, r = propose_evolution(self.item, proposed_content_sha256=dig('right'),
                                      change_kind='CHALLENGE', depth=0)
        self.assertEqual(l['parent_content_sha256'], r['parent_content_sha256'])
        self.assertNotEqual(left.content_sha256, right.content_sha256)
        self.assertEqual(self.item.content_sha256, l['parent_content_sha256'])
        self.assertFalse(l['receiver_ack'])

    def test_receipt_contains_no_mailbox_recipient_or_private_body(self):
        from outreach_stage_gate_r0 import propose_evolution
        _, receipt = propose_evolution(self.item, proposed_content_sha256=dig('private content'),
                                         change_kind='RETRACTION', depth=0)
        report = str(receipt)
        for secret in ('account-A', 'recipient:fixture', 'private content', 'synthetic-work-A'):
            self.assertNotIn(secret, report)
        self.assertEqual(receipt['effect'], 'NONE')

if __name__ == "__main__":
    unittest.main(verbosity=2)
