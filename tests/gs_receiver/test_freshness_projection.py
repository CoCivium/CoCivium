"""Isolated freshness projection contract. Not deployed on X2."""
import unittest

def project(sample, now_seconds, maximum_age_seconds):
    """Return evidence state, never infer receiver health from UI visibility."""
    if sample is None:
        return {"state": "NO_EVIDENCE", "age_seconds": None}
    observed = sample.get("observed_at")
    verified = sample.get("verified")
    if not isinstance(observed, (int, float)) or not verified:
        return {"state": "UNVERIFIED", "age_seconds": None}
    age = now_seconds - observed
    if age < 0:
        return {"state": "CLOCK_SKEW", "age_seconds": age}
    if age > maximum_age_seconds:
        return {"state": "STALE", "age_seconds": age}
    return {"state": "FRESH_VERIFIED", "age_seconds": age}

class FreshnessTests(unittest.TestCase):
    def test_fresh_stale_boundary(self):
        s = {"observed_at": 100, "verified": True}
        self.assertEqual(project(s, 160, 60)["state"], "FRESH_VERIFIED")
        self.assertEqual(project(s, 161, 60)["state"], "STALE")

    def test_no_evidence_is_not_success(self):
        self.assertEqual(project(None, 200, 60)["state"], "NO_EVIDENCE")
        self.assertEqual(project({"observed_at": 190, "verified": False}, 200, 60)["state"], "UNVERIFIED")

    def test_clock_skew_is_not_freshness(self):
        self.assertEqual(project({"observed_at": 210, "verified": True}, 200, 60)["state"], "CLOCK_SKEW")

if __name__ == "__main__":
    unittest.main(verbosity=2)
