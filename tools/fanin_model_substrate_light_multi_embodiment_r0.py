#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

def fail(code):
    raise SystemExit(code)

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-root", required=True)
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    fixture = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    files = sorted(Path(args.input_root).rglob("branch-receipt.json"))
    if len(files) != fixture["expected_fanin"]["branch_count"]:
        fail(f"FAIL_BRANCH_COUNT:{len(files)}")

    receipts = [json.loads(p.read_text(encoding="utf-8")) for p in files]
    for r in receipts:
        if r["STATE"] != "PASS_SYNTHETIC_MULTI_EMBODIMENT_BRANCH":
            fail("FAIL_BRANCH_STATE")
        if r["effect_execution_total"] != 0:
            fail("FAIL_EFFECT_EXECUTED")
        if r["logical_lane_id"] != fixture["logical_lane"]["logical_lane_id"]:
            fail("FAIL_LANE_ID_DRIFT")
        if r["replayed_completed_step_ids"]:
            fail("FAIL_COMPLETED_WORK_REPLAY")

    invariant_fields = [
        "checked_out_head_sha",
        "fixture_semantic_sha256",
        "logical_lane_id",
        "completed_step_ids_observed",
        "authority_ceiling",
        "confidentiality",
        "effect_ceiling",
        "decision_key"
    ]
    for field in invariant_fields:
        vals = {json.dumps(r[field], sort_keys=True) for r in receipts}
        if len(vals) != 1:
            fail("FAIL_CROSS_BRANCH_INVARIANT_DRIFT:" + field)

    embodiment_ids = {r["embodiment_id"] for r in receipts}
    if len(embodiment_ids) != len(receipts):
        fail("FAIL_DUPLICATE_EMBODIMENT_ID")

    failure_labels = {r["failure_domain_label"] for r in receipts}
    if len(failure_labels) != len(receipts):
        fail("FAIL_DUPLICATE_SIM_FAILURE_DOMAIN_LABEL")

    required_assertions = fixture["shared_assertions_required"]
    required_assertion_sha = canonical_sha(required_assertions)
    for r in receipts:
        if canonical_sha(r["shared_assertions"]) != required_assertion_sha:
            fail("FAIL_SHARED_ASSERTION_DRIFT")

    decision_key = fixture["decision_key"]
    decisions = {}
    branch_evidence = []
    unique_claims = []
    for r in sorted(receipts, key=lambda x: x["embodiment_id"]):
        decisions.setdefault(r["candidate_decision"], []).append(r["embodiment_id"])
        branch_evidence.append({
            "embodiment_id": r["embodiment_id"],
            "route_class": r["route_class"],
            "failure_domain_label": r["failure_domain_label"],
            "lens": r["lens"],
            "candidate_decision": r["candidate_decision"],
            "candidate_claims": r["candidate_claims"],
            "provenance": r["provenance"]
        })
        for claim in r["candidate_claims"]:
            unique_claims.append({
                "embodiment_id": r["embodiment_id"],
                "claim": claim
            })

    disagreements = []
    if len(decisions) > 1:
        disagreements.append({
            "decision_key": decision_key,
            "variants": [
                {"value": value, "embodiment_ids": ids}
                for value, ids in sorted(decisions.items())
            ],
            "winner": None,
            "disposition": "PRESERVE_DISAGREEMENT"
        })

    expected = fixture["expected_fanin"]
    if len(required_assertions) != expected["shared_assertion_count"]:
        fail("FAIL_SHARED_ASSERTION_COUNT")
    if len(disagreements) != expected["disagreement_count"]:
        fail("FAIL_DISAGREEMENT_COUNT")
    if expected["winner"] is not None:
        fail("FAIL_FIXTURE_MUST_NOT_PREDECLARE_WINNER")

    fanin = {
        "schema": "CoModelSubstrateLight.MultiEmbodimentFaninReceipt.v0.1",
        "STATE": "PASS_MULTI_EMBODIMENT_BRANCH_FANIN_PRESERVES_DISAGREEMENT",
        "checked_out_head_sha": receipts[0]["checked_out_head_sha"],
        "fixture_semantic_sha256": receipts[0]["fixture_semantic_sha256"],
        "logical_lane_id": receipts[0]["logical_lane_id"],
        "continuation_lane_id": expected["continuation_lane_id"],
        "branch_count": len(receipts),
        "branch_evidence_retained": True,
        "shared_assertions": required_assertions,
        "shared_assertion_count": len(required_assertions),
        "unique_candidate_claims": unique_claims,
        "disagreements": disagreements,
        "disagreement_count": len(disagreements),
        "winner": None,
        "replayed_completed_step_ids": [],
        "effect_execution_total": 0,
        "next_gate": expected["next_gate"],
        "branch_evidence": branch_evidence,
        "receipt_set_semantic_sha256": canonical_sha(branch_evidence),
        "coverage_boundary": [
            "SYNTHETIC_LOGICAL_EMBODIMENTS_ONLY",
            "NO_REAL_MODEL_BRANCHING",
            "NO_PHYSICAL_FAILURE_DOMAIN_INDEPENDENCE_CLAIM",
            "NO_RUNTIME_SCHEDULER",
            "NO_POLICY_WINNER_ELECTED"
        ],
        "nonclaims": fixture["nonclaims"]
    }

    if fanin["continuation_lane_id"] != fanin["logical_lane_id"]:
        fail("FAIL_CONTINUATION_LANE_DRIFT")
    if fanin["winner"] is not None:
        fail("FAIL_NEWEST_OR_MAJORITY_WINNER")
    if fanin["replayed_completed_step_ids"]:
        fail("FAIL_COMPLETED_WORK_REPLAY")

    out = Path(args.output)
    if out.exists():
        fail("FAIL_CLOSED_NO_CLOBBER")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(fanin, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "STATE": fanin["STATE"],
        "checked_out_head_sha": fanin["checked_out_head_sha"],
        "logical_lane_id": fanin["logical_lane_id"],
        "branch_count": fanin["branch_count"],
        "shared_assertion_count": fanin["shared_assertion_count"],
        "disagreement_count": fanin["disagreement_count"],
        "winner": fanin["winner"],
        "continuation_lane_id": fanin["continuation_lane_id"],
        "replayed_completed_step_ids": fanin["replayed_completed_step_ids"],
        "next_gate": fanin["next_gate"],
        "receipt_set_semantic_sha256": fanin["receipt_set_semantic_sha256"]
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
