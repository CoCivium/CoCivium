#!/usr/bin/env python3
"""CoUptake R0: offline, read-only, source-bound admission for a public AI onramp.

NO model calls, training, network, live receiver, writes, or consent capture.
Verification is a Git blob digest over the exact file bytes, not a semantic
truth assessment or cryptographic author signature.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

SCHEMA = "CoAll.UptakeBridge.Manifest.R0-candidate"
VALID_INTENTS = ("discover", "contextual", "persistent_candidate", "train_candidate")
ALLOWED_EPISTEMIC = frozenset(
    ("PUBLIC_POLICY", "PUBLIC_SOURCE_CONTRACT", "PUBLIC_BOOTSTRAP",
     "PUBLIC_ARCHITECTURE_CANDIDATE")
)
BLOCKED_RECORD_KEYS = frozenset(
    ("system_prompt", "developer_prompt", "tool_instructions", "execute_command",
     "model_directive", "grant_authority", "secret", "api_key", "training_authorized")
)
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
MAX_SOURCE_BYTES = 512_000
MAX_MANIFEST_BYTES = 128_000


class AdmissionError(ValueError):
    """A manifest or its eligibility policy is invalid."""


def git_blob_sha(data: bytes) -> str:
    """Git's content-addressed SHA-1 object identity, not an author signature."""
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def safe_source_path(root: Path, name: str) -> Path:
    """Reject path traversal, absolute, symlink escapes and non-public directories."""
    if not isinstance(name, str) or not name or "\\" in name:
        raise AdmissionError("INVALID_PATH")
    pure = PurePosixPath(name)
    if pure.is_absolute() or "." in pure.parts or ".." in pure.parts:
        raise AdmissionError("INVALID_PATH")
    if pure.parts[0] not in ("ai", "docs") or len(pure.parts) < 2:
        raise AdmissionError("PATH_OUTSIDE_PUBLIC_ONRAMP")
    path = root.joinpath(*pure.parts).resolve()
    if not path.is_relative_to(root.resolve()):
        raise AdmissionError("PATH_ESCAPES_REPO")
    if not path.is_file():
        raise AdmissionError("SOURCE_NOT_PRESENT")
    if path.stat().st_size > MAX_SOURCE_BYTES:
        raise AdmissionError("SOURCE_TOO_LARGE")
    return path


def load_manifest(path: Path) -> dict:
    if path.stat().st_size > MAX_MANIFEST_BYTES:
        raise AdmissionError("MANIFEST_TOO_LARGE")
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise AdmissionError("INVALID_MANIFEST_JSON") from exc
    if not isinstance(obj, dict) or obj.get("schema") != SCHEMA:
        raise AdmissionError("UNRECOGNIZED_MANIFEST_SCHEMA")
    if obj.get("reference_test", {}).get("mutation_authority") != "NONE":
        raise AdmissionError("MANIFEST_CLAIMS_MUTATION_AUTHORITY")
    if not isinstance(obj.get("sources"), list) or not obj["sources"]:
        raise AdmissionError("EMPTY_SOURCE_SET")
    ids, paths = set(), set()
    for item in obj["sources"]:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise AdmissionError("INVALID_SOURCE_ENTRY")
        if any(key in item for key in BLOCKED_RECORD_KEYS):
            raise AdmissionError("DIRECTIVE_OR_SECRET_FIELD")
        if not isinstance(item.get("path"), str):
            raise AdmissionError("INVALID_SOURCE_PATH")
        if item["id"] in ids or item["path"] in paths:
            raise AdmissionError("DUPLICATE_SOURCE_ID_OR_PATH")
        ids.add(item["id"])
        paths.add(item["path"])
        if not isinstance(item.get("git_blob_sha"), str) or not SHA_RE.fullmatch(item["git_blob_sha"]):
            raise AdmissionError("INVALID_OBJECT_DIGEST")
        if item.get("visibility") != "PUBLIC_SAFE":
            raise AdmissionError("NOT_PUBLIC_SAFE")
        if item.get("epistemic") not in ALLOWED_EPISTEMIC:
            raise AdmissionError("UNTYPED_OR_UNKNOWN_EPISTEMIC_CLASS")
        if item.get("license_review") != "REQUIRED_FOR_REUSE_OR_TRAINING":
            raise AdmissionError("TRAINING_RIGHTS_NOT_REVIEWED")
    return obj


