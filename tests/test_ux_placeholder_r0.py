"""Adversarial CoIb/CoEther/CoAsym UX-placeholder semantics.

No remote fetches, devices, network listeners, telemetry or UI mutation.
Execute under ordinary and -O Python; invalid candidates must fail closed.
"""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ai" / "measurement"))
from ux_placeholder_r0 import (new_placeholder, validate_placeholder,
                               initial_projections, ETHER_FACETS)


class PlaceholderContractTests(unittest.TestCase):
    def rejects(self, candidate):
        with self.assertRaises(ValueError):
            validate_placeholder(candidate)

    def test_three_slots_not_telemetry(self):
        items = initial_projections()
        self.assertEqual([x["slot"] for x in items], ["CoIb", "CoEther", "CoAsym"])
        for p in items:
            with self.subTest(slot=p["slot"]):
                self.assertIsNone(p["value"])
                self.assertIsNone(p["unit_id"])
                self.assertIsNone(p["observed_at_utc"])
                self.assertFalse(p["receiver_ack"])
                self.assertFalse(p["measurement_verified"])
                self.assertEqual(p["evidence_refs"], [])
                self.assertIn("PLACEHOLDER_NE_MEASUREMENT", p["nonclaims"])
                self.assertEqual(validate_placeholder(p), p)

    def test_coib_has_real_readback_wake(self):
        p = initial_projections()[0]
        self.assertEqual(p["state"], "AWAITING_EVIDENCE")
        self.assertIn("independent_receiver_readback", p["wake_condition"])
        self.assertEqual(p["established_metric_ref"], "CoMx.receiver_pickup_fraction")

    def test_coether_remains_open_research_placeholder(self):
        p = new_placeholder("CoEther")
        self.assertEqual(p["state"], "RESEARCH_CONCEPT")
        self.assertEqual(p["kind"], "OPEN_INTERSTICE_RESEARCH_PLACEHOLDER")
        self.assertEqual(p["display"], "Open questions; no empirical bridge established")
        self.assertIsNone(p["established_metric_ref"])
        self.assertIsNone(p["value"])
        self.assertFalse(p["measurement_verified"])
        self.assertIn("no verified common mechanism", p["reason"])

    def test_coether_transport_is_optional_child_not_the_umbrella(self):
        p = new_placeholder("CoEther.Transport")
        self.assertEqual(p["state"], "UNKNOWN")
        self.assertEqual(p["display"], "Not yet measured")
        self.assertEqual(p["established_metric_ref"], "CoTime.source_age")
        c = copy.deepcopy(p)
        c["display"] = "Signal Clean"
        self.rejects(c)
        # Never collapse the umbrella into its narrow measured descendant.
        c = new_placeholder("CoEther")
        c["established_metric_ref"] = "CoTime.source_age"
        self.rejects(c)

    def test_coether_facets_distinct_without_merger_assertion(self):
        self.assertIn("PHYSICAL_OBSERVATION", ETHER_FACETS)
        self.assertIn("VIRTUAL_REPRESENTATION", ETHER_FACETS)
        self.assertIn("MYTHOS_NARRATIVE", ETHER_FACETS)
        self.assertIn("PHILOSOPHICAL_G_D_INQUIRY", ETHER_FACETS)
        self.assertIn("UNKNOWN_OBSERVER_GAP", ETHER_FACETS)
        p = new_placeholder("CoEther", reason="open inquiry, no factual interpretation yet")
        self.assertEqual(p["reason"], "open inquiry, no factual interpretation yet")
        for key, value in [
            ("merged_with", "CoIb"),
            ("god_signal_confirmed", True),
            ("real_virtual_bridge", "PROVEN"),
        ]:
            with self.subTest(key=key):
                c = copy.deepcopy(p)
                c[key] = value
                self.rejects(c)

    def test_coether_cannot_be_promoted_to_measured_or_not_applicable(self):
        for state in ("UNKNOWN", "AWAITING_EVIDENCE", "NOT_APPLICABLE"):
            with self.subTest(state=state):
                with self.assertRaises(ValueError):
                    new_placeholder("CoEther", state=state,
                                    reason="symbolic only", wake_condition="test")

    def test_coasym_not_synthetic_physics(self):
        self.assertIsNone(initial_projections()[2]["established_metric_ref"])
        with self.assertRaises(ValueError):
            new_placeholder("CoAsym", state="AWAITING_EVIDENCE",
                            wake_condition="phony_sensor")
        with self.assertRaises(ValueError):
            new_placeholder("CoAsym", state="RESEARCH_CONCEPT")

    def test_unknown_not_a_zero(self):
        for val in ("0", 0, 0.0, False, "Hold 1x", "Clean", "100%"):
            with self.subTest(value=val):
                c = new_placeholder("CoEther")
                c["value"] = val
                self.rejects(c)

    def test_no_unit_or_timestamp_from_unobserved(self):
        for name, val in [("unit_id", "ms"),
                          ("observed_at_utc", "2026-11-11T15:00:00Z")]:
            c = new_placeholder("CoEther")
            c[name] = val
            self.rejects(c)

    def test_forged_receiver_ack_and_green(self):
        for name, val in [("receiver_ack", True),
                          ("measurement_verified", True),
                          ("authority", "RELEASE_APPROVED")]:
            c = new_placeholder("CoIb")
            c[name] = val
            self.rejects(c)

    def test_ack_prose_is_not_evidence(self):
        c = new_placeholder("CoIb")
        c["evidence_refs"] = ["receipt:written_by_model_not_receiver"]
        self.rejects(c)

    def test_forged_hardcoded_metric(self):
        c = new_placeholder("CoIb")
        c["established_metric_ref"] = "CoEther.signal_clean_percentage"
        self.rejects(c)
        c = new_placeholder("CoEther")
        c["measurement_gate"] = "NO_GATES_NEEDED"
        self.rejects(c)

    def test_pending_requires_specific_wake(self):
        with self.assertRaises(ValueError):
            new_placeholder("CoIb", state="AWAITING_EVIDENCE")
        self.assertEqual(new_placeholder("CoIb", state="AWAITING_EVIDENCE",
                         wake_condition="receiver_has_exact_object_readproof")["state"],
                         "AWAITING_EVIDENCE")

    def test_not_applicable_needs_justification(self):
        with self.assertRaises(ValueError):
            new_placeholder("CoEther.Transport", state="NOT_APPLICABLE")
        p = new_placeholder("CoEther.Transport", state="NOT_APPLICABLE",
                            reason="offline isolated, no transport")
        self.assertIn("declared, not independently verified", p["display"])

    def test_unknown_must_not_claim_schedule(self):
        with self.assertRaises(ValueError):
            new_placeholder("CoEther.Transport", state="UNKNOWN", wake_condition="next-hour")

    def test_wrong_slot_and_extraneous_telemetry(self):
        with self.assertRaises(ValueError):
            new_placeholder("CoSpeedo.CPU", state="UNKNOWN")
        c = new_placeholder("CoEther")
        c["packet_loss"] = 0
        self.rejects(c)

    def test_nonclaims_must_not_be_dropped(self):
        c = new_placeholder("CoIb")
        c["nonclaims"] = c["nonclaims"][:-1]
        self.rejects(c)

    def test_validate_does_not_mutate_input(self):
        c = new_placeholder("CoIb")
        clone = validate_placeholder(c)
        clone["nonclaims"].clear()
        self.assertNotEqual(c, clone)


if __name__ == "__main__":
    unittest.main()
