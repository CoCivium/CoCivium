"""Synthetic negative controls for bridge-independent CoStel postboot evidence."""
import copy
import json
import unittest
from datetime import datetime, timedelta, timezone

from bridge_recovery_cohort_r0 import INPUT_SCHEMA, OUTPUT_SCHEMA, classify

OBSERVED = datetime(2026, 11, 19, 21, 32, tzinfo=timezone.utc)
NOW = OBSERVED + timedelta(minutes=1)
BOOT = OBSERVED - timedelta(hours=22)


def fixture():
    return {
        "schema": INPUT_SCHEMA,
        "observed_at_utc": OBSERVED.isoformat(),
        "boot_time_utc": BOOT.isoformat(),
        "local_observation": {"kind": "USER_RETURNED_PS7", "read_only": True},
        "task": {"registered": True, "runner_matches_pin": True,
                 "state": "READY", "last_result": 0, "last_run_utc": None},
        "routes": [{"adapter": "DESKTOP_COMMANDER", "state": "OFFLINE",
                    "observed_at_utc": OBSERVED.isoformat()}],
    }


class BridgeRecoveryCohortTests(unittest.TestCase):
    def report(self, data=None, now=NOW):
        return classify(fixture() if data is None else data, at_utc=now)

    def test_ps7_observed_remote_offline_without_host_off_inference(self):
        x = self.report()
        self.assertEqual(x["schema"], OUTPUT_SCHEMA)
        self.assertTrue(x["local_host_observed"])
        self.assertEqual(x["bridge_independence_observation"],
                         "LOCAL_HOST_OBSERVED_WHILE_REMOTE_BRIDGE_OFFLINE")
        self.assertIn("BRIDGE_OFFLINE_NE_HOST_OFF", x["nonclaims"])

    def test_ready_and_last_exit_zero_not_postboot_proof(self):
        x = self.report()
        self.assertTrue(x["task_registration_reported"])
        self.assertTrue(x["task_last_result_zero_reported"])
        self.assertEqual(x["postboot_task_state"], "HOLD_POSTBOOT_EXECUTION_NOT_PROVEN")
        self.assertEqual(x["state"], "HOLD_AUTONOMOUS_WALKAWAY_NOT_PROVEN")

    def test_missing_run_timestamp_has_one_next_safe_probe(self):
        x = self.report()
        self.assertEqual(x["last_run_time_state"], "NOT_REPORTED")
        self.assertEqual(x["next_safe_probe"],
                         "READ_NATIVE_LAST_RUN_UTC_AND_MATCH_R20_RECEIPT_TO_BOOT_COHORT")

    def test_task_run_before_boot_not_accepted(self):
        x = fixture()
        x["task"]["last_run_utc"] = (BOOT - timedelta(minutes=5)).isoformat()
        self.assertEqual(self.report(x)["last_run_time_state"], "NOT_AFTER_REPORTED_BOOT")

    def test_task_run_at_boot_not_accepted(self):
        x = fixture()
        x["task"]["last_run_utc"] = BOOT.isoformat()
        self.assertEqual(self.report(x)["last_run_time_state"], "NOT_AFTER_REPORTED_BOOT")

    def test_reported_run_after_boot_is_not_useful_effect(self):
        x = fixture()
        x["task"]["last_run_utc"] = (BOOT + timedelta(minutes=3)).isoformat()
        r = self.report(x)
        self.assertEqual(r["postboot_task_state"],
                         "REPORTED_TASK_RUN_AFTER_BOOT_NOT_EFFECT_PROOF")
        self.assertEqual(r["state"], "HOLD_AUTONOMOUS_WALKAWAY_NOT_PROVEN")
        self.assertEqual(r["new_work_autonomous_intake"], "NOT_TESTED")

    def test_run_after_observation_conflicts(self):
        x = fixture()
        x["task"]["last_run_utc"] = (OBSERVED + timedelta(seconds=12)).isoformat()
        self.assertEqual(self.report(x)["last_run_time_state"], "CONFLICTING_FUTURE_TIMESTAMP")

    def test_no_observed_boot_cohort_holds(self):
        x = fixture()
        x["boot_time_utc"] = None
        r = self.report(x)
        self.assertFalse(r["local_host_observed"])
        self.assertEqual(r["postboot_task_state"], "HOLD_LOCAL_BOOT_COHORT_UNQUALIFIED")

    def test_boot_after_observation_holds(self):
        x = fixture()
        x["boot_time_utc"] = (OBSERVED + timedelta(minutes=1)).isoformat()
        self.assertEqual(self.report(x)["cohort"], "BOOT_COHORT_UNQUALIFIED")

    def test_stale_local_snapshot_cannot_claim_live_host(self):
        r = self.report(now=NOW + timedelta(hours=2))
        self.assertFalse(r["local_host_observed"])
        self.assertEqual(r["desktop_commander_adapter"], "STALE_UNQUALIFIED")

    def test_future_route_observation_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "HOLD_UNQUALIFIED_ROUTE_TIME"):
            self.report(now=OBSERVED-timedelta(seconds=1))

    def test_task_wrong_pin_holds(self):
        x = fixture()
        x["task"]["runner_matches_pin"] = False
        r = self.report(x)
        self.assertFalse(r["task_registration_reported"])
        self.assertEqual(r["postboot_task_state"], "HOLD_TASK_OWNER_OR_SOURCE_NOT_BOUND")

    def test_invalid_task_last_exit_bool_rejected(self):
        x = fixture()
        x["task"]["last_result"] = True
        with self.assertRaisesRegex(ValueError, "HOLD_TASK_EXIT_MALFORMED"):
            self.report(x)

    def test_bad_task_state_rejected(self):
        x = fixture()
        x["task"]["state"] = "PASS_REAL_REBOOT"
        with self.assertRaisesRegex(ValueError, "HOLD_TASK_STATE_MALFORMED"):
            self.report(x)

    def test_remote_route_online_still_not_host_acceptance(self):
        x = fixture()
        x["routes"][0]["state"] = "ONLINE"
        r = self.report(x)
        self.assertEqual(r["desktop_commander_adapter"], "ONLINE")
        self.assertEqual(r["state"], "HOLD_AUTONOMOUS_WALKAWAY_NOT_PROVEN")

    def test_multiple_claimed_adapters_not_independence(self):
        x = fixture()
        x["routes"].extend([
            {"adapter": "COSTEAD_NATIVE_RECEIVER", "state": "ONLINE", "observed_at_utc": OBSERVED.isoformat()},
            {"adapter": "COPING_TRUSTED_DROP", "state": "ONLINE", "observed_at_utc": OBSERVED.isoformat()},
        ])
        r = self.report(x)
        self.assertEqual(r["claimed_route_adapters_observed"], 3)
        self.assertEqual(r["authenticated_independent_failure_domains"], "NOT_VERIFIED")

    def test_duplicate_remote_observations_do_not_multiply(self):
        x = fixture()
        x["routes"].append(copy.deepcopy(x["routes"][0]))
        self.assertEqual(self.report(x)["claimed_route_adapters_observed"], 1)

    def test_contradictory_same_time_state_holds(self):
        x = fixture()
        x["routes"].append({"adapter": "DESKTOP_COMMANDER", "state": "ONLINE",
                            "observed_at_utc": OBSERVED.isoformat()})
        with self.assertRaisesRegex(ValueError, "HOLD_CONFLICTING_SAME_TIME_ROUTE"):
            self.report(x)

    def test_stale_route_not_counted_as_live(self):
        x = fixture()
        x["routes"][0]["observed_at_utc"] = (OBSERVED - timedelta(hours=3)).isoformat()
        self.assertEqual(self.report(x)["desktop_commander_adapter"], "STALE_UNQUALIFIED")

    def test_unknown_route_id_rejected(self):
        x = fixture()
        x["routes"][0]["adapter"] = "CLOUD_REMOTE_SHELL_OVERRIDE"
        with self.assertRaisesRegex(ValueError, "HOLD_UNKNOWN_ROUTE_OR_STATE"):
            self.report(x)

    def test_route_input_budget(self):
        x = fixture()
        x["routes"] = x["routes"] * 13
        with self.assertRaisesRegex(ValueError, "HOLD_ROUTE_COUNT_OR_TYPE"):
            self.report(x)

    def test_malicious_private_metadata_never_emitted(self):
        x = fixture()
        x["private_commandline"] = "SENSITIVE_SECRET_TOKEN_NEVER_EMIT"
        x["local_observation"]["user_name"] = "PRIVATE_USER_NEVER_EMIT"
        x["routes"][0]["process_command"] = "LOCAL_MACHINE_PATH_NEVER_EMIT"
        r = json.dumps(self.report(x))
        self.assertNotIn("NEVER_EMIT", r)
        self.assertNotIn("PRIVATE", r)

    def test_claimed_acceptance_flags_ignored(self):
        x = fixture()
        x["R20_reboot_confirmed"] = True
        x["independent_roots"] = 100
        x["task"]["real_reboot_verified"] = "PASS"
        x["local_observation"]["authority_granted"] = True
        r = self.report(x)
        self.assertEqual(r["state"], "HOLD_AUTONOMOUS_WALKAWAY_NOT_PROVEN")
        self.assertEqual(r["authenticated_independent_failure_domains"], "NOT_VERIFIED")

    def test_deterministic_no_mutation_no_effects(self):
        x = fixture()
        before = copy.deepcopy(x)
        a, b = self.report(x), self.report(x)
        self.assertEqual(x, before)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        self.assertEqual(sum(a["effects"].values()), 0)

    def test_missing_root_schema_rejected(self):
        x = fixture()
        x["schema"] = "ATTACKER_V2"
        with self.assertRaisesRegex(ValueError, "HOLD_SOURCE_SCHEMA"):
            self.report(x)

    def test_naive_time_rejected(self):
        with self.assertRaisesRegex(ValueError, "HOLD_NOW_MUST_BE_AWARE"):
            self.report(now=datetime(2026, 11, 19, 22))

    def test_no_remote_and_no_local_never_proves_offline_host(self):
        x = fixture()
        x["local_observation"] = {"kind": "NONE", "read_only": True}
        x["routes"] = []
        r = self.report(x)
        self.assertEqual(r["bridge_independence_observation"],
                         "HOST_LIVENESS_NOT_QUALIFIED_BY_THIS_SNAPSHOT")
        self.assertFalse(r["local_host_observed"])


if __name__ == "__main__":
    unittest.main()
