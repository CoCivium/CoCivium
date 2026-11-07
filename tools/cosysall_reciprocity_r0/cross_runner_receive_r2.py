#!/usr/bin/env python3
"""R2: replay a producer's source-pinned receipt on a separate, fresh CI runner.

Scope: same GitHub service, independent job/runner; NOT an independent AI
reader, provider failure domain, elapsed cold restart, or semantics oracle.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from full_source_replay_r1 import run

SOURCE_GIT_BLOB = "9cc47926d2f61f439db1818702127382f78d693f"
TRUST_STATE = "PASS_FOR_SOURCE_PINNED_LOCAL_CI_ONLY"
EXPECTED_AUTHORITY = "NO_EXTERNAL_EFFECTS__REVIEW_ONLY"

def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def check_receipt(producer_bytes: bytes, replay_bytes: bytes) -> list[str]:
    problems = []
    try:
        producer = json.loads(producer_bytes)
        replay = json.loads(replay_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return ["NOT_VALID_JSON"]
    if not isinstance(producer, dict) or not isinstance(replay, dict):
        return ["NOT_RECEIPT_OBJECT"]
    if producer_bytes != replay_bytes:
        problems.append("NOT_BYTE_IDENTICAL_REPLAY")
    for label, obj in [("PRODUCER", producer), ("RECEIVER", replay)]:
        if obj.get("qualified_git_blob") != SOURCE_GIT_BLOB:
            problems.append(label + "_SOURCE_BLOB_DRIFT")
        if obj.get("status") != TRUST_STATE:
            problems.append(label + "_UNJUSTIFIED_STATUS")
        if obj.get("source_nodes") != 56 or obj.get("source_edges") != 61:
            problems.append(label + "_SOURCE_SHAPE_DRIFT")
        if obj.get("identical_claim_digests") is not True:
            problems.append(label + "_CLAIM_PARITY_UNPROVEN")
        if not all(obj.get("negative_controls", {}).get(k) is True for k in
                   ("reversed_edge_held", "forged_permission_held")):
            problems.append(label + "_NEGATIVE_CONTROL_LOST")
        candidate = obj.get("candidate", {})
        if (not isinstance(candidate, dict)
            or candidate.get("mutation_class") != "PROPOSE"
            or candidate.get("epistemic_class") != "HYPOTHESIS"
            or candidate.get("authority_ceiling") != EXPECTED_AUTHORITY):
            problems.append(label + "_FALSE_AUTHORITY")
        if obj.get("actual_remote_effects") != 0 or obj.get("independent_reader_ack") != "NOT_OBSERVED":
            problems.append(label + "_FALSE_EXTERNAL_EFFECT_OR_ACK")
    return sorted(set(problems))

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--producer", type=Path, required=True)
    p.add_argument("--graph", type=Path, required=True)
    p.add_argument("--schema", type=Path, required=True)
    p.add_argument("--receipt", type=Path, required=True)
    p.add_argument("--run-id", required=True)
    args = p.parse_args()
    if args.receipt.exists():
        raise SystemExit("HOLD: receiver proof path already exists; no clobber")
    original = args.producer.read_bytes()
    with TemporaryDirectory(prefix="cosysall-r2-receiver-") as directory:
        replay_path = Path(directory) / "fresh-runner-replay.json"
        run(args.graph, args.schema, replay_path)
        fresh = replay_path.read_bytes()
    problems = check_receipt(original, fresh)
    # Two mutations must be rejected by the same verifier, not accepted as
    # a plausible alternate successor.
    swapped = copy.deepcopy(json.loads(original))
    swapped["registered_example_edges"][0]["from"] = "repo:CoCivium/MasterPlan"
    reversed_held = bool(check_receipt(json.dumps(swapped).encode(), fresh))
    forged = copy.deepcopy(json.loads(original))
    forged["candidate"]["authority_ceiling"] = "ALLOW_ALL"
    forged_held = bool(check_receipt(json.dumps(forged).encode(), fresh))
    if not reversed_held or not forged_held:
        problems.append("ADVERSARIAL_REPLAY_CHECK_FAILED")
    result = {
        "schema": "CoSysAll.SeparateRunnerReadproof.R2",
        "status": "PASS_SAME_PROVIDER_FRESH_RUNNER" if not problems else "HOLD_RECEIVER_VERIFICATION",
        "run_id": str(args.run_id),
        "producer_receipt_sha256": sha256(original),
        "fresh_replay_sha256": sha256(fresh),
        "byte_identical": original == fresh,
        "source_git_blob": SOURCE_GIT_BLOB,
        "source_graph_sha256": json.loads(fresh).get("canonical_graph_sha256"),
        "negative_canaries": {"altered_edge_rejected": reversed_held, "forged_authority_rejected": forged_held},
        "problems": problems,
        "receiver_scope": "FRESH_GITHUB_ACTIONS_JOB_NEW_WORKSPACE_SAME_PROVIDER",
        "external_actions": 0,
        "human_reader_ack": "NOT_OBSERVED",
        "cross_provider_recovery": "NOT_TESTED",
        "elapsed_24h_recovery": "NOT_TESTED",
        "x2_runtime": "NOT_OBSERVED",
        "public_coex_canon": "NOT_CLAIMED",
    }
    with args.receipt.open("x", encoding="utf-8") as out:
        out.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if problems:
        raise SystemExit("HOLD: " + ", ".join(problems))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
