import copy
import hashlib
import json
import os
import subprocess
import sys
import unittest
from CoReachIdentityGateR0 import InvalidInput, SCHEMA, review

ROOT = os.path.dirname(os.path.abspath(__file__))

def valid():
    return {
      "schema":SCHEMA,"mode":"REVIEW_ONLY","work_id":"synthetic:one","draft_id":"synthetic-draft-id",
      "review_at":"2026-10-26T23:00:00Z","state":"DRAFT",
      "sender":{"authenticated_account":"owner@example.test","account_observed_by_connector":True,
          "selected_from":"owner@example.test","selected_from_verified":True,"verified_send_as_alias":False,
          "visible_signatory":"Assist, writing for Owner","signatory_disclosed":True,"writer_kind":"AI_ASSISTANT",
          "represented_principal":"owner:1","principal_authorization_evidenced":True},
      "recipients":[{"field":"TO","address":"reader@example.test","person_or_org_id":"person:reader",
        "identity_proof":"OWNER_APPROVED_EXACT_ROUTE","identity_proof_at":"2026-10-26T22:00:00Z",
        "route_state":"QUALIFIED","recipient_aware_of_purpose":True}],
      "thread":{"kind":"NEW","message_target_mode":"NORMAL","quotes_or_forwards":False},
      "content":{"privacy":"PUBLIC","sha256":"sha256:"+hashlib.sha256(b"sample email").hexdigest(),
        "signatory_claim":"Assist, writing for Owner","body_digest_verified":True,"claims_reviewed":True,
        "audience_matches_recipients":True,"quotes_or_forwards":False,"speaker_attribution_verified":True,
        "private_third_party_material":False,"disclosure_authorized":False},
      "authority":{"level":"RECIPIENT_SCOPED","recipient_set_confirmed":True,
        "cc_visibility_approved":False,"bcc_specifically_approved":False},
      "suppressions":{"checked":True,"opt_out":False,"do_not_contact":False,"duplicate_recent":False,"route_bounced":False}
    }

