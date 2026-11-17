#!/usr/bin/env python3
"""One unattended PUBLIC-SOURCE logical work turn, inside existing CoGoAll CI.

This reads and verifies a bounded, explicit public workset, reuses the existing
CoSessionShadowLedger compiler, elects ONE source-check WorkID, and emits an
exact, replayable receipt. Never wakes chats, starts models/shells, sends mail,
touches X2, changes a task, or grants authority. GitHub CI != external CoStead.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from CoSessionShadowLedger import compile_ledger

WORKSET = "ai/session-autoturn-public-sources-r1.json"
WORKSET_SCHEMA = "CoAll.CoSessionAutocycle.PublicSourceWorkset.R1"
OUT_SCHEMA = "CoAll.CoSessionAutocycle.SourceBoundTurn.R1"
_ALLOWED_PROJECTIONS = {"DEGRADED", "WAITING", "SUCCESSOR_READY", "DORMANT"}
_ID = re.compile(r"[A-Za-z0-9_.:\-]{1,140}\Z")
_SHA = re.compile(r"[0-9a-f]{40}\Z")
NONCLAIMS = [
    "LOGICAL_WORK_TURN_NE_CHAT_SESSION_CYCLE",
    "PUBLIC_SOURCE_REVIEW_NE_RUNTIME_WORK_OUTCOME",
    "GITHUB_ACTIONS_RECEIVER_NE_INDEPENDENT_EXTERNAL_RECEIVER",
    "THREE_SCOPED_SOURCES_NE_ALL_SESSION_CENSUS",
    "NO_PROVIDER_TAB_MUTATION_OR_BACKGROUND_X2_TASK",
    "SOURCE_RECORD_NE_CURRENT_X2_STATE",
    "PROOF_CHECK_NE_RICKBAR_USER_ACCEPTANCE",
    "LOCAL_IS_NOT_LANDED",
    "VALIDATION_IS_NOT_ACCEPTANCE",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
    "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
    "HASHING_IS_NOT_SEMANTIC_INGESTION",
    "DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY",
]


def hold(condition, reason):
    if not condition:
        raise ValueError("HOLD_" + reason)


def read_public(root: Path, rel: str) -> bytes:
    hold(isinstance(rel, str) and rel.startswith("ai/") and
         "\\" not in rel and ".." not in Path(rel).parts and
         not Path(rel).is_absolute(), "UNSAFE_SOURCE_PATH")
    base = root.resolve()
    p = (base / rel).resolve()
    hold(p.is_relative_to(base) and p.is_file() and not p.is_symlink(),
         "SOURCE_MISSING_OR_LINKED")
    hold(0 < p.stat().st_size <= 150000, "SOURCE_SIZE")
    b = p.read_bytes()
    hold(0 < len(b) <= 150000, "SOURCE_SIZE")
    return b


def timestamp(s):
    hold(isinstance(s, str), "TIMESTAMP_TYPE")
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("HOLD_TIMESTAMP_SHAPE") from exc
    hold(d.tzinfo is not None, "TIMESTAMP_TIMEZONE")
    return d.astimezone(timezone.utc)


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def compare_public_source_turns(previous: dict, current: dict) -> dict:
    """Advisory source-byte comparison; no authority or useful-work inference.

    Caller-provided receipts are not authenticated external ACKs or independent
    receiver observations. They must never be used to actuate, skip due work,
    or qualify real-world change without separately verified provenance.
    """
    def index(obj: dict) -> dict:
        hold(isinstance(obj, dict) and obj.get("schema") == OUT_SCHEMA
             and obj.get("state") ==
             "ONE_SOURCE_WORKID_RECHECKED_AND_LOGICAL_FLEET_PROJECTED",
             "DELTA_TURN_SCHEMA")
        hold(obj.get("receiver_ack") is False and
             obj.get("external_work_effect_claimed") is False,
             "DELTA_EFFECT_AUTHORITY")
        run = obj.get("run")
        hold(isinstance(run, dict) and
             isinstance(run.get("run_id"), str) and
             re.fullmatch(r"[1-9][0-9]*", run["run_id"]) and
             isinstance(run.get("head_sha"), str) and
             _SHA.fullmatch(run["head_sha"]), "DELTA_RUN_IDENTITY")
        inp = obj.get("input")
        sources = obj.get("sources")
        hold(isinstance(inp, dict) and inp.get("path") == WORKSET
             and isinstance(inp.get("sha256"), str)
             and re.fullmatch(r"[0-9a-f]{64}", inp["sha256"])
             and isinstance(sources, list)
             and len(sources) == inp.get("work_item_count")
             and 1 <= len(sources) <= 8, "DELTA_INPUT_SHAPE")
        found = {}
        for source in sources:
            hold(isinstance(source, dict) and
                 isinstance(source.get("work_id"), str) and
                 bool(_ID.fullmatch(source["work_id"])) and
                 isinstance(source.get("source_path"), str) and
                 source["source_path"].startswith("ai/currentness/") and
                 isinstance(source.get("source_sha256"), str) and
                 re.fullmatch(r"[0-9a-f]{64}", source["source_sha256"]),
                 "DELTA_SOURCE_SHAPE")
            key = source["work_id"]
            hold(key not in found, "DELTA_DUPLICATE_WORKID")
            found[key] = (source["source_path"], source["source_sha256"])
        return found

    earlier = index(previous)
    later = index(current)
    hold(previous["input"]["sha256"] == current["input"]["sha256"]
         and set(earlier) == set(later)
         and all(earlier[key][0] == later[key][0] for key in earlier),
         "DELTA_WORKSET_IDENTITY_DRIFT")
    # A retry of the same run is not an independent execution.
    repeated_run = previous["run"]["run_id"] == current["run"]["run_id"]
    changed = sum(earlier[key][1] != later[key][1] for key in earlier)
    # A reused run ID is not proof of a valid replay. Detect conflicting
    # immutable source/head evidence before returning the quiet classification.
    if repeated_run:
        hold(previous["run"]["head_sha"] == current["run"]["head_sha"],
             "DELTA_SAME_RUN_HEAD_DRIFT")
        hold(changed == 0, "DELTA_SAME_RUN_SOURCE_DRIFT")
    classification = ("SAME_RUN_REPLAY_NOT_NEW_EVIDENCE" if repeated_run
                      else "UNCHANGED_PUBLIC_SOURCES_RECHECK" if changed == 0
                      else "PUBLIC_SOURCE_DIGEST_CHANGE_REQUIRES_SEMANTIC_REVIEW")
    return {
        "schema": "CoAll.CoSessionAutocycle.SourceDeltaAdvisory.R1",
        "classification": classification,
        "source_digests_changed": changed,
        "source_digests_unchanged": len(earlier) - changed,
        "novel_public_source_objects": 0 if changed == 0 else None,
        "verified_useful_work_outcomes": 0,
        "receiver_ack": False,
        "gain_estimate": None,
        "prior_receipt_authenticated": False,
        "purpose": "ADVISORY_SELF_REPORTED_SOURCE_COMPARISON_ONLY",
        "nonclaims": [
            "SOURCE_DIGEST_CHANGE_NE_NEW_KNOWLEDGE",
            "REPEATED_CI_NE_USEFUL_USER_WORK",
            "SELF_REPORTED_CI_RECEIPTS_NE_EXTERNAL_RECEIVER_PROOF",
            "ADVISORY_NE_AUTHORIZED_ELECTION_OR_EFFECT",
            "NO_PROVIDER_SESSION_CYCLING",
            "NO_X2_RUNTIME_EFFECTS",
            "VALIDATION_IS_NOT_ACCEPTANCE",
        ],
    }


def compile_turn(root: Path, observed_at: str, run_id: str, attempt: str, head: str):
    root = Path(root)
    when = timestamp(observed_at)
    hold(bool(re.fullmatch(r"[1-9][0-9]*", run_id)), "RUN_ID")
    hold(bool(re.fullmatch(r"[1-9][0-9]*", attempt)), "RUN_ATTEMPT")
    hold(isinstance(head, str) and bool(_SHA.fullmatch(head)), "SOURCE_COMMIT")
    raw_workset = read_public(root, WORKSET)
    config = json.loads(raw_workset)
    hold(isinstance(config, dict) and config.get("schema") == WORKSET_SCHEMA,
         "WORKSET_SCHEMA")
    hold(config.get("state") == "PUBLIC_SAFE_LOGICAL_WORKSET_NO_PROVIDER_SESSION_CONTROL",
         "WORKSET_STATE")
    hold(config.get("source_policy") == "ONLY_REPO_RELATIVE_PUBLIC_JSON_NO_PRIVATE_ACCOUNT_OR_CHAT_DATA",
         "WORKSET_PRIVACY")
    items = config.get("work_items")
    hold(isinstance(items, list) and 1 <= len(items) <= 8, "WORKSET_BOUNDS")
    seen_ids = set()
    seen_sources = set()
    seen_priority = set()
    verified = []
    observations = []
    for row in items:
        hold(isinstance(row, dict), "WORKITEM_TYPE")
        wid, rel = row.get("work_id"), row.get("source_path")
        priority = row.get("priority")
        hold(isinstance(wid, str) and bool(_ID.fullmatch(wid))
             and wid not in seen_ids, "WORKID_IDENTITY_COLLISION")
        hold(isinstance(rel, str) and rel.startswith("ai/currentness/")
             and rel not in seen_sources, "SOURCE_SCOPE_COLLISION")
        hold(type(priority) is int and 0 <= priority <= 1000
             and priority not in seen_priority, "PRIORITY_BOUNDS_OR_COLLISION")
        hold(row.get("effect_class") == "VERIFY_PUBLIC_SOURCE_ONLY" and
             row.get("native_effects_authorized") is False and
             row.get("external_receiver_pickup") is False,
             "EFFECT_AUTHORITY")
        hold(row.get("projection") in _ALLOWED_PROJECTIONS, "PROJECTION_CLASS")
        owner = row.get("owner")
        hold(isinstance(owner, str) and
             owner.startswith("https://github.com/CoCivium/CoCivium/"),
             "OWNER_SCOPE")
        candidate = read_public(root, rel)
        data = json.loads(candidate)
        hold(isinstance(data, dict) and data.get("schema") == row.get("expected_schema")
             and data.get("state") == row.get("expected_state")
             and data.get("work_id") == wid, "SOURCE_IDENTITY_OR_STATE_DRIFT")
        hold(isinstance(data.get("nonclaims"), list) and len(data["nonclaims"]) > 1,
             "NONCLAIMS_MISSING")
        if row["role"] == "X2_DESKTOP_RECOVERY":
            hold(data.get("current_rails", {}).get("further_runtime_mutation_authorized") is False,
                 "X2_EFFECT_CEILING")
            source_when = timestamp(data["date_utc"] + "T00:00:00Z")
        else:
            source_when = timestamp(data["observed_utc"])
        hold((when - source_when).total_seconds() >= 0, "SOURCE_FROM_FUTURE")
        seen_ids.add(wid)
        seen_sources.add(rel)
        seen_priority.add(priority)
        digest = sha(candidate)
        verified.append({
            "work_id": wid,
            "role": row["role"],
            "source_path": rel,
            "source_sha256": digest,
            "source_observed_at_utc": source_when.isoformat(),
            "priority": priority,
            "owner": owner,
            "projection": row["projection"],
            "next_safe_deed": row["next_safe_deed"],
            "source_effect_verified": "PUBLIC_SOURCE_READ_ONLY",
            "native_effect_authorized": False,
        })
        observations.append({
            "session_id": "logical:" + wid,
            "observed_at": source_when.isoformat(),
            "observer": "CoSessionAutoTurnR1:PUBLIC_SOURCE_ONLY",
            "work_state": "WAITING",
            "evidence_state": "PUBLIC_HISTORICAL_SOURCE",
            "authority_ceiling": "VERIFY_PUBLIC_SOURCE_ONLY",
            "currentness": "HISTORICAL_NOT_LIVE",
            "projection": row["projection"],
            "role": row["role"],
            "source_refs": [rel + "#sha256=" + digest],
            "prior_label": None,
            "tab_close_safe": False,
            "successor_ready": False,
        })

    compiler_input = {"observations": observations}
    ledger = compile_ledger(compiler_input, WORKSET, sha(raw_workset).upper())
    hold(ledger["state"] == "SHADOW_LEDGER_COMPILED__NO_PROVIDER_MUTATION"
         and len(ledger["sessions"]) == len(items)
         and all(v == 0 for v in ledger["effects"].values()),
         "SHADOW_COMPILER_EFFECT_BOUNDARY")
    ordered = sorted(verified, key=lambda x: (-x["priority"], x["work_id"]))
    chosen = ordered[0]
    return {
        "schema": OUT_SCHEMA,
        "state": "ONE_SOURCE_WORKID_RECHECKED_AND_LOGICAL_FLEET_PROJECTED",
        "observed_at_utc": when.isoformat(),
        "run": {"run_id": run_id, "attempt": attempt, "head_sha": head,
                "executor": "EXISTING_GITHUB_ACTIONS_HOURLY_PULSE"},
        "input": {"path": WORKSET, "sha256": sha(raw_workset),
                  "work_item_count": len(verified)},
        "elected": {
            "work_id": chosen["work_id"], "role": chosen["role"],
            "owner": chosen["owner"], "source_path": chosen["source_path"],
            "source_sha256": chosen["source_sha256"],
            "performed_effect": "VERIFY_PUBLIC_SOURCE_BYTES_ONLY",
            "next_safe_deed": chosen["next_safe_deed"],
            "owner_effect_lease": "NONE",
        },
        "other_workids": [{
            "work_id": x["work_id"], "state": "LOGICAL_SHADOW_NOT_MATERIALIZED",
            "priority": x["priority"],
        } for x in ordered[1:]],
        "sources": verified,
        "shadow_ledger": ledger,
        "co_speedo": {
            "qualified_public_source_objects": len(verified),
            "bounded_logical_work_contexts": len(ledger["sessions"]),
            "source_work_turns_verified": 1,
            "provider_tabs_cycled": 0,
            "x2_processes_started": 0,
            "receiver_ack": False,
            "current_native_x2_worker_count": None,
            "current_focus_interruptions_per_minute": None,
            "total_active_provider_sessions": None,
            "human_time_saved_seconds": None,
        },
        "co_needle": {
            "bottleneck_work_id": chosen["work_id"],
            "metric_class": "QUALITATIVE_SOURCE_PRIORITY_NOT_MEASURED_GAIN",
            "next_native_gate": "EXACT_INCUMBENT_OWNER_AND_REAL_X2_QUIET_INPUT_WITNESS",
            "predicted_productivity_improvement": None,
        },
        "receiver_ack": False,
        "external_work_effect_claimed": False,
        "nonclaims": NONCLAIMS,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--check", type=Path)
    ap.add_argument("--receipt", type=Path)
    args = ap.parse_args()
    try:
        import os
        run = os.environ.get("GITHUB_RUN_ID", "1")
        attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
        head = os.environ.get("GITHUB_SHA", "0" * 40)
        if args.check:
            original = json.loads(args.check.read_text(encoding="utf-8"))
            hold(isinstance(original, dict) and original.get("schema") == OUT_SCHEMA,
                 "PRODUCER_RECEIPT_SCHEMA")
            hold(original.get("run", {}).get("run_id") == run
                 and original.get("run", {}).get("attempt") == attempt
                 and original.get("run", {}).get("head_sha") == head,
                 "PRODUCER_RUN_IDENTITY")
            expected = compile_turn(args.root, original["observed_at_utc"], run, attempt, head)
            hold(original == expected, "PRODUCER_RECEIPT_OR_SOURCE_DRIFT")
            result = {
                "schema": "CoAll.CoSessionAutocycle.JobReceiverReadback.R1",
                "state": "PASS_INDEPENDENT_CI_JOB_SOURCE_RECOMPUTE",
                "source_record_sha256": sha(args.check.read_bytes()),
                "source_work_id": expected["elected"]["work_id"],
                "run_id": run,
                "job_scope": "SAME_PROVIDER_GITHUB_JOB_NOT_EXTERNAL_RECEIVER",
                "receiver_ack": False,
                "external_work_effect_verified": False,
                "nonclaims": NONCLAIMS,
            }
        else:
            import datetime
            stamp = datetime.datetime.now(timezone.utc).isoformat()
            result = compile_turn(args.root, stamp, run, attempt, head)
        dest = args.receipt if args.check else args.output
        hold(dest is not None and not dest.exists(), "NO_CLOBBER_OUTPUT")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"state": result["state"], "work_id":
            result.get("elected", {}).get("work_id", result.get("source_work_id")),
            "receiver_ack": False, "run_id": run}, sort_keys=True))
        return 0
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"state": "HOLD_SOURCE_AUTOTURN",
                          "reason": str(exc), "receiver_ack": False}, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
