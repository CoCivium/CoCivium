#!/usr/bin/env python3
"""CoAll Golden Braid R0: bounded local fanout with explicit receiver receipts.

Python standard library only. NEVER contacts a network, provider or user.
Only `alpha` and `beta` under a supplied local root are permitted destinations.
The journal is a hash-linked integrity trace, NOT a signature or trusted timestamp.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timezone

RECEIVERS = ("alpha", "beta")
GENESIS = "0" * 64
SCHEMA = "CoAllTaskPacket/R0"
JOURNAL_SCHEMA = "CoAllBraidEvent/R0"


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "xb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())


def atomic_replace(path, data):
    # For a test-only destination. An operator-controlled root is assumed.
    tmp = path.with_name(path.name + ".new")
    with open(tmp, "xb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def check_packet(packet):
    if packet.get("schema") != SCHEMA or not packet.get("task_id") or not packet.get("owner"):
        raise ValueError("INVALID_TASK_PACKET")
    scope = packet.get("scope", {})
    if (scope.get("classification") != "SYNTHETIC_PUBLIC_TEST_ONLY"
        or scope.get("permission") != "LOCAL_FILE_RECEIVERS_ONLY"
        or scope.get("external_effects_authorized") is not False
        or scope.get("authorized_receivers") != list(RECEIVERS)):
        raise ValueError("AUTHORITY_REJECTED")
    for key in ("source", "intent", "next_action", "acceptance_criteria", "created_utc", "status"):
        if not packet.get(key):
            raise ValueError("MISSING_" + key.upper())
    if packet["status"] != "SYNTHETIC_TEST_PACKET":
        raise ValueError("NOT_SYNTHETIC_TEST")
    for insight in packet.get("insights", []):
        if insight.get("epistemic_state") not in ("PROPOSAL_NOT_VALIDATED", "HYPOTHESIS", "OBSERVATION"):
            raise ValueError("INSIGHT_STATE_NOT_ALLOWED")
        if not insight.get("source_ref") or not insight.get("next_test"):
            raise ValueError("INSIGHT_WITHOUT_PROVENANCE_OR_TEST")
    return packet


def load_packet(root, expected_task_sha=None):
    ptr = json.loads((root / "pointer.json").read_text(encoding="utf-8"))
    if ptr.get("task_file") != "task.json" or ptr.get("receivers") != list(RECEIVERS):
        raise ValueError("INVALID_POINTER")
    raw = (root / "task.json").read_bytes()
    got = digest(raw)
    if got != ptr.get("task_sha256") or (expected_task_sha and got != expected_task_sha):
        raise ValueError("TASK_BYTES_CHANGED")
    task = check_packet(json.loads(raw))
    return task, got


def append_event(root, event, destination=None, detail=None):
    history, prior = read_journal(root)
    seq = len(history) + 1
    packet, _ = load_packet(root)
    entry = {
        "schema": JOURNAL_SCHEMA,
        "seq": seq,
        "at": now(),
        "task_id": packet["task_id"],
        "kind": event,
        "destination": destination,
        "detail": detail or {},
        "prev_hash": prior,
    }
    entry["hash"] = digest(canonical(entry))
    with open(root / "events.jsonl", "ab") as fh:
        fh.write(canonical(entry))
        fh.flush()
        os.fsync(fh.fileno())
    return entry


def read_journal(root, expected_head=None):
    lines = (root / "events.jsonl").read_bytes().splitlines()
    prev = GENESIS
    entries = []
    for idx, line in enumerate(lines, 1):
        def no_duplicates(pairs):
            d = {}
            for k, v in pairs:
                if k in d:
                    raise ValueError("DUPLICATE_JSON_KEY")
                d[k] = v
            return d
        e = json.loads(line, object_pairs_hook=no_duplicates)
        if e.get("schema") != JOURNAL_SCHEMA or e.get("seq") != idx or e.get("prev_hash") != prev:
            raise ValueError("BROKEN_EVENT_CHAIN")
        if e.get("destination") not in (*RECEIVERS, None):
            raise ValueError("UNKNOWN_RECEIVER_IN_JOURNAL")
        h = e.get("hash")
        if not isinstance(h, str) or h != digest(canonical({k: v for k, v in e.items() if k != "hash"})):
            raise ValueError("HASH_MISMATCH")
        entries.append(e)
        prev = h
    if expected_head and expected_head != prev:
        raise ValueError("HEAD_MISMATCH")
    return entries, prev


def init(root, fixture):
    if root.exists() and any(root.iterdir()):
        raise ValueError("NONEMPTY_ROOT_REFUSES_CLOBBER")
    raw = Path(fixture).read_bytes()
    check_packet(json.loads(raw))
    root.mkdir(parents=True, exist_ok=True)
    write_new(root / "task.json", raw)
    write_new(root / "pointer.json", canonical({"task_file": "task.json", "task_sha256": digest(raw), "receivers": list(RECEIVERS), "source_kind": "LOCAL_PINNED_SNAPSHOT"}))
    write_new(root / "events.jsonl", b"")
    e = append_event(root, "INTAKE", detail={"task_sha256": digest(raw), "source_type": "SYNTHETIC_LOCAL_FIXTURE"})
    return {"task_sha256": digest(raw), "head": e["hash"]}


@contextmanager
def supervisor_lock(root):
    """Fail closed on a competing or orphaned dispatcher. No automatic lock stealing."""
    lock = root / "DISPATCH_LOCK"
    stamp = canonical({"pid": os.getpid(), "at": now()})
    try:
        write_new(lock, stamp)
    except FileExistsError as exc:
        raise ValueError("DISPATCH_LOCK_HELD_REQUIRES_OWNER_REVIEW") from exc
    try:
        yield
    finally:
        if lock.is_file() and lock.read_bytes() == stamp:
            lock.unlink()


def verify_receiver(root, destination, packet, task_sha):
    if destination not in RECEIVERS:
        raise ValueError("INVALID_RECEIVER")
    base = root / "receivers" / destination
    delivery_path = base / "delivery.json"
    ack_path = base / "ack.json"
    if ack_path.is_file() and not delivery_path.is_file():
        raise ValueError("ACK_WITHOUT_DELIVERY")
    if not delivery_path.is_file() or not ack_path.is_file():
        return None
    dbytes = delivery_path.read_bytes()
    ack = json.loads(ack_path.read_bytes())
    delivery = json.loads(dbytes)
    if (ack.get("schema") != "CoAllReceiverAck/R0" or ack.get("receiver") != destination
        or ack.get("task_id") != packet["task_id"] or ack.get("task_sha256") != task_sha
        or ack.get("delivery_sha256") != digest(dbytes)
        or delivery.get("receiver") != destination or delivery.get("task_id") != packet["task_id"]
        or delivery.get("task_sha256") != task_sha or delivery.get("epistemic_state") != "PROPOSAL_NOT_VALIDATED"):
        raise ValueError("RECEIVER_READBACK_MISMATCH")
    return {"ack_sha256": digest(ack_path.read_bytes()), "delivery_sha256": digest(dbytes), "receiver": destination}


def worker(root, destination, fail_once=False, fail_after_delivery=False):
    task, task_sha = load_packet(root)
    if destination not in task["scope"]["authorized_receivers"]:
        raise ValueError("RECEIVER_UNAUTHORIZED")
    if (root / "STOP").exists():
        raise ValueError("REVOKED_STOP")
    already = verify_receiver(root, destination, task, task_sha)
    if already:
        print(json.dumps({"state": "ALREADY_DELIVERED", **already}))
        return 0
    base = root / "receivers" / destination
    base.mkdir(parents=True, exist_ok=True)
    if fail_once and destination == "beta" and not (base / "FAULT_INJECTED").exists():
        write_new(base / "FAULT_INJECTED", b"BETA_FIRST_ATTEMPT_FAULT\n")
        print(json.dumps({"state": "FAULT_INJECTED", "receiver": destination}))
        return 17
    payload = canonical({"schema": "CoAllLocalDelivery/R0", "receiver": destination,
      "task_id": task["task_id"], "task_sha256": task_sha, "insight_ids": [i["id"] for i in task["insights"]],
      "epistemic_state": "PROPOSAL_NOT_VALIDATED", "authority": "SYNTHETIC_LOCAL_ONLY"})
    if (base / "delivery.json").exists():
        if (base / "delivery.json").read_bytes() != payload:
            raise ValueError("PARTIAL_DELIVERY_DIVERGENCE")
    else:
        write_new(base / "delivery.json", payload)
    observed = (base / "delivery.json").read_bytes()
    if observed != payload:
        raise ValueError("DESTINATION_READBACK_FAILED")
    if fail_after_delivery and destination == "beta" and not (base / "FAULT_AFTER_DELIVERY").exists():
        write_new(base / "FAULT_AFTER_DELIVERY", b"NO_ACK_AFTER_DELIVERY\n")
        print(json.dumps({"state": "FAULT_AFTER_DELIVERY", "receiver": destination}))
        return 19
    if (root / "STOP").exists():
        raise ValueError("REVOKED_STOP")
    ack = canonical({"schema": "CoAllReceiverAck/R0", "receiver": destination,
      "task_id": task["task_id"], "task_sha256": task_sha, "delivery_sha256": digest(observed),
      "receiver_pid": os.getpid(), "receiver_observed_at": now(), "effect_class": "LOCAL_SYNTHETIC_FILE"})
    write_new(base / "ack.json", ack)
    proof = verify_receiver(root, destination, task, task_sha)
    print(json.dumps({"state": "DELIVERED", **proof}))
    return 0


def dispatch(root, fail_once_beta=False, skip_ack_log_for=None, fail_after_delivery_beta=False):
    with supervisor_lock(root):
        return _dispatch_unlocked(root, fail_once_beta, skip_ack_log_for, fail_after_delivery_beta)


def _dispatch_unlocked(root, fail_once_beta=False, skip_ack_log_for=None, fail_after_delivery_beta=False):
    task, task_sha = load_packet(root)
    events, _ = read_journal(root)
    if (root / "STOP").exists() or any(e["kind"] == "STOP" for e in events):
        raise ValueError("REVOKED_STOP")
    outcomes = {}
    for dest in RECEIVERS:
        history, _ = read_journal(root)
        proof = verify_receiver(root, dest, task, task_sha)
        recorded = any(e["kind"] in ("ACK_VERIFIED", "ACK_RECOVERED") and e["destination"] == dest for e in history)
        if proof and recorded:
            append_event(root, "SKIP_COMPLETED", dest, {"idempotent": True})
            outcomes[dest] = "SKIP_COMPLETED"
            continue
        if proof and not recorded:
            append_event(root, "ACK_RECOVERED", dest, proof)
            outcomes[dest] = "ACK_RECOVERED_NO_REDUPLICATION"
            continue
        if recorded and not proof:
            raise ValueError("RECORDED_ACK_WITHOUT_RECEIVER_PROOF")
        append_event(root, "ATTEMPT", dest, {"route": "LOCAL_SUBPROCESS", "external_effect": False})
        cmd = [sys.executable, str(Path(__file__).resolve()), "worker", "--root", str(root), "--destination", dest]
        if fail_once_beta:
            cmd.append("--fail-once-beta")
        if fail_after_delivery_beta:
            cmd.append("--fail-after-delivery")
        finished = subprocess.run(cmd, text=True, capture_output=True, timeout=15, check=False)
        if finished.returncode:
            append_event(root, "ATTEMPT_FAILED", dest, {"exit_code": finished.returncode, "retryable": True,
                                                          "error_class": "SYNTHETIC_INJECTED_FAULT" if finished.returncode == 17 else "WORKER_ERROR"})
            outcomes[dest] = "FAILED_PENDING_RETRY"
            continue
        proof = verify_receiver(root, dest, task, task_sha)
        if not proof:
            raise ValueError("WORKER_NO_READBACK")
        if skip_ack_log_for == dest:
            outcomes[dest] = "ACK_FILE_EXISTS_BUT_NOT_RECORDED"
            continue
        append_event(root, "ACK_VERIFIED", dest, proof)
        outcomes[dest] = "VERIFIED_LOCAL_RECEIVER"
    return outcomes


def reconcile(root, expected_task_sha=None, expected_head=None):
    packet, sha = load_packet(root, expected_task_sha)
    events, head = read_journal(root, expected_head)
    if not events or events[0]["kind"] != "INTAKE" or events[0]["detail"].get("task_sha256") != sha:
        raise ValueError("MISSING_OR_BAD_INTAKE")
    for e in events:
        if e["task_id"] != packet["task_id"]:
            raise ValueError("WRONG_TASK_ID_IN_LEDGER")
    status = {}
    for d in RECEIVERS:
        completed = [e for e in events if e["kind"] in ("ACK_VERIFIED", "ACK_RECOVERED") and e["destination"] == d]
        proof = verify_receiver(root, d, packet, sha)
        if completed and not proof:
            raise ValueError("DURABLE_ACK_PROOF_LOST")
        if completed:
            if completed[-1]["detail"] != proof:
                raise ValueError("ACK_LEDGER_DIVERGENCE")
            status[d] = "ACK_VERIFIED_LOCAL"
        elif proof:
            status[d] = "ACK_EXISTS_PENDING_LEDGER_RECOVERY"
        elif any(e["kind"] == "ATTEMPT_FAILED" and e["destination"] == d for e in events):
            status[d] = "FAILED_QUEUED"
        else:
            status[d] = "PENDING"
    stopped = (root / "STOP").exists() or any(e["kind"] == "STOP" for e in events)
    return {"schema": "CoAllReconciliation/R0", "task_id": packet["task_id"], "task_sha256": sha,
            "journal_head": head, "events": len(events), "destinations": status,
            "all_local_acked": all(x == "ACK_VERIFIED_LOCAL" for x in status.values()),
            "revoked": stopped, "external_delivery_or_adoption": "NOT_TESTED",
            "insight_states": [i["epistemic_state"] for i in packet["insights"]],
            "limits": ["LOCAL_TWO_RECEIVERS_ONLY", "NOT_TWO_INDEPENDENT_PROVIDER_FAILURE_DOMAINS", "HASH_CHAIN_NOT_SIGNATURE"]}


def stop(root):
    load_packet(root)
    if not (root / "STOP").exists():
        write_new(root / "STOP", canonical({"state": "REVOKED", "at": now()}))
        append_event(root, "STOP", detail={"reason": "EXPLICIT_LOCAL_REVOCATION"})
    return "STOPPED"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("init", "worker", "dispatch", "reconcile", "stop"):
        p = sub.add_parser(name)
        p.add_argument("--root", required=True, type=Path)
        if name == "init":
            p.add_argument("--fixture", type=Path, default=Path(__file__).with_name("fixture") / "task_packet.json")
        if name == "worker":
            p.add_argument("--destination", choices=RECEIVERS, required=True)
            p.add_argument("--fail-once-beta", action="store_true")
            p.add_argument("--fail-after-delivery", action="store_true")
        if name == "dispatch":
            p.add_argument("--fail-once-beta", action="store_true")
            p.add_argument("--fail-after-delivery-beta", action="store_true")
            p.add_argument("--skip-ack-log-for", choices=RECEIVERS)
        if name == "reconcile":
            p.add_argument("--expect-task-sha")
            p.add_argument("--expect-head")
    args = parser.parse_args(argv)
    try:
        if args.action == "init":
            out = init(args.root, args.fixture)
        elif args.action == "worker":
            return worker(args.root, args.destination, args.fail_once_beta, args.fail_after_delivery)
        elif args.action == "dispatch":
            out = dispatch(args.root, args.fail_once_beta, args.skip_ack_log_for, args.fail_after_delivery_beta)
        elif args.action == "reconcile":
            out = reconcile(args.root, args.expect_task_sha, args.expect_head)
        else:
            out = stop(args.root)
        print(json.dumps(out, sort_keys=True, indent=2))
        return 0
    except (ValueError, OSError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "FAIL_CLOSED", "error": str(exc)}), file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
