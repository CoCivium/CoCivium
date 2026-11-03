#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/cocivia/coall_resource_lease_revocation_r0.json")

def fail(code):
    raise SystemExit(code)

def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def leaseable(grant_state, explicit_accept, grant, task, lease_grant_version=None):
    if grant_state != "ACTIVE":
        return False
    if not explicit_accept:
        return False
    if grant["resource_class"] != task["resource_class"]:
        return False
    if grant["purpose"] != task["purpose"]:
        return False
    if grant["privacy_scope"] != task["privacy_scope"]:
        return False
    if task["requested_capacity_units"] > grant["capacity_units"]:
        return False
    if lease_grant_version is not None and lease_grant_version != grant["grant_version"]:
        return False
    return True

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]
    if git_blob(src["resource_field_fixture_path"]) != src["resource_field_fixture_blob_sha"]:
        fail("FAIL_RESOURCE_FIELD_SOURCE_DRIFT")

    grant = d["grant"]
    task = d["task"]
    lease = d["lease"]

    state = {
        "grant_state": grant["initial_state"],
        "lease_state": "NONE",
        "execution_count": 0,
        "lease_issue_count": 0,
    }

    observed = []
    for row in d["timeline"]:
        if row["step"] == 1:
            got = "ELIGIBLE_FOR_LEASE" if leaseable(
                row["grant_state"], grant["explicit_accept"], grant, task
            ) else "DENY"
        elif row["step"] == 2:
            if not leaseable(row["grant_state"], grant["explicit_accept"], grant, task):
                got = "DENY"
            else:
                state["lease_state"] = "ISSUED_NOT_EXECUTED"
                state["lease_issue_count"] += 1
                got = "LEASE_ISSUED_NOT_EXECUTED"
        elif row["step"] == 3:
            current = leaseable(
                row["grant_state"], grant["explicit_accept"], grant, task,
                lease_grant_version=lease["grant_version"]
            )
            got = (
                "EXECUTION_WOULD_BE_ELIGIBLE_BUT_NOT_AUTHORIZED_IN_R0"
                if current and state["lease_state"] == "ISSUED_NOT_EXECUTED"
                else "DENY"
            )
        elif row["step"] == 4:
            state["grant_state"] = "REVOKED"
            state["lease_state"] = "INVALIDATED"
            got = "LEASE_INVALIDATED_FOR_FUTURE_EXECUTION"
        elif row["step"] == 5:
            current = leaseable(
                row["grant_state"], grant["explicit_accept"], grant, task,
                lease_grant_version=lease["grant_version"]
            )
            got = "DENY_REVOKED_GRANT" if not current else "FAIL"
        elif row["step"] == 6:
            current = leaseable(
                row["grant_state"], grant["explicit_accept"], grant, task
            )
            got = "DENY_NEW_LEASE_REVOKED_GRANT" if not current else "FAIL"
        else:
            fail("FAIL_UNKNOWN_TIMELINE_STEP")

        if got != row["expected"]:
            fail(f"FAIL_TIMELINE_STEP_{row['step']}:got={got}:expected={row['expected']}")
        observed.append({"step": row["step"], "result": got})

    for n in d["negative_cases"]:
        ng = dict(grant)
        nt = dict(task)
        if "task_purpose" in n:
            nt["purpose"] = n["task_purpose"]
        if "requested_capacity_units" in n:
            nt["requested_capacity_units"] = n["requested_capacity_units"]
        lgv = n.get("lease_grant_version")
        got = leaseable(
            n["grant_state"],
            n["explicit_accept"],
            ng,
            nt,
            lease_grant_version=lgv
        )
        if got is not n["expected_leaseable"]:
            fail("FAIL_NEGATIVE_CASE:" + n["id"])

    if state["execution_count"] != d["expected"]["real_execution_count"]:
        fail("FAIL_EXECUTION_COUNT")
    if state["lease_issue_count"] != d["expected"]["lease_issue_count"]:
        fail("FAIL_LEASE_ISSUE_COUNT")
    if d["expected"]["governance_authority_changed"] is not False:
        fail("FAIL_GOVERNANCE_AUTHORITY_EXPECTATION")
    if lease["capacity_ceiling_units"] > grant["capacity_units"]:
        fail("FAIL_LEASE_CAP_EXCEEDS_GRANT")
    if lease["effect_ceiling"] != task["effect_ceiling"]:
        fail("FAIL_EFFECT_CEILING_DRIFT")
    if lease["receipt_required"] is not True:
        fail("FAIL_RECEIPT_REQUIREMENT")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({
        "STATE": "PASS_COALL_RESOURCE_LEASE_REVOCATION_R0",
        "checked_out_head_sha": head,
        "fixture_semantic_sha256": canonical_sha(d),
        "timeline_steps": len(d["timeline"]),
        "negative_case_count": len(d["negative_cases"]),
        "lease_issue_count": state["lease_issue_count"],
        "real_execution_count": state["execution_count"],
        "final_grant_state": state["grant_state"],
        "final_lease_state": state["lease_state"],
        "revocation_invalidates_future_execution": True,
        "new_lease_after_revocation_denied": True,
        "current_runtime_authority": False,
        "rails": d["rails"]
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
