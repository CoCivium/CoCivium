"""CoSession layer differential R0: strictly synthetic, content-free timing triage.

No browser hooking, ChatGPT/session API, OS/network access, message capture,
provider calls, or automated session recovery. Timing values must be from
one monotonic, local clock; no causal diagnosis is possible from one trace.
"""
from __future__ import annotations

import re

FIELDS = frozenset({
    "trial_id", "cohort", "phase", "now_ms", "action_ms", "request_sent_ms",
    "response_complete_ms", "final_paint_ms", "event_loop_lag_ms",
    "ui_responsive", "transport_signal", "explicit_limit", "test_code"
})
COHORTS = frozenset({"FRESH", "MEDIUM", "LONG"})
PHASES = frozenset({"IDLE", "SUBMITTED", "WAIT_FOR_WAKE"})
TRANSPORT = frozenset({"NONE", "TIMEOUT", "CONNECTION_ERROR", "HTTP_5XX"})
NONCLAIMS = [
    "TIMING_CORRELATION_NE_BACKEND_ROOT_CAUSE",
    "UPSTREAM_WAIT_NE_MODEL_CONTEXT_EXHAUSTION",
    "CLIENT_RENDER_GAP_NE_DOM_ROOT_CAUSE",
    "NO_PROVIDER_SESSION_OR_MESSAGE_ACCESS",
    "LOCAL_SYNTHETIC_FIXTURE_NE_REAL_CHAT_MEASUREMENT",
]


def _integer(value, field, allow_none=False):
    if value is None and allow_none:
        return
    if type(value) is not int or value < 0 or value > 86_400_000:
        raise ValueError("INVALID_" + field.upper())


def _identifier(value, field):
    if type(value) is not str or re.fullmatch(r"[A-Za-z0-9._:-]{1,80}", value) is None:
        raise ValueError("INVALID_" + field.upper())


def validate(sample):
    """Allow-list avoids leaking messages, URLs, tokens, cookies or raw IDs."""
    if type(sample) is not dict or set(sample) != FIELDS:
        raise ValueError("INVALID_OR_EXTRA_FIELDS")
    for field in ("trial_id", "test_code"):
        _identifier(sample[field], field)
    if sample["cohort"] not in COHORTS or type(sample["cohort"]) is not str:
        raise ValueError("INVALID_COHORT")
    if sample["phase"] not in PHASES or type(sample["phase"]) is not str:
        raise ValueError("INVALID_PHASE")
    if sample["transport_signal"] not in TRANSPORT or type(sample["transport_signal"]) is not str:
        raise ValueError("INVALID_TRANSPORT_SIGNAL")
    if type(sample["explicit_limit"]) is not bool:
        raise ValueError("INVALID_EXPLICIT_LIMIT")
    if sample["ui_responsive"] is not None and type(sample["ui_responsive"]) is not bool:
        raise ValueError("INVALID_UI_RESPONSIVE")
    _integer(sample["now_ms"], "now_ms")
    for k in ("action_ms", "request_sent_ms", "response_complete_ms",
              "final_paint_ms", "event_loop_lag_ms"):
        _integer(sample[k], k, allow_none=True)
    if sample["phase"] != "SUBMITTED":
        if any(sample[k] is not None for k in (
            "action_ms", "request_sent_ms", "response_complete_ms", "final_paint_ms"
        )) or sample["transport_signal"] != "NONE" or sample["explicit_limit"]:
            raise ValueError("INVALID_QUIET_WITH_REQUEST_EVIDENCE")
        return
    if sample["action_ms"] is None:
        raise ValueError("MISSING_ACTION_START")
    pairs = [
        ("action_ms", "request_sent_ms"),
        ("request_sent_ms", "response_complete_ms"),
        ("response_complete_ms", "final_paint_ms"),
    ]
    for prev, nxt in pairs:
        if sample[nxt] is not None and sample[prev] is None:
            raise ValueError("IMPOSSIBLE_MISSING_PREDECESSOR")
        if sample[prev] is not None and sample[nxt] is not None and sample[nxt] < sample[prev]:
            raise ValueError("NONMONOTONIC_EVENT_ORDER")
    for k in ("action_ms", "request_sent_ms", "response_complete_ms", "final_paint_ms"):
        if sample[k] is not None and sample[k] > sample["now_ms"]:
            raise ValueError("FUTURE_LOCAL_EVENT")
    if sample["transport_signal"] != "NONE" and sample["response_complete_ms"] is not None:
        raise ValueError("CONFLICTING_SUCCESS_AND_TRANSPORT_ERROR")


