#!/usr/bin/env python3
"""CoPre/CoStatusOffload -> pinned existing CoUptake receiver, synthetic only.

No additional receiver engine. Donor source is extracted from an exact Git
commit, its Git object hash is pinned, and only fixture-safe data is packaged.
CI-created receiver pins are explicitly NOT independently trusted.
"""
from __future__ import annotations
import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import CoStatusOffloadR0 as offload

DONOR_COMMIT = "248d3f3bc4836bb2b42378152f087221494cf0bc"
DONOR_PATH = "tools/couptake_r0/receiver_standalone.py"
DONOR_BLOB = "a3bbf5bf6b8ed9c1b54858346f67e8460ee958a5"
PACKET_SCHEMA = "CoAll.UptakeBridge.PortablePacket.R0.1-candidate"
PIN_SCHEMA = "CoAll.UptakeBridge.ReceiverPin.R0.1-synthetic"
SOURCE_PATH = "ai/uptake/copre_checkpoint_synthetic_r0.json"
SOURCE_ID = "copre_checkpoint"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def obtain_receiver(repo):
    args = ["git", "-C", str(repo), "show", DONOR_COMMIT + ":" + DONOR_PATH]
    raw = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         timeout=12, check=True).stdout
    if blob(raw) != DONOR_BLOB:
        raise ValueError("DONOR_BLOB_DRIFT")
    return raw


def packet_from_source(raw):
    source = {
        "id": SOURCE_ID, "path": SOURCE_PATH, "sha256": sha(raw),
        "git_blob_sha": blob(raw), "bytes": len(raw),
        "content_base64": base64.b64encode(raw).decode("ascii"),
        "visibility": "PUBLIC_SAFE",
        "epistemic": "PUBLIC_ARCHITECTURE_CANDIDATE",
        "instruction_authority": "NONE",
        "license_grant": "NOT_ESTABLISHED",
    }
    packet = {
        "schema": PACKET_SCHEMA, "state": "PUBLIC_SOURCE_LOCAL_PORTABLE_CANDIDATE",
        "sources": [source],
        "integrity": "SHA256_BYTES_PLUS_GIT_OBJECT_HASH_NOT_SIGNED_PUBLISHER",
        "source_instructions": "UNTRUSTED_DATA_NOT_TOOL_OR_SYSTEM_COMMANDS",
        "external_receiver_ack": "NOT_OBSERVED",
        "independent_replica": "NOT_OBSERVED",
        "memory_write": "NOT_PERFORMED",
        "model_weight_change": "NOT_PERFORMED",
        "created_by": "LOCAL_REFERENCE_TOOL_NOT_IDENTIFIED_EXTERNAL_PUBLISHER",
    }
    packet["packet_sha256"] = sha(canonical(packet))
    return packet


def synthetic_pin(packet):
    obj = packet["sources"][0]
    return {
        "schema": PIN_SCHEMA, "generation": 1,
        "trust": "TEST_PIN_ONLY_NO_SIGNED_AUTHORITY",
        "source_pins": {SOURCE_ID: {
            "path": SOURCE_PATH, "sha256": obj["sha256"],
            "git_blob_sha": obj["git_blob_sha"], "revoked_sha256": [],
        }},
        "status": "SYNTHETIC_RECEIVER_LOCAL_POLICY_NOT_DISTRIBUTED",
    }


def new_process_receiver(receiver_bytes, packet, pin, minimum_generation=1):
    with tempfile.TemporaryDirectory(prefix="copre-uptake-synthetic-") as d:
        directory = Path(d)
        executable = directory / "standalone_receiver.py"
        executable.write_bytes(receiver_bytes)
        (directory / "packet.json").write_bytes(canonical(packet))
        (directory / "pin.json").write_bytes(canonical(pin))
        assert set(p.name for p in directory.iterdir()) == {
            "standalone_receiver.py", "packet.json", "pin.json"
        }
        env = dict(os.environ)
        env["PYTHONPATH"] = "/missing/intentionally-disabled"
        proc = subprocess.run([
            sys.executable, "-I", "-S", str(executable),
            "--packet", str(directory / "packet.json"),
            "--receiver-pin", str(directory / "pin.json"),
            "--minimum-generation", str(minimum_generation),
        ], cwd=directory, env=env, capture_output=True,
           text=True, check=False, timeout=12)
        if proc.stderr.strip():
            raise RuntimeError("STANDALONE_RECEIVER_STDERR: " + proc.stderr[:500])
        value = json.loads(proc.stdout)
        return proc.returncode, value


def semantic_check_after_pin(packet, receipt, expected_work_id, expected_source_revision):
    # Source pin checking must finish before inner semantic validation.
    if receipt.get("effect_boundary") != "LOCAL_PIN_MATCH_ONLY":
        return "HELD_OUTER_SOURCE_PIN"
    raw = base64.b64decode(packet["sources"][0]["content_base64"], validate=True)
    try:
        checkpoint = json.loads(raw)
    except (ValueError, UnicodeError):
        return "HELD_INNER_CHECKPOINT"
    if offload.check_checkpoint(checkpoint) != "EXACT_STRUCTURAL_READBACK_ONLY":
        return "HELD_INNER_CHECKPOINT"
    if checkpoint["work_id"] != expected_work_id:
        return "HELD_WORK_ID_SUBSTITUTION"
    if checkpoint["source_revision"] != expected_source_revision:
        return "HELD_STALE_WORK_SOURCE"
    if checkpoint["authority"] != "READ_ONLY" or checkpoint["confidentiality"] != "PUBLIC":
        return "HELD_INNER_AUTHORITY"
    if not checkpoint.get("stop_condition") or not checkpoint.get("next_wake"):
        return "HELD_MISSING_NEXT_STOP"
    return "LOCAL_SOURCE_AND_WORK_CONTRACT_MATCH_ONLY"


