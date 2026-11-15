#!/usr/bin/env python3
"""RepoZipper+ R0: offline ChatGPT-export ZIP inspection and private ID census.

Standard library only. Does not extract members, print chat content, access an
account, use a network connection, or infer full account coverage. Creates
output only inside a new private directory. Input ZIP is read-only.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import io
import json
import os
from pathlib import Path, PurePosixPath
import secrets
import sqlite3
import stat
import sys
import zipfile

SCHEMA = "CoAll.RepoZipper.AIHistoryIntake.R0"
MAX_ENTRIES = 100_000
MAX_UNCOMPRESSED_BYTES = 128 * 1024**3
MAX_ITEM_CHARS = 64 * 1024**2
MAX_RECORDS = 5_000_000
RECEIPT = "PRIVATE_CENSUS_RECEIPT.json"
DB = "PRIVATE_CENSUS.sqlite3"
KEY = "PRIVATE_HMAC_KEY.bin"


class Hold(Exception):
    """Explicit safety gate, safe to report without source contents."""


def require(condition: bool, code: str) -> None:
    if not condition:
        raise Hold("HOLD_" + code)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def inspect_zip(archive: zipfile.ZipFile) -> tuple[dict, list]:
    members = archive.infolist()
    require(0 < len(members) <= MAX_ENTRIES, "MEMBER_COUNT")
    seen = set()
    matches = []
    total = 0
    for entry in members:
        name = entry.filename
        require(isinstance(name, str) and name and not any(c in name for c in ("\\", ":", "\x00")), "UNSAFE_NAME")
        pieces = name.rstrip("/").split("/")
        require(not name.startswith("/") and all(x not in ("", ".", "..") for x in pieces), "UNSAFE_PATH")
        require(name not in seen, "DUPLICATE_MEMBER")
        seen.add(name)
        if entry.create_system == 3:
            mode = (entry.external_attr >> 16) & 0xFFFF
            require(not (stat.S_ISLNK(mode) or stat.S_ISCHR(mode) or stat.S_ISBLK(mode)), "SPECIAL_MEMBER")
        require(not entry.flag_bits & 1, "ENCRYPTED_MEMBER")
        total += entry.file_size
        require(total <= MAX_UNCOMPRESSED_BYTES, "TOTAL_UNCOMPRESSED_LIMIT")
        if entry.file_size:
            require(entry.compress_size > 0, "ZERO_COMPRESSED_SIZE")
            require(entry.file_size <= 1000 * entry.compress_size, "EXCESSIVE_RATIO")
        if not entry.is_dir() and PurePosixPath(name).name == "conversations.json":
            matches.append(entry)
    return {"member_count": len(members), "declared_uncompressed_bytes": total,
            "conversation_source_candidates": len(matches)}, matches


def iter_chars(binary_stream):
    wrapper = io.TextIOWrapper(binary_stream, encoding="utf-8", errors="strict")
    while True:
        chunk = wrapper.read(65536)
        if not chunk:
            break
        yield from chunk


def json_array_objects(stream):
    """Yield bounded top-level JSON objects, never loading whole JSON array."""
    source = iter(iter_chars(stream))

    def nonspace():
        for char in source:
            if not char.isspace():
                return char
        return None

    require(nonspace() == "[", "TOP_LEVEL_NOT_ARRAY")
    char = nonspace()
    if char == "]":
        require(nonspace() is None, "TRAILING_DATA")
        return
    while True:
        require(char == "{", "ITEM_NOT_OBJECT")
        buf = ["{"]
        stack = ["{"]
        quoted = False
        escaped = False
        for char in source:
            buf.append(char)
            require(len(buf) <= MAX_ITEM_CHARS, "ITEM_TOO_BIG")
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
            elif char == '"':
                quoted = True
            elif char in "{[":
                stack.append(char)
            elif char in "}]":
                require(stack and ((char == "}" and stack[-1] == "{")
                                   or (char == "]" and stack[-1] == "[")), "INVALID_NESTING")
                stack.pop()
                if not stack:
                    break
        require(not stack and not quoted, "TRUNCATED_RECORD")
        try:
            obj = json.loads("".join(buf))
        except (ValueError, TypeError):
            raise Hold("HOLD_INVALID_RECORD_JSON") from None
        require(isinstance(obj, dict), "ITEM_NOT_OBJECT")
        yield obj
        char = nonspace()
        if char == "]":
            require(nonspace() is None, "TRAILING_DATA")
            return
        require(char == ",", "MISSING_SEPARATOR")
        char = nonspace()


def write_exclusive(path: Path, data: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as out:
        out.write(data)
        out.flush()
        os.fsync(out.fileno())


def prepare_output(output: Path) -> None:
    require(not output.exists(), "OUTPUT_ALREADY_EXISTS")
    require(output.parent.is_dir() and not output.parent.is_symlink(), "OUTPUT_PARENT_UNSAFE")
    output.mkdir(mode=0o700)


def run(archive_path: Path, output: Path, mode: str = "inspect") -> dict:
    require(mode in ("inspect", "census"), "MODE")
    require(archive_path.exists() and archive_path.is_file(), "SOURCE_MISSING")
    require(not archive_path.is_symlink(), "SOURCE_SYMLINK")
    require(archive_path.suffix.lower() == ".zip", "SOURCE_NOT_ZIP")
    require(not output.exists(), "OUTPUT_ALREADY_EXISTS")
    with zipfile.ZipFile(archive_path, allowZip64=True) as archive:
        metadata, candidates = inspect_zip(archive)
        summary = {
            "schema": SCHEMA,
            "mode": mode,
            "state": "FORMAT_CANDIDATE" if len(candidates) == 1 else "UNSUPPORTED_OR_AMBIGUOUS_FORMAT",
            "zip_sha256": sha256_file(archive_path),
            "zip_size_bytes": archive_path.stat().st_size,
            "scope": "EXPORTED_ZIP_ONLY_NOT_ACCOUNT_WIDE",
            "provider": "CHATGPT_EXPORT_CANDIDATE",
            **metadata,
            "archive_extraction": "NONE",
            "raw_conversations_ever_printed": False,
            "delete_safe": False,
            "external_receiver_ack": False,
        }
        if mode == "inspect":
            prepare_output(output)
            write_exclusive(output / RECEIPT, (json.dumps(summary, indent=2) + "\n").encode("utf-8"))
            return summary
        require(len(candidates) == 1, "EXACTLY_ONE_SUPPORTED_CONVERSATIONS_JSON_REQUIRED")
        prepare_output(output)
        key = secrets.token_bytes(32)
        write_exclusive(output / KEY, key)
        dbpath = output / DB
        conn = sqlite3.connect(dbpath)
        try:
            conn.execute("PRAGMA journal_mode=DELETE")
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute("CREATE TABLE conversations (id_hmac TEXT PRIMARY KEY, created_at REAL, updated_at REAL, message_nodes INTEGER)")
            observed = 0
            missing_id = 0
            repeated_id = 0
            with archive.open(candidates[0]) as stream:
                for doc in json_array_objects(stream):
                    observed += 1
                    require(observed <= MAX_RECORDS, "RECORD_LIMIT")
                    identity = doc.get("id")
                    if not isinstance(identity, str) or not identity:
                        missing_id += 1
                        continue
                    secret_id = hmac.new(key, identity.encode("utf-8"), hashlib.sha256).hexdigest()
                    nodes = doc.get("mapping")
                    message_count = (sum(1 for x in nodes.values() if isinstance(x, dict) and x.get("message") is not None)
                                     if isinstance(nodes, dict) else None)
                    def safe_float(value):
                        return float(value) if type(value) in (float, int) else None
                    try:
                        conn.execute("INSERT INTO conversations VALUES(?,?,?,?)",
                                     (secret_id, safe_float(doc.get("create_time")), safe_float(doc.get("update_time")), message_count))
                    except sqlite3.IntegrityError:
                        repeated_id += 1
                    if observed % 1000 == 0:
                        conn.commit()
            conn.commit()
            distinct = conn.execute("SELECT count(*) FROM conversations").fetchone()[0]
        finally:
            conn.close()
        if os.name != "nt":
            os.chmod(dbpath, 0o600)
        summary.update({
            "state": "STRUCTURAL_CENSUS_EXPORT_ONLY" if observed and not missing_id and not repeated_id else "HOLD_INCOMPLETE_OR_AMBIGUOUS_CENSUS",
            "observed_records": observed,
            "distinct_conversation_ids_in_export": distinct,
            "missing_id_records": missing_id,
            "duplicate_id_records": repeated_id,
            "privacy": "LOCAL_KEYED_IDS_ONLY_NO_TITLES_OR_MESSAGE_CONTENT",
            "receipt": "PRODUCER_LOCAL_ONLY_NOT_RESTORE_OR_NAS_ACK",
            "nonclaims": ["EXPORT_NE_COMPLETE_ACCOUNT", "MESSAGE_NODES_NE_COMPLETE_HISTORY", "CENSUS_NE_CONTENT_RESTORATION",
                          "LOCAL_COPY_NE_INDEPENDENT_BACKUP", "NO_CHAT_DELETION_OR_PROVIDER_ACTION"],
        })
        write_exclusive(output / RECEIPT, (json.dumps(summary, indent=2) + "\n").encode("utf-8"))
        return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path, help="Existing parent, entirely new output directory")
    parser.add_argument("--mode", choices=("inspect", "census"), default="inspect")
    args = parser.parse_args()
    try:
        result = run(args.zip.expanduser().resolve(), args.out.expanduser().absolute(), args.mode)
    except (Hold, OSError, ValueError, zipfile.BadZipFile, UnicodeError, sqlite3.DatabaseError) as exc:
        msg = str(exc) if isinstance(exc, Hold) else "HOLD_IO_FORMAT_OR_INTEGRITY"
        print(json.dumps({"state": "HOLD", "reason": msg, "no_data_deleted": True}))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