def admit(root: Path, manifest: dict, ids: list[str], intent: str = "discover") -> dict:
    """Return a bounded local proof. Never claim actual agent uptake or retention."""
    if intent not in VALID_INTENTS:
        raise AdmissionError("UNSUPPORTED_INTENT")
    root = root.resolve()
    available = {item["id"]: item for item in manifest["sources"]}
    if not ids or len(ids) != len(set(ids)):
        raise AdmissionError("EXPLICIT_DISTINCT_IDS_REQUIRED")
    if any(id_ not in available for id_ in ids):
        raise AdmissionError("UNKNOWN_SOURCE_ID")
    receipts = []
    for id_ in ids:
        source = available[id_]
        item = {
            "id": id_,
            "source_path": source["path"],
            "expected_git_blob_sha": source["git_blob_sha"],
            "epistemic": source["epistemic"],
            "status": "HELD",
            "reason": "",
        }
        try:
            path = safe_source_path(root, source["path"])
            raw = path.read_bytes()
            actual = git_blob_sha(raw)
            item["observed_git_blob_sha"] = actual
            if actual != source["git_blob_sha"]:
                item["reason"] = "CONTENT_DRIFT_OR_TAMPER"
            else:
                item["status"] = "LOCAL_SOURCE_BOUND"
                item["reason"] = "EXACT_BYTES_VERIFIED_NOT_SEMANTIC_ADOPTION"
        except (AdmissionError, PermissionError, OSError) as exc:
            item["reason"] = str(exc) or "SOURCE_READ_FAILED"
        receipts.append(item)

    bound = sum(x["status"] == "LOCAL_SOURCE_BOUND" for x in receipts)
    held = len(receipts) - bound
    effect = "LOCAL_SOURCE_BIND_ONLY" if not held else "PARTIAL_OR_HELD_LOCAL_SOURCE_BIND"
    intent_result = "READ_ONLY"
    if intent == "persistent_candidate":
        intent_result = "MEMORY_CANDIDATE_ONLY_NO_STORAGE_OR_CONSENT_PROOF"
    elif intent == "train_candidate":
        intent_result = "HELD_NO_WEIGHT_TRAINING_RIGHTS_CAPABILITY_OR_RUN"
    elif intent == "contextual":
        intent_result = "CONTEXT_PACKET_CANDIDATE_NOT_EXTERNAL_MODEL_USE"
    return {
        "schema": "CoAll.UptakeBridge.LocalReceipt.R0",
        "effect_boundary": effect,
        "intent": intent,
        "intent_result": intent_result,
        "source_count": len(receipts),
        "local_bound": bound,
        "held": held,
        "sources": receipts,
        "external_agent_fetch": "NOT_OBSERVED",
        "independent_receiver_ack": "NOT_OBSERVED",
        "independent_cold_restore": "NOT_OBSERVED",
        "model_weight_change": "NOT_PERFORMED",
        "persistent_memory_write": "NOT_PERFORMED",
        "authority_granted": "NONE",
        "disclosure": "PUBLIC_SOURCE_ONLY_NON_DIRECTIVE",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify pinned public AI onramp sources with no external effects")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--source-id", action="append", default=[],
                        help="One or more explicit source IDs. Defaults to only the AI/IA onramp.")
    parser.add_argument("--intent", choices=VALID_INTENTS, default="discover")
    args = parser.parse_args(argv)
    root = args.repo_root.resolve()
    manifest_path = args.manifest or root / "ai/uptake/couptake-manifest-r0.json"
    try:
        manifest = load_manifest(manifest_path)
        ids = args.source_id or ["ai_ia_onramp"]
        result = admit(root, manifest, ids, args.intent)
    except (AdmissionError, OSError) as exc:
        print(json.dumps({"schema":"CoAll.UptakeBridge.LocalReceipt.R0","effect_boundary":"HELD",
            "reason":str(exc),"authority_granted":"NONE"},sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result["held"] == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
