#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import subprocess
import urllib.request
from pathlib import Path

FIXTURE = Path("fixtures/resilience/coexit_convergence_hold_r0.json")


def fail(code):
    raise SystemExit(code)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest().upper()


def canonical_sha(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()


def api_get(path, token):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "CoCivium-CoExit-Convergence-R0",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        fail("FAIL_GITHUB_TOKEN_MISSING")

    raw = FIXTURE.read_bytes()
    d = json.loads(raw.decode("utf-8"))

    for src in d["local_source_bindings"]:
        if git_blob(src["path"]) != src["git_blob_sha"]:
            fail("FAIL_LOCAL_SOURCE_BIND:" + src["path"])

    donor_readproofs = []
    for donor in d["donor_prs"]:
        n = donor["pr_number"]
        pr = api_get(f"/repos/CoCivium/CoCivium/pulls/{n}", token)
        if pr["head"]["sha"] != donor["expected_head_sha"]:
            fail(f"FAIL_DONOR_HEAD_PR{n}")
        if bool(pr["draft"]) is not donor["expected_draft"]:
            fail(f"FAIL_DONOR_DRAFT_PR{n}")
        if pr["merged"] is not donor["expected_merged"]:
            fail(f"FAIL_DONOR_MERGED_PR{n}")

        run = api_get(
            f"/repos/CoCivium/CoCivium/actions/runs/{donor['required_success_run_id']}",
            token,
        )
        if run["head_sha"] != donor["expected_head_sha"]:
            fail(f"FAIL_DONOR_RUN_HEAD_PR{n}")
        if run["status"] != "completed" or run["conclusion"] != "success":
            fail(f"FAIL_DONOR_RUN_NOT_SUCCESS_PR{n}")

        for key in ["required_doc", "required_fixture"]:
            item = donor.get(key)
            if not item:
                continue
            remote = api_get(
                f"/repos/CoCivium/CoCivium/contents/{item['path']}?ref={donor['expected_head_sha']}",
                token,
            )
            if remote["sha"] != item["git_blob_sha"]:
                fail(f"FAIL_DONOR_OBJECT_BIND_PR{n}:{item['path']}")

        donor_readproofs.append({
            "pr_number": n,
            "role": donor["role"],
            "head_sha": donor["expected_head_sha"],
            "success_run_id": donor["required_success_run_id"],
            "receiver_readproof": "PASS_EXACT_REMOTE_DONOR_BIND",
        })

    c = d["convergence"]
    if c["account_retirement_state"] != "HOLD_NOT_EXIT_READY":
        fail("FAIL_EXIT_STATE")
    if c["current_account_close_safe"] is not False:
        fail("FAIL_ACCOUNT_CLOSE_OVERCLAIM")
    if c["current_account_delete_authority"] is not False:
        fail("FAIL_DELETE_AUTHORITY")
    if c["global_provider_tab_close_safe"] is not False:
        fail("FAIL_GLOBAL_TAB_CLOSE_OVERCLAIM")
    if c["new_long_lived_provider_work_identity_default"] is not False:
        fail("FAIL_PROVIDER_IDENTITY_SPAWN_POLICY")
    if c["new_provider_session_spawn_default_under_pressure"] is not False:
        fail("FAIL_PROVIDER_SPAWN_CONTRACTION")
    if c["new_github_only_exit_doctrine_default"] is not False:
        fail("FAIL_GITHUB_DOCTRINE_CONTRACTION")
    if c["elected_next"] != "HOLD_FOR_INDEPENDENT_ROUTE_OR_ACCOUNT_CENSUS":
        fail("FAIL_NEXT_ELECTION")
    if not c["wake_conditions"]:
        fail("FAIL_WAKE_CONDITIONS")

    required_close = {
        "UNIQUE_SCOPE_STATE_EXTERNALIZED",
        "ELECTED_DURABLE_DESTINATION_PROVEN",
        "EXACT_RECEIVER_READPROOF_PROVEN",
        "RECONSTRUCTION_FOR_SCOPE_PROVEN",
        "UNFINISHED_EFFECT_OBLIGATIONS_ABSENT_OR_TRANSFERRED",
        "ALTERNATIVE_EXECUTION_ROUTE_ADMISSIBLE",
    }
    if set(d["bounded_close_rule"]["individual_provider_session_may_retire_only_if"]) != required_close:
        fail("FAIL_BOUNDED_CLOSE_RULE")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "schema": "CoExitConvergence.Readproof.v0.1",
        "STATE": "PASS_PROVIDER_EXIT_CONVERGENCE_HOLD_R0",
        "checked_out_head_sha": head,
        "receiver_identity": "github-actions:coprovexit-resilience-r0",
        "fixture_sha256": sha256(raw),
        "fixture_semantic_sha256": canonical_sha(d),
        "local_source_object_count": len(d["local_source_bindings"]),
        "remote_donor_count": len(d["donor_prs"]),
        "remote_donor_readproofs": donor_readproofs,
        "account_retirement_state": c["account_retirement_state"],
        "elected_next": c["elected_next"],
        "provider_work_spawn_default": False,
        "github_only_exit_doctrine_spawn_default": False,
        "current_account_close_safe": False,
        "current_account_delete_authority": False,
        "global_provider_tab_close_safe": False,
        "wake_conditions": c["wake_conditions"],
        "external_effects": 0,
        "nonclaims": d["nonclaims"],
    }

    out = Path(args.output)
    if out.exists():
        fail("FAIL_CLOSED_NO_CLOBBER")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, separators=(",", ":")))


if __name__ == "__main__":
    main()