def selftest(repo):
    receiver = obtain_receiver(repo)
    checkpoint = offload.make_initial(
        "CoPre.Offshore.20261109", "fixture:public-allowed",
        "synthetic-source-revision-1")
    checkpoint["sections"] = {
        "next": {"deed": "compare exact-pin cold restore against WorkID-only"},
        "recovery": {"pointer": "synthetic://source-pointer"},
    }
    checkpoint["checkpoint_sha256"] = offload.sha256(
        {k: checkpoint[k] for k in offload.FIELDS})
    assert offload.check_checkpoint(checkpoint) == "EXACT_STRUCTURAL_READBACK_ONLY"
    original = packet_from_source(canonical(checkpoint))
    policy = synthetic_pin(original)
    count = 0

    def case(packet, pin, expected_effect, expected_semantic, generation=1):
        nonlocal count
        code, receipt = new_process_receiver(receiver, packet, pin, generation)
        assert receipt.get("effect_boundary") == expected_effect, (receipt, expected_effect)
        assert (code == 0) == (expected_effect == "LOCAL_PIN_MATCH_ONLY")
        semantic = semantic_check_after_pin(
            packet, receipt, checkpoint["work_id"], checkpoint["source_revision"])
        assert semantic == expected_semantic, (semantic, expected_semantic)
        assert receipt["external_agent_ack"] == "NOT_OBSERVED"
        assert receipt["authority_granted"] == "NONE"
        assert receipt["off_provider_cold_restore"] == "NOT_OBSERVED"
        count += 1

    case(original, policy, "LOCAL_PIN_MATCH_ONLY",
         "LOCAL_SOURCE_AND_WORK_CONTRACT_MATCH_ONLY")
    case(original, policy, "HELD", "HELD_OUTER_SOURCE_PIN", generation=2)
    altered = copy.deepcopy(original)
    altered["sources"][0]["content_base64"] = base64.b64encode(b"spoof").decode()
    case(altered, policy, "HELD", "HELD_OUTER_SOURCE_PIN")
    altered = copy.deepcopy(original)
    altered["external_receiver_ack"] = "VERIFIED"
    case(altered, policy, "HELD", "HELD_OUTER_SOURCE_PIN")
    bad_pin = copy.deepcopy(policy)
    bad_pin["source_pins"][SOURCE_ID]["sha256"] = "0" * 64
    case(original, bad_pin, "PARTIAL_OR_HELD", "HELD_OUTER_SOURCE_PIN")
    wrong_source = copy.deepcopy(checkpoint)
    wrong_source["source_revision"] = "synthetic-older"
    wrong_source["checkpoint_sha256"] = offload.sha256(
        {k: wrong_source[k] for k in offload.FIELDS})
    wrong_packet = packet_from_source(canonical(wrong_source))
    case(wrong_packet, synthetic_pin(wrong_packet), "LOCAL_PIN_MATCH_ONLY",
         "HELD_STALE_WORK_SOURCE")
    false_authority = copy.deepcopy(checkpoint)
    false_authority["authority"] = "EXECUTE"
    false_authority["checkpoint_sha256"] = offload.sha256(
        {k: false_authority[k] for k in offload.FIELDS})
    fake_packet = packet_from_source(canonical(false_authority))
    case(fake_packet, synthetic_pin(fake_packet), "LOCAL_PIN_MATCH_ONLY",
         "HELD_INNER_CHECKPOINT")
    missing_stop = copy.deepcopy(checkpoint)
    missing_stop["stop_condition"] = ""
    missing_stop["checkpoint_sha256"] = offload.sha256(
        {k: missing_stop[k] for k in offload.FIELDS})
    broken = packet_from_source(canonical(missing_stop))
    case(broken, synthetic_pin(broken), "LOCAL_PIN_MATCH_ONLY",
         "HELD_INNER_CHECKPOINT")
    replaced_id = copy.deepcopy(checkpoint)
    replaced_id["work_id"] = "CoPre.Other.Work"
    replaced_id["checkpoint_sha256"] = offload.sha256(
        {k: replaced_id[k] for k in offload.FIELDS})
    replace_packet = packet_from_source(canonical(replaced_id))
    case(replace_packet, synthetic_pin(replace_packet), "LOCAL_PIN_MATCH_ONLY",
         "HELD_WORK_ID_SUBSTITUTION")
    assert count == 9
    return {
        "schema": "CoCivium.CoPreUptakeBridgeSynthetic.R0",
        "tests_passed": count, "tests_run": count,
        "donor_commit": DONOR_COMMIT, "donor_blob": DONOR_BLOB,
        "source_checkpoint_sha256": checkpoint["checkpoint_sha256"],
        "source_packet_sha256": original["packet_sha256"],
        "effect": "LOCAL_SOURCE_AND_WORK_CONTRACT_MATCH_ONLY",
        "real_independent_receiver": "UNPROVEN",
        "remote_storage": "NOT_TESTED",
        "authority": "NONE", "effects_performed": 0,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--repo-root", default=".")
    opts = parser.parse_args()
    if not opts.selftest:
        parser.error("only --selftest is supported")
    print(json.dumps(selftest(Path(opts.repo_root).resolve()), sort_keys=True))
