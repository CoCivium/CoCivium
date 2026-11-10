#!/usr/bin/env python3
"""CoMVP CoPre first-use canary: current public issue -> read-only CoPrePack.

No session injection, private data, runtime mutation, or receiver certification.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
import urllib.error
import urllib.request
from pathlib import Path

from CoPreContinuationR0 import compile_pack, render_continuation_input

API_URL = "https://api.github.com/repos/CoCivium/CoCivium/issues/403"
ISSUE_URL = "https://github.com/CoCivium/CoCivium/issues/403"
WORK_ID = "CoMVP.CoPrePilot.20261109"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def source_projection(raw):
    if not isinstance(raw, dict):
        raise ValueError("UNREADABLE_ISSUE")
    if raw.get("number") != 403 or raw.get("html_url") != ISSUE_URL:
        raise ValueError("WRONG_ISSUE_IDENTITY")
    if raw.get("state") != "open":
        raise ValueError("SOURCE_NOT_OPEN")
    if not isinstance(raw.get("body"), str) or "CoMVP+" not in raw["body"]:
        raise ValueError("SOURCE_CONTRACT_NOT_FOUND")
    if not isinstance(raw.get("updated_at"), str) or not raw["updated_at"]:
        raise ValueError("SOURCE_TIME_UNAVAILABLE")
    return {
        "issue": raw["number"],
        "url": raw["html_url"],
        "updated_at": raw["updated_at"],
        "state": raw["state"],
        "title": raw.get("title"),
        "body": raw["body"],
    }


def source_identity(raw):
    """Content fingerprint of two trusted-in-path source reads; not authorship proof."""
    obj = source_projection(raw)
    return "sha256:" + sha(obj)


def last_edit_age_class(raw, now_utc=None):
    """Age of issue's LAST EDIT, not GitHub API response freshness."""
    value = source_projection(raw)["updated_at"]
    try:
        edited = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return "UNPARSEABLE_LAST_EDIT"
    if edited.tzinfo is None:
        return "UNPARSEABLE_LAST_EDIT"
    observed = now_utc or datetime.now(timezone.utc)
    age_seconds = (observed - edited).total_seconds()
    if age_seconds < -300:
        return "FUTURE_LAST_EDIT_OR_CLOCK_CONFLICT"
    if age_seconds > 86400:
        return "LAST_EDIT_OLDER_THAN_24H"
    return "LAST_EDIT_WITHIN_24H"


def observation(raw, result_revision):
    p = source_projection(raw)
    return {
        "work_id": WORK_ID,
        "source_ref": ISSUE_URL,
        "source_revision": result_revision,
        "purpose": "Finish one usable read-only CoPre CLI, not expand PR #401",
        "delta_ref": "CoMVP.first-use.issue403." + result_revision,
        "observer": "unattested-readonly-cli-executor",
        "authority_ceiling": "READ_ONLY",
        "confidentiality": "PUBLIC",
        "collision_domain": "CoMVP.CoPrePilot",
        "receiver": "future-independent-first-use-receiver-UNPROVEN",
        "wake_predicate": "source issue 403 content digest changes",
        "stop_predicate": "no authorized independent receiver or no material task delta",
        "budget": {"max_work_units": 1},
        "evidence_refs": [ISSUE_URL, "git:CoPreContinuationR0.py@5a1a8cd15eb41af151c9255bee46cc7549e1acd8"],
        "next_deed": "prove exact read-only task reconstruction with an independent first-use receiver",
        "verification": "source digest, bounded authority, user task and STOP independently checked",
        "recovery_ref": ISSUE_URL,
        "failure_domain": "single-unattested-cli-executor",
        "requested_effects": ["NONE"],
        "material_delta": True,
        "wake_is_bound": True,
        # Legacy CoPre compiler's internal guard accepts only VERIFIED.
        # Here this means the source representation agreed across two reads
        # in build_report, NEVER GitHub recency, origin independence or ACK.
        "source_currentness": "VERIFIED",
    }


def build_report(first, second):
    fp = source_identity(first)
    sp = source_identity(second)
    if fp != sp:
        return {"status": "HOLD", "reason": "SOURCE_CHANGED_BETWEEN_READS", "effects_performed": 0}
    pack = compile_pack(observation(second, sp))
    if pack.get("status") != "PACK_COMPILED_READ_ONLY":
        return {"status": "HOLD", "reason": pack.get("reason", "PACK_INVALID"), "effects_performed": 0}
    prompt = render_continuation_input(pack)
    pointer = {"work_id": WORK_ID, "source_ref": ISSUE_URL, "source_revision": sp}
    return {
        "schema": "CoCivium.CoMVPCoPreFirstUse.R0",
        "status": "SOURCE_TASK_CLI_GENERATED_ONLY",
        "source_checked_twice": True,
        "source_content_consistency": "TWO_READS_MATCHED",
        "source_freshness": "UNPROVEN_TWO_READS_ARE_NOT_FRESHNESS",
        "source_last_edit_age_class": last_edit_age_class(second),
        "source_updated_at": source_projection(second)["updated_at"],
        "source_origin_independence": "UNPROVEN_SAME_PUBLIC_API",
        "observer_attestation": "UNPROVEN_LOCAL_OR_CI",
        "source_revision": sp,
        "pack_sha256": pack["pack_sha256"],
        "pack": pack,
        "continuation_input": prompt,
        "pointer": pointer,
        "pointer_bytes": len(canonical(pointer).encode("utf-8")),
        "prompt_bytes": len(prompt.encode("utf-8")),
        "effects_performed": 0,
        "receiver_ack": "UNPROVEN",
        "task_mvp": "NOT_QUALIFIED",
        "ux_acceptance": "UX_ACCEPTANCE_UNPROVEN",
    }


