"""Synthetic adversarial tests for transport-only Pulse metadata adapter."""
import copy
import unittest
from pulse_transport_observation import SCHEMA, observe_automation_run

NOW = "2026-11-09T00:32:04Z"


def fixture(status="no_update"):
    return {"is_enabled": True, "title": "PRIVATE_SHOULD_NEVER_EMIT",
            "prompt": "SECRET_SHOULD_NEVER_EMIT",
            "run_details": {"last_run": {
                "id": "PRIVATE_RUN_ID", "recorded_status": status,
                "scheduled_for": "2026-11-09T00:08:33Z",
                "started_at": "2026-11-09T00:27:32.216782Z",
                "completed_at": "2026-11-09T00:27:34.514054Z",
                "chat_ref": {"id": "PRIVATE_CHAT_REF"}}}}


class TransportOnlyTests(unittest.TestCase):
    def observe(self, task, now=NOW):
        result = observe_automation_run(task, sampled_at_utc=now)
        self.assertEqual(result["schema"], SCHEMA)
        for key in ("source_work_id", "source_revision", "eligibility_census_complete",
                    "pending_work_count", "receiver_readback", "verified_useful_effect"):
            self.assertIsNone(result[key])
        self.assertEqual(result["work_result_class"], "NOT_EVIDENCED")
        self.assertFalse(result["private_identifiers_retained"])
        self.assertNotIn("PRIVATE", str(result))
        return result

    def test_no_update_ne_healthy_idle(self):
        self.assertEqual(self.observe(fixture())["transport_state"], "RECORDED_NO_UPDATE__CAUSE_UNKNOWN")

    def test_lag_is_not_progress(self):
        r = self.observe(fixture())
        self.assertEqual(r["start_lag_seconds"], 1139.217)
        self.assertEqual(r["execution_duration_seconds"], 2.297)

    def test_completed_ne_useful_effect(self):
        self.assertEqual(self.observe(fixture("completed"))["transport_state"], "RECORDED_COMPLETED__WORK_UNVERIFIED")

    def test_failed_ne_progress(self):
        self.assertEqual(self.observe(fixture("failed"))["transport_state"], "RECORDED_NON_SUCCESS_RUN")

    def test_cancelled_ne_progress(self):
        self.assertEqual(self.observe(fixture("cancelled"))["recorded_status_class"], "CANCELLED")

    def test_unknown_run_status(self):
        self.assertEqual(self.observe(fixture("ALL_DONE_TRUST_ME"))["transport_state"], "UNKNOWN_RECORDED_STATUS")

    def test_no_run_record(self):
        self.assertEqual(self.observe({"run_details": {"last_run": None}})["transport_state"], "NO_RUN_RECORD_AVAILABLE")

    def test_missing_run_details(self):
        self.assertEqual(self.observe({})["transport_state"], "NO_RUN_DETAIL_AVAILABLE")

    def test_wrong_task_type(self):
        self.assertEqual(self.observe(None)["transport_state"], "INVALID_TASK_METADATA")

    def test_missing_run_identity(self):
        t = fixture()
        del t["run_details"]["last_run"]["id"]
        self.assertEqual(self.observe(t)["transport_state"], "INVALID_RUN_IDENTITY")

    def test_missing_start_time(self):
        t = fixture()
        del t["run_details"]["last_run"]["started_at"]
        self.assertEqual(self.observe(t)["transport_state"], "INVALID_RUN_TIME")

    def test_future_completion(self):
        t = fixture()
        t["run_details"]["last_run"]["completed_at"] = "2026-11-09T00:45:00Z"
        self.assertEqual(self.observe(t)["transport_state"], "CONTRADICTORY_RUN_TIME")

    def test_reversed_clock(self):
        t = fixture()
        t["run_details"]["last_run"]["completed_at"] = "2026-11-09T00:25:00Z"
        self.assertEqual(self.observe(t)["transport_state"], "CONTRADICTORY_RUN_TIME")

    def test_non_utc_clock(self):
        t = fixture()
        t["run_details"]["last_run"]["started_at"] = "2026-11-08T19:27:32-05:00"
        self.assertEqual(self.observe(t)["transport_state"], "INVALID_RUN_TIME")

    def test_fake_work_fields_ignored(self):
        t = fixture()
        t["run_details"]["last_run"].update({
            "verified_useful_effect": True, "source_revision": "fake",
            "eligibility_census_complete": True, "pending_eligible_work": 0,
            "receiver_readback": "fake"})
        self.assertEqual(self.observe(t)["transport_state"], "RECORDED_NO_UPDATE__CAUSE_UNKNOWN")

    def test_chat_ref_not_an_ack(self):
        self.assertIsNone(self.observe(fixture())["receiver_readback"])

    def test_enabled_task_without_run(self):
        self.assertEqual(self.observe({"is_enabled": True, "run_details": {}})["transport_state"], "NO_RUN_RECORD_AVAILABLE")

    def test_pure_repeatable(self):
        t = fixture()
        old = copy.deepcopy(t)
        self.assertEqual(self.observe(t), self.observe(t))
        self.assertEqual(t, old)


if __name__ == "__main__":
    unittest.main()
