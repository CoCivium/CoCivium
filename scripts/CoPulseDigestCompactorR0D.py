#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


PRESSURES = {"LOW", "MODERATE", "HIGH", "DEGRADED"}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def entry_sha256(entry: dict[str, Any]) -> str:
    return sha256_bytes(canonical_bytes(entry))


def load_object(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    obj = json.loads(raw.decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"expected JSON object: {path}")
    return obj, raw


def chunk_size_for_pressure(pressure: str, digest_count: int) -> int:
    if pressure == "LOW":
        return 1
    if pressure == "MODERATE":
        return 3
    return max(1, digest_count)


def summarize_group(entries: list[dict[str, Any]], source_indices: list[int], group_index: int) -> dict[str, Any]:
    pulse_ids = [str(e["pulse_id"]) for e in entries]
    cursors = [int(e["cursor"]) for e in entries]
    domains = sorted({str(x) for e in entries for x in list(e.get("domains") or [])})
    topics = sorted({str(x) for e in entries for x in list(e.get("topics") or [])})
    relation_counts: dict[str, int] = {}
    epistemic_counts: dict[str, int] = {}
    manifests = []
    for entry, source_index in zip(entries, source_indices):
        relation = str(entry.get("relation_type") or "UNKNOWN")
        epistemic = str(entry.get("epistemic_class") or "UNKNOWN")
        relation_counts[relation] = relation_counts.get(relation, 0) + 1
        epistemic_counts[epistemic] = epistemic_counts.get(epistemic, 0) + 1
        manifests.append({
            "pulse_id": entry["pulse_id"],
            "cursor": entry["cursor"],
            "source_packet_index": source_index,
            "canonical_entry_sha256": entry_sha256(entry),
        })

    group_basis = {
        "group_index": group_index,
        "pulse_ids": pulse_ids,
        "cursors": cursors,
        "entry_hashes": [m["canonical_entry_sha256"] for m in manifests],
    }
    return {
        "digest_group_id": "copulsedigest:" + sha256_bytes(canonical_bytes(group_basis))[:24],
        "source_entry_count": len(entries),
        "cursor_min": min(cursors),
        "cursor_max": max(cursors),
        "pulse_ids": pulse_ids,
        "domains": domains,
        "topics": topics,
        "relation_type_counts": relation_counts,
        "epistemic_class_counts": epistemic_counts,
        "exact_replay_manifest": manifests,
    }


def compact(packet: dict[str, Any], packet_raw: bytes, pressure: str) -> dict[str, Any]:
    if pressure not in PRESSURES:
        raise ValueError(f"unsupported pressure: {pressure}")
    if packet.get("state") != "PUBLIC_SAFE_PACKET_COMPILED__DELIVERY_NOT_PICKUP":
        raise ValueError("source packet state unexpected")

    selected = list(packet.get("selected_pulses") or [])
    if not all(isinstance(x, dict) for x in selected):
        raise ValueError("selected_pulses must contain objects")

    retained: list[dict[str, Any]] = []
    digest_entries: list[dict[str, Any]] = []
    digest_indices: list[int] = []
    for index, entry in enumerate(selected):
        delivery_class = str(entry.get("delivery_class") or "")
        if delivery_class == "DIGEST":
            digest_entries.append(entry)
            digest_indices.append(index)
        else:
            retained.append(entry)

    groups: list[dict[str, Any]] = []
    if pressure == "LOW":
        retained.extend(digest_entries)
    elif digest_entries:
        size = chunk_size_for_pressure(pressure, len(digest_entries))
        for group_index, start in enumerate(range(0, len(digest_entries), size)):
            group_entries = digest_entries[start:start + size]
            group_indices = digest_indices[start:start + size]
            groups.append(summarize_group(group_entries, group_indices, group_index))

    omitted_fields = [
        "subject",
        "evidence_refs",
        "source_identity",
        "authority_ceiling",
        "confidentiality",
        "wake_conditions",
        "digest_state",
    ] if groups else []

    packet_sha = sha256_bytes(packet_raw)
    source_digest_hashes = [entry_sha256(e) for e in digest_entries]
    projection_basis = {
        "packet_sha256": packet_sha,
        "pressure": pressure,
        "digest_hashes": source_digest_hashes,
        "group_ids": [g["digest_group_id"] for g in groups],
    }
    visible_item_count = len(retained) + len(groups)

    return {
        "schema":"CoPulseDigestProjection.R0D.v0.1-candidate",
        "state":"DIGEST_PROJECTION_COMPILED__SOURCE_PACKET_PRESERVED__NO_ACK_MUTATION",
        "projection_id":"copulsedigestprojection:" + sha256_bytes(canonical_bytes(projection_basis))[:24],
        "receiver_id":packet.get("receiver_id"),
        "profile_id":packet.get("profile_id"),
        "pressure":pressure,
        "source_packet":{
            "packet_id":packet.get("packet_id"),
            "sha256":packet_sha,
            "selected_entry_count":len(selected),
            "candidate_delivered_cursor":(packet.get("cursor") or {}).get("candidate_delivered_cursor"),
            "ack_cursor_unchanged":(packet.get("cursor") or {}).get("ack_cursor_unchanged"),
        },
        "retained_entries":retained,
        "digest_groups":groups,
        "loss_report":{
            "compaction_applied":bool(groups),
            "source_digest_entry_count":len(digest_entries),
            "digest_group_count":len(groups),
            "source_selected_entry_count":len(selected),
            "visible_item_count":visible_item_count,
            "visible_item_reduction":len(selected) - visible_item_count,
            "individual_digest_fields_omitted_from_projection":omitted_fields,
            "individual_digest_entries_remain_replayable_from_exact_source_packet":True,
            "semantic_summary_generated":False,
            "source_entries_deleted":False,
        },
        "effects":{
            "source_packet_mutation":0,
            "ack_cursor_mutation":0,
            "receiver_context_mutation":0,
            "provider_session_mutation":0,
            "authority_change":0,
        },
        "next":"EXACT_REPLAY_VERIFY_DIGEST_MANIFEST_BEFORE_ANY_SOURCE_RETIREMENT_OR_INTEGRATION_CLAIM",
        "nonclaims":[
            "COMPACTION_NE_DELETION",
            "DIGEST_NE_SEMANTIC_EQUIVALENCE",
            "PROJECTION_NE_SOURCE_PACKET",
            "CANDIDATE_DELIVERED_CURSOR_NE_ACK_CURSOR",
            "COMPACTION_NE_RECEIVER_PICKUP",
            "COMPACTION_NE_INTEGRATION",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", required=True)
    ap.add_argument("--pressure", required=True, choices=sorted(PRESSURES))
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    packet_path = Path(args.packet).resolve()
    out = Path(args.output).resolve()
    if out.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out}")

    packet, raw = load_object(packet_path)
    projection = compact(packet, raw, args.pressure)
    out.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(projection, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    out.write_bytes(encoded)
    print(json.dumps({
        "STATE":projection["state"],
        "OUTPUT":str(out),
        "OUTPUT_SHA256":sha256_bytes(encoded),
        "PRESSURE":args.pressure,
        "SOURCE_SELECTED":projection["loss_report"]["source_selected_entry_count"],
        "SOURCE_DIGEST":projection["loss_report"]["source_digest_entry_count"],
        "DIGEST_GROUPS":projection["loss_report"]["digest_group_count"],
        "VISIBLE_ITEMS":projection["loss_report"]["visible_item_count"],
        "ACK_MUTATION_EXECUTED":False,
        "NEXT":projection["next"],
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
