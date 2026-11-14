#!/usr/bin/env python3
"""Read-only third-job CoObject synthetic artifact witness (directory or ZIP).

This verifies strict source and receipt consistency against a literal pinned in
this independent checker, and independently reconstructs from a surviving copy.
It DOES NOT authenticate a different organization, the producer/receiver authors,
or whether the second job truly restored bytes: its receipt is a claim.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import stat
import sys
import zipfile
from pathlib import Path

SOURCE = b"CoCivium CoObject R0 public synthetic cross-job file.\nNo user content, credentials or real external effects.\n"
SOURCE_SHA = hashlib.sha256(SOURCE).hexdigest()
PRODUCER_NAMES = {"capsule/manifest.json", "capsule/payload.bin", "capsule/recovery.bin", "handoff.json"}
RECEIVER_NAMES = {"receipt.json"}
PRODUCER_KEYS = {"schema", "object_id", "source_sha256", "source_bytes", "manifest_sha256", "authority", "content_class", "producer_claim", "receiver_ack", "independent_storage_verified"}
RECEIVER_KEYS = {"schema", "state", "work_id", "content_sha256", "producer_manifest_sha256", "produced_two_copies", "receiver_one_copy_degradation", "receiver_restored_bytes_match_literal", "source_authenticity_established", "third_party_independent_receiver_ack", "storage_fault_domain_independence_established", "x2_receiver_verified", "time_survival_24h_verified", "real_user_benefit_verified", "effect_authority"}
MAX_TOTAL_BYTES = 64_000

class Hold(ValueError):
    pass

def expect(ok, message):
    if not ok:
        raise Hold(message)

def sha(b):
    return hashlib.sha256(b).hexdigest()

def load_files(root: Path, names: set[str]):
    expect(not root.is_symlink(), "ROOT_SYMLINK_HELD")
    actual = {}
    if root.is_file():
        try:
            with zipfile.ZipFile(root) as bundle:
                info = bundle.infolist()
                expect(len(info) == len(names), "UNEXPECTED_ARCHIVE_FILE_COUNT")
                for entry in info:
                    name = entry.filename
                    expect(name in names and name not in actual, "UNEXPECTED_OR_DUPLICATE_ARCHIVE_MEMBER")
                    expect(not stat.S_ISLNK(entry.external_attr >> 16), "ARCHIVE_SYMLINK_HELD")
                    expect(entry.file_size <= MAX_TOTAL_BYTES, "OVERSIZE_ARCHIVE_MEMBER")
                    actual[name] = bundle.read(entry)
        except (zipfile.BadZipFile, RuntimeError, OSError, EOFError) as e:
            raise Hold("INVALID_ARCHIVE") from e
    else:
        expect(root.is_dir(), "INPUT_NOT_DIRECTORY_OR_ZIP")
        for walk_root, dirs, files in os.walk(root, followlinks=False):
            here = Path(walk_root)
            for d in dirs:
                expect(not (here / d).is_symlink(), "DIRECTORY_SYMLINK_HELD")
            for f in files:
                p = here / f
                expect(p.is_file() and not p.is_symlink(), "UNSAFE_INPUT_FILE")
                name = p.relative_to(root).as_posix()
                expect(name in names and name not in actual, "UNEXPECTED_INPUT_FILE")
                expect(p.stat().st_size <= MAX_TOTAL_BYTES, "OVERSIZE_INPUT_FILE")
                actual[name] = p.read_bytes()
    expect(set(actual) == names, "MISSING_OR_EXTRA_FILES")
    expect(sum(map(len, actual.values())) <= MAX_TOTAL_BYTES, "TOTAL_BYTE_BUDGET")
    return actual

def strict_json(blob: bytes, keys: set[str] | None = None):
    def pairs(ps):
        out = {}
        for key, value in ps:
            expect(key not in out, "DUPLICATE_JSON_KEY")
            out[key] = value
        return out
    try:
        obj = json.loads(blob.decode("utf-8"), object_pairs_hook=pairs)
    except Hold:
        raise
    except (ValueError, UnicodeError) as e:
        raise Hold("INVALID_JSON") from e
    expect(isinstance(obj, dict), "EXPECTED_JSON_OBJECT")
    if keys is not None:
        expect(set(obj) == keys, "UNEXPECTED_JSON_FIELDS")
    return obj

def inspect(producer: Path, receiver: Path):
    a = load_files(producer, PRODUCER_NAMES)
    b = load_files(receiver, RECEIVER_NAMES)
    manifest_raw = a["capsule/manifest.json"]
    manifest = strict_json(manifest_raw)
    handoff = strict_json(a["handoff.json"], PRODUCER_KEYS)
    receipt = strict_json(b["receipt.json"], RECEIVER_KEYS)
    expected_id = "coobj-" + SOURCE_SHA[:20]
    expect(a["capsule/payload.bin"] == SOURCE and a["capsule/recovery.bin"] == SOURCE, "PRODUCER_SOURCE_BYTES_WRONG")
    expect(manifest.get("schema") == "CoCivium.CoObject.OfflineCapsule.R0", "MANIFEST_SCHEMA")
    expect(manifest.get("object_id") == expected_id and manifest.get("content_sha256") == SOURCE_SHA, "MANIFEST_SOURCE_ID")
    expect(type(manifest.get("content_bytes")) is int and manifest["content_bytes"] == len(SOURCE), "MANIFEST_BYTE_LENGTH")
    expect(manifest.get("copies") == ["payload.bin", "recovery.bin"], "MANIFEST_COPY_IDS")
    expect(manifest.get("authority") == "DATA_ONLY_NO_EXECUTION", "MANIFEST_AUTHORITY")
    expect(manifest.get("privacy") == "LOCAL_PRIVATE_BY_DEFAULT", "MANIFEST_PRIVACY")
    expect(manifest.get("receiver_readproof") is None and manifest.get("source_authenticity") == "SELF_PACKAGED_NOT_EXTERNALLY_SIGNED", "MANIFEST_FALSE_PROOF")
    expect(manifest.get("minimum_use") == "Recover exact synthetic bytes after one local replica failure", "MANIFEST_MINIMUM_USE")
    expect(handoff["schema"] == "CoCivium.CoObject.CrossJobSyntheticArtifact.R0", "HANDOFF_SCHEMA")
    expect(handoff["object_id"] == expected_id and handoff["source_sha256"] == SOURCE_SHA, "HANDOFF_SOURCE_ID")
    expect(type(handoff["source_bytes"]) is int and handoff["source_bytes"] == len(SOURCE), "HANDOFF_BYTES")
    expect(handoff["manifest_sha256"] == sha(manifest_raw), "HANDOFF_MANIFEST_DIGEST")
    expect(handoff["authority"] == "DATA_ONLY_NO_EXECUTION" and handoff["content_class"] == "PUBLIC_SYNTHETIC_FIXED_LITERAL", "HANDOFF_AUTHORITY_OR_SCOPE")
    expect(handoff["producer_claim"] == "CAPSULE_CREATED_ONE_CI_JOB", "HANDOFF_PRODUCER_SCOPE")
    expect(handoff["receiver_ack"] is None and handoff["independent_storage_verified"] is False, "HANDOFF_FALSE_ACCEPTANCE")
    expect(receipt["schema"] == "CoCivium.CoObject.CrossJobSourceReadback.R0", "RECEIPT_SCHEMA")
    expect(receipt["state"] == "CROSS_JOB_SYNTHETIC_RECONSTRUCTION_PASS", "RECEIPT_STATE")
    expect(receipt["work_id"] == "CoObject.CrossJobSyntheticTransfer.R0", "RECEIPT_WORK_ID")
    expect(receipt["content_sha256"] == SOURCE_SHA and receipt["producer_manifest_sha256"] == sha(manifest_raw), "RECEIPT_DIGEST_MISMATCH")
    expect(receipt["produced_two_copies"] == "READY_LOCAL_TWO_COPIES" and receipt["receiver_one_copy_degradation"] == "DEGRADED_LOCAL_ONE_COPY", "RECEIPT_LIFECYCLE")
    expect(receipt["receiver_restored_bytes_match_literal"] is True, "RECEIVER_DID_NOT_REPORT_RESTORED_BYTES")
    for field in ["source_authenticity_established", "third_party_independent_receiver_ack", "storage_fault_domain_independence_established", "x2_receiver_verified", "time_survival_24h_verified", "real_user_benefit_verified"]:
        expect(receipt[field] is False, "FALSE_EVIDENCE_FIELD:" + field)
    expect(receipt["effect_authority"] == "NONE", "FALSE_AUTHORITY")
    # A separate reader independently checks the recovery bytes, not simply the producer/receiver hashes.
    recovered = bytes(a["capsule/recovery.bin"])
    expect(recovered == SOURCE and sha(recovered) == SOURCE_SHA, "WITNESS_RECONSTRUCTION_FAILED")
    return {
        "schema": "CoCivium.CoObject.CrossJobWitness.R0",
        "state": "THIRD_JOB_SOURCE_SCOPE_CONSISTENCY_PASS",
        "object_id": expected_id,
        "content_sha256": SOURCE_SHA,
        "manifest_sha256": sha(manifest_raw),
        "producer_artifact_file_hashes": {k: sha(a[k]) for k in sorted(a)},
        "receiver_receipt_sha256": sha(b["receipt.json"]),
        "witness_reconstructed_surviving_copy_exact": True,
        "producer_and_receiver_claims_coherent": True,
        "receiver_restoration_independently_observed": False,
        "authentic_origin_verified": False,
        "separate_organization_or_trust_root_verified": False,
        "durable_independent_storage_verified": False,
        "x2_runtime_verified": False,
        "receiver_usefulness_verified": False,
        "rights_or_effect_authority_granted": False,
    }

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("producer", type=Path)
    ap.add_argument("receiver", type=Path)
    ap.add_argument("--report", type=Path)
    args = ap.parse_args(argv)
    try:
        result = inspect(args.producer, args.receiver)
        if args.report is not None:
            expect(args.report.parent.is_dir() and not args.report.exists(), "REPORT_CANNOT_OVERWRITE")
            with args.report.open("x", encoding="utf-8") as f:
                json.dump(result, f, indent=2, sort_keys=True)
                f.write("\n")
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (Hold, OSError) as e:
        print("HELD:" + str(e), file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())