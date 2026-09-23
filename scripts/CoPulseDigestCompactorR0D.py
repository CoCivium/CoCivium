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


def load_packet(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    obj = json.loads(raw.decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("packet must be a JSON object")
    return obj, raw


def require_entry(entry: dict[str, Any]) -> None:
    required = ("pulse_id", "cursor", "delivery_class")
    missing = [k for k in required if k not in entry]
    if missing:
        raise ValueError("selected pulse missing: " + ",".join(missing))
    if not isinstance(entry["cursor"], int) or entry["cursor"] < 0:
        raise ValueError("selected pulse cursor invalid")


def partition(rows: list[dict[str, Any]], group_count: int) -> list[list[dict[str, Any]]]:
    if not rows:
        return []
    group_count = min(group_count, len(rows))
    base, extra = divmod(len(rows), group_count)
    out: list[list[dict[str, Any]]] = []
    start = 0
    for i in range(group_count):
        size = base + (1 if i < extra else 0)
        out.append(rows[start:start + size])
        start += size
    return out


def digest_summary(rows: list[dict[str, Any]], source_packet_sha256: str) -> dict[str, Any]:
    manifest = [
        {
            "pulse_id": str(row["pulse_id"]),
            "cursor": int(row["cursor"]),
            "canonical_entry_sha256": sha256_bytes(canonical(row)),
        }
        for row in rows
    ]
    basis = {
        "source_packet_sha256": source_packet_sha256,
        "manifest": manifest,
    }
    digest_id = "copulsedigest:" + sha256_bytes(canonical(basis))[:24]
    domains = sorted({str(x) for row in rows for x in (row.get("domains") or [])})
    topics = sorted({str(x) for row in rows for x in (row.get("topics") or [])})
    epistemic = sorted({str(row.get("epistemic_class")) for row in rows if row.get("epistemic_class") is not None})
    relations = sorted({str(row.get("relation_type")) for row in rows if row.get("relation_type") is not None})
    sources = sorted({str(row.get("source_identity")) for row in rows if row.get("source_identity") is not None})
    subjects = sorted({str(row.get("subject")) for row in rows if row.get("subject") is not None})
    cursors = [int(row["cursor"]) for row in rows]
    return {
        "digest_id": digest_id,
        "delivery_class": "DIGEST",
        "source_pulse_count": len(rows),
        "cursor_min": min(cursors),
        "cursor_max": max(cursors),
        "domains": domains,
        "topics": topics,
        "epistemic_classes": epistemic,
        "relation_types": relations,
        "source_identities": sources,
        "subject_count": len(subjects),
        "source_manifest": manifest,
        "loss_report": {
            "full_source_entries_emitted_inline": 0,
            "source_entries_omitted_from_compacted_packet": len(rows),
            "preserved_aggregates": [
                "cursor_min",
                "cursor_max",
                "domains",
                "topics",
                "epistemic_classes",
                "relation_types",
                "source_identities",
                "subject_count",
                "source_manifest",
            ],
            "not_preserved_as_digest_semantics": [
                "per_pulse_subject",
                "per_pulse_evidence_refs",
                "per_pulse_wake_conditions",
                "per_pulse_digest_state",
                "per_pulse_authority_ceiling",
            ],
            "exact_replay_requires": [
                "source_packet_sha256",
                "source_manifest",
            ],
            "semantic_summary_generated": false,
        },
    }


def compact(packet: dict[str, Any], packet_raw: bytes, digest_budget: int) -> dict[str, Any]:
    if packet.get("state") != "PUBLIC_SAFE_PACKET_COMPILED__DELIVERY_NOT_PICKUP":
        raise ValueError("FAIL_CLOSED__PACKET_STATE_UNEXPECTED")
    if digest_budget < 1:
        raise ValueError("FAIL_CLOSED__DIGEST_BUDGET_LT_ONE")
    selected = list(packet.get("selected_pulses") or [])
    if not all(isinstance(x, dict) for x in selected):
        raise ValueError("FAIL_CLOSED__SELECTED_PULSE_NOT_OBJECT")
    for entry in selected:
        require_entry(entry)
    selected = sorted(selected, key=lambda x: (int(x["cursor"]), str(x["pulse_id"])))
    digest_rows = [x for x in selected if x.get("delivery_class") == "DIGEST"]
    passthrough = [x for x in selected if x.get("delivery_class") != "DIGEST"]
    for entry in passthrough:
        if entry.get("delivery_class") not in {"HOT", "WARM"}:
            raise ValueError("FAIL_CLOSED__UNKNOWN_DELIVERY_CLASS=" + str(entry.get("delivery_class")))

    source_packet_sha = sha256_bytes(packet_raw)
    groups = partition(digest_rows, digest_budget) if digest_rows else []
    summaries = [digest_summary(group, source_packet_sha) for group in groups]

    result = {
        "schema": "CoPulseDigestCompaction.R0D.v0.1-candidate",
        "state": "PUBLIC_SAFE_DIGEST_COMPACTED__EXPLICIT_LOSS__EXACT_REPLAY_AVAILABLE",
        "source_packet": {
            "packet_id": packet.get("packet_id"),
            "sha256": source_packet_sha,
            "receiver_id": packet.get("receiver_id"),
            "profile_id": packet.get("profile_id"),
        },
        "cursor": packet.get("cursor"),
        "passthrough_selected_pulses": passthrough,
        "digest_summaries": summaries,
        "coverage": {
            "input_selected_count": len(selected),
            "passthrough_count": len(passthrough),
            "input_digest_count": len(digest_rows),
            "digest_summary_count": len(summaries),
            "source_digest_entries_omitted_inline": len(digest_rows),
            "representation_item_reduction": max(0, len(digest_rows) - len(summaries)),
        },
        "pressure": {
            "digest_budget": digest_budget,
            "budget_applies_to": "DIGEST_SUMMARY_COUNT_ONLY",
            "hot_warm_compaction": false,
        },
        "loss_report": {
            "loss_reporting": true,
            "semantic_summary_generated": false,
            "exact_source_replay_available": true,
            "replay_scope": "DIGEST_SOURCE_ENTRIES_ONLY",
            "source_packet_sha256": source_packet_sha,
            "omitted_source_entry_count": len(digest_rows),
        },
        "effects": {
            "receiver_context_mutation": 0,
            "provider_session_mutation": 0,
            "ack_cursor_mutation": 0,
            "authority_change": 0,
            "source_deletion": 0,
        },
        "next": "REPLAY_EXACT_DIGEST_SOURCE_ENTRIES_ON_DEMAND_BEFORE_CLAIMING_OMITTED_DETAIL",
        "nonclaims": [
            "COMPACTION_NE_DELETION",
            "SUMMARY_NE_SOURCE",
            "LOSS_REPORT_NE_ZERO_LOSS",
            "DIGEST_COMPACTION_NE_ACK",
            "COMPACTED_PACKET_NE_RECEIVER_PICKUP",
        ],
    }
    result["compacted_sha256"] = sha256_bytes(canonical(result))
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", required=True)
    ap.add_argument("--digest-budget", type=int, required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    source = Path(args.packet).resolve()
    output = Path(args.output).resolve()
    if output.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={output}")
    try:
        packet, raw = load_packet(source)
        result = compact(packet, raw, args.digest_budget)
    except ValueError as exc:
        raise SystemExit(str(exc))

    output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    output.write_bytes(encoded)
    print(json.dumps({
        "STATE": result["state"],
        "OUTPUT": str(output),
        "OUTPUT_SHA256": sha256_bytes(encoded),
        "SOURCE_PACKET_SHA256": result["source_packet"]["sha256"],
        "INPUT_DIGEST": result["coverage"]["input_digest_count"],
        "DIGEST_SUMMARIES": result["coverage"]["digest_summary_count"],
        "OMITTED_INLINE": result["coverage"]["source_digest_entries_omitted_inline"],
        "ITEM_REDUCTION": result["coverage"]["representation_item_reduction"],
        "ACK_CURSOR_MUTATION": 0,
        "NEXT": result["next"],
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
