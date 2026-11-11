#!/usr/bin/env python3
"""CoObject R0: exactly one trusted local read-only worker and cross-job readback.

Source data proposes a schema review; it cannot select executable code.
This adapter is *code-owned*, invokes the EXISTING CoObject vitality
validator, and emits an exact WorkID receipt. No model, network, external
permission, X2, deployment or independent provider receiver is involved.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import sys

if __package__:
    from .CoObjectAgencyBridgeR0 import plan, verified_bytes, Held, require, parse_time
    from .CoObjectVitalityR0 import run as check_vitality
else:
    from CoObjectAgencyBridgeR0 import plan, verified_bytes, Held, require, parse_time
    from CoObjectVitalityR0 import run as check_vitality

POLICY = "ai/vitality/coobject-vitality-policy-r0.json"
FIXTURE = "ai/vitality/coobject-vitality-fixture-r0.json"
CAPABILITY = "CI_TRUSTED_LOCAL_VITALITY_VALIDATOR"
RECEIPT_SCHEMA = "CoObject.OneTaskSourceEffect.R0"
WORK_ID = re.compile(r"^CoObject\.PolicyReview\.[1-9][0-9]*\.a[1-9][0-9]*$")
REV = re.compile(r"^[0-9a-f]{40}$")
SHA = re.compile(r"^[0-9a-f]{64}$")
MAX_RECEIPT = 32768


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def source_sha(root, relative):
    path = (Path(root) / relative)
    require(not path.is_symlink(), "SYMLINK_NOT_ALLOWED")
    require(path.is_file() and path.stat().st_size <= 2_097_152,
            "SOURCE_NOT_BOUNDED_REGULAR")
    return digest(path.read_bytes())


def execute_one(root, work_id, source_head, observed_at,
                *, policy_sha, fixture_sha, capability=CAPABILITY):
    require(isinstance(work_id, str) and WORK_ID.fullmatch(work_id),
            "WORK_ID_NOT_BOUNDED")
    require(isinstance(source_head, str) and REV.fullmatch(source_head),
            "INVALID_SOURCE_HEAD")
    require(capability == CAPABILITY, "UNREGISTERED_CAPABILITY")
    require(isinstance(policy_sha, str) and SHA.fullmatch(policy_sha),
            "INVALID_POLICY_DIGEST")
    require(isinstance(fixture_sha, str) and SHA.fullmatch(fixture_sha),
            "INVALID_FIXTURE_DIGEST")
    timestamp = parse_time(observed_at)
    require(timestamp <= datetime.now(timezone.utc) + timedelta(minutes=2),
            "FUTURE_TASK_TIME")
    root = Path(root).resolve(strict=True)
    policy_path, _, actual_policy = verified_bytes(root, POLICY, policy_sha)
    fixture_path, _, actual_fixture = verified_bytes(root, FIXTURE, fixture_sha)
    obj = {"object_id": "coobject-vitality-policy",
           "relative_path": POLICY, "expected_sha256": actual_policy,
           "lifecycle_state": "ACTIVE_WORKING",
           "known_debt": ["CHECK_EXISTING_VITALITY_CONTRACT"],
           "wake_predicates": []}
    ev = {"object_id": obj["object_id"], "kind": "MATERIAL_REVISION",
          "observed_at": timestamp.isoformat(),
          "observed_sha256": actual_policy, "wake_key": None}
    proposal = plan(root, {"schema": "CoObject.AgencyBridge.R0",
                           "objects": [obj]}, [ev],
                    as_of=timestamp.isoformat())
    require(proposal["eligible_proposals"] == 1
            and proposal["objects"][0]["proposal"] ==
            "REQUEST_SCHEMA_AND_RIGHTS_REVIEW",
            "NO_ELIGIBLE_POLICY_REVIEW")
    # This is the ONLY executable adapter in R0. No dynamic path or
    # agent-provided command can substitute for this implementation.
    try:
        policy = json.loads(policy_path.read_bytes())
        fixture = json.loads(fixture_path.read_bytes())
    except (ValueError, UnicodeDecodeError) as exc:
        raise Held("POLICY_OR_FIXTURE_JSON_INVALID") from exc
    checked = check_vitality(fixture, policy)
    require(checked["object_count"] == 3 and
            checked["state"] ==
            "PASS_THREE_OBJECT_METABOLIC_INTERFACE__EVENT_DRIVEN_HEARTBEAT",
            "EXISTING_VALIDATOR_HELD")
    require(all(v == 0 for v in checked["effects"].values()),
            "UNEXPECTED_EFFECT_CLAIM")
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "state": "TRUSTED_READ_ONLY_VALIDATOR_EXECUTED_IN_CI",
        "work_id": work_id, "source_commit": source_head,
        "event_claim": "SYNTHETIC_PRODUCER_ASSERTED_MATERIAL_REVISION",
        "observed_at": timestamp.isoformat(),
        "policy_sha256": actual_policy,
        "fixture_sha256": actual_fixture,
        "proposal_sha256": proposal["receipt_sha256"],
        "capability": CAPABILITY,
        "validation_result_sha256": digest(canonical(checked)),
        "objects_validated": checked["object_count"],
        "outcome": "LOCAL_FIXTURE_POLICY_CONTRACT_PASS",
        "rights_review": "NOT_PERFORMED",
        "semantic_review": "NOT_PERFORMED",
        "source_effect_class": "READ_ONLY_VALIDATION_RECEIPT",
        "external_effects": 0,
        "model_workers_started": 0,
        "external_receiver_ack": False,
        "native_x2_effect": False,
        "product_mvp_qualified": False,
        "failure_domain": "GITHUB_ACTIONS_ONLY",
    }
    receipt["receipt_sha256"] = digest(canonical(receipt))
    return receipt


def check_readback(root, receipt: dict, *, expected_work_id, expected_source_head):
    require(isinstance(receipt, dict), "RECEIPT_MUST_BE_OBJECT")
    require(receipt.get("schema") == RECEIPT_SCHEMA and
            receipt.get("state") ==
            "TRUSTED_READ_ONLY_VALIDATOR_EXECUTED_IN_CI",
            "RECEIPT_STATE_INVALID")
    require(receipt.get("work_id") == expected_work_id and
            receipt.get("source_commit") == expected_source_head,
            "RECEIPT_WRONG_RUN")
    actual_digest = receipt.get("receipt_sha256")
    require(isinstance(actual_digest, str) and SHA.fullmatch(actual_digest),
            "RECEIPT_DIGEST_INVALID")
    unsigned = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    require(digest(canonical(unsigned)) == actual_digest,
            "RECEIPT_TAMPERED")
    expected = execute_one(root, expected_work_id, expected_source_head,
                           receipt.get("observed_at"),
                           policy_sha=receipt.get("policy_sha256"),
                           fixture_sha=receipt.get("fixture_sha256"))
    require(receipt == expected, "RECEIPT_CONTENT_NOT_REPRODUCIBLE")
    return {
        "state": "SECOND_CI_JOB_RECOMPUTED_SOURCE_AND_VALIDATION",
        "work_id": expected_work_id, "source_commit": expected_source_head,
        "receipt_sha256": actual_digest,
        "receiver_job": "coobject-source-reader",
        "provider_domain": "SAME_GITHUB_ACTIONS",
        "actual_local_validation": True,
        "external_effects": 0, "external_receiver_ack": False,
        "x2_runtime_qualified": False, "mvp_qualified": False
    }


def _read_json(path):
    candidate = Path(path)
    require(candidate.is_file() and not candidate.is_symlink() and
            0 < candidate.stat().st_size <= MAX_RECEIPT,
            "RECEIPT_FILE_NOT_BOUNDED")
    try:
        return json.loads(candidate.read_bytes())
    except (UnicodeDecodeError, ValueError) as exc:
        raise Held("INVALID_RECEIPT_JSON") from exc


def main():
    p = argparse.ArgumentParser(description="CI-only existing CoObject worker")
    p.add_argument("mode", choices=["produce", "readback"])
    p.add_argument("--root", default=".")
    p.add_argument("--receipt", required=True)
    args = p.parse_args()
    env = os.environ
    mode_job = {"produce": "object-task", "readback": "object-source-reader"}
    try:
        require(env.get("GITHUB_ACTIONS") == "true" and
                env.get("GITHUB_JOB") == mode_job[args.mode],
                "CI_JOB_IDENTITY_REQUIRED")
        run_id, attempt, head = (env.get("GITHUB_RUN_ID", ""),
                                 env.get("GITHUB_RUN_ATTEMPT", ""),
                                 env.get("GITHUB_SHA", ""))
        require(bool(re.fullmatch(r"[1-9][0-9]*", run_id)) and
                bool(re.fullmatch(r"[1-9][0-9]*", attempt)) and
                bool(REV.fullmatch(head)), "UNBOUND_GITHUB_RUN")
        work_id = "CoObject.PolicyReview." + run_id + ".a" + attempt
        if args.mode == "produce":
            now = datetime.now(timezone.utc).isoformat()
            output = execute_one(args.root, work_id, head, now,
                                 policy_sha=source_sha(args.root, POLICY),
                                 fixture_sha=source_sha(args.root, FIXTURE))
        else:
            output = check_readback(args.root, _read_json(args.receipt),
                                    expected_work_id=work_id,
                                    expected_source_head=head)
        data = json.dumps(output, sort_keys=True, indent=2) + "\n"
        target = Path(args.receipt)
        if args.mode == "produce":
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("x", encoding="utf-8") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
        print(json.dumps({"state": output["state"],
                          "work_id": work_id,
                          "receipt_sha256": output["receipt_sha256"],
                          "external_receiver_ack": False}, sort_keys=True))
        return 0
    except (Held, ValueError, TypeError, OSError) as exc:
        print(json.dumps({"state": "HOLD", "reason": str(exc)[:130],
                          "external_receiver_ack": False}))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
