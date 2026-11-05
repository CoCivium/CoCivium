import copy
import importlib.util
import pathlib
import unittest
from datetime import datetime, timezone

P = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "CoGainLatchShadowR0.py"
spec = importlib.util.spec_from_file_location("CoGainLatchShadowR0", P)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BASE = {
  "schema":"CoGainLatch.ShadowInput.R0", "as_of":"2026-11-04T22:00:00Z",
  "policy":{"freshness_hours":24,"metric_directions":{"correctness":"max","recovery_success":"max","p95_latency_ms":"min","human_relay_minutes":"min"},"hard_floors":{"correctness":0.99,"recovery_success":0.99},"metric_domains":{"correctness":{"min":0,"max":1},"recovery_success":{"min":0,"max":1},"p95_latency_ms":{"min":0},"human_relay_minutes":{"min":0}}},
  "incumbent":{"candidate_id":"x2-rickbar-r0","workload_id":"x2-visible-ux","environment":"x2-lab","receiver_class":"rickbar-local","authority_ceiling":"read_only","privacy_class":"private_local","measurement_protocol":"ux-cold-restart-v1","config_sha256":"a"*64,"metrics":{"correctness":1.0,"recovery_success":1.0,"p95_latency_ms":2000,"human_relay_minutes":5}},
  "challengers":[{"candidate_id":"x2-rickbar-r1","incumbent_id":"x2-rickbar-r0","workload_id":"x2-visible-ux","environment":"x2-lab","receiver_class":"rickbar-local","authority_ceiling":"read_only","privacy_class":"private_local","measurement_protocol":"ux-cold-restart-v1","predecessor_config_sha256":"a"*64,"config_sha256":"b"*64,"observed_at":"2026-11-04T21:58:00Z","measurement_state":"PASS","evidence_class":"REPLAYABLE_BENCHMARK","metrics":{"correctness":1.0,"recovery_success":1.0,"p95_latency_ms":1500,"human_relay_minutes":3},"source_refs":["sample://synthetic-source"],"independent_challenge_refs":["sample://synthetic-challenge"],"inverse_falsifier_refs":["sample://synthetic-inverse"],"rollback":{"config_sha256":"a"*64,"recovery_test_ref":"sample://synthetic-rollback"}}],
  "receiver_candidates":[{"receiver_id":"X2","observer_route":"OFFLINE","currentness_verified":False,"capability_verified":False},{"receiver_id":"X1","observer_route":"UNKNOWN","currentness_verified":False,"capability_verified":False}]
}


EVALUATION_TIME = datetime.fromisoformat("2026-11-04T22:05:00+00:00")

def run(packet):
    return mod.run(packet, evaluation_time=EVALUATION_TIME)

