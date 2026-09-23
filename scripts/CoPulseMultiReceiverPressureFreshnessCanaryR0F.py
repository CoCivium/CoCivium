#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"not object: {path}")
    return obj


def run_json(cmd: list[str]) -> dict[str, Any]:
    cp = subprocess.run(cmd, check=True, capture_output=True, text=True)
    line = cp.stdout.strip().splitlines()[-1]
    obj = json.loads(line)
    if not isinstance(obj, dict):
        raise RuntimeError("terminal output not JSON object")
    return obj


def pulse(pid: str, cursor: int, delivery: str, domain: str) -> dict[str, Any]:
    return {
        "pulse_id": pid,
        "cursor": cursor,
        "delivery_class": delivery,
        "digest_state": "DIGEST_CLASS__NOT_YET_COMPACTED" if delivery == "DIGEST" else None,
        "subject": pid,
        "relation_type": "relates_to",
        "epistemic_class": "OBSERVED",
        "domains": [domain],
        "topics": ["r0f-fixture"],
        "evidence_refs": [f"fixture://{pid}"],
        "source_identity": f"fixture-source:{pid}",
        "authority_ceiling": "CANDIDATE_ONLY",
        "confidentiality": "PUBLIC",
        "wake_conditions": [],
    }


def packet_from_field(
    receiver_id: str,
    profile_id: str,
    last_acked_cursor: int,
    pulse_field: list[dict[str, Any]],
    pulse_field_sha256: str,
) -> dict[str, Any]:
    selected = [
        row for row in pulse_field
        if int(row["cursor"]) > last_acked_cursor
    ]
    counts = {"HOT": 0, "WARM": 0, "DIGEST": 0, "SLEEP": 0, "OLDER_OR_ACKED": 0}
    for row in selected:
        counts[row["delivery_class"]] += 1
    counts["OLDER_OR_ACKED"] = len(pulse_field) - len(selected)
    max_seen = max(int(row["cursor"]) for row in pulse_field)
    return {
        "schema": "CoPulseSubscriptionPacket.R0A.v0.1-candidate",
        "state": "PUBLIC_SAFE_PACKET_COMPILED__DELIVERY_NOT_PICKUP",
        "packet_id": "copulsepacket:r0f:" + receiver_id,
        "receiver_id": receiver_id,
        "profile_id": profile_id,
        "source_bindings": {"pulses_sha256": pulse_field_sha256},
        "cursor": {
            "last_acked_cursor": last_acked_cursor,
            "max_seen_cursor": max_seen,
            "candidate_delivered_cursor": max_seen,
            "ack_cursor_unchanged": last_acked_cursor,
        },
        "counts": counts,
        "selected_pulses": selected,
        "effects": {
            "receiver_context_mutation": 0,
            "provider_session_mutation": 0,
            "authority_change": 0,
            "public_outreach": 0,
        },
        "next": "RECEIVER_EXACT_PACKET_READPROOF_BEFORE_ACK_CURSOR_ADVANCE",
        "nonclaims": ["DELIVERY_NE_PICKUP", "PACKET_SELECTION_NE_ACK_COMMIT"],
    }


