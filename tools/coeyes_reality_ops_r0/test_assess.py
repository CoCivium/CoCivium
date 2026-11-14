"""No-actuation adversarial checks for CoEyes source truth and popup opportunity."""
import copy
import unittest
from assess import assess, at

NOW = "2026-11-08T12:50:00Z"
SHA = "f" * 64

def fixture():
    return {
        "schema": "CoAll.CoEyes.RealityAndOpportunity.R0.SYNTHETIC",
        "as_of": NOW,
        "remote_route": "OFFLINE",
        "surface": {
            "visual": {"kind": "STATIC_WALLPAPER", "observer_id": "human-report", "observed_at": NOW},
        },
        "events": [],
    }

def proc():
    return {"present": True, "process_id": 1234, "observer_id": "os-process", "observed_at": NOW}

def response():
    return {"ok": True, "process_id": 1234, "challenge_id": "challenge-01",
            "source_sha256": SHA, "observer_id": "app-reply", "observed_at": NOW}

def receiver():
    return {"challenge_id": "challenge-01", "source_sha256": SHA,
            "observer_id": "separate-reader", "observed_at": NOW}

def effect():
    return {"challenge_id": "challenge-01", "source_sha256": SHA,
            "effect_class": "BOUNDED_TEST_DELTA", "observer_id": "effect-reader", "observed_at": NOW}

def event(i, when, owner="", source="USER_REPORT", ownership="UNKNOWN"):
    return {"event_id": "event-" + str(i), "kind": "FOREGROUND_CONSOLE_INTRUSION",
            "source_type": source, "owner_ref": owner, "ownership": ownership,
            "observed_at": when}

