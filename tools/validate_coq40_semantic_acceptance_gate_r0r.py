#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

P = Path("fixtures/relations/coq40_semantic_acceptance_gate_r0r.json")


def fail(code):
    raise SystemExit(code)


def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()


def assess(candidate, contract):
    reasons = []
    if candidate.get("action") not in contract["allowed_actions"]:
        reasons.append("ACTION_NOT_ALLOWED")
    if candidate.get("nonclaim") != contract["required_nonclaim"]:
        reasons.append("REQUIRED_NONCLAIM_MISSING_OR_CHANGED")
    reason = candidate.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        reasons.append("REASON_MISSING")

    probe = candidate.get("next_probe")
    if not isinstance(probe, dict):
        reasons.append("NEXT_PROBE_NOT_STRUCTURED")
    else:
        for field in contract["required_next_probe_fields"]:
            value = probe.get(field)
            if not isinstance(value, str) or not value.strip():
                reasons.append("NEXT_PROBE_FIELD_MISSING:" + field)
        if probe.get("kind") not in contract["allowed_probe_kinds"]:
            reasons.append("NEXT_PROBE_KIND_NOT_ALLOWED")
    return len(reasons) == 0, reasons


def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]

    if git_blob(src["q40_canary_path"]) != src["q40_canary_blob_sha"]:
        fail("FAIL_Q40_SOURCE_BIND")
    if git_blob(src["post_q14_recompile_path"]) != src["post_q14_recompile_blob_sha"]:
        fail("FAIL_R0P_SOURCE_BIND")

    q40 = json.loads(Path(src["q40_canary_path"]).read_text(encoding="utf-8"))
    actual = q40["attempts"][1]["output"]
    if actual != d["cases"][0]["candidate"]:
        fail("FAIL_ACTUAL_R0Q_OUTPUT_DRIFT")

    accepted = 0
    rejected = 0
    observed = []
    for case in d["cases"]:
        got_accept, got_reasons = assess(case["candidate"], d["semantic_contract"])
        exp = case["expected"]
        if got_accept is not exp["accepted"]:
            fail("FAIL_ACCEPTANCE:" + case["id"])
        if got_reasons != exp["reasons"]:
            fail("FAIL_REASONS:" + case["id"] + ":" + json.dumps(got_reasons))
        accepted += int(got_accept)
        rejected += int(not got_accept)
        observed.append({
            "id": case["id"],
            "accepted": got_accept,
            "reasons": got_reasons
        })

    exp = d["expected"]
    if len(d["cases"]) != exp["case_count"]:
        fail("FAIL_CASE_COUNT")
    if accepted != exp["accepted_count"] or rejected != exp["rejected_count"]:
        fail("FAIL_ACCEPT_REJECT_COUNTS")
    if observed[0]["accepted"] is not exp["actual_r0q_output_accepted"]:
        fail("FAIL_ACTUAL_ACCEPTANCE")
    if exp["local_model_retry_authorized"] is not False:
        fail("FAIL_RETRY_AUTHORITY_OVERCLAIM")
    if exp["q40_full_semantic_acceptance_proven"] is not False:
        fail("FAIL_Q40_CLOSURE_OVERCLAIM")
    if exp["runtime_effect"] or exp["public_effect"]:
        fail("FAIL_EFFECT_OVERCLAIM")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({
        "STATE": "PASS_Q40_SEMANTIC_ACCEPTANCE_GATE_R0R",
        "checked_out_head_sha": head,
        "case_count": len(d["cases"]),
        "accepted_count": accepted,
        "rejected_count": rejected,
        "actual_r0q_output_accepted": False,
        "actual_r0q_rejection_reasons": observed[0]["reasons"],
        "compiler_contract_upgrade_required": True,
        "local_model_retry_authorized": False,
        "q40_full_semantic_acceptance_proven": False,
        "runtime_effect": False,
        "public_effect": False
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
