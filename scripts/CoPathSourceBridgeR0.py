#!/usr/bin/env python3
"""CoSeed+ / CoPath+ role-bound source reader R0.

Reuses existing PUBLIC main CoPre/CoSeed/CoPath sources, plus a public draft
session donor; never contacts or speaks for external receivers. Local git-tree
readback is a bounded source check, not independent receiver pickup, CoEx,
canon, automatic fan-out, or complete cross-front integration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

SCHEMA = "CoAll.CoPath.SessionFrontBridge.R0"
REPORT = "CoAll.CoPath.SourceReadback.R0"
MAX_NODES = 40
MAX_ROUTE = 8
MAX_BYTES = 250_000
NAME = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")
PIN = re.compile(r"^[0-9a-f]{40}$")


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def git_blob(data):
    header = b"blob " + str(len(data)).encode() + b"\x00"
    return hashlib.sha1(header + data).hexdigest()


def must(test, message):
    if not test:
        raise ValueError(message)


def validate(manifest):
    must(isinstance(manifest, dict) and manifest.get("schema") == SCHEMA,
         "INVALID_SCHEMA")
    must(manifest.get("path_rules", {}).get("external_effect_authority") == "NONE",
         "EFFECT_AUTHORITY_NOT_FENCED")
    must(manifest.get("path_rules", {}).get("no_auto_fanout") is True,
         "AUTOFANOUT_NOT_FENCED")
    must(manifest.get("path_rules", {}).get("no_overwrite") is True,
         "NO_CLOBBER_NOT_FENCED")
    sources = manifest.get("sources")
    must(isinstance(sources, list) and 1 <= len(sources) <= MAX_NODES,
         "UNBOUNDED_SOURCES")
    source_by_id = {}
    for source in sources:
        must(isinstance(source, dict), "BAD_SOURCE")
        key, path = source.get("id"), source.get("path")
        must(isinstance(key, str) and NAME.fullmatch(key), "BAD_SOURCE_ID")
        must(key not in source_by_id, "DUPLICATE_SOURCE_ID")
        must(source.get("branch") in ("main", "candidate", "corun"), "BAD_BRANCH")
        must(isinstance(path, str) and path and not path.startswith("/")
             and "\\" not in path and ".." not in path.split("/"),
             "UNSAFE_PATH")
        must(isinstance(source.get("git_blob_sha1"), str)
             and PIN.fullmatch(source["git_blob_sha1"]), "BAD_SOURCE_PIN")
        must(source.get("custody") == "PUBLIC_REPO_SOURCE_ONLY",
             "UNKNOWN_PUBLICATION_CLASS")
        must(source.get("receiver_ack") is None, "SELF_REPORTED_RECEIVER_ACK")
        source_by_id[key] = source
    for root in manifest.get("source_roots", []):
        must(root.get("id") in source_by_id, "UNKNOWN_UPSTREAM_ROOT")
    routes = manifest.get("routes")
    must(isinstance(routes, dict) and 1 <= len(routes) <= 16, "BAD_ROUTES")
    for role, ids in routes.items():
        must(isinstance(role, str) and NAME.fullmatch(role), "BAD_ROLE")
        must(isinstance(ids, list) and 1 <= len(ids) <= MAX_ROUTE,
             "UNBOUNDED_ROLE_ROUTE")
        must(len(ids) == len(set(ids)), "DUPLICATE_ROUTE_SOURCE")
        must(set(ids).issubset(source_by_id), "UNRESOLVED_ROUTE")
        must(ids[0] == "copre-entry", "MISSING_COMMON_ENTRY")
    must(manifest.get("selected_receiver_readproof_state") == "NONE",
         "INVALID_RECEIVER_CLAIM")
    must(len(manifest.get("website_mirrors", [])) == 3
         and all(m.get("verified") is False for m
                 in manifest["website_mirrors"]),
         "MIRRORS_UNEARNED")
    return source_by_id


def git_reader(root, main_ref, candidate_ref, corun_ref):
    def get_bytes(branch, path):
        ref = {"main": main_ref, "candidate": candidate_ref,
               "corun": corun_ref}[branch]
        result = subprocess.run(["git", "-C", str(root), "show",
                                 ref + ":" + path], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, check=False)
        if result.returncode:
            raise OSError("MISSING_GIT_SOURCE:" + branch + ":" + path)
        if len(result.stdout) > MAX_BYTES:
            raise OSError("OVERSIZE_GIT_SOURCE:" + branch + ":" + path)
        return result.stdout
    return get_bytes


def git_pinned_reader(root):
    """Look up an immutable Git blob when the moving branch has changed."""
    def read_sha(sha1):
        must(isinstance(sha1, str) and PIN.fullmatch(sha1), "BAD_PIN")
        result = subprocess.run(["git", "-C", str(root), "cat-file",
                                 "blob", sha1], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, check=False)
        if result.returncode:
            raise OSError("PINNED_GIT_OBJECT_UNAVAILABLE")
        if len(result.stdout) > MAX_BYTES:
            raise OSError("OVERSIZE_PINNED_GIT_OBJECT")
        return result.stdout
    return read_sha


def assess(manifest, role, read_source, read_pinned=None):
    """Preserve recoverable historical pins without misclassifying drift as loss."""
    sources = validate(manifest)
    must(role in manifest["routes"], "UNKNOWN_ROLE")
    items = []
    for key in manifest["routes"][role]:
        source = sources[key]
        pin = source["git_blob_sha1"]
        try:
            current = read_source(source["branch"], source["path"])
            if len(current) > MAX_BYTES:
                raise OSError("OVERSIZE")
            current_sha = git_blob(current)
        except OSError:
            current, current_sha = None, None
        currentness = ("CURRENT_MATCHES_PIN" if current_sha == pin else
                       "CURRENT_MOVED" if current_sha is not None else
                       "CURRENT_UNAVAILABLE")
        if current_sha == pin:
            chosen = current
            state = "EXACT_CURRENT_SOURCE_READBACK"
        else:
            try:
                if read_pinned is None:
                    raise OSError("NO_HISTORICAL_BLOB_READER")
                historic = read_pinned(pin)
                if len(historic) > MAX_BYTES or git_blob(historic) != pin:
                    raise OSError("HISTORICAL_BLOB_MISMATCH")
                chosen = historic
                state = "EXACT_HISTORICAL_SOURCE_RECOVERED__CURRENTNESS_HELD"
            except OSError:
                chosen = None
                state = "HELD_SOURCE_UNVERIFIED"
        items.append({
            "source_id": key, "branch": source["branch"],
            "path": source["path"], "source_blob_expected": pin,
            "current_tree_blob_actual": current_sha,
            "source_currentness": currentness,
            "selected_pinned_blob_actual": git_blob(chosen) if chosen is not None else None,
            "source_sha256_actual": hashlib.sha256(chosen).hexdigest()
                                    if chosen is not None else None,
            "source_bytes": len(chosen) if chosen is not None else None,
            "readback_state": state, "receiver_ack": None,
            "historical_path_binding": "PREVIOUS_GITHUB_CONNECTOR_OBSERVATION"
        })
    verified = sum(x["readback_state"].startswith("EXACT_") for x in items)
    current_count = sum(x["readback_state"] == "EXACT_CURRENT_SOURCE_READBACK"
                        for x in items)
    challenged = [x["source_id"] for x in items
                  if x["readback_state"] ==
                  "EXACT_HISTORICAL_SOURCE_RECOVERED__CURRENTNESS_HELD"]
    status = ("HELD_SOURCE_PATH_UNVERIFIED" if verified != len(items)
              else "HISTORICAL_PINS_RECOVERABLE__CURRENTNESS_HELD" if challenged
              else "SOURCE_PATH_READBACK__NOT_PICKUP")
    return {
        "schema": REPORT,
        "work_id": manifest["work_id"],
        "chosen_role": role,
        "source_entry": manifest["source_entry"],
        "source_roots": manifest["source_roots"],
        "route": items,
        "source_readbacks": verified,
        "current_source_readbacks": current_count,
        "currentness_challenges": challenged,
        "total": len(items),
        "status": status,
        "scope": "LOCAL_GIT_CI_SOURCE_READ_ONLY",
        "receiver_identity": None,
        "receiver_acknowledged": False,
        "cross_front_integration": "NOT_ESTABLISHED",
        "public_mirrors_qualified": False,
        "source_readback_ne_receiver_pickup": True,
        "missing_history": "UNKNOWN_NOT_CENSUSED",
        "effects": "NONE",
        "next_gate": ("AUTHORIZED_INDEPENDENT_RECEIVER_EXACT_OBJECT_READ"
                      "_PLUS_USEFUL_TASK_AND_RECOVERY_PROOF"),
        "nonclaims": list(manifest["nonclaims"]) +
                    ["HISTORICAL_BLOB_NE_CURRENT_MAIN",
                     "HISTORICAL_BLOB_NE_REVALIDATED_PATH_BINDING"],
    }


def write_receipt(path, result):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(canonical(result))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--main-ref", default="origin/main")
    parser.add_argument("--candidate-ref", default="HEAD")
    parser.add_argument("--corun-ref", default="origin/corun-donor")
    parser.add_argument("--role", required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        proof = assess(manifest, args.role, git_reader(
            args.repo_root, args.main_ref, args.candidate_ref,
            args.corun_ref),
            git_pinned_reader(args.repo_root))
        if args.out:
            digest = write_receipt(args.out, proof)
            proof["report_sha256"] = digest
        print(json.dumps(proof, sort_keys=True))
        return 0 if proof["source_readbacks"] == proof["total"] or (
            not args.strict) else 2
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("FAIL_CLOSED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
