#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MANIFEST = Path("evidence/substrate/pressure-observations-r0/manifest.json")
LANDED = Path("evidence/substrate/pressure-observations-r0/complementary-search-counterfactual-fanin-r0.json")


def fail(code: str) -> None:
    raise SystemExit(code)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().lower()


def canonical_sha(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def git_blob(ref: str, path: str) -> str:
    return subprocess.check_output(["git", "rev-parse", f"{ref}:{path}"], text=True).strip()


def api_get(path: str, token: str):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "CoCivium-PR135-real-pressure-observation-r0",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def seconds(a: str, b: str) -> int:
    return int((parse_time(b) - parse_time(a)).total_seconds())


def max_concurrency(intervals):
    events = []
    for start, end in intervals:
        events.append((parse_time(start), 1))
        events.append((parse_time(end), -1))
    # End before start at the same timestamp => half-open [start,end).
    events.sort(key=lambda x: (x[0], x[1]))
    current = 0
    maximum = 0
    for _, delta in events:
        current += delta
        maximum = max(maximum, current)
    return maximum


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--downloaded-receipt", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        fail("FAIL_GITHUB_TOKEN_MISSING")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    obj = manifest["object"]
    prov = obj["Provenance"]
    binding = manifest["policy_binding"]

    if git_blob("HEAD", binding["benefit_fixture_path"]) != binding["benefit_fixture_blob_sha"]:
        fail("FAIL_BENEFIT_POLICY_BLOB_DRIFT")
    policy = json.loads(Path(binding["benefit_fixture_path"]).read_text(encoding="utf-8"))

    landed_raw = LANDED.read_bytes()
    source_raw = Path(args.downloaded_receipt).read_bytes()
    expected_hash = obj["ContentHash"].split(":", 1)[1].lower()
    if sha256(landed_raw) != expected_hash:
        fail("FAIL_LANDED_CONTENT_HASH")
    if sha256(source_raw) != expected_hash:
        fail("FAIL_SOURCE_CONTENT_HASH")
    if landed_raw != source_raw:
        fail("FAIL_SOURCE_NE_LANDED_BYTES")

    receipt = json.loads(source_raw.decode("utf-8"))
    if receipt.get("STATE") != "PASS_CONTROLLED_COMPLEMENTARY_SEARCH_COUNTERFACTUAL_R0":
        fail("FAIL_SOURCE_RECEIPT_STATE")
    if receipt.get("checked_out_head_sha") != prov["source_head_sha"]:
        fail("FAIL_SOURCE_HEAD_BIND")
    if receipt.get("parallel_strict_verified_benefit_gain") is not True:
        fail("FAIL_POSITIVE_BENEFIT_GATE")
    if receipt.get("physical_width_change_authorized") is not False:
        fail("FAIL_SOURCE_ALREADY_AUTHORIZES_WIDTH")
    if receipt.get("picked_up_receiver_receipt_count") != 4:
        fail("FAIL_SOURCE_READPROOF_COUNT")

    artifact = api_get(
        f"/repos/CoCivium/CoCivium/actions/artifacts/{prov['artifact_id']}",
        token,
    )
    if artifact.get("id") != prov["artifact_id"]:
        fail("FAIL_ARTIFACT_ID")
    if artifact.get("name") != prov["artifact_name"]:
        fail("FAIL_ARTIFACT_NAME")
    if artifact.get("digest") != prov["artifact_archive_digest"]:
        fail("FAIL_ARTIFACT_DIGEST")
    if artifact.get("expired") is not False:
        fail("FAIL_ARTIFACT_EXPIRED")
    wr = artifact.get("workflow_run") or {}
    if wr.get("id") != prov["workflow_run_id"]:
        fail("FAIL_ARTIFACT_RUN_ID")
    if wr.get("head_sha") != prov["source_head_sha"]:
        fail("FAIL_ARTIFACT_HEAD")

    run = api_get(
        f"/repos/CoCivium/CoCivium/actions/runs/{prov['workflow_run_id']}",
        token,
    )
    if run.get("head_sha") != prov["source_head_sha"]:
        fail("FAIL_RUN_HEAD")
    if run.get("conclusion") != "success":
        fail("FAIL_RUN_NOT_SUCCESS")

    jobs_payload = api_get(
        f"/repos/CoCivium/CoCivium/actions/runs/{prov['workflow_run_id']}/jobs?per_page=100",
        token,
    )
    jobs = {j["name"]: j for j in jobs_payload.get("jobs", [])}
    bindings = manifest["job_bindings"]
    required_names = [bindings["single"], *bindings["parallel"], bindings["fanin"]]
    if any(name not in jobs for name in required_names):
        fail("FAIL_REQUIRED_JOB_MISSING")

    for name in required_names:
        j = jobs[name]
        if j.get("conclusion") != "success":
            fail("FAIL_JOB_NOT_SUCCESS:" + name)
        if j.get("head_sha") != prov["source_head_sha"]:
            fail("FAIL_JOB_HEAD:" + name)
        if not j.get("started_at") or not j.get("completed_at") or not j.get("created_at"):
            fail("FAIL_JOB_TIMESTAMPS:" + name)

    single = jobs[bindings["single"]]
    parallels = [jobs[name] for name in bindings["parallel"]]
    fanin = jobs[bindings["fanin"]]

    single_queue = seconds(single["created_at"], single["started_at"])
    single_wall = seconds(single["started_at"], single["completed_at"])
    parallel_queue = {
        j["name"]: seconds(j["created_at"], j["started_at"]) for j in parallels
    }
    parallel_wall = {
        j["name"]: seconds(j["started_at"], j["completed_at"]) for j in parallels
    }
    parallel_intervals = [(j["started_at"], j["completed_at"]) for j in parallels]
    observed_max_concurrency = max_concurrency(parallel_intervals)
    parallel_span_seconds = int(
        (
            max(parse_time(j["completed_at"]) for j in parallels)
            - min(parse_time(j["started_at"]) for j in parallels)
        ).total_seconds()
    )

    requested_width = receipt["parallel"]["physical_width"]
    receiver_leases = receipt["parallel"]["receiver_count"]
    if requested_width != 3 or receiver_leases != 3:
        fail("FAIL_PARALLEL_TREATMENT_BIND")

    missing_readproofs = 4 - receipt["picked_up_receiver_receipt_count"]
    if missing_readproofs != 0:
        fail("FAIL_MISSING_READPROOFS")

    replica_ids = [r["replica_id"] for r in receipt["readproofs"]]
    shard_ids = [
        r["assigned_shard_id"]
        for r in receipt["readproofs"]
        if r["counterfactual_mode"] == "PARALLEL"
    ]
    observed_identity_collisions = len(replica_ids) - len(set(replica_ids))
    observed_parallel_assignment_collisions = len(shard_ids) - len(set(shard_ids))
    if observed_identity_collisions != 0 or observed_parallel_assignment_collisions != 0:
        fail("FAIL_OBSERVED_COLLISION")

    budgets = policy["policy"]["hard_budgets"]

    raw_observables = {
        "requested_parallel_width": requested_width,
        "parallel_receiver_lease_count": receiver_leases,
        "observed_max_concurrent_parallel_jobs": observed_max_concurrency,
        "full_requested_width_observed": observed_max_concurrency >= requested_width,
        "single_queue_wait_seconds": single_queue,
        "single_job_wall_seconds": single_wall,
        "parallel_queue_wait_seconds_by_job": parallel_queue,
        "parallel_job_wall_seconds_by_job": parallel_wall,
        "parallel_max_queue_wait_seconds": max(parallel_queue.values()),
        "parallel_sum_receiver_job_wall_seconds": sum(parallel_wall.values()),
        "parallel_receiver_span_seconds": parallel_span_seconds,
        "fanin_queue_wait_seconds": seconds(fanin["created_at"], fanin["started_at"]),
        "fanin_job_wall_seconds": seconds(fanin["started_at"], fanin["completed_at"]),
        "missing_receiver_readproof_count": missing_readproofs,
        "observed_replica_identity_collision_count": observed_identity_collisions,
        "observed_parallel_assignment_collision_count": observed_parallel_assignment_collisions,
        "human_attention_cost": None,
        "energy_consumption": None,
    }

    translation = {
        "receiver_pressure": {
            "policy_limit": budgets["receiver_pressure_max"],
            "state": "UNMAPPED_TO_POLICY_SCALE",
            "raw_evidence": {
                "requested_parallel_width": requested_width,
                "observed_max_concurrent_parallel_jobs": observed_max_concurrency,
                "parallel_max_queue_wait_seconds": max(parallel_queue.values()),
            },
        },
        "proof_debt": {
            "policy_limit": budgets["proof_debt_max"],
            "state": "RAW_MISSING_READPROOF_COUNT_OBSERVED__POLICY_SCALE_UNCALIBRATED",
            "raw_value": missing_readproofs,
        },
        "collision_risk": {
            "policy_limit": budgets["collision_risk_max"],
            "state": "RAW_COLLISION_COUNT_OBSERVED__RISK_SCALE_UNCALIBRATED",
            "raw_value": observed_identity_collisions + observed_parallel_assignment_collisions,
        },
        "human_attention_cost": {
            "policy_limit": budgets["human_attention_cost_max"],
            "state": "UNMEASURED",
            "raw_value": None,
        },
        "compute_cost": {
            "policy_limit": budgets["compute_cost_max"],
            "state": "RAW_RUNNER_TIME_AND_LEASES_OBSERVED__POLICY_SCALE_UNCALIBRATED",
            "raw_evidence": {
                "parallel_receiver_leases": receiver_leases,
                "parallel_sum_receiver_job_wall_seconds": sum(parallel_wall.values()),
                "single_receiver_leases": receipt["single"]["receiver_count"],
                "single_job_wall_seconds": single_wall,
            },
        },
    }

    all_budget_pass = all(
        item["state"] == "PROVEN_PASS"
        for item in translation.values()
    )

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    out_obj = {
        "schema": "CoModelSubstrateLight.RealPressureObservation.v0.1",
        "STATE": "PASS_REAL_PRESSURE_OBSERVATION_WITH_WIDTH_DOWNGRADE_R0",
        "checked_out_head_sha": head,
        "receiver_identity": obj["Receiver"],
        "source_receipt_identity": obj["Identity"],
        "source_receipt_content_sha256": obj["ContentHash"],
        "source_receipt_lifecycle_transition": "LANDED_TO_PICKED_UP_BY_PRESSURE_COMPILER",
        "source_workflow_run_id": prov["workflow_run_id"],
        "source_artifact_id": prov["artifact_id"],
        "positive_verified_coverage_gain": True,
        "parallel_efficiency_gain_claimed": False,
        "experimental_treatment_interpretation": {
            "single": "ONE_RECEIVER_LEASE",
            "parallel": "THREE_REQUESTED_RECEIVER_LEASES_WITHIN_ONE_WORKFLOW_WAVE",
            "literal_simultaneous_physical_width_3_proven": False,
            "observed_max_concurrent_parallel_jobs": observed_max_concurrency,
        },
        "prior_width_claim_correction": "DECLARED_PHYSICAL_WIDTH_3_DOWNGRADED_TO_REQUESTED_WIDTH_3__OBSERVED_MAX_CONCURRENCY_" + str(observed_max_concurrency),
        "coverage_gain_evidence_status": "PRESERVED_FOR_THREE_COMPLEMENTARY_RECEIVER_LEASES_WITHIN_ONE_WORKFLOW_WAVE",
        "raw_observables": raw_observables,
        "pressure_budget_translation": translation,
        "all_hard_budgets_proven_pass": all_budget_pass,
        "advisory_width_decision": "HOLD_PRESSURE_BUDGET_TRANSLATION_UNCALIBRATED",
        "physical_width_change_authorized": False,
        "runtime_state_mutated": False,
        "integration_state": "UNPROVEN",
        "next_gate": "CALIBRATE_POLICY_PRESSURE_UNITS_OR_COLLECT_DIRECT_RUNTIME_METRICS_BEFORE_ANY_POSITIVE_WIDENING_ADVISORY",
        "manifest_semantic_sha256": canonical_sha(manifest),
        "coverage_boundary": manifest["coverage_boundary"],
        "nonclaims": manifest["nonclaims"] + [
            "DECLARED_WIDTH_NE_OBSERVED_SIMULTANEOUS_WIDTH",
            "OBSERVED_MAX_CONCURRENCY_2_NE_GITHUB_GLOBAL_CAPACITY_2",
            "POSITIVE_COVERAGE_GAIN_NE_PROVEN_WIDTH_3_SIMULTANEITY",
            "PICKED_UP_NE_INTEGRATED",
        ],
    }

    out = Path(args.output)
    if out.exists():
        fail("FAIL_CLOSED_NO_CLOBBER")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(out_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "STATE": out_obj["STATE"],
        "checked_out_head_sha": head,
        "source_receipt_lifecycle_transition": out_obj["source_receipt_lifecycle_transition"],
        "requested_parallel_width": requested_width,
        "observed_max_concurrent_parallel_jobs": observed_max_concurrency,
        "full_requested_width_observed": raw_observables["full_requested_width_observed"],
        "parallel_max_queue_wait_seconds": raw_observables["parallel_max_queue_wait_seconds"],
        "parallel_sum_receiver_job_wall_seconds": raw_observables["parallel_sum_receiver_job_wall_seconds"],
        "single_job_wall_seconds": single_wall,
        "missing_receiver_readproof_count": missing_readproofs,
        "all_hard_budgets_proven_pass": all_budget_pass,
        "advisory_width_decision": out_obj["advisory_width_decision"],
        "physical_width_change_authorized": False,
        "manifest_semantic_sha256": out_obj["manifest_semantic_sha256"],
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
