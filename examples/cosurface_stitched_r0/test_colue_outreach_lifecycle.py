"""CoLUE+ synthetic outreach lifecycle: drafts are not sends.

Privacy preserving, pure-state fixtures. No Gmail API, real addresses or mail
effects. Sender/account identity is a distinct key from subject or recipient.
"""
from dataclasses import dataclass
import unittest


@dataclass(frozen=True)
class Outreach:
    work_id: str
    mailbox_key: str
    source_revision: str
    draft_revision: str = ""
    recipient_qualified: bool = False
    consent_reviewed: bool = False
    approval_proven: bool = False
    held: bool = False
    revoked: bool = False
    source_stale: bool = False
    sent_receipt: str = ""
    delivery_receipt: str = ""
    bounced: bool = False
    reply_thread_verified: bool = False
    followup_authorized: bool = False


def status(x):
    """One current projection; unproven states never advance by optimism."""
    if not x.work_id or not x.mailbox_key or not x.source_revision:
        return "INVALID_PROVENANCE"
    if x.revoked:
        return "REVOKED"
    if x.bounced:
        return "DELIVERY_FAILED" if x.sent_receipt else "CONFLICTING_BOUNCE"
    if x.reply_thread_verified:
        return "REPLY_OBSERVED" if x.sent_receipt else "UNLINKED_REPLY"
    if x.delivery_receipt:
        return "DELIVERY_OBSERVED" if x.sent_receipt else "UNLINKED_DELIVERY"
    if x.sent_receipt:
        return "SENT_PROVEN"
    if x.held:
        return "HELD_FOR_REVIEW"
    if x.source_stale:
        return "STALE_CONTEXT"
    if not x.draft_revision:
        return "IDEA"
    if not x.recipient_qualified:
        return "NO_QUALIFIED_RECIPIENT"
    if not x.consent_reviewed or not x.approval_proven:
        return "AWAIT_REVIEW"
    return "APPROVED_NOT_SENT"


def may_followup(x):
    return (status(x) in ("SENT_PROVEN", "DELIVERY_OBSERVED")
            and x.followup_authorized and not x.revoked and not x.bounced)


def work_key(x):
    return (x.mailbox_key, x.work_id)


class OutreachLifecycleTests(unittest.TestCase):
    def obj(self, **kwargs):
        base = dict(work_id="synthetic-1", mailbox_key="test-mailbox-a",
                    source_revision="sha123", draft_revision="draft-v1",
                    recipient_qualified=True, consent_reviewed=True)
        return Outreach(**{**base, **kwargs})

    def test_unsent_draft_not_delivered(self):
        self.assertEqual(status(self.obj()), "AWAIT_REVIEW")

    def test_sender_approved_is_not_sent(self):
        self.assertEqual(status(self.obj(approval_proven=True)), "APPROVED_NOT_SENT")

    def test_missing_recipient_blocks(self):
        self.assertEqual(status(self.obj(recipient_qualified=False, approval_proven=True)),
                         "NO_QUALIFIED_RECIPIENT")

    def test_different_mailboxes_never_merge(self):
        self.assertNotEqual(work_key(self.obj()), work_key(self.obj(mailbox_key="other")))

    def test_stale_source_blocks(self):
        self.assertEqual(status(self.obj(source_stale=True, approval_proven=True)),
                         "STALE_CONTEXT")

    def test_review_hold_wins(self):
        self.assertEqual(status(self.obj(held=True, approval_proven=True)), "HELD_FOR_REVIEW")

    def test_sent_receipt_is_not_delivery(self):
        self.assertEqual(status(self.obj(sent_receipt="provider-sent")), "SENT_PROVEN")

    def test_delivery_requires_sent(self):
        self.assertEqual(status(self.obj(delivery_receipt="smtp-log")), "UNLINKED_DELIVERY")

    def test_bounce_overrides_delivery(self):
        self.assertEqual(status(self.obj(sent_receipt="sent", delivery_receipt="delivered",
                                         bounced=True)), "DELIVERY_FAILED")

    def test_reply_requires_sent_thread_proof(self):
        self.assertEqual(status(self.obj(reply_thread_verified=True)), "UNLINKED_REPLY")

    def test_reply_with_sent_is_observed(self):
        self.assertEqual(status(self.obj(sent_receipt="sent", reply_thread_verified=True)),
                         "REPLY_OBSERVED")

    def test_followup_requires_authorized_nonbounced_sent(self):
        self.assertFalse(may_followup(self.obj(sent_receipt="sent")))
        self.assertTrue(may_followup(self.obj(sent_receipt="sent",
                                              followup_authorized=True)))
        self.assertFalse(may_followup(self.obj(sent_receipt="sent",
                                               followup_authorized=True, bounced=True)))

    def test_revoke_precedes_sent_state(self):
        self.assertEqual(status(self.obj(sent_receipt="sent", revoked=True)), "REVOKED")

    def test_no_real_recipient_field_exposed(self):
        self.assertNotIn("recipient_address", self.obj().__dict__)


if __name__ == "__main__":
    unittest.main()
