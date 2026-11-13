"""Pure wake-admission tests: source-only and no host, scheduler or receiver effects."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
import copy
import unittest

from scripts.CoGoAllWakeAdmissionR0 import review, _identity, SCHEMA

NOW = datetime(2026, 11, 13, 15, 7, tzinfo=timezone.utc)
DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


def fixture(**changes):
    event = {
        "schema": SCHEMA,
        "event_id": "source-delta-01",
        "work_id": "CoAll.Work.SourceReview.R0",
        "source_path": "ai/currentness/colocal-x2-postcontainment-focus-20261112-r1.json",
        "source_revision": "c" * 40,
        "source_sha256": DIGEST_A,
        "observed_at_utc": "2026-11-13T15:02:00Z",
        "materiality": "MATERIAL_DELTA",
        "materiality_evidence_sha256": DIGEST_B,
        "authority_ceiling": "PUBLIC_READ_ONLY_SOURCE_VALIDATION",
        "confidentiality": "PUBLIC_SYNTHETIC",
        "collision_domain": "CI_PUBLIC_SOURCE_REVIEW",
        "idempotency_key": "coall-work-source-review-01",
        "predecessor_checkpoint_sha256": None,
        "receiver_class": "EXISTING_COGOALL_CI_SOURCE_VALIDATOR",
        "receiver_ready": True,
        "wake_condition": "ON_QUALIFIED_MATERIAL_DELTA",
        "stop_condition": "STOP_ON_HOLD_OR_NO_DELTA",
        "claimed_external_ack": False,
    }
    event.update(changes)
    return event


def prior_of(event, checkpoint=DIGEST_A):
    return {
        "wake_id": _identity(event),
        "work_id": event["work_id"],
        "collision_domain": event["collision_domain"],
        "source_sha256": event["source_sha256"],
        "checkpoint_sha256": checkpoint,
    }


class WakeAdmissionSourceTests(unittest.TestCase):
    def test_source_bound_one_candidate_is_not_live_execution(self):
        result = review(fixture(), [], NOW)
        self.assertEqual(result["state"], "WAKE_ADMISSION_REVIEW_CANDIDATE")
        self.assertTrue(result["candidate_eligible_for_owner_review"])
        for key in ("candidate_written", "task_dispatched", "external_receiver_ack",
                    "runtime_accepted", "prior_journal_authenticated"):
            self.assertFalse(result[key], key)
        self.assertEqual(result["receiver_class"], "EXISTING_COGOALL_CI_SOURCE_VALIDATOR")
        self.assertTrue(result["wake_id"].startswith("CoWake."))

    def test_same_event_stable_identity_even_after_dict_order_change(self):
        event = fixture()
        reverse = dict(reversed(list(event.items())))
        self.assertEqual(review(event, [], NOW)["wake_id"],
                         review(reverse, [], NOW)["wake_id"])

    def test_duplicate_suppressed_without_second_effect(self):
        event = fixture()
        result = review(event, [prior_of(event)], NOW)
        self.assertEqual(result["state"], "QUIESCENT_DUPLICATE_NO_WAKE")
        self.assertFalse(result["candidate_written"])
        self.assertFalse(result["task_dispatched"])

    def test_conflicting_event_same_workid_is_held(self):
        event = fixture()
        another = fixture(source_sha256=DIGEST_B, event_id="source-delta-02")
        result = review(another, [prior_of(event)], NOW)
        self.assertEqual(result["reason"], "HOLD_COLLISION_DOMAIN_ALREADY_OCCUPIED")

    def test_other_workid_same_actuator_domain_is_also_held(self):
        event = fixture()
        other = fixture(work_id="Another.Public.WorkID", event_id="another-01")
        self.assertEqual(review(other, [prior_of(event)], NOW)["reason"],
                         "HOLD_COLLISION_DOMAIN_ALREADY_OCCUPIED")

    def test_no_delta_quiet_without_relay(self):
        result = review(fixture(materiality="NO_MATERIAL_DELTA"), [], NOW)
        self.assertEqual(result["state"], "QUIESCENT_NO_WAKE")
        self.assertFalse(result["candidate_written"])

    def test_unknown_delta_not_zero(self):
        result = review(fixture(materiality="UNKNOWN"), [], NOW)
        self.assertEqual(result["reason"], "HOLD_MATERIALITY_UNQUALIFIED")

    def test_expired_sample_holds(self):
        result = review(fixture(observed_at_utc="2026-11-12T00:00:00Z"), [], NOW)
        self.assertEqual(result["reason"], "HOLD_STALE_OR_FUTURE_EVENT")

    def test_future_event_holds(self):
        event = fixture(observed_at_utc="2099-01-01T00:00:00Z")
        self.assertEqual(review(event, [], NOW)["reason"], "HOLD_STALE_OR_FUTURE_EVENT")

    def test_unknown_privacy_holds(self):
        self.assertEqual(review(fixture(confidentiality="UNKNOWN"), [], NOW)["reason"],
                         "HOLD_AUTHORITY_PRIVACY_OR_CLAIM")

    def test_authority_escalation_holds(self):
        event = fixture(authority_ceiling="READ_WRITE_PUBLIC_DEPLOYMENT")
        self.assertEqual(review(event, [], NOW)["reason"],
                         "HOLD_AUTHORITY_PRIVACY_OR_CLAIM")

    def test_forged_external_ack_holds(self):
        self.assertEqual(review(fixture(claimed_external_ack=True), [], NOW)["reason"],
                         "HOLD_AUTHORITY_PRIVACY_OR_CLAIM")

    def test_receiver_down_holds_with_no_new_worker(self):
        result = review(fixture(receiver_ready=False), [], NOW)
        self.assertEqual(result["reason"], "HOLD_RECEIVER_UNAVAILABLE")
        self.assertFalse(result["task_dispatched"])

    def test_unbound_predecessor_holds(self):
        event = fixture(predecessor_checkpoint_sha256="f" * 64)
        self.assertEqual(review(event, [], NOW)["reason"],
                         "HOLD_PREDECESSOR_NOT_IN_PRIOR")

    def test_bad_source_hash_holds(self):
        self.assertEqual(review(fixture(source_sha256="garbage"), [], NOW)["reason"],
                         "HOLD_SOURCE_IDENTITY")

    def test_source_private_or_escaped_holds(self):
        for path in ("../secret.json", "ai/currentness/../private/file.json",
                     "C:\\secret.json", "ai/currentness/log.txt"):
            with self.subTest(path=path):
                result = review(fixture(source_path=path), [], NOW)
                self.assertEqual(result["reason"], "HOLD_SOURCE_PATH")

    def test_wrong_wake_stop_predicate_holds(self):
        event = fixture(stop_condition="IGNORE_USER_STOP")
        self.assertEqual(review(event, [], NOW)["reason"], "HOLD_WAKE_STOP_RULES")

    def test_extra_authority_field_is_not_accepted(self):
        event = fixture(native_runtime_authorized=True)
        self.assertEqual(review(event, [], NOW)["reason"], "HOLD_EVENT_SCHEMA")

    def test_prior_is_caller_claim_not_authentic_journal(self):
        event = fixture()
        p = prior_of(event)
        result = review(event, [p], NOW)
        self.assertFalse(result["external_receiver_ack"])
        self.assertFalse(result["task_dispatched"])
        p["checkpoint_sha256"] = "not-a-hash"
        self.assertEqual(review(event, [p], NOW)["reason"],
                         "HOLD_UNVERIFIED_PRIOR_SHAPE")

    def test_prior_over_budget_or_duplicate_ids_holds(self):
        event = fixture()
        p = prior_of(event)
        self.assertEqual(review(event, [p] * 9, NOW)["reason"], "HOLD_PRIOR_BOUNDS")
        self.assertEqual(review(event, [p, copy.deepcopy(p)], NOW)["reason"],
                         "HOLD_UNVERIFIED_PRIOR_SHAPE")

    def test_review_clock_must_be_utc(self):
        event = fixture()
        result = review(event, [], datetime(2026, 11, 13, 10, 7))
        self.assertEqual(result["reason"], "HOLD_REVIEW_CLOCK")

    def test_intent_only_is_not_no_delta(self):
        result = review(fixture(materiality="PROPOSED"), [], NOW)
        self.assertEqual(result["reason"], "HOLD_MATERIALITY_UNQUALIFIED")


if __name__ == "__main__":
    unittest.main()
