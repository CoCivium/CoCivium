"""Negative controls for CoStel cold-open, synthetic only. Never touches Windows."""
import copy
from datetime import datetime, timedelta, timezone
import json
import unittest

from cold_open_readiness import RESULT_SCHEMA, SOURCE_SCHEMA, classify


OBSERVED = datetime(2026, 11, 12, 0, 0, 0, tzinfo=timezone.utc)
NOW = OBSERVED + timedelta(minutes=2)


def fixture():
    return {
        "schema": SOURCE_SCHEMA,
        "state": "READ_ONLY_LOCAL_WINDOWS_SNAPSHOT",
        "observed_at_utc": OBSERVED.isoformat(),
        "boot_time_utc": (OBSERVED - timedelta(minutes=5)).isoformat(),
        "uptime_seconds_at_observation": 300,
        "audio_service_readback": [
            {"service_role": "Audiosrv", "status": "RUNNING"},
            {"service_role": "AudioEndpointBuilder", "status": "RUNNING"},
        ],
        "peripheral_utility_process_candidates": [
            {"process_role": "MOUSE_UTILITY_CANDIDATE", "process_name": "lghub.exe"},
            {"process_role": "LOCAL_MODEL_CANDIDATE", "process_name": "ollama.exe"},
            {"process_role": "COALL_SURFACE_CANDIDATE", "process_name": "coall.exe"},
        ],
        "display_driver_modes": [{"width_px": 2560, "height_px": 1440}],
        "x2_host_observed": False,
        "audio_muted_state": "NOT_OBSERVED",
        "per_monitor_dpi": "NOT_OBSERVED",
        "owned_desktop_background": "NOT_OBSERVED",
        "post_login_restoration_state": "NOT_ATTESTED",
    }


