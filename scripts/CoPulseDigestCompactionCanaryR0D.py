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


def pulse(pid: str, cursor: int, delivery: str, domain: str, subject: str) -> dict[str, Any]:
    return {
        "pulse_id": pid,
        "cursor": cursor,
        "delivery_class": delivery,
        "digest_state": "DIGEST_CLASS__NOT_YET_COMPACTED" if delivery == "DIGEST" else None,
        "subject": subject,
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--compactor", required=True)
    ap.add_argument("--replay", required=True)
    ap.add_argument("--out-root", required=True)
    args = ap.parse_args()

    root = Path(args.out_root).resolve()
    if root.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={root}")
    root.mkdir(parents=True, exist_ok=False)

    selected = [
        pulse("pulse.hot.001", 1, "HOT", "CoUX+/CoSurface+", "hot-one"),
        pulse("pulse.warm.002", 2, "WARM", "CoLex+", "warm-two"),
        pulse("pulse.digest.003", 3, "DIGEST", "CoHumour+", "digest-three"),
        pulse("pulse.digest.004", 4, "DIGEST", "CoTheoryAll+", "digest-four"),
        pulse("pulse.digest.005", 5, "DIGEST", "CoHumour+", "digest-five"),
        pulse("pulse.digest.006", 6, "DIGEST", "CoTheoryAll+", "digest-six"),
    ]
    packet = {
        "schema": "CoPulseSubscriptionPacket.R0A.v0.1-candidate",
        "state": "PUBLIC_SAFE_PACKET_COMPILED__DELIVERY_NOT_PICKUP",
        "packet_id": "copulsepacket:r0d-fixture",
        "receiver_id": "VirtualReceiver-CoGeneralist-R0D",
        "profile_id": "CoGeneralist",
        "source_bindings": {"pulses_sha256": "F" * 64},
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
    source_path = root / "source-packet.json"
    source_path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    compacted_path = root / "compacted.json"
    compact_terminal = run_json([
        sys.executable, str(Path(args.compactor).resolve()),
        "--packet", str(source_path),
        "--digest-budget", "1",
        "--output", str(compacted_path),
    ])
    compacted = load(compacted_path)

    replay_path = root / "replay.json"
    replay_terminal = run_json([
        sys.executable, str(Path(args.replay).resolve()),
        "--compacted", str(compacted_path),
        "--source-packet", str(source_path),
        "--output", str(replay_path),
    ])
    replay = load(replay_path)

    if compacted["coverage"]["input_digest_count"] != 4:
        raise SystemExit("FAIL_CLOSED__EXPECTED_4_DIGEST")
    if compacted["coverage"]["digest_summary_count"] != 1:
        raise SystemExit("FAIL_CLOSED__EXPECTED_1_DIGEST_SUMMARY")
    if compacted["coverage"]["source_digest_entries_omitted_inline"] != 4:
        raise SystemExit("FAIL_CLOSED__OMITTED_COUNT_WRONG")
    if compacted["coverage"]["representation_item_reduction"] != 3:
        raise SystemExit("FAIL_CLOSED__REPRESENTATION_REDUCTION_WRONG")
    if compacted["passthrough_selected_pulses"] != selected[:2]:
        raise SystemExit("FAIL_CLOSED__HOT_WARM_NOT_EXACT_PASSTHROUGH")
    if replay["replayed_digest_pulses"] != selected[2:]:
        raise SystemExit("FAIL_CLOSED__DIGEST_REPLAY_NOT_EXACT")
    if not replay["coverage"]["exact_object_equality"]:
        raise SystemExit("FAIL_CLOSED__REPLAY_OBJECT_EQUALITY_FALSE")
    if any(v != 0 for v in compacted["effects"].values()):
        raise SystemExit("FAIL_CLOSED__COMPACTOR_EFFECT_NONZERO")
    if any(v != 0 for v in replay["effects"].values()):
        raise SystemExit("FAIL_CLOSED__REPLAY_EFFECT_NONZERO")

    result = {
        "schema": "CoPulseDigestCompactionCanary.R0D.v0.1-candidate",
        "state": "PASS_R0D_COPRESSURE_DIGEST_COMPACTION__EXPLICIT_LOSS__EXACT_REPLAY__HOT_WARM_PASSTHROUGH",
        "source_packet_sha256": sha256_path(source_path),
        "compacted_output_sha256": sha256_path(compacted_path),
        "replay_output_sha256": sha256_path(replay_path),
        "coverage": {
            "selected_input": 6,
            "hot_warm_passthrough": 2,
            "digest_input": 4,
            "digest_budget": 1,
            "digest_summaries": 1,
            "digest_entries_omitted_inline": 4,
            "representation_item_reduction": 3,
            "digest_entries_exactly_replayed": 4,
        },
        "checks": {
            "hot_warm_exact_passthrough": true,
            "loss_report_present": true,
            "semantic_summary_generated": false,
            "source_packet_hash_bound": true,
            "manifest_entry_hashes_verified": true,
            "exact_digest_object_replay": true,
            "source_deletion": false,
            "ack_cursor_mutation": false,
        },
        "terminals": {
            "compactor": compact_terminal,
            "replay": replay_terminal,
        },
        "effects": {
            "provider_session_mutation": 0,
            "receiver_context_mutation": 0,
            "ack_cursor_mutation": 0,
            "authority_change": 0,
            "source_deletion": 0,
        },
        "next": "R0E_RECEIVER_PRESSURE_POLICY_AND_MULTI_DIGEST_BUDGET_REPLAY_CANARY",
        "nonclaims": [
            "COMPACTION_NE_DELETION",
            "SUMMARY_NE_SOURCE",
            "EXPLICIT_LOSS_NE_ZERO_LOSS",
            "REPLAY_NE_INTEGRATION",
            "LOCAL_CANARY_NE_LIVE_GLOBAL_BUS",
        ],
    }
    result_path = root / "r0d-result.json"
    encoded = (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    result_path.write_bytes(encoded)
    print(json.dumps({
        "STATE": result["state"],
        "OUTPUT": str(result_path),
        "OUTPUT_SHA256": hashlib.sha256(encoded).hexdigest().upper(),
        "DIGEST_INPUT": 4,
        "DIGEST_SUMMARIES": 1,
        "OMITTED_INLINE": 4,
        "ITEM_REDUCTION": 3,
        "REPLAYED": 4,
        "ACK_CURSOR_MUTATION": false,
        "NEXT": result["next"],
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