def pressure(
    receiver_id: str,
    name: str,
    sampled_at: str,
    capacity: int,
) -> dict[str, Any]:
    return {
        "sample_id": f"pressure:r0f:{name}",
        "receiver_id": receiver_id,
        "sampled_at": sampled_at,
        "capacity_source": "SYNTHETIC_FIXTURE",
        "max_currentness_items": capacity,
        "max_digest_summaries": 4,
        "authority_ceiling": "CANDIDATE_ONLY",
        "notes": ["bounded R0F synthetic canary"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--freshness-gate", required=True)
    ap.add_argument("--r0e-budget", required=True)
    ap.add_argument("--r0d-compactor", required=True)
    ap.add_argument("--r0d-replay", required=True)
    ap.add_argument("--out-root", required=True)
    args = ap.parse_args()

    root = Path(args.out_root).resolve()
    if root.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={root}")
    root.mkdir(parents=True, exist_ok=False)

    evaluated_at = "2026-09-23T12:35:00Z"
    max_age_seconds = 300
    max_future_skew_seconds = 30

    pulse_field = [
        pulse("pulse.hot.001", 1, "HOT", "CoUX+/CoSurface+"),
        pulse("pulse.warm.002", 2, "WARM", "CoLex+"),
        pulse("pulse.digest.003", 3, "DIGEST", "CoHumour+"),
        pulse("pulse.digest.004", 4, "DIGEST", "CoTheoryAll+"),
        pulse("pulse.digest.005", 5, "DIGEST", "CoHumour+"),
        pulse("pulse.digest.006", 6, "DIGEST", "CoTheoryAll+"),
    ]
    field_path = root / "shared-pulse-field.json"
    field_path.write_text(json.dumps(pulse_field, indent=2) + "\n", encoding="utf-8")
    field_sha = sha256_path(field_path)

    receivers = [
        {
            "name": "receiver-a",
            "receiver_id": "VirtualReceiver-CoGeneralist-R0F-A",
            "profile_id": "CoGeneralist",
            "last_acked_cursor": 2,
            "sampled_at": "2026-09-23T12:34:40Z",
            "capacity": 6,
            "expect_freshness": "PASS_FRESH_PRESSURE_SAMPLE",
            "expect_budget": 4,
            "expect_tier": "LIGHT",
        },
        {
            "name": "receiver-b",
            "receiver_id": "VirtualReceiver-CoGeneralist-R0F-B",
            "profile_id": "CoGeneralist",
            "last_acked_cursor": 0,
            "sampled_at": "2026-09-23T12:34:40Z",
            "capacity": 3,
            "expect_freshness": "PASS_FRESH_PRESSURE_SAMPLE",
            "expect_budget": 1,
            "expect_tier": "HIGH",
        },
        {
            "name": "receiver-c-stale",
            "receiver_id": "VirtualReceiver-CoGeneralist-R0F-C",
            "profile_id": "CoGeneralist",
            "last_acked_cursor": 0,
            "sampled_at": "2026-09-23T12:20:00Z",
            "capacity": 6,
            "expect_freshness": "HOLD_STALE_PRESSURE_SAMPLE",
            "expect_budget": None,
            "expect_tier": None,
        },
    ]

    records: list[dict[str, Any]] = []
    for spec in receivers:
        packet = packet_from_field(
            spec["receiver_id"],
            spec["profile_id"],
            spec["last_acked_cursor"],
            pulse_field,
            field_sha,
        )
        packet_path = root / f"{spec['name']}-packet.json"
        packet_path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")

        pressure_obj = pressure(
            spec["receiver_id"],
            spec["name"],
            spec["sampled_at"],
            spec["capacity"],
        )
        pressure_path = root / f"{spec['name']}-pressure.json"
        pressure_path.write_text(json.dumps(pressure_obj, indent=2) + "\n", encoding="utf-8")

        freshness_path = root / f"{spec['name']}-freshness.json"
        freshness_terminal = run_json([
            sys.executable, str(Path(args.freshness_gate).resolve()),
            "--pressure", str(pressure_path),
            "--evaluated-at", evaluated_at,
            "--max-age-seconds", str(max_age_seconds),
            "--max-future-skew-seconds", str(max_future_skew_seconds),
            "--output", str(freshness_path),
        ])
        freshness = load(freshness_path)
        if freshness["state"] != spec["expect_freshness"]:
            raise SystemExit("FAIL_CLOSED__FRESHNESS_STATE=" + spec["name"])

        record: dict[str, Any] = {
            "name": spec["name"],
            "receiver_id": spec["receiver_id"],
            "source_pulse_field_sha256": field_sha,
            "last_acked_cursor": spec["last_acked_cursor"],
            "selected_cursors": [int(row["cursor"]) for row in packet["selected_pulses"]],
            "pressure_sampled_at": spec["sampled_at"],
            "pressure_age_seconds": freshness["age_seconds"],
            "freshness_state": freshness["state"],
            "freshness_output_sha256": sha256_path(freshness_path),
            "freshness_terminal": freshness_terminal,
        }

        if freshness["state"] != "PASS_FRESH_PRESSURE_SAMPLE":
            record["budget_election_state"] = "NOT_RUN_STALE_PRESSURE_HELD"
            records.append(record)
            continue

        election_path = root / f"{spec['name']}-election.json"
        election_terminal = run_json([
            sys.executable, str(Path(args.r0e_budget).resolve()),
            "--packet", str(packet_path),
            "--pressure", str(pressure_path),
            "--output", str(election_path),
        ])
        election = load(election_path)
        if election["elected_digest_budget"] != spec["expect_budget"]:
            raise SystemExit("FAIL_CLOSED__BUDGET=" + spec["name"])
        if election["pressure_vector"]["tier"] != spec["expect_tier"]:
            raise SystemExit("FAIL_CLOSED__TIER=" + spec["name"])

        compacted_path = root / f"{spec['name']}-compacted.json"
        compactor_terminal = run_json([
            sys.executable, str(Path(args.r0d_compactor).resolve()),
            "--packet", str(packet_path),
            "--digest-budget", str(spec["expect_budget"]),
            "--output", str(compacted_path),
        ])
        replay_path = root / f"{spec['name']}-replay.json"
        replay_terminal = run_json([
            sys.executable, str(Path(args.r0d_replay).resolve()),
            "--compacted", str(compacted_path),
            "--source-packet", str(packet_path),
            "--output", str(replay_path),
        ])
        replay = load(replay_path)
        expected_digest_count = sum(
            1 for row in packet["selected_pulses"] if row["delivery_class"] == "DIGEST"
        )
        if replay["coverage"]["replayed_digest_count"] != expected_digest_count:
            raise SystemExit("FAIL_CLOSED__REPLAY_COUNT=" + spec["name"])
        if not replay["coverage"]["exact_object_equality"]:
            raise SystemExit("FAIL_CLOSED__REPLAY_EQUALITY=" + spec["name"])
        if packet["cursor"]["last_acked_cursor"] != spec["last_acked_cursor"]:
            raise SystemExit("FAIL_CLOSED__ACK_CURSOR_MUTATED=" + spec["name"])

        record.update({
            "budget_election_state": election["state"],
            "elected_digest_budget": election["elected_digest_budget"],
            "pressure_tier": election["pressure_vector"]["tier"],
            "election_output_sha256": sha256_path(election_path),
            "compacted_output_sha256": sha256_path(compacted_path),
            "replay_output_sha256": sha256_path(replay_path),
            "replayed_digest_count": replay["coverage"]["replayed_digest_count"],
            "exact_replay": replay["coverage"]["exact_object_equality"],
            "election_terminal": election_terminal,
            "compactor_terminal": compactor_terminal,
            "replay_terminal": replay_terminal,
        })
        records.append(record)

    a, b, c = records
    if a["source_pulse_field_sha256"] != b["source_pulse_field_sha256"]:
        raise SystemExit("FAIL_CLOSED__SOURCE_FIELD_DIVERGED")
    if a["elected_digest_budget"] == b["elected_digest_budget"]:
        raise SystemExit("FAIL_CLOSED__EXPECTED_DIVERGENT_BUDGETS")
    if a["last_acked_cursor"] == b["last_acked_cursor"]:
        raise SystemExit("FAIL_CLOSED__EXPECTED_INDEPENDENT_ACK_STATE")
    if c["budget_election_state"] != "NOT_RUN_STALE_PRESSURE_HELD":
        raise SystemExit("FAIL_CLOSED__STALE_SAMPLE_REACHED_BUDGET_ELECTION")

    result = {
        "schema": "CoPulseMultiReceiverPressureFreshnessCanary.R0F.v0.1-candidate",
        "state": "PASS_R0F_EXPLICIT_STALENESS_GATE__DIVERGENT_RECEIVER_BUDGETS__INDEPENDENT_ACK__EXACT_REPLAY",
        "evaluated_at": evaluated_at,
        "max_age_seconds": max_age_seconds,
        "max_future_skew_seconds": max_future_skew_seconds,
        "shared_pulse_field_sha256": field_sha,
        "receivers": records,
        "checks": {
            "same_shared_pulse_field": True,
            "fresh_receivers": 2,
            "stale_receivers_held": 1,
            "fresh_budget_pair": [a["elected_digest_budget"], b["elected_digest_budget"]],
            "divergent_fresh_budgets": True,
            "independent_ack_pair": [a["last_acked_cursor"], b["last_acked_cursor"]],
            "independent_ack_state_preserved": True,
            "exact_replay_for_fresh_receivers": True,
            "stale_sample_never_reached_budget_election": True,
            "ack_cursor_mutation": False,
            "source_deletion": False,
        },
        "effects": {
            "provider_session_mutation": 0,
            "receiver_context_mutation": 0,
            "ack_cursor_mutation": 0,
            "authority_change": 0,
            "source_deletion": 0,
        },
        "next": "R0G_CAPACITY_SOURCE_PROVENANCE_AND_LIVE_RECEIVER_BINDING_CANARY",
        "nonclaims": [
            "FRESHNESS_NE_TRUTH",
            "FRESH_SAMPLE_NE_CAPACITY_ACCURACY_PROOF",
            "STALE_SAMPLE_NE_ZERO_CAPACITY",
            "DIVERGENT_BUDGETS_NE_INCONSISTENCY",
            "INDEPENDENT_ACK_NE_GLOBAL_ACK",
            "LOCAL_CANARY_NE_LIVE_GLOBAL_BUS",
        ],
    }
    result_path = root / "r0f-result.json"
    encoded = (json.dumps(result, indent=2) + "\n").encode("utf-8")
    result_path.write_bytes(encoded)
    print(json.dumps({
        "STATE": result["state"],
        "OUTPUT": str(result_path),
        "OUTPUT_SHA256": sha256_bytes(encoded),
        "FRESH_BUDGETS": [a["elected_digest_budget"], b["elected_digest_budget"]],
        "ACK_PAIR": [a["last_acked_cursor"], b["last_acked_cursor"]],
        "STALE_HELD": True,
        "ACK_CURSOR_MUTATION": 0,
        "NEXT": result["next"],
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
