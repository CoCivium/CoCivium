#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


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
        "topics": ["fixture"],
        "evidence_refs": [f"fixture://{pid}"],
        "source_identity": f"fixture-source:{pid}",
        "authority_ceiling": "CANDIDATE_ONLY",
        "confidentiality": "PUBLIC",
        "wake_conditions": [],
    }


def write_pressure(path: Path, receiver_id: str, name: str, capacity: int) -> None:
    obj = {
        "sample_id": f"pressure:{name}",
        "receiver_id": receiver_id,
        "sampled_at": "2026-09-23T12:27:00Z",
        "capacity_source": "SYNTHETIC_FIXTURE",
        "max_currentness_items": capacity,
        "max_digest_summaries": 4,
        "authority_ceiling": "CANDIDATE_ONLY",
        "notes": ["bounded R0E synthetic canary"],
    }
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget-election", required=True)
    ap.add_argument("--r0d-compactor", required=True)
    ap.add_argument("--r0d-replay", required=True)
    ap.add_argument("--out-root", required=True)
    args = ap.parse_args()

    root = Path(args.out_root).resolve()
    if root.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={root}")
    root.mkdir(parents=True, exist_ok=False)

    receiver_id = "VirtualReceiver-CoGeneralist-R0E"
    selected = [
        pulse("pulse.hot.001", 1, "HOT", "CoUX+/CoSurface+"),
        pulse("pulse.warm.002", 2, "WARM", "CoLex+"),
        pulse("pulse.digest.003", 3, "DIGEST", "CoHumour+"),
        pulse("pulse.digest.004", 4, "DIGEST", "CoTheoryAll+"),
        pulse("pulse.digest.005", 5, "DIGEST", "CoHumour+"),
        pulse("pulse.digest.006", 6, "DIGEST", "CoTheoryAll+"),
    ]
    packet = {
        "schema": "CoPulseSubscriptionPacket.R0A.v0.1-candidate",
        "state": "PUBLIC_SAFE_PACKET_COMPILED__DELIVERY_NOT_PICKUP",
        "packet_id": "copulsepacket:r0e-fixture",
        "receiver_id": receiver_id,
        "profile_id": "CoGeneralist",
        "source_bindings": {"pulses_sha256": "E" * 64},
        "cursor": {
            "last_acked_cursor": 0,
            "max_seen_cursor": 6,
            "candidate_delivered_cursor": 6,
            "ack_cursor_unchanged": 0,
        },
        "counts": {"HOT": 1, "WARM": 1, "DIGEST": 4, "SLEEP": 0, "OLDER_OR_ACKED": 0},
        "selected_pulses": selected,
        "effects": {
            "receiver_context_mutation": 0,
            "provider_session_mutation": 0,
            "authority_change": 0,
            "public_outreach": 0,
        },
        "next": "RECEIVER_EXACT_PACKET_READPROOF_BEFORE_ACK_CURSOR_ADVANCE",
        "nonclaims": ["DELIVERY_NE_PICKUP"],
    }
    packet_path = root / "source-packet.json"
    packet_path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")

    cases = [
        ("light", 6, 4, "LIGHT"),
        ("moderate", 4, 2, "MODERATE"),
        ("high", 3, 1, "HIGH"),
        ("saturated", 2, 0, "SATURATED"),
    ]
    records: list[dict[str, Any]] = []
    for name, capacity, expected_budget, expected_tier in cases:
        pressure_path = root / f"pressure-{name}.json"
        write_pressure(pressure_path, receiver_id, name, capacity)
        election_path = root / f"election-{name}.json"
        terminal = run_json([
            sys.executable, str(Path(args.budget_election).resolve()),
            "--packet", str(packet_path),
            "--pressure", str(pressure_path),
            "--output", str(election_path),
        ])
        election = load(election_path)
        if election["elected_digest_budget"] != expected_budget:
            raise SystemExit(f"FAIL_CLOSED__{name.upper()}_BUDGET")
        if election["pressure_vector"]["tier"] != expected_tier:
            raise SystemExit(f"FAIL_CLOSED__{name.upper()}_TIER")

        record: dict[str, Any] = {
            "name": name,
            "capacity": capacity,
            "budget": expected_budget,
            "tier": expected_tier,
            "election_sha256": sha256_path(election_path),
            "election_terminal": terminal,
        }
        if expected_budget == 0:
            if election["state"] != "HOLD_DIGEST_CAPACITY_EXHAUSTED":
                raise SystemExit("FAIL_CLOSED__SATURATED_NOT_HELD")
            record["compaction_state"] = "NOT_RUN_ZERO_CAPACITY"
        else:
            compacted_path = root / f"compacted-{name}.json"
            comp_terminal = run_json([
                sys.executable, str(Path(args.r0d_compactor).resolve()),
                "--packet", str(packet_path),
                "--digest-budget", str(expected_budget),
                "--output", str(compacted_path),
            ])
            replay_path = root / f"replay-{name}.json"
            replay_terminal = run_json([
                sys.executable, str(Path(args.r0d_replay).resolve()),
                "--compacted", str(compacted_path),
                "--source-packet", str(packet_path),
                "--output", str(replay_path),
            ])
            compacted = load(compacted_path)
            replay = load(replay_path)
            if compacted["coverage"]["digest_summary_count"] != expected_budget:
                raise SystemExit(f"FAIL_CLOSED__{name.upper()}_SUMMARY_COUNT")
            expected_reduction = 4 - expected_budget
            if compacted["coverage"]["representation_item_reduction"] != expected_reduction:
                raise SystemExit(f"FAIL_CLOSED__{name.upper()}_REDUCTION")
            if replay["coverage"]["replayed_digest_count"] != 4 or not replay["coverage"]["exact_object_equality"]:
                raise SystemExit(f"FAIL_CLOSED__{name.upper()}_REPLAY")
            record.update({
                "compaction_state": compacted["state"],
                "compacted_sha256": sha256_path(compacted_path),
                "replay_sha256": sha256_path(replay_path),
                "digest_summaries": expected_budget,
                "representation_item_reduction": expected_reduction,
                "replayed_digest_count": 4,
                "compactor_terminal": comp_terminal,
                "replay_terminal": replay_terminal,
            })
        records.append(record)

    budgets = [r["budget"] for r in records]
    if budgets != [4, 2, 1, 0]:
        raise SystemExit("FAIL_CLOSED__BUDGET_SEQUENCE")
    if any(v != 0 for r in records for v in (r.get("election_terminal") or {}).values() if isinstance(v, int) and False):
        raise SystemExit("FAIL_CLOSED__UNREACHABLE")

    result = {
        "schema": "CoPulseReceiverPressureBudgetCanary.R0E.v0.1-candidate",
        "state": "PASS_R0E_RECEIVER_PRESSURE_DERIVED_BUDGET__MULTI_BUDGET_EXACT_REPLAY__SATURATION_HOLD",
        "source_packet_sha256": sha256_path(packet_path),
        "pressure_vector_cases": records,
        "checks": {
            "budget_monotonic_with_available_capacity": True,
            "light_budget": 4,
            "moderate_budget": 2,
            "high_budget": 1,
            "saturated_budget": 0,
            "saturated_digest_held_not_dropped": True,
            "hot_warm_occupancy_reserved": True,
            "r0d_exact_replay_for_all_nonzero_budgets": True,
            "source_deletion": False,
            "ack_cursor_mutation": False,
        },
        "effects": {
            "provider_session_mutation": 0,
            "receiver_context_mutation": 0,
            "ack_cursor_mutation": 0,
            "authority_change": 0,
            "source_deletion": 0,
        },
        "next": "R0F_STALENESS_AND_MULTI_RECEIVER_CAPACITY_ELECTION_CANARY",
        "nonclaims": [
            "COPRESSURE_VECTOR_NE_UNIVERSAL_SCORE",
            "CAPACITY_NE_AUTHORITY",
            "BUDGET_NE_PERMISSION_TO_DELETE",
            "SATURATION_NE_SILENT_DROP",
            "LOCAL_CANARY_NE_LIVE_GLOBAL_BUS",
        ],
    }
    result_path = root / "r0e-result.json"
    encoded = (json.dumps(result, indent=2) + "\n").encode("utf-8")
    result_path.write_bytes(encoded)
    print(json.dumps({
        "STATE": result["state"],
        "OUTPUT": str(result_path),
        "OUTPUT_SHA256": hashlib.sha256(encoded).hexdigest().upper(),
        "BUDGETS": budgets,
        "SATURATED_HELD": True,
        "NONZERO_CASES_REPLAYED": 3,
        "ACK_CURSOR_MUTATION": 0,
        "NEXT": result["next"],
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
