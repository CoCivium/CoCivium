#!/usr/bin/env python3
"""CoBind candidate routing R0: deterministic read-only proposal, not an actuator."""
import argparse
import json
from pathlib import Path

CLAIM_TO_ANCHOR = {
    "OBSERVED": "SOURCE_WITNESS",
    "HYPOTHESIS": "HYPOTHESIS_BRANCH",
    "INTERPRETIVE": "INTERPRETATION_BRANCH",
    "PREDICTED": "FORECAST_BRANCH",
    "COUNTERFACTUAL": "SCENARIO_BRANCH",
    "UNKNOWN": "UNKNOWN_REGISTER",
}
TEMPORAL = {"PAST", "PRESENT", "FUTURE", "COUNTERFACTUAL", "UNSPECIFIED"}
METRICS = ("provenance", "meaning", "time", "recovery", "receiver", "cost", "risk")


def route(claim, anchors):
    """Find a proposed source-bound anchor. Never execute a binding or upgrade claims."""
    required = ("relation_id", "work_id", "epistemic", "temporal_mode", "privacy", "receiver")
    missing = [k for k in required if not claim.get(k)]
    if missing:
        return {"state": "HELD_MISSING_CLAIM_FIELDS", "missing": missing}
    epistemic = claim["epistemic"]
    if epistemic not in CLAIM_TO_ANCHOR or claim["temporal_mode"] not in TEMPORAL:
        return {"state": "HELD_UNSUPPORTED_CLASS"}
    if epistemic == "OBSERVED":
        if not claim.get("source_ref") or not claim.get("evidence_refs"):
            return {"state": "HELD_NO_OBSERVED_SOURCE_PROOF"}
        if claim["temporal_mode"] == "FUTURE":
            return {"state": "HELD_FUTURE_IS_NOT_OBSERVED"}
        if claim["temporal_mode"] == "PAST" and not claim.get("event_at"):
            return {"state": "HELD_UNDATED_PAST_WITNESS"}
    if epistemic == "PREDICTED":
        if claim["temporal_mode"] != "FUTURE" or not claim.get("issued_at") or not claim.get("assumptions"):
            return {"state": "HELD_UNBOUND_FORECAST"}
    if epistemic == "COUNTERFACTUAL" and claim["temporal_mode"] != "COUNTERFACTUAL":
        return {"state": "HELD_COUNTERFACTUAL_SCOPE"}
    if epistemic == "HYPOTHESIS" and not claim.get("challenge"):
        return {"state": "HELD_UNCHALLENGEABLE_HYPOTHESIS"}
    if epistemic == "INTERPRETIVE" and claim.get("assert_empirical_effect"):
        return {"state": "HELD_INTERPRETATION_AS_EVIDENCE"}
    accepted, rejected = [], []
    for a in anchors:
        failures = []
        if a.get("kind") != CLAIM_TO_ANCHOR[epistemic]:
            failures.append("wrong_epistemic_anchor")
        if a.get("work_id") != claim["work_id"]:
            failures.append("work_identity_mismatch")
        if a.get("privacy") != claim["privacy"]:
            failures.append("privacy_mismatch")
        if claim["receiver"] not in a.get("allowed_receivers", []):
            failures.append("receiver_not_qualified")
        if claim.get("source_ref") and epistemic == "OBSERVED" and a.get("source_ref") != claim["source_ref"]:
            failures.append("source_mismatch")
        if epistemic == "OBSERVED" and a.get("immutable_event_at") not in (None, claim.get("event_at")):
            failures.append("historical_event_would_be_rewritten")
        if claim.get("operation") == "INVERSE_LOOKUP" and "INVERSE_LOOKUP" not in a.get("operations", []):
            failures.append("inverse_lookup_unsupported")
        metrics = a.get("metrics", {})
        if any(not isinstance(metrics.get(m), int) or isinstance(metrics.get(m), bool)
               or not 0 <= metrics[m] <= 5 for m in METRICS):
            failures.append("invalid_bounded_metrics")
        if failures:
            rejected.append({"id": a.get("id", "unnamed"), "reasons": failures})
            continue
        score = (
            3 * metrics["provenance"] + 2 * metrics["meaning"]
            + 2 * metrics["time"] + metrics["recovery"] + metrics["receiver"]
            - 2 * metrics["risk"] - metrics["cost"]
        )
        accepted.append({"id": a["id"], "kind": a["kind"], "score": score})
    if not accepted:
        return {"state": "HELD_NO_QUALIFIED_ANCHOR", "rejected": rejected}
    accepted.sort(key=lambda x: (-x["score"], x["id"]))
    return {
        "state": "CANDIDATE_BIND_NOT_EXECUTED",
        "selected": accepted[0],
        "alternatives": accepted[1:],
        "rejected": rejected,
        "relation_semantics": "LOOKUP_ONLY_NO_CAUSAL_INFERENCE"
        if claim.get("operation") == "INVERSE_LOOKUP" else "ORIGINAL_CLAIM_CLASS_PRESERVED",
        "authority_effect": "NONE",
        "evidence_effect": "NONE",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, help="JSON containing claim and anchors")
    args = ap.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    print(json.dumps(route(data["claim"], data["anchors"]), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