class Tests(unittest.TestCase):
    def test_synthetic_valid_proposal_is_only_shadow(self):
        r=run(copy.deepcopy(BASE))
        self.assertEqual(r["assessments"][0]["state"],"ELIGIBLE_SHADOW_PROMOTION_PROPOSAL")
        self.assertEqual(r["runtime_status"],"NOT_INSTALLED__NO_X2_ACTION")
    def test_x2_offline_blocks_actual_route(self):
        r=run(copy.deepcopy(BASE))
        self.assertEqual(r["receiver_route_proposals"][0]["state"],"HOLD_OBSERVER_ROUTE_OFFLINE")
    def test_wrong_environment_is_sibling_not_promotion(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["environment"]="different-node"
        self.assertEqual(run(p)["assessments"][0]["state"],"HOLD")
    def test_better_speed_cannot_bypass_correctness_floor(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["metrics"]["correctness"]=0.98
        self.assertTrue(any("CORRECTNESS" in x.upper() for x in run(p)["assessments"][0]["holds"]))
    def test_bool_metrics_rejected(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["metrics"]["correctness"]=True
        self.assertIn("INVALID_OR_INCOMPLETE_METRICS",run(p)["assessments"][0]["holds"])
    def test_no_rollback_no_promotion(self):
        p=copy.deepcopy(BASE);del p["challengers"][0]["rollback"]
        self.assertIn("ROLLBACK_PLAN_MISSING",run(p)["assessments"][0]["holds"])
    def test_stale_evidence_blocks(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["observed_at"]="2026-10-30T00:00:00Z"
        self.assertIn("STALE_OR_FUTURE_OBSERVATION",run(p)["assessments"][0]["holds"])
    def test_no_independent_challenge_blocks(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["independent_challenge_refs"]=[]
        self.assertIn("INDEPENDENT_CHALLENGE_UNBOUND",run(p)["assessments"][0]["holds"])
    def test_inverse_proof_is_required(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["inverse_falsifier_refs"]=[]
        self.assertIn("INVERSE_FALSIFIER_UNBOUND",run(p)["assessments"][0]["holds"])
    def test_non_gain_does_not_promote(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["metrics"]=copy.deepcopy(p["incumbent"]["metrics"])
        self.assertIn("NO_STRICT_MEASURED_GAIN",run(p)["assessments"][0]["holds"])
    def test_misleading_synthetic_class_not_promotable(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["evidence_class"]="SYNTHETIC_FIXTURE"
        self.assertIn("EVIDENCE_CLASS_NOT_PROMOTABLE",run(p)["assessments"][0]["holds"])
    def test_missing_authentic_source_refs_blocks(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["source_refs"]=[]
        self.assertIn("SOURCE_REFS_MISSING",run(p)["assessments"][0]["holds"])
    def test_only_proposals_even_when_receiver_ready(self):
        p=copy.deepcopy(BASE);p["receiver_candidates"][0].update(observer_route="ONLINE",currentness_verified=True,capability_verified=True)
        x=run(p)["receiver_route_proposals"][0]
        self.assertEqual(x["state"],"CANDIDATE_ROUTE__RECEIVER_READPROOF_REQUIRED")
        self.assertFalse(x["applied"])
    def test_no_auto_promote_foreign_authority(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["authority_ceiling"]="public_post"
        self.assertIn("DIFFERENT_COMPARABILITY_ENVELOPE__SIBLING_EVALUATION_REQUIRED",run(p)["assessments"][0]["holds"])
    def test_packet_digest_deterministic(self):
        self.assertEqual(run(copy.deepcopy(BASE))["input_sha256"],run(copy.deepcopy(BASE))["input_sha256"])


    def test_negative_latency_rejected(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["metrics"]["p95_latency_ms"]=-100
        self.assertIn("METRIC_DOMAIN_VIOLATION_CHALLENGER:p95_latency_ms",run(p)["assessments"][0]["holds"])

    def test_over_100_percent_recovery_rejected(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["metrics"]["recovery_success"]=2.0
        self.assertIn("METRIC_DOMAIN_VIOLATION_CHALLENGER:recovery_success",run(p)["assessments"][0]["holds"])

    def test_invalid_config_hash_rejected(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["config_sha256"]="g"*64
        self.assertIn("CONFIG_DIGEST_REQUIRED",run(p)["assessments"][0]["holds"])

    def test_bad_predecessor_hash_rejected(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["predecessor_config_sha256"]="z"*64
        self.assertIn("PREDECESSOR_DIGEST_INVALID",run(p)["assessments"][0]["holds"])

    def test_invalid_rollback_digest_rejected(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["rollback"]["config_sha256"]="x"*64
        self.assertIn("ROLLBACK_CONFIG_DIGEST_INVALID",run(p)["assessments"][0]["holds"])

    def test_incumbent_invalid_metric_does_not_pass(self):
        p=copy.deepcopy(BASE);p["incumbent"]["metrics"]["p95_latency_ms"]=-1
        self.assertIn("METRIC_DOMAIN_VIOLATION_INCUMBENT:p95_latency_ms",run(p)["assessments"][0]["holds"])

    def test_negative_human_relay_rejected(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["metrics"]["human_relay_minutes"]=-10
        self.assertIn("METRIC_DOMAIN_VIOLATION_CHALLENGER:human_relay_minutes",run(p)["assessments"][0]["holds"])

    def test_future_observation_rejected(self):
        p=copy.deepcopy(BASE);p["challengers"][0]["observed_at"]="2026-11-05T23:59:59Z"
        self.assertIn("STALE_OR_FUTURE_OBSERVATION",run(p)["assessments"][0]["holds"])

    def test_self_reported_clock_cannot_rejuvenate_old_measurement(self):
        p=copy.deepcopy(BASE)
        p["as_of"]="2000-01-01T00:05:00Z"
        p["challengers"][0]["observed_at"]="2000-01-01T00:00:00Z"
        observed=mod.run(p)
        self.assertIn("STALE_OR_FUTURE_OBSERVATION",observed["assessments"][0]["holds"])
        self.assertEqual(observed["evaluation_clock_source"],"HOST_UTC_CLOCK")

    def test_explicit_trusted_clock_for_reproducibility(self):
        observed=run(copy.deepcopy(BASE))
        self.assertEqual(observed["evaluation_clock_source"],"TRUSTED_CALLER_INJECTION")
        self.assertEqual(observed["assessments"][0]["state"],"ELIGIBLE_SHADOW_PROMOTION_PROPOSAL")

    def test_missing_metric_domains_fails_policy_validation(self):
        p=copy.deepcopy(BASE);del p["policy"]["metric_domains"]
        with self.assertRaisesRegex(ValueError,"INVALID_METRIC_POLICY"):
            run(p)

    def test_inverted_domain_fails_policy_validation(self):
        p=copy.deepcopy(BASE);p["policy"]["metric_domains"]["correctness"]={"min":1,"max":0}
        with self.assertRaisesRegex(ValueError,"INVALID_METRIC_DOMAINS"):
            run(p)

    def test_untrusted_naive_clock_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNTRUSTED_EVALUATION_CLOCK"):
            mod.run(copy.deepcopy(BASE),evaluation_time=datetime(2026,11,4,22,5))

if __name__ == "__main__": unittest.main()