class RealityChecks(unittest.TestCase):
    def setUp(self):
        self.x = fixture()
    def runstate(self):
        return assess(self.x)["surface"]["state"]
    def test_static_cobar_label_not_live(self):
        self.assertEqual(self.runstate(), "APPEARANCE_ONLY")
        self.assertEqual(assess(self.x)["surface"]["appearance"], "STATIC_ARTWORK")
    def test_video_motion_not_live(self):
        self.x["surface"]["visual"]["kind"] = "VIDEO_OR_ANIMATION"
        self.x["surface"]["visual"]["motion"] = True
        self.assertEqual(self.runstate(), "APPEARANCE_ONLY")
        self.assertEqual(assess(self.x)["surface"]["appearance"], "MOTION_DEPICTED_NOT_LIVENESS")
    def test_window_view_not_live(self):
        self.x["surface"]["visual"]["kind"] = "WINDOW_VIEW"
        self.assertEqual(self.runstate(), "APPEARANCE_ONLY")
    def test_process_alone_not_responsive(self):
        self.x["surface"]["process"] = proc()
        self.assertEqual(self.runstate(), "PROCESS_PRESENT_UNPROVEN_RESPONSIVE")
    def test_missing_process_in_complete_scope(self):
        self.x["surface"]["process"] = dict(proc(), present=False, coverage="COMPLETE_FOR_DECLARED_SCOPE")
        self.assertEqual(self.runstate(), "PROCESS_NOT_FOUND_IN_SCOPE")
    def test_missing_process_with_incomplete_scope(self):
        self.x["surface"]["process"] = dict(proc(), present=False, coverage="PARTIAL")
        self.assertEqual(self.runstate(), "UNKNOWN")
    def test_response_correlated_to_process(self):
        self.x["surface"]["process"] = proc()
        self.x["surface"]["response"] = response()
        self.assertEqual(self.runstate(), "RESPONSIVE_FOR_DECLARED_SCOPE")
    def test_response_mismatched_pid_does_not_promote(self):
        self.x["surface"]["process"] = proc()
        self.x["surface"]["response"] = dict(response(), process_id=9876)
        self.assertEqual(self.runstate(), "PROCESS_PRESENT_UNPROVEN_RESPONSIVE")
    def test_response_missing_challenge_does_not_promote(self):
        self.x["surface"]["process"] = proc()
        self.x["surface"]["response"] = dict(response(), challenge_id="")
        self.assertEqual(self.runstate(), "PROCESS_PRESENT_UNPROVEN_RESPONSIVE")
    def test_response_without_sha_does_not_promote(self):
        self.x["surface"]["process"] = proc()
        self.x["surface"]["response"] = dict(response(), source_sha256="not-a-sha")
        self.assertEqual(self.runstate(), "PROCESS_PRESENT_UNPROVEN_RESPONSIVE")
    def test_receiver_with_different_observer_promotes_bounded(self):
        self.x["surface"].update(process=proc(), response=response(), receiver=receiver())
        self.assertEqual(self.runstate(), "RECEIVER_READBACK_CONSISTENT")
    def test_same_observer_receiver_not_independent(self):
        self.x["surface"].update(process=proc(), response=response(), receiver=dict(receiver(), observer_id="app-reply"))
        self.assertEqual(self.runstate(), "RESPONSIVE_FOR_DECLARED_SCOPE")
    def test_receiver_with_wrong_source_not_admitted(self):
        self.x["surface"].update(process=proc(), response=response(), receiver=dict(receiver(), source_sha256="a"*64))
        self.assertEqual(self.runstate(), "RESPONSIVE_FOR_DECLARED_SCOPE")
    def test_effect_without_receiver_not_promoted(self):
        self.x["surface"].update(process=proc(), response=response(), effect=effect())
        self.assertEqual(self.runstate(), "RESPONSIVE_FOR_DECLARED_SCOPE")
    def test_receiver_effect_chain_only_receipt_consistent(self):
        self.x["surface"].update(process=proc(), response=response(), receiver=receiver(), effect=effect())
        answer = assess(self.x)
        self.assertEqual(answer["surface"]["state"], "EFFECT_RECEIPT_CONSISTENT")
        self.assertFalse(answer["surface"]["effect_proven_in_real_world"])
        self.assertEqual(answer["surface"]["source_authenticity"], "NOT_CHECKED")
    def test_receiver_effect_wrong_nonce_held(self):
        self.x["surface"].update(process=proc(), response=response(), receiver=receiver(),
                                 effect=dict(effect(), challenge_id="wrong"))
        self.assertEqual(self.runstate(), "RECEIVER_READBACK_CONSISTENT")
    def test_stale_appearance_not_current(self):
        self.x["surface"]["visual"]["observed_at"] = "2026-11-08T12:00:00Z"
        self.assertEqual(self.runstate(), "STALE_OR_UNOBSERVED")
    def test_stale_process_not_live(self):
        self.x["surface"].update(process=dict(proc(), observed_at="2026-11-08T12:00:00Z"), response=response())
        self.assertEqual(self.runstate(), "APPEARANCE_ONLY")
    def test_negative_clock_skew_held(self):
        self.x["surface"]["visual"]["observed_at"] = "2026-11-08T13:00:00Z"
        with self.assertRaisesRegex(ValueError, "CLOCK_FUTURE_HELD"): self.runstate()
    def test_reject_naive_time(self):
        self.x["as_of"] = "2026-11-08T12:50:00"
        with self.assertRaisesRegex(ValueError, "NAIVE_TIMESTAMP"): self.runstate()
    def test_no_evidence_unknown(self):
        self.x["surface"] = {}
        self.assertEqual(self.runstate(), "UNKNOWN")
    def test_visual_conflicts_with_missing_process(self):
        self.x["surface"].update(process=dict(proc(), present=False, coverage="COMPLETE_FOR_DECLARED_SCOPE"), response=response())
        self.assertEqual(self.runstate(), "CONFLICT_HELD")
    def test_bad_pid_fails(self):
        self.x["surface"]["process"] = dict(proc(), process_id=True)
        with self.assertRaisesRegex(ValueError, "INVALID_PID"): self.runstate()
    def test_unknown_visual_class_fails(self):
        self.x["surface"]["visual"]["kind"] = "MIND_READ"
        with self.assertRaisesRegex(ValueError, "UNKNOWN_VISUAL_SOURCE_KIND"): self.runstate()
    def test_missing_observer_fails(self):
        del self.x["surface"]["visual"]["observer_id"]
        with self.assertRaisesRegex(ValueError, "SOURCE_OBSERVER_REQUIRED"): self.runstate()
    def test_wrong_schema_fails(self):
        self.x["schema"] = "MAGICAL"
        with self.assertRaisesRegex(ValueError, "INVALID_SCHEMA"): self.runstate()

