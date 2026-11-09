"""Adversarial local CoLUE staging tests. No Gmail calls or send effects."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'colue_stage_r1.py'
spec = importlib.util.spec_from_file_location('colue', SOURCE)
colue = importlib.util.module_from_spec(spec)
spec.loader.exec_module(colue)


def packet():
    a = colue.content_sha256('synthetic v0')
    return dict(work_id='fixture-work-1', sender_mailbox_id='mailbox-a',
                connected_mailbox_id='mailbox-a', recipient_ref='fictional-recipient',
                thread_ref='thread-fixture-1', purpose_id='fictional-intent',
                versions=[dict(revision=0, content_sha256=a, predecessor_sha256=None)],
                approval_sha256=a, route_verified=True, thread_verified=True,
                claims_verified=True, consent_current=True, opt_out=False,
                approver_authorized=True, inbound_reply_readproof=False,
                outcome_verified=False, collision_inventory_verified=True, sent_receipt=None)


class Tests(unittest.TestCase):
    def test_preflight_never_issues_send(self):
        d = colue.assess(packet())
        self.assertEqual(d['state'], 'PREFLIGHT_PASS_NO_SEND')
        self.assertFalse(d['authorized_send'])
        self.assertEqual(d['effect'], 'NONE')

    def test_wrong_mailbox_fails_closed(self):
        p = packet(); p['connected_mailbox_id'] = 'other-mailbox'
        self.assertEqual(colue.assess(p)['state'], 'HOLD_WRONG_MAILBOX')

    def test_reply_requires_native_latest_thread(self):
        p = packet(); p['thread_verified'] = False
        self.assertEqual(colue.assess(p)['state'], 'HOLD_LATEST_THREAD')

    def test_new_thread_does_not_require_prior_thread_read(self):
        p = packet(); p['thread_ref'] = None; p['thread_verified'] = False
        self.assertEqual(colue.assess(p)['state'], 'PREFLIGHT_PASS_NO_SEND')

    def test_recipient_identity_must_be_verified(self):
        p = packet(); p['route_verified'] = False
        self.assertEqual(colue.assess(p)['state'], 'HOLD_RECIPIENT_ROUTE')

    def test_permission_and_opt_out_override_approval(self):
        p = packet(); p['consent_current'] = False
        self.assertEqual(colue.assess(p)['state'], 'HOLD_RELATION_PERMISSION')
        p['opt_out'] = True
        self.assertEqual(colue.assess(p)['state'], 'CLOSED_OPT_OUT')

    def test_claims_unchecked_holds(self):
        p = packet(); p['claims_verified'] = False
        self.assertEqual(colue.assess(p)['state'], 'HOLD_EVIDENCE')

    def test_unreviewed_draft_holds(self):
        p = packet(); p['approval_sha256'] = None
        self.assertEqual(colue.assess(p)['state'], 'REVIEW_REQUIRED_OR_STALE')

    def test_new_revision_invalidates_previous_approval(self):
        p = packet(); before=p['versions'][-1]['content_sha256']
        p['versions'].append(dict(revision=1, content_sha256=colue.content_sha256('synthetic v1'),
                                  predecessor_sha256=before))
        self.assertEqual(colue.assess(p)['state'], 'REVIEW_REQUIRED_OR_STALE')

    def test_broken_version_lineage_rejected(self):
        p = packet(); p['versions'].append(dict(revision=1, content_sha256=colue.content_sha256('v1'),
                                                 predecessor_sha256='0'*64))
        with self.assertRaisesRegex(ValueError, 'HOLD_BROKEN_PREDECESSOR'):
            colue.assess(p)

    def test_review_authority_is_distinct(self):
        p = packet(); p['approver_authorized'] = False
        self.assertEqual(colue.assess(p)['state'], 'HOLD_APPROVER_AUTHORITY')

    def test_collision_detected_even_if_copy_looks_new(self):
        p = packet(); peer = copy.deepcopy(p)
        peer['work_id'] = 'fixture-other-version'; peer['approval_sha256']=None
        self.assertEqual(colue.assess(p, (peer,))['state'], 'HOLD_COLLISION')

    def test_different_account_same_recipient_not_same_collision(self):
        p = packet(); peer = copy.deepcopy(p)
        peer['work_id'] = 'fixture-other'; peer['sender_mailbox_id'] = 'another-identity'
        self.assertEqual(colue.assess(p, (peer,))['state'], 'PREFLIGHT_PASS_NO_SEND')

    def test_provider_sent_not_receiver_read(self):
        p = packet(); p['sent_receipt'] = dict(provider_message_ref='provider-001',
             sender_mailbox_id=p['sender_mailbox_id'], thread_ref=p['thread_ref'],
             content_sha256=p['versions'][-1]['content_sha256'])
        d=colue.assess(p)
        self.assertEqual(d['state'], 'SENT_RECEIPT_ASSERTED_UNVERIFIED')
        self.assertFalse(d['receiver_ack'])

    def test_reply_does_not_imply_adoption(self):
        p = packet(); p['sent_receipt'] = dict(provider_message_ref='provider-001',
             sender_mailbox_id=p['sender_mailbox_id'], thread_ref=p['thread_ref'],
             content_sha256=p['versions'][-1]['content_sha256'])
        p['inbound_reply_readproof']=True
        self.assertEqual(colue.assess(p)['state'], 'REPLY_READPROOF_ASSERTED_NOT_INDEPENDENT')

    def test_forged_sent_receipt_rejected(self):
        p = packet(); p['sent_receipt'] = dict(provider_message_ref='provider-001',
             sender_mailbox_id='different-mailbox', thread_ref=p['thread_ref'],
             content_sha256=p['versions'][-1]['content_sha256'])
        self.assertEqual(colue.assess(p)['state'], 'HOLD_RECEIPT_MISMATCH')

    def test_string_true_is_not_approved_boolean(self):
        p = packet(); p['approver_authorized'] = 'true'
        with self.assertRaisesRegex(ValueError, 'HOLD_BOOLEAN_FLAG'):
            colue.assess(p)

    def test_unobserved_collision_inventory_blocks_send_readiness(self):
        p = packet(); p['collision_inventory_verified'] = False
        self.assertEqual(colue.assess(p)['state'], 'HOLD_COLLISION_INVENTORY')

    def test_work_output_contains_no_recipient_or_body(self):
        d = colue.assess(packet())
        raw = str(d)
        self.assertNotIn('fictional-recipient', raw)
        self.assertNotIn('synthetic v0', raw)
        self.assertNotIn('mailbox-a', raw)
        self.assertNotIn('fixture-work-1', raw)

    def test_unknown_outcome_not_promoted_to_true_adoption(self):
        p=packet(); p['sent_receipt'] = dict(provider_message_ref='provider-001',
              sender_mailbox_id=p['sender_mailbox_id'], thread_ref=p['thread_ref'],
              content_sha256=p['versions'][-1]['content_sha256'])
        p['outcome_verified']=True
        self.assertEqual(colue.assess(p)['state'], 'OUTCOME_ASSERTED_REQUIRES_INDEPENDENT_PROOF')

    def test_historical_sent_revision_survives_unsent_successor(self):
        p = packet()
        sent_hash = p['versions'][-1]['content_sha256']
        p['sent_receipt'] = dict(provider_message_ref='provider-fixture',
             sender_mailbox_id=p['sender_mailbox_id'], thread_ref=p['thread_ref'],
             content_sha256=sent_hash)
        p['versions'].append(dict(revision=1,
             content_sha256=colue.content_sha256('synthetic successor v1'),
             predecessor_sha256=sent_hash))
        result = colue.assess(p)
        self.assertEqual(result['state'], 'SENT_HISTORY_WITH_UNSENT_SUCCESSOR')
        self.assertEqual(result['next_event'], 'REVIEW_NEW_REVISION')
        self.assertFalse(result['authorized_send'])

    def test_unchanged_content_does_not_create_fake_evolution(self):
        p=packet()
        digest=p['versions'][0]['content_sha256']
        p['versions'].append(dict(revision=1, content_sha256=digest,
                                  predecessor_sha256=digest))
        with self.assertRaisesRegex(ValueError, 'HOLD_NONMATERIAL_REVISION'):
            colue.assess(p)

    def test_wrong_account_blocks_even_claimed_provider_receipt(self):
        p=packet()
        p['connected_mailbox_id']='other-account'
        p['sent_receipt']=dict(provider_message_ref='provider-fixture',
            sender_mailbox_id=p['sender_mailbox_id'], thread_ref=p['thread_ref'],
            content_sha256=p['versions'][-1]['content_sha256'])
        self.assertEqual(colue.assess(p)['state'], 'HOLD_WRONG_MAILBOX')

    def test_receipt_not_in_version_history_is_held(self):
        p=packet()
        p['sent_receipt']=dict(provider_message_ref='provider-fixture',
            sender_mailbox_id=p['sender_mailbox_id'], thread_ref=p['thread_ref'],
            content_sha256=colue.content_sha256('forged history'))
        self.assertEqual(colue.assess(p)['state'], 'HOLD_RECEIPT_MISMATCH')

    def test_peer_missing_required_identity_is_fail_closed(self):
        p=packet()
        with self.assertRaisesRegex(ValueError, 'HOLD_PEER_SCHEMA'):
            colue.assess(p, ({'work_id':'other'},))

    def test_peer_with_unusable_identity_is_fail_closed(self):
        p=packet()
        peer=dict(p);peer['work_id']='different';peer['recipient_ref']=None
        with self.assertRaisesRegex(ValueError, 'HOLD_PEER_SCHEMA'):
            colue.assess(p, (peer,))

    def test_idempotent_without_time_or_randomness(self):
        self.assertEqual(colue.assess(packet()), colue.assess(packet()))

if __name__ == '__main__':
    unittest.main(verbosity=2)
