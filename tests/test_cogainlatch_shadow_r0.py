import copy
import importlib.util
import pathlib
import unittest

P = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "CoGainLatchShadowR0.py"
spec = importlib.util.spec_from_file_location("CoGainLatchShadowR0", P)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BASE = {
  "schema":"CoGainLatch.ShadowInput.R0", "as_of":"2026-11-04T22:00:00Z",
  "policy":{"freshness_hours":24,"metric_directions":{"correctness":"max","recovery_success":"max","p95_latency_ms":"min","human_relay_minutes":"min"},"hard_floors":{"correctness":0.99,"recovery_success":0.99}},
  "incumbent":{"candidate_id":"x2-rickbar-r0","workload_id":"x2-visible-ux","environment":"x2-lab","receiver_class":"rickbar-local","authority_ceiling":"read_only","privacy_class":"private_local","measurement_protocol":"ux-cold-restart-v1","config_sha256":"a"*64,"metrics":{"correctness":1.0,"recovery_success":1.0,"p95_latency_ms":2000,"human_relay_minutes":5}},
  "challengers":[{"candidate_id":"x2-rickbar-r1","incumbent_id":"x2-rickbar-r0","workload_id":"x2-visible-ux","environment":"x2-lab","receiver_class":"rickbar-local","authority_ceiling":"read_only","privacy_class":"private_local","measurement_protocol":"ux-cold-restart-v1","predecessor_config_sha256":"a"*64,"config_sha256":"b"*64,"observed_at":"2026-11-04T21:58:00Z","measurement_state":"PASS","evidence_class":"REPLAYABLE_BENCHMARK","metrics":{"correctness":1.0,"recovery_success":1.0,"p95_latency_ms":1500,"human_relay_minutes":3},"source_refs":["sample://synthetic-source"],"independent_challenge_refs":["sample://synthetic-challenge"],"inverse_falsifier_refs":["sample://synthetic-inverse"],"rollback":{"config_sha256":"a"*64,"recovery_test_ref":"sample://synthetic-rollback"}}],
  "receiver_candidates":[{"receiver_id":"X2","observer_route":"OFFLINE","currentness_verified":False,"capability_verified":False},{"receiver_id":"X1","observer_route":"UNKNOWN","currentness_verified":False,"capability_verified":False}]
}

class Tests(unittest.TestCase):
    def test_synthetic_valid_proposal_is_only_shadow(self):
        r=mod.run(copy.deepcopy(BASE))
        self.assertEqual(r["assessments"][0]["state"],"ELIGIBLE_SHADOW_PROMOTION_PROPOSAL")
        self.assertEqual(r["runtime_status"],"NOT_INSTALLED__NO_X2_ACTION")
    def test_x2_offline_blocks_actual_route(self):
        r=mod.run(copy.deepcopy(BASE))
        self.assertEqual(r["receiver_route_proposals"][0]["state"],"HOLD_OBSERVER_ROUTE_OFFLINE")
    def test_wrong_environment_is_sibling_not_promotion(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["environment"]="different-node"
        self.assertEqual(mod.run(p)["assessments"][0]["state"],"HOLD")
    def test_better_speed_cannot_bypass_correctness_floor(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["metrics"]["correctness"]=0.98
        self.assertTrue(any("CORRECTNESS" in x.upper() for x in mod.run(p)["assessments"][0]["holds"]))
    def test_bool_metrics_rejected(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["metrics"]["correctness"]=True
        self.assertIn("INVALID_OR_INCOMPLETE_METRICS",mod.run(p)["assessments"][0]["holds"])
    def test_no_rollback_no_promotion(self):
        p=copy.deepcopy(BASE);del p["challengers"][0]["rollback"]
        self.assertIn("ROLLBACK_PLAN_MISSING",mod.run(p)["assessments"][0]["holds"])
    def test_stale_evidence_blocks(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["observed_at"]="2026-10-30T00:00:00Z"
        self.assertIn("STALE_OR_FUTURE_OBSERVATION",mod.run(p)["assessments"][0]["holds"])
    def test_no_independent_challenge_blocks(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["independent_challenge_refs"]=[]
        self.assertIn("INDEPENDENT_CHALLENGE_UNBOUND",mod.run(p)["assessments"][0]["holds"])
    def test_inverse_proof_is_required(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["inverse_falsifier_refs"]=[]
        self.assertIn("INVERSE_FALSIFIER_UNBOUND",mod.run(p)["assessments"][0]["holds"])
    def test_non_gain_does_not_promote(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["metrics"]=copy.deepcopy(p["incumbent"]["metrics"])
        self.assertIn("NO_STRICT_MEASURED_GAIN",mod.run(p)["assessments"][0]["holds"])
    def test_misleading_synthetic_class_not_promotable(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["evidence_class"]="SYNTHETIC_FIXTURE"
        self.assertIn("EVIDENCE_CLASS_NOT_PROMOTABLE",mod.run(p)["assessments"][0]["holds"])
    def test_missing_authentic_source_refs_blocks(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["source_refs"]=[]
        self.assertIn("SOURCE_REFS_MISSING",mod.run(p)["assessments"][0]["holds"])
    def test_only_proposals_even_when_receiver_ready(self):
        p=copy.deepcopy(BASE);p["receiver_candidates"][0].update(observer_route="ONLINE",currentness_verified=True,capability_verified=True)
        x=mod.run(p)["receiver_route_proposals"][0]
        self.assertEqual(x["state"],"CANDIDATE_ROUTE__RECEIVER_READPROOF_REQUIRED")
        self.assertFalse(x["applied"])
    def test_no_auto_promote_foreign_authority(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["authority_ceiling"]="public_post"
        self.assertIn("DIFFERENT_COMPARABILITY_ENVELOPE__SIBLING_EVALUATION_REQUIRED",mod.run(p)["assessments"][0]["holds"])
    def test_packet_digest_deterministic(self):
        self.assertEqual(mod.run(copy.deepcopy(BASE))["input_sha256"],mod.run(copy.deepcopy(BASE))["input_sha256"])

if __name__ == "__main__": unittest.main()
