#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def load_object(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    obj = json.loads(raw.decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"expected JSON object: {path}")
    return obj, raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--compacted", required=True)
    ap.add_argument("--source-packet", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    compacted_path = Path(args.compacted).resolve()
    source_path = Path(args.source_packet).resolve()
    output = Path(args.output).resolve()
    if output.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={output}")

    try:
        compacted, compacted_raw = load_object(compacted_path)
        source, source_raw = load_object(source_path)
    except ValueError as exc:
        raise SystemExit(str(exc))

    if compacted.get("state") != "PUBLIC_SAFE_DIGEST_COMPACTED__EXPLICIT_LOSS__EXACT_REPLAY_AVAILABLE":
        raise SystemExit("FAIL_CLOSED__COMPACTED_STATE_UNEXPECTED")
    source_sha = sha256_bytes(source_raw)
    bound_sha = ((compacted.get("source_packet") or {}).get("sha256"))
    if source_sha != bound_sha:
        raise SystemExit("FAIL_CLOSED__SOURCE_PACKET_HASH_DRIFT")
    if source.get("packet_id") != ((compacted.get("source_packet") or {}).get("packet_id")):
        raise SystemExit("FAIL_CLOSED__SOURCE_PACKET_ID_DRIFT")

    selected = list(source.get("selected_pulses") or [])
    by_id: dict[str, dict[str, Any]] = {}
    for row in selected:
        if not isinstance(row, dict) or not row.get("pulse_id"):
            raise SystemExit("FAIL_CLOSED__SOURCE_SELECTED_PULSE_INVALID")
        pid = str(row["pulse_id"])
        if pid in by_id:
            raise SystemExit("FAIL_CLOSED__DUPLICATE_SOURCE_PULSE_ID=" + pid)
        by_id[pid] = row

    replayed: list[dict[str, Any]] = []
    seen: set[str] = set()
    for summary in compacted.get("digest_summaries") or []:
        for ref in summary.get("source_manifest") or []:
            pid = str(ref.get("pulse_id") or "")
            if not pid or pid in seen:
                raise SystemExit("FAIL_CLOSED__INVALID_OR_DUPLICATE_MANIFEST_PULSE_ID=" + pid)
            row = by_id.get(pid)
            if row is None:
                raise SystemExit("FAIL_CLOSED__MANIFEST_PULSE_MISSING_FROM_SOURCE=" + pid)
            if row.get("delivery_class") != "DIGEST":
                raise SystemExit("FAIL_CLOSED__MANIFEST_REFERENCES_NON_DIGEST=" + pid)
            if int(row.get("cursor")) != int(ref.get("cursor")):
                raise SystemExit("FAIL_CLOSED__MANIFEST_CURSOR_DRIFT=" + pid)
            actual_sha = sha256_bytes(canonical(row))
            if actual_sha != ref.get("canonical_entry_sha256"):
                raise SystemExit("FAIL_CLOSED__MANIFEST_ENTRY_HASH_DRIFT=" + pid)
            seen.add(pid)
            replayed.append(row)

    expected_digest = sorted(
        [x for x in selected if isinstance(x, dict) and x.get("delivery_class") == "DIGEST"],
        key=lambda x: (int(x["cursor"]), str(x["pulse_id"])),
    )
    replayed = sorted(replayed, key=lambda x: (int(x["cursor"]), str(x["pulse_id"])))
    if replayed != expected_digest:
        raise SystemExit("FAIL_CLOSED__REPLAY_COVERAGE_NOT_EXACT")

    result = {
        "schema": "CoPulseDigestReplay.R0D.v0.1-candidate",
        "state": "PASS_EXACT_DIGEST_SOURCE_REPLAY_FROM_BOUND_PACKET",
        "source_packet": {
            "packet_id": source.get("packet_id"),
            "sha256": source_sha,
        },
        "compacted_packet": {
            "sha256": sha256_bytes(compacted_raw),
            "compacted_sha256": compacted.get("compacted_sha256"),
        },
        "coverage": {
            "expected_digest_count": len(expected_digest),
            "replayed_digest_count": len(replayed),
            "exact_object_equality": true,
            "manifest_unique": true,
        },
        "replayed_digest_pulses": replayed,
        "effects": {
            "source_mutation": 0,
            "receiver_context_mutation": 0,
            "ack_cursor_mutation": 0,
            "authority_change": 0,
        },
        "next": "RECEIVER_MAY_DRILL_DOWN_TO_EXACT_REPLAYED_SOURCE_ENTRIES",
        "nonclaims": [
            "REPLAY_NE_INTEGRATION",
            "REPLAY_NE_ACK",
            "REPLAY_NE_SOURCE_DELETION",
            "CANONICAL_OBJECT_EQUALITY_NE_RAW_SUBSTRING_IDENTITY",
        ],
    }
    result["replay_sha256"] = sha256_bytes(canonical(result))

    output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    output.write_bytes(encoded)
    print(json.dumps({
        "STATE": result["state"],
        "OUTPUT": str(output),
        "OUTPUT_SHA256": sha256_bytes(encoded),
        "SOURCE_PACKET_SHA256": source_sha,
        "REPLAYED_DIGEST": len(replayed),
        "EXACT_OBJECT_EQUALITY": true,
        "ACK_CURSOR_MUTATION": 0,
        "NEXT": result["next"],
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
