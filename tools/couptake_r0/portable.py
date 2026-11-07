#!/usr/bin/env python3
"""CoUptake R0.1 portable packet + local correction/recovery demonstration.

This is a reference integrity check, NOT a signed publisher identity,
a real independent receiver, consent, model training, revocation delivery
or cryptographically secure distribution mechanism. No automatic network,
model, external filesystem, authentication or existing-file overwrite.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

from uptake import (
    ALLOWED_EPISTEMIC, MAX_SOURCE_BYTES, AdmissionError,
    admit, git_blob_sha, load_manifest, safe_source_path
)

PACKET_SCHEMA = "CoAll.UptakeBridge.PortablePacket.R0.1-candidate"
POLICY_SCHEMA = "CoAll.UptakeBridge.ReceiverPin.R0.1-synthetic"
RECEIPT_SCHEMA = "CoAll.UptakeBridge.PortableReceipt.R0.1"
MAX_PACKET_BYTES = 3_000_000
MAX_OBJECTS = 4
ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")


def canonical_bytes(obj: dict) -> bytes:
    """Stable JSON encoding for candidate integrity (not author authentication)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def packet_digest(packet: dict) -> str:
    body = {k: v for k, v in packet.items() if k != "packet_sha256"}
    return sha256(canonical_bytes(body))


def source_name(name: str) -> str:
    """Enforce machine-readable public-source path spelling, no normalization tricks."""
    if not isinstance(name, str) or not name or "\\" in name:
        raise AdmissionError("INVALID_PACKET_SOURCE_PATH")
    segments = name.split("/")
    if any(s in ("", ".", "..") for s in segments):
        raise AdmissionError("INVALID_PACKET_SOURCE_PATH")
    pure = PurePosixPath(name)
    if pure.is_absolute() or segments[0] not in ("ai", "docs") or len(segments) < 2:
        raise AdmissionError("PACKET_PATH_OUTSIDE_PUBLIC_ONRAMP")
    if pure.suffix.lower() not in (".md", ".json", ".txt"):
        raise AdmissionError("UNSUPPORTED_PACKET_SOURCE_TYPE")
    return name


def build_packet(repo_root: Path, manifest: dict, selected: list[str]) -> dict:
    """Bind actual source bytes before packaging; no files written here."""
    if not selected or len(selected) > MAX_OBJECTS or len(selected) != len(set(selected)):
        raise AdmissionError("INVALID_SELECTIVE_PACKET_SIZE")
    receipt = admit(repo_root, manifest, selected)
    if receipt["held"]:
        raise AdmissionError("SOURCE_BIND_HELD_NO_EXPORT")
    lookup = {s["id"]: s for s in manifest["sources"]}
    objects = []
    for id_ in selected:
        item = lookup[id_]
        name = source_name(item["path"])
        raw = safe_source_path(repo_root, name).read_bytes()
        if len(raw) > MAX_SOURCE_BYTES or git_blob_sha(raw) != item["git_blob_sha"]:
            raise AdmissionError("SOURCE_DRIFT_DURING_PACK")
        objects.append({
            "id": id_, "path": name, "sha256": sha256(raw),
            "git_blob_sha": git_blob_sha(raw), "bytes": len(raw),
            "content_base64": base64.b64encode(raw).decode("ascii"),
            "visibility": item["visibility"], "epistemic": item["epistemic"],
            "instruction_authority": "NONE",
            "license_grant": "NOT_ESTABLISHED",
        })
    packet = {
        "schema": PACKET_SCHEMA, "state": "PUBLIC_SOURCE_LOCAL_PORTABLE_CANDIDATE",
        "sources": objects,
        "integrity": "SHA256_BYTES_PLUS_GIT_OBJECT_HASH_NOT_SIGNED_PUBLISHER",
        "source_instructions": "UNTRUSTED_DATA_NOT_TOOL_OR_SYSTEM_COMMANDS",
        "external_receiver_ack": "NOT_OBSERVED",
        "independent_replica": "NOT_OBSERVED",
        "memory_write": "NOT_PERFORMED",
        "model_weight_change": "NOT_PERFORMED",
        "created_by": "LOCAL_REFERENCE_TOOL_NOT_IDENTIFIED_EXTERNAL_PUBLISHER",
    }
    packet["packet_sha256"] = packet_digest(packet)
    if len(canonical_bytes(packet)) > MAX_PACKET_BYTES:
        raise AdmissionError("PACKET_TOO_LARGE")
    return packet


