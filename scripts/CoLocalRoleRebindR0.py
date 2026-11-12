#!/usr/bin/env python3
"""Public-safe role-scoped CoLocal session rebind, source-only; no OS/network effects.

Reuses the EXISTING CoAll session bootstrap and CoDesktop incident WorkID.
Never contacts X2, starts a shell, queries private data, or authorizes actions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BOOT = "ai/session-bootstrap.json"
CONTRACT_SCHEMA = "CoAll.RoleScopedSessionRebind.R0"
RESULT_SCHEMA = "CoAll.CoLocalRoleRebind.R0"
SOURCE_SCHEMA = "CoAll.CoLocal.X2PostContainmentFocusReconciliation.R1"
EXPECTED_WORK = "CoLocal2601109_X2_R5_FOCUS_INTERRUPTION_20261112"
NONCLAIMS = [
    "SOURCE_POINTER_NE_CROSS_SESSION_NOTIFICATION",
    "PUBLIC_SOURCE_NE_CURRENT_X2_RUNTIME",
    "READBACK_NE_OWNER_ACK",
    "THREE_TASKS_DISABLED_NE_FOCUS_CURED",
    "SHELL_FREE_BOOTSTRAP_NE_USER_UX_ACCEPTANCE",
    "LOCAL_IS_NOT_LANDED",
    "VALIDATION_IS_NOT_ACCEPTANCE",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
    "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
    "HASHING_IS_NOT_SEMANTIC_INGESTION",
    "DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY",
]


def _gitblob(value: bytes) -> str:
    return hashlib.sha1(f"blob {len(value)}\0".encode("ascii") + value).hexdigest()


def _safe_path(root: Path, name: Any) -> Path:
    if not isinstance(name, str) or not name or "\\" in name:
        raise ValueError("HOLD_BAD_SOURCE_PATH")
    parent = root.resolve()
    full = (parent / name).resolve()
    if not full.is_relative_to(parent) or not full.is_file():
        raise ValueError("HOLD_SOURCE_MISSING_OR_ESCAPE")
    return full


def _hold(reason: str) -> dict:
    return {
        "schema": RESULT_SCHEMA,
        "state": "HOLD_SOURCE_REBIND",
        "reason": reason,
        "operation_performed": False,
        "x2_shell_started": False,
        "receiver_pickup": False,
        "runtime_accepted": False,
        "nonclaims": NONCLAIMS,
    }


def rebind(root: Path, role: str) -> dict:
    try:
        root = Path(root)
        boot = json.loads(_safe_path(root, BOOT).read_text("utf-8"))
        lane = boot["role_scoped_rebind"]
        if lane["schema"] != CONTRACT_SCHEMA or lane["state"] != "PUBLIC_REENTRY_SAFETY_POINTER_NOT_LIVE_AGENT_DIRECTIVE":
            return _hold("HOLD_BOOTSTRAP_SCHEMA_OR_STATE")
        roles = lane["role_topics"]
        if not isinstance(roles, list) or len(set(roles)) != len(roles) or any(not isinstance(r, str) for r in roles):
            return _hold("HOLD_ROLE_SET")
        if lane["task_mutation_authorized"] is not False or lane["no_new_x2_terminal_or_scheduled_watcher"] is not True:
            return _hold("HOLD_UNSAFE_AUTHORITY")
        if lane["all_session_ack"] != "UNKNOWN" or lane["receiver_pickup"] != "UNVERIFIED" or lane["runtime_integration"] != "NOT_CLAIMED":
            return _hold("HOLD_FALSE_PICKUP_OR_RUNTIME")
        if role not in roles:
            return {
                "schema": RESULT_SCHEMA,
                "state": "NO_RELEVANT_INCIDENT_CONTENT",
                "role": role,
                "operation_performed": False,
                "x2_shell_started": False,
                "receiver_pickup": False,
                "runtime_accepted": False,
                "nonclaims": NONCLAIMS,
            }
        source = lane["source"]
        path = _safe_path(root, source["path"])
        raw = path.read_bytes()
        blob = _gitblob(raw)
        if blob != source["git_blob_sha1"]:
            return _hold("HOLD_SOURCE_BLOB_DRIFT")
        packet = json.loads(raw)
        if packet.get("schema") != SOURCE_SCHEMA or packet.get("work_id") != EXPECTED_WORK:
            return _hold("HOLD_INCIDENT_SOURCE_IDENTITY")
        if packet.get("state") != "PARTIAL_NATIVE_CONTAINMENT_VERIFIED__FOCUS_CURE_HELD":
            return _hold("HOLD_UNQUALIFIED_INCIDENT_STATE")
        if packet.get("current_rails", {}).get("further_runtime_mutation_authorized") is not False:
            return _hold("HOLD_INCIDENT_AUTHORITY_CONFLICT")
        owner = lane.get("incumbent_owner")
        if owner != "https://github.com/CoCivium/CoCivium/issues/181":
            return _hold("HOLD_INCUMBENT_OWNER_DRIFT")
        if packet.get("current_rails", {}).get("incident_owner") != owner:
            return _hold("HOLD_SOURCE_OWNER_CONFLICT")
        if lane.get("currentness_rule") != "FETCH_INCUMBENT_CURRENT_HEAD_BEFORE_EFFECT__THIS_POINTER_MAY_BECOME_STALE":
            return _hold("HOLD_MISSING_CURRENTNESS_BOUNDARY")
        return {
            "schema": RESULT_SCHEMA,
            "state": "SOURCE_BOUND_REBIND_OWNER_REFRESH_REQUIRED",
            "role": role,
            "work_id": EXPECTED_WORK,
            "CoHereNow": "Selected task quarantine is source-evidenced; focus cure and native R6 are unverified.",
            "CoNext": "Refresh CoDesktop owner issue #181; preserve quiet interval; no competing X2 diagnostic shell.",
            "source_path": source["path"],
            "source_git_blob_sha1": blob,
            "incident_owner": owner,
            "read_scope": "PUBLIC_SOURCE_ONLY_NOT_LIVE_DEVICE",
            "owner_refresh_required": True,
            "operation_performed": False,
            "x2_shell_started": False,
            "receiver_pickup": False,
            "runtime_accepted": False,
            "nonclaims": NONCLAIMS,
        }
    except (OSError, ValueError, TypeError, KeyError, AttributeError, json.JSONDecodeError):
        return _hold("HOLD_MISSING_OR_MALFORMED_SOURCE")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--role", default="X2_DESKTOP_RECOVERY")
    args = p.parse_args()
    result = rebind(args.root, args.role)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if result["state"].startswith("HOLD_") else 0


if __name__ == "__main__":
    raise SystemExit(main())
