#!/usr/bin/env python3
"""Read-only, bounded, cross-substrate GitHub artifact byte verifier.

Checks a pinned ZIP and the two files it contains. Does not execute work,
mutate the archived object, authenticate a CoStead/X2 receiver, validate
real-time lease expiry or verify the original CoPre.md source bytes.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import zipfile

PIN = {
    "zip_sha256": "df10aa56be73cb131aa78cecf341dd4b329edabd6f1822711c755335fa9e813e",
    "manifest_sha256": "eda81823dd2e2f07401bbe22bb9d43de19c0d1656921d8af55047f89c8a53599",
    "queue_sha256": "f54e89033aa68c9c94ce803feb41a1bcd70a71bb3c4ec444ee4a92f69dfeed04",
    "source_sha256_claim": "30129e630e73359bbe476d61e21cff4f5e7a8992cd1a79630c001a7de6bf84e4",
    "source_commit": "6ca5f069ca0e0cf7f9ae6985b2e16a28cf579e6f",
    "artifact_id": 13896878596,
    "run_id": "43113671112",
    "attempt": "1",
    "work_id": "CoGoAll.Unfinished.43113671112.a1",
    "owner": "CoGoAll.Seed.43113671112.a1",
}

class Held(Exception):
    pass


def require(test: bool, code: str) -> None:
    if not test:
        raise Held(code)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify(data: bytes, pin: dict = PIN) -> dict:
    require(type(data) is bytes and 0 < len(data) <= 1_000_000, "HOLD_ZIP_SIZE")
    zip_sha = sha(data)
    require(zip_sha == pin["zip_sha256"], "HOLD_ZIP_HASH")
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            infos = archive.infolist()
            require(len(infos) == 2 and {x.filename for x in infos}
                    == {"manifest.json", "queue.sqlite"}, "HOLD_ZIP_ENTRIES")
            require(all(not i.is_dir() and not i.flag_bits & 1
                        and 0 < i.file_size <= 32768 for i in infos),
                    "HOLD_ZIP_ENTRY_LIMIT")
            values = {i.filename: archive.read(i) for i in infos}
    except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
        raise Held("HOLD_ZIP_CORRUPT") from exc
    require(sha(values["manifest.json"]) == pin["manifest_sha256"],
            "HOLD_MANIFEST_HASH")
    require(sha(values["queue.sqlite"]) == pin["queue_sha256"],
            "HOLD_QUEUE_HASH")
    try:
        m = json.loads(values["manifest.json"].decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise Held("HOLD_MANIFEST_PARSE") from exc
    require(type(m) is dict, "HOLD_MANIFEST_SCHEMA")
    for key, value in {
        "schema": "CoGoAll.UnfinishedJobBoundary.R0",
        "run_id": pin["run_id"], "attempt": pin["attempt"],
        "source_commit": pin["source_commit"],
        "source_sha256": pin["source_sha256_claim"],
        "work_id": pin["work_id"], "lease_owner": pin["owner"],
        "queue_sha256": pin["queue_sha256"],
        "clock_scope": "SYNTHETIC_VIRTUAL_SECONDS",
        "provider_scope": "SAME_GITHUB_ACTIONS",
    }.items():
        require(m.get(key) == value and type(m.get(key)) is type(value),
                "HOLD_MANIFEST_FIELD_" + key.upper())
    for k in ("effect_executed", "external_receiver_ack"):
        require(m.get(k) is False, "HOLD_MANIFEST_FALSE_REQUIRED_" + k.upper())
    require(type(m.get("lease_epoch")) is int and m["lease_epoch"] == 1,
            "HOLD_LEASE_EPOCH")
    require(type(m.get("lease_until")) is int and m["lease_until"] == 130,
            "HOLD_LEASE_UNTIL")
    # Read archived SQLite through a disposable read-only copy; never open the
    # original checkpoint for writing or execute code from the artifact.
    with tempfile.TemporaryDirectory() as tmp:
        file = Path(tmp) / "queue.sqlite"
        file.write_bytes(values["queue.sqlite"])
        db = sqlite3.connect(f"file:{file}?mode=ro&immutable=1", uri=True)
        try:
            require(db.execute("PRAGMA quick_check").fetchall() == [("ok",)],
                    "HOLD_SQLITE_INTEGRITY")
            rows = db.execute("""SELECT work_id,source_revision,payload_sha256,
                due_at,state,epoch,owner,lease_until,result_sha256,completed_at
                FROM work""").fetchall()
        except sqlite3.Error as exc:
            raise Held("HOLD_SQLITE_STRUCTURE") from exc
        finally:
            db.close()
    expected = [(pin["work_id"], pin["source_commit"],
                 pin["source_sha256_claim"], 100, "LEASED", 1,
                 pin["owner"], 130, None, None)]
    require(rows == expected, "HOLD_QUEUE_ROW_MISMATCH")
    return {
        "schema": "CoGoAll.CrossSubstrateArchiveByteReadproof.R0",
        "state": "VERIFIED_EXACT_ARCHIVE_BYTES_OFF_GITHUB_RUNNER",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "observer_execution_domain": "OPENAI_CONTAINER_TRANSIENT",
        "source_transport": "GITHUB_CONNECTOR_DOWNLOAD",
        "source_artifact_id": pin["artifact_id"],
        "source_run_id": pin["run_id"],
        "source_commit_in_manifest": pin["source_commit"],
        "source_sha256_in_manifest": pin["source_sha256_claim"],
        "source_bytes_independently_fetched": False,
        "zip_sha256": zip_sha,
        "archive_entry_sha256": {"manifest.json": sha(values["manifest.json"]),
                                 "queue.sqlite": sha(values["queue.sqlite"])},
        "work_id": pin["work_id"],
        "queue_rows": 1,
        "queue_state": "LEASED_UNFINISHED",
        "queue_lease_epoch": 1,
        "queue_completed_at": None,
        "queue_result_sha256": None,
        "sqlite_read_only_quick_check": "ok",
        "new_effect_executed": False,
        "external_receiver_ack": False,
        "x2_receiver_pickup": False,
        "costead_receiver_pickup": False,
        "independent_signed_receiver_identity": False,
        "permanent_agent_or_unattended_uptime": False,
        "physical_elapsed_lease_expiry_verified": False,
        "receiver_lifecycle": "VERIFIED_TRANSIENT_BYTES_ONLY",
        "nonclaims": ["LOCAL_IS_NOT_LANDED", "VALIDATION_IS_NOT_ACCEPTANCE",
            "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
            "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
            "HASHING_IS_NOT_SEMANTIC_INGESTION", "DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY"],
        "verifier_source_sha256": sha(Path(__file__).read_bytes()),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("HOLD_EXISTING_RECEIPT")
    try:
        result = verify(args.archive.read_bytes())
    except (Held, OSError) as exc:
        print(json.dumps({"state":"HOLD", "reason":str(exc),
                          "external_receiver_ack":False}))
        return 3
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")
        f.flush()
    print(json.dumps({"state":result["state"], "work_id":result["work_id"],
                      "receiver_ack":False, "archive_sha256":result["zip_sha256"]}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
