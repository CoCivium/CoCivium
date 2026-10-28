#!/usr/bin/env python3
import copy
import hashlib
import unittest
from CoOutreachWhoSaidWhatGateR0 import validate, recipient_digest


def fixture():
    bodyhash = hashlib.sha256(b"fictional approved example").hexdigest()
    people = [{
        "kind": "to", "address": "sample-recipient@example.invalid",
        "identity_verified": True, "contact_state": "CLEAR", "explicit_stop_request": False,
        "private_suppression_check_ref": "private:fictional-check", "contact_basis_ref": "private:fictional-request",
        "content_fit_reviewed": True,
    }]
    return {
        "intent": "ONE_OUTBOUND_MESSAGE_REVIEW",
        "sender": {"authenticated_mailbox": "sample-sender@example.invalid",
                   "from_header": "sample-sender@example.invalid",
                   "mailbox_proof_ref": "private:fictional-mailbox", "account_principal": "fictional-principal",
                   "actual_actor": "fictional-human-actor", "actor_kind": "AI_ASSISTED_HUMAN",
                   "authoritative_actor_proof_ref": "private:fictional-actor",
                   "delegation_proof_ref": "private:fictional-delegation",
                   "claims_ai_unaccountable_for_account": False},
        "message": {"body_sha256": bodyhash, "top_level_author": "fictional-human-actor",
                    "quotes_distinguished": True, "claims_reviewed": True,
                    "attachments_reviewed": True, "thread_context_checked": True,
                    "message_mode": "reply", "reply_parent_message_id": "fictional-parent"},
        "recipients": people,
        "review": {"reviewed_body_sha256": bodyhash,
                   "reviewed_recipients_sha256": recipient_digest(people),
                   "headers_preflight_checked": True, "reviewer_identity_proof_ref": "private:fictional-human-review",
                   "human_approved": True, "bcc_explicitly_reviewed": True},
    }


class IdentityGateTests(unittest.TestCase):
    def setUp(self):
        self.base = fixture()

    def test_fixture_is_only_reviewable_not_sent(self):
        self.assertEqual(validate(self.base)["state"], "STRUCTURALLY_REVIEWABLE_ONLY")
        self.assertEqual(validate(self.base)["effect"], "NONE")

    def expect_hold(self, mutation, code):
        p = copy.deepcopy(self.base)
        mutation(p)
        report = validate(p)
        self.assertEqual(report["state"], "HOLD")
        self.assertIn(code, report["reasons"])

    def test_from_mismatch(self):
        self.expect_hold(lambda p: p["sender"].update(from_header="other@example.invalid"), "FROM_MAILBOX_MISMATCH")

    def test_unbound_actor(self):
        self.expect_hold(lambda p: p["sender"].pop("actual_actor"), "UNBOUND_ACTOR")

    def test_delegation_missing(self):
        self.expect_hold(lambda p: p["sender"].pop("delegation_proof_ref"), "NO_AGENT_DELEGATION_PROOF_POINTER")

    def test_wrong_top_level_author(self):
        self.expect_hold(lambda p: p["message"].update(top_level_author="quoted-author"), "TOP_LEVEL_AUTHOR_ACTOR_MISMATCH")

    def test_quote_confusion(self):
        self.expect_hold(lambda p: p["message"].update(quotes_distinguished=False), "QUOTE_AUTHORSHIP_NOT_SEPARATED")

    def test_opt_out(self):
        self.expect_hold(lambda p: p["recipients"][0].update(explicit_stop_request=True), "RECIPIENT_0_OPT_OUT")

    def test_contact_state_unknown(self):
        self.expect_hold(lambda p: p["recipients"][0].update(contact_state="UNKNOWN"), "RECIPIENT_0_CONTACT_NOT_CLEAR")

    def test_no_suppression_check(self):
        self.expect_hold(lambda p: p["recipients"][0].pop("private_suppression_check_ref"), "RECIPIENT_0_NO_SUPPRESSION_READPROOF")

    def test_wrong_recipient(self):
        self.expect_hold(lambda p: p["recipients"][0].update(address="other@example.invalid"), "REVIEWED_RECIPIENTS_CHANGED")

    def test_body_changed(self):
        self.expect_hold(lambda p: p["message"].update(body_sha256="a"*64), "REVIEWED_BODY_CHANGED")

    def test_missing_reply_parent(self):
        self.expect_hold(lambda p: p["message"].update(reply_parent_message_id=""), "REPLY_PARENT_UNVERIFIED")

    def test_bcc_unreviewed(self):
        self.expect_hold(lambda p: p["review"].update(bcc_explicitly_reviewed=False), "BCC_NOT_REVIEWED")

    def test_ai_accountability_deflection(self):
        self.expect_hold(lambda p: p["sender"].update(claims_ai_unaccountable_for_account=True), "FALSE_AI_ACCOUNTABILITY_CLAIM")

    def test_unverified_recipient(self):
        self.expect_hold(lambda p: p["recipients"][0].update(identity_verified=False), "RECIPIENT_0_IDENTITY_UNVERIFIED")

    def test_approval_missing(self):
        self.expect_hold(lambda p: p["review"].update(human_approved=False), "HUMAN_APPROVAL_MISSING")

    def test_missing_message(self):
        self.assertEqual(validate({"sender": {}})["state"], "HOLD")

if __name__ == "__main__":
    unittest.main(verbosity=2)
