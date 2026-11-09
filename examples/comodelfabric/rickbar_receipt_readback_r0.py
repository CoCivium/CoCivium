"""Second-process, read-only WorkID receipt verification for local rickBar.

A process-local structural readback is NOT an independent receiver ACK,
model-grounded truth, X2 deployment, or durable multi-host custody.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import stat

_ID = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_SHA = re.compile(r"^[a-f0-9]{64}$")
_MAX_BYTES = 1024 * 1024


def readback(receipt_dir: str, work_id: str, expected_sha256: str) -> dict:
    if not isinstance(work_id, str) or not _ID.fullmatch(work_id):
        raise ValueError("INVALID_WORK_ID")
    if not isinstance(expected_sha256, str) or not _SHA.fullmatch(expected_sha256):
        raise ValueError("INVALID_EXPECTED_DIGEST")
    root = Path(receipt_dir)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("UNBOUND_RECEIPT_ROOT")
    path = root / (work_id + ".json")
    # O_NOFOLLOW prevents a symlink swap at final open on supported platforms.
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(str(path), flags)
    except (OSError, ValueError) as exc:
        raise ValueError("RECEIPT_NOT_READABLE") from exc
    with os.fdopen(fd, "rb") as handle:
        meta = os.fstat(handle.fileno())
        if (not stat.S_ISREG(meta.st_mode) or meta.st_size > _MAX_BYTES
                or (path.is_symlink())):
            raise ValueError("UNSAFE_RECEIPT_FILE")
        raw = handle.read(_MAX_BYTES + 1)
    if len(raw) > _MAX_BYTES:
        raise ValueError("RECEIPT_TOO_LARGE")
    digest = hashlib.sha256(raw).hexdigest()
    if not hmac.compare_digest(digest, expected_sha256):
        raise ValueError("RECEIPT_DIGEST_MISMATCH")
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("INVALID_RECEIPT_JSON") from exc
    if (not isinstance(data, dict) or data.get("work_id") != work_id
            or data.get("status") != "MODEL_OUTPUT_UNVERIFIED"
            or not isinstance(data.get("result"), dict)
            or data["result"].get("work_id") not in (None, work_id)):
        raise ValueError("RECEIPT_IDENTITY_OR_STATE_MISMATCH")
    return {
        "work_id": work_id,
        "sha256": digest,
        "state": "STRUCTURAL_COLD_PROCESS_READBACK",
        "reader_pid": os.getpid(),
        "model_output_verified": False,
        "independent_receiver_ack": False,
        "native_rickbar_effect": False,
        "source": "LOCAL_RECEIPT_FILE_ONLY",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Read-only local receipt verification")
    p.add_argument("--receipt-dir", required=True)
    p.add_argument("--work-id", required=True)
    p.add_argument("--sha256", required=True)
    args = p.parse_args()
    try:
        result = readback(args.receipt_dir, args.work_id, args.sha256)
    except ValueError as exc:
        print(json.dumps({"state": "HOLD", "reason": str(exc),
                          "independent_receiver_ack": False}))
        return 3
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
