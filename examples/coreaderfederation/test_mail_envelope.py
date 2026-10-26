#!/usr/bin/env python3
"""CoMail R0 negative tests, no mail/API/network/recipient access."""
import copy
import json
from pathlib import Path
import unittest

from mail_envelope import project, validate, SCHEMA

F = json.loads(Path(__file__).with_name("mail_fixture.json").read_text(encoding="utf-8"))


def clone():
    return copy.deepcopy(F)


class LivingEnvelopeTests(unittest.TestCase):
    def test_01_fixed_schema(self):
        self.assertEqual(F["schema"], SCHEMA)
        self.assertEqual(len(validate(F)), 4)

    def test_02_pin_holds_historical_message_and_source(self):
        p = project(F)
        self.assertEqual(p["reader_selected_mode"], "PIN")
        self.assertEqual(p["sent_version_id"], "v1")
        self.assertEqual(p["selected_version_id"], "v1")
        self.assertEqual(p["historical_message_sha256"], "a"*64)

    def test_03_follow_elects_latest_without_rewriting_sent(self):
        a,b = project(F,"PIN"),project(F,"FOLLOW")
        self.assertEqual(b["selected_version_id"], "v3")
        self.assertEqual(a["historical_message_sha256"],b["historical_message_sha256"])
        self.assertEqual(a["composed_at"],b["composed_at"])
        self.assertEqual(b["reader_selected_mode"],"FOLLOW")
        self.assertEqual(b["effects"]["emails_sent"],0)

    def test_04_compare_exposes_declared_steps(self):
        p=project(F,"COMPARE")
        self.assertEqual([v["version_id"] for v in p["declared_changes_on_elected_lineage"]],["v2","v3"])
        self.assertTrue(all(v["verified_diff"] is False for v in p["declared_changes_on_elected_lineage"]))

    def test_05_compare_is_not_automatically_real_diff(self):
        p=project(F,"COMPARE")
        self.assertEqual(p["version_currentness"],"DECLARED_ONLY__NOT_FETCH_VERIFIED")

    def test_06_retracted_source_is_tombstoned_not_recalled(self):
        m=clone()
        m["versions"][2]["state"]="RETRACTED"
        p=project(m,"FOLLOW")
        self.assertIsNone(p["selected_source_url"])
        self.assertEqual(p["change_notice"],"SOURCE_WITHDRAWN__HISTORICAL_MESSAGE_NOT_RECALLED")

    def test_07_retraction_warning_also_shown_when_pinned(self):
        m=clone()
        m["versions"][2]["state"]="RETRACTED"
        p=project(m,"PIN")
        self.assertEqual(p["selected_version_id"],"v1")
        self.assertEqual(p["change_notice"],"SOURCE_WITHDRAWN__HISTORICAL_MESSAGE_NOT_RECALLED")

    def test_08_correction_propagates_notice_not_email(self):
        p=project(F,"PIN")
        self.assertEqual(p["change_notice"],"CORRECTION_OR_RETRACTION_AVAILABLE")
        self.assertEqual(p["effects"]["notifications_sent"],0)

    def test_09_alternative_branch_not_elected_without_review(self):
        p=project(F,"FOLLOW")
        self.assertEqual(p["unpromoted_branch_tips"],["v2b"])
        self.assertEqual(p["elected_current_version_id"],"v3")

    def test_10_current_must_descend_from_original(self):
        m=clone()
        m["envelope"]["sent_version_id"]="v2"
        m["current_version_id"]="v2b"
        with self.assertRaisesRegex(ValueError,"ELECTED_VERSION_NOT_IN_SENT_LINEAGE"):
            project(m,"FOLLOW")

    def test_11_bad_mode_fail_closed(self):
        for mode in ("AUTO_SEND","SUBSCRIBE_ALL","SILENT_REWRITE",None):
            with self.subTest(mode=mode),self.assertRaises(ValueError):
                project(F,mode)

    def test_12_zero_effects_all_modes(self):
        for mode in ("PIN","FOLLOW","COMPARE"):
            p=project(F,mode)
            self.assertFalse(any(p["effects"].values()))
            self.assertEqual(p["send_authority"],"NONE")
            self.assertIsNone(p["recipient_ack"])

    def test_13_unknown_model_fields_rejected(self):
        m=clone();m["secret_email"]="synthetic-no-secret"
        with self.assertRaisesRegex(ValueError,"INVALID_MODEL_FIELDS"):
            project(m)

    def test_14_unknown_envelope_fields_rejected(self):
        m=clone();m["envelope"]["recipient_email"]="synthetic@example.invalid"
        with self.assertRaisesRegex(ValueError,"INVALID_ENVELOPE_FIELDS"):
            project(m)

    def test_15_unknown_version_fields_rejected(self):
        m=clone();m["versions"][0]["body_text"]="synthetic"
        with self.assertRaisesRegex(ValueError,"INVALID_VERSION_FIELDS"):
            project(m)

    def test_16_no_fake_send_receipt(self):
        m=clone();m["envelope"]["send_receipt"]="provider-accepted"
        with self.assertRaisesRegex(ValueError,"NO_REAL_SEND_RECEIPT_ACCEPTED"):
            project(m)

    def test_17_no_provider_state_promotion(self):
        m=clone();m["envelope"]["message_state"]="DELIVERED"
        with self.assertRaisesRegex(ValueError,"NO_REAL_SEND_RECEIPT_ACCEPTED"):
            project(m)

    def test_18_no_effect_authority(self):
        m=clone();m["envelope"]["effect_authority"]="SEND"
        with self.assertRaisesRegex(ValueError,"NO_EFFECT_AUTHORITY"):
            project(m)

    def test_19_sha_format_required(self):
        for bad in ("abc","A"*64,"f"*65,None):
            m=clone();m["versions"][1]["source_sha256"]=bad
            with self.subTest(bad=bad),self.assertRaisesRegex(ValueError,"INVALID_SHA256"):
                project(m)

    def test_20_public_url_allowlist(self):
        for bad in ("https://example.com/x","http://github.com/CoCivium/x",
                    "https://github.com@evil.invalid/x","https://github.com/CoCivium/foo?token=x"):
            m=clone();m["versions"][0]["source_url"]=bad
            with self.subTest(bad=bad),self.assertRaisesRegex(ValueError,"SOURCE_URL_NOT_ALLOWED"):
                project(m)

    def test_21_missing_version_held(self):
        m=clone();m["current_version_id"]="lost"
        with self.assertRaisesRegex(ValueError,"CURRENT_VERSION_MISSING"):
            project(m)

    def test_22_duplicate_version_ids(self):
        m=clone();m["versions"][3]["version_id"]="v2"
        with self.assertRaisesRegex(ValueError,"DUPLICATE_VERSION_ID"):
            project(m)

    def test_23_invalid_parent(self):
        m=clone();m["versions"][1]["parent_id"]="unknown"
        with self.assertRaisesRegex(ValueError,"PREDECESSOR_MUST_PRECEDE_SUCCESSOR"):
            project(m)

    def test_24_fork_is_not_an_extra_root(self):
        m=clone();m["versions"][3]["parent_id"]=None
        with self.assertRaisesRegex(ValueError,"EXACT_ONE_VERSION_ROOT"):
            project(m)

    def test_25_time_cannot_travel_backwards(self):
        m=clone();m["versions"][1]["issued_at"]="2026-10-24T00:00:00Z"
        with self.assertRaisesRegex(ValueError,"SUCCESSOR_TIME_MUST_ADVANCE"):
            project(m)

    def test_26_timestamps_require_timezone(self):
        m=clone();m["versions"][1]["issued_at"]="2026-10-26T01:00:00"
        with self.assertRaises(ValueError):project(m)

    def test_27_private_rights_unqualified(self):
        m=clone();m["versions"][1]["privacy"]="PRIVATE"
        with self.assertRaisesRegex(ValueError,"PRIVACY_OR_RIGHTS_UNQUALIFIED"):
            project(m)

    def test_28_no_unreviewed_scientific_promotion(self):
        m=clone();m["versions"][1]["epistemic_class"]="CONFIRMED_ET_CONTACT"
        with self.assertRaisesRegex(ValueError,"UNQUALIFIED_SOURCE_CLASS"):
            project(m)

    def test_29_unsupported_state_rejected(self):
        m=clone();m["versions"][1]["state"]="SILENT_DELETE"
        with self.assertRaisesRegex(ValueError,"UNQUALIFIED_SOURCE_CLASS"):
            project(m)

    def test_30_need_explanation_of_delta(self):
        m=clone();m["versions"][1]["change_summary"]=""
        with self.assertRaisesRegex(ValueError,"CHANGE_SUMMARY_REQUIRED"):
            project(m)

    def test_31_no_anonymous_unbounded_frontier(self):
        m=clone()
        for idx in range(33):
            v=copy.deepcopy(m["versions"][1])
            v["version_id"]="z"+str(idx).zfill(3)
            m["versions"].append(v)
        with self.assertRaisesRegex(ValueError,"BOUNDED_VERSION_COUNT_REQUIRED"):
            project(m)

    def test_32_readonly_reproducibility(self):
        old=clone();a=project(F,"COMPARE");b=project(F,"COMPARE")
        self.assertEqual(a,b)
        self.assertEqual(F,old)

    def test_33_pinned_source_pointer_is_not_verified_read(self):
        p=project(F,"PIN")
        self.assertIn("DECLARED_SOURCE_SHA_NE_VERIFIED_PUBLIC_READPROOF",p["nonclaims"])
        self.assertTrue(p["selected_source_url"].startswith("https://github.com/CoCivium/"))
        self.assertIsNone(p["recipient_ack"])

    def test_34_no_implicit_tracking_or_subscription(self):
        p=project(F,"FOLLOW")
        self.assertEqual(p["effects"]["tracking_events"],0)
        self.assertEqual(p["effects"]["notifications_sent"],0)
        self.assertIn("FOLLOW_NE_AUTO_NOTIFICATION",p["nonclaims"])

    def test_36_history_identity_does_not_prove_legal_or_technical_access(self):
        m=clone()
        m["versions"][2]["state"]="RETRACTED"
        p=project(m,"PIN")
        self.assertTrue(p["historical_version_identity_preserved"])
        self.assertEqual(p["historical_content_access"],"NOT_VERIFIED__MAY_BE_RESTRICTED")
        self.assertEqual(p["historical_message_state"],"SYNTHETIC_NOT_SENT")

    def test_35_snapshot_and_current_are_distinct_identities(self):
        p=project(F,"COMPARE")
        self.assertNotEqual(p["selected_source_sha256"],"1"*64)
        self.assertEqual(p["sent_version_id"],"v1")
        self.assertEqual(p["elected_current_version_id"],"v3")


if __name__ == "__main__":
    unittest.main()