class Gate(unittest.TestCase):
    def held(self, mutate, expected):
        x=valid();mutate(x)
        r=review(x)
        self.assertEqual(r["state"],"HELD")
        self.assertIn(expected,r["holds"])
        self.assertEqual(r["effects"],{"network":0,"email_sent":0,"draft_updated":0,"provider_call":0,"file_write":0})
        self.assertEqual(r["send_authority"],"NONE_FROM_THIS_VALIDATOR")
        self.assertNotIn('reader@example.test',json.dumps(r))
        return r
    def test_valid_only_review_not_send(self):
        r=review(valid());self.assertEqual(r["state"],"READY_FOR_HUMAN_REVIEW_ONLY")
        self.assertEqual(r["holds"],[]);self.assertEqual(r["send_authority"],"NONE_FROM_THIS_VALIDATOR")
        self.assertEqual(r["recipient_counts"],{"TO":1,"CC":0,"BCC":0})
    def test_determinism(self):
        self.assertEqual(json.dumps(review(valid()),sort_keys=True),json.dumps(review(valid()),sort_keys=True))
    def test_no_cleartext(self):
        s=json.dumps(review(valid()));self.assertNotIn('reader@example.test',s);self.assertNotIn('sample email',s)
    def test_input_not_mutated(self):
        x=valid();s=json.dumps(x);review(x);self.assertEqual(json.dumps(x),s)
    def test_case_address_canonical(self):
        x=valid();x['recipients'][0]['address']='Reader@EXAMPLE.TEST'
        self.assertEqual(review(x)['recipient_address_digests'],review(valid())['recipient_address_digests'])
    def test_warning_not_send_promotion(self):
        x=valid();x['recipients'][0]['recipient_aware_of_purpose']=False
        r=review(x);self.assertEqual(r['state'],'READY_FOR_HUMAN_REVIEW_ONLY');self.assertIn('WARN_RECIPIENT_PURPOSE_UNCONFIRMED',r['warnings'])
    def test_valid_cc_requires_approval(self):
        x=valid();entry=copy.deepcopy(x['recipients'][0]);entry.update(address='cc@example.test',field='CC',person_or_org_id='person:cc');x['recipients'].append(entry)
        x['authority']['cc_visibility_approved']=True
        self.assertEqual(review(x)['state'],'READY_FOR_HUMAN_REVIEW_ONLY')
    def test_valid_bcc_requires_specific_approval(self):
        x=valid();entry=copy.deepcopy(x['recipients'][0]);entry.update(address='bcc@example.test',field='BCC',person_or_org_id='person:bcc');x['recipients'].append(entry)
        x['authority']['bcc_specifically_approved']=True
        self.assertEqual(review(x)['state'],'READY_FOR_HUMAN_REVIEW_ONLY')
    def test_valid_verified_alias(self):
        x=valid();s=x['sender'];s['selected_from']='alias@example.test';s['verified_send_as_alias']=True
        s['verified_alias_address']='alias@example.test';s['alias_verified_at']='2026-10-26T22:30:00Z'
        self.assertEqual(review(x)['state'],'READY_FOR_HUMAN_REVIEW_ONLY')
    def test_valid_reply_context(self):
        x=valid();x['thread'].update(kind='REPLY',thread_id='t',original_message_id='m',reply_to_checked=True,audience_changed=False)
        self.assertEqual(review(x)['state'],'READY_FOR_HUMAN_REVIEW_ONLY')
    def test_valid_forward_context(self):
        x=valid();x['thread'].update(kind='FORWARD',original_message_id='m',forward_disclosure_checked=True)
        self.assertEqual(review(x)['state'],'READY_FOR_HUMAN_REVIEW_ONLY')
    def test_valid_intermediary_not_direct_target(self):
        x=valid();x['thread'].update(message_target_mode='INTERMEDIARY_CONTACT',referenced_person='person:third')
        self.assertEqual(review(x)['state'],'READY_FOR_HUMAN_REVIEW_ONLY')
    def test_valid_direct_recipient(self):
        x=valid();x['thread'].update(message_target_mode='DIRECT_TO_REFERENCED_PERSON',direct_target_addresses=['reader@example.test'])
        self.assertEqual(review(x)['state'],'READY_FOR_HUMAN_REVIEW_ONLY')
    def test_private_output_not_echoed(self):
        x=valid();x['content']['privacy']='PRIVATE';self.assertEqual(review(x)['state'],'READY_FOR_HUMAN_REVIEW_ONLY')
        self.assertNotIn('reader@example.test',json.dumps(review(x)))
    def test_multiple_suppression_reasons_retained(self):
        x=valid();x['suppressions'].update(opt_out=True,route_bounced=True,duplicate_recent=True)
        r=review(x);self.assertTrue({'HOLD_RECIPIENT_SUPPRESSED','HOLD_BOUNCED_ROUTE','HOLD_DUPLICATE_FOLLOWUP'}<=set(r['holds']))
    def test_stable_digest(self):
        x=valid();r=review(x);self.assertEqual(r['recipient_address_digests'][0]['address_sha256'],
            'sha256:'+hashlib.sha256(b'reader@example.test').hexdigest())
    def test_cli_exact_result(self):
        x=valid();r=subprocess.run([sys.executable,os.path.join(ROOT,'CoReachIdentityGateR0.py')],input=json.dumps(x),text=True,capture_output=True)
        self.assertEqual(r.returncode,0);self.assertEqual(json.loads(r.stdout),review(x))
    def test_cli_no_sensitive_error(self):
        x=valid();x['sender']['selected_from']='SECRET_PASSWORD_AND_IDENTITY'
        r=subprocess.run([sys.executable,os.path.join(ROOT,'CoReachIdentityGateR0.py')],input=json.dumps(x),text=True,capture_output=True)
        self.assertEqual(r.returncode,2);self.assertEqual(r.stdout,'');self.assertNotIn('SECRET_PASSWORD',r.stderr)
    def test_cli_duplicate_json_key_hold(self):
        r=subprocess.run([sys.executable,os.path.join(ROOT,'CoReachIdentityGateR0.py')],input='{"schema":"x","schema":"y"}',text=True,capture_output=True)
        self.assertEqual(r.returncode,2);self.assertIn('INVALID_DUPLICATE_JSON_KEY',r.stderr)
    def test_cli_input_ceiling(self):
        r=subprocess.run([sys.executable,os.path.join(ROOT,'CoReachIdentityGateR0.py')],input='x'*131073,text=True,capture_output=True)
        self.assertEqual(r.returncode,2);self.assertIn('HELD_INPUT_TOO_LARGE',r.stderr)

