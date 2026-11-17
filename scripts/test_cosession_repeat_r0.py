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

class DeathAnytimeSourceSafetyTests(unittest.TestCase):
    """Manual sessions have no predictable end; labels are source assertions only."""

    def row(self, **changes):
        item = obs()
        item.update(changes)
        return mod.compile_ledger([item], "fixture:death-anytime", "F"*64)["sessions"][0]

    def test_recovery_required_overrides_claimed_close_safe(self):
        row = self.row(projection="CLOSE_SAFE", recovery_required=True, tab_close_safe=True)
        self.assertEqual(row["projection"], "RECOVERY")
        self.assertEqual(row["close_safety"], "HELD_RECOVERY_OR_STALE")
        self.assertNotIn(".close-ok", row["candidate_label"])

    def test_stale_currentness_overrides_explicit_close_safe(self):
        row = self.row(projection="CLOSE_SAFE", currentness="STALE", tab_close_safe=True)
        self.assertEqual(row["projection"], "DEGRADED")
        self.assertEqual(row["close_safety"], "HELD_RECOVERY_OR_STALE")

    def test_unknown_stale_overrides_successor_ready(self):
        row = self.row(projection="SUCCESSOR_READY", currentness="UNKNOWN_STALE")
        self.assertEqual(row["projection"], "DEGRADED")

    def test_unqualified_currentness_cannot_claim_close_safe(self):
        row = self.row(projection="CLOSE_SAFE", currentness="NOT_OBSERVED")
        self.assertEqual(row["projection"], "DEGRADED")
        self.assertEqual(row["projection_basis"], "CURRENTNESS_UNQUALIFIED_FOR_CLOSE_OR_SUCCESSION")

    def test_unqualified_currentness_cannot_claim_successor_ready(self):
        row = self.row(projection="SUCCESSOR_READY", currentness="UNVERIFIED")
        self.assertEqual(row["projection"], "DEGRADED")

    def test_supersession_overrides_old_close_safe_projection(self):
        row = self.row(projection="CLOSE_SAFE", superseded=True)
        self.assertEqual(row["projection"], "SUPERSEDED")

    def test_close_safe_boolean_cannot_override_recovery(self):
        row = self.row(tab_close_safe=True, recovery_required=True)
        self.assertEqual(row["projection"], "RECOVERY")
        self.assertEqual(row["close_safety"], "HELD_RECOVERY_OR_STALE")

    def test_claimed_prior_proven_true_is_held_when_stale(self):
        row = self.row(close_safety="PROVEN_TRUE", currentness="DEGRADED")
        self.assertEqual(row["projection"], "DEGRADED")
        self.assertEqual(row["close_safety"], "HELD_RECOVERY_OR_STALE")

    def test_fresh_explicit_projection_not_reclassified(self):
        row = self.row(projection="ACTIVE", currentness="CURRENT")
        self.assertEqual(row["projection"], "ACTIVE")
        self.assertEqual(row["projection_basis"], "EXPLICIT_SOURCE_PROJECTION")

    def test_malformed_explicit_projection_does_not_crash_guard(self):
        row = self.row(projection={"unsupported": True})
        self.assertEqual(row["projection"], "ACTIVE")

    def test_repeating_stale_close_claim_is_not_second_ack(self):
        item = obs(currentness="STALE")
        item.update(projection="CLOSE_SAFE", tab_close_safe=True)
        report = mod.compile_ledger([item, item], "fixture", "F"*64)
        self.assertEqual(report["coverage"]["exact_repeat_count"], 1)
        self.assertEqual(len(report["sessions"]), 1)
        self.assertEqual(report["sessions"][0]["projection"], "DEGRADED")
        self.assertEqual(report["effects"]["provider_tab_close"], 0)
        self.assertIn("STALE_OR_RECOVERY_NE_CLOSE_SAFE", report["sessions"][0]["nonclaims"])

if __name__=="__main__":
    unittest.main()
