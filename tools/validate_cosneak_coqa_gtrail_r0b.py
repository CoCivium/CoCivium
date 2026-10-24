#!/usr/bin/env python3
import collections
import json
import subprocess
from pathlib import Path

P = Path("fixtures/relations/cosneak_coqa_gtrail_r0b.json")

def fail(code):
    raise SystemExit(code)

def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()

def elect_trail(q):
    if not q["durable"]:
        return "NONE"
    if q["authority_or_effect_impact"] or q["risk"] == "HIGH":
        return "FORENSIC"
    if q["reopened"] or q["time_sensitive"] or q["disputed"]:
        return "DEEP"
    if q["edge_count"] >= 4 or q["risk"] == "MEDIUM":
        return "STANDARD"
    return "LIGHT"

def recurs(q):
    return q["expected_loop_mode"] in {
        "OPTIONAL_NEXT_QUESTION",
        "WAKE_ON_EVIDENCE_REOPEN",
        "HOLD_UNTIL_AUTHORITY_RESOLVED"
    }

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]
    for path_key, sha_key in [
        ("coqa_doc_path", "coqa_doc_blob_sha"),
        ("coqa_schema_path", "coqa_schema_blob_sha"),
        ("cosneak_r0_path", "cosneak_r0_blob_sha"),
        ("local_census_path", "local_census_blob_sha")
    ]:
        if git_blob(src[path_key]) != src[sha_key]:
            fail("FAIL_SOURCE_BIND:" + src[path_key])

    dist = collections.Counter()
    recur = 0
    for q in d["qa_objects"]:
        got = elect_trail(q)
        if got != q["expected_trail"]:
            fail("FAIL_TRAIL_ELECTION:" + q["id"] + ":" + got)
        if q["durable"] and got == "NONE":
            fail("FAIL_DURABLE_WITHOUT_MIN_TRAIL:" + q["id"])
        dist[got] += 1
        recur += int(recurs(q))

    if dict(dist) != d["expected"]["trail_distribution"]:
        fail("FAIL_TRAIL_DISTRIBUTION")
    if recur != d["expected"]["qa_objects_with_recurrence"]:
        fail("FAIL_RECURRENCE_COUNT")
    if len(d["qa_objects"]) - recur != d["expected"]["qa_objects_without_recurrence"]:
        fail("FAIL_NO_RECURRENCE_COUNT")

    qp = d["qa_loop_policy"]
    if qp["every_qa_must_loop"] is not False:
        fail("FAIL_FORCED_QA_LOOP")
    if qp["semantic_loop_requires_graph_cycle"] is not False:
        fail("FAIL_GRAPH_CYCLE_REQUIRED")
    if qp["reopen_requires_material_delta_or_explicit_receiver_request"] is not True:
        fail("FAIL_REOPEN_GATE")

    gp = d["gtrail_policy"]
    if gp["adaptive_levels"] != ["NONE", "LIGHT", "STANDARD", "DEEP", "FORENSIC"]:
        fail("FAIL_GTRAIL_LEVELS")
    if gp["default_everything_forensic"] is not False:
        fail("FAIL_EVERYTHING_FORENSIC")
    if gp["trail_overhead_is_free"] is not False:
        fail("FAIL_TRAIL_OVERHEAD_FREE")
    if gp["trace_implies_truth"] is not False or gp["path_implies_causation"] is not False:
        fail("FAIL_TRACE_EPISTEMIC_OVERCLAIM")

    signals = d["sneak_signals"]
    if len(signals) != d["expected"]["sneak_signals_generate_diagnostic_questions"]:
        fail("FAIL_SIGNAL_COUNT")
    if any(not s["diagnostic_question"].strip() for s in signals):
        fail("FAIL_EMPTY_DIAGNOSTIC_QUESTION")
    if sum(int(s["causal_proof"]) for s in signals) != d["expected"]["sneak_signals_with_causal_proof"]:
        fail("FAIL_CAUSAL_PROOF_OVERCLAIM")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({
        "STATE": "PASS_COSNEAK_COQA_GTRAIL_ADAPTIVE_TRACE_R0B",
        "checked_out_head_sha": head,
        "trail_distribution": dict(dist),
        "qa_objects_with_recurrence": recur,
        "qa_objects_without_recurrence": len(d["qa_objects"]) - recur,
        "diagnostic_question_count": len(signals),
        "causal_blocker_proven_count": 0
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
