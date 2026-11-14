#!/usr/bin/env python3
"""Public, synthetic-only CoMeasure cross-family falsification canary.

Run: python -m unittest -v test_outcome_crosswalk.py
No network, provider, credentials, actual receiver or production measurements.
"""
import copy
import re
import unittest
from fractions import Fraction


class Hold(ValueError):
    """Fail closed when a declaration is incomplete or semantically invalid."""


def require(test, reason):
    if not test:
        raise Hold(reason)


_RATIONAL = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:/[1-9][0-9]*)?\Z")
_ID = re.compile(r"[a-z][a-z0-9_-]{0,31}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")


def exact_number(value):
    """Accept a bounded exact string, not a binary float or null proxy."""
    require(type(value) is str and 0 < len(value) <= 40 and _RATIONAL.fullmatch(value),
            "HOLD_EXACT_RATIONAL_REQUIRED")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise Hold("HOLD_INVALID_RATIONAL") from exc


def exact_text(number):
    return str(number.numerator) if number.denominator == 1 else str(number)


def synthetic_energy(envelope):
    """Model energy as sum(P_i * duration_i), in joules, under constant-power assumption."""
    require(isinstance(envelope, dict), "HOLD_ENVELOPE_REQUIRED")
    require(envelope.get("mode") == "SYNTHETIC_TEST_ONLY", "HOLD_REAL_MEASUREMENT_UNPROVEN")
    require(envelope.get("model") == "CONSTANT_POWER_SEGMENTS", "HOLD_POWER_MODEL_UNBOUND")
    require(envelope.get("power_unit") == "W" and envelope.get("duration_unit") == "s",
            "HOLD_UNBOUND_UNITS")
    segments = envelope.get("segments")
    require(type(segments) is list and 0 < len(segments) <= 100, "HOLD_SEGMENT_SCOPE")
    total_j, total_s = Fraction(0), Fraction(0)
    for segment in segments:
        require(isinstance(segment, dict), "HOLD_SEGMENT_RECORD")
        watts = exact_number(segment.get("power_w"))
        seconds = exact_number(segment.get("duration_s"))
        require(watts >= 0 and seconds > 0, "HOLD_POWER_OR_DURATION_DOMAIN")
        total_j += watts * seconds
        total_s += seconds
    return {
        "evidence_class": "SYNTHETIC_DERIVATION_ONLY",
        "energy_j": exact_text(total_j),
        "duration_s": exact_text(total_s),
        "uncertainty_state": "UNBOUNDED_MODEL_BIAS_NO_CALIBRATION",
        "operational_measurement": None,
    }


def synthetic_ack_claim_coverage(envelope):
    """Bound a simulated *claim* ratio; never authenticate an actual receiver."""
    require(isinstance(envelope, dict), "HOLD_ENVELOPE_REQUIRED")
    require(envelope.get("mode") == "SYNTHETIC_TEST_ONLY", "HOLD_EXTERNAL_RECEIVER_AUTHENTICATION_REQUIRED")
    require(envelope.get("coverage_complete") is True, "HOLD_COVERAGE_UNKNOWN")
    eligible = envelope.get("eligible")
    events = envelope.get("events")
    require(type(eligible) is list and len(eligible) <= 100, "HOLD_ELIGIBILITY_SCOPE")
    require(type(events) is list and len(events) <= 500, "HOLD_EVENT_SCOPE")
    objects = {}
    for item in eligible:
        require(isinstance(item, dict), "HOLD_ELIGIBILITY_RECORD")
        work_id, digest = item.get("work_id"), item.get("sha256")
        require(type(work_id) is str and _ID.fullmatch(work_id), "HOLD_WORK_ID")
        require(type(digest) is str and _SHA.fullmatch(digest), "HOLD_SOURCE_HASH")
        require(work_id not in objects, "HOLD_DUPLICATE_ELIGIBLE_WORK")
        objects[work_id] = digest
    seen_event_ids, acked, failed = set(), set(), set()
    for event in events:
        require(isinstance(event, dict), "HOLD_EVENT_RECORD")
        event_id = event.get("event_id")
        work_id = event.get("work_id")
        event_kind = event.get("kind")
        require(type(event_id) is str and _ID.fullmatch(event_id), "HOLD_EVENT_ID")
        require(event_id not in seen_event_ids, "HOLD_DUPLICATE_EVENT_ID")
        seen_event_ids.add(event_id)
        require(work_id in objects, "HOLD_EVENT_OUTSIDE_ELIGIBLE_SCOPE")
        require(event.get("sha256") == objects[work_id], "HOLD_EXACT_OBJECT_MISMATCH")
        require(event_kind in ("PROVIDER_SENT", "RECEIVER_ACK_CLAIM", "NONDELIVERY"),
                "HOLD_UNKNOWN_EVENT_KIND")
        if event_kind == "RECEIVER_ACK_CLAIM":
            acked.add(work_id)
        if event_kind == "NONDELIVERY":
            failed.add(work_id)
    require(not (acked & failed), "HOLD_CONTRADICTORY_RECIPIENT_EVENTS")
    if not objects:
        return {
            "evidence_class": "SYNTHETIC_ONLY",
            "state": "NOT_APPLICABLE_EMPTY_DENOMINATOR",
            "ratio": None,
            "independently_verified_receiver_acks": None,
        }
    return {
        "evidence_class": "SYNTHETIC_ACK_CLAIMS_ONLY",
        "state": "NOT_EXTERNALLY_ATTESTED",
        "numerator_claims": len(acked),
        "eligible_denominator": len(objects),
        "ratio": exact_text(Fraction(len(acked), len(objects))),
        "independently_verified_receiver_acks": None,
        "receiver_acceptance": None,
    }


