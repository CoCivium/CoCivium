#!/usr/bin/env python3
"""Synthetic-only, fail-closed CoOwnedWork browser-record -> existing SQLite receiver.

This adapter does not authenticate real consent, transport browser storage,
authorize an external effect, or claim a production receiver.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from CoNarrativeWorkIDR0 import (
    SCHEMA as RECEIVER_SCHEMA, Held, canonical, commit_once, digest,
    readback, revoke, validate,
)

BROWSER_SCHEMA = "CoAll.CoOwnedWork.BrowserLocal.R0"
PINNED_COMMIT = "63b41ead8797e5a781699f32bcbc77b78bdbd7af"
PINNED_SHA256 = "58f8c722bfbfc34cac41189c072d2effe4b19dbbe8a37be4f8687344d6b00b9a"
JS_DONOR_SHA256 = "2cf5cc23af395c731d1ccbc71fa61e4befb146ad8a5bea74e0642111f57c0f48"
RECEIVER_SHA256 = "4929bfd7c131733729547213eab668bdbb62644e159acad6a26a910141dcb39f"
WORK_ID = "CoPre.ReadyCycle.Synthetic.R0"
SOURCE_REF = "CoCivium/CoCivium:CoPre.md@" + PINNED_COMMIT
PACKET_FIELDS = frozenset({
    "schema", "work_id", "source_ref", "source_sha256", "narrative_summary",
    "prior_decisions", "open_blockers", "next_safe_deed", "privacy",
    "consent", "lease_epoch",
})
RECORD_FIELDS = frozenset({
    "schema", "packet", "state", "commit_sequence",
    "receiver_ack", "source_verified_by_browser",
})
GATE_FIELDS = frozenset({
    "schema", "fixture_id", "actor", "work_id", "source_commit",
    "source_sha256", "consent_epoch", "scope", "permission",
})
GATE_SCHEMA = "CoAll.CoOwnedWork.CISyntheticGate.R0"
FIXTURE_ID = "CoPreOwnedWork.synthetic.20261110"
ACTOR = "GITHUB_CI_SYNTHETIC_FIXTURE_NOT_REAL_PERMISSION"
PERMISSION = "ONE_EPHEMERAL_SQLITE_SYNTHETIC_WRITE"


def require(test, code):
    if not test:
        raise Held(code)


def checked_file(path, expected_name, max_bytes=131072):
    path = Path(path)
    require(path.name == expected_name and path.is_file() and
            not path.is_symlink(), "HELD_WRONG_OR_UNSAFE_FILE")
    data = path.read_bytes()
    require(0 < len(data) <= max_bytes, "HELD_INVALID_FILE_SIZE")
    return data


def source_check(source_path):
    raw = checked_file(source_path, "CoPre.md")
    require(hashlib.sha256(raw).hexdigest() == PINNED_SHA256,
            "HELD_PINNED_SOURCE_MISMATCH")
    return PINNED_SHA256


def dependency_check(js_path, receiver_path=None):
    """Bind the adapter to the exact reviewed donor and receiver bytes."""
    js_raw = checked_file(js_path, "CoOwnedWorkR0.js")
    require(hashlib.sha256(js_raw).hexdigest() == JS_DONOR_SHA256,
            "HELD_JS_DONOR_MISMATCH")
    receiver = (Path(receiver_path) if receiver_path is not None else
                Path(__file__).with_name("CoNarrativeWorkIDR0.py"))
    receiver_raw = checked_file(receiver, "CoNarrativeWorkIDR0.py")
    require(hashlib.sha256(receiver_raw).hexdigest() == RECEIVER_SHA256,
            "HELD_SQLITE_RECEIVER_MISMATCH")
    return {
        "js_donor_sha256": JS_DONOR_SHA256,
        "sqlite_receiver_sha256": RECEIVER_SHA256,
    }


def node_fixture(js_path):
    path = Path(js_path)
    dependency_check(path)
    # Source JS fixture is a co-located reviewed donor, not an external user.
    script = "process.stdout.write(JSON.stringify(require(process.argv[1]).fixture()))"
    proc = subprocess.run(["node", "-e", script, str(path.resolve())],
                          text=True, capture_output=True, timeout=10, check=False)
    require(proc.returncode == 0 and len(proc.stdout) <= 8192,
            "HELD_JS_FIXTURE_UNAVAILABLE")
    return json.loads(proc.stdout)


def adapt(record, gate, source_path, js_path):
    require(type(record) is dict and set(record) == RECORD_FIELDS,
            "HELD_BROWSER_RECORD_SCHEMA")
    require(record["schema"] == BROWSER_SCHEMA + ".Record"
            and record["state"] == "ACTIVE" and
            type(record["commit_sequence"]) is int and
            record["commit_sequence"] == 1 and
            record["receiver_ack"] is False and
            record["source_verified_by_browser"] is False,
            "HELD_BROWSER_RECORD_NOT_SYNTHETIC_ACTIVE")
    p = record["packet"]
    require(type(p) is dict and set(p) == PACKET_FIELDS,
            "HELD_BROWSER_PACKET_SCHEMA")
    require(p["schema"] == BROWSER_SCHEMA + ".Packet" and
            p["work_id"] == WORK_ID and p["source_ref"] == SOURCE_REF and
            p["source_sha256"] == PINNED_SHA256 and
            p["privacy"] == "PUBLIC_SYNTHETIC" and
            p["consent"] == "SYNTHETIC_TEST_ONLY" and
            type(p["lease_epoch"]) is int and p["lease_epoch"] == 1,
            "HELD_BROWSER_PACKET_INELIGIBLE")
    require(p == node_fixture(js_path), "HELD_BROWSER_FIXTURE_DIVERGED")
    require(type(gate) is dict and set(gate) == GATE_FIELDS,
            "HELD_EXPLICIT_GATE_MISSING")
    require(gate["schema"] == GATE_SCHEMA and
            gate["fixture_id"] == FIXTURE_ID and gate["actor"] == ACTOR and
            gate["work_id"] == WORK_ID and
            gate["source_commit"] == PINNED_COMMIT and
            gate["source_sha256"] == PINNED_SHA256 and
            type(gate["consent_epoch"]) is int and gate["consent_epoch"] == 1 and
            gate["scope"] == "PUBLIC_SYNTHETIC" and
            gate["permission"] == PERMISSION,
            "HELD_UNAUTHORIZED_OR_STALE_SYNTHETIC_GATE")
    source_check(source_path)
    # Explicitly reconcile the missing consent_epoch: only a provided,
    # separately labeled synthetic gate can supply it. Do NOT rewrite text.
    packet = {**p, "schema": RECEIVER_SCHEMA,
              "consent_epoch": gate["consent_epoch"]}
    require({k: packet[k] for k in (
        "narrative_summary", "prior_decisions", "open_blockers",
        "next_safe_deed")} == {k: p[k] for k in (
        "narrative_summary", "prior_decisions", "open_blockers",
        "next_safe_deed")}, "HELD_NARRATIVE_MUTATION")
    validate(packet)
    return packet



def apply_browser_revocation(db_path, active_record, revoked_record,
                             gate, source_path, js_path):
    """Synthetic cross-job revocation of the exact browser-origin WorkID.

    Validates record identity and epoch before touching SQLite. Caller-supplied
    browser JSON is not cryptographically authenticated human authorization.
    """
    packet = adapt(active_record, gate, source_path, js_path)
    require(type(revoked_record) is dict and
            set(revoked_record) == RECORD_FIELDS,
            "HELD_REVOKE_RECORD_SCHEMA")
    require(revoked_record == {**active_record, "state": "REVOKED"},
            "HELD_REVOKE_NOT_SAME_BROWSER_RECORD")
    # The destination must already contain precisely this unrevised WorkID.
    original = readback(db_path, expected_packet=packet,
                        source_path=source_path)
    require(original["state"] == "COLD_SOURCE_RECONSTRUCTED"
            and original["committed_work_ids"] == 1
            and original["external_receiver_ack"] is False,
            "HELD_RECEIVER_NOT_ACTIVE_FOR_REVOKE")
    revoke(db_path, packet, expected_lease=packet["lease_epoch"])
    observed = readback(db_path, expected_packet=packet,
                        source_path=source_path)
    require(observed["state"] == "HELD_REVOKED"
            and observed["next_safe_deed"] is None
            and observed["external_receiver_ack"] is False,
            "HELD_REVOCATION_NOT_APPLIED")
    return {
        "schema": "CoAll.CoOwnedWork.BrowserRevokeToSqliteR0",
        "state": "SYNTHETIC_BROWSER_ORIGIN_REVOCATION_APPLIED_CI_ONLY",
        "work_id": WORK_ID, "source_sha256": PINNED_SHA256,
        "active_browser_record_sha256": digest(active_record),
        "revoked_browser_record_sha256": digest(revoked_record),
        "sqlite_packet_sha256": digest(packet),
        "consent_epoch": packet["consent_epoch"],
        "before": original["state"], "after": observed["state"],
        "receiver_ack": False, "real_human_consent": False,
        "independent_sender_authentication": False,
        "cross_provider_delivery": False, "external_effects": 0,
        "nonclaims": [
            "CI_SIMULATED_UI_REVOCATION_NOT_REAL_HUMAN_CONSENT",
            "SOURCE_ORIGIN_BYTES_NOT_AUTHENTICATED_SIGNED_EVENT",
            "SAME_GITHUB_FAILURE_DOMAIN",
            "EPHEMERAL_SQLITE_NOT_PRODUCTION_RECEIVER",
            "NO_24H_SURVIVAL", "NOT_CANON", "NOT_COEX"
        ]
    }


def run(record_path, gate_path, source_path, js_path, output_dir):
    record = json.loads(checked_file(record_path, "browser-record.json", 8192))
    gate = json.loads(checked_file(gate_path, "ownedwork_synthetic_gate_r0.json", 8192))
    packet = adapt(record, gate, source_path, js_path)
    dependencies = dependency_check(js_path)
    out = Path(output_dir)
    require(not out.exists(), "HELD_OUTPUT_EXISTS_NO_CLOBBER")
    out.mkdir(parents=True)
    db = out / "receiver.sqlite"
    first = commit_once(db, packet)
    second = commit_once(db, packet)
    require(first["new_commits"] == 1 and second["new_commits"] == 0
            and second["duplicate"] and not first["receipt"]["receiver_ack"],
            "HELD_DUPLICATE_OR_ACK")
    cold = readback(db, expected_packet=packet, source_path=source_path)
    require(cold["state"] == "COLD_SOURCE_RECONSTRUCTED" and
            cold["committed_work_ids"] == 1 and
            cold["external_receiver_ack"] is False,
            "HELD_LOCAL_RECEIVER_READBACK")
    obj = {
        "schema": "CoAll.CoOwnedWork.SqliteBridgeProof.R0",
        "state": "SYNTHETIC_CROSS_JOB_LOCAL_SQLITE_HANDOFF_VERIFIED",
        "work_id": WORK_ID, "source_ref": SOURCE_REF,
        "source_sha256": PINNED_SHA256,
        "browser_record_sha256": digest(record),
        "explicit_gate_sha256": digest(gate),
        "translated_packet_sha256": digest(packet),
        "dependency_sha256": dependencies,
        "narrative_fields_preserved": True,
        "consent_epoch_origin": "EXPLICIT_CI_SYNTHETIC_GATE_NOT_BROWSER",
        "local_commits": 1, "duplicate_suppressed": 1,
        "receiver_readback": cold,
        "receiver_ack": False, "real_human_consent": False,
        "external_effects": 0, "live_browser_transport": False,
        "independent_provider": False, "runtime_24h": False,
        "nonclaims": ["NODE_BROWSER_FIXTURE_NOT_USER_GESTURE",
                      "CI_FIXTURE_IS_NOT_AUTHENTICATED_PERMISSION",
                      "LOCAL_SQLITE_IS_NOT_INTENDED_COALL_RECEIVER",
                      "GITHUB_CI_IS_ONE_FAILURE_DOMAIN",
                      "NOT_COEX", "NOT_CANON", "NO_24H_PROOF"],
    }
    (out / "translated-packet.json").write_text(
        json.dumps(packet, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    (out / "receiver-observation.json").write_text(
        json.dumps(obj, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(canonical({"state": obj["state"], "work_id": WORK_ID,
                     "source_sha256": PINNED_SHA256, "new_commits": 1,
                     "duplicates_suppressed": 1, "receiver_ack": False}))
    return obj


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--record", required=True)
    p.add_argument("--gate", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--js", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    try:
        run(a.record, a.gate, a.source, a.js, a.output)
    except (Held, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(canonical({"state": "HELD", "reason": str(exc),
                         "external_effects": 0, "receiver_ack": False}))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
