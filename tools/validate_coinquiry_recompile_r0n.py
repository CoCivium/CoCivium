#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

P = Path("fixtures/relations/coinquiry_recompile_r0n.json")

def fail(code):
    raise SystemExit(code)

def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()

def gate(c):
    return (
        bool(c.get("receiver"))
        and bool(c.get("bounded_probe"))
        and c.get("evidence_surface_available") is True
        and c.get("authority_conflict") is False
        and c.get("already_resolved") is False
        and bool(c.get("negative_evidence"))
        and bool(c.get("retirement_condition"))
    )

def dominates(a, b):
    dims_hi = ["retirement_leverage", "dependency_reduction", "human_attention_reduction", "false_completion_detection"]
    no_worse = all(a[k] >= b[k] for k in dims_hi) and a["proof_cost"] <= b["proof_cost"]
    strictly = any(a[k] > b[k] for k in dims_hi) or a["proof_cost"] < b["proof_cost"]
    return no_worse and strictly

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]

    for path_key, sha_key in [
        ("inquiry_compiler_path", "inquiry_compiler_blob_sha"),
        ("post_q07_recompile_path", "post_q07_recompile_blob_sha"),
        ("q10_live_use_trace_path", "q10_live_use_trace_blob_sha")
    ]:
        if git_blob(src[path_key]) != src[sha_key]:
            fail("FAIL_SOURCE_BIND:" + src[path_key])

    r0f = json.loads(Path(src["inquiry_compiler_path"]).read_text(encoding="utf-8"))
    r0l = json.loads(Path(src["post_q07_recompile_path"]).read_text(encoding="utf-8"))
    r0m = json.loads(Path(src["q10_live_use_trace_path"]).read_text(encoding="utf-8"))

    if r0l["resolved_question"]["id"] != "Q07_PASS_WITHOUT_PICKUP":
        fail("FAIL_Q07_BIND")
    if r0m["sampled_scope_closed"] is not True:
        fail("FAIL_Q10_SCOPE_NOT_CLOSED")
    if r0m["global_census_complete"] is not False:
        fail("FAIL_Q10_GLOBAL_OVERCLAIM")
    if r0m["totals"]["proven_live_human_relay_dependencies"] != 0:
        fail("FAIL_Q10_LIVE_DEP_COUNT")

    resolved = {x["id"] for x in d["resolved_questions"]}
    candidates = [c for c in r0f["candidates"] if c["id"] not in resolved]
    eligible = [c for c in candidates if gate(c)]
    eligible_ids = sorted(c["id"] for c in eligible)

    expected_eligible = sorted(d["expected"]["eligible_ids"])
    if eligible_ids != expected_eligible:
        fail("FAIL_ELIGIBLE:" + json.dumps(eligible_ids))

    frontier = []
    for c in eligible:
        if not any(dominates(other, c) for other in eligible if other["id"] != c["id"]):
            frontier.append(c)
    frontier_ids = sorted(c["id"] for c in frontier)

    if frontier_ids != sorted(d["expected"]["pareto_frontier_ids"]):
        fail("FAIL_PARETO:" + json.dumps(frontier_ids))

    elected = sorted(
        frontier,
        key=lambda c: (
            c["proof_cost"],
            -c["false_completion_detection"],
            c["id"]
        )
    )[0]

    exp = d["expected"]
    if elected["id"] != exp["elected_next_proof_id"]:
        fail("FAIL_ELECTION:" + elected["id"])
    if elected["receiver"] != exp["elected_receiver"]:
        fail("FAIL_RECEIVER")
    if elected["bounded_probe"] != exp["elected_probe"]:
        fail("FAIL_PROBE")
    if exp["runtime_effect"] or exp["public_effect"]:
        fail("FAIL_EFFECT_BOUNDARY")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({
        "STATE": "PASS_COINQUIRY_RECOMPILE_AFTER_Q10_R0N",
        "checked_out_head_sha": head,
        "resolved_ids": sorted(resolved),
        "eligible_ids": eligible_ids,
        "pareto_frontier_ids": frontier_ids,
        "elected_next_proof_id": elected["id"],
        "elected_receiver": elected["receiver"],
        "elected_probe": elected["bounded_probe"],
        "runtime_effect": False,
        "public_effect": False
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
