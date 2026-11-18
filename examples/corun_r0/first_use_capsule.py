#!/usr/bin/env python3
"""Package exactly one pinned CoPreCursor HTML artifact without changing it.

This creates an ephemeral same-provider handoff capsule, not off-provider
custody, user data backup, CoStead delivery, product deployment, or CoMVP.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

GIT_BLOB_SHA1 = "773e9de7aa7c6b03bf0bc75eddb7ca0a0c8dd101"
REL = Path("examples/coprecursor/index.html")


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def blob_sha1(raw):
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw
    ).hexdigest()


def member(name, raw):
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    return info, raw


def build(root, out):
    source = (root / REL).resolve(strict=True)
    raw = source.read_bytes()
    actual = blob_sha1(raw)
    if actual != GIT_BLOB_SHA1:
        raise ValueError("HOLD_SOURCE_BLOB_DRIFT: " + actual)
    if len(raw) > 2_000_000 or not raw.lstrip().startswith(b"<!doctype html>"):
        raise ValueError("HOLD_UNEXPECTED_SOURCE_FORMAT_OR_SIZE")
    manifest = {
        "schema": "CoCivium.CoPreCursor.SourceHandoffCapsule.R0",
        "source_path": REL.as_posix(),
        "blob_sha1": actual,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "source_bytes": len(raw),
        "source_runtime": "offline_single_HTML",
        "source_software_provenance": "public_GitHub_repository_branch",
        "claim_scope": "SOURCE_ARTIFACT_TRANSPORT_ONLY",
        "independent_provider": False,
        "human_receiver": False,
        "user_data_included": False,
        "durable_custody": False,
        "product_promotion": False,
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        for name, data in [("manifest.json", canonical(manifest)),
                           ("index.html", raw)]:
            info, blob = member(name, data)
            archive.writestr(info, blob)
    bundle = buffer.getvalue()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("xb") as stream:
        stream.write(bundle)
    receipt_path = out.with_name(out.name + ".receipt.json")
    receipt = {
        "schema": "CoCivium.CoPreCursor.CapsuleProducerReceipt.R0",
        "capsule_sha256": hashlib.sha256(bundle).hexdigest(),
        "capsule_bytes": len(bundle),
        "source_sha256": manifest["source_sha256"],
        "source_blob_sha1": actual,
        "result": "PACKAGE_CREATED_NOT_LANDED",
        "receiver_ack": False,
        "coex": False,
        "qualified_mvp": False,
    }
    with receipt_path.open("xb") as stream:
        stream.write(canonical(receipt))
    assert source.read_bytes() == raw, "SOURCE_MODIFIED"
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = build(args.repo_root, args.out)
    except (OSError, ValueError, AssertionError) as error:
        print("HELD_OR_FAIL_CLOSED:", error)
        return 2
    print(json.dumps({"status": result["result"], "bytes": result["capsule_bytes"],
                      "sha256": result["capsule_sha256"], "receiver_ack": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
