#!/usr/bin/env python3
"""CoAllBloom R0 downstream CoDoodle R1 harvest gate. Never executes candidates."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

FRONTIER_SCHEMA = "CoDoodle.CoNex.CandidateFrontier.R1"
RESULT_SCHEMA = "CoAllBloom.HarvestGate.R0"
MAX_CANDIDATES = 32
SCENARIOS = {
    "ENGINEERING_DEVICE": ("ENGINEERING_CANDIDATE", "BOUNDED_POLICY_TEST_ONLY"),
    "INTERSTICE_UI": ("ENGINEERING_CANDIDATE", "BOUNDED_POLICY_TEST_ONLY"),
    "ET_TECHNOSIGNATURE": ("EMPIRICAL_HYPOTHESIS", "HELD_NO_ACTUAL_DATA_OR_INDEPENDENT_REPLICATION"),
    "G_D_PHILOSOPHY": ("PHILOSOPHICAL_OR_METAPHORICAL", "NOT_AN_EMPIRICAL_ENTITY_FINDER"),
    "SYNTHKIND_FICTION": ("SPECULATIVE_STORY", "NO_VERIFIED_PRIMARY_DECLARATION_OR_FINISHED_MEDIA"),
}
NONCLAIMS = [
    "HARVEST_GATE_NE_EXECUTION", "SCORE_NE_TRUTH_OR_VALUE_PROOF",
    "PUBLISHER_OUTPUT_NE_RECEIVER_ACK", "COORBWARE_PROJECTION_NE_INSTALLED_RUNTIME",
    "X2_ROUTE_OFFLINE_NE_X2_POWER_OFF", "LOCAL_IS_NOT_LANDED",
    "LOGICAL_POPULATION_NE_WORKER_POPULATION", "METAPHOR_NE_EMPIRICAL_CAUSE",
]

class GateError(ValueError):
    pass


def canonical(data):
    return (json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _require(condition, message):
    if not condition:
        raise GateError(message)


def evaluate(frontier):
    """Validate one published R1 frontier and elect at most one no-effect study."""
    _require(isinstance(frontier, dict), "HOLD_FRONTIER_NOT_OBJECT")
    _require(frontier.get("schema") == FRONTIER_SCHEMA, "HOLD_UNKNOWN_FRONTIER_SCHEMA")
    selected = frontier.get("selected")
    _require(isinstance(selected, list) and len(selected) <= MAX_CANDIDATES,
             "HOLD_UNBOUNDED_OR_MISSING_CANDIDATES")
    _require(type(frontier.get("selected_count")) is int and frontier["selected_count"] == len(selected),
             "HOLD_COUNT_MISMATCH")
    _require(frontier.get("active_workers") == 0 and frontier.get("no_execution") is True,
             "HOLD_FRONTIER_MAY_HAVE_EFFECTS")
    source_sha = frontier.get("source_sha256", "")
    _require(isinstance(source_sha, str) and re.fullmatch(r"[0-9a-f]{64}", source_sha) is not None,
             "HOLD_MISSING_SOURCE_BINDING")
    seen = set()
    rows = []
    for x in selected:
        _require(isinstance(x, dict), "HOLD_BAD_DESCRIPTOR")
        cid = x.get("candidate_id")
        _require(isinstance(cid, str) and re.fullmatch(r"[0-9a-f]{20}", cid) is not None,
                 "HOLD_BAD_CANDIDATE_ID")
        _require(cid not in seen, "HOLD_DUPLICATE_CANDIDATE_ID")
        seen.add(cid)
        axes = x.get("axes")
        _require(isinstance(axes, dict), "HOLD_MISSING_AXES")
        scenario = axes.get("scenario")
        _require(scenario in SCENARIOS, "HOLD_UNKNOWN_EPISTEMIC_CLASS")
        expected = SCENARIOS[scenario]
        _require((x.get("epistemic_class"), x.get("proof_boundary")) == expected,
                 "HOLD_EVIDENCE_CLASS_PROMOTION_OR_MISMATCH")
        _require(x.get("authority") == "NONE", "HOLD_AUTHORITY_ESCALATION")
        effects = x.get("effects")
        _require(isinstance(effects, dict) and effects and
                 all(type(v) is int and v == 0 for v in effects.values()),
                 "HOLD_NONZERO_OR_UNKNOWN_EFFECTS")
        score = x.get("score")
        _require(type(score) is int and 0 <= score <= 100, "HOLD_UNBOUNDED_HEURISTIC")
        eligible = (scenario in ("ENGINEERING_DEVICE", "INTERSTICE_UI") and
                    axes.get("substrate") == "DETERMINISTIC_LOCAL" and
                    x.get("micro_canary_eligible") is True and
                    x.get("review_state") == "PASS_SHADOW_POLICY_ONLY")
        if not eligible:
            _require(isinstance(x.get("review_state"), str) and
                     x["review_state"].startswith("HELD"), "HOLD_UNGATED_CANDIDATE")
        rows.append({"candidate_id": cid, "scenario": scenario,
                     "operator": axes.get("operator"), "heuristic_score": score,
                     "harvest_state": "ELIGIBLE_FOR_NO_EFFECT_STUDY" if eligible else "HELD",
                     "source_review_state": x.get("review_state"),
                     "epistemic_class": expected[0], "proof_boundary": expected[1]})
    eligible_rows = sorted((r for r in rows if r["harvest_state"] == "ELIGIBLE_FOR_NO_EFFECT_STUDY"),
                           key=lambda r: (-r["heuristic_score"], r["candidate_id"]))
    elected = eligible_rows[0]["candidate_id"] if eligible_rows else None
    return {"schema": RESULT_SCHEMA,
            "status": "PASS_SHADOW_PROPOSAL_ONLY" if elected else "HELD_NO_ELIGIBLE_STUDY",
            "input_schema": FRONTIER_SCHEMA,
            "input_canonical_sha256": digest(canonical(frontier)),
            "source_sha256": source_sha,
            "total_addressable_not_executed": frontier.get("total_syntactic_descriptors"),
            "considered_count": len(rows), "elected_candidate_id": elected,
            "elected_action": "PROPOSE_ONE_READ_ONLY_CANARY" if elected else "NONE",
            "challenge_operators_present": sorted({r["operator"] for r in rows if r["operator"] in
                                                   ("NULL", "INVERSE", "FALSIFIER")}),
            "candidates": rows,
            "actual_worker_count": 0, "effects_performed": 0, "receiver_ack": False,
            "CoStead_landed": False, "CoOrbWare_runtime": False,
            "nonclaims": NONCLAIMS}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontier", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path,
                        help="A NEW file path; existing files are not overwritten")
    args = parser.parse_args()
    data = json.loads(args.frontier.read_text(encoding="utf-8"))
    result = evaluate(data)
    payload = canonical(result)
    with args.output.open("xb") as fp:
        fp.write(payload)
        fp.flush()
    _require(digest(args.output.read_bytes()) == digest(payload), "HOLD_RECEIPT_READBACK_MISMATCH")
    print(json.dumps({"status": result["status"], "elected": result["elected_candidate_id"],
                      "considered": result["considered_count"],
                      "output_sha256": digest(payload), "receiver_ack": False}, sort_keys=True))

if __name__ == "__main__":
    main()
