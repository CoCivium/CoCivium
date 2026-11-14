#!/usr/bin/env python3
"""CoPre cold-handoff R0: public-only GitHub CI packet across two isolated jobs.

This is *not* a CoStead or cross-provider receiver. Source is public and
read-only; no listener, browser access, background worker, model call or effects.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

from copre_path_query_r0 import discover, index_graph

SCHEMA = "CoAll.CoPre.ColdHandoff.R0"
REPO = "CoCivium/CoCivium"
FILES = ("CoPre.md", "ai/copre-seed-path-fabric-r0-20261109.json")
MAX_BYTES = 524288
MAX_MANIFEST_BYTES = 8192
MANIFEST_FIELDS = frozenset((
    "schema", "source_repo", "source_commit", "scope", "work_id", "files",
    "producer", "receiver", "independent_receiver_ack", "co_stead_pickup",
    "cross_session_sync", "effect_count",
))
RECORD_FIELDS = frozenset(("path", "sha256", "byte_count"))
PACKET_FILES = frozenset(("packet.json", "payload/CoPre.md",
                          "payload/ai/copre-seed-path-fabric-r0-20261109.json"))
PACKET_DIRS = frozenset(("payload", "payload/ai"))
NONCLAIMS = [
    "SEPARATE_GITHUB_JOB_NE_INDEPENDENT_FAILURE_DOMAIN",
    "CI_READBACK_NE_CO_STEAD_ACK",
    "SOURCE_RECOVERY_NE_RUNTIME_SURVIVAL_24H",
    "NAVIGABLE_POINTER_NE_SESSION_SYNCHRONIZATION",
    "VALIDATION_IS_NOT_ACCEPTANCE",
    "NO_COEX_CANON_OR_PUBLIC_SITE_DEPLOYMENT",
]

class Held(Exception):
    pass

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def commit_check(value):
    if not isinstance(value, str) or not re.fullmatch("[0-9a-f]{40}", value):
        raise Held("HELD_INVALID_SOURCE_COMMIT")
    return value

def safe_read(root, relative):
    if relative not in FILES:
        raise Held("HELD_NONALLOWLIST_SOURCE")
    path = Path(root) / relative
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(Path(root).resolve()):
        raise Held("HELD_MISSING_OR_LINKED_SOURCE")
    if path.stat().st_size > MAX_BYTES:
        raise Held("HELD_TOO_LARGE")
    with path.open("rb") as reader:
        raw = reader.read(MAX_BYTES + 1)
    if not raw or len(raw) > MAX_BYTES:
        raise Held("HELD_EMPTY_OR_TOO_LARGE")
    raw.decode("utf-8")
    return raw

def content_identity(commit, records):
    canonical = json.dumps({"commit": commit, "files": records},
                           sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "copre:cold:" + sha(canonical)

def records_of(root):
    return [{"path": path, "sha256": sha(safe_read(root, path)),
             "byte_count": len(safe_read(root, path))} for path in FILES]

def write_exclusive(path, raw):
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as writer:
        writer.write(raw)
        writer.flush()
        os.fsync(writer.fileno())

def emit(source_root, output_root, commit):
    """Package exact PUBLIC repo content, no private user content."""
    commit = commit_check(commit)
    output_root = Path(output_root)
    if output_root.exists():
        raise Held("HELD_PACKET_PATH_EXISTS_NO_CLOBBER")
    records = records_of(source_root)
    manifest = {
        "schema": SCHEMA,
        "source_repo": REPO,
        "source_commit": commit,
        "scope": "PUBLIC_SOURCE_ONLY",
        "work_id": content_identity(commit, records),
        "files": records,
        "producer": "GITHUB_ACTIONS_JOB",
        "receiver": "FRESH_GITHUB_ACTIONS_JOB",
        "independent_receiver_ack": False,
        "co_stead_pickup": False,
        "cross_session_sync": False,
        "effect_count": 0,
    }
    output_root.mkdir(parents=True, mode=0o700)
    payload = output_root / "payload"
    for name in FILES:
        destination = payload / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        write_exclusive(destination, safe_read(source_root, name))
    write_exclusive(output_root / "packet.json",
                    (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    return manifest

def validate_packet_tree(root):
    """No unlisted files, directories, or symlinks survive artifact download."""
    if root.is_symlink() or not root.is_dir():
        raise Held("HELD_PACKET_ROOT_UNTRUSTED")
    for folder in (root, root / "payload", root / "payload" / "ai"):
        if folder.is_symlink() or not folder.is_dir():
            raise Held("HELD_PACKET_CONTAINS_UNDECLARED_ENTRY")
        for child in folder.iterdir():
            relative = child.relative_to(root).as_posix()
            if child.is_symlink():
                if relative in PACKET_FILES:
                    raise Held("HELD_MISSING_OR_LINKED_SOURCE")
                raise Held("HELD_PACKET_CONTAINS_UNDECLARED_ENTRY")
            if child.is_dir() and relative in PACKET_DIRS:
                continue
            if child.is_file() and relative in PACKET_FILES:
                continue
            raise Held("HELD_PACKET_CONTAINS_UNDECLARED_ENTRY")


def validate(root):
    """Validate only the declared public bytes in an untrusted downloaded artifact."""
    root = Path(root)
    validate_packet_tree(root)
    manifest_file = root / "packet.json"
    if manifest_file.is_symlink() or not manifest_file.is_file():
        raise Held("HELD_MANIFEST_ABSENT_OR_LINKED")
    if manifest_file.stat().st_size > MAX_MANIFEST_BYTES:
        raise Held("HELD_MANIFEST_TOO_LARGE")
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise Held("HELD_MANIFEST_INVALID")
    if set(manifest) != MANIFEST_FIELDS:
        raise Held("HELD_MANIFEST_UNDECLARED_FIELD")
    if (manifest.get("schema") != SCHEMA or manifest.get("source_repo") != REPO or
        manifest.get("scope") != "PUBLIC_SOURCE_ONLY" or
        manifest.get("producer") != "GITHUB_ACTIONS_JOB" or
        manifest.get("receiver") != "FRESH_GITHUB_ACTIONS_JOB" or
        manifest.get("independent_receiver_ack") is not False or
        manifest.get("co_stead_pickup") is not False or
        manifest.get("cross_session_sync") is not False or
        type(manifest.get("effect_count")) is not int or manifest["effect_count"] != 0):
        raise Held("HELD_CUSTODY_OR_AUTHORITY_ESCALATION")
    commit = commit_check(manifest.get("source_commit"))
    records = manifest.get("files")
    if (not isinstance(records, list) or len(records) != len(FILES) or
        [r.get("path") for r in records if isinstance(r, dict)] != list(FILES)):
        raise Held("HELD_FILE_ALLOWLIST_OR_ORDER")
    for record in records:
        if set(record) != RECORD_FIELDS:
            raise Held("HELD_RECORD_UNDECLARED_FIELD")
        raw = safe_read(root / "payload", record["path"])
        if (not isinstance(record.get("sha256"), str) or
            record.get("sha256") != sha(raw) or
            type(record.get("byte_count")) is not int or
            record["byte_count"] != len(raw)):
            raise Held("HELD_PAYLOAD_DIGEST_MISMATCH")
    if manifest.get("work_id") != content_identity(commit, records):
        raise Held("HELD_WORK_ID_MISMATCH")
    text = safe_read(root / "payload", "CoPre.md").decode("utf-8")
    if not text.startswith("# CoPreGeneric") or "SESSION_BOOTSTRAP.md" not in text:
        raise Held("HELD_PUBLIC_FRONT_DOOR_MISSING")
    graph = json.loads(safe_read(root / "payload", FILES[1]).decode("utf-8"))
    if graph.get("schema") != "CoAll.CoSeedCoPathFabric.R0-candidate":
        raise Held("HELD_WRONG_GRAPH")
    index_graph(graph)
    navigation = discover(graph, "copre-entry", "copre-package", direction="forward")
    if navigation.get("status") != "NAVIGABLE_SOURCE_POINTER_ONLY" or navigation.get("recipient_ack") is not False:
        raise Held("HELD_GRAPH_RECOVERY_FAILED")
    return manifest, navigation

def read_public_at_commit(commit, path):
    """Verify from public immutable Git SHA, not a mutable branch alias."""
    if path not in FILES:
        raise Held("HELD_NONALLOWLIST_SOURCE")
    commit_check(commit)
    url = f"https://raw.githubusercontent.com/{REPO}/{commit}/{path}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "CoPreColdHandoff-R0/1.0", "Accept": "text/plain, application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status != 200 or response.geturl() != url:
                raise Held("HELD_REDIRECT_OR_HTTP_SOURCE")
            raw = response.read(MAX_BYTES + 1)
    except (urllib.error.URLError, TimeoutError, OSError) as err:
        raise Held("HELD_PUBLIC_REFETCH_UNAVAILABLE") from err
    if not raw or len(raw) > MAX_BYTES:
        raise Held("HELD_PUBLIC_REFETCH_SIZE")
    return raw

def accept(packet_root, readback, *, reader_id):
    """A fresh job must fetch PUBLIC source again before a positive verdict."""
    if not isinstance(reader_id, str) or not re.fullmatch("[A-Za-z0-9_.:-]{1,100}", reader_id):
        raise Held("HELD_UNQUALIFIED_READER")
    manifest, nav = validate(packet_root)
    if not callable(readback):
        raise Held("HELD_NO_INDEPENDENT_REFETCH")
    for item in manifest["files"]:
        raw = readback(manifest["source_commit"], item["path"])
        if not isinstance(raw, bytes) or sha(raw) != item["sha256"] or len(raw) != item["byte_count"]:
            raise Held("HELD_COLD_REFETCH_MISMATCH")
    return {
        "schema": "CoAll.CoPre.ColdReadbackReceipt.R0",
        "state": "CI_SEPARATE_JOB_COLD_SOURCE_READBACK_ONLY",
        "work_id": manifest["work_id"],
        "source_commit": manifest["source_commit"],
        "source_hashes": {r["path"]: r["sha256"] for r in manifest["files"]},
        "reader_id": reader_id,
        "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "navigation": nav["path"],
        "failure_domain": "GITHUB_ACTIONS_SHARED_PROVIDER",
        "distinct_job_filesystem": True,
        "source_refetched_from_immutable_git_commit": True,
        "independent_external_receiver_ack": False,
        "co_stead_pickup": False,
        "cross_session_sync": False,
        "survived_24h": False,
        "effect_count": 0,
        "nonclaims": NONCLAIMS,
    }

def main():
    ap = argparse.ArgumentParser(description="Public-only CoPre CI cold-handoff")
    sub = ap.add_subparsers(dest="mode", required=True)
    emit_parser = sub.add_parser("emit")
    emit_parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[1])
    emit_parser.add_argument("--output", type=Path, required=True)
    emit_parser.add_argument("--commit", required=True)
    accept_parser = sub.add_parser("accept")
    accept_parser.add_argument("--packet", type=Path, required=True)
    accept_parser.add_argument("--receipt", type=Path, required=True)
    accept_parser.add_argument("--reader", required=True)
    args = ap.parse_args()
    try:
        if args.mode == "emit":
            manifest = emit(args.source_root, args.output, args.commit)
            print(json.dumps({"state": "CI_PACKET_PREPARED_NO_EFFECT",
                              "work_id": manifest["work_id"], "source_commit": manifest["source_commit"]}))
        else:
            receipt = accept(args.packet, read_public_at_commit, reader_id=args.reader)
            write_exclusive(args.receipt, (json.dumps(receipt, sort_keys=True, indent=2) + "\n").encode())
            print(json.dumps({"state": receipt["state"], "work_id": receipt["work_id"],
                              "independent_external_receiver_ack": False, "co_stead_pickup": False}))
    except (Held, ValueError, KeyError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        state = str(exc) if isinstance(exc, Held) else "HELD_INVALID_OR_UNREADABLE_PACKET"
        print(json.dumps({"state": state, "effect_count": 0, "receiver_ack": False}))
        raise SystemExit(2)

if __name__ == "__main__":
    main()
