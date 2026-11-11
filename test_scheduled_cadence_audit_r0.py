"""Deterministic schedule-coverage tests using fabricated run metadata.

No fixture is proof of a real scheduled wake; the production auditor queries
GitHub Actions separately and labels absence as an unobserved tick.
"""
import unittest
from examples.cotalkitout.scheduled_cadence_audit_r0 import coverage, instant

def entry(identity, when, *, event="schedule", conclusion="success",
          name="CoGoAll unattended proof pulse"):
    return {"id":identity,"created_at":when,"name":name,
            "event":event,"conclusion":conclusion}

NOW="2026-11-09T10:21:00Z"

class Tests(unittest.TestCase):
    def test_one_wake_does_not_prove_hourly_coverage(self):
        d=coverage([entry(42552131960,"2026-11-09T02:39:25Z")],observed_at=NOW)
        self.assertEqual(d["state"],"SCHEDULE_TICKS_UNOBSERVED")
        self.assertEqual(len(d["matched_scheduled_runs"]),1)
        self.assertGreater(len(d["unobserved_tick_times"]),0)
        self.assertFalse(d["self_certified_continuity"])

    def test_one_matured_tick_seen(self):
        d=coverage([entry(1,"2026-11-09T03:20:00Z")],
                   observed_at="2026-11-09T04:21:00Z",
                   since="2026-11-09T02:30:00Z",lookback_hours=2)
        self.assertEqual(d["state"],"SCHEDULE_COVERAGE_OBSERVED")
        self.assertEqual(d["expected_matured_ticks"],1)
        self.assertFalse(d["actual_work_effect"])

    def test_failed_run_observed_not_success(self):
        d=coverage([entry(1,"2026-11-09T03:20:00Z",conclusion="failure")],
                   observed_at="2026-11-09T04:21:00Z",
                   since="2026-11-09T02:30:00Z",lookback_hours=2)
        self.assertEqual(d["state"],"SCHEDULE_RUNS_NOT_ALL_SUCCESSFUL")

    def test_push_not_scheduled_wake(self):
        d=coverage([entry(1,"2026-11-09T03:20:00Z",event="push")],
                   observed_at="2026-11-09T04:21:00Z",
                   since="2026-11-09T02:30:00Z",lookback_hours=2)
        self.assertEqual(d["state"],"SCHEDULE_TICKS_UNOBSERVED")

    def test_dispatch_not_scheduled_wake(self):
        d=coverage([entry(1,"2026-11-09T03:20:00Z",event="workflow_dispatch")],
                   observed_at="2026-11-09T04:21:00Z",
                   since="2026-11-09T02:30:00Z",lookback_hours=2)
        self.assertEqual(d["state"],"SCHEDULE_TICKS_UNOBSERVED")

    def test_other_workflow_not_scheduled_wake(self):
        d=coverage([entry(1,"2026-11-09T03:20:00Z",name="different")],
                   observed_at="2026-11-09T04:21:00Z",
                   since="2026-11-09T02:30:00Z",lookback_hours=2)
        self.assertEqual(d["state"],"SCHEDULE_TICKS_UNOBSERVED")

    def test_late_run_not_assumed_on_time(self):
        d=coverage([entry(1,"2026-11-09T03:52:00Z")],
                   observed_at="2026-11-09T04:21:00Z",
                   since="2026-11-09T02:30:00Z",lookback_hours=2,
                   grace_minutes=30)
        self.assertEqual(d["state"],"SCHEDULE_TICKS_UNOBSERVED")

    def test_duplicate_run_identity_rejected(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            coverage([entry(1,"2026-11-09T03:20:00Z"),
                      entry(1,"2026-11-09T03:21:00Z")],
                     observed_at="2026-11-09T04:21:00Z")

    def test_future_run_time_rejected(self):
        with self.assertRaisesRegex(ValueError,"FUTURE"):
            coverage([entry(1,"2026-11-10T12:00:00Z")],observed_at=NOW)

    def test_censored_history_not_false_gap(self):
        d=coverage([entry(12,"2026-11-09T09:59:00Z")],
                   observed_at=NOW,reported_total=200)
        self.assertEqual(d["state"],"HISTORY_CENSORED")

    def test_no_matured_tick_not_failure(self):
        d=coverage([],observed_at="2026-11-09T03:21:00Z",
                   since="2026-11-09T03:05:00Z")
        self.assertEqual(d["state"],"INSUFFICIENT_MATURED_TICKS")

    def test_unbounded_horizon_rejected(self):
        with self.assertRaisesRegex(ValueError,"BOUNDED"):
            coverage([],observed_at=NOW,lookback_hours=48)

    def test_naive_clock_rejected(self):
        with self.assertRaisesRegex(ValueError,"TIMEZONE_REQUIRED"):
            instant("2026-11-09T10:21:00")

    def test_no_self_attestation(self):
        d=coverage([entry(1,"2026-11-09T03:20:00Z")],
                   observed_at="2026-11-09T04:21:00Z",
                   since="2026-11-09T02:30:00Z",lookback_hours=2)
        self.assertFalse(d["independent_receiver_ack"])
        self.assertFalse(d["native_x2_proof"])

if __name__=="__main__":
    unittest.main(verbosity=2)