def fetch_issue():
    request = urllib.request.Request(
        API_URL,
        headers={"Accept": "application/vnd.github+json",
                 "User-Agent": "CoMVPCoPreFirstUseR0-readonly"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        raw = response.read(256 * 1024 + 1)
        if len(raw) > 256 * 1024:
            raise ValueError("OVERSIZE_PUBLIC_ISSUE")
    return json.loads(raw)


def selftest():
    # These R0 selftest assertions are intentionally not optimization-safe.
    # Failing closed is mandatory until converted to always-on requirements.
    if not __debug__:
        raise RuntimeError("HOLD_OPTIMIZED_MODE_SELFTEST_ASSERTS_DISABLED")
    example = {"number": 403, "html_url": ISSUE_URL, "state": "open",
               "title": "CoMVP+ acceptance", "body": "CoMVP+ task contract",
               "updated_at": "2026-11-09T10:54:01Z"}
    checks = 0
    ok = build_report(example, example)
    assert ok["status"] == "SOURCE_TASK_CLI_GENERATED_ONLY";checks += 1
    assert ok["pack"]["authority_ceiling"] == "READ_ONLY" and ok["pack"]["effects"] == 0;checks += 1
    assert ok["pack_sha256"] in ok["continuation_input"];checks += 1
    assert ok["pointer_bytes"] < ok["prompt_bytes"];checks += 1
    assert ok["receiver_ack"] == "UNPROVEN" and ok["task_mvp"] == "NOT_QUALIFIED";checks += 1
    assert ok["source_content_consistency"] == "TWO_READS_MATCHED" and ok["source_freshness"].startswith("UNPROVEN");checks += 1
    assert ok["observer_attestation"] == "UNPROVEN_LOCAL_OR_CI" and ok["pack"]["observer"] == "unattested-readonly-cli-executor";checks += 1
    stale = {**example, "updated_at": "2020-01-01T00:00:00Z"}
    old = build_report(stale, stale)
    assert old["status"] == "SOURCE_TASK_CLI_GENERATED_ONLY" and old["source_last_edit_age_class"] == "LAST_EDIT_OLDER_THAN_24H" and old["source_freshness"].startswith("UNPROVEN");checks += 1
    assert build_report(example, {**example, "updated_at": "new"})["reason"] == "SOURCE_CHANGED_BETWEEN_READS";checks += 1
    for change in ({"number": 404}, {"html_url": "https://example.test"}, {"state": "closed"},
                   {"body": ""}, {"updated_at": ""}):
        try:
            build_report({**example, **change}, {**example, **change})
            raise AssertionError("ineligible source accepted")
        except ValueError:
            checks += 1
    bad_observation=observation(example, source_identity(example))
    bad_observation["authority_ceiling"]="WRITE"
    assert compile_pack(bad_observation)["status"] == "HOLD";checks+=1
    bad_observation=observation(example, source_identity(example))
    bad_observation["material_delta"]=False
    assert compile_pack(bad_observation)["status"] == "QUIESCENT";checks+=1
    print(canonical({"schema":"CoCivium.CoMVPCoPreFirstUseSelftest.R0",
                     "cases":checks,"passed":checks,"scope":"SYNTHETIC_ONLY",
                     "effects_performed":0,"receiver_ack":"UNPROVEN"}))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--live-public-issue-403", action="store_true")
    args=parser.parse_args()
    if args.selftest:
        selftest()
    elif args.live_public_issue_403:
        try:
            first=fetch_issue()
            second=fetch_issue()
            result=build_report(first, second)
        except (ValueError, KeyError, TypeError, urllib.error.URLError, TimeoutError) as e:
            print(canonical({"status":"HOLD","reason":type(e).__name__,
                             "effects_performed":0,"receiver_ack":"UNPROVEN"}))
            raise SystemExit(2)
        print(canonical(result))
        if result["status"]!="SOURCE_TASK_CLI_GENERATED_ONLY":
            raise SystemExit(2)
    else:
        parser.error("choose --selftest or --live-public-issue-403")


if __name__ == "__main__":
    main()