class OpportunityChecks(unittest.TestCase):
    def setUp(self):
        self.x = fixture()
    def opportunity(self):
        return assess(self.x)["popup_opportunity"]
    def test_one_report_needs_owner_not_auto_fix(self):
        self.x["events"] = [event(1, NOW)]
        o = self.opportunity()
        self.assertEqual(o["state"], "CAPTURE_OWNER_READ_ONLY")
        self.assertEqual(o["next"], "HOLD_REMOTE_OFFLINE_NO_RESTART")
    def test_three_distinct_reports_without_os_attribution(self):
        self.x["events"] = [event(i, t) for i,t in enumerate([
            "2026-11-08T12:40:00Z", "2026-11-08T12:45:00Z", NOW])]
        self.assertEqual(self.opportunity()["state"], "TRACE_REPEAT_INTERRUPTIONS")
    def test_duplicate_report_not_tripled(self):
        a = event(1, NOW)
        self.x["events"] = [a, a, a]
        self.assertEqual(self.opportunity()["count"], 1)
    def test_stale_events_not_current(self):
        self.x["events"] = [event(1, "2026-11-08T11:00:00Z")]
        self.assertEqual(self.opportunity()["count"], 0)
    def test_future_events_rejected(self):
        self.x["events"] = [event(1, "2026-11-09T11:00:00Z")]
        with self.assertRaisesRegex(ValueError, "CLOCK_FUTURE_HELD"): self.opportunity()
    def test_source_owner_attributed_review_only(self):
        self.x["remote_route"] = "CONNECTED"
        self.x["events"] = [event(i, t, "local-digest", "OS_WINDOW_METADATA", "ATTRIBUTED_FOR_SCOPE")
                            for i,t in enumerate(["2026-11-08T12:40:00Z",
                                                    "2026-11-08T12:45:00Z", NOW])]
        o = self.opportunity()
        self.assertEqual(o["state"], "REVIEW_BOUNDED_LAUNCHER_REPAIR")
        self.assertEqual(o["next"], "REVIEW_OWNED_LAUNCHER_HEADLESS_CANARY_NO_AUTOMATIC_CHANGE")
        self.assertEqual(o["actual_popup_cause"], "NOT_ESTABLISHED")
    def test_owner_name_without_os_data_cannot_promote(self):
        self.x["remote_route"] = "CONNECTED"
        self.x["events"] = [event(i, t, "claimed-PS7", "USER_REPORT", "ATTRIBUTED_FOR_SCOPE")
                            for i,t in enumerate(["2026-11-08T12:40:00Z",
                                                    "2026-11-08T12:45:00Z", NOW])]
        self.assertEqual(self.opportunity()["state"], "TRACE_REPEAT_INTERRUPTIONS")
    def test_forecast_is_uncalibrated_and_no_action(self):
        self.x["remote_route"] = "CONNECTED"
        self.x["events"] = [event(i, t, "verified-digest", "OS_WINDOW_METADATA", "ATTRIBUTED_FOR_SCOPE")
                            for i,t in enumerate(["2026-11-08T12:40:00Z",
                                                    "2026-11-08T12:45:00Z", NOW])]
        prediction = self.opportunity()["forecast"]
        self.assertEqual(prediction["epistemic_class"], "SHORT_HORIZON_UNCALIBRATED_PREDICTION")
        self.assertEqual(prediction["action_authority"], "NONE")
        self.assertEqual(prediction["predicted_at"], "2026-11-08T12:55:00+00:00")
    def test_unreliable_cadence_no_forecast(self):
        self.x["events"] = [event(i,t,"verified","OS_WINDOW_METADATA","ATTRIBUTED_FOR_SCOPE")
                            for i,t in enumerate(["2026-11-08T12:20:00Z",
                                                    "2026-11-08T12:46:30Z", NOW])]
        self.assertEqual(self.opportunity()["forecast"], "UNAVAILABLE")
    def test_many_events_budget(self):
        self.x["events"] = [event(i,NOW) for i in range(257)]
        with self.assertRaisesRegex(ValueError, "EVENT_BUDGET_EXCEEDED"): self.opportunity()
    def test_non_popup_events_ignored(self):
        a = event(1,NOW)
        a["kind"] = "CONTENT_CHANGE"
        self.x["events"] = [a]
        self.assertEqual(self.opportunity()["count"], 0)
    def test_unknown_event_class_fails(self):
        a = event(1,NOW)
        a["source_type"] = "MIND_READER"
        self.x["events"] = [a]
        with self.assertRaisesRegex(ValueError, "UNTRUSTED_EVENT_CLASS"): self.opportunity()
    def test_never_mutates_source(self):
        self.x["events"] = [event(1,NOW)]
        before=copy.deepcopy(self.x)
        self.opportunity()
        self.assertEqual(self.x,before)
    def test_no_simulated_device_restarts(self):
        self.x["events"]=[event(1,NOW)]
        out=assess(self.x)
        self.assertEqual(out["actual_process_restart"],"NOT_ATTEMPTED")
        self.assertFalse(out["live_automation_installed"])
        self.assertIsNone(out["popup_opportunity"]["measured_human_savings"])
    def test_video_movement_cannot_override_route_offline(self):
        self.x["surface"]["visual"]["kind"]="VIDEO_OR_ANIMATION"
        self.x["events"]=[event(1,NOW)]
        out=assess(self.x)
        self.assertEqual(out["popup_opportunity"]["next"],"HOLD_REMOTE_OFFLINE_NO_RESTART")
        self.assertEqual(out["surface"]["state"],"APPEARANCE_ONLY")

if __name__ == "__main__":
    unittest.main()
