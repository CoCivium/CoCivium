"""CoMail stage-review negative controls: CoEv source and policy must not auto-send."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from stage_review_r0 import SCHEMA, evaluate


class CoMailStageReviewR0(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads((ROOT / "fixture.json").read_text(encoding="utf-8"))

    def stage(self):
        f = self.fixture
        return {
            "schema": SCHEMA,
            "stage_id": "comail.synthetic.stage.v1",
            "predecessor_stage_id": "comail.synthetic.stage.v0",
            "resource_id": f["resource"]["resource_id"],
            "pinned_resource_sha256": f["resource"]["current_sha256"],
            "pinned_message_sha256": f["fixed_message"]["sha256"],
            "policy_revision": "policy.v1",
            "current_policy_revision": "policy.v1",
            "sender_qualified": True,
            "recipient_qualified": True,
            "thread_qualified": True,
            "claims_reviewed": True,
            "consent_checked": True,
            "delivery": "NOT_SENT",
        }

    def test_bounded_stage_never_sends_or_self_acks(self):
        result = evaluate(self.fixture, self.stage())
        self.assertEqual(result["status"], "READY_FOR_EXPLICIT_HUMAN_REVIEW")
        self.assertEqual(result["effect"], "NONE")
        self.assertEqual(result["delivery"], "NOT_SENT")
        self.assertEqual(result["receiver_ack"], "UNPROVEN")
        self.assertEqual(result["sender_authority"], "NOT_GRANTED")

    def test_changed_resource_forces_review_without_changing_original(self):
        stage = self.stage()
        original = copy.deepcopy(stage)
        changed = copy.deepcopy(self.fixture)
        changed["resource"]["current_sha256"] = "a" * 64
        # Mutating only a hash fails core validation, so use a *legitimate*
        # new version by updating the last version's content and all pins.
        from core import update_pins
        changed = copy.deepcopy(self.fixture)
        changed["resource"]["versions"][-1]["body"] += " New reviewed evidence."
        update_pins(changed)
        result = evaluate(changed, stage)
        self.assertIn("SOURCE_REVISION_DRIFT", result["reasons"])
        self.assertEqual(result["status"], "HOLD_FOR_REQUALIFICATION")
        self.assertEqual(stage, original)

    def test_evolved_review_policy_forces_requalification(self):
        stage = self.stage()
        stage["current_policy_revision"] = "policy.v2"
        result = evaluate(self.fixture, stage)
        self.assertIn("REVIEW_POLICY_EVOLVED", result["reasons"])
        self.assertEqual(result["status"], "HOLD_FOR_REQUALIFICATION")

    def test_identity_thread_consent_and_claims_are_independent_gates(self):
        for key in ("sender_qualified", "recipient_qualified", "thread_qualified",
                    "claims_reviewed", "consent_checked"):
            with self.subTest(key=key):
                stage = self.stage()
                stage[key] = False
                result = evaluate(self.fixture, stage)
                self.assertIn(key.upper() + "_MISSING", result["reasons"])
                self.assertEqual(result["effect"], "NONE")

    def test_wrong_resource_and_frozen_message_rejected(self):
        for key, value, reason in (
            ("resource_id", "urn:co:resource:synthetic:other", "RESOURCE_ID_MISMATCH"),
            ("pinned_message_sha256", "0" * 64, "HISTORICAL_MESSAGE_MISMATCH"),
        ):
            with self.subTest(key=key):
                stage = self.stage()
                stage[key] = value
                self.assertIn(reason, evaluate(self.fixture, stage)["reasons"])

    def test_no_forged_send_or_extra_data_or_invalid_previous(self):
        for field, value in (
            ("delivery", "SENT"),
            ("predecessor_stage_id", "comail.synthetic.stage.v1"),
            ("recipient_qualified", "yes"),
        ):
            with self.subTest(field=field):
                stage = self.stage()
                stage[field] = value
                with self.assertRaises(ValueError):
                    evaluate(self.fixture, stage)
        stage = self.stage()
        stage["recipient_email"] = "private@example.invalid"
        with self.assertRaises(ValueError):
            evaluate(self.fixture, stage)

    def test_no_material_delta_is_deterministic_and_quiet(self):
        a = evaluate(self.fixture, self.stage())
        b = evaluate(self.fixture, self.stage())
        self.assertEqual(a, b)
        self.assertEqual(a["next_wake"], "EXPLICIT_HUMAN_SEND_DECISION")


if __name__ == "__main__":
    unittest.main()
