"""Negative controls for the CoLatch R0 *shadow* admission contract."""
import copy
import unittest

from release_gate_r0 import ROLES, evaluate, synthetic_example


class LatchReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.example = synthetic_example()

    def check_hold(self, token):
        result = evaluate(self.example)
        self.assertEqual(result["shadow"], "HOLD_INVALID_EVIDENCE")
        self.assertIn(token, result["reasons"])
        self.assertEqual(result["native_x2"], "HOLD_UNATTESTED_RECEIVER")

    def test_synthetic_complete_structure_never_promotes_native(self):
        out = evaluate(self.example)
        self.assertEqual(out["shadow"], "STRUCTURE_PASS_NOT_ATTESTATION")
        self.assertEqual(out["native_x2"], "HOLD_UNATTESTED_RECEIVER")
        self.assertEqual(out["independent_sync"], "UNPROVEN")

    def test_each_of_five_roles_must_exist_once(self):
        for role in ROLES:
            with self.subTest(role=role):
                bad = copy.deepcopy(self.example)
                bad["components"][role] = []
                result = evaluate(bad)
                self.assertIn("NOT_EXACTLY_ONE_" + role.upper(), result["reasons"])

    def test_second_seed_does_not_count_as_better(self):
        self.example["components"]["seed"].append(copy.deepcopy(self.example["components"]["seed"][0]))
        self.check_hold("NOT_EXACTLY_ONE_SEED")

    def test_role_alias_collision_detected(self):
        self.example["components"]["orb"][0]["id"] = "seed-fixture"
        self.check_hold("COMPONENT_ID_COLLISION")

    def test_every_role_must_have_source(self):
        self.example["components"]["gauge"][0].pop("source_ref")
        self.check_hold("UNBOUND_GAUGE")

    def test_stale_role_source_fails(self):
        self.example["components"]["thumb"][0]["source_sha256"] = "b" * 64
        self.check_hold("SOURCE_MISMATCH_THUMB")

    def test_cross_work_role_fails(self):
        self.example["components"]["time"][0]["work_id"] = "wrong"
        self.check_hold("WORK_ID_MISMATCH_TIME")

    def test_work_identity_required(self):
        self.example["work_id"] = ""
        self.check_hold("MISSING_WORK_ID")

    def test_hex_digest_required(self):
        self.example["source_sha256"] = "untrusted"
        self.check_hold("INVALID_SOURCE_SHA256")

    def test_zero_placeholders_is_literal(self):
        self.example["placeholder_count"] = 1
        self.check_hold("PLACEHOLDERS_NOT_ZERO")

    def test_human_mailman_not_allowed_in_claimed_automatic_result(self):
        self.example["human_relays"] = 1
        self.check_hold("HUMAN_RELAY_REQUIRED")

    def test_effect_count_exactly_one(self):
        self.example["system_effect_count"] = 2
        self.check_hold("SYSTEM_EFFECT_COUNT_NOT_ONE")

    def test_native_escape_required(self):
        self.example["native_escape"] = False
        self.check_hold("MISSING_RECOVERY_OR_ESCAPE")

    def test_stop_wins(self):
        self.example["stop_supported"] = False
        self.check_hold("MISSING_STOP")

    def test_24h_exactly_is_not_greater_than_24h(self):
        self.example["seed_observations"][1]["observed_at"] = "2026-11-08T16:00:00Z"
        self.check_hold("COLD_SURVIVAL_GT24H_NOT_EVEN_STRUCTURALLY_SHOWN")

    def test_distinct_renderer_required(self):
        self.example["seed_observations"][1]["renderer_epoch"] = "fixture-1"
        self.check_hold("COLD_SURVIVAL_GT24H_NOT_EVEN_STRUCTURALLY_SHOWN")

    def test_missing_second_observation(self):
        self.example["seed_observations"].pop()
        self.check_hold("MISSING_COLD_SURVIVAL_PAIR")

    def test_invalid_clock_is_not_promoted(self):
        self.example["seed_observations"][1]["observed_at"] = "not-a-time"
        self.check_hold("INVALID_COLD_SURVIVAL_TIMES")

    def test_handoff_exactly_once(self):
        self.example["handoffs"].append(copy.deepcopy(self.example["handoffs"][0]))
        self.check_hold("HANDOFF_COUNT_NOT_ONE")

    def test_sender_cannot_ack_as_receiver(self):
        self.example["receipt"]["issued_by"] = "fixture-producer"
        self.check_hold("RECEIVER_ORIGIN_READBACK_NOT_STRUCTURALLY_SHOWN")

    def test_missing_receipt_cannot_claim_pickup(self):
        self.example["receipt"] = None
        self.check_hold("RECEIVER_ORIGIN_READBACK_NOT_STRUCTURALLY_SHOWN")

    def test_unauthorized_cross_work_handoff(self):
        self.example["handoffs"][0]["work_id"] = "not-original"
        self.check_hold("HANDOFF_IDENTITY_CONFLICT")

    def test_no_material_delta_quiesces_without_fake_runtime(self):
        self.example["material_delta"] = False
        result = evaluate(self.example)
        self.assertEqual(result["shadow"], "NO_MATERIAL_DELTA")
        self.assertEqual(result["native_x2"], "HOLD_UNATTESTED_RECEIVER")
        self.assertEqual(result["independent_sync"], "UNPROVEN")

    def test_even_forged_external_verified_flag_does_not_promote(self):
        self.example["external_verified"] = True
        self.example["trusted_x2_reboot_attestation"] = "I say so"
        result = evaluate(self.example)
        self.assertEqual(result["native_x2"], "HOLD_UNATTESTED_RECEIVER")
        self.assertEqual(result["shadow"], "STRUCTURE_PASS_NOT_ATTESTATION")


if __name__ == "__main__":
    unittest.main()
