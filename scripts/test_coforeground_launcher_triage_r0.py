"""No-device negative controls for a future X2 launcher snapshot. Never starts powershell."""
import copy
import datetime as dt
import importlib.util
import json
import unittest
from pathlib import Path

SCRIPT=Path(__file__).with_name("coforeground_launcher_triage_r0.py")
spec=importlib.util.spec_from_file_location("coforeground_launcher_triage_r0",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
UTC=dt.timezone.utc
NOW=dt.datetime(2026,11,10,17,5,0,tzinfo=UTC)

def record(name,state="Ready",kind="POWERSHELL",automated=True,
           windowstyle_hidden=False,noninteractive=False,ui_mode=False):
    return {"task_name":name,"state":state,"kind":kind,"automated":automated,
            "windowstyle_hidden":windowstyle_hidden,"noninteractive":noninteractive,
            "ui_mode":ui_mode,"action_sha256":"a"*64}

def fixture():
    return {"schema":m.SCHEMA,"scope":"SYNTHETIC_CI_ONLY",
            "coverage":"BOUNDED_MATCHING_LAUNCHERS_ONLY",
            "observed_at_utc":"2026-11-10T17:00:00Z",
            "tasks":[
                record("CoCiviumExeDevMuleResidentTick1Min"),
                record("CoPing_CopyBlock_InboxProcessor_1min_V05",windowstyle_hidden=True,noninteractive=True),
                record("CoEyesStructuralReview10Min",state="Disabled"),
                record("CoCiviumExeProductShellWatchdog5Min",state="Disabled"),
            ]}

class LauncherTriageTests(unittest.TestCase):
    def run_snapshot(self, value=None,now=NOW):
        return m.inspect(value if value is not None else fixture(),now=now)
    def assert_held(self, changed,code):
        with self.assertRaisesRegex(m.Held,code):
            self.run_snapshot(changed)
    def test_synthetic_never_promotes_host_proof(self):
        r=self.run_snapshot()
        self.assertEqual(r["state"],"SYNTHETIC_POLICY_CHECK_ONLY")
        self.assertEqual(r["popup_cause"],"UNIDENTIFIED")
        self.assertEqual(r["local_execution_effects"],0)
        self.assertFalse(r["complete_inventory"])
        self.assertEqual(r["processes_terminated"],0)
        self.assertFalse(r["task_settings_changed"])
        self.assertFalse(r["restart_triggered"])
    def test_real_known_mule_role_preserved(self):
        r=self.run_snapshot()
        self.assertEqual(r["findings"][0]["function_to_preserve"],"LOCAL_DEV_MULE_HEALTH")
        self.assertEqual(r["findings"][0]["risk"],"P1_AUTOMATED_PS7_CONSOLE_RISK")
        self.assertEqual(r["findings"][0]["next_effect"],"NONE_READ_ONLY_CLASSIFICATION")
    def test_known_copyblock_role_preserved(self):
        r=self.run_snapshot()
        self.assertEqual(r["findings"][1]["function_to_preserve"],"LOCAL_COPYBLOCK_INBOX")
        self.assertEqual(r["findings"][1]["risk"],"HEADLESS_FLAGS_PRESENT_FOCUS_UNVERIFIED")
    def test_disabled_watchdog_does_not_get_reactivated(self):
        r=self.run_snapshot()
        self.assertEqual(r["findings"][3]["risk"],"DISABLED_AS_OBSERVED_NOT_CURRENTNESS")
        self.assertEqual(r["findings"][3]["function_to_preserve"],"LEGACY_PRODUCT_SHELL_WATCH")
    def test_scheduled_ui_ranks_above_console_risk(self):
        x=fixture()
        x["tasks"].append(record("CoThumbUIAuto",ui_mode=True))
        self.assertEqual(self.run_snapshot(x)["findings"][-1]["risk"],"P0_AUTOMATED_VISIBLE_UI_RISK")
    def test_manual_ui_not_scheduled_risk(self):
        x=fixture();x["tasks"].append(record("ManualUIOnly",automated=False,ui_mode=True))
        self.assertEqual(self.run_snapshot(x)["findings"][-1]["risk"],"NO_RISK_IN_DECLARED_FLAGS_NOT_REAL_HOST_PASS")
    def test_nonpowershell_automatic_not_inferred_as_console(self):
        x=fixture();x["tasks"].append(record("OpaqueNativeRunner",kind="NATIVE"))
        self.assertEqual(self.run_snapshot(x)["findings"][-1]["risk"],"NO_RISK_IN_DECLARED_FLAGS_NOT_REAL_HOST_PASS")
    def test_unknown_action_held(self):
        x=fixture();x["tasks"].append(record("Unresolved",kind="UNKNOWN"))
        self.assertEqual(self.run_snapshot(x)["findings"][-1]["risk"],"HOLD_UNRESOLVED_LAUNCHER")
    def test_stale_snapshot_cannot_be_current(self):
        r=self.run_snapshot(now=NOW+dt.timedelta(days=4))
        self.assertFalse(r["host_snapshot_fresh"])
        self.assertEqual(r["popup_cause"],"UNIDENTIFIED")
    def test_freshness_is_not_live_focus_proof(self):
        r=self.run_snapshot()
        self.assertTrue(r["host_snapshot_fresh"])
        self.assertIn("SOURCE_INVENTORY_NE_LIVE_FOREGROUND_ATTRIBUTION",r["nonclaims"])
    def test_future_observation_holds(self):
        x=fixture();x["observed_at_utc"]="2026-11-10T18:00:00Z"
        self.assert_held(x,"HELD_FUTURE_OBSERVATION")
    def test_invalid_schema_holds(self):
        x=fixture();x["schema"]="AUTONOMOUS_X2_GOOD"
        self.assert_held(x,"HELD_INVALID_SCHEMA")
    def test_unknown_scope_holds(self):
        x=fixture();x["scope"]="COEX"
        self.assert_held(x,"HELD_UNKNOWN_OBSERVATION_SCOPE")
    def test_false_total_coverage_holds(self):
        x=fixture();x["coverage"]="ALL_PROCESSES_PROVEN"
        self.assert_held(x,"HELD_FALSE_COMPLETE_COVERAGE")
    def test_missing_time_holds(self):
        x=fixture();x["observed_at_utc"]="unknown"
        self.assert_held(x,"HELD_UNKNOWN_OBSERVATION_TIME")
    def test_duplicate_task_id_holds(self):
        x=fixture();x["tasks"].append(copy.deepcopy(x["tasks"][0]))
        self.assert_held(x,"HELD_DUPLICATE_TASK_ID")
    def test_casefold_duplicate_holds(self):
        x=fixture();a=copy.deepcopy(x["tasks"][0]);a["task_name"]=a["task_name"].upper();x["tasks"].append(a)
        self.assert_held(x,"HELD_DUPLICATE_TASK_ID")
    def test_undeclared_fields_hold(self):
        x=fixture();x["tasks"][0]["user"]="Owner"
        self.assert_held(x,"HELD_UNDECLARED_TASK_FIELDS")
    def test_boolean_strings_cannot_circumvent(self):
        x=fixture();x["tasks"][0]["windowstyle_hidden"]="true"
        self.assert_held(x,"HELD_INVALID_BOOLEAN_FLAGS")
    def test_action_sha_must_be_digest(self):
        x=fixture();x["tasks"][0]["action_sha256"]="looks-clean"
        self.assert_held(x,"HELD_UNVERIFIABLE_ACTION_FINGERPRINT")
    def test_unknown_task_state_is_not_true(self):
        x=fixture();x["tasks"][0]["state"]="ProvenDisabled"
        self.assert_held(x,"HELD_UNKNOWN_STATE_OR_KIND")
    def test_missing_collection_is_not_proof(self):
        x=fixture();del x["tasks"]
        self.assert_held(x,"HELD_INVALID_TASK_COLLECTION")
    def test_empty_collection_reports_bounded_empty_not_everything_good(self):
        x=fixture();x["tasks"]=[]
        r=self.run_snapshot(x)
        self.assertEqual(r["count"],0)
        self.assertFalse(r["complete_inventory"])
    def test_malformed_task_rejected(self):
        x=fixture();x["tasks"].append("text")
        self.assert_held(x,"HELD_UNDECLARED_TASK_FIELDS")
    def test_quiet_boot_preserves_all_known_legacy_functions(self):
        note=(SCRIPT.parents[1]/"docs/Architecture/COFOREGROUND_QUIET_BOOT_FUNCTION_SALVAGE_R0_20261110.md").read_text(encoding="utf-8")
        for name in m.KNOWN_FUNCTIONS:
            self.assertIn(name,note)
        self.assertIn("not current installation truth",note.lower())
        self.assertIn("SOURCE-ONLY",note)
    def test_no_remote_scheduler_as_single_point_of_failure(self):
        note=(SCRIPT.parents[1]/"docs/Architecture/COFOREGROUND_QUIET_BOOT_FUNCTION_SALVAGE_R0_20261110.md").read_text(encoding="utf-8")
        self.assertIn("sole clock",note)
        self.assertIn("sole store",note)
        self.assertIn("sole actuator",note)
        self.assertIn("No X2 task, process, registry, service, DNS or scheduler was modified",note)
    def test_never_use_remote_scheduler_as_runtime(self):
        code=SCRIPT.read_text(encoding="utf-8")
        for unsafe in ("subprocess", "os.system", "Stop-Process", "Disable-ScheduledTask",
                       "Register-ScheduledTask", "Restart-Computer", "requests.get", "urllib.request"):
            self.assertNotIn(unsafe,code)
        self.assertIn("CLOUD_CI_NE_LOCAL_BOOTDEPENDENCY",code)

if __name__=="__main__":
    unittest.main()
