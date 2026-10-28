#!/usr/bin/env python3
"""CoAll coordination fan-out R0.

Deterministic, repo-local synthetic proof for GitHub issue #317.
No network, credential, account, device, or external-message effects.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Any

ZERO_EFFECTS = {
    "network_calls": 0,
    "external_messages": 0,
    "credential_access": 0,
    "account_changes": 0,
    "device_mutations": 0,
    "external_publications": 0,
}


def stable_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def sha256(value: Any) -> str:
    return hashlib.sha256(stable_bytes(value)).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def load_packet(packet_path: Path) -> tuple[dict[str, Any], Path, dict[str, Any]]:
    packet = read_json(packet_path)
    require(packet.get("schema") == "CoAll.CanonicalTaskPacket.R0.v0.1", "wrong packet schema")
    require(packet.get("task_id"), "task_id required")
    require(packet.get("source", {}).get("pointer"), "source pointer required")
    require(packet.get("source", {}).get("version"), "source version required")
    require(len(packet.get("destinations", [])) == 2, "exactly two canary destinations required")

    runtime_rel = Path(packet["runtime_relpath"])
    require(not runtime_rel.is_absolute(), "runtime path must be repo-relative")
    require(runtime_rel.parts and runtime_rel.parts[0] == ".coall-runtime", "runtime must stay under .coall-runtime")
    runtime = Path.cwd() / runtime_rel

    inv_path = Path(packet["receiver_inventory"])
    inventory = read_json(inv_path)
    require(
        inventory.get("schema") == "CoAll.CoordinationReceiverInventory.R0.v0.1",
        "wrong inventory schema",
    )

    by_id = {d["destination_id"]: d for d in inventory["destinations"]}
    for destination_id in packet["destinations"]:
        require(destination_id in by_id, f"missing destination {destination_id}")
        d = by_id[destination_id]
        require(d["availability"] == "AVAILABLE_AND_VERIFIED", f"{destination_id} not verified")
        require(d["authority"] == "AUTHORIZED_FOR_SYNTHETIC_TEST_ONLY", f"{destination_id} authority mismatch")
        require(d["external_effects"] is False, f"{destination_id} must be local-only")

    return packet, runtime, inventory


def ledger_path(runtime: Path) -> Path:
    return runtime / "receipts" / "ledger.jsonl"


def lock_path(runtime: Path) -> Path:
    return runtime / "supervisor.lock"


def stop_path(runtime: Path) -> Path:
    return runtime / "STOP.json"


@contextmanager
def exclusive_runtime_lock(runtime: Path):
    path = lock_path(runtime)
    try:
        path.mkdir()
    except FileExistsError as exc:
        raise RuntimeError(f"runtime lock already held: {path}") from exc
    try:
        yield
    finally:
        path.rmdir()


def stop_state(runtime: Path, packet: dict[str, Any]) -> dict[str, Any] | None:
    path = stop_path(runtime)
    if not path.exists():
        return None
    marker = read_json(path)
    require(marker.get("schema") == "CoAll.CoordinationStop.R0.v0.1", "wrong STOP schema")
    require(marker.get("task_id") == packet["task_id"], "STOP task identity mismatch")
    require(marker.get("packet_sha256") == sha256(packet), "STOP packet digest mismatch")
    return marker


def write_stop(runtime: Path, packet: dict[str, Any], reason: str) -> dict[str, Any]:
    marker = {
        "schema": "CoAll.CoordinationStop.R0.v0.1",
        "task_id": packet["task_id"],
        "packet_sha256": sha256(packet),
        "reason": reason,
        "effects": dict(ZERO_EFFECTS),
    }
    path = stop_path(runtime)
    if path.exists():
        existing = read_json(path)
        require(existing == marker, "conflicting STOP marker")
        return existing
    write_json(path, marker)
    return marker


def clear_stop(runtime: Path, packet: dict[str, Any]) -> dict[str, Any]:
    marker = stop_state(runtime, packet)
    if marker is None:
        return {"state": "STOP_ALREADY_CLEAR", "effects": dict(ZERO_EFFECTS)}
    stop_path(runtime).unlink()
    return {"state": "STOP_CLEARED", "reason": marker["reason"], "effects": dict(ZERO_EFFECTS)}


def read_ledger(runtime: Path) -> list[dict[str, Any]]:
    path = ledger_path(runtime)
    if not path.exists():
        return []
    rows = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        obj = json.loads(line)
        require(obj.get("receipt_id"), f"ledger line {lineno}: receipt_id missing")
        probe = dict(obj)
        rid = probe.pop("receipt_id")
        require(rid == sha256(probe), f"ledger line {lineno}: receipt hash mismatch")
        rows.append(obj)
    return rows


def append_receipt(
    runtime: Path,
    packet: dict[str, Any],
    *,
    kind: str,
    destination_id: str | None = None,
    attempt: int | None = None,
    result: str,
    detail: str,
) -> dict[str, Any]:
    rows = read_ledger(runtime)
    event: dict[str, Any] = {
        "schema": "CoAll.CoordinationReceipt.R0.v0.1",
        "logical_seq": len(rows) + 1,
        "task_id": packet["task_id"],
        "packet_sha256": sha256(packet),
        "source_pointer": packet["source"]["pointer"],
        "source_version": packet["source"]["version"],
        "kind": kind,
        "destination_id": destination_id,
        "attempt": attempt,
        "result": result,
        "detail": detail,
        "effects": dict(ZERO_EFFECTS),
    }
    event["receipt_id"] = sha256(event)
    path = ledger_path(runtime)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
    return event


def summarize_destination(
    runtime: Path, packet: dict[str, Any], destination_id: str
) -> dict[str, Any]:
    rows = [
        r for r in read_ledger(runtime)
        if r.get("destination_id") == destination_id
    ]
    attempts = [r for r in rows if r["kind"] == "DISPATCH_ATTEMPT"]
    failures = [r for r in rows if r["kind"] == "DISPATCH_FAILURE"]
    acks = [r for r in rows if r["kind"] == "DESTINATION_ACK"]
    skips = [r for r in rows if r["kind"] == "RECOVERY_SKIP_ALREADY_ACKED"]

    payload_path = runtime / "destinations" / destination_id / f"{packet['task_id']}.json"
    payload_exists = payload_path.exists()
    payload_sha = None
    if payload_exists:
        payload = read_json(payload_path)
        payload_sha = sha256(payload)
        require(payload["task_id"] == packet["task_id"], "destination task identity mismatch")
        require(payload["packet_sha256"] == sha256(packet), "destination packet digest mismatch")

    if acks:
        state = "ACKED"
    elif payload_exists and attempts:
        state = "DELIVERED_UNACKED_RECOVERABLE"
    elif failures:
        state = "RETRY_QUEUED"
    else:
        state = "QUEUED"

    return {
        "destination_id": destination_id,
        "state": state,
        "attempt_count": len(attempts),
        "failure_count": len(failures),
        "ack_count": len(acks),
        "recovery_skip_count": len(skips),
        "payload_exists": payload_exists,
        "payload_sha256": payload_sha,
        "latest_ack_receipt_id": acks[-1]["receipt_id"] if acks else None,
        "latest_failure_receipt_id": failures[-1]["receipt_id"] if failures else None,
    }


def init_runtime(packet_path: Path, reset: bool) -> dict[str, Any]:
    packet, runtime, inventory = load_packet(packet_path)
    if reset and runtime.exists():
        shutil.rmtree(runtime)
    require(not runtime.exists() or not read_ledger(runtime), "runtime already contains receipts; use --reset only for bounded test reset")
    runtime.mkdir(parents=True, exist_ok=True)

    meta = {
        "schema": "CoAll.CoordinationRuntime.R0.v0.1",
        "task_id": packet["task_id"],
        "packet_sha256": sha256(packet),
        "source_pointer": packet["source"]["pointer"],
        "source_version": packet["source"]["version"],
        "receiver_inventory_sha256": sha256(inventory),
        "receipt_ledger": str(ledger_path(runtime).relative_to(Path.cwd())).replace("\\", "/"),
    }
    write_json(runtime / "meta.json", meta)

    for destination_id in packet["destinations"]:
        append_receipt(
            runtime,
            packet,
            kind="QUEUE_CREATED",
            destination_id=destination_id,
            result="QUEUED",
            detail="Synthetic destination queued from canonical task packet.",
        )

    return {
        "state": "INITIALIZED",
        "task_id": packet["task_id"],
        "runtime": str(runtime.relative_to(Path.cwd())).replace("\\", "/"),
        "packet_sha256": sha256(packet),
        "destinations": packet["destinations"],
        "effects": dict(ZERO_EFFECTS),
    }


def deliver(
    runtime: Path,
    packet: dict[str, Any],
    inventory: dict[str, Any],
    destination_id: str,
    *,
    recovery: bool,
) -> dict[str, Any]:
    summary = summarize_destination(runtime, packet, destination_id)
    if summary["state"] == "ACKED":
        if recovery:
            receipt = append_receipt(
                runtime,
                packet,
                kind="RECOVERY_SKIP_ALREADY_ACKED",
                destination_id=destination_id,
                result="NOOP",
                detail="Completed destination preserved; dispatch not duplicated.",
            )
            return {"destination_id": destination_id, "result": "SKIPPED_ALREADY_ACKED", "receipt_id": receipt["receipt_id"]}
        return {"destination_id": destination_id, "result": "ALREADY_ACKED"}

    attempt = summary["attempt_count"] + 1
    attempt_receipt = append_receipt(
        runtime,
        packet,
        kind="DISPATCH_ATTEMPT",
        destination_id=destination_id,
        attempt=attempt,
        result="ATTEMPTED",
        detail="Synthetic local dispatch attempt.",
    )

    by_id = {d["destination_id"]: d for d in inventory["destinations"]}
    behavior = by_id[destination_id]["behavior"]

    if behavior == "FAIL_FIRST_THEN_ACK" and attempt == 1:
        failure = append_receipt(
            runtime,
            packet,
            kind="DISPATCH_FAILURE",
            destination_id=destination_id,
            attempt=attempt,
            result="SIMULATED_FAILURE",
            detail="Intentional first-attempt failure; item remains recoverable and queued.",
        )
        return {
            "destination_id": destination_id,
            "result": "SIMULATED_FAILURE",
            "attempt_receipt_id": attempt_receipt["receipt_id"],
            "failure_receipt_id": failure["receipt_id"],
        }

    projection = {
        "schema": "CoAll.SyntheticDestinationProjection.R0.v0.1",
        "task_id": packet["task_id"],
        "packet_sha256": sha256(packet),
        "source": packet["source"],
        "destination_id": destination_id,
        "payload": packet["payload"],
        "authority": "SYNTHETIC_LOCAL_TEST_ONLY",
    }
    path = runtime / "destinations" / destination_id / f"{packet['task_id']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        existing = read_json(path)
        require(existing == projection, f"{destination_id}: conflicting existing projection")
    else:
        write_json(path, projection)

    if behavior == "CRASH_AFTER_WRITE_THEN_ACK" and attempt == 1:
        raise RuntimeError("SIMULATED_CRASH_AFTER_PROJECTION_BEFORE_ACK")

    ack = append_receipt(
        runtime,
        packet,
        kind="DESTINATION_ACK",
        destination_id=destination_id,
        attempt=attempt,
        result="ACKED_LOCAL_PROJECTION",
        detail="Exact synthetic projection materialized and read back locally.",
    )
    return {
        "destination_id": destination_id,
        "result": "ACKED_LOCAL_PROJECTION",
        "attempt_receipt_id": attempt_receipt["receipt_id"],
        "ack_receipt_id": ack["receipt_id"],
        "projection_sha256": sha256(projection),
    }


def dispatch(packet_path: Path) -> dict[str, Any]:
    packet, runtime, inventory = load_packet(packet_path)
    require(runtime.exists(), "runtime not initialized")
    with exclusive_runtime_lock(runtime):
        stopped = stop_state(runtime, packet)
        if stopped is not None:
            return {
                "state": "STOPPED_NO_DISPATCH",
                "task_id": packet["task_id"],
                "stop_reason": stopped["reason"],
                "results": [],
                "effects": dict(ZERO_EFFECTS),
            }
        results = [
            deliver(runtime, packet, inventory, d, recovery=False)
            for d in packet["destinations"]
        ]
    return {
        "state": "DISPATCH_CYCLE_COMPLETE",
        "task_id": packet["task_id"],
        "results": results,
        "effects": dict(ZERO_EFFECTS),
    }


def reconcile(packet_path: Path) -> dict[str, Any]:
    packet, runtime, _ = load_packet(packet_path)
    require(runtime.exists(), "runtime not initialized")
    destinations = [
        summarize_destination(runtime, packet, d)
        for d in packet["destinations"]
    ]
    acked = sum(1 for d in destinations if d["state"] == "ACKED")
    retry = sum(1 for d in destinations if d["state"] == "RETRY_QUEUED")
    unacked = sum(1 for d in destinations if d["state"] == "DELIVERED_UNACKED_RECOVERABLE")
    if acked == len(destinations):
        overall = "COMPLETE_ACKED_LOCAL"
    elif acked > 0 and (retry > 0 or unacked > 0):
        overall = "PARTIAL_RECOVERABLE"
    else:
        overall = "INCOMPLETE"

    ledger = read_ledger(runtime)
    require(all(r["task_id"] == packet["task_id"] for r in ledger), "mixed task ids in ledger")
    require(all(all(v == 0 for v in r["effects"].values()) for r in ledger), "nonzero effect in ledger")

    return {
        "schema": "CoAll.CoordinationStatusView.R0.v0.1",
        "task_id": packet["task_id"],
        "source": packet["source"],
        "packet_sha256": sha256(packet),
        "overall_state": overall,
        "destinations": destinations,
        "receipt_count": len(ledger),
        "effects": dict(ZERO_EFFECTS),
        "uncertainty": [
            "LOCAL_ACK_NE_EXTERNAL_RECEIVER_EFFECT",
            "SYNTHETIC_RECOVERY_NE_GLOBAL_SYNC",
        ],
    }


def recover(packet_path: Path) -> dict[str, Any]:
    packet, runtime, inventory = load_packet(packet_path)
    require(runtime.exists(), "runtime not initialized")
    with exclusive_runtime_lock(runtime):
        stopped = stop_state(runtime, packet)
        if stopped is not None:
            return {
                "schema": "CoAll.FreshProcessRecoveryReport.R0.v0.1",
                "task_id": packet["task_id"],
                "recovered_from_task_packet_and_receipts": True,
                "before_state": reconcile(packet_path)["overall_state"],
                "results": [],
                "after_state": "STOPPED_NO_RECOVERY",
                "stop_reason": stopped["reason"],
                "effects": dict(ZERO_EFFECTS),
            }
        before = reconcile(packet_path)
        start = append_receipt(
            runtime,
            packet,
            kind="RECOVERY_START",
            result="RECONSTRUCTED_FROM_PACKET_AND_RECEIPTS",
            detail="Fresh process derived runtime path from task packet and reconstructed destination states from receipt ledger.",
        )
        results = [
            deliver(runtime, packet, inventory, d, recovery=True)
            for d in packet["destinations"]
        ]
        after = reconcile(packet_path)
        complete = append_receipt(
            runtime,
            packet,
            kind="RECOVERY_COMPLETE",
            result=after["overall_state"],
            detail="Recovery cycle completed without redispatching already-acked destinations.",
        )
    return {
        "schema": "CoAll.FreshProcessRecoveryReport.R0.v0.1",
        "task_id": packet["task_id"],
        "recovered_from_task_packet_and_receipts": True,
        "source_pointer_used": packet["source"]["pointer"],
        "before_state": before["overall_state"],
        "results": results,
        "after_state": after["overall_state"],
        "recovery_start_receipt_id": start["receipt_id"],
        "recovery_complete_receipt_id": complete["receipt_id"],
        "effects": dict(ZERO_EFFECTS),
    }


def verify(packet_path: Path) -> dict[str, Any]:
    packet, runtime, _ = load_packet(packet_path)
    status = reconcile(packet_path)
    by_id = {d["destination_id"]: d for d in status["destinations"]}
    a = by_id["synthetic-local-a"]
    b = by_id["synthetic-local-b"]
    rows = read_ledger(runtime)
    recovery = [r for r in rows if r["kind"] == "RECOVERY_START"]

    checks = {
        "two_destinations_acked": a["state"] == "ACKED" and b["state"] == "ACKED",
        "destination_a_single_dispatch": a["attempt_count"] == 1 and a["ack_count"] == 1,
        "destination_a_not_duplicated_on_recovery": a["recovery_skip_count"] == 1,
        "destination_b_failed_then_acked": b["attempt_count"] == 2 and b["failure_count"] == 1 and b["ack_count"] == 1,
        "same_canonical_task_id": all(r["task_id"] == packet["task_id"] for r in rows),
        "fresh_process_recovery_receipted": len(recovery) == 1 and recovery[0]["result"] == "RECONSTRUCTED_FROM_PACKET_AND_RECEIPTS",
        "zero_external_effects": all(all(v == 0 for v in r["effects"].values()) for r in rows),
        "final_state_complete": status["overall_state"] == "COMPLETE_ACKED_LOCAL",
    }
    require(all(checks.values()), f"acceptance failure: {checks}")

    return {
        "schema": "CoAll.CoordinationAcceptanceReport.R0.v0.1",
        "state": "PASS_SYNTHETIC_TWO_DESTINATION_FANOUT_AND_RECOVERY",
        "task_id": packet["task_id"],
        "checks": checks,
        "final_status": status,
        "nonclaims": [
            "SYNTHETIC_LOCAL_ACK_NE_EXTERNAL_DELIVERY",
            "LOCAL_PROJECTION_NE_RECEIVER_USE",
            "FRESH_PROCESS_NE_DIFFERENT_MACHINE",
            "RECOVERY_PASS_NE_GLOBAL_SYNC",
            "NO_BACKGROUND_EXECUTION_PROVED",
            "NO_EXTERNAL_OUTREACH_PERFORMED",
            "NO_DEVICE_INTEGRATION_PROVED",
        ],
    }


def stop(packet_path: Path, reason: str) -> dict[str, Any]:
    packet, runtime, _ = load_packet(packet_path)
    require(runtime.exists(), "runtime not initialized")
    with exclusive_runtime_lock(runtime):
        marker = write_stop(runtime, packet, reason)
    return {
        "state": "STOP_ACTIVE",
        "task_id": packet["task_id"],
        "reason": marker["reason"],
        "effects": dict(ZERO_EFFECTS),
    }


def resume(packet_path: Path) -> dict[str, Any]:
    packet, runtime, _ = load_packet(packet_path)
    require(runtime.exists(), "runtime not initialized")
    with exclusive_runtime_lock(runtime):
        result = clear_stop(runtime, packet)
    return {
        "task_id": packet["task_id"],
        **result,
    }


def emit(value: Any, output: Path | None) -> None:
    text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["init", "dispatch", "reconcile", "recover", "verify", "stop", "resume"])
    p.add_argument("--packet", type=Path, required=True)
    p.add_argument("--output", type=Path)
    p.add_argument("--reset", action="store_true")
    p.add_argument("--reason", default="OPERATOR_STOP")
    args = p.parse_args()

    if args.command == "init":
        result = init_runtime(args.packet, args.reset)
    elif args.command == "dispatch":
        result = dispatch(args.packet)
    elif args.command == "reconcile":
        result = reconcile(args.packet)
    elif args.command == "recover":
        result = recover(args.packet)
    elif args.command == "verify":
        result = verify(args.packet)
    elif args.command == "stop":
        result = stop(args.packet, args.reason)
    else:
        result = resume(args.packet)

    emit(result, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
