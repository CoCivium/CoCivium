"""Bounded GitHub Actions artifact handoff with a distinct receiver job.

The producer makes a public synthetic object and a SHA-256 claim; the receiver
recomputes the digest on downloaded bytes and writes its own observation.
This proves only a separate-job readback within one GitHub Actions provider.
It is not an independent provider, X2 receiver, CoEx, or useful work effect.
No network, credentials, scheduler, subprocess, or host mutation in this code.
"""
from __future__ import annotations

from collections.abc import Mapping
import argparse
import hashlib
import json
import os
import re
from pathlib import Path

WORK_ID = "CoStel.CI.ArtifactPickup.R0"
SOURCE_SCHEMA = "CoStel.CI.SourceEnvelope.R0"
PRODUCER_SCHEMA = "CoStel.CI.ProducerClaim.R0"
RECEIVER_SCHEMA = "CoStel.CI.ReceiverObservation.R0"
SOURCE_MESSAGE = "Public synthetic handoff fixture, not a task command"
PRODUCER_JOB = "handoff-producer"
RECEIVER_JOB = "handoff-receiver"


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("utf-8")


def require_context(env, job):
    keys = ("GITHUB_ACTIONS", "GITHUB_JOB", "GITHUB_RUN_ID",
            "GITHUB_RUN_ATTEMPT", "GITHUB_SHA")
    # GitHub's real environment is os._Environ (a Mapping), not a dict.
    # Still require every expected Actions field to be a nonempty string.
    if not isinstance(env, Mapping) or any(not isinstance(env.get(k), str) or not env.get(k) for k in keys):
        raise ValueError("HOLD_MISSING_GITHUB_CONTEXT")
    if env["GITHUB_ACTIONS"] != "true" or env["GITHUB_JOB"] != job:
        raise ValueError("HOLD_WRONG_JOB_IDENTITY")
    if not re.fullmatch(r"[1-9][0-9]*", env["GITHUB_RUN_ID"]):
        raise ValueError("HOLD_INVALID_RUN_ID")
    if not re.fullmatch(r"[1-9][0-9]*", env["GITHUB_RUN_ATTEMPT"]):
        raise ValueError("HOLD_INVALID_ATTEMPT")
    if not re.fullmatch(r"[0-9a-f]{40}", env["GITHUB_SHA"]):
        raise ValueError("HOLD_INVALID_SOURCE_REVISION")
    return {k: env[k] for k in keys}


def produce(directory, env):
    ctx = require_context(env, PRODUCER_JOB)
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=False)
    source = {
        "schema": SOURCE_SCHEMA,
        "work_id": WORK_ID,
        "source_commit": ctx["GITHUB_SHA"],
        "ci_run_id": ctx["GITHUB_RUN_ID"],
        "ci_attempt": ctx["GITHUB_RUN_ATTEMPT"],
        "producer_job": PRODUCER_JOB,
        "message": SOURCE_MESSAGE,
    }
    raw = canonical(source)
    manifest = {
        "schema": PRODUCER_SCHEMA,
        "work_id": WORK_ID,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "source_bytes": len(raw),
        "producer_job": PRODUCER_JOB,
    }
    with (target / "source.json").open("xb") as stream:
        stream.write(raw)
    with (target / "producer_claim.json").open("xb") as stream:
        stream.write(canonical(manifest))
    return manifest


def receive(directory, receipt_path, env):
    ctx = require_context(env, RECEIVER_JOB)
    root = Path(directory)
    raw = (root / "source.json").read_bytes()
    claim_raw = (root / "producer_claim.json").read_bytes()
    source = json.loads(raw)
    claim = json.loads(claim_raw)
    if not isinstance(source, dict) or not isinstance(claim, dict):
        raise ValueError("HOLD_INVALID_OBJECT")
    if raw != canonical(source) or claim_raw != canonical(claim):
        raise ValueError("HOLD_NONCANONICAL_OBJECT")
    expected_source = {
        "schema": SOURCE_SCHEMA,
        "work_id": WORK_ID,
        "source_commit": ctx["GITHUB_SHA"],
        "ci_run_id": ctx["GITHUB_RUN_ID"],
        "ci_attempt": ctx["GITHUB_RUN_ATTEMPT"],
        "producer_job": PRODUCER_JOB,
        "message": SOURCE_MESSAGE,
    }
    if source != expected_source:
        raise ValueError("HOLD_SOURCE_BINDING_MISMATCH")
    digest = hashlib.sha256(raw).hexdigest()
    expected_claim = {
        "schema": PRODUCER_SCHEMA,
        "work_id": WORK_ID,
        "source_sha256": digest,
        "source_bytes": len(raw),
        "producer_job": PRODUCER_JOB,
    }
    if claim != expected_claim:
        raise ValueError("HOLD_PRODUCER_CLAIM_MISMATCH")
    # The job identity is asserted by runner environment and corroborated by
    # hosted CI job records. Do not claim independent external attestation.
    receipt = {
        "schema": RECEIVER_SCHEMA,
        "state": "HASH_MATCHED_ARTIFACT_PICKUP_CI_SCOPE",
        "work_id": WORK_ID,
        "source_commit": ctx["GITHUB_SHA"],
        "ci_run_id": ctx["GITHUB_RUN_ID"],
        "ci_attempt": ctx["GITHUB_RUN_ATTEMPT"],
        "producer_job": PRODUCER_JOB,
        "receiver_job": RECEIVER_JOB,
        "receiver_witness": "GITHUB_ACTIONS_JOB_BOUNDARY",
        "source_sha256": digest,
        "source_bytes": len(raw),
        "source_readback": "SHA256_AND_CANONICAL_PAYLOAD_MATCHED",
        "provider_failure_domain": "SAME_GITHUB_ACTIONS_PROVIDER",
        "useful_work_effect": "NOT_TESTED",
        "cross_provider_recovery": "NOT_TESTED",
        "x2_native_receiver": "NOT_TESTED",
        "global_session_ack": False,
    }
    dest = Path(receipt_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("xb") as stream:
        stream.write(canonical(receipt))
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("produce", "receive"))
    parser.add_argument("location")
    parser.add_argument("--receipt")
    args = parser.parse_args()
    if args.mode == "produce":
        if args.receipt:
            parser.error("producer does not accept --receipt")
        result = produce(args.location, os.environ)
    else:
        if not args.receipt:
            parser.error("receiver requires --receipt")
        result = receive(args.location, args.receipt, os.environ)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
