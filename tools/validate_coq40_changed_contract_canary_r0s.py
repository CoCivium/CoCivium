#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

P = Path("fixtures/relations/coq40_changed_contract_canary_r0s.json")


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
        np = contract["next_probe"]
        for field in np["required_fields"]:
            value = probe.get(field)
            if not isinstance(value, str) or not value.strip():
                reasons.append("NEXT_PROBE_FIELD_MISSING:" + field)
        if probe.get("kind") not in np["allowed_kinds"]:
            reasons.append("NEXT_PROBE_KIND_NOT_ALLOWED")
    return len(reasons) == 0, reasons


def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]

    if git_blob(src["r0q_path"]) != src["r0q_blob_sha"]:
        fail("FAIL_R0Q_SOURCE_BIND")
    if git_blob(src["r0r_path"]) != src["r0r_blob_sha"]:
        fail("FAIL_R0R_SOURCE_BIND")

    r0q = json.loads(Path(src["r0q_path"]).read_text(encoding="utf-8"))
    r0r = json.loads(Path(src["r0r_path"]).read_text(encoding="utf-8"))

    prior_actual = r0q["attempts"][1]["output"]
    if isinstance(prior_actual.get("next_probe"), dict):
        fail("FAIL_PRIOR_REJECTION_REASON_DRIFT")

    cc = d["changed_output_contract"]
    r0r_contract = r0r["semantic_contract"]
    if cc["allowed_actions"] != r0r_contract["allowed_actions"]:
        fail("FAIL_ALLOWED_ACTION_DRIFT")
    if cc["required_nonclaim"] != r0r_contract["required_nonclaim"]:
        fail("FAIL_NONCLAIM_DRIFT")
    if cc["next_probe"]["required_fields"] != r0r_contract["required_next_probe_fields"]:
        fail("FAIL_PROBE_FIELDS_DRIFT")
    if cc["next_probe"]["allowed_kinds"] != r0r_contract["allowed_probe_kinds"]:
        fail("FAIL_PROBE_KIND_DRIFT")

    accepted, reasons = assess(d["positive_control"], cc)
    if not accepted or reasons:
        fail("FAIL_POSITIVE_CONTROL:" + json.dumps(reasons))

    route = d["target_route"]
    if route["persistent_worker_install_allowed"] is not False:
        fail("FAIL_PERSISTENT_WORKER_AUTHORITY")
    if route["model_pull_or_install_allowed"] is not False:
        fail("FAIL_MODEL_INSTALL_AUTHORITY")
    if route["max_changed_contract_attempts"] != 1:
        fail("FAIL_RETRY_BUDGET")

    if d["local_attempt"] is not None:
        fail("FAIL_LOCAL_EXECUTION_OVERCLAIM")

    exp = d["expected"]
    if exp["actual_local_changed_contract_attempt_executed"] is not False:
        fail("FAIL_EXECUTION_EXPECTATION")
    if exp["actual_local_output_semantically_accepted"] is not False:
        fail("FAIL_ACCEPTANCE_OVERCLAIM")
    if exp["q40_full_semantic_acceptance_proven"] is not False:
        fail("FAIL_Q40_CLOSURE_OVERCLAIM")
    if exp["persistent_worker_installed"] or exp["provider_route_disabled"]:
        fail("FAIL_RUNTIME_AUTHORITY_OVERCLAIM")
    if exp["runtime_effect"] or exp["public_effect"]:
        fail("FAIL_EFFECT_OVERCLAIM")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({
        "STATE": "PASS_Q40_CHANGED_CONTRACT_PREPARATION_R0S",
        "checked_out_head_sha": head,
        "contract_compiles": True,
        "positive_control_semantically_accepted": True,
        "actual_local_changed_contract_attempt_executed": False,
        "actual_local_output_semantically_accepted": False,
        "q40_full_semantic_acceptance_proven": False,
        "max_changed_contract_attempts": 1,
        "runtime_effect": False,
        "public_effect": False,
        "next_gate": d["next_gate"]["action"]
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
