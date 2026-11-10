#!/usr/bin/env python3
"""CoOwm R0: explicit-file, private, idempotent narrative capsule experiment.

No clipboard, web session, mouse hook, chat export, publishing, external network,
background task or model call. Treat the input as intentionally supplied text.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
import stat
import sys
from pathlib import Path

MAX_BYTES=256*1024
SCHEMA="CoAll.CoOwm.NarrativeCapsule.R0"

class Held(Exception):
    pass

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read_text(path):
    p=Path(path)
    if p.is_symlink() or not p.is_file():
        raise Held("HELD_SOURCE_NOT_REGULAR")
    if p.stat().st_size > MAX_BYTES:
        raise Held("HELD_SOURCE_TOO_LARGE")
    with p.open("rb") as fp:
        data=fp.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES:
        raise Held("HELD_SOURCE_TOO_LARGE")
    try:
        s=data.decode("utf-8")
    except UnicodeDecodeError:
        raise Held("HELD_NON_UTF8")
    if not s.strip():
        raise Held("HELD_EMPTY_TEXT")
    if "\x00" in s:
        raise Held("HELD_BINARY_IN_TEXT")
    return data

def private_dir(p):
    p=Path(p).expanduser()
    if p.is_symlink():
        raise Held("HELD_OUTPUT_SYMLINK")
    p.mkdir(parents=True,exist_ok=True,mode=0o700)
    if p.is_symlink():
        raise Held("HELD_OUTPUT_SYMLINK")
    if os.name!="nt":
        os.chmod(p,0o700)
    return p

def write_once(path,data):
    fd=os.open(path, os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,"wb") as fp:
            fp.write(data)
            fp.flush();os.fsync(fp.fileno())
    except:
        try: Path(path).unlink()
        except OSError: pass
        raise

def verify(folder, sha):
    folder=Path(folder)
    text_path=folder/"text.txt"
    receipt_path=folder/"receipt.json"
    if not text_path.is_file() or not receipt_path.is_file() or text_path.is_symlink() or receipt_path.is_symlink():
        return "HELD_INCOMPLETE_CAPSULE"
    try:
        raw=text_path.read_bytes()
        rec=json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError,ValueError):
        return "HELD_CORRUPT_CAPSULE"
    if (rec.get("schema")!=SCHEMA or rec.get("sha256")!=sha or
        rec.get("bytes")!=len(raw) or digest(raw)!=sha or
        rec.get("scope")!="PRIVATE_LOCAL_ONLY"):
        return "HELD_DIGEST_OR_RECEIPT_MISMATCH"
    return "VERIFIED_LOCAL_ONLY"

def capture_bytes(raw, root, *, source_kind="EXPLICIT_VISIBLE_LOCAL_BROWSER_POST"):
    """Capture explicit UTF-8 bytes without creating an extra plaintext input file."""
    if not isinstance(raw, bytes) or not raw or len(raw)>MAX_BYTES:
        raise Held("HELD_INVALID_OR_OVERSIZED_TEXT")
    try:
        content=raw.decode("utf-8")
    except UnicodeDecodeError:
        raise Held("HELD_NON_UTF8")
    if not content.strip():
        raise Held("HELD_EMPTY_TEXT")
    if "\x00" in content:
        raise Held("HELD_BINARY_IN_TEXT")
    if source_kind not in {"EXPLICIT_USER_SUPPLIED_UTF8_FILE", "EXPLICIT_VISIBLE_LOCAL_BROWSER_POST"}:
        raise Held("HELD_UNKNOWN_SOURCE_KIND")
    sha=digest(raw)
    root=private_dir(root)
    folder=root/sha
    if folder.exists():
        status=verify(folder,sha)
        return {"state":"DUPLICATE_VERIFIED_LOCAL_ONLY" if status=="VERIFIED_LOCAL_ONLY" else status,
                "sha256":sha,"capsule_id":"coowm:"+sha}
    try:
        folder.mkdir(mode=0o700)
    except FileExistsError:
        status=verify(folder,sha)
        return {"state":"DUPLICATE_VERIFIED_LOCAL_ONLY" if status=="VERIFIED_LOCAL_ONLY" else status,
                "sha256":sha,"capsule_id":"coowm:"+sha}
    receipt={"schema":SCHEMA,"sha256":sha,"bytes":len(raw),
             "capsule_id":"coowm:"+sha,"scope":"PRIVATE_LOCAL_ONLY",
             "created_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
             "source_kind":source_kind,
             "original_source_path_stored":False,"receiver_ack":False,
             "cross_session_sync":False,"published":False}
    try:
        write_once(folder/"text.txt",raw)
        write_once(folder/"receipt.json",(json.dumps(receipt,sort_keys=True,indent=2)+"\n").encode())
    except Exception:
        return {"state":"HELD_INCOMPLETE_CAPSULE","sha256":sha,
                "capsule_id":"coowm:"+sha}
    return {"state":verify(folder,sha),"sha256":sha,"capsule_id":"coowm:"+sha}

def capture(source,root):
    return capture_bytes(read_text(source),root,source_kind="EXPLICIT_USER_SUPPLIED_UTF8_FILE")

def main():
    ap=argparse.ArgumentParser(description="Explicit-file private CoOwm narrative capture")
    ap.add_argument("--source",required=True,type=Path,help="A deliberately supplied UTF-8 text file")
    ap.add_argument("--private-root",required=True,type=Path,help="Existing trusted user-owned local destination")
    args=ap.parse_args()
    try:
        result=capture(args.source,args.private_root)
    except (Held,OSError) as exc:
        result={"state":str(exc) if isinstance(exc,Held) else "HELD_IO_ERROR"}
    print(json.dumps(result,sort_keys=True))
    if not result["state"].startswith(("VERIFIED_","DUPLICATE_VERIFIED_")):
        raise SystemExit(2)

if __name__=="__main__":
    main()
