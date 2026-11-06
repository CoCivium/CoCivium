#!/usr/bin/env python3
"""Synthetic no-send identity-routing regression tests."""
import copy
import importlib.util
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("identity_gate", root / "scripts" / "CoOutreachIdentityGateR0.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def fixture():
    person = {
        "person_id": "recipient-one", "display_name": "Example Reviewer",
        "address": "reviewer@example.test", "identity_source_ref": "synthetic:identity",
        "route_source_ref": "synthetic:route", "permission_source_ref": "synthetic:consent",
        "permission_basis": "APPROVED_ONE_OFF"}
    data = {
        "schema": gate.SCHEMA, "channel": "EMAIL", "message_id": "synthetic-01",
        "purpose": "Request critique without implying endorsement",
        "sender": {"person_id": "sender-one", "display_name": "Example Sender",
                   "from_address": "sender@example.test",
                   "authenticated_account": "sender@example.test",
                   "identity_source_ref": "synthetic:author",
                   "account_source_ref": "synthetic:account"},
        "audience": {"to": [person], "cc": [], "bcc": []},
        "intended_recipient_ids": ["recipient-one"],
        "thread": {"mode": "NEW", "thread_id": None, "participant_ids": []},
        "content": {"subject": "Please review", "body": "A synthetic test.",
                    "attributed_claims": [], "attachments": []},
        "privacy_class": "PRIVATE", "review": {}}
    return approve(data)


def approve(data):
    data["review"] = {
        "human_reviewer_id": "synthetic-reviewer",
        "human_review_evidence_ref": "synthetic:human",
        "sender_route_review_ref": "synthetic:route-check",
        "semantic_content_review_ref": "synthetic:content-check",
        "reviewed_fingerprint": gate.validate({**data, "review": {}})["bound_fingerprint_sha256"]}
    return data


class RouteGateTests(unittest.TestCase):
    def held(self, data, expected):
        result = gate.validate(data)
        self.assertEqual(result["state"], "HELD")
        self.assertIn(expected, result["issue_codes"])
        self.assertEqual(result["send_status"], "NOT_SENT")
        self.assertEqual(result["external_effects"], 0)

    def test_clean_draft_review_ready_only(self):
        result = gate.validate(fixture())
        self.assertEqual(result["state"], "REVIEW_READY_ONLY")
        self.assertEqual(result["issue_codes"], [])
        self.assertEqual(result["send_status"], "NOT_SENT")

    def test_wrong_person(self):
        d = fixture(); d["audience"]["to"][0]["person_id"] = "wrong-person"
        approve(d); self.held(d, "INTENDED_ACTUAL_AUDIENCE_MISMATCH")

    def test_changed_address_after_review(self):
        d = fixture(); d["audience"]["to"][0]["address"] = "other@example.test"
        self.held(d, "REVIEW_FINGERPRINT_MISMATCH")

    def test_identity_evidence_missing(self):
        d = fixture(); d["audience"]["to"][0]["identity_source_ref"] = ""
        approve(d); self.held(d, "RECIPIENT_IDENTITY_UNBOUND")

    def test_sender_send_as_unproven(self):
        d = fixture(); d["sender"]["authenticated_account"] = "different@example.test"
        approve(d); self.held(d, "UNVERIFIED_SEND_AS")

    def test_reply_to_third_party_not_approved(self):
        d = fixture(); d["sender"]["reply_to_address"] = "other@example.test"
        approve(d); self.held(d, "UNVERIFIED_REPLY_TO")

    def test_reply_all_needs_audience_review(self):
        d = fixture()
        d["thread"] = {"mode": "REPLY_ALL", "thread_id": "thread1",
                       "thread_source_ref": "synthetic:thread",
                       "participant_ids": ["recipient-one"]}
        approve(d); self.held(d, "MULTIPARTY_OR_FORWARD_SCOPE_UNREVIEWED")

    def test_reply_outside_thread(self):
        d = fixture()
        d["thread"] = {"mode": "REPLY", "thread_id": "thread1",
                       "thread_source_ref": "synthetic:thread",
                       "participant_ids": ["wrong-person"]}
        approve(d); self.held(d, "RECIPIENT_OUTSIDE_VERIFIED_THREAD")

    def test_duplicate_cc_person(self):
        d = fixture(); d["audience"]["cc"] = [copy.deepcopy(d["audience"]["to"][0])]
        approve(d); self.held(d, "DUPLICATE_PERSON_ACROSS_RECIPIENTS")

    def test_same_display_name_different_people(self):
        d = fixture()
        another = copy.deepcopy(d["audience"]["to"][0])
        another.update(person_id="recipient-two", address="second@example.test")
        d["audience"]["cc"] = [another]; d["intended_recipient_ids"].append("recipient-two")
        approve(d); self.held(d, "AMBIGUOUS_SHARED_DISPLAY_NAME")

    def test_unverified_claimed_endorsement(self):
        d = fixture()
        d["content"]["attributed_claims"] = [{
            "subject_person_id": "recipient-one", "claim_text": "Endorsed CoCivium",
            "evidence_ref": "synthetic:quote", "review_state": "UNKNOWN"}]
        approve(d); self.held(d, "ATTRIBUTED_CLAIM_NOT_CHECKED")

    def test_attachment_scope(self):
        d = fixture()
        d["content"]["attachments"] = [{
            "name": "test.txt", "source_ref": "synthetic:attachment",
            "sha256": "cafe", "approved_person_ids": ["someone-else"]}]
        approve(d); self.held(d, "ATTACHMENT_AUDIENCE_NOT_APPROVED")

    def test_permission_missing(self):
        d = fixture(); d["audience"]["to"][0]["permission_basis"] = "UNKNOWN"
        approve(d); self.held(d, "RECIPIENT_PERMISSION_UNBOUND")

    def test_header_injection(self):
        d = fixture(); d["content"]["subject"] = "Hello\r\nBcc: stranger@example.test"
        approve(d); self.held(d, "SUBJECT_HEADER_INJECTION")

    def test_privacy_review_mandatory_for_restricted(self):
        d = fixture(); d["privacy_class"] = "RESTRICTED"
        approve(d); self.held(d, "RESTRICTED_DATA_REVIEW_MISSING")

    def test_mutating_body_invalidates_approval(self):
        d = fixture(); d["content"]["body"] += " Changed after review."
        self.held(d, "REVIEW_FINGERPRINT_MISMATCH")

    def test_missing_review_not_passed(self):
        d = fixture(); d["review"] = {}
        self.held(d, "HUMAN_REVIEW_MISSING")

    def test_no_mutation_and_non_dict_fails_closed(self):
        d = fixture(); previous = copy.deepcopy(d)
        gate.validate(d)
        self.assertEqual(d, previous)
        for invalid in (None, [], ""):
            self.assertEqual(gate.validate(invalid)["state"], "HELD")


if __name__ == "__main__":
    unittest.main()
