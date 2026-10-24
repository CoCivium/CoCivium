#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

P = Path("fixtures/relations/coinquiry_recompile_r0l.json")

def fail(code):
    raise SystemExit(code)

def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()

def eligible(c, resolved_id):
    if c["id"] == resolved_id:
        return False
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
    highs = [
        "retirement_leverage",
        "dependency_reduction",
        "human_attention_reduction",
        "false_completion_detection",
    ]
    no_worse = all(a[k] >= b[k] for k in highs) and a["proof_cost"] <= b["proof_cost"]
    strictly = any(a[k] > b[k] for k in highs) or a["proof_cost"] < b["proof_cost"]
    return no_worse and strictly

def main():
    cfg = json.loads(P.read_text(encoding="utf-8"))
    src = cfg["source_bindings"]

    for path_key, sha_key in [
        ("inquiry_compiler_path", "inquiry_compiler_blob_sha"),
        ("pickup_gap_disposition_path", "pickup_gap_disposition_blob_sha"),
    ]:
        if git_blob(src[path_key]) != src[sha_key]:
            fail("FAIL_SOURCE_BIND:" + src[path_key])

    inquiry = json.loads(Path(src["inquiry_compiler_path"]).read_text(encoding="utf-8"))
    disp = json.loads(Path(src["pickup_gap_disposition_path"]).read_text(encoding="utf-8"))

    resolved = cfg["resolved_question"]
    if len(disp["gaps"]) != resolved["sampled_gap_count"]:
        fail("FAIL_RESOLVED_GAP_COUNT")
    blockers = sum(int(x["current_blocker"]) for x in disp["gaps"])
    if blockers != resolved["required_current_blocker_count"]:
        fail("FAIL_CURRENT_BLOCKERS")
    if disp["direct_pickup_retroactively_inferred"] is not False:
        fail("FAIL_RETROACTIVE_PICKUP")
    if resolved["global_census_complete"] is not False:
        fail("FAIL_GLOBAL_CENSUS_OVERCLAIM")

    candidates = inquiry["candidates"]
    active = [c for c in candidates if eligible(c, resolved["id"])]
    active_ids = sorted(c["id"] for c in active)

    frontier = []
    for c in active:
        if not any(dominates(other, c) for other in active if other["id"] != c["id"]):
            frontier.append(c)
    frontier_ids = sorted(c["id"] for c in frontier)

    expected = cfg["expected"]
    if active_ids != sorted(expected["eligible_ids"]):
        fail("FAIL_ELIGIBLE:" + ",".join(active_ids))
    if frontier_ids != sorted(expected["pareto_frontier_ids"]):
        fail("FAIL_FRONTIER:" + ",".join(frontier_ids))

    elected = sorted(
        frontier,
        key=lambda c: (
            c["proof_cost"],
            -c["false_completion_detection"],
            c["id"],
        ),
    )[0]

    if elected["id"] != expected["elected_next_proof_id"]:
        fail("FAIL_ELECTION:" + elected["id"])
    if elected["receiver"] != expected["elected_receiver"]:
        fail("FAIL_RECEIVER:" + elected["receiver"])
    if expected["runtime_effect"] or expected["public_effect"]:
        fail("FAIL_EFFECT_BOUNDARY")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({
        "STATE": "PASS_COINQUIRY_RECOMPILE_AFTER_Q07_R0L",
        "checked_out_head_sha": head,
        "resolved_question_id": resolved["id"],
        "resolved_sampled_gap_count": len(disp["gaps"]),
        "current_blocker_count": blockers,
        "eligible_ids": active_ids,
        "pareto_frontier_ids": frontier_ids,
        "elected_next_proof_id": elected["id"],
        "elected_receiver": elected["receiver"],
        "elected_bounded_probe": elected["bounded_probe"],
        "runtime_effect": False,
        "public_effect": False
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