def validate_packet(packet: dict) -> list[dict]:
    if not isinstance(packet, dict) or packet.get("schema") != PACKET_SCHEMA:
        raise AdmissionError("UNRECOGNIZED_PACKET_SCHEMA")
    expected_packet_fields = {
        "schema", "state", "sources", "integrity", "source_instructions",
        "external_receiver_ack", "independent_replica", "memory_write",
        "model_weight_change", "created_by", "packet_sha256"
    }
    if set(packet) != expected_packet_fields:
        raise AdmissionError("UNKNOWN_PACKET_FIELDS_OR_MISSING_CEILING")
    ceilings = {
        "state": "PUBLIC_SOURCE_LOCAL_PORTABLE_CANDIDATE",
        "integrity": "SHA256_BYTES_PLUS_GIT_OBJECT_HASH_NOT_SIGNED_PUBLISHER",
        "external_receiver_ack": "NOT_OBSERVED",
        "independent_replica": "NOT_OBSERVED",
        "memory_write": "NOT_PERFORMED",
        "model_weight_change": "NOT_PERFORMED",
        "created_by": "LOCAL_REFERENCE_TOOL_NOT_IDENTIFIED_EXTERNAL_PUBLISHER"
    }
    if any(packet.get(k) != v for k, v in ceilings.items()):
        raise AdmissionError("FORBIDDEN_PACKET_EFFECT_OR_IDENTITY_CLAIM")
    if not isinstance(packet.get("sources"), list) or not 1 <= len(packet["sources"]) <= MAX_OBJECTS:
        raise AdmissionError("INVALID_PACKET_SOURCE_COUNT")
    if not isinstance(packet.get("packet_sha256"), str) or not SHA256_RE.fullmatch(packet["packet_sha256"]):
        raise AdmissionError("INVALID_PACKET_DIGEST")
    if packet_digest(packet) != packet["packet_sha256"]:
        raise AdmissionError("PACKET_DIGEST_MISMATCH")
    if packet.get("source_instructions") != "UNTRUSTED_DATA_NOT_TOOL_OR_SYSTEM_COMMANDS":
        raise AdmissionError("PACKET_AUTHORITY_CLAIM_INVALID")
    ids, paths = set(), set()
    result = []
    for item in packet["sources"]:
        if not isinstance(item, dict):
            raise AdmissionError("INVALID_PACKET_OBJECT")
        expected_source_fields = {
            "id", "path", "sha256", "git_blob_sha", "bytes", "content_base64",
            "visibility", "epistemic", "instruction_authority", "license_grant"
        }
        if set(item) != expected_source_fields:
            raise AdmissionError("UNKNOWN_SOURCE_FIELDS_OR_DIRECTIVE_INJECTION")
        id_ = item.get("id")
        if not isinstance(id_, str) or not ID_RE.fullmatch(id_):
            raise AdmissionError("INVALID_PACKET_OBJECT_ID")
        name = source_name(item.get("path"))
        if id_ in ids or name in paths:
            raise AdmissionError("DUPLICATE_PACKET_SOURCE")
        ids.add(id_)
        paths.add(name)
        if item.get("visibility") != "PUBLIC_SAFE" or item.get("epistemic") not in ALLOWED_EPISTEMIC:
            raise AdmissionError("NOT_PUBLIC_SAFE_OR_UNTYPED")
        if item.get("instruction_authority") != "NONE" or item.get("license_grant") != "NOT_ESTABLISHED":
            raise AdmissionError("PACKET_AUTHORITY_OR_LICENSE_CLAIM")
        if not isinstance(item.get("sha256"), str) or not SHA256_RE.fullmatch(item["sha256"]):
            raise AdmissionError("INVALID_OBJECT_SHA256")
        if not isinstance(item.get("git_blob_sha"), str) or not SHA1_RE.fullmatch(item["git_blob_sha"]):
            raise AdmissionError("INVALID_OBJECT_GIT_HASH")
        if not isinstance(item.get("bytes"), int) or not 0 <= item["bytes"] <= MAX_SOURCE_BYTES:
            raise AdmissionError("INVALID_OBJECT_SIZE")
        value = item.get("content_base64")
        if not isinstance(value, str) or len(value) > (MAX_SOURCE_BYTES * 4 // 3 + 16):
            raise AdmissionError("INVALID_BASE64_FIELD")
        try:
            raw = base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise AdmissionError("INVALID_BASE64_BYTES") from exc
        if len(raw) != item["bytes"] or sha256(raw) != item["sha256"] or git_blob_sha(raw) != item["git_blob_sha"]:
            raise AdmissionError("PACKET_SOURCE_BYTES_MISMATCH")
        result.append(item)
    return result


def test_only_receiver_pin(packet: dict, generation: int = 1) -> dict:
    """Synthetic receiver-held policy; MUST NOT be mistaken for signed authority."""
    objects = validate_packet(packet)
    if not isinstance(generation, int) or generation < 1:
        raise AdmissionError("INVALID_GENERATION")
    return {
        "schema": POLICY_SCHEMA, "generation": generation,
        "trust": "TEST_PIN_ONLY_NO_SIGNED_AUTHORITY",
        "source_pins": {obj["id"]: {
            "path": obj["path"], "sha256": obj["sha256"],
            "git_blob_sha": obj["git_blob_sha"],
            "revoked_sha256": []
        } for obj in objects},
        "status": "SYNTHETIC_RECEIVER_LOCAL_POLICY_NOT_DISTRIBUTED"
    }


def simulate_supersession(old_policy: dict, replacement_packet: dict) -> dict:
    """Synthetic test update only. No authority to distribute revocation to the world."""
    if not isinstance(old_policy, dict) or old_policy.get("schema") != POLICY_SCHEMA:
        raise AdmissionError("INVALID_PREVIOUS_POLICY")
    if old_policy.get("trust") != "TEST_PIN_ONLY_NO_SIGNED_AUTHORITY":
        raise AdmissionError("UNVERIFIED_POLICY_AUTHORITY")
    if not isinstance(old_policy.get("generation"), int) or old_policy["generation"] < 1:
        raise AdmissionError("INVALID_PREVIOUS_GENERATION")
    records = validate_packet(replacement_packet)
    revised = json.loads(json.dumps(old_policy))
    for obj in records:
        record = revised["source_pins"].get(obj["id"])
        if not isinstance(record, dict) or record.get("path") != obj["path"]:
            raise AdmissionError("SOURCE_SCOPE_CHANGED_WITHOUT_REVIEW")
        prior = record.get("sha256")
        if not isinstance(prior, str) or not SHA256_RE.fullmatch(prior):
            raise AdmissionError("INVALID_PREVIOUS_PIN")
        if prior != obj["sha256"] and prior not in record["revoked_sha256"]:
            record["revoked_sha256"].append(prior)
        record["sha256"] = obj["sha256"]
        record["git_blob_sha"] = obj["git_blob_sha"]
    revised["generation"] += 1
    revised["status"] = "SYNTHETIC_SUPERSESSION_FOR_TESTS_NEEDS_EXTERNAL_TRUST_DISTRIBUTION"
    return revised


def verify_against_receiver_pin(packet: dict, policy: dict, minimum_generation: int = 1) -> dict:
    """Compare to independent supplied expected pins, never trust a pin found inside packet."""
    receipt = {
        "schema": RECEIPT_SCHEMA, "effect_boundary": "HELD",
        "source_count": 0, "matched": 0, "held": 0, "checks": [],
        "external_receiver_ack": "NOT_OBSERVED",
        "independent_cold_restore": "NOT_OBSERVED",
        "persistent_memory_write": "NOT_PERFORMED",
        "model_weight_change": "NOT_PERFORMED",
        "issuer_signature_validated": False,
        "authority_granted": "NONE",
        "reason": ""
    }
    try:
        objects = validate_packet(packet)
        receipt["source_count"] = len(objects)
        if not isinstance(minimum_generation, int) or minimum_generation < 1:
            raise AdmissionError("INVALID_MINIMUM_GENERATION")
        if not isinstance(policy, dict) or policy.get("schema") != POLICY_SCHEMA:
            raise AdmissionError("MISSING_RECEIVER_POLICY")
        if policy.get("trust") != "TEST_PIN_ONLY_NO_SIGNED_AUTHORITY":
            raise AdmissionError("POLICY_TRUST_STATUS_UNSUPPORTED")
        epoch = policy.get("generation")
        if not isinstance(epoch, int) or epoch < minimum_generation:
            raise AdmissionError("POLICY_ROLLBACK_OR_STALE")
        pins = policy.get("source_pins")
        if not isinstance(pins, dict):
            raise AdmissionError("POLICY_PINS_MISSING")
        receipt["receiver_policy_generation"] = epoch
        for obj in objects:
            expected = pins.get(obj["id"])
            entry = {"id": obj["id"], "status": "HELD", "reason": ""}
            if not isinstance(expected, dict):
                entry["reason"] = "SOURCE_NOT_IN_RECEIVER_ALLOWLIST"
            elif expected.get("path") != obj["path"]:
                entry["reason"] = "SOURCE_PATH_NOT_APPROVED"
            elif obj["sha256"] in expected.get("revoked_sha256", []):
                entry["reason"] = "REVOKED_OR_SUPERSEDED_OBJECT"
            elif obj["sha256"] != expected.get("sha256") or obj["git_blob_sha"] != expected.get("git_blob_sha"):
                entry["reason"] = "NOT_CURRENT_IN_RECEIVER_POLICY"
            else:
                entry["status"] = "LOCAL_PACKET_PIN_MATCH"
                entry["reason"] = "LOCAL_INTEGRITY_AND_RECEIVER_PIN_ONLY_NOT_PUBLISHER_AUTHENTICATION"
            receipt["checks"].append(entry)
        receipt["matched"] = sum(x["status"] == "LOCAL_PACKET_PIN_MATCH" for x in receipt["checks"])
        receipt["held"] = receipt["source_count"] - receipt["matched"]
        receipt["effect_boundary"] = ("LOCAL_PACKET_PIN_MATCH_ONLY" if receipt["held"] == 0
                                      else "PARTIAL_OR_HELD_PACKET")
    except (AdmissionError, KeyError, TypeError, ValueError) as exc:
        receipt["reason"] = str(exc)
        receipt["held"] = receipt["source_count"] or 1
    return receipt


def bounded_json(path: Path, limit: int) -> dict:
    if not path.is_file() or path.stat().st_size > limit:
        raise AdmissionError("INPUT_MISSING_OR_OVERSIZED")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise AdmissionError("INVALID_JSON_INPUT") from exc
    if not isinstance(data, dict):
        raise AdmissionError("JSON_OBJECT_REQUIRED")
    return data


def exclusive_write(path: Path, obj: dict) -> None:
    """Refuse clobber; packages contain only source classified PUBLIC_SAFE."""
    data = json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if len(data.encode("utf-8")) > MAX_PACKET_BYTES:
        raise AdmissionError("OUTPUT_TOO_LARGE")
    try:
        with path.open("x", encoding="utf-8") as f:
            f.write(data)
    except FileExistsError as exc:
        raise AdmissionError("REFUSE_EXISTING_FILE") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build/verify local CoUptake packets with externally held synthetic trust pins")
    subs = parser.add_subparsers(dest="command", required=True)
    pack = subs.add_parser("pack")
    pack.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    pack.add_argument("--manifest", type=Path)
    pack.add_argument("--source-id", action="append", default=[])
    pack.add_argument("--output", type=Path, required=True)
    pin = subs.add_parser("pin-demo")
    pin.add_argument("--packet", type=Path, required=True)
    pin.add_argument("--generation", type=int, default=1)
    pin.add_argument("--output", type=Path, required=True)
    verify = subs.add_parser("verify")
    verify.add_argument("--packet", type=Path, required=True)
    verify.add_argument("--receiver-policy", type=Path, required=True)
    verify.add_argument("--minimum-generation", type=int, default=1)
    args = parser.parse_args(argv)
    try:
        if args.command == "pack":
            root = args.repo_root.resolve()
            manifest = load_manifest(args.manifest or root / "ai/uptake/couptake-manifest-r0.json")
            value = build_packet(root, manifest, args.source_id or ["ai_ia_onramp"])
            exclusive_write(args.output, value)
            print(json.dumps({"effect_boundary": "PUBLIC_PACKET_WRITTEN_LOCAL_ONLY",
                "packet_sha256": value["packet_sha256"], "sources": len(value["sources"]),
                "external_receiver_ack": "NOT_OBSERVED", "memory_write": "NOT_PERFORMED"}, sort_keys=True))
            return 0
        if args.command == "pin-demo":
            value = test_only_receiver_pin(bounded_json(args.packet, MAX_PACKET_BYTES), args.generation)
            exclusive_write(args.output, value)
            print(json.dumps({"effect_boundary": "LOCAL_SYNTHETIC_PIN_WRITTEN_NO_AUTHENTICATION",
                "generation": value["generation"], "external_ack": "NOT_OBSERVED"}, sort_keys=True))
            return 0
        packet = bounded_json(args.packet, MAX_PACKET_BYTES)
        policy = bounded_json(args.receiver_policy, 128_000)
        result = verify_against_receiver_pin(packet, policy, args.minimum_generation)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["effect_boundary"] == "LOCAL_PACKET_PIN_MATCH_ONLY" else 2
    except (AdmissionError, OSError) as exc:
        print(json.dumps({"effect_boundary": "HELD", "reason": str(exc),
                          "authority_granted": "NONE", "external_receiver_ack": "NOT_OBSERVED"}, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
