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


def count_classes(packet: dict[str, Any]) -> tuple[int, int, int]:
    hot = warm = digest = 0
    for row in list(packet.get("selected_pulses") or []):
        if not isinstance(row, dict):
            raise ValueError("FAIL_CLOSED__SELECTED_PULSE_NOT_OBJECT")
        delivery = str(row.get("delivery_class") or "")
        if delivery == "HOT":
            hot += 1
        elif delivery == "WARM":
            warm += 1
        elif delivery == "DIGEST":
            digest += 1
        else:
            raise ValueError("FAIL_CLOSED__UNKNOWN_DELIVERY_CLASS=" + delivery)
    return hot, warm, digest


def validate_pressure(pressure: dict[str, Any], receiver_id: str) -> None:
    required = (
        "sample_id",
        "receiver_id",
        "sampled_at",
        "capacity_source",
        "max_currentness_items",
        "max_digest_summaries",
        "authority_ceiling",
    )
    missing = [k for k in required if k not in pressure]
    if missing:
        raise ValueError("FAIL_CLOSED__PRESSURE_MISSING_FIELDS=" + ",".join(missing))
    if pressure["receiver_id"] != receiver_id:
        raise ValueError("FAIL_CLOSED__PRESSURE_RECEIVER_MISMATCH")
    if pressure["capacity_source"] not in {"MEASURED", "DECLARED", "SYNTHETIC_FIXTURE"}:
        raise ValueError("FAIL_CLOSED__INVALID_CAPACITY_SOURCE")
    if not isinstance(pressure["max_currentness_items"], int) or pressure["max_currentness_items"] < 0:
        raise ValueError("FAIL_CLOSED__INVALID_MAX_CURRENTNESS_ITEMS")
    if not isinstance(pressure["max_digest_summaries"], int) or pressure["max_digest_summaries"] < 1:
        raise ValueError("FAIL_CLOSED__INVALID_MAX_DIGEST_SUMMARIES")


def elect(packet: dict[str, Any], packet_raw: bytes, pressure: dict[str, Any]) -> dict[str, Any]:
    if packet.get("state") != "PUBLIC_SAFE_PACKET_COMPILED__DELIVERY_NOT_PICKUP":
        raise ValueError("FAIL_CLOSED__PACKET_STATE_UNEXPECTED")
    receiver_id = str(packet.get("receiver_id") or "")
    if not receiver_id:
        raise ValueError("FAIL_CLOSED__PACKET_RECEIVER_ID_MISSING")
    validate_pressure(pressure, receiver_id)

    hot, warm, digest = count_classes(packet)
    non_digest = hot + warm
    capacity = pressure["max_currentness_items"]
    free = max(0, capacity - non_digest)
    max_summaries = pressure["max_digest_summaries"]

    if digest == 0:
        state = "IDLE_NO_DIGEST"
        budget = 0
        tier = "NO_DIGEST"
        compact = False
        nxt = "NO_DIGEST_COMPACTION_REQUIRED"
    elif free == 0:
        state = "HOLD_DIGEST_CAPACITY_EXHAUSTED"
        budget = 0
        tier = "SATURATED"
        compact = False
        nxt = "HOLD_DIGEST_AND_REEVALUATE_RECEIVER_CAPACITY_OR_ROUTE"
    else:
        budget = min(digest, free, max_summaries)
        state = "PASS_DIGEST_BUDGET_ELECTED"
        compact = budget < digest
        if budget >= digest:
            tier = "LIGHT"
        elif budget == 1:
            tier = "HIGH"
        else:
            tier = "MODERATE"
        nxt = "RUN_R0D_COMPACTOR_WITH_ELECTED_BUDGET_AND_REQUIRE_EXACT_REPLAY"

    result = {
        "schema": "CoPulseDigestBudgetElection.R0E.v0.1-candidate",
        "state": state,
        "receiver_id": receiver_id,
        "packet_id": packet.get("packet_id"),
        "source_packet_sha256": sha256_bytes(packet_raw),
        "pressure_sample": {
            "sample_id": pressure["sample_id"],
            "sampled_at": pressure["sampled_at"],
            "capacity_source": pressure["capacity_source"],
            "authority_ceiling": pressure["authority_ceiling"],
        },
        "pressure_vector": {
            "hot_count": hot,
            "warm_count": warm,
            "digest_count": digest,
            "non_digest_occupancy": non_digest,
            "max_currentness_items": capacity,
            "free_digest_slots": free,
            "max_digest_summaries": max_summaries,
            "tier": tier,
        },
        "elected_digest_budget": budget,
        "compaction_required": compact,
        "effects": {
            "source_mutation": 0,
            "receiver_context_mutation": 0,
            "ack_cursor_mutation": 0,
            "provider_session_mutation": 0,
            "authority_change": 0,
        },
        "next": nxt,
        "nonclaims": [
            "COPRESSURE_VECTOR_NE_UNIVERSAL_SCORE",
            "CAPACITY_NE_AUTHORITY",
            "BUDGET_NE_PERMISSION_TO_DELETE",
            "ZERO_CAPACITY_NE_SILENT_DROP",
            "ELECTION_NE_COMPACTION",
            "ELECTION_NE_DELIVERY",
        ],
    }
    result["election_sha256"] = sha256_bytes(canonical(result))
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", required=True)
    ap.add_argument("--pressure", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    output = Path(args.output).resolve()
    if output.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={output}")
    try:
        packet, packet_raw = load_object(Path(args.packet).resolve())
        pressure, _ = load_object(Path(args.pressure).resolve())
        result = elect(packet, packet_raw, pressure)
    except ValueError as exc:
        raise SystemExit(str(exc))

    output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    output.write_bytes(encoded)
    print(json.dumps({
        "STATE": result["state"],
        "OUTPUT": str(output),
        "OUTPUT_SHA256": sha256_bytes(encoded),
        "ELECTED_DIGEST_BUDGET": result["elected_digest_budget"],
        "PRESSURE_TIER": result["pressure_vector"]["tier"],
        "COMPACTION_REQUIRED": result["compaction_required"],
        "ACK_CURSOR_MUTATION": 0,
        "NEXT": result["next"],
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
