#!/usr/bin/env python3
"""Public-synthetic CoObject cross-job artifact handoff. No network or secrets.

Producer packages exact bounded bytes; receiver independently checks against an
expected literal committed in *this* source file before testing local recovery.
Never infer external receiver ACK, source authenticity, independent storage
fault-domains, deployed CoStead, X2 availability or usable product status.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from coobject_capsule_r0 import pack, verify, restore, CapsuleError, digest, manifest_for

SCHEMA = "CoCivium.CoObject.CrossJobSyntheticArtifact.R0"
READBACK_SCHEMA = "CoCivium.CoObject.CrossJobSourceReadback.R0"
LITERAL = b"CoCivium CoObject R0 public synthetic cross-job file.\nNo user content, credentials or real external effects.\n"
OBJECT_TITLE = "Cross-job public synthetic CoObject"
OBJECT_USE = "Recover exact synthetic bytes after one local replica failure"
ALLOWED_ENVELOPE = {"schema", "object_id", "source_sha256", "source_bytes", "manifest_sha256", "authority", "content_class", "producer_claim", "receiver_ack", "independent_storage_verified"}

class Held(ValueError):
    pass

def require(cond: bool, msg: str) -> None:
    if not cond:
        raise Held(msg)

def _load_json_strict(path: Path) -> dict:
    require(path.is_file() and not path.is_symlink(), "MISSING_OR_UNSAFE_ENVELOPE")
    require(path.stat().st_size <= 32768, "OVERSIZE_ENVELOPE")
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, ValueError, OSError) as exc:
        raise Held("INVALID_ENVELOPE_JSON") from exc
    require(isinstance(obj, dict) and set(obj) == ALLOWED_ENVELOPE, "ENVELOPE_FIELDS_DIVERGED")
    return obj

def produce(root: Path) -> dict:
    require(not root.exists() and not root.is_symlink(), "NO_PRODUCER_OVERWRITE")
    require(root.parent.is_dir(), "PARENT_NOT_FOUND")
    root.mkdir()
    source = root / "source.txt"
    source.write_bytes(LITERAL)
    try:
        result = pack(source, root / "capsule", OBJECT_TITLE, "document", OBJECT_USE)
        require(result["status"] == "READY_LOCAL_TWO_COPIES", "PRODUCER_CAPSULE_NOT_READY")
        record = {
            "schema": SCHEMA,
            "object_id": result["object_id"],
            "source_sha256": digest(LITERAL),
            "source_bytes": len(LITERAL),
            "manifest_sha256": digest((root / "capsule" / "manifest.json").read_bytes()),
            "authority": "DATA_ONLY_NO_EXECUTION",
            "content_class": "PUBLIC_SYNTHETIC_FIXED_LITERAL",
            "producer_claim": "CAPSULE_CREATED_ONE_CI_JOB",
            "receiver_ack": None,
            "independent_storage_verified": False,
        }
        (root / "handoff.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    finally:
        source.unlink(missing_ok=True)
    return record

def consume(root: Path, receipt: Path) -> dict:
    require(root.is_dir() and not root.is_symlink(), "INVALID_ARTIFACT_ROOT")
    require({p.name for p in root.iterdir()} == {"capsule", "handoff.json"}, "ARTIFACT_ROOT_MISMATCH")
    capsule = root / "capsule"
    require(capsule.is_dir() and not capsule.is_symlink(), "UNSAFE_CAPSULE_ROOT")
    require({p.name for p in capsule.iterdir()} == {"manifest.json", "payload.bin", "recovery.bin"}, "CAPSULE_FILESET_MISMATCH")
    record = _load_json_strict(root / "handoff.json")
    require(record["schema"] == SCHEMA, "WRONG_HANDOFF_SCHEMA")
    require(record["authority"] == "DATA_ONLY_NO_EXECUTION", "AUTHORITY_ESCALATION")
    require(record["content_class"] == "PUBLIC_SYNTHETIC_FIXED_LITERAL", "UNSAFE_CONTENT_CLASS")
    require(record["producer_claim"] == "CAPSULE_CREATED_ONE_CI_JOB", "PRODUCER_CLAIM_CHANGED")
    require(record["receiver_ack"] is None and record["independent_storage_verified"] is False, "FABRICATED_PROOF")
    # Verify independently against the literal in the receiver's source, not only
    # the author's self-packaged manifest or claimed envelope digest.
    expected = digest(LITERAL)
    require(record["source_sha256"] == expected and record["source_bytes"] == len(LITERAL), "UNEXPECTED_SOURCE_CONTENT")
    actual_manifest = capsule / "manifest.json"
    require(actual_manifest.is_file() and not actual_manifest.is_symlink(), "UNSAFE_MANIFEST")
    require(record["manifest_sha256"] == digest(actual_manifest.read_bytes()), "MANIFEST_TRANSFER_TAMPER")
    meta = manifest_for(capsule)
    require(meta["object_id"] == record["object_id"] and meta["content_sha256"] == expected, "MANIFEST_SOURCE_MISMATCH")
    require(meta["title"] == OBJECT_TITLE and meta["minimum_use"] == OBJECT_USE and meta["kind"] == "document", "OBJECT_CONTRACT_CHANGED")
    first = verify(capsule)
    require(first["status"] == "READY_LOCAL_TWO_COPIES", "INCOMPLETE_TRANSFER")
    (capsule / "payload.bin").unlink()
    degraded = verify(capsule)
    require(degraded["status"] == "DEGRADED_LOCAL_ONE_COPY", "DEGRADED_STATE_INCORRECT")
    require(not receipt.exists() and receipt.parent.is_dir(), "RECEIPT_DEST_NOT_CLEAN")
    restored = receipt.with_name("restored.txt")
    require(not restored.exists(), "RESTORE_DEST_EXISTS")
    proof = restore(capsule, restored)
    require(restored.read_bytes() == LITERAL and proof["sha256"] == expected, "RESTORE_MISMATCH")
    output = {
        "schema": READBACK_SCHEMA,
        "state": "CROSS_JOB_SYNTHETIC_RECONSTRUCTION_PASS",
        "work_id": "CoObject.CrossJobSyntheticTransfer.R0",
        "content_sha256": expected,
        "producer_manifest_sha256": record["manifest_sha256"],
        "produced_two_copies": first["status"],
        "receiver_one_copy_degradation": degraded["status"],
        "receiver_restored_bytes_match_literal": True,
        "source_authenticity_established": False,
        "third_party_independent_receiver_ack": False,
        "storage_fault_domain_independence_established": False,
        "x2_receiver_verified": False,
        "time_survival_24h_verified": False,
        "real_user_benefit_verified": False,
        "effect_authority": "NONE",
    }
    receipt.write_text(json.dumps(output, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return output

def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("mode", choices=["produce", "consume"])
    cli.add_argument("root", type=Path)
    cli.add_argument("--receipt", type=Path)
    a = cli.parse_args()
    try:
        result = produce(a.root) if a.mode == "produce" else consume(a.root, a.receipt or a.root.parent / "receiver_readback.json")
        print(json.dumps(result, sort_keys=True, indent=2))
    except (Held, CapsuleError, OSError) as error:
        cli.exit(2, "HELD: " + str(error) + "\n")

if __name__ == "__main__":
    main()