class ColdOpenTests(unittest.TestCase):
    def test_fresh_inventory_is_never_usable_desktop_pass(self):
        r = classify(fixture(), at_utc=NOW)
        self.assertEqual(r["schema"], RESULT_SCHEMA)
        self.assertEqual(r["state"], "HOLD_USABLE_DESKTOP_UNPROVEN")
        self.assertEqual(r["observation_state"], "FRESH_BOOT_INVENTORY_ONLY")
        self.assertTrue(r["snapshot_fresh"])
        self.assertTrue(r["boot_timestamp_qualified"])
        self.assertFalse(r["surface_functional"])
        self.assertEqual(r["post_login_automatic_recovery"], "NOT_ATTESTED")

    def test_audio_services_running_does_not_prove_unmuted(self):
        r = classify(fixture(), at_utc=NOW)
        self.assertEqual(r["audio_services"], "REPORTED_RUNNING")
        self.assertEqual(r["actual_audio_mute_state"], "UNKNOWN")

    def test_mouse_and_coall_processes_never_prove_ux(self):
        r = classify(fixture(), at_utc=NOW)
        self.assertEqual(r["mouse_software"], "PROCESS_CANDIDATE_PRESENT")
        self.assertEqual(r["mouse_mapping_functional"], "UNKNOWN")
        self.assertEqual(r["coall_surface"], "PROCESS_CANDIDATE_PRESENT")
        self.assertFalse(r["surface_functional"])
        self.assertFalse(r["local_model_response_tested"])

    def test_display_mode_is_not_dpi_or_alignment(self):
        r = classify(fixture(), at_utc=NOW)
        self.assertEqual(r["display_driver_mode"], "REPORTED")
        self.assertEqual(r["per_monitor_dpi_and_alignment"], "UNKNOWN")

    def test_stale_inventory_is_not_x2_off(self):
        r = classify(fixture(), at_utc=NOW + timedelta(hours=1))
        self.assertEqual(r["observation_state"], "BOOT_INVENTORY_STALE")
        self.assertEqual(r["next_safe_probe"], "REFRESH_EXISTING_READ_ONLY_INVENTORY_ON_AUTHORIZED_X2")
        self.assertIn("BRIDGE_OFFLINE_NE_HOST_OFF", r["nonclaims"])

    def test_absent_boot_is_held(self):
        q = fixture()
        q["boot_time_utc"] = None
        r = classify(q, at_utc=NOW)
        self.assertEqual(r["observation_state"], "BOOT_INVENTORY_UNQUALIFIED")
        self.assertFalse(r["boot_timestamp_qualified"])

    def test_impossible_future_boot_is_held(self):
        q = fixture()
        q["boot_time_utc"] = (OBSERVED + timedelta(minutes=1)).isoformat()
        r = classify(q, at_utc=NOW)
        self.assertEqual(r["observation_state"], "BOOT_INVENTORY_UNQUALIFIED")

    def test_inconsistent_uptime_is_held(self):
        q = fixture()
        q["uptime_seconds_at_observation"] = -10
        self.assertFalse(classify(q, at_utc=NOW)["boot_timestamp_qualified"])
        q["uptime_seconds_at_observation"] = True
        self.assertFalse(classify(q, at_utc=NOW)["boot_timestamp_qualified"])

    def test_service_or_process_absence_does_not_infer_machine_off(self):
        q = fixture()
        q["audio_service_readback"] = [{"service_role": "Audiosrv", "status": "RUNNING"}]
        q["peripheral_utility_process_candidates"] = []
        q["display_driver_modes"] = []
        r = classify(q, at_utc=NOW)
        self.assertEqual(r["audio_services"], "UNVERIFIED_OR_NOT_RUNNING")
        self.assertEqual(r["mouse_software"], "NOT_ESTABLISHED")
        self.assertEqual(r["display_driver_mode"], "NOT_ESTABLISHED")
        self.assertEqual(r["state"], "HOLD_USABLE_DESKTOP_UNPROVEN")

    def test_invented_pass_flags_in_source_are_never_trusted(self):
        q = fixture()
        q.update({
            "reboot_autostart_success": "PASS",
            "visible_ui_screenshot_accepted": True,
            "post_login_restoration_state": "PASS",
            "audio_muted_state": "UNMUTED",
            "owned_desktop_background": "YES",
        })
        r = classify(q, at_utc=NOW)
        self.assertEqual(r["state"], "HOLD_USABLE_DESKTOP_UNPROVEN")
        self.assertEqual(r["cocivium_owned_desktop_background"], "NOT_ATTESTED")
        self.assertEqual(r["actual_audio_mute_state"], "UNKNOWN")

    def test_private_unrelated_input_is_not_re_emitted(self):
        q = fixture()
        q["raw_command_line"] = "SECRET_PASSWORD_NEVER_ECHO"
        q["user_profile"] = "PRIVATE_PERSONAL_DETAILS_NEVER_ECHO"
        result = json.dumps(classify(q, at_utc=NOW))
        self.assertNotIn("SECRET_PASSWORD", result)
        self.assertNotIn("PRIVATE_PERSONAL", result)
        self.assertNotIn("lghub.exe", result)

    def test_no_mutation_no_hidden_actions(self):
        q = fixture()
        before = copy.deepcopy(q)
        r = classify(q, at_utc=NOW)
        self.assertEqual(q, before)
        self.assertEqual(sum(r["effects"].values()), 0)
        self.assertFalse(r["human_keyboard_action_required_by_this_classifier"])

    def test_wrong_schema_or_state_fails_closed(self):
        q = fixture()
        q["schema"] = "ATTACKER_CLAIMED_PASS"
        with self.assertRaisesRegex(ValueError, "HOLD_UNEXPECTED_SOURCE_SCHEMA"):
            classify(q, at_utc=NOW)
        q = fixture()
        q["state"] = "RUNTIME_PASS"
        with self.assertRaisesRegex(ValueError, "HOLD_UNQUALIFIED_SOURCE_STATE"):
            classify(q, at_utc=NOW)

    def test_naive_now_rejected(self):
        with self.assertRaisesRegex(ValueError, "HOLD_NOW_REQUIRES_TIMEZONE"):
            classify(fixture(), at_utc=datetime(2026, 11, 12))

    def test_deterministic_byte_identical_projections(self):
        a = classify(fixture(), at_utc=NOW)
        b = classify(fixture(), at_utc=NOW)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        self.assertIn("desktop was not verified", a["human_summary"])


if __name__ == "__main__":
    unittest.main()
