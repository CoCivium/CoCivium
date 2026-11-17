"""Synthetic differential timing negatives. No ChatGPT traffic or personal data."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "examples" / "cotalkitout"))
from session_layer_differential_r0 import classify, compare_matched, validate


def obs(**overrides):
    row = dict(
        trial_id="fixture-1", test_code="public-synthetic-constant",
        cohort="LONG", phase="SUBMITTED",
        now_ms=60000, action_ms=0, request_sent_ms=100,
        response_complete_ms=200, final_paint_ms=250,
        event_loop_lag_ms=20, ui_responsive=True,
        transport_signal="NONE", explicit_limit=False,
    )
    row.update(overrides)
    return row


class LayerDifferentialTests(unittest.TestCase):
    def test_finished_response_and_render_is_success(self):
        result = classify(obs())
        self.assertEqual("COMPLETED", result["state"])
        self.assertEqual("NOT_PROVEN", result["causal_attribution"])
        self.assertEqual(0, result["provider_session_effects"])

    def test_completed_backend_client_render_bottleneck(self):
        result = classify(obs(final_paint_ms=None, event_loop_lag_ms=1200))
        self.assertEqual("CLIENT_RENDER_PRESSURE_CANDIDATE", result["state"])
        self.assertNotIn("DOM", result["reason"])

    def test_response_without_paint_does_not_claim_dom_cause(self):
        result = classify(obs(final_paint_ms=None, event_loop_lag_ms=None))
        self.assertEqual("CLIENT_DELIVERY_OR_RENDER_GAP", result["state"])

    def test_render_grace_is_not_failure(self):
        result = classify(obs(now_ms=1000, final_paint_ms=None))
        self.assertEqual("RENDER_PENDING", result["state"])

    def test_sent_unresolved_not_context_exhaustion(self):
        result = classify(obs(response_complete_ms=None, final_paint_ms=None))
        self.assertEqual("TRANSPORT_OR_UPSTREAM_UNRESOLVED", result["state"])
        self.assertNotIn("CONTEXT", result["reason"])

    def test_pending_request_remains_pending(self):
        result = classify(obs(now_ms=600, response_complete_ms=None, final_paint_ms=None))
        self.assertEqual("REQUEST_PENDING", result["state"])

    def test_transport_signal_preempts_speculation(self):
        result = classify(obs(transport_signal="TIMEOUT", response_complete_ms=None,
                              final_paint_ms=None))
        self.assertEqual("TRANSPORT_OR_UPSTREAM_ERROR", result["state"])
        self.assertEqual("TIMEOUT", result["reason"])

    def test_explicit_provider_limit_separately_identified(self):
        result = classify(obs(explicit_limit=True, response_complete_ms=None,
                              final_paint_ms=None))
        self.assertEqual("PROVIDER_LIMIT_SIGNAL", result["state"])

    def test_idle_and_bound_wait_are_not_dead(self):
        for phase in ("IDLE", "WAIT_FOR_WAKE"):
            with self.subTest(phase=phase):
                result = classify(obs(
                    phase=phase, action_ms=None, request_sent_ms=None,
                    response_complete_ms=None, final_paint_ms=None))
                self.assertEqual("HEALTHY_QUIET", result["state"])

    def test_unresponsive_before_request_sent_is_client_input_candidate(self):
        result = classify(obs(request_sent_ms=None, response_complete_ms=None,
                              final_paint_ms=None, ui_responsive=False))
        self.assertEqual("CLIENT_INPUT_PATH_CANDIDATE", result["state"])

    def test_no_response_is_not_dom_diagnosis(self):
        result = classify(obs(response_complete_ms=None, final_paint_ms=None,
                              event_loop_lag_ms=1600))
        self.assertEqual("TRANSPORT_OR_UPSTREAM_UNRESOLVED", result["state"])

    def test_missing_input_unknown(self):
        result = classify(obs(request_sent_ms=None, response_complete_ms=None,
                              final_paint_ms=None, ui_responsive=True))
        self.assertEqual("UNKNOWN", result["state"])

    def test_extra_sensitive_fields_rejected(self):
        for key in ("message", "url", "cookie", "token", "account_id", "conversation_id"):
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError, "EXTRA_FIELDS"):
                    validate(obs(**{key: "sensitive"}))

    def test_invalid_identity_and_time_rejected(self):
        variants = [
            {"trial_id": "https://example.invalid/?s=secret"},
            {"test_code": "secret text with spaces"},
            {"now_ms": -1}, {"now_ms": 8.0}, {"ui_responsive": 1},
            {"event_loop_lag_ms": -5}, {"explicit_limit": 1},
            {"request_sent_ms": True},
            {"request_sent_ms": 1000, "response_complete_ms": 100},
            {"response_complete_ms": 1000, "final_paint_ms": 200},
            {"response_complete_ms": None, "final_paint_ms": 200},
        ]
        for kv in variants:
            with self.subTest(kv=kv), self.assertRaises(ValueError):
                validate(obs(**kv))

    def test_conflicting_success_transport_evidence_rejected(self):
        with self.assertRaisesRegex(ValueError, "CONFLICTING_SUCCESS"):
            validate(obs(transport_signal="HTTP_5XX"))

    def test_healthy_idle_with_submitted_request_rejected(self):
        with self.assertRaisesRegex(ValueError, "INVALID_QUIET"):
            validate(obs(phase="IDLE"))

    def test_matched_cohort_difference_does_not_claim_cause(self):
        fresh = obs(cohort="FRESH", request_sent_ms=10, response_complete_ms=110,
                    final_paint_ms=120)
        long = obs(cohort="LONG", request_sent_ms=10, response_complete_ms=510,
                   final_paint_ms=520)
        result = compare_matched(fresh, long)
        self.assertEqual("LONG_LATENCY_ASSOCIATED", result["state"])
        self.assertEqual(100, result["fresh_request_ms"])
        self.assertEqual(500, result["long_request_ms"])
        self.assertEqual("NOT_PROVEN", result["causal_attribution"])

    def test_comparison_fails_closed_if_mismatched_or_unfinished(self):
        fresh = obs(cohort="FRESH")
        different = obs(cohort="LONG", test_code="different")
        self.assertEqual("HOLD_TASK_MISMATCH", compare_matched(fresh, different)["state"])
        incomplete = obs(response_complete_ms=None, final_paint_ms=None)
        self.assertEqual("HOLD_NO_MATCHED_COMPLETIONS",
                         compare_matched(fresh, incomplete)["state"])

    def test_non_executing_and_bounded_policy(self):
        result = classify(obs())
        self.assertEqual(0, result["request_effects"])
        self.assertIn("NO_PROVIDER_SESSION_OR_MESSAGE_ACCESS", result["nonclaims"])
        with self.assertRaisesRegex(ValueError, "INVALID_POLICY_REQUEST_DEADLINE"):
            classify(obs(), request_deadline_ms=0)


if __name__ == "__main__":
    unittest.main()