mutations={
 'no_body_digest':(lambda x:x['content'].update(body_digest_verified=False),'HOLD_BODY_DIGEST_NOT_VERIFIED'),
 'zero_hash':(lambda x:x['content'].update(sha256='sha256:'+'0'*64),'HOLD_BODY_DIGEST_NOT_VERIFIED'),
 'requested_account_differs':(lambda x:x['sender'].update(requested_sender_address='elsewhere@example.test'),'HOLD_REQUESTED_SENDER_NOT_VERIFIED'),
 'no_from_proof':(lambda x:x['sender'].update(selected_from_verified=False),'HOLD_UNVERIFIED_SELECTED_FROM_HEADER'),
 'no_account_proof':(lambda x:x['sender'].update(account_observed_by_connector=False),'HOLD_UNVERIFIED_AUTHENTICATED_ACCOUNT'),
 'unknown_from_header':(lambda x:x['sender'].update(selected_from=''),'HOLD_SELECTED_FROM_HEADER_MISSING'),
 'unknown_thread_kind':(lambda x:x['thread'].update(kind='UNKNOWN'),'HOLD_THREAD_KIND_UNRESOLVED'),
 'unverified_alias':(lambda x:x['sender'].update(selected_from='alias@example.test'),'HOLD_UNVERIFIED_FROM_ALIAS'),
 'stale_alias':(lambda x:x['sender'].update(selected_from='alias@example.test',verified_send_as_alias=True,verified_alias_address='alias@example.test',alias_verified_at='2026-08-01T00:00:00Z'),'HOLD_STALE_FROM_ALIAS_PROOF'),
 'undisclosed_signatory':(lambda x:x['sender'].update(signatory_disclosed=False),'HOLD_SIGNATORY_NOT_DISCLOSED'),
 'unknown_writer_kind':(lambda x:x['sender'].update(writer_kind='BOT_OR_HUMAN_MAYBE'),'HOLD_WRITER_KIND_UNVERIFIED'),
 'unverified_principal':(lambda x:x['sender'].update(principal_authorization_evidenced=False),'HOLD_UNVERIFIED_ON_BEHALF_OF'),
 'signatory_mismatch':(lambda x:x['content'].update(signatory_claim='Another entity'),'HOLD_SIGNATORY_CONTENT_MISMATCH'),
 'unreviewed_claims':(lambda x:x['content'].update(claims_reviewed=False),'HOLD_CLAIMS_AND_ADDRESSEE_NOT_REVIEWED'),
 'mismatched_audience':(lambda x:x['content'].update(audience_matches_recipients=False),'HOLD_AUDIENCE_MISMATCH'),
 'unknown_quotes':(lambda x:x['content'].update(quotes_or_forwards=True,speaker_attribution_verified=False),'HOLD_UNVERIFIED_QUOTED_SPEAKERS'),
 'private_disclosure':(lambda x:x['content'].update(private_third_party_material=True,disclosure_authorized=False),'HOLD_UNAUTHORIZED_THIRD_PARTY_DISCLOSURE'),
 'draft_only_authority':(lambda x:x['authority'].update(level='DRAFT_ONLY'),'HOLD_NO_SCOPED_SEND_AUTHORITY'),
 'unapproved_recipient_set':(lambda x:x['authority'].update(recipient_set_confirmed=False),'HOLD_RECIPIENT_SET_NOT_APPROVED'),
 'do_not_contact':(lambda x:x['suppressions'].update(do_not_contact=True),'HOLD_RECIPIENT_SUPPRESSED'),
 'opt_out':(lambda x:x['suppressions'].update(opt_out=True),'HOLD_RECIPIENT_SUPPRESSED'),
 'duplicate_recent':(lambda x:x['suppressions'].update(duplicate_recent=True),'HOLD_DUPLICATE_FOLLOWUP'),
 'bounced_route':(lambda x:x['suppressions'].update(route_bounced=True),'HOLD_BOUNCED_ROUTE'),
 'unchecked_suppression':(lambda x:x['suppressions'].update(checked=False),'HOLD_SUPPRESSION_NOT_CHECKED'),
 'already_sent_state':(lambda x:x.update(state='SENT'),'HOLD_NOT_AN_UNSENT_DRAFT'),
 'no_primary':(lambda x:x['recipients'][0].update(field='CC'),'HOLD_NO_PRIMARY_RECIPIENT'),
 'no_any':(lambda x:x.update(recipients=[]),'HOLD_NO_RECIPIENTS'),
 'unresolved_person':(lambda x:x['recipients'][0].update(identity_proof='CONTACT_ENTRY_ONLY'),'HOLD_UNRESOLVED_RECIPIENT_IDENTITY'),
 'missing_person_id':(lambda x:x['recipients'][0].update(person_or_org_id=''),'HOLD_UNRESOLVED_RECIPIENT_IDENTITY'),
 'bounced_address':(lambda x:x['recipients'][0].update(route_state='BOUNCED'),'HOLD_RECIPIENT_ROUTE_NOT_QUALIFIED'),
 'missing_identity_date':(lambda x:x['recipients'][0].pop('identity_proof_at'),'HOLD_MISSING_RECIPIENT_IDENTITY_TIME'),
 'stale_identity_date':(lambda x:x['recipients'][0].update(identity_proof_at='2026-07-01T00:00:00Z'),'HOLD_STALE_RECIPIENT_IDENTITY'),
 'future_identity_date':(lambda x:x['recipients'][0].update(identity_proof_at='2027-10-26T22:00:00Z'),'HOLD_STALE_RECIPIENT_IDENTITY'),
 'duplicate_headers':(lambda x:x['recipients'].append({**copy.deepcopy(x['recipients'][0]),'field':'CC'}),'HOLD_DUPLICATE_ADDRESS_ACROSS_HEADERS'),
 'cc_disclosure':(lambda x:x['recipients'].append({**copy.deepcopy(x['recipients'][0]),'field':'CC','address':'cc@example.test','person_or_org_id':'person:cc'}),'HOLD_CC_DISCLOSURE_NOT_APPROVED'),
 'bcc_disclosure':(lambda x:x['recipients'].append({**copy.deepcopy(x['recipients'][0]),'field':'BCC','address':'bcc@example.test','person_or_org_id':'person:bcc'}),'HOLD_BCC_UNAUTHORIZED'),
 'reply_no_thread':(lambda x:x['thread'].update(kind='REPLY',reply_to_checked=True),'HOLD_REPLY_WITHOUT_SOURCE_THREAD'),
 'reply_to_unknown':(lambda x:x['thread'].update(kind='REPLY',thread_id='t',original_message_id='m',reply_to_checked=False),'HOLD_REPLY_TO_NOT_VERIFIED'),
 'reply_audience_changed':(lambda x:x['thread'].update(kind='REPLY',thread_id='t',original_message_id='m',reply_to_checked=True,audience_changed=True),'HOLD_CHANGED_THREAD_AUDIENCE'),
 'forward_unknown':(lambda x:x['thread'].update(kind='FORWARD'),'HOLD_FORWARD_CONTEXT_NOT_APPROVED'),
 'direct_to_wrong_person':(lambda x:x['thread'].update(message_target_mode='DIRECT_TO_REFERENCED_PERSON',direct_target_addresses=['someoneelse@example.test']),'HOLD_DIRECT_RECIPIENT_CLAIM_MISMATCH'),
 'unknown_directness':(lambda x:x['thread'].update(message_target_mode='UNKNOWN'),'HOLD_UNKNOWN_DIRECTNESS_OF_ADDRESS'),
}
for name,(mutate,expected) in mutations.items():
    def make(mut, exp):
        def test(self):self.held(mut,exp)
        return test
    setattr(Gate,'test_hold_'+name,make(mutate,expected))

