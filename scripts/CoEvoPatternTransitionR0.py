#!/usr/bin/env python3
"""CoPatternGate R0: bounded, read-only CoEvo fan-in -> candidate fan-out review.

No network, filesystem writes, sessions, device actions, broadcasts or authority grants.
A qualifying result is a shadow REVIEW PLAN, not a receiver ACK or deployment.
"""
import argparse
import copy
import json
import sys

KINDS = {
    "RECURRENT", "INVERSION", "INBETWEEN", "FEEDBACK", "LAG",
    "INVARIANT", "CONTRADICTION", "BOTTLENECK", "TRANSFER",
    "UNKNOWN_RELATION", "REGRESSION",
}
EPISTEMIC = {
    "OBSERVED", "INFERRED", "HYPOTHESIS", "PREDICTED", "UNKNOWN",
    "COUNTERFACTUAL", "METAPHORICAL",
}
EFFECTS = {
    "NONE", "PUBLICATION", "PUBLIC_OUTREACH", "RUNTIME",
    "CREDENTIAL", "FINANCIAL", "PRIVACY_BOUNDARY",
    "AUTHORITY_CHANGE", "ACCESS_GRANT", "ACCESS_REVOCATION",
    "IRREVERSIBLE", "UNKNOWN",
}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value, min_count=0):
    return (
        isinstance(value, list)
        and len(value) >= min_count
        and all(nonempty(x) for x in value)
    )


def outcome(record, disposition, reason):
    # Do not echo confidential claims or untrusted evidence into routing reports.
    return {
        "schema": "CoEvo.PatternTransitionDecision.R0",
        "delta_id": (record.get("delta_id") if record.get("confidentiality") == "PUBLIC" and nonempty(record.get("delta_id")) else None),
        "disposition": disposition,
        "reason": reason,
        "effects_performed": 0,
        "receiver_ack": "UNPROVEN",
        "runtime_state": "NOT_OBSERVED",
        "authority_granted": False,
        "claim_ceiling": "SOURCE_BOUND_RESEARCH_CANDIDATE_ONLY",
    }


def evaluate(record):
    if not isinstance(record, dict):
        return outcome({}, "HOLD_INVALID", "RECORD_NOT_OBJECT")
    if not nonempty(record.get("delta_id")):
        return outcome(record, "HOLD_INVALID", "MISSING_DELTA_ID")
    if record.get("materiality") == "NONMATERIAL":
        return outcome(record, "QUIESCENT", "NO_MATERIAL_DELTA")
    if record.get("materiality") != "MATERIAL":
        return outcome(record, "HOLD_INVALID", "UNKNOWN_MATERIALITY")
    if not strings(record.get("source_refs"), 1):
        return outcome(record, "HOLD_UNVERIFIED", "MISSING_SOURCE_BINDING")
    if record.get("currentness") != "CURRENT":
        return outcome(record, "HOLD_UNVERIFIED", "CURRENTNESS_UNQUALIFIED")
    if record.get("confidentiality") != "PUBLIC":
        return outcome(record, "HOLD_PRIVATE", "NO_PUBLIC_ROUTE_FROM_UNQUALIFIED_PRIVACY")
    if record.get("pattern_kind") not in KINDS:
        return outcome(record, "HOLD_INVALID", "UNKNOWN_PATTERN_KIND")
    if record.get("epistemic_class") not in EPISTEMIC:
        return outcome(record, "HOLD_INVALID", "UNKNOWN_EPISTEMIC_CLASS")
    if not nonempty(record.get("claim")):
        return outcome(record, "HOLD_INVALID", "MISSING_CLAIM")
    effects = record.get("effect_classes")
    if not strings(effects, 1) or any(e not in EFFECTS for e in effects):
        return outcome(record, "HOLD_INVALID", "INVALID_EFFECT_CLASS")
    if effects != ["NONE"]:
        return outcome(record, "HOLD_EFFECT_GATE", "EFFECT_AUTHORIZATION_REQUIRED")
    if record.get("authority_ceiling") != "READ_ONLY":
        return outcome(record, "HOLD_EFFECT_GATE", "NO_AUTHORITY_PROMOTION")
    if not nonempty(record.get("receiver_class")):
        return outcome(record, "HOLD_UNVERIFIED", "MISSING_RECEIVER_FIT")
    if not nonempty(record.get("bounded_test")):
        return outcome(record, "HOLD_UNVERIFIED", "MISSING_DISCRIMINATING_TEST")
    if not nonempty(record.get("wake_condition")):
        return outcome(record, "HOLD_UNVERIFIED", "MISSING_WAKE_OR_STOP")
    if not nonempty(record.get("expiry_condition")):
        return outcome(record, "HOLD_UNVERIFIED", "UNBOUNDED_HYPOTHESIS_SLOT")
    if record.get("pattern_kind") == "INVERSION":
        if not strings(record.get("alternatives"), 2):
            return outcome(record, "HOLD_UNVERIFIED", "INVERSION_WITHOUT_ORIGINAL_AND_ALTERNATIVE")
    if record.get("pattern_kind") in {"INBETWEEN", "UNKNOWN_RELATION"}:
        if not strings(record.get("gap_endpoints"), 2):
            return outcome(record, "HOLD_UNVERIFIED", "GAP_WITHOUT_TYPED_ENDPOINTS")
    if record.get("epistemic_class") == "PREDICTED" or record.get("pattern_kind") == "LAG":
        pred = record.get("prediction")
        if not isinstance(pred, dict) or not all(
            nonempty(pred.get(k))
            for k in ("outcome", "horizon", "falsifier", "baseline_ref")
        ):
            return outcome(record, "HOLD_UNVERIFIED", "FORECAST_WITHOUT_TESTABLE_HORIZON")
    if record.get("self_reported_ack"):
        return outcome(record, "HOLD_UNVERIFIED", "SELF_REPORT_NE_RECEIVER_READPROOF")
    if not strings(record.get("counterexamples"), 1):
        return outcome(record, "HOLD_UNVERIFIED", "NO_CHALLENGE_OR_NEGATIVE_CONTROL")
    if record.get("pattern_kind") == "CONTRADICTION" or record.get("contradiction_unresolved"):
        return outcome(record, "CHALLENGE_READ_ONLY", "PRESERVE_CONTRADICTION")
    return outcome(record, "REVIEW_SHADOW_ONLY", "ELIGIBLE_FOR_BOUNDED_HUMAN_OR_MACHINE_REVIEW")


