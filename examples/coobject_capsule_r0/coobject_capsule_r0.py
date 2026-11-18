#!/usr/bin/env python3
"""Offline CoObject R0 micro-prodlet: pack, inspect, restore, and question-bridge.

No network, no execution of packed bytes, no issuer/authority inference.
The two local replicas do NOT represent independent physical fault domains.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "CoCivium.CoObject.OfflineCapsule.R0"
MAX_CONTENT = 16 * 1024 * 1024
MAX_MANIFEST = 32 * 1024
COPIES = ("payload.bin", "recovery.bin")
KINDS = ("document", "data", "source", "question", "reference", "service_spec")
SAFE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$")

class CapsuleError(Exception):
    pass

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def require(cond: bool, reason: str) -> None:
    if not cond:
        raise CapsuleError(reason)

def json_out(obj: dict[str, Any]) -> None:
    print(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=True))

def file_bytes(p: Path, max_bytes: int) -> bytes:
    require(p.is_file() and not p.is_symlink(), "NOT_REGULAR_FILE_OR_SYMLINK:" + p.name)
    require(p.stat().st_size <= max_bytes, "OVERSIZE:" + p.name)
    return p.read_bytes()

def manifest_for(folder: Path) -> dict[str, Any]:
    require(folder.is_dir() and not folder.is_symlink(), "INVALID_CAPSULE_ROOT")
    try:
        raw = file_bytes(folder / "manifest.json", MAX_MANIFEST)
        m = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, ValueError) as ex:
        raise CapsuleError("MANIFEST_UNREADABLE") from ex
    require(isinstance(m, dict) and m.get("schema") == SCHEMA, "WRONG_SCHEMA")
    for k in ("object_id", "title", "kind", "content_sha256", "content_bytes", "copies", "authority", "privacy", "minimum_use"):
        require(k in m, "MISSING_FIELD:" + k)
    require(isinstance(m["object_id"], str) and SAFE.fullmatch(m["object_id"]) is not None, "BAD_ID")
    require(isinstance(m["title"], str) and 0 < len(m["title"]) <= 160, "BAD_TITLE")
    require(m["kind"] in KINDS, "BAD_KIND")
    require(isinstance(m["content_sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", m["content_sha256"]) is not None, "BAD_DIGEST")
    require(type(m["content_bytes"]) is int and 0 <= m["content_bytes"] <= MAX_CONTENT, "BAD_LENGTH")
    require(m["copies"] == list(COPIES), "NONCANONICAL_COPY_PATHS")
    require(m["authority"] == "DATA_ONLY_NO_EXECUTION", "AUTHORITY_ESCALATION")
    require(m["privacy"] == "LOCAL_PRIVATE_BY_DEFAULT", "UNEXPECTED_PRIVACY")
    require(isinstance(m["minimum_use"], str) and bool(m["minimum_use"].strip()), "MISSING_MINIMUM_USE")
    return m

def verify(folder: Path) -> dict[str, Any]:
    m = manifest_for(folder)
    copies: dict[str, str] = {}
    valid: list[str] = []
    for name in COPIES:
        p = folder / name
        if not p.exists() and not p.is_symlink():
            copies[name] = "MISSING"
            continue
        try:
            b = file_bytes(p, MAX_CONTENT)
            if len(b) == m["content_bytes"] and digest(b) == m["content_sha256"]:
                copies[name] = "VALID_LOCAL_COPY"
                valid.append(name)
            else:
                copies[name] = "CORRUPT_OR_WRONG_SOURCE"
        except (OSError, CapsuleError):
            copies[name] = "UNSAFE_OR_UNREADABLE"
    state = "READY_LOCAL_TWO_COPIES" if len(valid) == 2 else "DEGRADED_LOCAL_ONE_COPY" if len(valid) == 1 else "HELD_NO_VALID_LOCAL_COPY"
    return {
        "object_id": m["object_id"], "kind": m["kind"], "title": m["title"],
        "minimum_use": m["minimum_use"], "content_sha256": m["content_sha256"],
        "status": state, "copies": copies, "valid_copies": valid,
        "independent_physical_fault_domains_verified": False,
        "independent_origin_authentication_verified": False,
        "receiver_acceptance_verified": False, "public_release_verified": False,
        "executable_authority": "NONE", "observed_at_utc": datetime.now(timezone.utc).isoformat(),
    }

def pack(source: Path, dest: Path, title: str, kind: str, purpose: str) -> dict[str, Any]:
    data = file_bytes(source, MAX_CONTENT)
    require(kind in KINDS and title.strip() and purpose.strip(), "INVALID_KIND_OR_PURPOSE")
    sha = digest(data)
    oid = "coobj-" + sha[:20]
    require(not dest.exists() and not dest.is_symlink(), "CAPSULE_DEST_ALREADY_EXISTS")
    require(dest.parent.is_dir(), "CAPSULE_PARENT_MISSING")
    dest.mkdir()
    m = {
        "schema": SCHEMA, "object_id": oid, "version": "r0", "title": title[:160],
        "kind": kind, "minimum_use": purpose, "content_sha256": sha,
        "content_bytes": len(data), "copies": list(COPIES),
        "authority": "DATA_ONLY_NO_EXECUTION", "privacy": "LOCAL_PRIVATE_BY_DEFAULT",
        "source_basename": source.name, "source_authenticity": "SELF_PACKAGED_NOT_EXTERNALLY_SIGNED",
        "dependency_contract": "PYTHON_STDLIB_TO_INSPECT_AND_RESTORE",
        "fault_domain_notice": "TWO_LOCAL_COPIES_DO_NOT_PROVE_INDEPENDENT_STORAGE_OR_OFF_HOST_SURVIVAL",
        "projection_loss": "Capsule manifest does not include historical conversation context, permissions or external references",
        "reconstruction_status": "CAN_RESTORE_FILE_FROM_ONE_VALID_LOCAL_COPY_ONLY",
        "wake_condition": "MATERIAL_CONTENT_CHANGE_OR_COPY_FAILURE",
        "hypothesis_relation_authority": "NONE",
        "receiver_readproof": None,
    }
    try:
        for n in COPIES:
            (dest / n).write_bytes(data)
        (dest / "manifest.json").write_text(json.dumps(m, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    except Exception:
        for n in (*COPIES, "manifest.json"):
            (dest / n).unlink(missing_ok=True)
        dest.rmdir()
        raise
    return verify(dest)

def restore(folder: Path, destination: Path) -> dict[str, Any]:
    evidence = verify(folder)
    require(bool(evidence["valid_copies"]), "HELD_NO_VALID_COPY_NO_RESTORE")
    require(destination.parent.is_dir(), "RESTORE_PARENT_MISSING")
    require(not destination.is_dir(), "RESTORE_TARGET_IS_DIRECTORY")
    source_name = evidence["valid_copies"][0]
    data = file_bytes(folder / source_name, MAX_CONTENT)
    require(digest(data) == evidence["content_sha256"], "SOURCE_CHANGED_AFTER_VERIFY")
    try:
        with destination.open("xb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
    except FileExistsError as ex:
        raise CapsuleError("RESTORE_NO_CLOBBER") from ex
    return {"state": "LOCAL_FILE_RESTORED", "source_copy": source_name,
            "object_id": evidence["object_id"], "destination_name": destination.name,
            "sha256": digest(data), "receiver_ack": False, "independent_storage": False}

def relate(left: Path, right: Path, seed: int) -> dict[str, Any]:
    a, b = verify(left), verify(right)
    require(a["valid_copies"] and b["valid_copies"], "CANNOT_RELATE_UNVERIFIED_SOURCE")
    require(a["object_id"] != b["object_id"], "SAME_OBJECT_NOT_AN_UNEXPECTED_BRIDGE")
    lenses = ("recovery", "translation_loss", "receiver_accessibility", "contradiction", "optional_dependency", "counterexample")
    pair = "::".join(sorted([a["object_id"], b["object_id"]]))
    index = int(digest((pair + ":" + str(seed)).encode("utf-8")), 16) % len(lenses)
    lens = lenses[index]
    return {"state": "SERENDIPITY_CANDIDATE_ONLY", "seed": seed, "lens": lens,
            "left_id": a["object_id"], "right_id": b["object_id"],
            "question": "Might " + a["title"] + " and " + b["title"] + " reveal a useful " + lens + " relation?",
            "required_discriminator": "Define a bounded, measurable gain over separate unchanged objects; seek an independent counterexample",
            "evidence": "NOT_TESTED", "new_relation_granted": False, "authority": "NONE",
            "source_integrity_prechecked": True, "randomness": "DETERMINISTIC_SEEDED_HEURISTIC_NOT_INDEPENDENT_DISCOVERY"}

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="op", required=True)
    a = sub.add_parser("pack", help="Create a whole, offline, no-network local capsule")
    a.add_argument("source", type=Path); a.add_argument("dest", type=Path)
    a.add_argument("--title", required=True); a.add_argument("--kind", choices=KINDS, required=True)
    a.add_argument("--purpose", required=True)
    a = sub.add_parser("check"); a.add_argument("folder", type=Path)
    a = sub.add_parser("restore"); a.add_argument("folder", type=Path); a.add_argument("destination", type=Path)
    a = sub.add_parser("relate"); a.add_argument("left", type=Path); a.add_argument("right", type=Path); a.add_argument("--seed", type=int, default=0)
    args = p.parse_args(argv)
    try:
        if args.op == "pack": result = pack(args.source, args.dest, args.title, args.kind, args.purpose)
        elif args.op == "check": result = verify(args.folder)
        elif args.op == "restore": result = restore(args.folder, args.destination)
        else: result = relate(args.left, args.right, args.seed)
        json_out(result)
        return 2 if result.get("status") == "HELD_NO_VALID_LOCAL_COPY" else 0
    except (CapsuleError, OSError) as ex:
        json_out({"state": "HELD_FAIL_CLOSED", "reason": str(ex)})
        return 2

if __name__ == "__main__":
    sys.exit(main())
