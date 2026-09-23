from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FEED_SURFACE = "CoEvoDeltaFeed"
RECEIPT_SCHEMA = "CoAll.CoEvoSubscriptionReceiverReceipt.v0.1-candidate"
PACKET_SCHEMA = "CoAll.CoEvoSubscriptionPickupPacket.v0.1-candidate"


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def parse_dt(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return dt.astimezone(timezone.utc)


def load_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(obj, dict):
        raise ValueError(f"JSON_OBJECT_REQUIRED={path}")
    return obj


def load_deltas(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig")
    stripped = text.lstrip()
    if not stripped:
        return []
    if stripped.startswith("["):
        obj = json.loads(text)
        if not isinstance(obj, list) or not all(isinstance(x, dict) for x in obj):
            raise ValueError("DELTA_ARRAY_OF_OBJECTS_REQUIRED")
        return obj
    rows: list[dict[str, Any]] = []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        obj = json.loads(line)
        if not isinstance(obj, dict):
            raise ValueError(f"DELTA_JSONL_OBJECT_REQUIRED line={n}")
        rows.append(obj)
    return rows


def subscription_map(subscriptions: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = subscriptions.get("subscriptions")
    if not isinstance(rows, list) or not rows:
        raise ValueError("SUBSCRIPTIONS_REQUIRED")
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("SUBSCRIPTION_OBJECT_REQUIRED")
        domain = row.get("domain")
        temp = row.get("temperature")
        if not isinstance(domain, str) or not domain:
            raise ValueError("SUBSCRIPTION_DOMAIN_REQUIRED")
        if temp not in {"HOT", "WARM", "DIGEST", "SLEEP"}:
            raise ValueError(f"SUBSCRIPTION_TEMPERATURE_INVALID={temp}")
        if domain in out:
            raise ValueError(f"SUBSCRIPTION_DOMAIN_DUPLICATE={domain}")
        out[domain] = row
    return out


def material_only(subscriptions: dict[str, Any]) -> bool:
    policy = subscriptions.get("material_delta_policy") or {}
    return bool(policy.get("emit_on_material_change_only", False))


def quiet_on_empty(subscriptions: dict[str, Any]) -> bool:
    policy = subscriptions.get("material_delta_policy") or {}
    return bool(policy.get("quiet_when_no_material_delta", False))


def cursor_from_receipt(receipt: dict[str, Any] | None) -> datetime | None:
    if receipt is None:
        return None
    value = receipt.get("new_cursor")
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("CURSOR_MUST_BE_STRING")
    return parse_dt(value)


def validate_delta(delta: dict[str, Any]) -> None:
    for key in ("delta_id", "observed_at", "domain", "subject", "relation", "materiality"):
        if key not in delta:
            raise ValueError(f"DELTA_FIELD_REQUIRED={key}")
    if not isinstance(delta["delta_id"], str) or not delta["delta_id"]:
        raise ValueError("DELTA_ID_INVALID")
    parse_dt(str(delta["observed_at"]))
    domains = delta["domain"]
    if not isinstance(domains, list) or not domains or not all(isinstance(x, str) and x for x in domains):
        raise ValueError(f"DELTA_DOMAIN_INVALID={delta['delta_id']}")
    if delta["materiality"] not in {"MATERIAL", "NONMATERIAL", "UNKNOWN"}:
        raise ValueError(f"DELTA_MATERIALITY_INVALID={delta['delta_id']}")


def dedupe_deltas(deltas: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    by_id: dict[str, tuple[str, dict[str, Any]]] = {}
    exact_duplicates = 0
    for delta in deltas:
        validate_delta(delta)
        delta_id = delta["delta_id"]
        digest = sha256_bytes(canonical_bytes(delta))
        prior = by_id.get(delta_id)
        if prior is None:
            by_id[delta_id] = (digest, delta)
            continue
        if prior[0] == digest:
            exact_duplicates += 1
            continue
        raise RuntimeError(f"HOLD_DIVERGENT_DELTA_ID_COLLISION={delta_id}")
    ordered = [item[1] for item in by_id.values()]
    ordered.sort(key=lambda x: (parse_dt(x["observed_at"]), x["delta_id"]))
    return ordered, exact_duplicates


def eligible_subscription(delta: dict[str, Any], subs: dict[str, dict[str, Any]], wake_domains: set[str]) -> tuple[str, str] | None:
    candidates: list[tuple[int, str, str]] = []
    rank = {"HOT": 0, "WARM": 1, "DIGEST": 2, "SLEEP": 3}
    for domain in delta["domain"]:
        row = subs.get(domain)
        if row is None:
            continue
        temp = row["temperature"]
        if temp == "SLEEP" and domain not in wake_domains:
            continue
        candidates.append((rank[temp], domain, temp))
    if not candidates:
        return None
    _, domain, temp = sorted(candidates)[0]
    return domain, temp


def digest_projection(delta: dict[str, Any], matched_domain: str) -> dict[str, Any]:
    return {
        "delta_id": delta["delta_id"],
        "observed_at": delta["observed_at"],
        "matched_domain": matched_domain,
        "subject": delta["subject"],
        "relation": delta["relation"],
        "epistemic_class": delta.get("epistemic_class", "UNKNOWN"),
        "materiality": delta["materiality"],
        "source_refs": delta.get("source_refs", []),
        "next_receiver": delta.get("next_receiver"),
        "projection": "DIGEST",
    }


def select_deltas(
    subscriptions: dict[str, Any],
    deltas: list[dict[str, Any]],
    prior_cursor: datetime | None,
    wake_domains: set[str],
) -> tuple[list[dict[str, Any]], dict[str, int], str | None]:
    subs = subscription_map(subscriptions)
    material_filter = material_only(subscriptions)
    selected: list[dict[str, Any]] = []
    stats = {
        "input_unique": len(deltas),
        "before_or_at_cursor": 0,
        "nonmaterial_filtered": 0,
        "unsubscribed_or_sleeping": 0,
        "selected_full": 0,
        "selected_digest": 0,
    }
    max_seen: datetime | None = prior_cursor

    for delta in deltas:
        observed = parse_dt(delta["observed_at"])
        if max_seen is None or observed > max_seen:
            max_seen = observed
        if prior_cursor is not None and observed <= prior_cursor:
            stats["before_or_at_cursor"] += 1
            continue
        if material_filter and delta["materiality"] != "MATERIAL":
            stats["nonmaterial_filtered"] += 1
            continue
        matched = eligible_subscription(delta, subs, wake_domains)
        if matched is None:
            stats["unsubscribed_or_sleeping"] += 1
            continue
        domain, temp = matched
        if temp == "DIGEST":
            selected.append(digest_projection(delta, domain))
            stats["selected_digest"] += 1
        else:
            full = dict(delta)
            full["_receiver"] = {"matched_domain": domain, "temperature": temp, "projection": "FULL"}
            selected.append(full)
            stats["selected_full"] += 1

    cursor = None if max_seen is None else max_seen.isoformat().replace("+00:00", "Z")
    return selected, stats, cursor


def write_new(path: Path, obj: dict[str, Any]) -> str:
    if path.exists():
        raise FileExistsError(f"NO_CLOBBER={path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = canonical_bytes(obj)
    path.write_bytes(raw)
    return sha256_bytes(raw)


def build_outputs(
    subscriptions: dict[str, Any],
    deltas: list[dict[str, Any]],
    prior_receipt: dict[str, Any] | None,
    wake_domains: set[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    unique, exact_duplicates = dedupe_deltas(deltas)
    prior_cursor = cursor_from_receipt(prior_receipt)
    selected, stats, new_cursor = select_deltas(subscriptions, unique, prior_cursor, wake_domains)
    stats["input_total"] = len(deltas)
    stats["exact_duplicates_suppressed"] = exact_duplicates
    stats["selected_total"] = len(selected)

    packet = {
        "schema": PACKET_SCHEMA,
        "subscriber_id": subscriptions.get("subscriber_id"),
        "prior_cursor": None if prior_cursor is None else prior_cursor.isoformat().replace("+00:00", "Z"),
        "new_cursor": new_cursor,
        "selected": selected,
        "stats": stats,
        "quiet": bool(not selected and quiet_on_empty(subscriptions)),
        "authority_transfer": "NONE",
        "nonclaims": [
            "CURSOR_NE_PICKUP_PROOF",
            "SUBSCRIPTION_NE_AUTHORITY",
            "ROUTE_NE_AUTHORITY",
            "EMPTY_PACKET_NE_GLOBAL_WORK_COMPLETE",
        ],
    }
    packet_sha = sha256_bytes(canonical_bytes(packet))
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "state": "PASS_COEVO_SUBSCRIPTION_RECEIVER",
        "subscriber_id": subscriptions.get("subscriber_id"),
        "packet_sha256": packet_sha,
        "prior_cursor": packet["prior_cursor"],
        "new_cursor": new_cursor,
        "selected_total": len(selected),
        "exact_duplicates_suppressed": exact_duplicates,
        "quiet": packet["quiet"],
        "source_mutations": 0,
        "network_effects": 0,
        "authority_transfer": "NONE",
    }
    return packet, receipt


def run_selftest() -> None:
    subscriptions = {
        "subscriber_id": "SELFTEST",
        "subscriptions": [
            {"domain": "CoPressure+/CoEnerget+", "temperature": "HOT"},
            {"domain": "CoRoute+/CoCapabilityMesh+/CoRouteMorph+", "temperature": "WARM"},
            {"domain": "CoIndex+/CoLex+/CoGibberTru+/CoPriMath+", "temperature": "DIGEST"},
            {"domain": "RickBar+/CoUX+/CoHumour+/CoHighlight+", "temperature": "SLEEP"},
        ],
        "material_delta_policy": {
            "emit_on_material_change_only": True,
            "dedupe_before_emit": True,
            "quiet_when_no_material_delta": True,
        },
    }
    d1 = {
        "delta_id": "d1",
        "session_id": "s",
        "observed_at": "2026-09-23T11:00:00Z",
        "domain": ["CoPressure+/CoEnerget+"],
        "subject": "pressure",
        "relation": "changed",
        "epistemic_class": "OBSERVED",
        "source_refs": [],
        "target_surfaces": ["CoCivium"],
        "mutation_class": "OBSERVE",
        "authority_ceiling": "NONE",
        "confidentiality": "PUBLIC",
        "materiality": "MATERIAL",
        "next_receiver": "SELFTEST",
    }
    d2 = dict(d1, delta_id="d2", observed_at="2026-09-23T11:01:00Z", materiality="NONMATERIAL")
    d3 = dict(
        d1,
        delta_id="d3",
        observed_at="2026-09-23T11:02:00Z",
        domain=["CoIndex+/CoLex+/CoGibberTru+/CoPriMath+"],
        subject="lex",
    )
    d4 = dict(
        d1,
        delta_id="d4",
        observed_at="2026-09-23T11:03:00Z",
        domain=["RickBar+/CoUX+/CoHumour+/CoHighlight+"],
        subject="ux",
    )
    packet, receipt = build_outputs(subscriptions, [d1, d1, d2, d3, d4], None, set())
    assert receipt["state"] == "PASS_COEVO_SUBSCRIPTION_RECEIVER"
    assert receipt["selected_total"] == 2
    assert receipt["exact_duplicates_suppressed"] == 1
    assert packet["stats"]["nonmaterial_filtered"] == 1
    assert packet["stats"]["unsubscribed_or_sleeping"] == 1
    assert packet["selected"][0]["_receiver"]["temperature"] == "HOT"
    assert packet["selected"][1]["projection"] == "DIGEST"
    assert packet["new_cursor"] == "2026-09-23T11:03:00Z"

    packet2, receipt2 = build_outputs(subscriptions, [d1, d2, d3, d4], receipt, set())
    assert receipt2["selected_total"] == 0
    assert receipt2["quiet"] is True

    packet3, receipt3 = build_outputs(subscriptions, [d4], None, {"RickBar+/CoUX+/CoHumour+/CoHighlight+"})
    assert receipt3["selected_total"] == 1
    assert packet3["selected"][0]["_receiver"]["temperature"] == "SLEEP"

    divergent = dict(d1, relation="different")
    try:
        build_outputs(subscriptions, [d1, divergent], None, set())
    except RuntimeError as exc:
        assert str(exc).startswith("HOLD_DIVERGENT_DELTA_ID_COLLISION=")
    else:
        raise AssertionError("divergent duplicate was not held")

    print("SELFTEST=PASS")
    print("CASES=4")
    print("EXACT_DUPLICATE_SUPPRESSION=PASS")
    print("MATERIALITY_FILTER=PASS")
    print("SLEEP_WAKE_GATE=PASS")
    print("DIVERGENT_ID_COLLISION=HOLD")
    print("QUIET_ON_NO_MATERIAL_DELTA=PASS")


def main() -> int:
    parser = argparse.ArgumentParser(description="Filter CoEvoDelta objects through bounded session subscriptions and advance a receiver-relative currentness cursor.")
    parser.add_argument("--subscriptions", type=Path)
    parser.add_argument("--deltas", type=Path)
    parser.add_argument("--cursor-receipt", type=Path)
    parser.add_argument("--wake-domain", action="append", default=[])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.selftest:
        run_selftest()
        return 0

    required = [args.subscriptions, args.deltas, args.out, args.receipt]
    if any(x is None for x in required):
        parser.error("--subscriptions --deltas --out --receipt are required unless --selftest is used")

    subscriptions = load_json(args.subscriptions)
    deltas = load_deltas(args.deltas)
    prior = load_json(args.cursor_receipt) if args.cursor_receipt else None

    packet, receipt = build_outputs(subscriptions, deltas, prior, set(args.wake_domain))

    # All parsing, validation, dedupe, collision checks, filtering, and cursor computation happen before first write.
    packet_sha = write_new(args.out, packet)
    if packet_sha != receipt["packet_sha256"]:
        raise RuntimeError("PACKET_SHA_INTERNAL_DRIFT")
    receipt_sha = write_new(args.receipt, receipt)

    print(f"STATE={receipt['state']}")
    print(f"PACKET={args.out}")
    print(f"PACKET_SHA256={packet_sha}")
    print(f"RECEIPT={args.receipt}")
    print(f"RECEIPT_SHA256={receipt_sha}")
    print(f"SELECTED_TOTAL={receipt['selected_total']}")
    print(f"EXACT_DUPLICATES_SUPPRESSED={receipt['exact_duplicates_suppressed']}")
    print(f"QUIET={receipt['quiet']}")
    print(f"NEW_CURSOR={receipt['new_cursor']}")
    print("SOURCE_MUTATIONS=0")
    print("NETWORK_EFFECTS=0")
    print("AUTHORITY_TRANSFER=NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
