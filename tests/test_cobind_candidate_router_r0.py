"""Source-only adversarial tests for CoBind R0. No network or external effects."""
import copy
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "CoBindCandidateRouterR0.py"
spec = importlib.util.spec_from_file_location("cobind", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

WORK = "coall:research:comindseed:binding-lenses:r0"
BASE_METRICS = dict(provenance=4, meaning=4, time=4, recovery=3, receiver=4, cost=1, risk=1)


def claim(epistemic="HYPOTHESIS", **kw):
    c = dict(relation_id="synthetic-candidate", work_id=WORK, epistemic=epistemic,
             temporal_mode="UNSPECIFIED", privacy="PUBLIC", receiver="research",
             challenge="What observation discriminates it?")
    c.update(kw)
    return c


def anchor(kind="HYPOTHESIS_BRANCH", **kw):
    a = dict(id="qualified", kind=kind, work_id=WORK, privacy="PUBLIC",
             allowed_receivers=["research"], operations=["RELATE", "INVERSE_LOOKUP"],
             metrics=BASE_METRICS.copy())
    a.update(kw)
    return a


class CoBindAdversarialTests(unittest.TestCase):
    def test_hypothesis_qualified_only_as_candidate(self):
        out = mod.route(claim(), [anchor()])
        self.assertEqual(out["state"], "CANDIDATE_BIND_NOT_EXECUTED")
        self.assertEqual(out["authority_effect"], "NONE")
        self.assertEqual(out["evidence_effect"], "NONE")

    def test_observed_without_source_held(self):
        self.assertEqual(mod.route(claim("OBSERVED"), [anchor("SOURCE_WITNESS")])["state"],
                         "HELD_NO_OBSERVED_SOURCE_PROOF")

    def test_observed_with_exact_witness(self):
        c = claim("OBSERVED", temporal_mode="PAST", event_at="2026-10-24T00:00:00Z",
                  source_ref="sha:synthetic", evidence_refs=["synthetic-only"])
        a = anchor("SOURCE_WITNESS", source_ref="sha:synthetic",
                   immutable_event_at="2026-10-24T00:00:00Z")
        self.assertEqual(mod.route(c, [a])["state"], "CANDIDATE_BIND_NOT_EXECUTED")

    def test_late_discovery_cannot_rewrite_original_event(self):
        c = claim("OBSERVED", temporal_mode="PAST", event_at="2026-10-24T00:00:00Z",
                  observed_at="2026-11-10T00:00:00Z", source_ref="sha:synthetic",
                  evidence_refs=["synthetic-only"])
        a = anchor("SOURCE_WITNESS", source_ref="sha:synthetic",
                   immutable_event_at="2026-11-10T00:00:00Z")
        self.assertIn("historical_event_would_be_rewritten",
                      mod.route(c, [a])["rejected"][0]["reasons"])

    def test_prediction_must_have_issue_and_assumptions(self):
        c = claim("PREDICTED", temporal_mode="FUTURE", assumptions=["synthetic"])
        self.assertEqual(mod.route(c, [anchor("FORECAST_BRANCH")])["state"],
                         "HELD_UNBOUND_FORECAST")
        c["issued_at"] = "2026-11-10T00:00:00Z"
        self.assertEqual(mod.route(c, [anchor("FORECAST_BRANCH")])["state"],
                         "CANDIDATE_BIND_NOT_EXECUTED")

    def test_future_is_not_observed(self):
        c = claim("OBSERVED", temporal_mode="FUTURE", source_ref="synthetic",
                  evidence_refs=["synthetic-only"])
        self.assertEqual(mod.route(c, [anchor("SOURCE_WITNESS")])["state"],
                         "HELD_FUTURE_IS_NOT_OBSERVED")

    def test_counterfactual_stays_scenario(self):
        c = claim("COUNTERFACTUAL", temporal_mode="COUNTERFACTUAL")
        out = mod.route(c, [anchor("SOURCE_WITNESS"), anchor("SCENARIO_BRANCH")])
        self.assertEqual(out["selected"]["kind"], "SCENARIO_BRANCH")

    def test_inverse_is_read_only_lookup(self):
        out = mod.route(claim(operation="INVERSE_LOOKUP"), [anchor()])
        self.assertEqual(out["relation_semantics"], "LOOKUP_ONLY_NO_CAUSAL_INFERENCE")

    def test_private_source_cannot_use_public_anchor(self):
        out = mod.route(claim(privacy="PRIVATE"), [anchor()])
        self.assertEqual(out["state"], "HELD_NO_QUALIFIED_ANCHOR")
        self.assertIn("privacy_mismatch", out["rejected"][0]["reasons"])

    def test_wrong_workid_cannot_rebind(self):
        out = mod.route(claim(), [anchor(work_id="not-the-same")])
        self.assertIn("work_identity_mismatch", out["rejected"][0]["reasons"])

    def test_symbolic_cannot_claim_empirical_effect(self):
        out = mod.route(claim("INTERPRETIVE", assert_empirical_effect=True),
                        [anchor("INTERPRETATION_BRANCH")])
        self.assertEqual(out["state"], "HELD_INTERPRETATION_AS_EVIDENCE")

    def test_consciousness_claim_not_promoted_to_observation(self):
        out = mod.route(claim("HYPOTHESIS"), [anchor("SOURCE_WITNESS")])
        self.assertEqual(out["state"], "HELD_NO_QUALIFIED_ANCHOR")

    def test_ranking_only_after_gates(self):
        bad = anchor(id="impressive-but-private", privacy="PRIVATE",
                     metrics=dict(provenance=5, meaning=5, time=5, recovery=5,
                                  receiver=5, cost=0, risk=0))
        weak = anchor(id="qualified-low", metrics=dict(provenance=2, meaning=3, time=3,
                         recovery=3, receiver=2, cost=4, risk=3))
        good = anchor(id="qualified-high")
        out = mod.route(claim(), [bad, weak, good])
        self.assertEqual(out["selected"]["id"], "qualified-high")
        self.assertEqual(out["alternatives"][0]["id"], "qualified-low")

    def test_unknown_not_forced_false(self):
        out = mod.route(claim("UNKNOWN"), [anchor("UNKNOWN_REGISTER")])
        self.assertEqual(out["selected"]["kind"], "UNKNOWN_REGISTER")

    def test_unbounded_score_rejected(self):
        a = anchor(metrics=dict(BASE_METRICS, provenance=100))
        out = mod.route(claim(), [a])
        self.assertEqual(out["state"], "HELD_NO_QUALIFIED_ANCHOR")
        self.assertIn("invalid_bounded_metrics", out["rejected"][0]["reasons"])


if __name__ == "__main__":
    unittest.main()
