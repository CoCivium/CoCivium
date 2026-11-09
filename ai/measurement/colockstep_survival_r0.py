#!/usr/bin/env python3
"""CoLockStep R0: source-pinned, synthetic known-green capability survival.

The previously CI-green CoMeasure source is snapshotted to an isolated temp
directory. An experimental copy receives one deliberate, invalid centimetre
scale mutation. A passing FIRST-USE demo is insufficient to promote it if its
independent registry verifier rejects it. Replaying the untouched baseline
must still work in ordinary and optimized Python.

No live worker control, release promotion, operator ACK, X2 access, or persistent
receipt. This tests only one temporary Python execution failure domain.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

BASE = Path(__file__).resolve().parent
FROZEN_GIT_BLOBS = {
    "registry_r0_1.json": "d66132c8773c825a7944107d32b3827254178bcf",
    "verify_registry_r0_1.py": "3c8427c20d5d491020b94b5159e6a69589d776ad",
    "observation_domain_r0.py": "0e85a0bb923bfd7e7c24640d9b0ab773a4b13088",
    "first_use_demo_r0.py": "3a468ddb2fb455b998de5da9453bf191437f9337",
}
PINNED_CODE_HEAD = "797872ac91f5b1a19e43d1ccc972a745561337d4"


def require(ok, reason):
    if not ok:
        raise RuntimeError("HOLD_COLOCKSTEP_R0: " + reason)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(data):
    return hashlib.sha1(("blob " + str(len(data)) + "\0").encode("ascii") + data).hexdigest()


def check_source_pins():
    hashes = {}
    for filename, blob in FROZEN_GIT_BLOBS.items():
        source = BASE / filename
        require(source.is_file(), "SOURCE_MISSING_" + filename)
        data = source.read_bytes()
        require(git_blob_sha1(data) == blob, "FROZEN_SOURCE_DRIFT_" + filename)
        hashes[filename] = hashlib.sha256(data).hexdigest()
    return hashes


def run_python(directory, filename, optimized):
    args = [sys.executable, "-E", "-s"]
    if optimized:
        args.append("-O")
    args.extend(["-B", str(directory / filename)])
    try:
        completed = subprocess.run(args, cwd=directory, capture_output=True,
                                   text=True, timeout=20, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("HOLD_COLOCKSTEP_R0: CHILD_TIMEOUT_" + filename) from exc
    return completed


def check_demo(directory, optimized, expected_registry_sha):
    child = run_python(directory, "first_use_demo_r0.py", optimized)
    require(child.returncode == 0, "DEMO_FAILED_" + child.stderr[-350:])
    try:
        result = json.loads(child.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("HOLD_COLOCKSTEP_R0: INVALID_DEMO_RESULT") from exc
    require(result.get("scope") == "SYNTHETIC_DOMAIN_DEMO_ONLY",
            "UNEXPECTED_DEMO_SCOPE")
    require(result.get("passed") == 8 and result.get("total") == 8,
            "DEMO_CASE_COUNT_OR_FAILURE")
    require(result.get("registry_sha256") == expected_registry_sha,
            "DEMO_REGISTRY_NOT_SAME_SOURCE")
    return result


def check_verifier(directory, optimized):
    child = run_python(directory, "verify_registry_r0_1.py", optimized)
    require(child.returncode == 0, "VERIFIER_FAILED_" + child.stderr[-350:])
    try:
        result = json.loads(child.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("HOLD_COLOCKSTEP_R0: INVALID_VERIFIER_RESULT") from exc
    require(result.get("state") == "PASS_FOR_SCOPE" and
            result.get("total_asserted_cases") == 35, "VERIFIER_NOT_QUALIFIED")
    receipt = directory / "registry_test_receipt_r0.json"
    require(receipt.is_file() and sha256(receipt) == result.get("receipt_sha256"),
            "RECEIPT_NOT_EQUAL_TO_READBACK")
    return result


def run_survival():
    before = check_source_pins()
    with tempfile.TemporaryDirectory(prefix="colockstep_r0_") as scratch:
        scratch_path = Path(scratch)
        qualified = scratch_path / "known_green"
        successor = scratch_path / "experimental"
        for folder in (qualified, successor):
            folder.mkdir()
            for filename in FROZEN_GIT_BLOBS:
                shutil.copyfile(BASE / filename, folder / filename)
        require(all(sha256(qualified / name) == val for name, val in before.items()),
                "BASELINE_SNAPSHOT_CHANGED")

        corrupt_file = successor / "registry_r0_1.json"
        original_registry = json.loads(corrupt_file.read_text(encoding="utf-8"))
        units = [u for u in original_registry["units"] if u.get("id") == "cm"]
        require(len(units) == 1 and units[0]["scale_to_anchor"] == "1/100",
                "MUTATION_PRECONDITION_UNMET")
        units[0]["scale_to_anchor"] = "1/10"
        corrupt_file.write_text(json.dumps(original_registry, indent=2) + "\n",
                                encoding="utf-8")
        corrupt_sha = sha256(corrupt_file)
        require(corrupt_sha != before["registry_r0_1.json"],
                "CANDIDATE_NOT_CHANGED")

        outcomes = []
        for optimized in (False, True):
            mode = "python_-O" if optimized else "python_normal"
            # The usable known-green candidate must work before AND after.
            initial_demo = check_demo(
                qualified, optimized, before["registry_r0_1.json"])
            initial_verify = check_verifier(qualified, optimized)
            receipt_sha_before = sha256(qualified / "registry_test_receipt_r0.json")

            # Partial green is deliberately inadequate: first-use tests do
            # not exercise centimetre conversion, but verifier must reject.
            candidate_demo = check_demo(successor, optimized, corrupt_sha)
            failed_verifier = run_python(successor, "verify_registry_r0_1.py",
                                         optimized)
            require(failed_verifier.returncode != 0,
                    "FALSE_GREEN_CANDIDATE_VERIFIER_" + mode)
            require("centimetre" in failed_verifier.stderr,
                    "CANDIDATE_FAILED_FOR_WRONG_REASON_" + mode)
            require(not (successor / "registry_test_receipt_r0.json").exists(),
                    "BAD_CANDIDATE_ISSUED_SUCCESS_RECEIPT")

            replay_demo = check_demo(
                qualified, optimized, before["registry_r0_1.json"])
            replay_verify = check_verifier(qualified, optimized)
            require(replay_demo["cases"] == initial_demo["cases"],
                    "BASELINE_BEHAVIOUR_REGRESSED_" + mode)
            require(replay_verify["registry_sha256"] == initial_verify["registry_sha256"],
                    "BASELINE_REGISTRY_CHANGED_" + mode)
            require(sha256(qualified / "registry_test_receipt_r0.json")
                    == receipt_sha_before, "BASELINE_RECEIPT_CLOBBERED_" + mode)
            require(all(sha256(qualified / name) == val for name, val in before.items()),
                    "BASELINE_SOURCE_MUTATED_" + mode)
            outcomes.append({
                "mode": mode, "baseline_demo_passed_before_and_after": 8,
                "baseline_registry_asserted_cases_before_and_after": 35,
                "candidate_demo_partial_green": candidate_demo["passed"] == 8,
                "candidate_verifier_rejected": True,
                "candidate_success_receipt_written": False,
                "baseline_receipt_unchanged": True,
                "promoted_successor": False,
            })
    require(check_source_pins() == before, "PUBLIC_WORKTREE_WAS_MODIFIED")
    return {
        "schema": "CoAll.CoLockStep.CandidateSurvivalR0",
        "status": "PASS_FOR_SYNTHETIC_SCOPE",
        "baseline_maturity": "REPRODUCIBLE_ONLY_NOT_QUALIFIED_MVP",
        "source_commit_reference": PINNED_CODE_HEAD,
        "frozen_git_blobs_sha1": FROZEN_GIT_BLOBS,
        "source_sha256": before,
        "fault_injected": "experimental_cm.scale_to_anchor:1/100_to_1/10",
        "same_failure_domain": True,
        "outcomes": outcomes,
        "effects": {"public_writes": 0, "network_calls": 0,
                    "original_source_changes": 0, "real_receiver_actions": 0},
        "next_gate": "independent receiver-origin accepted useful task and crash/recovery test",
        "nonclaims": [
            "NOT_PRODUCTION_STABILITY", "NOT_MVP_ACCEPTANCE",
            "NOT_CROSS_FAILURE_DOMAIN", "NOT_RECEIVER_ACK",
            "NOT_RUNTIME_FAILOVER", "NOT_RELEASE_OR_CANON",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run_survival(), indent=2, sort_keys=True))
