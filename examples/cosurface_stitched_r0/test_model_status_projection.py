"""Pure projection guards: current, stale, failed, and fake-currentness."""
import unittest
from datetime import datetime, timezone, timedelta
from model_status_projection import project

NOW = datetime(2026, 11, 8, 19, 0, tzinfo=timezone.utc)
def obs(**changes):
    data = {"schema": "CoLocalModelStatus.R0", "status": "LOCAL_MODEL_INVENTORY_OBSERVED",
            "source": "http://127.0.0.1:11434/api/tags",
            "observed_at_utc": (NOW - timedelta(seconds=5)).isoformat(),
            "model_count": 1, "model_names": ["qwen3:4b"]}
    data.update(changes)
    return data

class ProjectionTest(unittest.TestCase):
    def test_current_healthy_is_behind_drilldown(self):
        result = project(obs(), now_utc=NOW)
        self.assertEqual(result["state"], "LOCAL_MODEL_INVENTORY_OBSERVED")
        self.assertEqual(result["model_count"], 1)
        self.assertFalse(result["show_in_rail"])
        self.assertEqual(result["verified_work_effects"], 0)
        self.assertEqual(result["x2_power_state"], "NOT_INFERRED")

    def test_stale_looks_stale_not_current(self):
        result = project(obs(observed_at_utc=(NOW - timedelta(seconds=120)).isoformat()), now_utc=NOW)
        self.assertEqual(result["state"], "STALE_HOLD")
        self.assertIsNone(result["model_count"])
        self.assertTrue(result["show_in_rail"])

    def test_endpoint_down_does_not_implicate_x2(self):
        result = project(obs(status="OLLAMA_ENDPOINT_UNREACHABLE", model_count=0, model_names=[]),now_utc=NOW)
        self.assertEqual(result["state"], "OLLAMA_ENDPOINT_UNREACHABLE")
        self.assertEqual(result["x2_power_state"], "NOT_INFERRED")

    def test_future_clock_fails_closed(self):
        result = project(obs(observed_at_utc=(NOW+timedelta(minutes=1)).isoformat()),now_utc=NOW)
        self.assertEqual(result["state"], "CLOCK_SKEW_HOLD")

    def test_mismatched_inventory_holds(self):
        self.assertEqual(project(obs(model_count=2),now_utc=NOW)["state"],"INVALID_INVENTORY_HOLD")

    def test_wrong_source_holds(self):
        self.assertEqual(project(obs(source="http://example.com/api/tags"),now_utc=NOW)["state"],"INVALID_SOURCE_HOLD")

    def test_naive_time_holds(self):
        self.assertEqual(project(obs(observed_at_utc="2026-11-08T19:00:00"),now_utc=NOW)["state"],"INVALID_TIME_HOLD")

    def test_bad_reference_rejected(self):
        with self.assertRaisesRegex(ValueError,"UTC_REFERENCE"):
            project(obs(),now_utc=datetime(2026,11,8,19,0))

    def test_inference_never_claimed(self):
        for status in ("LOCAL_MODEL_INVENTORY_OBSERVED", "MALFORMED_RESPONSE_HOLD"):
            data=obs(status=status)
            if status!="LOCAL_MODEL_INVENTORY_OBSERVED":
                data["model_count"]=0
                data["model_names"]=[]
            result=project(data,now_utc=NOW)
            self.assertEqual(result["verified_work_effects"],0)

if __name__=="__main__":
    unittest.main()