invalids={
 'invalid_schema':lambda x:x.update(schema='not valid'),
 'invalid_mode':lambda x:x.update(mode='AUTO_SEND'),
 'invalid_email':lambda x:x['recipients'][0].update(address='Alice <reader@example.test>'),
 'invalid_date':lambda x:x.update(review_at='2026-02-31T00:00:00Z'),
 'invalid_privacy':lambda x:x['content'].update(privacy='EVERYONE'),
 'invalid_content_hash':lambda x:x['content'].update(sha256='not-real'),
 'invalid_route':lambda x:x['recipients'][0].update(route_state='ACTIVE_FOREVER'),
 'invalid_field':lambda x:x['recipients'][0].update(field='TO_CC_BCC'),
 'invalid_thread_kind':lambda x:x['thread'].update(kind='EVERYONE'),
 'invalid_authority':lambda x:x['authority'].update(level='INFINITE'),
 'invalid_work_id':lambda x:x.update(work_id=''),
 'invalid_recipients':lambda x:x.update(recipients='bad'),
 'invalid_sender':lambda x:x.update(sender='nope'),
 'invalid_content':lambda x:x.update(content='nope'),
 'invalid_suppressions':lambda x:x.update(suppressions='bad'),
 'too_many_recipients':lambda x:x.update(recipients=[copy.deepcopy(x['recipients'][0]) for _ in range(65)]),
}
for name,mutate in invalids.items():
    def make(mut):
        def test(self):
            x=valid();mut(x)
            with self.assertRaises(InvalidInput):review(x)
        return test
    setattr(Gate,'test_invalid_'+name,make(mutate))

if __name__=='__main__':
    unittest.main(verbosity=2)
