"""CoArrival inverse-prerequisite tests: synthetic only, no OS or network."""
import copy
from datetime import timedelta
import json
import unittest

from cold_open_readiness import (
    ARRIVAL_PREREQUISITES, classify, trace_inverse_requirements,
)
from test_cold_open_readiness import fixture, NOW


class InverseProofTests(unittest.TestCase):
    def test_fully_populated_inventory_cannot_certify_user_arrival(self):
        result = classify(fixture(), at_utc=NOW)
        tree = result["inverse_proof_tree"]
        self.assertEqual(tree["root"], "COARRIVAL_USABLE_DESKTOP")
        self.assertEqual(tree["leaf_count"], 15)
        self.assertEqual(tree["inventory_indicated_count"], 5)
        self.assertEqual(tree["unverified_count"], 10)
        self.assertEqual(tree["first_missing_dependency"], "MOUSE_MAPPING_TESTED")
        self.assertEqual(tree["actual_user_acceptance"], "NOT_ATTESTED")
        self.assertIs(tree["success_claim"], False)
        self.assertEqual(result["state"], "HOLD_USABLE_DESKTOP_UNPROVEN")

    def test_first_missing_source_utility_is_explicit(self):
        src = fixture()
        src["peripheral_utility_process_candidates"] = [
            e for e in src["peripheral_utility_process_candidates"]
            if e["process_role"] != "MOUSE_UTILITY_CANDIDATE"
        ]
        tree = classify(src, at_utc=NOW)["inverse_proof_tree"]
        self.assertEqual(tree["first_missing_dependency"], "MOUSE_UTILITY_PRESENT")
        self.assertEqual(tree["unverified_count"], 11)

    def test_stale_source_downgrades_all_indications(self):
        result = classify(fixture(), at_utc=NOW + timedelta(hours=2))
        tree = result["inverse_proof_tree"]
        self.assertEqual(tree["inventory_indicated_count"], 0)
        self.assertEqual(tree["unverified_count"], 15)
        self.assertEqual(tree["first_missing_dependency"], "BOOT_COHORT_QUALIFIED")
        self.assertEqual(tree["all_paths"][0]["evidence"], "STALE_SNAPSHOT")
        self.assertFalse(result["snapshot_fresh"])

    def test_invalid_boot_prevents_false_qualification_of_other_leaves(self):
        src = fixture()
        src["boot_time_utc"] = None
        tree = classify(src, at_utc=NOW)["inverse_proof_tree"]
        self.assertEqual(tree["inventory_indicated_count"], 0)
        self.assertEqual(tree["all_paths"][0]["evidence"], "UNKNOWN")

    def test_inverse_dependency_retains_readable_causal_path(self):
        tree = classify(fixture(), at_utc=NOW)["inverse_proof_tree"]
        paths = [e["inverse_path"] for e in tree["unverified_dependencies"]]
        self.assertIn(
            ["COARRIVAL_USABLE_DESKTOP", "DESKTOP_USABLE", "NO_FOREGROUND_FOCUS_THEFT"],
            paths,
        )
        self.assertIn(
            ["COARRIVAL_USABLE_DESKTOP", "AUTO_RECOVERY_CONFIRMED",
             "NO_HUMAN_SESSION_CYCLING"],
            paths,
        )

    def test_user_reported_fake_pass_cannot_promote_runtime(self):
        src = fixture()
        src.update({
            "post_login_restoration_state": "PASS",
            "reboot_autostart_success": "YES",
            "all_turtles_ready": True,
            "signed_human_ack": "FAKE",
            "surface_alignment_and_scale": "PASS",
            "audio_muted_state": "UNMUTED",
            "visible_ui_screenshot_accepted": True,
        })
        report = classify(src, at_utc=NOW)
        self.assertEqual(report["state"], "HOLD_USABLE_DESKTOP_UNPROVEN")
        self.assertEqual(report["inverse_proof_tree"]["unverified_count"], 10)

    def test_cycle_is_held_not_mistaken_for_self_support(self):
        with self.assertRaisesRegex(ValueError, "HOLD_CYCLIC_REQUIREMENT"):
            trace_inverse_requirements({}, graph={"A": ("B",), "B": ("A",)}, root="A")

    def test_missing_leaf_does_not_create_implicit_pass(self):
        tree = trace_inverse_requirements({}, graph={"A": ("B",)}, root="A")
        self.assertEqual(tree["unverified_count"], 1)
        self.assertEqual(tree["all_paths"][0]["evidence"], "UNKNOWN")

    def test_excessive_depth_is_held(self):
        graph = {f"G{i}": (f"G{i+1}",) for i in range(12)}
        with self.assertRaisesRegex(ValueError, "HOLD_INVERSE_BUDGET_EXCEEDED"):
            trace_inverse_requirements({}, graph=graph, root="G0", max_depth=5)

    def test_excessive_node_budget_is_held(self):
        with self.assertRaisesRegex(ValueError, "HOLD_INVERSE_BUDGET_EXCEEDED"):
            trace_inverse_requirements({}, max_visits=4)

    def test_empty_dependency_is_held(self):
        with self.assertRaisesRegex(ValueError, "HOLD_INVALID_DEPENDENCIES"):
            trace_inverse_requirements({}, graph={"A": ()}, root="A")

    def test_unknown_evidence_label_cannot_be_treated_as_pass(self):
        with self.assertRaisesRegex(ValueError, "HOLD_UNRECOGNIZED_GATE_EVIDENCE"):
            trace_inverse_requirements({"B": "RUNTIME_PASS"}, graph={"A": ("B",)}, root="A")

    def test_boolean_evidence_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "HOLD_UNRECOGNIZED_GATE_EVIDENCE"):
            trace_inverse_requirements({"B": True}, graph={"A": ("B",)}, root="A")

    def test_all_declared_leaves_reported_still_not_human_accepted(self):
        all_gates = {}
        for children in ARRIVAL_PREREQUISITES.values():
            for leaf in children:
                if leaf not in ARRIVAL_PREREQUISITES:
                    all_gates[leaf] = "REPORTED_IN_SNAPSHOT"
        tree = trace_inverse_requirements(all_gates)
        self.assertEqual(tree["unverified_count"], 0)
        self.assertIs(tree["success_claim"], False)
        self.assertEqual(tree["actual_user_acceptance"], "NOT_ATTESTED")

    def test_sibling_shared_requirement_is_not_a_cycle(self):
        graph = {"ROOT": ("A", "B"), "A": ("EVIDENCE",), "B": ("EVIDENCE",)}
        tree = trace_inverse_requirements({"EVIDENCE": "REPORTED_IN_SNAPSHOT"},
                                          graph=graph, root="ROOT")
        self.assertEqual(tree["leaf_count"], 2)
        self.assertEqual(tree["inventory_indicated_count"], 2)

    def test_privacy_and_input_immutability(self):
        src = fixture()
        src["private_auth"] = "DO_NOT_EMIT_SENSITIVE_PAYLOAD"
        prior = copy.deepcopy(src)
        tree = classify(src, at_utc=NOW)["inverse_proof_tree"]
        self.assertEqual(src, prior)
        self.assertNotIn("DO_NOT_EMIT", json.dumps(tree))

    def test_deterministic_and_action_free(self):
        a = classify(fixture(), at_utc=NOW)
        b = classify(fixture(), at_utc=NOW)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        self.assertEqual(sum(a["effects"].values()), 0)
        self.assertEqual(a["next_safe_probe"],
                         "INDEPENDENT_POST_LOGIN_X2_UX_AND_RECEIVER_READBACK")


if __name__ == "__main__":
    unittest.main()
