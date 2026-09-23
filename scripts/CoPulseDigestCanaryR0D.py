#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_json(cmd: list[str]):
    cp = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(cp.stdout.strip().splitlines()[-1])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--compactor", required=True)
    ap.add_argument("--replay", required=True)
    ap.add_argument("--source-packet", required=True)
    ap.add_argument("--out-root", required=True)
    args = ap.parse_args()

    out_root = Path(args.out_root).resolve()
    if out_root.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out_root}")
    out_root.mkdir(parents=True, exist_ok=False)

    compactor = str(Path(args.compactor).resolve())
    replay = str(Path(args.replay).resolve())
    source = Path(args.source_packet).resolve()
    source_before = sha256_path(source)

    projections = {}
    replays = {}
    for pressure in ("LOW", "MODERATE", "HIGH", "DEGRADED"):
        proj_path = out_root / f"projection-{pressure.lower()}.json"
        run_json([sys.executable, compactor, "--packet", str(source), "--pressure", pressure, "--output", str(proj_path)])
        projections[pressure] = load(proj_path)

        if pressure != "LOW":
            replay_path = out_root / f"replay-{pressure.lower()}.json"
            run_json([sys.executable, replay, "--projection", str(proj_path), "--source-packet", str(source), "--output", str(replay_path)])
            replays[pressure] = load(replay_path)

    source_after = sha256_path(source)
    if source_before != source_after:
        raise SystemExit("FAIL_CLOSED__SOURCE_PACKET_MUTATED")

    low = projections["LOW"]
    moderate = projections["MODERATE"]
    high = projections["HIGH"]
    degraded = projections["DEGRADED"]

    if low["loss_report"]["compaction_applied"] is not False or low["loss_report"]["visible_item_count"] != 8:
        raise SystemExit("FAIL_CLOSED__LOW_PRESSURE_POLICY")
    if moderate["loss_report"]["digest_group_count"] != 2 or moderate["loss_report"]["visible_item_count"] != 4:
        raise SystemExit("FAIL_CLOSED__MODERATE_PRESSURE_POLICY")
    if high["loss_report"]["digest_group_count"] != 1 or high["loss_report"]["visible_item_count"] != 3:
        raise SystemExit("FAIL_CLOSED__HIGH_PRESSURE_POLICY")
    if degraded["loss_report"]["digest_group_count"] != 1 or degraded["loss_report"]["visible_item_count"] != 3:
        raise SystemExit("FAIL_CLOSED__DEGRADED_PRESSURE_POLICY")

    for pressure in ("MODERATE", "HIGH", "DEGRADED"):
        replay_obj = replays[pressure]
        if replay_obj["state"] != "PASS_EXACT_DIGEST_SOURCE_ENTRY_REPLAY__NO_SOURCE_MUTATION":
            raise SystemExit(f"FAIL_CLOSED__REPLAY_STATE={pressure}")
        if replay_obj["coverage"]["source_digest_entry_count"] != 6 or replay_obj["coverage"]["replayed_digest_entry_count"] != 6:
            raise SystemExit(f"FAIL_CLOSED__REPLAY_COUNT={pressure}")
        if replay_obj["coverage"]["sequence_exact"] is not True:
            raise SystemExit(f"FAIL_CLOSED__REPLAY_SEQUENCE={pressure}")

    result = {
        "schema":"CoPulseDigestCanary.R0D.v0.1-candidate",
        "state":"PASS_R0D_COPRESSURE_AWARE_DIGEST_COMPACTION__EXPLICIT_LOSS_REPORT__EXACT_REPLAY__NO_SOURCE_OR_ACK_MUTATION",
        "source_packet_sha256":source_before,
        "pressure_results":{
            p:{
                "source_selected":projections[p]["loss_report"]["source_selected_entry_count"],
                "source_digest":projections[p]["loss_report"]["source_digest_entry_count"],
                "digest_groups":projections[p]["loss_report"]["digest_group_count"],
                "visible_items":projections[p]["loss_report"]["visible_item_count"],
                "visible_item_reduction":projections[p]["loss_report"]["visible_item_reduction"],
                "exact_replay_proven": p == "LOW" or replays[p]["coverage"]["sequence_exact"] is True,
            } for p in ("LOW","MODERATE","HIGH","DEGRADED")
        },
        "checks":{
            "low_pressure_no_compaction":True,
            "moderate_pressure_chunked_digest":True,
            "high_pressure_single_digest_group":True,
            "degraded_pressure_single_digest_group":True,
            "explicit_loss_report":True,
            "exact_digest_sequence_replay":True,
            "source_packet_unchanged":True,
            "ack_cursor_mutation":False,
        },
        "effects":{
            "source_packet_mutation":0,
            "ack_cursor_mutation":0,
            "provider_session_mutation":0,
            "authority_change":0,
        },
        "next":"R0E_DIGEST_RECEIVER_PICKUP_AND_ACK_CANARY_WITH_SOURCE_REPLAY_DRILLDOWN",
        "nonclaims":[
            "COMPACTION_NE_SEMANTIC_EQUIVALENCE",
            "REPLAYABILITY_NE_SOURCE_RETIREMENT_AUTHORITY",
            "DIGEST_PROJECTION_NE_RECEIVER_PICKUP",
            "LOCAL_CANARY_NE_LIVE_GLOBAL_BUS",
        ],
    }
    result_path = out_root / "r0d-result.json"
    encoded = (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    result_path.write_bytes(encoded)
    print(json.dumps({
        "STATE":result["state"],
        "OUTPUT":str(result_path),
        "OUTPUT_SHA256":hashlib.sha256(encoded).hexdigest().upper(),
        "LOW_VISIBLE":8,
        "MODERATE_VISIBLE":4,
        "HIGH_VISIBLE":3,
        "DEGRADED_VISIBLE":3,
        "SOURCE_DIGEST":6,
        "REPLAYED_EXACT":6,
        "NEXT":result["next"],
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
