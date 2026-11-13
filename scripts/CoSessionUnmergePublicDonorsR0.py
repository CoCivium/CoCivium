#!/usr/bin/env python3
"""Bounded public-donor CoUnmerge round trip, with no provider or external effects.

The active projection is intentionally NOT self-contained: rehydration requires
the original, immutable Git-identified source bytes from independent custody.
This proves byte-for-byte source recovery from repo files, not chat recovery.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

SCHEMA = "CoSession.UnmergePublicDonorManifest.R0"
FIELDS = ("delta_id", "session_id", "subject", "epistemic_class", "relation",
          "contradictions", "tests", "source_refs", "next_receiver")
NO_EFFECTS = {"session_merges": 0, "provider_sessions_closed": 0,
              "provider_sessions_deleted": 0, "external_messages": 0,
              "device_changes": 0, "account_changes": 0}
NONCLAIMS = [
    "SOURCE_DEFINED_SESSION_ID_NE_PROVIDER_SESSION_ID",
    "PUBLIC_GIT_SOURCE_RECOVERY_NE_PRIVATE_CHAT_RECOVERY",
    "GIT_CHECKOUT_RESTORE_NE_INDEPENDENT_EXTERNAL_RECEIVER_PICKUP",
    "HASHED_BYTES_NE_SEMANTIC_INTEGRATION",
    "CONVERGENCE_NE_SESSION_CLOSE_SAFE",
]


class Hold(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Hold("HOLD_" + reason)


def git_blob_sha(blob: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(blob)).encode("ascii") + b"\0" + blob).hexdigest()


def read_donor(root: Path, item: dict) -> tuple[bytes, dict]:
    rel = item.get("path")
    require(isinstance(rel, str) and rel.startswith("ai/evolution-deltas/") and
            rel.endswith(".json") and "\\" not in rel and ".." not in Path(rel).parts,
            "SOURCE_SCOPE")
    base = root.resolve()
    path = (base / rel).resolve()
    require(path.is_relative_to(base) and path.is_file() and not path.is_symlink(),
            "MISSING_SOURCE")
    source = path.read_bytes()
    require(0 < len(source) <= 100000, "SOURCE_SIZE")
    sha = item.get("git_blob_sha")
    require(isinstance(sha, str) and len(sha) == 40 and
            git_blob_sha(source) == sha, "SOURCE_BLOB_CHANGED")
    obj = json.loads(source)
    require(isinstance(obj, dict) and obj.get("session_id") == item.get("session_id"),
            "DONOR_IDENTITY")
    require(all(k in obj for k in FIELDS), "MISSING_SOURCE_FIELDS")
    require(obj.get("confidentiality") == "PUBLIC", "NOT_PUBLIC")
    return source, obj


def compile_projection(root: Path, fixture: dict) -> dict:
    require(isinstance(fixture, dict) and fixture.get("schema") == SCHEMA, "MANIFEST_SCHEMA")
    require(fixture.get("authority") == "READ_ONLY_NO_PROVIDER_EFFECTS", "AUTHORITY")
    rows = fixture.get("records")
    require(isinstance(rows, list) and len(rows) == 3, "THREE_DONORS_REQUIRED")
    seen_ids, seen_paths, records, dissent_ids = set(), set(), [], []
    for item in rows:
        require(isinstance(item, dict), "ROW_TYPE")
        sid, rel = item.get("session_id"), item.get("path")
        require(sid and sid not in seen_ids and rel not in seen_paths, "DUPLICATE_IDENTITY")
        seen_ids.add(sid)
        seen_paths.add(rel)
        blob, source = read_donor(root, item)
        # Preserve a compact independent annotation and full source pointer.
        selected = {k: source[k] for k in FIELDS}
        records.append({
            "session_id": sid, "delta_id": source["delta_id"],
            "source_path": rel, "source_git_blob_sha": git_blob_sha(blob),
            "source_sha256": hashlib.sha256(blob).hexdigest(),
            "bytes": len(blob), "epistemic_class": source["epistemic_class"],
            "selected_fields": selected,
            "source_disposition": "PRESERVED_NOT_SUPERSEDED",
        })
        dissent_ids.extend(source["contradictions"])
    require(len({x["delta_id"] for x in records}) == 3, "DUPLICATE_DELTA")
    return {
        "schema": "CoSession.UnmergePublicProjection.R0",
        "state": "THREE_REAL_PUBLIC_DONOR_OBJECTS_INDEXED__NO_PROVIDER_EFFECTS",
        "shared_front": fixture.get("shared_front"),
        "coverage": {"source_records": 3, "distinct_source_defined_session_ids": 3,
                     "provider_chat_census": "UNPROVEN"},
        "records": records,
        "dissent": dissent_ids,
        "effects": dict(NO_EFFECTS),
        "close_safe": False,
        "delete_safe": False,
        "nonclaims": list(NONCLAIMS),
    }


def unmerge_rehydrate(root: Path, projection: dict) -> dict:
    """Recover ORIGINAL bytes from immutable source pointers; reject corruption."""
    require(projection.get("schema") == "CoSession.UnmergePublicProjection.R0",
            "PROJECTION_SCHEMA")
    records = projection.get("records")
    require(isinstance(records, list) and len(records) == 3, "PROJECTION_SCOPE")
    recovered = []
    for record in records:
        blob, source = read_donor(root, {
            "path": record.get("source_path"),
            "session_id": record.get("session_id"),
            "git_blob_sha": record.get("source_git_blob_sha"),
        })
        require(hashlib.sha256(blob).hexdigest() == record.get("source_sha256"),
                "REHYDRATION_DIGEST")
        require({k: source[k] for k in FIELDS} == record.get("selected_fields"),
                "SELECTED_FIELDS_CHANGED")
        recovered.append({
            "session_id": record["session_id"],
            "delta_id": record["delta_id"],
            "source_sha256": hashlib.sha256(blob).hexdigest(),
            "source_bytes_recovered": len(blob),
            "status": "EXACT_SOURCE_BYTES_RECOVERABLE_FROM_GIT",
        })
    return {
        "state": "PASS_THREE_PUBLIC_GIT_DONOR_ROUNDTRIP__NO_SESSION_CLOSE",
        "recovered": recovered, "effects": dict(NO_EFFECTS),
        "recipient_class": "GITHUB_CI_PROCESS_ONLY",
        "external_receiver_ack": False,
        "private_provider_history_recovered": False,
    }