def classify(sample, *, request_deadline_ms=30000, render_grace_ms=3000,
             event_loop_pressure_ms=250):
    """Only discriminates observable *layers*, never hidden provider internals."""
    validate(sample)
    for name, value in (
        ("REQUEST_DEADLINE", request_deadline_ms),
        ("RENDER_GRACE", render_grace_ms),
        ("EVENT_LOOP_PRESSURE", event_loop_pressure_ms),
    ):
        if type(value) is not int or value <= 0:
            raise ValueError("INVALID_POLICY_" + name)
    state = "UNKNOWN"
    reason = "INSUFFICIENT_EVIDENCE"
    next_check = "COLLECT_CONTENT_FREE_STAGE_TIMINGS"
    if sample["phase"] in {"IDLE", "WAIT_FOR_WAKE"}:
        state, reason, next_check = "HEALTHY_QUIET", "NO_SUBMITTED_ACTION", "WAIT_FOR_BOUND_WAKE"
    elif sample["explicit_limit"]:
        state, reason, next_check = (
            "PROVIDER_LIMIT_SIGNAL", "EXPLICIT_LIMIT_OBSERVED", "QUALIFY_PROVIDER_LIMIT_METADATA"
        )
    elif sample["transport_signal"] != "NONE":
        state, reason, next_check = (
            "TRANSPORT_OR_UPSTREAM_ERROR", sample["transport_signal"],
            "COMPARE_INDEPENDENT_NETWORK_AND_PROVIDER_STATUS"
        )
    elif sample["response_complete_ms"] is not None:
        if sample["final_paint_ms"] is not None:
            state, reason, next_check = (
                "COMPLETED", "RESPONSE_AND_FINAL_RENDER_OBSERVED", "PRESERVE_BASELINE"
            )
        elif sample["now_ms"] - sample["response_complete_ms"] >= render_grace_ms:
            if (sample["event_loop_lag_ms"] is not None
                    and sample["event_loop_lag_ms"] >= event_loop_pressure_ms):
                state, reason, next_check = (
                    "CLIENT_RENDER_PRESSURE_CANDIDATE",
                    "COMPLETED_RESPONSE_PLUS_LAGGED_LOCAL_EVENT_LOOP",
                    "COMPARE_CLEAN_BROWSER_PROFILE"
                )
            else:
                state, reason, next_check = (
                    "CLIENT_DELIVERY_OR_RENDER_GAP",
                    "RESPONSE_COMPLETE_BUT_NO_FINAL_PAINT",
                    "COMPARE_CLIENT_VERSUS_RENDERER"
                )
        else:
            state, reason, next_check = (
                "RENDER_PENDING", "WITHIN_RENDER_GRACE", "WAIT_WITHOUT_EXTRA_REQUEST"
            )
    elif sample["request_sent_ms"] is not None:
        if sample["now_ms"] - sample["request_sent_ms"] >= request_deadline_ms:
            state, reason, next_check = (
                "TRANSPORT_OR_UPSTREAM_UNRESOLVED",
                "SENT_NO_CONFIRMED_COMPLETION",
                "CHECK_NETWORK_REQUEST_OUTCOME_WITHOUT_CONTENT"
            )
        else:
            state, reason, next_check = (
                "REQUEST_PENDING", "WITHIN_REQUEST_DEADLINE", "WAIT_WITHOUT_RETRY"
            )
    elif sample["ui_responsive"] is False and (
        sample["now_ms"] - sample["action_ms"] >= render_grace_ms
    ):
        state, reason, next_check = (
            "CLIENT_INPUT_PATH_CANDIDATE",
            "ACTION_BUT_NO_SENT_REQUEST_AND_UI_NOT_RESPONSIVE",
            "COMPARE_CLEAN_BROWSER_PROFILE"
        )
    return {
        "trial_id": sample["trial_id"],
        "cohort": sample["cohort"],
        "state": state,
        "reason": reason,
        "next_safe_check": next_check,
        "request_effects": 0,
        "provider_session_effects": 0,
        "causal_attribution": "NOT_PROVEN",
        "nonclaims": NONCLAIMS,
    }


def compare_matched(fresh, long):
    """Cross-cohort observation; controls are mandatory, inference remains weak."""
    validate(fresh)
    validate(long)
    if fresh["cohort"] != "FRESH" or long["cohort"] != "LONG":
        raise ValueError("INVALID_COMPARISON_COHORT")
    if fresh["test_code"] != long["test_code"]:
        return {"state": "HOLD_TASK_MISMATCH", "causal_attribution": "NOT_PROVEN"}
    if classify(fresh)["state"] != "COMPLETED" or classify(long)["state"] != "COMPLETED":
        return {"state": "HOLD_NO_MATCHED_COMPLETIONS", "causal_attribution": "NOT_PROVEN"}
    f = fresh["response_complete_ms"] - fresh["request_sent_ms"]
    l = long["response_complete_ms"] - long["request_sent_ms"]
    return {
        "state": "LONG_LATENCY_ASSOCIATED" if l >= 2 * max(f, 1) else "NO_TWO_FOLD_DIFFERENCE",
        "fresh_request_ms": f, "long_request_ms": l,
        "causal_attribution": "NOT_PROVEN",
        "next_safe_check": "REPEAT_MATCHED_PAIRS_ACROSS_INDEPENDENT_BROWSER_PROFILES",
    }
