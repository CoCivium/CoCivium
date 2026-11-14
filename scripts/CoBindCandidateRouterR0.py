#!/usr/bin/env python3
"""CoBind candidate routing R0: deterministic read-only proposal, not an actuator."""
import argparse
from datetime import datetime, timezone
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


def aware_time(value):
    """Parse ISO-8601 including an offset. Naive or invalid clocks cannot attest order."""
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return moment.astimezone(timezone.utc) if moment.tzinfo is not None else None
    except (ValueError, OverflowError):
        return None


def route(claim, anchors):
    """Propose a location. No authorization, evidence upgrade, binding, or execution."""
    if not isinstance(claim, dict) or not isinstance(anchors, list):
        return {"state": "HELD_MALFORMED_INPUT"}
    required = ("relation_id", "work_id", "epistemic", "temporal_mode", "privacy", "receiver")
    missing = [k for k in required
               if not isinstance(claim.get(k), str) or not claim[k].strip()]
    if missing:
        return {"state": "HELD_MISSING_CLAIM_FIELDS", "missing": missing}
    epistemic = claim["epistemic"]
    mode = claim["temporal_mode"]
    if epistemic not in CLAIM_TO_ANCHOR or mode not in TEMPORAL:
        return {"state": "HELD_UNSUPPORTED_CLASS"}
    if epistemic == "OBSERVED":
        if mode not in ("PAST", "PRESENT"):
            return {"state": "HELD_OBSERVED_TEMPORAL_MODE"}
        if (not isinstance(claim.get("source_ref"), str)
                or not claim["source_ref"].strip()
                or not isinstance(claim.get("evidence_refs"), list)
                or not claim["evidence_refs"]):
            return {"state": "HELD_NO_OBSERVED_SOURCE_PROOF"}
        observed = aware_time(claim.get("observed_at"))
        if observed is None:
            return {"state": "HELD_UNDATED_OBSERVATION"}
        if mode == "PAST" and not claim.get("event_at"):
            return {"state": "HELD_UNDATED_PAST_WITNESS"}
        if claim.get("event_at") is not None:
            event = aware_time(claim["event_at"])
            if event is None or event > observed:
                return {"state": "HELD_INVALID_OBSERVATION_CLOCKS"}
    if epistemic == "PREDICTED":
        if (mode != "FUTURE" or not claim.get("issued_at")
                or not isinstance(claim.get("assumptions"), list)
                or not claim["assumptions"]):
            return {"state": "HELD_UNBOUND_FORECAST"}
        issued = aware_time(claim["issued_at"])
        target = aware_time(claim.get("target_at"))
        if issued is None or target is None or target <= issued:
            return {"state": "HELD_INVALID_FORECAST_CLOCKS"}
    if epistemic == "COUNTERFACTUAL" and mode != "COUNTERFACTUAL":
        return {"state": "HELD_COUNTERFACTUAL_SCOPE"}
    if epistemic == "HYPOTHESIS" and not claim.get("challenge"):
        return {"state": "HELD_UNCHALLENGEABLE_HYPOTHESIS"}
    if epistemic == "INTERPRETIVE" and claim.get("assert_empirical_effect"):
        return {"state": "HELD_INTERPRETATION_AS_EVIDENCE"}
    accepted, rejected = [], []
    for a in anchors:
        if not isinstance(a, dict):
            rejected.append({"id": "malformed-anchor", "reasons": ["malformed_anchor"]})
            continue
        failures = []
        if not isinstance(a.get("id"), str) or not a["id"].strip():
            failures.append("missing_anchor_identity")
        if a.get("kind") != CLAIM_TO_ANCHOR[epistemic]:
            failures.append("wrong_epistemic_anchor")
        if a.get("work_id") != claim["work_id"]:
            failures.append("work_identity_mismatch")
        if a.get("privacy") != claim["privacy"]:
            failures.append("privacy_mismatch")
        if (not isinstance(a.get("allowed_receivers"), list)
                or claim["receiver"] not in a["allowed_receivers"]):
            failures.append("receiver_not_qualified")
        if epistemic == "OBSERVED":
            if a.get("source_ref") != claim["source_ref"]:
                failures.append("source_mismatch")
            if mode == "PAST" and a.get("immutable_event_at") is None:
                failures.append("missing_frozen_event_time")
            if (a.get("immutable_event_at") is not None
                    and aware_time(a["immutable_event_at"]) != aware_time(claim.get("event_at"))):
                failures.append("historical_event_would_be_rewritten")
        if claim.get("operation") == "INVERSE_LOOKUP":
            if (not isinstance(a.get("operations"), list)
                    or "INVERSE_LOOKUP" not in a["operations"]):
                failures.append("inverse_lookup_unsupported")
        metrics = a.get("metrics", {})
        if (not isinstance(metrics, dict)
                or any(not isinstance(metrics.get(m), int) or isinstance(metrics.get(m), bool)
                       or not 0 <= metrics[m] <= 5 for m in METRICS)):
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
