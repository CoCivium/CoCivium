#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

P = Path("fixtures/relations/coinquiry_compiler_r0f.json")

def fail(code):
    raise SystemExit(code)

def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()

def eligible(c):
    return (
        bool(c["receiver"].strip())
        and bool(c["bounded_probe"].strip())
        and c["evidence_surface_available"] is True
        and c["authority_conflict"] is False
        and c["already_resolved"] is False
        and bool(c["negative_evidence"].strip())
        and bool(c["retirement_condition"].strip())
    )

def dominates(a, b):
    no_worse = (
        a["retirement_leverage"] >= b["retirement_leverage"]
        and a["dependency_reduction"] >= b["dependency_reduction"]
        and a["human_attention_reduction"] >= b["human_attention_reduction"]
        and a["false_completion_detection"] >= b["false_completion_detection"]
        and a["proof_cost"] <= b["proof_cost"]
    )
    strictly_better = (
        a["retirement_leverage"] > b["retirement_leverage"]
        or a["dependency_reduction"] > b["dependency_reduction"]
        or a["human_attention_reduction"] > b["human_attention_reduction"]
        or a["false_completion_detection"] > b["false_completion_detection"]
        or a["proof_cost"] < b["proof_cost"]
    )
    return no_worse and strictly_better

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]
    for path_key, sha_key in [
        ("question_frontier_path", "question_frontier_blob_sha"),
        ("question_metabolism_path", "question_metabolism_blob_sha"),
        ("local_census_path", "local_census_blob_sha"),
        ("human_dependency_census_path", "human_dependency_census_blob_sha")
    ]:
        if git_blob(src[path_key]) != src[sha_key]:
            fail("FAIL_SOURCE_BIND:" + src[path_key])

    frontier_doc = json.loads(Path(src["question_frontier_path"]).read_text(encoding="utf-8"))
    valid_qids = {q for ids in frontier_doc["categories"].values() for q in ids}

    candidates = d["candidates"]
    if len({c["id"] for c in candidates}) != len(candidates):
        fail("FAIL_DUPLICATE_CANDIDATE_ID")
    if any(c["frontier_question_id"] not in valid_qids for c in candidates):
        fail("FAIL_UNKNOWN_FRONTIER_QUESTION")

    got_eligible = sorted(c["id"] for c in candidates if eligible(c))
    if got_eligible != sorted(d["expected"]["eligible_ids"]):
        fail("FAIL_ELIGIBLE_SET:" + json.dumps(got_eligible))

    for c in candidates:
        if eligible(c) != c["expected_eligible"]:
            fail("FAIL_ELIGIBILITY_EXPECTATION:" + c["id"])

    elig = [c for c in candidates if eligible(c)]
    pareto = []
    for c in elig:
        if not any(dominates(other, c) for other in elig if other["id"] != c["id"]):
            pareto.append(c)

    got_pareto = sorted(c["id"] for c in pareto)
    if got_pareto != sorted(d["expected"]["pareto_frontier_ids"]):
        fail("FAIL_PARETO_SET:" + json.dumps(got_pareto))

    min_cost = min(c["proof_cost"] for c in pareto)
    cheapest = [c for c in pareto if c["proof_cost"] == min_cost]
    max_false_completion = max(c["false_completion_detection"] for c in cheapest)
    finalists = [c for c in cheapest if c["false_completion_detection"] == max_false_completion]
    elected = sorted(finalists, key=lambda c: c["id"])[0]

    if elected["id"] != d["expected"]["elected_next_proof_id"]:
        fail("FAIL_ELECTED_NEXT_PROOF:" + elected["id"])

    if d["expected"]["runtime_effect"] is not False or d["expected"]["public_effect"] is not False:
        fail("FAIL_EFFECT_BOUNDARY")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    out = {
        "STATE": "PASS_COINQUIRY_COMPILER_R0F",
        "checked_out_head_sha": head,
        "candidate_count": len(candidates),
        "eligible_count": len(elig),
        "eligible_ids": got_eligible,
        "pareto_frontier_ids": got_pareto,
        "elected_next_proof_id": elected["id"],
        "elected_frontier_question_id": elected["frontier_question_id"],
        "elected_receiver": elected["receiver"],
        "elected_bounded_probe": elected["bounded_probe"],
        "elected_negative_evidence": elected["negative_evidence"],
        "elected_retirement_condition": elected["retirement_condition"],
        "runtime_effect": False,
        "public_effect": False,
        "rails": d["rails"]
    }
    print(json.dumps(out, separators=(",", ":")))

if __name__ == "__main__":
    main()