BASE = {
    "delta_id": "synthetic:pattern-001",
    "materiality": "MATERIAL",
    "source_refs": ["public:synthetic-fixture"],
    "currentness": "CURRENT",
    "confidentiality": "PUBLIC",
    "pattern_kind": "RECURRENT",
    "epistemic_class": "HYPOTHESIS",
    "claim": "A material pattern may be present",
    "effect_classes": ["NONE"],
    "authority_ceiling": "READ_ONLY",
    "receiver_class": "internal-review",
    "bounded_test": "compare independent observations against pinned baseline",
    "wake_condition": "new independent evidence",
    "expiry_condition": "close after bounded review without corroboration",
    "counterexamples": ["negative-control:synthetic"],
    "alternatives": ["retain existing approach", "test challenger"],
    "gap_endpoints": ["synthetic:source", "synthetic:receiver"],
    "prediction": {
        "outcome": "observable outcome would change",
        "horizon": "next test window",
        "falsifier": "no difference against preregistered baseline",
        "baseline_ref": "public:synthetic-baseline",
    },
}


def selftest():
    scenarios = [
        ("eligible shadow", {}, "REVIEW_SHADOW_ONLY"),
        ("no material", {"materiality": "NONMATERIAL"}, "QUIESCENT"),
        ("missing source", {"source_refs": []}, "HOLD_UNVERIFIED"),
        ("stale", {"currentness": "STALE"}, "HOLD_UNVERIFIED"),
        ("unknown privacy", {"confidentiality": "UNKNOWN"}, "HOLD_PRIVATE"),
        ("private", {"confidentiality": "PRIVATE"}, "HOLD_PRIVATE"),
        ("effect gated", {"effect_classes": ["RUNTIME"]}, "HOLD_EFFECT_GATE"),
        ("no authority escalation", {"authority_ceiling": "SYSTEM_ACTUATOR"}, "HOLD_EFFECT_GATE"),
        ("unbounded slot", {"expiry_condition": ""}, "HOLD_UNVERIFIED"),
        ("no discriminating test", {"bounded_test": ""}, "HOLD_UNVERIFIED"),
        ("no negative control", {"counterexamples": []}, "HOLD_UNVERIFIED"),
        ("inversion without alternatives", {"pattern_kind": "INVERSION", "alternatives": ["one"]}, "HOLD_UNVERIFIED"),
        ("valid inversion", {"pattern_kind": "INVERSION"}, "REVIEW_SHADOW_ONLY"),
        ("missing between endpoints", {"pattern_kind": "INBETWEEN", "gap_endpoints": []}, "HOLD_UNVERIFIED"),
        ("valid between", {"pattern_kind": "INBETWEEN"}, "REVIEW_SHADOW_ONLY"),
        ("unknown relation kept", {"pattern_kind": "UNKNOWN_RELATION"}, "REVIEW_SHADOW_ONLY"),
        ("prediction lacks falsifier", {"epistemic_class": "PREDICTED", "prediction": {"horizon": "tomorrow"}}, "HOLD_UNVERIFIED"),
        ("lag with horizon", {"pattern_kind": "LAG"}, "REVIEW_SHADOW_ONLY"),
        ("self reported ack", {"self_reported_ack": True}, "HOLD_UNVERIFIED"),
        ("contradiction", {"pattern_kind": "CONTRADICTION"}, "CHALLENGE_READ_ONLY"),
        ("unresolved contradiction", {"contradiction_unresolved": True}, "CHALLENGE_READ_ONLY"),
        ("unknown effect", {"effect_classes": ["UNKNOWN"]}, "HOLD_EFFECT_GATE"),
    ]
    for name, edits, expected in scenarios:
        r = copy.deepcopy(BASE)
        r.update(edits)
        actual = evaluate(r)
        assert actual["disposition"] == expected, (name, actual, expected)
        assert actual["effects_performed"] == 0
        assert actual["receiver_ack"] == "UNPROVEN"
        assert not actual["authority_granted"]
        if r.get("confidentiality") != "PUBLIC":
            assert actual["delta_id"] is None, (name, "PRIVATE_ID_LEAK")
    print(json.dumps({
        "schema": "CoEvo.PatternTransitionSelftest.R0",
        "cases": len(scenarios), "passed": len(scenarios),
        "scope": "SYNTHETIC_SELFTEST_ONLY",
        "receiver_ack": "UNPROVEN", "runtime": "NOT_TESTED",
    }, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--input", help="read-only JSON input path")
    args = parser.parse_args()
    if args.selftest:
        selftest()
        return 0
    if not args.input:
        parser.error("supply --selftest or --input PATH")
    with open(args.input, "r", encoding="utf-8") as f:
        record = json.load(f)
    print(json.dumps(evaluate(record), sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
