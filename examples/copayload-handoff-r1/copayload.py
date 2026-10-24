#!/usr/bin/env python3
"""CoPayload R1: explicit, local-only, byte-identical FILE_BACKED preview packets.

No clipboard access, OS input hooks, network, AI, external send or execution.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import mimetypes
import os
from pathlib import Path
import stat
import sys

SCHEMA = "CoPayload.FileHandoffPreview.R1"
CHUNK_MIN = 256 * 1024
CHUNK_DEFAULT = 1024 * 1024
CHUNK_MAX = 32
MAX_BYTES_DEFAULT = 1024 * 1024 * 1024  # 1 GiB, overridable bounded
IO_BLOCK = 1024 * 1024
NONCLAIMS = [
    "FILE_BACKED_NE_RECEIVER_UPLOADED",
    "PREVIEW_NE_PASTE_OR_SEND",
    "SHA256_NE_SEMANTIC_TRUTH",
    "MANIFEST_NE_CUSTODY",
    "SOURCE_PATH_NOT_PUBLISHED",
    "LOCAL_IS_NOT_LANDED",
    "VALIDATION_IS_NOT_ACCEPTANCE",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
    "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
    "HASHING_IS_NOT_SEMANTIC_INGESTION",
    "DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY",
]


class Hold(Exception):
    """Fail-closed unqualified operation, not a PASS."""


def checked_source(path: Path, max_bytes: int) -> tuple[int, int, int]:
    try:
        source_stat = path.lstat()
    except (OSError, ValueError) as exc:
        raise Hold(f"Source unavailable: {type(exc).__name__}") from exc
    if not stat.S_ISREG(source_stat.st_mode):
        raise Hold("Expected one explicitly selected regular file; symlinks/directories held")
    if not (0 <= source_stat.st_size <= max_bytes):
        raise Hold("Selected source exceeds the explicit byte budget")
    return source_stat.st_size, source_stat.st_mtime_ns, source_stat.st_ino


def consume_file(path: Path, max_bytes: int, max_chunks: int) -> dict:
    if not (1 <= max_chunks <= CHUNK_MAX):
        raise Hold("max_chunks must be between 1 and 32")
    size, mtime, inode = checked_source(path, max_bytes)
    chunk_bytes = max(CHUNK_MIN, CHUNK_DEFAULT * math.ceil(size / (CHUNK_DEFAULT * max_chunks)))
    whole = hashlib.sha256()
    chunks = []
    count = 0
    try:
        with path.open("rb", buffering=0) as fh:
            if not stat.S_ISREG(os.fstat(fh.fileno()).st_mode):
                raise Hold("Source must remain a regular file")
            if os.fstat(fh.fileno()).st_ino != inode:
                raise Hold("Source changed during open")
            while True:
                ch = hashlib.sha256()
                length = 0
                while length < chunk_bytes:
                    data = fh.read(min(IO_BLOCK, chunk_bytes - length))
                    if not data:
                        break
                    whole.update(data)
                    ch.update(data)
                    length += len(data)
                    count += len(data)
                    if count > max_bytes:
                        raise Hold("Source exceeded byte budget while reading")
                if length == 0:
                    break
                chunks.append({"offset": count-length, "bytes": length, "sha256": ch.hexdigest()})
                if len(chunks) > max_chunks:
                    raise Hold("Chunk cap unexpectedly exceeded")
            end = os.fstat(fh.fileno())
            if end.st_size != size or end.st_mtime_ns != mtime or end.st_ino != inode:
                raise Hold("Source changed while hashing: retry with stable snapshot")
    except OSError as exc:
        raise Hold(f"Read failed: {type(exc).__name__}") from exc
    if count != size:
        raise Hold("Source changed length during hashing")
    return {"sha256": whole.hexdigest(), "bytes": count, "chunk_bytes": chunk_bytes, "chunks": chunks}


def prepare(path: Path, classification: str, max_bytes: int, max_chunks: int) -> dict:
    d = consume_file(path, max_bytes, max_chunks)
    mime_guess, _ = mimetypes.guess_type(path.name)
    return {
        "schema": SCHEMA,
        "packet_id": "sha256:" + d["sha256"],
        "status": "LOCAL_CANDIDATE_PREVIEW_ONLY",
        "payload_mode": "FILE_BACKED_CONTENT_ADDRESSED",
        "payload_type_guess": mime_guess or "application/octet-stream",
        "type_evidence": "FILENAME_EXTENSION_ONLY_NOT_MEDIA_DECODER",
        "source_ref": None,
        "source_path_included": False,
        "source_class": "EXPLICITLY_SELECTED_LOCAL_REGULAR_FILE",
        "source_sha256": d["sha256"],
        "byte_count": d["bytes"],
        "chunk_size": d["chunk_bytes"],
        "chunk_hashes": d["chunks"],
        "privacy_class": classification,
        "content_not_embedded": True,
        "preview_ref": None,
        "receiver_candidates": [],
        "authority_ceiling": "NONE",
        "outbound_effects": 0,
        "receiver_ack": False,
        "human_ux_acceptance": "UNPROVEN",
        "physical_button_event": "HELD_NOT_OBSERVED",
        "readback_instruction": "Receiver supplies its own authorized exact file to `copayload.py verify`",
        "nonclaims": NONCLAIMS,
    }


def write_new(path: Path, payload: dict) -> None:
    body = (json.dumps(payload, indent=2, ensure_ascii=True, sort_keys=True) + "\n").encode("utf-8")
    # Don't automatically create unfamiliar directory trees; receipt destination must exist.
    if not path.parent.is_dir():
        raise Hold("Output directory is missing; nothing created")
    try:
        with path.open("xb") as fh:
            fh.write(body)
    except FileExistsError as exc:
        raise Hold("Output already exists; no-clobber HOLD") from exc
    except OSError as exc:
        raise Hold(f"Output not written: {type(exc).__name__}") from exc


def verify(file: Path, manifest: Path, max_bytes: int) -> dict:
    try:
        if manifest.lstat().st_size > 100 * 1024:
            raise Hold("Unreasonably large manifest")
        packet = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        raise Hold(f"Manifest unavailable or invalid: {type(exc).__name__}") from exc
    if not isinstance(packet, dict) or packet.get("schema") != SCHEMA:
        raise Hold("Unknown manifest schema")
    if packet.get("receiver_ack") is not False or packet.get("authority_ceiling") != "NONE":
        raise Hold("Manifest requests an unsupported authority or ACK")
    if packet.get("source_path_included") is not False or packet.get("content_not_embedded") is not True:
        raise Hold("Manifest violates privacy/capture boundary")
    original_chunks = packet.get("chunk_hashes")
    if not isinstance(original_chunks, list) or len(original_chunks) > CHUNK_MAX:
        raise Hold("Invalid chunk index")
    digest = packet.get("source_sha256")
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        raise Hold("Invalid expected digest")
    d = consume_file(file, max_bytes, CHUNK_MAX)
    # Consumer need not have same extension or path; compare exact bytes and range hashes.
    if d["sha256"] != digest or d["bytes"] != packet.get("byte_count"):
        raise Hold("Byte identity does not match")
    if packet.get("packet_id") != "sha256:" + digest:
        raise Hold("Packet identity inconsistent")
    # Original chunk layout can be larger than our local default chosen from size. Verify ranges independently.
    try:
        with file.open("rb") as fh:
            previous = 0
            for ch in original_chunks:
                offset, length, chash = ch["offset"], ch["bytes"], ch["sha256"]
                if not isinstance(offset,int) or not isinstance(length,int) or offset != previous or length <= 0:
                    raise Hold("Chunk boundaries inconsistent")
                if not isinstance(chash,str) or len(chash)!=64:
                    raise Hold("Invalid chunk hash")
                h = hashlib.sha256()
                remaining = length
                while remaining:
                    buf=fh.read(min(IO_BLOCK,remaining))
                    if not buf: raise Hold("Missing chunk bytes")
                    h.update(buf); remaining-=len(buf)
                if h.hexdigest()!=chash: raise Hold("Chunk digest mismatch")
                previous += length
            if previous != d["bytes"]:
                if previous==0 and d["bytes"]==0: pass
                else:raise Hold("Chunks do not cover the file")
    except (KeyError,TypeError,ValueError) as exc:
        raise Hold("Malformed chunk manifest") from exc
    return {
        "schema": "CoPayload.ByteReadback.R1",
        "status": "PASS_EXACT_BYTES_ONLY",
        "packet_id": packet["packet_id"],
        "readback_sha256": d["sha256"],
        "bytes_read": d["bytes"],
        "receiver_class": "EXPLICIT_LOCAL_CLI_INVOCATION",
        "independent_receiver_ack": False,
        "semantic_validation": "NOT_PERFORMED",
        "runtime_integration": False,
        "outbound_effects": 0,
        "nonclaims": ["BYTE_READBACK_NE_REMOTE_DELIVERY","HASHING_IS_NOT_SEMANTIC_INGESTION"]
    }


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description="Prepare or verify local file-backed CoQuanta. Never sends or pastes.")
    sub=parser.add_subparsers(dest="operation",required=True)
    p=sub.add_parser("prepare",help="write one no-clobber manifest for explicitly selected file")
    p.add_argument("--file",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--privacy",choices=["PUBLIC_SAFE_FIXTURE","PRIVATE","RESTRICTED"],default="PRIVATE")
    p.add_argument("--max-bytes",type=int,default=MAX_BYTES_DEFAULT)
    p.add_argument("--max-chunks",type=int,default=CHUNK_MAX)
    v=sub.add_parser("verify",help="check exact independently supplied local file; no receiver ACK")
    v.add_argument("--file",type=Path,required=True)
    v.add_argument("--manifest",type=Path,required=True)
    v.add_argument("--max-bytes",type=int,default=MAX_BYTES_DEFAULT)
    a=parser.parse_args(argv)
    try:
        if a.max_bytes < 0 or a.max_bytes > 20*1024**3:
            raise Hold("max-bytes outside supported 0..20 GiB policy")
        if a.operation=="prepare":
            m=prepare(a.file,a.privacy,a.max_bytes,a.max_chunks)
            write_new(a.out,m)
            print(json.dumps({"status":"PASS_LOCAL_PREVIEW_MANIFEST","packet_id":m["packet_id"],"bytes":m["byte_count"],"chunks":len(m["chunk_hashes"]),"output_written":True,"external_effects":0,"receiver_ack":False},sort_keys=True))
        elif a.operation=="verify":
            print(json.dumps(verify(a.file,a.manifest,a.max_bytes),sort_keys=True))
        return 0
    except Hold as exc:
        # Do not reveal paths or data even on error.
        print(json.dumps({"status":"HELD","reason":str(exc),"external_effects":0,"receiver_ack":False},sort_keys=True),file=sys.stderr)
        return 2

if __name__=="__main__":
    sys.exit(main())