A, B, C = "a" * 64, "b" * 64, "c" * 64


def receiver_fixture():
    return {
        "mode": "SYNTHETIC_TEST_ONLY",
        "coverage_complete": True,
        "eligible": [
            {"work_id": "alpha", "sha256": A},
            {"work_id": "beta", "sha256": B},
            {"work_id": "gamma", "sha256": C},
        ],
        "events": [
            {"event_id": "sent-alpha", "work_id": "alpha", "sha256": A, "kind": "PROVIDER_SENT"},
            {"event_id": "ack-beta", "work_id": "beta", "sha256": B, "kind": "RECEIVER_ACK_CLAIM"},
            {"event_id": "ack-gamma", "work_id": "gamma", "sha256": C, "kind": "RECEIVER_ACK_CLAIM"},
        ],
    }


def energy_fixture():
    return {
        "mode": "SYNTHETIC_TEST_ONLY", "model": "CONSTANT_POWER_SEGMENTS",
        "power_unit": "W", "duration_unit": "s",
        "segments": [
            {"power_w": "100", "duration_s": "10"},
            {"power_w": "40", "duration_s": "5"},
        ],
    }


class CoMeasureOutcomeCrosswalkR0(unittest.TestCase):
    def assert_held(self, call, reason):
        with self.assertRaisesRegex(Hold, reason):
            call()

    def test_a_energy_exact_joules_and_seconds(self):
        result = synthetic_energy(energy_fixture())
        self.assertEqual(result["energy_j"], "1200")
        self.assertEqual(result["duration_s"], "15")
        self.assertIsNone(result["operational_measurement"])

    def test_a_fractional_power_exact_arithmetic(self):
        data = energy_fixture()
        data["segments"] = [{"power_w": "1/2", "duration_s": "3"}]
        self.assertEqual(synthetic_energy(data)["energy_j"], "3/2")

    def test_a_non_si_or_ambiguous_units_hold(self):
        for field, bad in (("power_unit", "kW"), ("duration_unit", "ms")):
            data = energy_fixture()
            data[field] = bad
            self.assert_held(lambda: synthetic_energy(data), "HOLD_UNBOUND_UNITS")

    def test_a_zero_or_negative_duration_holds(self):
        for value in ("0", "-1"):
            data = energy_fixture()
            data["segments"][0]["duration_s"] = value
            self.assert_held(lambda: synthetic_energy(data), "HOLD_POWER_OR_DURATION_DOMAIN")

    def test_a_float_nan_and_null_hold(self):
        for value in (0.5, "NaN", None, "Infinity", "1/0"):
            data = energy_fixture()
            data["segments"][0]["power_w"] = value
            self.assert_held(lambda: synthetic_energy(data), "HOLD_EXACT_RATIONAL_REQUIRED|HOLD_INVALID_RATIONAL")

    def test_a_real_measurement_claim_is_not_promoted(self):
        data = energy_fixture()
        data["mode"] = "PRODUCTION"
        self.assert_held(lambda: synthetic_energy(data), "HOLD_REAL_MEASUREMENT_UNPROVEN")

    def test_b_two_claims_out_of_three_not_actual_acks(self):
        result = synthetic_ack_claim_coverage(receiver_fixture())
        self.assertEqual(result["ratio"], "2/3")
        self.assertEqual(result["numerator_claims"], 2)
        self.assertIsNone(result["independently_verified_receiver_acks"])
        self.assertIsNone(result["receiver_acceptance"])

    def test_b_sent_is_never_receiver_ack(self):
        data = receiver_fixture()
        data["events"] = [data["events"][0]]
        result = synthetic_ack_claim_coverage(data)
        self.assertEqual(result["ratio"], "0")
        self.assertEqual(result["numerator_claims"], 0)
        self.assertIsNone(result["independently_verified_receiver_acks"])

    def test_b_two_claims_same_work_id_count_only_once(self):
        data = receiver_fixture()
        data["events"].append({"event_id": "second-beta", "work_id": "beta", "sha256": B, "kind": "RECEIVER_ACK_CLAIM"})
        self.assertEqual(synthetic_ack_claim_coverage(data)["ratio"], "2/3")

    def test_b_duplicate_event_identity_holds(self):
        data = receiver_fixture()
        data["events"][1]["event_id"] = data["events"][0]["event_id"]
        self.assert_held(lambda: synthetic_ack_claim_coverage(data), "HOLD_DUPLICATE_EVENT_ID")

    def test_b_mismatched_object_hash_holds(self):
        data = receiver_fixture()
        data["events"][1]["sha256"] = A
        self.assert_held(lambda: synthetic_ack_claim_coverage(data), "HOLD_EXACT_OBJECT_MISMATCH")

    def test_b_unknown_work_id_holds(self):
        data = receiver_fixture()
        data["events"][1]["work_id"] = "unregistered"
        self.assert_held(lambda: synthetic_ack_claim_coverage(data), "HOLD_EVENT_OUTSIDE_ELIGIBLE_SCOPE")

    def test_b_ambiguous_or_incomplete_coverage_holds(self):
        data = receiver_fixture()
        data["coverage_complete"] = False
        self.assert_held(lambda: synthetic_ack_claim_coverage(data), "HOLD_COVERAGE_UNKNOWN")

    def test_b_duplicate_eligible_id_holds(self):
        data = receiver_fixture()
        data["eligible"].append(copy.deepcopy(data["eligible"][0]))
        self.assert_held(lambda: synthetic_ack_claim_coverage(data), "HOLD_DUPLICATE_ELIGIBLE_WORK")

    def test_b_no_eligible_work_is_not_zero_rate(self):
        data = receiver_fixture()
        data["eligible"] = []
        data["events"] = []
        result = synthetic_ack_claim_coverage(data)
        self.assertEqual(result["state"], "NOT_APPLICABLE_EMPTY_DENOMINATOR")
        self.assertIsNone(result["ratio"])

    def test_b_ack_and_non_delivery_conflict_holds(self):
        data = receiver_fixture()
        data["events"].append({"event_id": "failed-beta", "work_id": "beta", "sha256": B, "kind": "NONDELIVERY"})
        self.assert_held(lambda: synthetic_ack_claim_coverage(data), "HOLD_CONTRADICTORY_RECIPIENT_EVENTS")

    def test_b_real_receiver_claim_is_not_promoted(self):
        data = receiver_fixture()
        data["mode"] = "LIVE"
        self.assert_held(lambda: synthetic_ack_claim_coverage(data), "HOLD_EXTERNAL_RECEIVER_AUTHENTICATION_REQUIRED")

    def test_independent_family_shapes_and_distinct_units(self):
        physical = synthetic_energy(energy_fixture())
        reception = synthetic_ack_claim_coverage(receiver_fixture())
        self.assertEqual(physical["energy_j"], "1200")
        self.assertEqual(reception["ratio"], "2/3")
        self.assertNotIn("energy_j", reception)
        self.assertNotIn("eligible_denominator", physical)


if __name__ == "__main__":
    unittest.main()
