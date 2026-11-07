#!/usr/bin/env python3
"""Standalone CoUptake R0.2 packet verifier.

An intentionally self-contained verifier for a *synthetic receiver-held pin*.
It reads ONLY two local JSON files, uses Python's standard library, and has
no repository, network, AI model, publisher account or signing dependency.
PASS means local integrity + match to the supplied pin, NOT authentic
publisher identity, independent operator, external memory or global correction.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import re
import sys
from pathlib import Path

PACKET_SCHEMA = "CoAll.UptakeBridge.PortablePacket.R0.1-candidate"
PIN_SCHEMA = "CoAll.UptakeBridge.ReceiverPin.R0.1-synthetic"
RESULT_SCHEMA = "CoAll.UptakeBridge.IsolatedReceiverReceipt.R0.2"
MAX_PACKET = 3_000_000
MAX_PIN = 128_000
MAX_SOURCE = 512_000
MAX_OBJECTS = 4
SHA1 = re.compile(r"^[a-f0-9]{40}$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")
NAME = re.compile(r"^[a-z][a-z0-9_]*$")
ALLOWED_EPISTEMIC = frozenset((
    "PUBLIC_POLICY", "PUBLIC_SOURCE_CONTRACT", "PUBLIC_BOOTSTRAP",
    "PUBLIC_ARCHITECTURE_CANDIDATE"
))
PACKET_FIELDS = {
    "schema", "state", "sources", "integrity", "source_instructions",
    "external_receiver_ack", "independent_replica", "memory_write",
    "model_weight_change", "created_by", "packet_sha256"
}
SOURCE_FIELDS = {
    "id", "path", "sha256", "git_blob_sha", "bytes",
    "content_base64", "visibility", "epistemic",
    "instruction_authority", "license_grant"
}
PIN_FIELDS = {"schema", "generation", "trust", "source_pins", "status"}
SOURCE_PIN_FIELDS = {"path", "sha256", "git_blob_sha", "revoked_sha256"}


class Held(ValueError):
    pass


def unique_pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise Held("DUPLICATE_JSON_FIELD")
        result[key] = value
    return result


def bad_constant(text):
    raise Held("NONFINITE_JSON_CONSTANT")


def read_bounded_json(path: Path, limit: int):
    if not path.is_file() or path.stat().st_size > limit:
        raise Held("INPUT_MISSING_OR_OVERSIZED")
    try:
        return json.loads(path.read_text(encoding="utf-8"),
                          object_pairs_hook=unique_pairs, parse_constant=bad_constant)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise Held("INVALID_JSON_INPUT") from exc


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def git_blob_digest(content: bytes) -> str:
    header = b"blob " + str(len(content)).encode("ascii") + b"\0"
    return hashlib.sha1(header + content).hexdigest()


def packet_digest(packet: dict) -> str:
    body = {key: val for key, val in packet.items() if key != "packet_sha256"}
    raw = json.dumps(body, sort_keys=True, ensure_ascii=True,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    return digest(raw)


def valid_source_path(path) -> bool:
    if not isinstance(path, str) or not path or "\\" in path:
        return False
    parts = path.split("/")
    return (parts[0] in ("ai", "docs") and len(parts) > 1 and
            all(x not in ("", ".", "..") for x in parts) and
            parts[-1].lower().endswith((".md", ".json", ".txt")))


def validate_packet(packet):
    if not isinstance(packet, dict) or set(packet) != PACKET_FIELDS:
        raise Held("PACKET_FIELDS_OR_SCHEMA_INVALID")
    if packet["schema"] != PACKET_SCHEMA:
        raise Held("PACKET_SCHEMA_NOT_RECOGNIZED")
    required = {
        "state": "PUBLIC_SOURCE_LOCAL_PORTABLE_CANDIDATE",
        "integrity": "SHA256_BYTES_PLUS_GIT_OBJECT_HASH_NOT_SIGNED_PUBLISHER",
        "source_instructions": "UNTRUSTED_DATA_NOT_TOOL_OR_SYSTEM_COMMANDS",
        "external_receiver_ack": "NOT_OBSERVED",
        "independent_replica": "NOT_OBSERVED",
        "memory_write": "NOT_PERFORMED",
        "model_weight_change": "NOT_PERFORMED",
        "created_by": "LOCAL_REFERENCE_TOOL_NOT_IDENTIFIED_EXTERNAL_PUBLISHER"
    }
    if any(packet.get(key) != value for key, value in required.items()):
        raise Held("FORGED_AUTHORITY_OR_EFFECT_CLAIM")
    if not isinstance(packet.get("packet_sha256"), str) or not SHA256.fullmatch(packet["packet_sha256"]):
        raise Held("PACKET_CHECKSUM_INVALID")
    if packet_digest(packet) != packet["packet_sha256"]:
        raise Held("PACKET_CHECKSUM_MISMATCH")
    sources = packet.get("sources")
    if not isinstance(sources, list) or not 1 <= len(sources) <= MAX_OBJECTS:
        raise Held("INVALID_SOURCE_COUNT")
    seen_names, seen_ids = set(), set()
    for source in sources:
        if not isinstance(source, dict) or set(source) != SOURCE_FIELDS:
            raise Held("UNEXPECTED_SOURCE_FIELD_OR_MISSING_DATA")
        source_id, path = source["id"], source["path"]
        if not isinstance(source_id, str) or not NAME.fullmatch(source_id):
            raise Held("INVALID_SOURCE_ID")
        if not valid_source_path(path):
            raise Held("INVALID_SOURCE_PATH")
        if source_id in seen_ids or path in seen_names:
            raise Held("DUPLICATE_SOURCE")
        seen_ids.add(source_id)
        seen_names.add(path)
        if source["visibility"] != "PUBLIC_SAFE" or source["epistemic"] not in ALLOWED_EPISTEMIC:
            raise Held("PRIVATE_OR_UNTYPED_OBJECT")
        if source["instruction_authority"] != "NONE" or source["license_grant"] != "NOT_ESTABLISHED":
            raise Held("UNAUTHORIZED_INSTRUCTION_OR_LICENSE")
        if not isinstance(source["sha256"], str) or not SHA256.fullmatch(source["sha256"]):
            raise Held("INVALID_SOURCE_CHECKSUM")
        if not isinstance(source["git_blob_sha"], str) or not SHA1.fullmatch(source["git_blob_sha"]):
            raise Held("INVALID_GIT_OBJECT_CHECKSUM")
        size = source["bytes"]
        if type(size) is not int or not 0 <= size <= MAX_SOURCE:
            raise Held("INVALID_SOURCE_SIZE")
        encoded = source["content_base64"]
        if not isinstance(encoded, str) or len(encoded) > (MAX_SOURCE * 4 // 3 + 16):
            raise Held("INVALID_ENCODED_SOURCE")
        try:
            raw = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise Held("INVALID_BASE64_SOURCE") from exc
        if len(raw) != size or digest(raw) != source["sha256"] or git_blob_digest(raw) != source["git_blob_sha"]:
            raise Held("SOURCE_BYTES_TAMPERED")
    return sources


def validate_pin(policy, min_generation):
    if not isinstance(policy, dict) or set(policy) != PIN_FIELDS:
        raise Held("RECEIVER_PIN_FIELDS_INVALID")
    if policy["schema"] != PIN_SCHEMA or policy["trust"] != "TEST_PIN_ONLY_NO_SIGNED_AUTHORITY":
        raise Held("UNAUTHENTICATED_PIN_CLAIMS_AUTHORITY")
    generation = policy["generation"]
    if type(generation) is not int or generation < min_generation:
        raise Held("STALE_RECEIVER_PIN_OR_ROLLBACK")
    pins = policy["source_pins"]
    if not isinstance(pins, dict) or len(pins) > MAX_OBJECTS:
        raise Held("INVALID_RECEIVER_PINS")
    for ident, pin in pins.items():
        if not isinstance(ident, str) or not NAME.fullmatch(ident):
            raise Held("INVALID_PIN_ID")
        if not isinstance(pin, dict) or set(pin) != SOURCE_PIN_FIELDS:
            raise Held("PIN_SOURCE_FIELDS_INVALID")
        if not valid_source_path(pin["path"]):
            raise Held("INVALID_PIN_PATH")
        if not isinstance(pin["sha256"], str) or not SHA256.fullmatch(pin["sha256"]):
            raise Held("INVALID_PIN_SHA256")
        if not isinstance(pin["git_blob_sha"], str) or not SHA1.fullmatch(pin["git_blob_sha"]):
            raise Held("INVALID_PIN_GIT_BLOB")
        revoked = pin["revoked_sha256"]
        if not isinstance(revoked, list) or len(revoked) > 512:
            raise Held("INVALID_REVOCATION_LIST")
        if not all(isinstance(x, str) and SHA256.fullmatch(x) for x in revoked):
            raise Held("INVALID_REVOKED_SHA256")
        if pin["sha256"] in revoked:
            raise Held("CURRENT_DIGEST_ALREADY_REVOKED")
    return generation, pins


def verify(packet, policy, min_generation=1):
    result = {
        "schema": RESULT_SCHEMA,
        "effect_boundary": "HELD",
        "checked_sources": 0, "matched": 0, "held": 0,
        "reasons": [], "receiver_policy_generation": None,
        "issuer_signature_validated": False,
        "external_agent_ack": "NOT_OBSERVED",
        "independent_operator": "NOT_OBSERVED",
        "off_provider_cold_restore": "NOT_OBSERVED",
        "persistent_memory_write": "NOT_PERFORMED",
        "model_weight_change": "NOT_PERFORMED",
        "authority_granted": "NONE",
        "source_data_executed": False
    }
    try:
        if type(min_generation) is not int or min_generation < 1:
            raise Held("INVALID_MINIMUM_GENERATION")
        sources = validate_packet(packet)
        result["checked_sources"] = len(sources)
        generation, pins = validate_pin(policy, min_generation)
        result["receiver_policy_generation"] = generation
        for source in sources:
            pin = pins.get(source["id"])
            status = "LOCAL_PIN_MATCH"
            if pin is None:
                status = "SOURCE_NOT_ALLOWED_BY_RECEIVER"
            elif pin["path"] != source["path"]:
                status = "UNAPPROVED_SOURCE_PATH"
            elif source["sha256"] in pin["revoked_sha256"]:
                status = "REVOKED_OR_SUPERSEDED_SOURCE"
            elif pin["sha256"] != source["sha256"] or pin["git_blob_sha"] != source["git_blob_sha"]:
                status = "UNRECOGNIZED_OR_STALE_SOURCE"
            if status == "LOCAL_PIN_MATCH":
                result["matched"] += 1
            else:
                result["reasons"].append({"id": source["id"], "status": status})
        result["held"] = len(sources) - result["matched"]
        result["effect_boundary"] = ("LOCAL_PIN_MATCH_ONLY" if result["held"] == 0
                                     else "PARTIAL_OR_HELD")
    except (Held, KeyError, TypeError, ValueError) as exc:
        result["held"] = result["checked_sources"] or 1
        result["reasons"].append({"status": str(exc)})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Standalone source-byte verifier; no model or internet")
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--receiver-pin", type=Path, required=True)
    parser.add_argument("--minimum-generation", type=int, default=1)
    args = parser.parse_args(argv)
    try:
        packet = read_bounded_json(args.packet, MAX_PACKET)
        pin = read_bounded_json(args.receiver_pin, MAX_PIN)
        result = verify(packet, pin, args.minimum_generation)
    except (Held, OSError) as exc:
        result = {
            "schema": RESULT_SCHEMA, "effect_boundary": "HELD",
            "reasons": [{"status": str(exc)}],
            "issuer_signature_validated": False,
            "external_agent_ack": "NOT_OBSERVED",
            "off_provider_cold_restore": "NOT_OBSERVED",
            "persistent_memory_write": "NOT_PERFORMED",
            "model_weight_change": "NOT_PERFORMED",
            "authority_granted": "NONE"
        }
    print(json.dumps(result, sort_keys=True))
    return 0 if result["effect_boundary"] == "LOCAL_PIN_MATCH_ONLY" else 2


if __name__ == "__main__":
    sys.exit(main())
