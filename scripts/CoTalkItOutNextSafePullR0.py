#!/usr/bin/env python3
"""Read-only, role-scoped CoTalkItOut roadmap pull. No agent, scheduler or actuator.

Turns an exact-source DAG into ONE review candidate and a typed HOLD/next
read-only check. Reuses CoLocalRoleRebindR0 for X2 incident currentness.
Cannot notify other sessions, read private state or authorize side effects.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any

from verify_cotalkitout_headless_roadmap_r0 import (
    CSV_PATH, EXPECTED_SHA256, EXPECTED_TASKS, ROOT, WORKID,
    validate,
)
from CoLocalRoleRebindR0 import rebind as colocal_rebind

SCHEMA = "CoAll.CoTalkItOut.RoleScopedPull.R0"
ROLES = {
    "X2_DESKTOP_RECOVERY": "01 Quiet X2 foreground",
    "WORKID_CUSTODY": "03 Durable WorkID & state",
    "PROVIDER_EXIT": "13 Provider-exit substitution",
    "VOICE_FIRST": "08 Voice-first interaction",
    "SESSION_EVOLUTION": "15 CoEv+ tuning & receiver trials",
    "GENERAL_READ_ONLY": None,
}
STATES_NOT_ACCEPTANCE = {"HELD", "PLANNED", "SOURCE_TESTED_ONLY", "OBSERVED_GAP", "HUMAN_GATE"}
NONCLAIMS = [
    "PUBLIC_SOURCE_NE_SESSION_DELIVERY",
    "SOURCE_TESTED_NE_NATIVE_RUNTIME",
    "PLANNED_NE_AUTHORIZED",
    "RELATED_WORK_NE_COMPLETED_PREREQUISITE",
    "LOCAL_MODEL_NE_CONNECTED_WORKER",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
    "HUMAN_OPTIONAL_NE_NO_HUMAN_AUTHORITY",
    "NO_X2_SHELL_OR_NEW_WATCHER",
]

def _hold(reason: str, role: str, source_sha: str = "") -> dict[str, Any]:
    return {
        "schema": SCHEMA, "work_id": WORKID, "role": role,
        "decision": "HOLD", "reason": reason,
        "source_sha256": source_sha, "selected_task": None,
        "authority": "NONE", "dispatch_allowed": False,
        "external_effect": False, "independent_receiver_ack": "UNKNOWN",
        "source_promoted_to_runtime": False, "nonclaims": NONCLAIMS,
    }

def _blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()

def _record_clean(row: dict[str, str]) -> dict[str, Any]:
    deps = [x.strip() for x in row["depends_on"].split(",") if x.strip()]
    return {
        "task_id": row["task_id"], "topo": int(row["topo"]),
        "lane": row["lane"], "title": row["title"],
        "operation": row["operation"], "acceptance": row["acceptance"],
        "source_url": row["source_url"], "prerequisite_task_ids": deps,
        "priority": row["priority"], "evidence_state": row["evidence_state"],
        "human_gate": row["human_gate"] == "YES",
        "accepted": False,
    }

def choose(records: list[dict[str, str]], role: str, *,
           x2_rebind: dict[str, Any] | None,
           source_sha256: str, source_blob: str) -> dict[str, Any]:
    if role not in ROLES:
        return _hold("HOLD_UNRECOGNIZED_ROLE", role, source_sha256)
    if not records or any(r["evidence_state"] not in STATES_NOT_ACCEPTANCE for r in records):
        return _hold("HOLD_SOURCE_STATE_UNQUALIFIED", role, source_sha256)
    lane = ROLES[role]
    subset = [r for r in records if lane is None or r["lane"] == lane]
    if not subset:
        return _hold("HOLD_NO_ROLE_WORK", role, source_sha256)
    # A root candidate can be REVIEWED. It is never accepted or executable
    # just because it has no roadmap dependencies.
    priority = {"P0": 0, "P1": 1, "P2": 2}
    proof_need = {"OBSERVED_GAP": 0, "SOURCE_TESTED_ONLY": 1, "PLANNED": 2,
                  "HELD": 3, "HUMAN_GATE": 4}
    subset.sort(key=lambda r: (
        bool(r["depends_on"]), priority[r["priority"]],
        proof_need[r["evidence_state"]], int(r["topo"]), r["task_id"]
    ))
    candidate = _record_clean(subset[0])
    if candidate["prerequisite_task_ids"]:
        decision, reason = "HOLD", "HOLD_PREREQUISITE_ACCEPTANCE_UNPROVEN"
        next_safe = "READ_EXISTING_SOURCE_AND_REQUIRE_INDEPENDENT_PREDECESSOR_PROOF"
    elif role == "X2_DESKTOP_RECOVERY":
        if not isinstance(x2_rebind, dict) or (
            x2_rebind.get("state") != "SOURCE_BOUND_REBIND_OWNER_REFRESH_REQUIRED"
            or x2_rebind.get("incident_owner") != "https://github.com/CoCivium/CoCivium/issues/181"
            or x2_rebind.get("x2_shell_started") is not False
            or x2_rebind.get("runtime_accepted") is not False
        ):
            return _hold("HOLD_X2_ROLE_REBIND_FAILED", role, source_sha256)
        decision, reason = "HOLD", "HOLD_INCUMBENT_X2_OWNER_REFRESH_REQUIRED"
        next_safe = "REFRESH_EXISTING_OWNER_181_WITHOUT_START_PROCESS_OR_PS7"
    else:
        decision, reason = "READ_ONLY_REVIEW_CANDIDATE", "NO_ACTION_AUTHORITY"
        next_safe = "VERIFY_SOURCE_AND_REQUIRE_SEPARATE_ACCEPTANCE_FOR_NEXT_EFFECT"
    return {
        "schema": SCHEMA, "work_id": WORKID, "role": role,
        "decision": decision, "reason": reason, "selected_task": candidate,
        "source_sha256": source_sha256, "source_git_blob_sha1": source_blob,
        "source_repo": "CoCivium/CoCivium",
        "source_path": "ai/roadmaps/CoTalkItOut_CausalOps_R0_20261112.csv",
        "source_snapshot_accepted": "EXACT_SOURCE_MATCHED_FOR_READ_ONLY_SELECTION",
        "next_safe_probe": next_safe,
        "prerequisites_accepted": False, "task_acceptance": "NOT_VERIFIED",
        "authority": "NONE", "dispatch_allowed": False, "external_effect": False,
        "session_created": False, "new_watcher_created": False,
        "private_payload_accessed": False,
        "independent_receiver_ack": "UNKNOWN", "all_sessions_ack": "UNKNOWN",
        "source_promoted_to_runtime": False,
        "wake_predicate": "MATERIAL_SOURCE_OR_AUTHORIZED_RECEIVER_EVIDENCE_CHANGED",
        "recovery": "RERUN_EXACT_SOURCE_READ_ONLY_CHECK_WITH_LATEST_OWNER_STATE",
        "nonclaims": NONCLAIMS,
    }

def pull(root: Path, role: str) -> dict[str, Any]:
    try:
        raw = (root / CSV_PATH.relative_to(ROOT)).read_bytes()
        raw_text = raw.decode("utf-8", errors="strict")
        validate(raw_text, expected_sha=EXPECTED_SHA256, count_gate=True)
        records = list(csv.DictReader(io.StringIO(raw_text)))
        if len(records) != EXPECTED_TASKS:
            return _hold("HOLD_SOURCE_ROW_DRIFT", role)
        bind = colocal_rebind(root, role) if role == "X2_DESKTOP_RECOVERY" else None
        return choose(records, role, x2_rebind=bind,
                      source_sha256=hashlib.sha256(raw).hexdigest(),
                      source_blob=_blob(raw))
    except (OSError, ValueError, TypeError, KeyError, UnicodeError):
        return _hold("HOLD_SOURCE_UNAVAILABLE_OR_MALFORMED", role)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--role", choices=sorted(ROLES), default="GENERAL_READ_ONLY")
    args = ap.parse_args()
    result = pull(args.root, args.role)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["decision"] != "HOLD" else 2

if __name__ == "__main__":
    raise SystemExit(main())
