#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def load_object(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    obj = json.loads(raw.decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"expected JSON object: {path}")
    return obj, raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--projection", required=True)
    ap.add_argument("--source-packet", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    projection_path = Path(args.projection).resolve()
    packet_path = Path(args.source_packet).resolve()
    out = Path(args.output).resolve()
    if out.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out}")

    projection, projection_raw = load_object(projection_path)
    packet, packet_raw = load_object(packet_path)
    packet_sha = sha256_bytes(packet_raw)
    expected_sha = str((projection.get("source_packet") or {}).get("sha256") or "")
    if packet_sha != expected_sha:
        raise SystemExit(f"FAIL_CLOSED__SOURCE_PACKET_HASH_DRIFT__EXPECTED={expected_sha}__ACTUAL={packet_sha}")

    selected = list(packet.get("selected_pulses") or [])
    replayed: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []

    for group in list(projection.get("digest_groups") or []):
        for manifest in list(group.get("exact_replay_manifest") or []):
            index = manifest.get("source_packet_index")
            if not isinstance(index, int) or index < 0 or index >= len(selected):
                raise SystemExit("FAIL_CLOSED__SOURCE_PACKET_INDEX_INVALID")
            entry = selected[index]
            if str(entry.get("delivery_class") or "") != "DIGEST":
                raise SystemExit("FAIL_CLOSED__REPLAY_TARGET_NOT_DIGEST")
            if entry.get("pulse_id") != manifest.get("pulse_id") or entry.get("cursor") != manifest.get("cursor"):
                raise SystemExit("FAIL_CLOSED__REPLAY_IDENTITY_MISMATCH")
            actual_entry_sha = sha256_bytes(canonical_bytes(entry))
            if actual_entry_sha != manifest.get("canonical_entry_sha256"):
                raise SystemExit("FAIL_CLOSED__REPLAY_ENTRY_HASH_DRIFT")
            replayed.append(entry)
            manifest_rows.append({
                "pulse_id":entry["pulse_id"],
                "cursor":entry["cursor"],
                "source_packet_index":index,
                "canonical_entry_sha256":actual_entry_sha,
                "exact_match":True,
            })

    original_digest = [e for e in selected if str(e.get("delivery_class") or "") == "DIGEST"]
    if [sha256_bytes(canonical_bytes(e)) for e in replayed] != [sha256_bytes(canonical_bytes(e)) for e in original_digest]:
        raise SystemExit("FAIL_CLOSED__REPLAYED_DIGEST_SEQUENCE_NOT_EXACT")

    result = {
        "schema":"CoPulseDigestReplay.R0D.v0.1-candidate",
        "state":"PASS_EXACT_DIGEST_SOURCE_ENTRY_REPLAY__NO_SOURCE_MUTATION",
        "projection":{
            "path":str(projection_path),
            "sha256":sha256_bytes(projection_raw),
            "projection_id":projection.get("projection_id"),
            "pressure":projection.get("pressure"),
        },
        "source_packet":{
            "path":str(packet_path),
            "sha256":packet_sha,
            "packet_id":packet.get("packet_id"),
        },
        "coverage":{
            "source_digest_entry_count":len(original_digest),
            "replayed_digest_entry_count":len(replayed),
            "manifest_rows":manifest_rows,
            "sequence_exact":True,
        },
        "replayed_digest_entries":replayed,
        "effects":{
            "source_packet_mutation":0,
            "projection_mutation":0,
            "ack_cursor_mutation":0,
            "provider_session_mutation":0,
        },
        "next":"DIGEST_PROJECTION_MAY_BE_USED_AS_LOSSY_VIEW_WHILE_EXACT_SOURCE_REMAINS_BOUND",
        "nonclaims":[
            "REPLAY_NE_INTEGRATION",
            "REPLAY_NE_COEX",
            "REPLAYABILITY_NE_SOURCE_RETIREMENT_AUTHORITY",
            "DIGEST_NE_SEMANTIC_EQUIVALENCE",
        ],
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    out.write_bytes(encoded)
    print(json.dumps({
        "STATE":result["state"],
        "OUTPUT":str(out),
        "OUTPUT_SHA256":sha256_bytes(encoded),
        "SOURCE_DIGEST":len(original_digest),
        "REPLAYED":len(replayed),
        "SEQUENCE_EXACT":True,
        "NEXT":result["next"],
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
