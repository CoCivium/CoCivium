"""Negative controls for CoForeground R0. Source-only, no child launches."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT=Path(__file__).with_name("coforeground_launch_gate_r0.py")
ROOT=SCRIPT.resolve().parents[1]
spec=importlib.util.spec_from_file_location("coforeground_gate",SCRIPT)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

VISIBLE_SCRIPT="""param([ValidateSet('HOLD','UI','Worker','SelfTest')][string]$Mode = 'HOLD')
if ($Mode -eq 'HOLD') { throw 'HELD_EXPLICIT_MODE_REQUIRED' }
[IO.Directory]::CreateDirectory($root)
Add-Type -AssemblyName System.Windows.Forms
$form = [Windows.Forms.Form]::new()
"""
HEADLESS_SCRIPT="""param()
Set-StrictMode -Version Latest
Write-Output '{"state":"UNKNOWN"}'
"""
def base():
    return {"module_id":"CoThumbCoCopyR1","source":"scripts/CoThumbCoCopyR1.ps1",
     "runtime":"pwsh","visibility":"SURFACE",
     "allowed_triggers":["USER_GESTURE"],
     "qualification":"CANDIDATE_SOURCE_ONLY",
     "launch_args":["-NoProfile","-STA","-File","scripts/CoThumbCoCopyR1.ps1","-Mode","UI"],
     "max_live_instances":1,"restart_policy":"NONE",
     "foreground_ownership":"USER_INVOCATION_ONLY","user_exit":"Close panel"}

def auto():
    e=base()
    e.update({"module_id":"HeadlessRunner1","visibility":"HEADLESS",
       "allowed_triggers":["SCHEDULED"],"qualification":"QUALIFIED_FOR_HOST_TRIAL",
       "launch_args":["-NoProfile","-NonInteractive","-WindowStyle","Hidden","-File",
                      "scripts/CoThumbCoCopyR1.ps1"],"foreground_ownership":"NONE_NEVER_STEAL_FOCUS",
       "restart_policy":"SUPERVISED_BACKOFF","user_exit":"Stop task"})
    return e

class GuardTests(unittest.TestCase):
    def test_real_candidate_manifest_audits(self):
        data=json.loads((ROOT/"ai/coforeground_launch_manifest_r0.json").read_text())
        out=m.inspect_manifest(ROOT,data)
        self.assertEqual(out["state"],"PASS_FOR_SOURCE_POLICY")
        self.assertEqual(out["window_or_process_launches"],0)
        self.assertEqual(out["entries"][0]["foreground_focus_proof"],"UNKNOWN")
    def test_explicit_mode_default_holds(self):
        src=(ROOT/"scripts/CoThumbCoCopyR1.ps1").read_text()
        self.assertIn("[string]$Mode = 'HOLD'",src)
        self.assertIn("HELD_EXPLICIT_MODE_REQUIRED",src)
        self.assertNotIn("[string]$Mode = 'UI'",src)
    def test_visible_manual_can_pass_source_rail(self):
        self.assertEqual(m.audit(base(),VISIBLE_SCRIPT),[])
    def test_scheduled_visible_is_rejected(self):
        e=base();e["allowed_triggers"]=["SCHEDULED"]
        self.assertIn("HELD_AUTOMATED_FOREGROUND_SURFACE",m.audit(e,VISIBLE_SCRIPT))
    def test_recovery_visible_is_rejected(self):
        e=base();e["allowed_triggers"]=["RECOVERY"]
        self.assertIn("HELD_AUTOMATED_FOREGROUND_SURFACE",m.audit(e,VISIBLE_SCRIPT))
    def test_event_visible_is_rejected(self):
        e=base();e["allowed_triggers"]=["EVENT"]
        self.assertIn("HELD_AUTOMATED_FOREGROUND_SURFACE",m.audit(e,VISIBLE_SCRIPT))
    def test_autostart_visible_is_rejected(self):
        e=base();e["allowed_triggers"]=["AUTOSTART"]
        self.assertIn("HELD_AUTOMATED_FOREGROUND_SURFACE",m.audit(e,VISIBLE_SCRIPT))
    def test_headless_powershell_requires_hidden(self):
        e=auto();e["launch_args"]=["-NoProfile","-File","scripts/foo.ps1"]
        self.assertIn("HELD_POWERSHELL_BACKGROUND_CONSOLE_RISK",m.audit(e,HEADLESS_SCRIPT))
    def test_headless_powershell_rejects_visible_gui_source(self):
        self.assertIn("HELD_HEADLESS_GUI_ESCAPE_CANDIDATE",m.audit(auto(),VISIBLE_SCRIPT))
    def test_headless_powershell_rejects_messagebox(self):
        self.assertIn("HELD_HEADLESS_GUI_ESCAPE_CANDIDATE",
                      m.audit(auto(),"[System.Windows.Forms.MessageBox]::Show('popup')"))
    def test_headless_powershell_rejects_out_grid_view(self):
        self.assertIn("HELD_HEADLESS_GUI_ESCAPE_CANDIDATE",m.audit(auto(),"Get-Process | Out-GridView"))
    def test_headless_powershell_rejects_spawn_normal(self):
        self.assertIn("HELD_HEADLESS_GUI_ESCAPE_CANDIDATE",
                      m.audit(auto(),"Start-Process pwsh.exe -WindowStyle Normal"))
    def test_unsafe_noexit_is_rejected(self):
        e=auto();e["launch_args"]+=["-NoExit"]
        self.assertIn("HELD_DYNAMIC_OR_PERSISTENT_CONSOLE",m.audit(e,HEADLESS_SCRIPT))
    def test_headless_source_can_pass_static_gate_not_runtime(self):
        self.assertEqual(m.audit(auto(),HEADLESS_SCRIPT),[])
    def test_automated_flags_after_file_are_not_host_flags(self):
        e=auto()
        e["launch_args"]=["-File","scripts/worker.ps1","-NoProfile","-NonInteractive","-WindowStyle","Hidden"]
        self.assertIn("HELD_POWERSHELL_SWITCH_ORDER_UNTRUSTED",m.audit(e,HEADLESS_SCRIPT))
    def test_automated_windowstyle_must_bind_hidden_value(self):
        e=auto()
        e["launch_args"]=["-NoProfile","-NonInteractive","-WindowStyle","Normal",
                          "-File","scripts/worker.ps1","Hidden"]
        self.assertIn("HELD_POWERSHELL_SWITCH_ORDER_UNTRUSTED",m.audit(e,HEADLESS_SCRIPT))
    def test_automated_duplicate_windowstyle_conflict_is_held(self):
        e=auto()
        e["launch_args"]=["-NoProfile","-NonInteractive","-WindowStyle","Hidden",
                          "-WindowStyle","Normal","-File","scripts/worker.ps1"]
        self.assertIn("HELD_POWERSHELL_SWITCH_ORDER_UNTRUSTED",m.audit(e,HEADLESS_SCRIPT))
    def test_automated_executionpolicy_bypass_is_held(self):
        e=auto()
        e["launch_args"]=["-NoProfile","-NonInteractive","-WindowStyle","Hidden",
                          "-ExecutionPolicy","Bypass","-File","scripts/worker.ps1"]
        self.assertIn("HELD_UNREVIEWED_EXECUTION_POLICY_BYPASS",m.audit(e,HEADLESS_SCRIPT))
    def test_automated_executionpolicy_ep_alias_is_held(self):
        e=auto()
        e["launch_args"]=["-NoProfile","-NonInteractive","-WindowStyle","Hidden",
                          "-ep","Bypass","-File","scripts/worker.ps1"]
        self.assertIn("HELD_UNREVIEWED_EXECUTION_POLICY_BYPASS",m.audit(e,HEADLESS_SCRIPT))
    def test_good_headless_flag_order_is_still_admissible_as_source(self):
        self.assertEqual(m.audit(auto(),HEADLESS_SCRIPT),[])
    def test_candidate_cannot_autostart_even_when_hidden(self):
        e=auto();e["qualification"]="CANDIDATE_SOURCE_ONLY"
        self.assertIn("HELD_AUTOSTART_OF_CANDIDATE",m.audit(e,HEADLESS_SCRIPT))
    def test_python_console_auto_is_rejected(self):
        e=auto();e["runtime"]="python"
        self.assertIn("HELD_PYTHON_CONSOLE_BACKGROUND_RISK",m.audit(e,HEADLESS_SCRIPT))
    def test_missing_owner_and_exit_hold(self):
        e=base();e["foreground_ownership"]="UNKNOWN";e["user_exit"]=""
        holds=m.audit(e,VISIBLE_SCRIPT)
        self.assertIn("HELD_FOREGROUND_OWNER_UNVERIFIED",holds)
        self.assertIn("HELD_NO_USER_EXIT",holds)
    def test_non_single_runner_hold(self):
        e=auto();e["max_live_instances"]=3
        self.assertIn("HELD_NOT_SINGLE_ELECTED_RUNNER",m.audit(e,HEADLESS_SCRIPT))
    def test_ui_default_reversion_detected(self):
        self.assertIn("HELD_UI_SCRIPT_DEFAULTS_VISIBLE",
                      m.audit(base(),VISIBLE_SCRIPT.replace("$Mode = 'HOLD'","$Mode = 'UI'")))
    def test_ui_guard_after_side_effect_detected(self):
        s=VISIBLE_SCRIPT.replace("if ($Mode -eq 'HOLD') { throw 'HELD_EXPLICIT_MODE_REQUIRED' }","")
        s+="\nthrow 'HELD_EXPLICIT_MODE_REQUIRED'\n"
        self.assertIn("HELD_MODE_GUARD_AFTER_EFFECT",m.audit(base(),s))
    def test_ui_no_mode_flag_rejected(self):
        e=base();e["launch_args"]=["-File","scripts/CoThumbCoCopyR1.ps1"]
        self.assertIn("HELD_UI_MODE_NOT_EXPLICIT",m.audit(e,VISIBLE_SCRIPT))
    def test_source_path_escape_rejected(self):
        with self.assertRaisesRegex(ValueError,"HELD_SOURCE_PATH_UNSAFE"):
            m.source_file(ROOT,"scripts/../AGENTS.md")
        with self.assertRaisesRegex(ValueError,"HELD_SOURCE_OUTSIDE_SCRIPTS"):
            m.source_file(ROOT,"C:/Windows/System32/pwsh.exe")
    def test_unregistered_blank_manifest_cannot_green(self):
        self.assertEqual(m.inspect_manifest(ROOT,{"schema":m.SCHEMA,"entries":[]})["state"],"HOLD")
    def test_duplicate_manifest_id_cannot_green(self):
        e=base();data={"schema":m.SCHEMA,"entries":[e,e]}
        out=m.inspect_manifest(ROOT,data)
        self.assertEqual(out["state"],"HOLD")
        self.assertIn("HELD_DUPLICATE_MODULE_ID",out["entries"][1]["holds"])
    def test_unknown_entry_cannot_green(self):
        e=base();e["source"]="scripts/nonexistent-do-not-create.ps1"
        out=m.inspect_manifest(ROOT,{"schema":m.SCHEMA,"entries":[e]})
        self.assertEqual(out["state"],"HOLD")
    def test_retroactive_lineage_links_existing_source_not_new_canon(self):
        text=(ROOT/"docs/Architecture/COFRONT_RETRO_ECHO_NO_ORPHANS_R0_20261109.md").read_text(encoding="utf-8")
        for relation in ("CoResourceFlow_PressureField_20261012_R0.json",
                         "CoX2_ForegroundPressure_Observation_20261016_R0.json",
                         "CoCivium/issues/181",
                         "scripts/coforeground_launch_gate_r0.py",
                         "## Bounded CoEcho example | X2 foreground interruption"):
            self.assertIn(relation,text)
    def test_retro_echo_preserves_uncertainty_and_private_holds(self):
        text=(ROOT/"docs/Architecture/COFRONT_RETRO_ECHO_NO_ORPHANS_R0_20261109.md").read_text(encoding="utf-8")
        for contract in ("ORPHAN_RISK", "**not** a complete reconstruction",
                         "**does not** retroactively establish",
                         "not private conversation ingestion"):
            self.assertIn(contract.lower(),text.lower())
    def test_never_launches_from_source(self):
        content=SCRIPT.read_text()
        for token in ("subprocess.run(","subprocess.Popen(","os.system(","os.startfile(","os.execv("):
            self.assertNotIn(token,content)

if __name__=="__main__":
    unittest.main()
