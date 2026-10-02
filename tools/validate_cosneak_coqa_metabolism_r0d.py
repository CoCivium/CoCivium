#!/usr/bin/env python3
import collections
import json
import subprocess
from pathlib import Path

P = Path("fixtures/relations/cosneak_coqa_metabolism_r0d.json")

def fail(code):
    raise SystemExit(code)

def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()

def elect(case):
    if case["authority_conflict"]:
        return "HOLD_AUTHORITY", "FORENSIC", "AUTHORITY_AMBIGUITY"
    if case["question_bundles_independent_decisions"]:
        return "SPLIT_BEFORE_ANSWER", "STANDARD", "BUNDLED_QUESTION_SCOPE"

    state = case["state"]
    has_delta = case["new_evidence_count"] > 0 or case["material_uncertainty_reduction"]

    if state in {"CLOSED_FOR_SCOPE", "STALE", "REOPEN_ON_EVIDENCE"}:
        if has_delta or case["explicit_receiver_request"]:
            trail = "DEEP" if (state == "STALE" or case["active_challenge"] or has_delta) else "STANDARD"
            signal = "STALE_CURRENTNESS" if state == "STALE" else None
            return "REOPEN", trail, signal
        return "PARK", "LIGHT", "QA_RETRY_WITHOUT_NEW_EVIDENCE"

    if (
        state == "PROVISIONALLY_RESOLVED"
        and case["receiver_scope_satisfied"]
        and not case["active_challenge"]
        and case["new_evidence_count"] == 0
    ):
        return "CLOSE_FOR_SCOPE", "LIGHT", None

    if case["trail_cost_exceeds_diagnostic_value"] and not has_delta and not case["active_challenge"]:
        return "COMPACT_AND_PARK", "LIGHT", "TRAIL_INFLATION"

    if case["retry_without_delta_count"] > 0 and not has_delta and not case["active_challenge"] and not case["explicit_receiver_request"]:
        return "PARK", "LIGHT", "QA_RETRY_WITHOUT_NEW_EVIDENCE"

    if has_delta or case["active_challenge"] or case["explicit_receiver_request"]:
        return "CONTINUE", "STANDARD", None

    return "PARK", "LIGHT", "QA_RETRY_WITHOUT_NEW_EVIDENCE"

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]
    for path_key, sha_key in [
        ("coqa_doc_path", "coqa_doc_blob_sha"),
        ("coqa_schema_path", "coqa_schema_blob_sha"),
        ("adaptive_trace_path", "adaptive_trace_blob_sha"),
        ("question_frontier_path", "question_frontier_blob_sha")
    ]:
        if git_blob(src[path_key]) != src[sha_key]:
            fail("FAIL_SOURCE_BIND:" + src[path_key])

    p = d["policy"]
    if p["reopen_requires_material_delta_or_explicit_receiver_request"] is not True:
        fail("FAIL_REOPEN_GATE")
    if p["history_erasure_allowed"] is not False:
        fail("FAIL_HISTORY_ERASURE_ALLOWED")
    if p["parked_object_deleted"] is not False:
        fail("FAIL_PARK_DELETES_OBJECT")
    if p["closed_for_scope_is_global_finality"] is not False:
        fail("FAIL_GLOBAL_FINALITY")

    counts = collections.Counter()
    signal_count = 0
    for case in d["cases"]:
        action, trail, signal = elect(case)
        if action != case["expected_action"]:
            fail("FAIL_ACTION:" + case["id"] + ":" + action)
        if trail != case["expected_trail"]:
            fail("FAIL_TRAIL:" + case["id"] + ":" + trail)
        if signal != case["expected_sneak_signal"]:
            fail("FAIL_SIGNAL:" + case["id"] + ":" + str(signal))
        counts[action] += 1
        signal_count += int(signal is not None)

    exp = d["expected"]
    if len(d["cases"]) != exp["case_count"]:
        fail("FAIL_CASE_COUNT")
    if counts["CONTINUE"] != exp["continue_count"]:
        fail("FAIL_CONTINUE_COUNT")
    if counts["PARK"] + counts["COMPACT_AND_PARK"] != exp["park_or_compact_count"]:
        fail("FAIL_PARK_COUNT")
    if counts["CLOSE_FOR_SCOPE"] != exp["close_for_scope_count"]:
        fail("FAIL_CLOSE_COUNT")
    if counts["REOPEN"] != exp["reopen_count"]:
        fail("FAIL_REOPEN_COUNT")
    if counts["HOLD_AUTHORITY"] != exp["hold_authority_count"]:
        fail("FAIL_HOLD_COUNT")
    if counts["SPLIT_BEFORE_ANSWER"] != exp["split_count"]:
        fail("FAIL_SPLIT_COUNT")
    if signal_count != exp["sneak_signal_count"]:
        fail("FAIL_SIGNAL_COUNT")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({
        "STATE":"PASS_COSNEAK_COQA_QUESTION_METABOLISM_R0D",
        "checked_out_head_sha":head,
        "case_count":len(d["cases"]),
        "action_counts":dict(counts),
        "sneak_signal_count":signal_count,
        "history_erasure_count":0,
        "runtime_mutation":False
    },separators=(",",":")))

if __name__ == "__main__":
    main()
