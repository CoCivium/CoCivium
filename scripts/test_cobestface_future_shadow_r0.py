#!/usr/bin/env python3
"""Synthetic adversarial CoBF futures shadow selector tests."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from CoBestFaceFutureShadowR0 import shadow_select

def b():
    return dict(id="face.lastgood",work_id="work.public001",audience="PUBLIC_HUMAN",
                source_sha256="a"*64,privacy="PUBLIC_SAFE",currentness_at=1000,
                evidence="DECLARED_RECEIVER_MEASURE",
                metrics=dict(first_use_ms=8000,comprehension_per_1000=700,
                             task_success_per_1000=600,interruptions=0),
                focus_interference=False,state="SELECTED_LAST_GOOD")
def c(id="face.future1",**changes):
    r=b();r.pop("state");r["id"]=id;r["source_sha256"]="b"*64
    r["future"]=dict(future_id="future.portability",epistemic="PREFERRED",
                     horizon_seconds=7200,falsifier="Lower visitor completion",
                     inverse_ref="inverse.avoid_rewrite",null_ref="null.keep_baseline")
    r["metrics"]=dict(first_use_ms=7000,comprehension_per_1000=750,
                      task_success_per_1000=650,interruptions=0)
    r.update(changes);return r
def run(candidates=None,**changes):
    return shadow_select(b(), [c()] if candidates is None else candidates,
                         event=changes.pop("event","MATERIAL_SOURCE_DELTA"),
                         now_s=changes.pop("now_s",1100),**changes)

class CoBFFutureShadowR0(unittest.TestCase):
    def test_proposed_better_stays_shadow(self):
        o=run()
        self.assertEqual(o["state"],"SHADOW_PARETO_IMPROVEMENT_CANDIDATES")
        self.assertEqual(o["shadow_candidate_ids"],["face.future1"])
        self.assertEqual(o["selected_live_id"],"face.lastgood")
        self.assertEqual(o["effect"],"NONE")
        self.assertFalse(o["release_authorized"])
        self.assertFalse(o["global_front_binding"])
    def test_idle_tick_no_repaint(self):
        o=run(event="TIMER_TICK")
        self.assertEqual(o["state"],"QUIET_NO_QUALIFIED_EVENT")
        self.assertEqual(o["selected_live_id"],"face.lastgood")
    def test_scenario_is_not_observed(self):
        o=run([c(evidence="SYNTHETIC_FIXTURE")])
        self.assertEqual(o["state"],"SHADOW_HYPOTHESES_NEED_MEASUREMENT")
        self.assertIn("NO_INDEPENDENT_MEASUREMENTS",o["holds"])
    def test_declared_measure_not_receiver_ack(self):
        self.assertEqual(run()["receiver_ack"],"NOT_ESTABLISHED")
    def test_inversion_not_permission(self):
        self.assertFalse(run()["model_authority"])
    def test_tradeoff_not_silent_promotion(self):
        x=c();x["metrics"]["interruptions"]=1
        self.assertEqual(run([x])["state"],"KEEP_LAST_GOOD")
    def test_worse_time_fails(self):
        x=c();x["metrics"]["first_use_ms"]=8001
        self.assertEqual(run([x])["state"],"KEEP_LAST_GOOD")
    def test_no_change_not_improvement(self):
        x=c(metrics=b()["metrics"])
        self.assertEqual(run([x])["state"],"KEEP_LAST_GOOD")
    def test_focus_steal_fails(self):
        self.assertIn("INVALID_CANDIDATE",run([c(focus_interference=True)])["holds"])
    def test_private_candidate_fails(self):
        self.assertIn("INVALID_CANDIDATE",run([c(privacy="PRIVATE")])["holds"])
    def test_cross_audience_fails(self):
        self.assertIn("CROSS_WORK_OR_AUDIENCE",run([c(audience="PUBLIC_MACHINE")])["holds"])
    def test_cross_work_fails(self):
        self.assertIn("CROSS_WORK_OR_AUDIENCE",run([c(work_id="work.other")])["holds"])
    def test_stale_candidate_fails(self):
        self.assertIn("STALE_OR_FUTURE_DATED_CANDIDATE",run([c(currentness_at=1)],max_age_s=100)["holds"])
    def test_future_dated_candidate_fails(self):
        self.assertIn("STALE_OR_FUTURE_DATED_CANDIDATE",run([c(currentness_at=3000)])["holds"])
    def test_stale_baseline_fails(self):
        self.assertIn("STALE_OR_FUTURE_DATED_LAST_GOOD",run(now_s=300000)["holds"])
    def test_no_baseline_fails(self):
        self.assertIn("INVALID_LAST_GOOD",shadow_select({},[],event="MATERIAL_SOURCE_DELTA",now_s=1100)["holds"])
    def test_no_metric_float_or_nan(self):
        x=c();x["metrics"]["first_use_ms"]=float("nan")
        self.assertIn("INVALID_CANDIDATE",run([x])["holds"])
    def test_no_bool_as_score(self):
        x=c();x["metrics"]["first_use_ms"]=True
        self.assertIn("INVALID_CANDIDATE",run([x])["holds"])
    def test_no_unbounded_fanout(self):
        self.assertIn("INVALID_CANDIDATE_BUDGET",run([c("face.future%02d"%i) for i in range(9)])["holds"])
    def test_duplicate_source_identifier_fails(self):
        self.assertIn("DUPLICATE_ID",run([c(),c()])["holds"])
    def test_duplicate_does_not_block_valid_other_candidate(self):
        o=run([c(),c(),c("face.future2")])
        self.assertEqual(o["state"],"SHADOW_PARETO_IMPROVEMENT_CANDIDATES")
        self.assertIn("DUPLICATE_ID",o["holds"])
    def test_untrusted_future_class_fails(self):
        self.assertIn("INVALID_CANDIDATE",run([c(future=dict(c()["future"],epistemic="OBSERVED"))])["holds"])
    def test_empty_falsifier_fails(self):
        self.assertIn("INVALID_CANDIDATE",run([c(future=dict(c()["future"],falsifier=""))])["holds"])
    def test_null_future_is_required(self):
        f=c()["future"];del f["null_ref"]
        self.assertIn("INVALID_CANDIDATE",run([c(future=f)])["holds"])
    def test_incomparable_candidate_retained(self):
        x=c("face.tradeoff");x["metrics"]["comprehension_per_1000"]=650
        o=run([x,c("face.future2")])
        self.assertEqual(o["shadow_candidate_ids"],["face.future2"])
    def test_shadows_do_not_clobber_input(self):
        x=c();original=x.copy()
        run([x])
        self.assertEqual(x,original)
    def test_no_automatic_action_primitives(self):
        src=(Path(__file__).resolve().parent/"CoBestFaceFutureShadowR0.py").read_text()
        for banned in ("subprocess","os.system","socket","urllib.request","requests.post","git push","Popen"):
            self.assertNotIn(banned,src)

if __name__=="__main__":
    unittest.main()
