#!/usr/bin/env python3
"""CoStageReview+ R0: read-only, bounded structural review-coverage canary.

It does not run reviewers, authenticate attestations, access the network, or
accept a real release. It validates a policy/source snapshot and reports holds.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

STAGES = (
    "DISCOVERY", "HYPOTHESIS", "DESIGN", "BUILD", "EXPERIMENT",
    "RELEASE", "OPERATION", "RECOVERY", "REEVO",
)
SEATS = (
    "PROPOSAL", "FORMAL_CHECK", "EMPIRICAL_CHECK", "CHALLENGE",
    "PERSPECTIVE", "PROVENANCE_CHECK", "SYNTHESIS",
)
SCORECARD_PASS = "PASS_BOUNDED"
CHECK_STATUSES = {"PASS_BOUNDED", "FAIL_OBSERVED", "PARTIAL_BOUNDED", "HELD", "UNKNOWN", "REVIEW_REQUIRED"}
REQUIRED_NONCLAIMS = {
    "PANEL_SEAT_NE_INDEPENDENT_REVIEWER",
    "STATIC_POLICY_PASS_NE_RUNTIME_ENFORCEMENT",
    "GITHUB_SOURCE_NE_RECEIVER_ACK",
    "SYNTHETIC_TEST_NE_PUBLIC_RELEASE",
    "LOCAL_IS_NOT_LANDED",
    "VALIDATION_IS_NOT_ACCEPTANCE",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
    "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
    "HASHING_IS_NOT_SEMANTIC_INGESTION",
    "DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY",
}

class ReviewError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise ReviewError(message)


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\x00" + data).hexdigest()


def canonical_json(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def validate_policy(policy: dict):
    require(isinstance(policy, dict), "POLICY_OBJECT_REQUIRED")
    require(policy.get("schema") == "CoCivium.CoStageReview.Policy.R0", "WRONG_POLICY_SCHEMA")
    require(policy.get("lifecycle_state") == "DESIGN_ONLY_NOT_ENFORCED_RUNTIME", "POLICY_MUST_NOT_CLAIM_RUNTIME")
    require(policy.get("risk_mode") == "FAIL_CLOSED_WHEN_UNPROVEN", "POLICY_NOT_FAIL_CLOSED")
    require(policy.get("seats") == list(SEATS), "SEVEN_SEATS_MUST_BE_DESCRIPTIVE_ONLY")
    limits = policy.get("turtle_limits", {})
    require(type(limits.get("max_depth")) is int and 0 <= limits["max_depth"] <= 2, "TURTLE_DEPTH_OVERRUN")
    require(type(limits.get("max_rounds")) is int and 0 <= limits["max_rounds"] <= 2, "TURTLE_ROUNDS_OVERRUN")
    require(limits.get("budget_inheritance") == "SHARED_PARENT_NO_REPLENISHMENT", "TURTLE_BUDGET_MINTING")
    require(limits.get("authority_inheritance") == "NO_AUTHORITY_EXPANSION", "TURTLE_AUTHORITY_EXPANSION")
    require(set(policy.get("nonclaims", [])) >= REQUIRED_NONCLAIMS, "MISSING_NONCLAIM")
    sources = policy.get("source_bindings")
    require(isinstance(sources, list) and len(sources) >= 3, "SOURCE_BINDINGS_MISSING")
    paths = [s.get("path") for s in sources]
    require(len(paths) == len(set(paths)), "DUPLICATE_SOURCE_BINDING")
    for s in sources:
        require(isinstance(s, dict) and set(s) == {"path", "git_blob_sha1", "role"}, "SOURCE_BINDING_SHAPE")
        require(isinstance(s["path"], str) and s["path"].startswith(("ai/", "docs/")) and ".." not in Path(s["path"]).parts, "SOURCE_PATH_NOT_PINNED_RELATIVE")
        require(isinstance(s["git_blob_sha1"], str) and len(s["git_blob_sha1"]) == 40 and all(c in "0123456789abcdef" for c in s["git_blob_sha1"]), "SOURCE_BLOB_SHA_INVALID")
    stages = policy.get("stages")
    require(isinstance(stages, list) and [s.get("stage") for s in stages] == list(STAGES), "LIFECYCLE_COVERAGE_NOT_NINE_STAGES")
    for stage in stages:
        require(set(stage) == {"stage", "required_gates", "required_evidence", "review_seats", "promotion_boundary", "next_proof"}, "STAGE_CONTRACT_FIELDS")
        require(isinstance(stage["required_gates"], list) and stage["required_gates"] and len(set(stage["required_gates"])) == len(stage["required_gates"]), "STAGE_GATE_EMPTY_OR_DUPLICATED")
        require(isinstance(stage["required_evidence"], list) and stage["required_evidence"] and len(set(stage["required_evidence"])) == len(stage["required_evidence"]), "STAGE_EVIDENCE_EMPTY_OR_DUPLICATED")
        require("PRIOR_WORK_REVIEW" in stage["required_evidence"], "STAGE_MISSING_PRIOR_REVIEW")
        require("NEGATIVE_RESULT_PRESERVATION" in stage["required_evidence"], "STAGE_MISSING_NEGATIVE_REVIEW")
        require(stage["review_seats"] and len(set(stage["review_seats"])) == len(stage["review_seats"]) and set(stage["review_seats"]) <= set(SEATS), "UNKNOWN_OR_DUPLICATE_REVIEW_SEAT")
        require(stage["promotion_boundary"] == "HELD_UNTIL_EXTERNAL_EVIDENCE_AND_AUTHORITY", "STAGE_AUTO_PROMOTION")
        require(isinstance(stage["next_proof"], str) and bool(stage["next_proof"].strip()), "MISSING_NEXT_PROOF")
    return True


def verify_source_bindings(policy: dict, root: Path) -> list[dict]:
    """Verify exact source bytes, not semantic correctness or durability."""
    bindings = []
    root = root.resolve()
    for bind in policy["source_bindings"]:
        p = (root / bind["path"]).resolve(strict=True)
        require(p.is_relative_to(root) and p.is_file(), "SOURCE_ESCAPED_ROOT")
        data = p.read_bytes()
        sha = git_blob_sha1(data)
        require(sha == bind["git_blob_sha1"], "SOURCE_CHANGED_OR_UNVERIFIED: " + bind["path"])
        bindings.append({"path": bind["path"], "git_blob_sha1": sha, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "role": bind["role"]})
    return bindings


def assess_scorecard(policy: dict, scorecard: dict, source_verification: bool = False) -> dict:
    """Only records missing gates; it cannot elevate self-reported passes to approval."""
    require(isinstance(scorecard, dict), "SCORECARD_NOT_OBJECT")
    require(scorecard.get("schema") == "CoCivium.CoSpiffSurvivabilityFireworks.R1", "WRONG_SCORECARD_SCHEMA")
    gates = scorecard.get("gates")
    require(isinstance(gates, list), "SCORECARD_GATES_MISSING")
    ids = [g.get("id") for g in gates]
    require(len(ids) == len(set(ids)), "DUPLICATE_GATE_IDS")
    require(all(isinstance(g.get("state"), str) and g["state"] in CHECK_STATUSES for g in gates), "UNKNOWN_GATE_STATE")
    gate_map = {g["id"]: g for g in gates}
    require(len(gate_map) == 14 and set(gate_map) == {"G%02d" % i for i in range(1, 15)}, "EXPECTED_FOURTEEN_SCORECARD_GATES")
    for g in gates:
        require(isinstance(g.get("nonclaim"), str) and g["nonclaim"].strip(), "SCORECARD_MISSING_NONCLAIM")
        require(isinstance(g.get("next_proof"), str) and g["next_proof"].strip(), "SCORECARD_MISSING_NEXT_PROOF")
    rows = []
    for stage in policy["stages"]:
        deps = stage["required_gates"]
        require(set(deps) <= set(gate_map), "UNKNOWN_DEPENDENCY")
        unproven = [x for x in deps if gate_map[x]["state"] != SCORECARD_PASS]
        rows.append({
            "stage": stage["stage"],
            "review_seats_required": stage["review_seats"],
            "review_seats_assigned_and_authenticated": 0,
            "proof_requirements": stage["required_evidence"],
            "source_scorecard_gates": {id: gate_map[id]["state"] for id in deps},
            "unproven_gates": unproven,
            "decision": "HELD_UNQUALIFIED_GATE" if unproven else "HELD_UNASSIGNED_UNAUTHENTICATED_REVIEW",
            "review_executed": False,
            "receiver_accepted": False,
            "next_proof": stage["next_proof"],
        })
    return {
        "schema": "CoCivium.CoStageReview.CoverageResult.R0",
        "status": "STATIC_COVERAGE_ONLY_NO_PANEL_EXECUTION",
        "source_bindings_verified": source_verification,
        "stage_count": len(rows),
        "eligible_for_release": False,
        "independent_receiver_ack": False,
        "stage_assessments": rows,
        "held_stages": sum(1 for r in rows if r["decision"].startswith("HELD_")),
        "reviewer_assignments_created": 0,
        "workers_started": 0,
        "external_messages_sent": 0,
        "next_safe_action": "One consenting independent first-use report and separate off-provider restore, each bound to exact source and receiver proof",
        "nonclaims": sorted(REQUIRED_NONCLAIMS),
    }


def validate_turtle_proposal(proposal: dict) -> bool:
    """Candidate budget and authority check only; does not launch a turtle."""
    require(isinstance(proposal, dict), "PROPOSAL_OBJECT_REQUIRED")
    require(type(proposal.get("depth")) is int and 0 <= proposal["depth"] <= 2, "DEPTH_TOO_HIGH")
    require(type(proposal.get("rounds")) is int and 0 <= proposal["rounds"] <= 2, "ROUNDS_TOO_HIGH")
    parent, allocated = proposal.get("parent_budget"), proposal.get("allocated_children")
    require(type(parent) is int and parent >= 0, "PARENT_BUDGET_INVALID")
    require(isinstance(allocated, list) and all(type(x) is int and x >= 0 for x in allocated), "CHILD_BUDGET_INVALID")
    require(sum(allocated) <= parent, "CHILDREN_MINT_BUDGET")
    parent_auth = proposal.get("parent_effects")
    child_auth = proposal.get("child_effects")
    require(isinstance(parent_auth, list) and isinstance(child_auth, list), "AUTHORITY_ARRAYS_REQUIRED")
    require(set(child_auth) <= set(parent_auth), "CHILDREN_GAIN_AUTHORITY")
    return True


def panel_independence_claim(reviewers: list[dict]) -> dict:
    """Detect obvious double-counting, but do not authenticate real human/model origins."""
    if not reviewers:
        return {"state": "HELD_NO_REVIEWERS", "independent_review_proven": False}
    actors = [x.get("actor_id") for x in reviewers]
    families = [x.get("model_family") for x in reviewers]
    origins = [x.get("source_domain") for x in reviewers]
    if any(not x for x in actors) or len(set(actors)) < len(actors):
        status = "HELD_DUPLICATED_ACTOR"
    elif len(set(families)) == 1 and len(set(origins)) == 1:
        status = "HELD_SHARED_MODEL_AND_SOURCE"
    else:
        status = "DECLARED_DIVERSE_NOT_AUTHENTICATED"
    return {"state": status, "independent_review_proven": False}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--policy", type=Path, default=Path("ai/review/stage-review-policy-r0.json"))
    p.add_argument("--scorecard", type=Path, default=Path("ai/resilience/cospiff-fireworks-r1.json"))
    p.add_argument("--report", type=Path, help="Write exclusive, no-clobber result; omit to stdout only")
    args = p.parse_args()
    try:
        policy = json.loads((args.repo_root / args.policy).read_text(encoding="utf-8"))
        validate_policy(policy)
        expected_scorecard_path = next((v["path"] for v in policy["source_bindings"] if v["role"] == "latest_inspected_resilience_scorecard"), None)
        require(expected_scorecard_path == args.scorecard.as_posix(), "SCORECARD_PATH_NOT_PINNED")
        bindings = verify_source_bindings(policy, args.repo_root)
        score = json.loads((args.repo_root / args.scorecard).read_text(encoding="utf-8"))
        result = assess_scorecard(policy, score, source_verification=True)
        result["verified_source_bindings"] = bindings
        if args.report:
            raw = json.dumps(result, sort_keys=True, indent=2).encode("utf-8") + b"\n"
            with args.report.open("xb") as f:
                f.write(raw)
            require(args.report.read_bytes() == raw, "REPORT_READBACK_MISMATCH")
        print(json.dumps({"status": result["status"], "stage_count": result["stage_count"],
            "held_stages": result["held_stages"], "source_bindings": len(bindings),
            "runtime_reviewers": 0, "public_fireworks_authorized": False, "report": str(args.report) if args.report else None}))
    except (ReviewError, OSError, ValueError, KeyError, TypeError) as exc:
        print("FAIL_CLOSED: " + str(exc))
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
