"""CoPre optional-ingress R0 regression, authority and replay inversion tests."""
from __future__ import annotations
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import copre_optional_ingress_r0 as m

SHA="a"*64
def event(kind="NO_INPUT", event_id="event-1", *, source_ref=None, digest=None,
          requested_authority="NONE", privacy_class="UNKNOWN"):
    return {"schema":m.SCHEMA,"kind":kind,"event_id":event_id,
            "source_ref":source_ref,"source_sha256":digest,
            "observed_at_utc":"2026-11-10T18:25:00Z",
            "requested_authority":requested_authority,
            "privacy_class":privacy_class}

def sourced(kind, event_id="evt-1", digest=SHA, source_ref="CoCivium/CoCivium:CoPre.md"):
    return event(kind,event_id,source_ref=source_ref,digest=digest)

class OptionalIngressTests(unittest.TestCase):
    def test_no_input_is_valid_and_never_requests_a_new_phrase(self):
        r=m.preview(event())
        self.assertEqual(r["decision"],"NO_USER_MESSAGE_REQUIRED")
        self.assertFalse(r["user_prompt_required_to_start_review"])
        self.assertFalse(r["eligible_for_further_qualification"])
    def test_no_input_cannot_carry_requested_effect(self):
        x=event(requested_authority="CONSEQUENTIAL_GATED")
        with self.assertRaisesRegex(m.Held,"HELD_NO_INPUT_CANNOT_REQUEST_EFFECT"):
            m.preview(x)
    def test_no_input_cannot_spoof_a_source(self):
        x=event(source_ref="CoPre.md",digest=SHA)
        with self.assertRaisesRegex(m.Held,"HELD_NO_INPUT_CANNOT_REQUEST_EFFECT"):
            m.preview(x)
    def test_schedule_due_can_inspire_review_without_chat_message(self):
        r=m.preview(sourced("SCHEDULED_DUE"))
        self.assertEqual(r["decision"],"SOURCE_BOUND_REVIEW_CANDIDATE")
        self.assertTrue(r["eligible_for_further_qualification"])
        self.assertFalse(r["human_effect_authority_granted"])
    def test_schedule_same_due_event_dedupes(self):
        x=sourced("SCHEDULED_DUE")
        key=m.stable_key(x)
        self.assertEqual(m.preview(x,seen_keys={key})["decision"],"EXACT_DUPLICATE_OBSERVATION")
    def test_schedule_new_due_event_can_be_reviewed_even_if_source_unchanged(self):
        old=sourced("SCHEDULED_DUE","20261110T1800")
        new=sourced("SCHEDULED_DUE","20261110T1900")
        self.assertNotEqual(m.stable_key(old),m.stable_key(new))
        self.assertTrue(m.preview(new,seen_keys={m.stable_key(old)})["eligible_for_further_qualification"])
    def test_same_content_source_change_dedupes_across_event_ids(self):
        a=sourced("SOURCE_CHANGED","webhook-1")
        b=sourced("SOURCE_CHANGED","webhook-2")
        self.assertEqual(m.stable_key(a),m.stable_key(b))
        self.assertEqual(m.preview(b,seen_keys={m.stable_key(a)})["decision"],"EXACT_DUPLICATE_OBSERVATION")
    def test_new_source_hash_creates_distinct_candidate(self):
        a=sourced("SOURCE_CHANGED",digest="a"*64)
        b=sourced("SOURCE_CHANGED",digest="b"*64)
        self.assertNotEqual(m.stable_key(a),m.stable_key(b))
    def test_independent_receiver_events_must_not_be_collapsed_on_same_content_hash(self):
        a=sourced("RECEIVER_READBACK","receiver-a")
        b=sourced("RECEIVER_READBACK","receiver-b")
        self.assertNotEqual(m.stable_key(a),m.stable_key(b))
        self.assertTrue(m.preview(b,seen_keys={m.stable_key(a)})["eligible_for_further_qualification"])
    def test_assent_is_compatibility_only(self):
        r=m.preview(sourced("USER_ASSENT"))
        self.assertEqual(r["decision"],"STANDING_INTENT_ALREADY_PRESENT")
        self.assertFalse(r["eligible_for_further_qualification"])
    def test_assent_never_grants_the_requested_effect(self):
        x=sourced("USER_ASSENT");x["requested_authority"]="CONSEQUENTIAL_GATED"
        r=m.preview(x)
        self.assertFalse(r["human_effect_authority_granted"])
        self.assertEqual(r["external_effect_count"],0)
    def test_new_idea_is_not_discarded_as_formula(self):
        r=m.preview(sourced("USER_IDEA"))
        self.assertEqual(r["decision"],"IDEA_CANDIDATE_FOR_QUALIFICATION")
    def test_repeated_user_idea_has_no_second_effect(self):
        a=sourced("USER_IDEA")
        self.assertFalse(m.preview(a,seen_keys={m.stable_key(a)})["eligible_for_further_qualification"])
    def test_real_stop_does_not_require_hash_or_user_latch(self):
        r=m.preview(event("USER_STOP"))
        self.assertEqual(r["decision"],"STOP_REQUEST_REQUIRES_RUNTIME_ACK")
        self.assertTrue(r["stop_or_correction_attention_required"])
        self.assertFalse(r["stop_effect_ack"])
    def test_replayed_stop_is_still_attended_not_quietly_ignored(self):
        x=event("USER_STOP")
        r=m.preview(x,seen_keys={m.stable_key(x)})
        self.assertTrue(r["prior_seen"])
        self.assertEqual(r["decision"],"STOP_REQUEST_REQUIRES_RUNTIME_ACK")
    def test_correction_does_not_depend_on_seed_paste(self):
        r=m.preview(event("USER_CORRECTION"))
        self.assertEqual(r["decision"],"CORRECTION_REQUIRES_REVIEW_ACK")
        self.assertTrue(r["stop_or_correction_attention_required"])
    def test_duplicate_correction_requires_explicit_ack(self):
        x=event("USER_CORRECTION")
        r=m.preview(x,seen_keys={m.stable_key(x)})
        self.assertTrue(r["stop_or_correction_attention_required"])
    def test_missing_external_source_evidence_holds(self):
        r=m.preview(event("SOURCE_CHANGED"))
        self.assertEqual(r["decision"],"HELD_SOURCE_POINTER_OR_HASH_ABSENT")
    def test_unknown_privacy_is_not_auto_public(self):
        r=m.preview(sourced("SOURCE_CHANGED"))
        self.assertFalse(r["human_effect_authority_granted"])
        self.assertFalse(r["receiver_ack"])
    def test_declared_bytes_hash_not_independent_readback(self):
        r=m.preview(sourced("RECEIVER_READBACK"))
        self.assertIn("SOURCE_SHA_STRING_NE_INDEPENDENT_BYTE_READBACK",r["nonclaims"])
        self.assertFalse(r["receiver_ack"])
    def test_no_unrecognized_raw_private_text_field(self):
        x=sourced("USER_IDEA");x["raw_chat_text"]="private"
        with self.assertRaisesRegex(m.Held,"HELD_UNKNOWN_OR_MISSING_FIELDS"):
            m.preview(x)
    def test_no_forged_external_ack_field(self):
        x=sourced("RECEIVER_READBACK");x["receiver_ack"]=True
        with self.assertRaisesRegex(m.Held,"HELD_UNKNOWN_OR_MISSING_FIELDS"):
            m.preview(x)
    def test_ref_rejects_whitespace_or_query_exfiltration(self):
        x=sourced("SOURCE_CHANGED");x["source_ref"]="https://host/?private=hi there"
        with self.assertRaisesRegex(m.Held,"HELD_INVALID_SOURCE_REFERENCE"):
            m.preview(x)
    def test_bad_digest_fails_closed(self):
        x=sourced("SOURCE_CHANGED",digest="HASH_NOT_SHA")
        with self.assertRaisesRegex(m.Held,"HELD_INVALID_SOURCE_DIGEST"):
            m.preview(x)
    def test_extra_case_digest_fails_closed(self):
        x=sourced("SOURCE_CHANGED",digest="A"*64)
        with self.assertRaisesRegex(m.Held,"HELD_INVALID_SOURCE_DIGEST"):
            m.preview(x)
    def test_unqualified_requested_authority_holds(self):
        x=sourced("SOURCE_CHANGED");x["requested_authority"]="OWNER_APPROVED_PERMANENTLY"
        with self.assertRaisesRegex(m.Held,"HELD_UNQUALIFIED_AUTHORITY_OR_PRIVACY"):
            m.preview(x)
    def test_invalid_observation_clock_holds(self):
        x=sourced("SOURCE_CHANGED");x["observed_at_utc"]="tomorrow"
        with self.assertRaisesRegex(m.Held,"HELD_INVALID_OBSERVATION_CLOCK"):
            m.preview(x)
    def test_seen_keys_must_be_verified_shape_not_free_text(self):
        x=sourced("SCHEDULED_DUE")
        with self.assertRaisesRegex(m.Held,"HELD_UNQUALIFIED_DEDUPE_KEYS"):
            m.preview(x,seen_keys={"I said agree already"})
    def test_source_only_code_contains_no_worker_or_network_invocation(self):
        source=(ROOT/"scripts/copre_optional_ingress_r0.py").read_text()
        for token in ("subprocess.", "os.system", "urllib.request", "requests.", "socket.",
                      "Start-Process", "genui", "time.sleep", "setInterval", "TaskScheduler"):
            self.assertNotIn(token,source)
        r=m.preview(event())
        self.assertEqual(r["actual_actor_or_runtime"],"NONE_THIS_ADAPTER")
    def test_draft_protocol_disclaims_majority(self):
        doc=(ROOT/"docs/CoPreGeneric/Shareable_R0_20261109/CoPreGeneric-v1.0-DRAFT.md").read_text()
        self.assertIn("No new user message is required",doc)
        self.assertIn("Most active sessions",doc)
        self.assertIn("No adopted cross-session consensus",doc)

if __name__=="__main__":
    unittest.main()
