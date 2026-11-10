"""Isolated freshness projection contract. Not deployed on X2."""
import unittest
import math


def project(sample, now_seconds, maximum_age_seconds, verify_receipt=None):
    """Only an independently accepted receipt can make evidence fresh-verified."""
    if sample is None:
        return {"state": "NO_EVIDENCE", "age_seconds": None}
    observed = sample.get("observed_at")
    if (not isinstance(observed, (int, float))
            or isinstance(observed, bool)
            or not math.isfinite(observed)
            or not callable(verify_receipt)
            or not verify_receipt(sample)):
        return {"state": "UNVERIFIED", "age_seconds": None}
    age = now_seconds - observed
    if age < 0:
        return {"state": "CLOCK_SKEW", "age_seconds": age}
    if age > maximum_age_seconds:
        return {"state": "STALE", "age_seconds": age}
    return {"state": "FRESH_VERIFIED", "age_seconds": age}


class FreshnessTests(unittest.TestCase):
    @staticmethod
    def trusted(sample):
        # Fixture only: real integration must verify signature/hash and custody.
        return sample.get("receipt_id") == "fixture-accepted"

    def test_fresh_stale_boundary(self):
        s = {"observed_at": 100, "receipt_id": "fixture-accepted"}
        self.assertEqual(project(s, 160, 60, self.trusted)["state"], "FRESH_VERIFIED")
        self.assertEqual(project(s, 161, 60, self.trusted)["state"], "STALE")

    def test_no_evidence_is_not_success(self):
        self.assertEqual(project(None, 200, 60, self.trusted)["state"], "NO_EVIDENCE")
        self.assertEqual(project({"observed_at": 190}, 200, 60, self.trusted)["state"], "UNVERIFIED")

    def test_clock_skew_is_not_freshness(self):
        s = {"observed_at": 210, "receipt_id": "fixture-accepted"}
        self.assertEqual(project(s, 200, 60, self.trusted)["state"], "CLOCK_SKEW")

    def test_self_asserted_verified_flag_cannot_bypass_verifier(self):
        forged = {"observed_at": 199, "verified": True, "receipt_id": "forged"}
        self.assertEqual(project(forged, 200, 60, self.trusted)["state"], "UNVERIFIED")
        self.assertEqual(project(forged, 200, 60)["state"], "UNVERIFIED")

    def test_nonfinite_timestamps_are_unverified(self):
        for observed in (float("nan"), float("inf"), float("-inf")):
            s = {"observed_at": observed, "receipt_id": "fixture-accepted"}
            self.assertEqual(project(s, 200, 60, self.trusted)["state"], "UNVERIFIED")

    def test_boolean_timestamp_is_not_valid_time(self):
        s = {"observed_at": True, "receipt_id": "fixture-accepted"}
        self.assertEqual(project(s, 200, 60, self.trusted)["state"], "UNVERIFIED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
