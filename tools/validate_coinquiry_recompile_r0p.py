#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

P = Path("fixtures/relations/coinquiry_recompile_r0p.json")

def fail(code):
    raise SystemExit(code)

def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]

    for path_key, sha_key in [
        ("inquiry_compiler_path", "inquiry_compiler_blob_sha"),
        ("post_q10_recompile_path", "post_q10_recompile_blob_sha"),
        ("q14_audit_path", "q14_audit_blob_sha")
    ]:
        actual = git_blob(src[path_key])
        if actual != src[sha_key]:
            fail("FAIL_SOURCE_BIND:" + src[path_key] + ":" + actual)

    compiler = json.loads(Path(src["inquiry_compiler_path"]).read_text(encoding="utf-8"))
    q14 = json.loads(Path(src["q14_audit_path"]).read_text(encoding="utf-8"))

    if q14["sampled_scope_closed"] is not True:
        fail("FAIL_Q14_SCOPE_NOT_CLOSED")
    if q14["global_resilience_proven"] is not False:
        fail("FAIL_Q14_GLOBAL_OVERCLAIM")
    if q14["totals"]["cross_failure_domain_independence_proven"] != 0:
        fail("FAIL_Q14_UNEXPECTED_INDEPENDENCE_PROOF")

    resolved = {x["id"] for x in d["resolved_questions"]}
    if resolved != {
        "Q07_PASS_WITHOUT_PICKUP",
        "Q10_HUMAN_RELAY_DEPENDENCY",
        "Q14_FALSE_FAILURE_DOMAIN_DIVERSITY"
    }:
        fail("FAIL_RESOLVED_SET")

    candidates = {x["id"]: x for x in compiler["candidates"]}
    active = []
    for qid, c in candidates.items():
        if qid in resolved:
            continue
        eligible = (
            bool(c["receiver"])
            and bool(c["bounded_probe"])
            and c["evidence_surface_available"] is True
            and c["authority_conflict"] is False
            and c["already_resolved"] is False
            and bool(c["negative_evidence"])
            and bool(c["retirement_condition"])
        )
        if eligible:
            active.append(qid)

    if sorted(active) != sorted(d["expected"]["eligible_ids"]):
        fail("FAIL_ELIGIBLE_SET:" + ",".join(sorted(active)))

    if active != ["Q40_COMPILE_RECURRING_DEED_LOCAL"]:
        fail("FAIL_EXPECTED_SINGLE_FRONTIER")

    q40 = candidates["Q40_COMPILE_RECURRING_DEED_LOCAL"]
    exp = d["expected"]
    if exp["elected_next_proof_id"] != q40["id"]:
        fail("FAIL_ELECTED_ID")
    if exp["elected_receiver"] != q40["receiver"]:
        fail("FAIL_ELECTED_RECEIVER")
    if exp["elected_probe"] != q40["bounded_probe"]:
        fail("FAIL_ELECTED_PROBE")
    if exp["negative_evidence"] != q40["negative_evidence"]:
        fail("FAIL_NEGATIVE_EVIDENCE")
    if exp["retirement_condition"] != q40["retirement_condition"]:
        fail("FAIL_RETIREMENT_CONDITION")
    if exp["runtime_effect"] or exp["public_effect"]:
        fail("FAIL_EFFECT_BOUNDARY")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({
        "STATE": "PASS_POST_Q14_INQUIRY_RECOMPILE_R0P",
        "checked_out_head_sha": head,
        "resolved_sampled_questions": sorted(resolved),
        "active_eligible_ids": active,
        "pareto_frontier_ids": d["expected"]["pareto_frontier_ids"],
        "elected_next_proof_id": exp["elected_next_proof_id"],
        "elected_receiver": exp["elected_receiver"],
        "runtime_effect": False,
        "public_effect": False
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
