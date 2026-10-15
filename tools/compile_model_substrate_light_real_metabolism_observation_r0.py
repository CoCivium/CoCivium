#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import subprocess
import urllib.request
from pathlib import Path

MANIFEST = Path("evidence/substrate/metabolism-observations-r0/manifest.json")
LANDED = Path("evidence/substrate/metabolism-observations-r0/controlled-counterfactual-fanin-r0.json")


def fail(code):
    raise SystemExit(code)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest().lower()


def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def git_blob(ref, path):
    return subprocess.check_output(["git", "rev-parse", f"{ref}:{path}"], text=True).strip()


def api_get(path, token):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "CoCivium-PR135-real-metabolism-observation-r0",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


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
    policies = manifest["policy_bindings"]

    if git_blob("HEAD", policies["metabolism_fixture_path"]) != policies["metabolism_fixture_blob_sha"]:
        fail("FAIL_METABOLISM_POLICY_BLOB_DRIFT")
    if git_blob("HEAD", policies["benefit_fixture_path"]) != policies["benefit_fixture_blob_sha"]:
        fail("FAIL_BENEFIT_POLICY_BLOB_DRIFT")

    metabolism = json.loads(Path(policies["metabolism_fixture_path"]).read_text(encoding="utf-8"))
    benefit = json.loads(Path(policies["benefit_fixture_path"]).read_text(encoding="utf-8"))

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
    if receipt.get("STATE") != "PASS_CONTROLLED_SINGLE_VS_PARALLEL_COUNTERFACTUAL_R0":
        fail("FAIL_COUNTERFACTUAL_STATE")
    if receipt.get("checked_out_head_sha") != prov["source_head_sha"]:
        fail("FAIL_SOURCE_HEAD")
    if receipt.get("same_exact_work_object") is not True:
        fail("FAIL_NOT_SAME_EXACT_WORK")
    if receipt.get("parallel_strict_benefit_yield_gain") is not False:
        fail("FAIL_UNEXPECTED_PARALLEL_GAIN")
    if receipt.get("physical_width_change_authorized") is not False:
        fail("FAIL_SOURCE_ALREADY_AUTHORIZES_WIDTH_CHANGE")

    single_yield = receipt["single"]["benefit_yield"]
    parallel_yield = receipt["parallel"]["benefit_yield"]
    if single_yield != parallel_yield:
        fail("FAIL_YIELD_MISMATCH_EXPECTATION")
    if receipt["parallel"]["execution_cost_units"] <= receipt["single"]["execution_cost_units"]:
        fail("FAIL_PARALLEL_COST_NOT_GREATER")

    no_gain_rule = benefit["policy"]["no_gain_rule"]
    if no_gain_rule != "NO_STRICT_VERIFIED_YIELD_GAIN_SERIALIZES_PHYSICAL_WIDTH_WITHOUT_COLLAPSING_LOGICAL_LANES":
        fail("FAIL_NO_GAIN_POLICY_RULE")

    initial = metabolism["initial_state"]
    if initial["physical_width"] != 1:
        fail("FAIL_METABOLISM_BASELINE_WIDTH")
    if initial["logical_branch_count"] != 3:
        fail("FAIL_METABOLISM_LOGICAL_BRANCH_COUNT")

    meta = api_get(
        f"/repos/CoCivium/CoCivium/actions/artifacts/{prov['artifact_id']}",
        token,
    )
    if meta.get("id") != prov["artifact_id"]:
        fail("FAIL_ARTIFACT_ID")
    if meta.get("name") != prov["artifact_name"]:
        fail("FAIL_ARTIFACT_NAME")
    if meta.get("digest") != prov["artifact_archive_digest"]:
        fail("FAIL_ARTIFACT_ARCHIVE_DIGEST")
    if meta.get("expired") is not False:
        fail("FAIL_ARTIFACT_EXPIRED")
    wr = meta.get("workflow_run") or {}
    if wr.get("id") != prov["workflow_run_id"]:
        fail("FAIL_ARTIFACT_RUN")
    if wr.get("head_sha") != prov["source_head_sha"]:
        fail("FAIL_ARTIFACT_SOURCE_HEAD")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    out_obj = {
        "schema": "CoModelSubstrateLight.RealMetabolismObservation.v0.1",
        "STATE": "PASS_REAL_COUNTERFACTUAL_METABOLISM_OBSERVATION_R0",
        "checked_out_head_sha": head,
        "receiver_identity": obj["Receiver"],
        "source_receipt_identity": obj["Identity"],
        "source_receipt_content_sha256": obj["ContentHash"],
        "source_artifact_id": prov["artifact_id"],
        "source_artifact_archive_digest": prov["artifact_archive_digest"],
        "receiver_readproof": "PASS_EXACT_OBJECT_READBACK",
        "source_receipt_lifecycle_transition": "LANDED_TO_PICKED_UP_BY_METABOLISM_COMPILER",
        "observation_class": "CONTROLLED_CI_COUNTERFACTUAL",
        "logical_work_id": receipt["logical_work_id"],
        "single": receipt["single"],
        "parallel": receipt["parallel"],
        "parallel_strict_benefit_yield_gain": False,
        "candidate_controller_baseline": {
            "physical_width": initial["physical_width"],
            "logical_branch_count": initial["logical_branch_count"],
        },
        "metabolism_advisory_action": "HOLD_PHYSICAL_WIDTH_1_NO_WIDEN",
        "advisory_basis": [
            "NO_STRICT_VERIFIED_BENEFIT_YIELD_GAIN",
            "PARALLEL_EXECUTION_COST_GREATER_FOR_SAME_UNIQUE_VERIFIED_BENEFIT",
        ],
        "pressure_metrics_present": False,
        "pressure_metrics_required_to_reject_widening_here": False,
        "physical_width_change_authorized": False,
        "runtime_state_mutated": False,
        "integration_state": "UNPROVEN",
        "next_gate": "CONTROLLED_COMPLEMENTARY_TASK_COUNTERFACTUAL_BEFORE_ANY_POSITIVE_WIDENING_EVIDENCE",
        "manifest_semantic_sha256": canonical_sha(manifest),
        "coverage_boundary": manifest["coverage_boundary"],
        "nonclaims": manifest["nonclaims"] + [
            "PICKED_UP_NE_INTEGRATED",
            "REAL_COUNTERFACTUAL_OBSERVATION_NE_RUNTIME_STATE",
            "ONE_NO_GAIN_OBSERVATION_NE_GLOBAL_SERIAL_DEFAULT",
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
        "single_benefit_yield": out_obj["single"]["benefit_yield"],
        "parallel_benefit_yield": out_obj["parallel"]["benefit_yield"],
        "single_execution_cost_units": out_obj["single"]["execution_cost_units"],
        "parallel_execution_cost_units": out_obj["parallel"]["execution_cost_units"],
        "metabolism_advisory_action": out_obj["metabolism_advisory_action"],
        "physical_width_change_authorized": out_obj["physical_width_change_authorized"],
        "runtime_state_mutated": out_obj["runtime_state_mutated"],
        "integration_state": out_obj["integration_state"],
        "manifest_semantic_sha256": out_obj["manifest_semantic_sha256"],
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
