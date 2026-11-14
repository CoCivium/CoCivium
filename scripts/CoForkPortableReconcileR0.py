#!/usr/bin/env python3
"""Synthetic-only, no-network, nonauthoritative 3-way WorkID fork reconciliation.

This preserves exact input bytes and every branch snapshot. It never updates an
existing receiver, authenticates a user, or promotes a merge into accepted work.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
from pathlib import Path

SCHEMA = "CoAll.CoFork.PortableSyntheticInput.R0"
BUNDLE = "CoAll.CoFork.PortableMergeProposal.R0"
FIELDS = frozenset({"goal", "progress", "next_deed"})
STATES = frozenset({"PENDING", "HELD", "UNVERIFIED"})
MAX_BYTES = 65536


class Held(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise Held(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def decode_source(raw):
    require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES,
            "HELD_INPUT_SIZE_OR_TYPE")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise Held("HELD_INPUT_NOT_JSON") from exc
    require(type(value) is dict and
            set(value) == {"schema", "scope", "work_id", "common_base", "forks"},
            "HELD_INPUT_SCHEMA")
    require(value["schema"] == SCHEMA and value["scope"] == "PUBLIC_SYNTHETIC",
            "HELD_NOT_PUBLIC_SYNTHETIC")
    work = value["work_id"]
    require(type(work) is str and 1 <= len(work) <= 160 and
            all(c.isascii() and (c.isalnum() or c in "-_.:/") for c in work),
            "HELD_WORK_ID")
    base = value["common_base"]
    require(type(base) is dict and set(base) == FIELDS and
            all(type(v) is str and len(v) <= 4096 for v in base.values()),
            "HELD_BASE")
    forks = value["forks"]
    require(type(forks) is dict and len(forks) == 2, "HELD_FORK_COUNT")
    for name, fork in forks.items():
        require(type(name) is str and 1 <= len(name) <= 64 and
                all(c.isascii() and (c.isalnum() or c in "-_.") for c in name),
                "HELD_FORK_NAME")
        require(type(fork) is dict and set(fork) == {"snapshot", "reported_state"},
                "HELD_FORK_SCHEMA")
        require(type(fork["snapshot"]) is dict and set(fork["snapshot"]) == FIELDS and
                all(type(v) is str and len(v) <= 4096 for v in fork["snapshot"].values()),
                "HELD_FORK_SNAPSHOT")
        require(type(fork["reported_state"]) is str and
                fork["reported_state"] in STATES,
                "HELD_REPORTED_STATE")
    return value


def reconcile(raw):
    packet = decode_source(raw)
    names = sorted(packet["forks"])
    left = packet["forks"][names[0]]["snapshot"]
    right = packet["forks"][names[1]]["snapshot"]
    base = packet["common_base"]
    proposal = {}
    conflicts = {}
    for field in sorted(FIELDS):
        a, b, old = left[field], right[field], base[field]
        if a == b:
            proposal[field] = a
        elif a == old:
            proposal[field] = b
        elif b == old:
            proposal[field] = a
        else:
            conflicts[field] = {"ancestor": old, names[0]: a, names[1]: b}
    return {
        "schema": BUNDLE,
        "state": "CONFLICT_HELD" if conflicts else "MERGE_PROPOSAL_ONLY",
        "work_id": packet["work_id"],
        "source_sha256": sha(raw),
        "exact_source_b64": base64.b64encode(raw).decode("ascii"),
        "ancestor_sha256": sha(canonical(base)),
        "fork_sha256": {
            n: sha(canonical(packet["forks"][n])) for n in names
        },
        "fork_ids": names,
        "conflicts": conflicts,
        "proposed_snapshot": None if conflicts else proposal,
        "source_statuses_unverified": {
            n: packet["forks"][n]["reported_state"] for n in names
        },
        "receiver_ack": False,
        "authorized_merge": False,
        "source_history_deleted": False,
        "requires_independent_receiver": True,
        "nonclaims": [
            "Synthetic public fixture only; not a live ChatGPT transcript",
            "Preserved input bytes do not establish complete provider history",
            "A merge proposal is not an authenticated or accepted effect",
            "Cross-process readback is not an independent NAS failure domain",
        ],
    }


def verify_bundle(payload):
    require(type(payload) is dict and
            payload.get("schema") == BUNDLE and
            type(payload.get("exact_source_b64")) is str,
            "HELD_BUNDLE_SCHEMA")
    try:
        raw = base64.b64decode(payload["exact_source_b64"], validate=True)
    except (ValueError, Exception) as exc:
        # Keep both invalid bytes and invalid Base64 fail-closed.
        raise Held("HELD_BUNDLE_SOURCE_ENCODING") from exc
    require(sha(raw) == payload.get("source_sha256"),
            "HELD_SOURCE_HASH")
    expected = reconcile(raw)
    require(payload == expected, "HELD_BUNDLE_MANIFEST_TAMPER")
    return raw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify is not None:
        require(args.input is None and args.output is None, "HELD_ARGUMENTS")
        obj = json.loads(args.verify.read_text(encoding="utf-8"))
        raw = verify_bundle(obj)
        print(json.dumps({"state": obj["state"], "verified_source_sha256": sha(raw),
                          "branch_count": len(obj["fork_ids"]),
                          "receiver_ack": False}, sort_keys=True))
        return
    require(args.input is not None and args.output is not None, "HELD_ARGUMENTS")
    result = reconcile(args.input.read_bytes())
    # Exclusive creation: no overwriting old branch content or receipts.
    with args.output.open("xb") as fp:
        fp.write(canonical(result))
    print(json.dumps({"state": result["state"],
                      "source_sha256": result["source_sha256"],
                      "conflict_fields": sorted(result["conflicts"]),
                      "receiver_ack": False}, sort_keys=True))


if __name__ == "__main__":
    main()
