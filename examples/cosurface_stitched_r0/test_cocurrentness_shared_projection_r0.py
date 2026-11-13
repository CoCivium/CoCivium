"""Shared CoCurrentness projection source-only regression checks."""
import unittest
from cocurrentness_shared_projection_r0 import project

NOW="2026-11-11T01:57:00Z"
def obs(t,ref=None,ack=None):
    return {"observed_at":t,"receipt_ref":ref,"receiver_ack":ack}
class CurrentnessTests(unittest.TestCase):
    def test_mixed_freshness_is_not_green(self):
        p=project({"bar":obs("2026-11-11T01:56:45Z"),"speedo":obs("2026-11-11T01:50:00Z")},NOW)
        self.assertEqual(p["status"],"MIXED_FRESHNESS")
        self.assertEqual(p["sources"]["speedo"]["freshness"],"STALE")
    def test_same_timestamp_same_state_for_all_renderers(self):
        p=project({"bar":obs(NOW),"speedo":obs(NOW),"orb":obs(NOW)},NOW)
        self.assertEqual(p["status"],"FRESH_OBSERVATIONS_ONLY")
        self.assertEqual(p["receiver_acceptance"],"UNVERIFIED")
    def test_missing_observer_unknown(self):
        p=project({"bar":obs(NOW),"observer":obs(None)},NOW)
        self.assertEqual(p["status"],"MIXED_FRESHNESS")
        self.assertEqual(p["sources"]["observer"]["freshness"],"UNKNOWN")
    def test_future_clock_conflict(self):
        p=project({"bar":obs("2026-11-11T01:58:00Z")},NOW)
        self.assertEqual(p["status"],"CONFLICT")
    def test_receipt_not_receiver(self):
        p=project({"bar":obs(NOW,"some-claimed-receipt",True)},NOW)
        self.assertEqual(p["receiver_acceptance"],"UNVERIFIED")
        self.assertEqual(p["sources"]["bar"]["receiver_ack"],"CLAIMED_NOT_VERIFIED")
    def test_absent_observations(self):
        self.assertEqual(project({},NOW)["status"],"UNKNOWN")
    def test_timezone_required(self):
        with self.assertRaises(ValueError):project({}, "2026-11-11T01:57:00")
    def test_bounded_inputs(self):
        with self.assertRaises(ValueError):project({},NOW,max_age_seconds=0)
        with self.assertRaises(ValueError):project({str(i):obs(NOW) for i in range(33)},NOW)
    def test_stale_is_not_failure(self):
        p=project({"speedo":obs("2026-11-10T23:00:00Z")},NOW)
        self.assertEqual(p["status"],"STALE_OR_UNKNOWN")
        self.assertNotIn("FAILED",str(p))
if __name__=="__main__":unittest.main()
