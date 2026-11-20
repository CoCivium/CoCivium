#!/usr/bin/env python3
"""Deterministic CoNod exact-message alias / pinned-source rebind gate R0.

Pure, no network, no device input, no subprocess, no background work,
no authority grants. Source observations must be supplied by a real reader;
fixtures are NOT independent receiver readproof.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

_BLOB = re.compile(r"[a-f0-9]{40}\Z")


def classify_message(text: object) -> str:
    """Never scan arbitrary text for triggers or swallow explicit user content."""
    if not isinstance(text, str):
        return "NO_ALIAS"
    normalized = text.strip()
    if normalized in ("'", "CoNod"):
        return "REBIND_REQUEST"
    return "EXPLICIT_TEXT_NOT_ALIAS" if normalized else "NO_ALIAS"


def _parse_utc(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def validate_manifest(manifest: object) -> bool:
    if not isinstance(manifest, dict):
        return False
    if manifest.get("schema") != "CoCivium.CoNod.RebindIntent.R0":
        return False
    if manifest.get("state") != "CANDIDATE_SOURCE_ONLY_NOT_GOVERNING":
        return False
    if manifest.get("alias") != "'" or manifest.get("explicit_alias") != "CoNod":
        return False
    roots = manifest.get("public_source_roots")
    if not isinstance(roots, list) or len(roots) != 4:
        return False
    paths = [v.get("path") for v in roots if isinstance(v, dict)]
    if len(paths) != 4 or len(set(paths)) != 4:
        return False
    if any(not isinstance(v.get("git_blob_sha1"), str)
           or not _BLOB.fullmatch(v["git_blob_sha1"])
           or not isinstance(v["path"], str)
           for v in roots):
        return False
    resolution = manifest.get("resolution")
    if not isinstance(resolution, dict):
        return False
    max_age = resolution.get("max_source_age_seconds_for_readiness")
    if type(max_age) is not int or not 1 <= max_age <= 86400:
        return False
    return manifest.get("default_authority") == "NONE_FROM_ALIAS"


def rebind(manifest: object, message: object, *, work_id: object = None,
           role: object = None, receiver: object = None,
           observations: object = None, now_utc: object = None) -> dict:
    """Return a proposal, never perform work or grant permission.

    observations map path to {git_blob_sha1, observed_utc}; this is a local
    evidence-input contract. A caller must independently authenticate the reader.
    """
    state = classify_message(message)
    result = {
        "schema": "CoCivium.CoNod.RebindDecision.R0",
        "state": state,
        "effect_authority": "NONE",
        "effect_executions": 0,
        "receiver_ack": False,
        "one_next": None,
    }
    if state != "REBIND_REQUEST":
        return result
    if not validate_manifest(manifest):
        result["state"] = "HOLD_INVALID_OR_AMBIGUOUS_MANIFEST"
        return result
    if not isinstance(work_id, str) or not work_id.strip() or len(work_id) > 256:
        result["state"] = "HOLD_UNBOUND_WORKID"
        return result
    if not isinstance(role, str) or not role.strip() or len(role) > 128:
        result["state"] = "HOLD_UNBOUND_ROLE"
        return result
    if not isinstance(receiver, str) or not receiver.strip() or len(receiver) > 128:
        result["state"] = "HOLD_UNBOUND_RECEIVER"
        return result
    now = _parse_utc(now_utc)
    if now is None or not isinstance(observations, dict):
        result["state"] = "HOLD_MISSING_SOURCE_OBSERVATIONS"
        return result
    age_ceiling = manifest["resolution"]["max_source_age_seconds_for_readiness"]
    for root in manifest["public_source_roots"]:
        observed = observations.get(root["path"])
        if not isinstance(observed, dict):
            result["state"] = "HOLD_MISSING_SOURCE_OBSERVATIONS"
            return result
        digest = observed.get("git_blob_sha1")
        if digest != root["git_blob_sha1"]:
            result["state"] = "HOLD_SOURCE_HASH_MISMATCH"
            return result
        t = _parse_utc(observed.get("observed_utc"))
        if t is None or (now - t).total_seconds() < 0:
            result["state"] = "HOLD_INVALID_OBSERVATION_TIME"
            return result
        if (now - t).total_seconds() > age_ceiling:
            result["state"] = "HOLD_STALE_SOURCE_OBSERVATION"
            return result
    result.update({
        "state": "QUALIFIED_READ_ONLY_REBIND_PROPOSAL",
        "work_id": work_id,
        "role": role,
        "receiver": receiver,
        "source_pin_count": len(manifest["public_source_roots"]),
        "one_next": "RECONCILE_PRIORS_THEN_ELECT_ONE_SAFE_DEED_UNDER_SEPARATE_AUTHORITY",
        "source_scope": "SUPPLIED_OBSERVATIONS_NOT_AUTHENTICATED_BY_THIS_FUNCTION",
    })
    return result


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--work-id")
    parser.add_argument("--role")
    parser.add_argument("--receiver")
    parser.add_argument("--observations")
    parser.add_argument("--now-utc")
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    observations = (json.loads(Path(args.observations).read_text(encoding="utf-8"))
                    if args.observations else None)
    decision = rebind(manifest, args.message, work_id=args.work_id,
                      role=args.role, receiver=args.receiver,
                      observations=observations, now_utc=args.now_utc)
    print(json.dumps(decision, sort_keys=True, ensure_ascii=True))
    return 0 if decision["state"] in (
        "QUALIFIED_READ_ONLY_REBIND_PROPOSAL", "EXPLICIT_TEXT_NOT_ALIAS", "NO_ALIAS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
