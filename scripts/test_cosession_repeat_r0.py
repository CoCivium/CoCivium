"""Fail-closed duplicate observation checks, synthetic data only."""
import importlib.util
import pathlib
import unittest

SCRIPT=pathlib.Path(__file__).with_name("CoSessionShadowLedger.py")
spec=importlib.util.spec_from_file_location("cosession_shadow",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def obs(sid="synthetic-session", currentness="CURRENT"):
    return {"session_id":sid,"observed_at":"2026-11-09T20:00:00Z",
            "observer":"fixture","work_state":"ACTIVE","evidence_state":"SOURCE_ONLY",
            "authority_ceiling":"NONE","currentness":currentness,
            "source_refs":["fixture:one"]}

class RepeatTests(unittest.TestCase):
    def test_exact_repeat_not_second_session_or_signal(self):
        item=obs()
        report=mod.compile_ledger({"observations":[item,item]},
                                  "fixture", "A"*64)
        self.assertEqual(report["coverage"]["input_observation_count"],2)
        self.assertEqual(report["coverage"]["observation_count"],1)
        self.assertEqual(report["coverage"]["exact_repeat_count"],1)
        self.assertEqual(len(report["sessions"]),1)
        self.assertEqual(len(report["label_signals"]),1)
        self.assertIn("DUPLICATE_SOURCE_INPUT_NE_INDEPENDENT_ACK", report["nonclaims"])
    def test_material_changed_observation_preserved(self):
        report=mod.compile_ledger([obs(),obs(currentness="DEGRADED")],"fixture","B"*64)
        self.assertEqual(report["coverage"]["observation_count"],2)
        self.assertEqual(report["coverage"]["exact_repeat_count"],0)
        self.assertEqual({x["projection"] for x in report["sessions"]},{"ACTIVE","DEGRADED"})
    def test_repeat_does_not_create_effect(self):
        report=mod.compile_ledger([obs(),obs(),obs()],"fixture","C"*64)
        self.assertEqual(report["effects"]["provider_tab_close"],0)
        self.assertEqual(report["effects"]["provider_session_create"],0)
        self.assertEqual(report["effects"]["public_outreach"],0)
    def test_replay_is_deterministic(self):
        x=[obs(),obs(),obs("other")]
        self.assertEqual(mod.compile_ledger(x,"fixture","D"*64),
                         mod.compile_ledger(x,"fixture","D"*64))

if __name__=="__main__":
    unittest.main()
