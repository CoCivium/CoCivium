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
                               initial_projections, ETHER_FACETS,
                               propose_relation, validate_relation_proposal,
                               RELATION_NONCLAIMS)


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



class CrossDomainProposalTests(unittest.TestCase):
    """An appealing connection is not evidence of a shared physical cause."""

    def modeled(self):
        return propose_relation(
            "synthetic:virtual_clock_model",
            "VIRTUAL_REPRESENTATION", "PHYSICAL_OBSERVATION", "MODELS",
            "A simulated timing rule may predict a future instrument reading",
            discriminator="Pre-register a blinded prospective holdout and compare predictions.",
            ordinary_alternative="Overfitting shared calibration or a common source sample",
        )

    def analogized(self):
        return propose_relation(
            "synthetic:mythos_pattern_analogy",
            "MYTHOS_NARRATIVE", "PHYSICAL_OBSERVATION", "ANALOGY_TO",
            "A fictional pattern resembles an observed instrument trace",
        )

    def rejects(self, candidate):
        with self.assertRaises(ValueError):
            validate_relation_proposal(candidate)

    def test_model_proposal_requires_prospective_discriminator(self):
        model = self.modeled()
        self.assertEqual(model["status"], "PROPOSED_UNVERIFIED")
        self.assertEqual(model["interpretation_domain"], "EMPIRICAL_TEST_PROPOSAL")
        self.assertFalse(model["verified_bridge"])
        self.assertIsNone(model.get("actual_observation"))
        self.assertEqual(model["evidence_refs"], [])
        self.assertIn("CANDIDATE_MERGER_NE_IDENTITY", model["nonclaims"])

    def test_analogy_stays_symbolic_and_cannot_prove_mechanism(self):
        analogy = self.analogized()
        self.assertEqual(analogy["interpretation_domain"], "NARRATIVE_OR_PHILOSOPHICAL")
        self.assertIsNone(analogy["discriminator"])
        self.assertEqual(analogy["source_scope"], "SYNTHETIC_FIXTURE_ONLY")
        self.assertFalse(analogy["verified_bridge"])

    def test_philosophical_interpretation_is_not_divine_signal_evidence(self):
        thought = propose_relation(
            "synthetic:interpretation_fixture",
            "PHYSICAL_OBSERVATION", "PHILOSOPHICAL_G_D_INQUIRY",
            "INTERPRETED_AS", "A fictional observer interprets a pattern spiritually",
        )
        self.assertEqual(thought["status"], "PROPOSED_UNVERIFIED")
        self.assertFalse(thought["receiver_ack"])
        self.assertEqual(thought["evidence_refs"], [])
        for key, value in [
            ("divine_origin_verified", True),
            ("signal_verified", "G_d"),
        ]:
            with self.subTest(key=key):
                changed = copy.deepcopy(thought)
                changed[key] = value
                self.rejects(changed)

    def test_candidate_merger_stays_unverified_even_when_testable(self):
        merger = propose_relation(
            "synthetic:merger_fixture",
            "VIRTUAL_REPRESENTATION", "PHYSICAL_OBSERVATION",
            "MERGER_HYPOTHESIS",
            "A simulated system may encode the same referent as a measured event",
            discriminator="Use independent instruments to predict a hidden new observation.",
            ordinary_alternative="Two descriptions may share training examples or calibration",
        )
        self.assertEqual(merger["status"], "PROPOSED_UNVERIFIED")
        self.assertFalse(merger["verified_bridge"])
        self.assertNotIn("SAME_REFERENT", merger["edge_type"])

    def test_wrong_edges_never_promote_analogy_to_identity(self):
        for edge in ("SAME_REFERENT", "CAUSES", "G_D_CONFIRMED", "VERIFIED_MERGER"):
            with self.subTest(edge=edge):
                changed = self.analogized()
                changed["edge_type"] = edge
                self.rejects(changed)

    def test_no_self_verification_or_receiver_ack(self):
        for key, value in [
            ("status", "VERIFIED"),
            ("verified_bridge", True),
            ("receiver_ack", True),
            ("authority", "COEX_APPROVED"),
            ("source_scope", "INDEPENDENT_OBSERVATORY"),
            ("evidence_refs", ["claimed:independent_reviewer"]),
        ]:
            with self.subTest(key=key):
                changed = self.modeled()
                changed[key] = value
                self.rejects(changed)

    def test_empirical_proposal_requires_competing_explanation(self):
        for key, value in [
            ("discriminator", None),
            ("discriminator", "Just trust us"),
            ("ordinary_alternative", None),
            ("ordinary_alternative", "N/A"),
        ]:
            with self.subTest(key=key):
                changed = self.modeled()
                changed[key] = value
                self.rejects(changed)

    def test_no_empirical_merger_with_mythos_or_g_d(self):
        for facet in ("MYTHOS_NARRATIVE", "PHILOSOPHICAL_G_D_INQUIRY"):
            with self.subTest(facet=facet):
                changed = self.modeled()
                changed["target_facet"] = facet
                self.rejects(changed)

    def test_models_has_declared_direction_not_mythos_as_sensor(self):
        for src, dst in [
            ("PHYSICAL_OBSERVATION", "VIRTUAL_REPRESENTATION"),
            ("UNKNOWN_OBSERVER_GAP", "PHYSICAL_OBSERVATION"),
        ]:
            with self.subTest(src=src):
                changed = self.modeled()
                changed["source_facet"], changed["target_facet"] = src, dst
                self.rejects(changed)

    def test_unknown_facet_requires_versioned_extension(self):
        changed = self.analogized()
        changed["target_facet"] = "NEW_UNKNOWN_FACET"
        self.rejects(changed)

    def test_same_facet_not_a_cross_domain_rel(self):
        changed = self.analogized()
        changed["target_facet"] = changed["source_facet"]
        self.rejects(changed)

    def test_symbolic_relation_must_not_hide_empirical_witness(self):
        changed = self.analogized()
        changed["discriminator"] = "Faked external evidence from source"
        self.rejects(changed)
        changed = self.analogized()
        changed["interpretation_domain"] = "EMPIRICAL_TEST_PROPOSAL"
        self.rejects(changed)

    def test_proposed_relation_must_preserve_nonclaims(self):
        changed = self.modeled()
        changed["nonclaims"] = list(RELATION_NONCLAIMS[:-1])
        self.rejects(changed)

    def test_replay_is_pure_and_does_not_mutate_original(self):
        original = self.modeled()
        verified_copy = validate_relation_proposal(original)
        verified_copy["nonclaims"].clear()
        self.assertNotEqual(original, verified_copy)
        self.assertEqual(validate_relation_proposal(original), original)

    def test_id_and_hypothesis_are_bounded(self):
        changed = self.analogized()
        changed["proposal_id"] = "a"
        self.rejects(changed)
        changed = self.analogized()
        changed["hypothesis"] = ""
        self.rejects(changed)


if __name__ == "__main__":
    unittest.main()
