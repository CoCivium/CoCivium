#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import subprocess
import urllib.request
from pathlib import Path

FIXTURE = Path("fixtures/architecture/cocatchup_delta_surface_r0.json")

def fail(code):
    raise SystemExit(code)

def sha256(raw):
    return hashlib.sha256(raw).hexdigest().upper()

def canonical_sha(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))

def api_get(path, token):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "CoCivium-CoCatchUp-DeltaSurface-R0",
        },
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.loads(resp.read().decode("utf-8"))

def workflow_summary(repo, head, token):
    payload = api_get(
        f"/repos/{repo}/actions/runs?head_sha={head}&per_page=100",
        token,
    )
    runs = payload.get("workflow_runs", [])
    current = [
        {
            "id": r["id"],
            "name": r["name"],
            "status": r["status"],
            "conclusion": r["conclusion"],
        }
        for r in runs
        if r.get("head_sha") == head
    ]
    successful = [r for r in current if r["status"] == "completed" and r["conclusion"] == "success"]
    failing = [r for r in current if r["status"] == "completed" and r["conclusion"] == "failure"]
    pending = [r for r in current if r["status"] != "completed"]
    return {
        "run_count": len(current),
        "success_count": len(successful),
        "failure_count": len(failing),
        "pending_count": len(pending),
        "has_any_success": bool(successful),
        "runs": current,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        fail("FAIL_GITHUB_TOKEN_MISSING")

    raw = FIXTURE.read_bytes()
    d = json.loads(raw.decode("utf-8"))
    repo = "CoCivium/CoCivium"

    local_head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    host_pr = api_get(f"/repos/{repo}/pulls/{d['host_pr']}", token)
    if host_pr["head"]["sha"] != local_head:
        fail("FAIL_HOST_PR_HEAD_NE_LOCAL_HEAD")

    main = api_get(f"/repos/{repo}/commits/main", token)
    current_main_head = main["sha"]
    main_delta = current_main_head != d["baseline_main_head_sha"]

    rows = []
    material_delta_count = int(main_delta)
    hold_count = 0
    wait_count = 0

    for watch in d["watched_prs"]:
        n = watch["pr_number"]
        pr = api_get(f"/repos/{repo}/pulls/{n}", token)
        head = pr["head"]["sha"]
        baseline = watch["baseline_head_sha"]

        if n == d["host_pr"]:
            # The observer commit necessarily advances its host branch.
            relation = (
                "HOST_ADVANCED_BY_OBSERVER_COMMIT"
                if head != baseline
                else "HOST_MATCHES_PRE_OBSERVER_BASELINE"
            )
            head_delta = False
        else:
            head_delta = head != baseline
            relation = "HEAD_ADVANCED_OR_REBASED" if head_delta else "MATCHES_BOUND_BASELINE"

        merged = bool(pr.get("merged"))
        state = pr.get("state")
        closed = state == "closed"
        draft = bool(pr.get("draft"))

        wf = workflow_summary(repo, head, token)

        is_host = n == d["host_pr"]
        if is_host:
            # A workflow cannot truthfully use its own in-flight status as evidence
            # of its eventual conclusion. Its external GitHub run conclusion is the
            # proof surface after this receipt is emitted.
            current_head_hold = False
            current_head_wait = False
            current_head_assessment = "HOST_SELF_PROOF_DEFERRED_TO_EXTERNAL_RUN_CONCLUSION"
        else:
            no_runs = wf["run_count"] == 0
            pending_only = (
                wf["pending_count"] > 0
                and not wf["has_any_success"]
                and wf["failure_count"] == 0
            )
            failed_after_settle = (
                wf["failure_count"] > 0
                and not wf["has_any_success"]
                and wf["pending_count"] == 0
            )
            current_head_wait = pending_only
            current_head_hold = no_runs or failed_after_settle
            if no_runs:
                current_head_assessment = "HOLD_NO_CURRENT_HEAD_PROOF"
            elif failed_after_settle:
                current_head_assessment = "HOLD_CURRENT_HEAD_FAILURE_WITHOUT_SUCCESS"
            elif pending_only:
                current_head_assessment = "WAIT_CURRENT_HEAD_PROOF_IN_FLIGHT"
            elif wf["has_any_success"]:
                current_head_assessment = "CURRENT_HEAD_HAS_SUCCESS"
            else:
                current_head_assessment = "CURRENT_HEAD_MIXED_OR_UNKNOWN"

        if head_delta or merged or closed:
            material_delta_count += 1
        if current_head_hold:
            hold_count += 1
        if current_head_wait:
            wait_count += 1

        rows.append({
            "pr_number": n,
            "role": watch["role"],
            "title": pr["title"],
            "current_head_sha": head,
            "baseline_head_sha": baseline,
            "baseline_relation": relation,
            "draft": draft,
            "merged": merged,
            "state": state,
            "mergeable": pr.get("mergeable"),
            "updated_at": pr.get("updated_at"),
            "current_head_workflows": wf,
            "current_head_hold": current_head_hold,
            "current_head_wait": current_head_wait,
            "current_head_assessment": current_head_assessment,
            "special_disposition": watch["special_disposition"],
        })

    if hold_count:
        next_action = "REVIEW_CURRENT_HEAD_HOLD_SIGNALS"
        state = "PASS_COCATCHUP_DELTA_SURFACE_R0__HOLD_SIGNAL_PRESENT"
    elif material_delta_count:
        next_action = "RELATE_MATERIAL_DELTAS_BEFORE_NEW_BRANCH_OR_MUTATION"
        state = "PASS_COCATCHUP_DELTA_SURFACE_R0__DELTA_PRESENT"
    elif wait_count:
        next_action = "WAIT_FOR_NON_HOST_CURRENT_HEAD_PROOF_TO_SETTLE"
        state = "PASS_COCATCHUP_DELTA_SURFACE_R0__WAIT_SIGNAL_PRESENT"
    else:
        next_action = "NONE__WATCHED_FRONTIER_MATCHES_BOUND_BASELINE"
        state = "PASS_COCATCHUP_DELTA_SURFACE_R0__NO_MATERIAL_DELTA"

    receipt = {
        "schema": "CoCatchUp.DeltaSurfaceReceipt.v0.1",
        "STATE": state,
        "checked_out_head_sha": local_head,
        "receiver_identity": "github-actions:cocatchup-delta-surface-r0",
        "fixture_sha256": sha256(raw),
        "fixture_semantic_sha256": canonical_sha(d),
        "current_main_head_sha": current_main_head,
        "baseline_main_head_sha": d["baseline_main_head_sha"],
        "main_head_changed": main_delta,
        "watched_pr_count": len(rows),
        "material_delta_count": material_delta_count,
        "current_head_hold_count": hold_count,
        "current_head_wait_count": wait_count,
        "next_safe_action": next_action,
        "rows": rows,
        "ux_summary": {
            "CoHereNow": f"{len(rows)} watched candidate surfaces queried live; material deltas={material_delta_count}; holds={hold_count}; waits={wait_count}",
            "Meaning": "Live GitHub currentness is separated from bound baseline pointers and historical failures.",
            "NextSafeAction": next_action,
            "UXState": "UX_ACCEPTANCE_UNPROVEN",
        },
        "external_effects": 0,
        "nonclaims": d["nonclaims"],
    }

    out = Path(args.output)
    if out.exists():
        fail("FAIL_CLOSED_NO_CLOBBER")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "STATE": state,
        "checked_out_head_sha": local_head,
        "current_main_head_sha": current_main_head,
        "watched_pr_count": len(rows),
        "material_delta_count": material_delta_count,
        "current_head_hold_count": hold_count,
        "current_head_wait_count": wait_count,
        "next_safe_action": next_action,
        "fixture_semantic_sha256": receipt["fixture_semantic_sha256"],
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
