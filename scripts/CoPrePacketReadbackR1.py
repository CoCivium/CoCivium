#!/usr/bin/env python3
"""Standalone, read-only verifier for CoPreGeneric R1 portable CI preview.

Runs without repository checkout, networking, external effects, or provider
credentials. It verifies packet bytes and reconstructs the two synthetic views,
NOT independent external receiver adoption, human comprehension, or canon.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SOURCE_PATH = "source/copre-r1-source.json"
SYNTH_PATH = "synthetic-local-a/copre-r1-synth.json"
BIO_PATH = "synthetic-local-b/copre-r1-bio.md"
FRONT_PATH = "README.md"
MANIFEST_PATH = "receipt.json"
EXPECTED_PATHS = {
    "source": SOURCE_PATH, "synth": SYNTH_PATH,
    "bio": BIO_PATH, "front_door": FRONT_PATH,
}
REQUIRED_NONCLAIMS = {
    "NO_INDEPENDENT_RECEIVER_PICKUP",
    "NOT_GLOBAL_COPRE_CANON",
    "NOT_AGI_OR_SENTIENCE_PROOF",
    "NOT_SPIRITUAL_REVELATION",
    "CI_ARTIFACT_NOT_DURABLE_LANDING",
}


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)


def read_member(root: Path, relative: str) -> bytes:
    require(relative in set(EXPECTED_PATHS.values()) | {MANIFEST_PATH}, "UNKNOWN_PATH")
    candidate = root / relative
    require(candidate.is_file() and not candidate.is_symlink(), "MISSING_OR_SYMLINK_MEMBER")
    return candidate.read_bytes()


def verify(root: Path) -> dict:
    root = Path(root)
    require(root.is_dir() and not root.is_symlink(), "INVALID_ROOT")
    receipt_bytes = read_member(root, MANIFEST_PATH)
    receipt = json.loads(receipt_bytes)
    require(receipt.get("schema") == "CoAll.CoPre.PortablePreviewReceipt.R1", "INVALID_SCHEMA")
    require(receipt.get("lifecycle") == "TEMPORARY_CI_PREVIEW_NOT_DURABLE_RECEIVER_LANDING",
            "PROMOTED_LIFECYCLE")
    require(receipt.get("effect_authority") == "NONE", "UNSAFE_AUTHORITY")
    require(receipt.get("external_effects") == 0, "EXTERNAL_EFFECT")
    require(receipt.get("receiver") is None and receipt.get("receiver_readproof") is None,
            "INVENTED_RECEIVER")
    require(REQUIRED_NONCLAIMS.issubset(receipt.get("nonclaims", [])), "LOST_NONCLAIMS")
    observed = receipt["readback"]
    require(set(observed) == set(EXPECTED_PATHS), "MISSING_OR_EXTRA_MANIFEST_MEMBER")

    raw = {}
    for role, rel in EXPECTED_PATHS.items():
        require(observed[role].get("path") == rel, "PATH_REBIND")
        payload = read_member(root, rel)
        require(sha256(payload) == observed[role].get("sha256"), "SHA256_MISMATCH:" + role)
        require(len(payload) == observed[role].get("bytes"), "LENGTH_MISMATCH:" + role)
        raw[role] = payload

    obj = json.loads(raw["source"])
    synth = json.loads(raw["synth"])
    bio = raw["bio"].decode("utf-8")
    guide = raw["front_door"].decode("utf-8")
    blob = git_blob_sha(raw["source"])
    work_id = obj["work_id"]

    require(obj.get("schema") == "CoAll.CoPreGeneric.SynthBioGdTerms.R1-candidate",
            "SOURCE_SCHEMA_MISMATCH")
    require(obj.get("state") == "PUBLIC_DRAFT_PR_NOT_MERGED_NOT_CANON",
            "SOURCE_PROMOTION")
    require(obj.get("effect_authority") == "NONE", "SOURCE_EFFECT_AUTHORITY")
    require(receipt.get("work_id") == work_id and
            receipt["source"].get("git_blob_sha") == blob and
            observed["source"].get("git_blob_sha") == blob, "SOURCE_IDENTITY_MISMATCH")
    require(synth.get("work_id") == work_id and
            synth.get("source_git_blob_sha") == blob and
            synth.get("effect_authority") == "NONE" and
            synth.get("receiver_ack") is None, "SYNTH_IDENTITY_OR_AUTHORITY")
    require(synth.get("schema") == "CoAll.CoPre.ReceiverNative.SynthR1",
            "SYNTH_SCHEMA_MISMATCH")
    terms = obj.get("terms", [])
    edges = obj.get("relations", [])
    require(len(terms) == 72 and len(edges) == 22, "SOURCE_COUNTS")
    require(synth["graph"]["nodes"] == terms and
            synth["graph"]["relations"] == edges and
            synth["graph"]["families"] == obj["families"], "GRAPH_RECONSTRUCTION_MISMATCH")
    require(all(t.get("status") == "UNQUALIFIED_PUBLIC_CANDIDATE" for t in terms),
            "TERM_PROMOTION")
    require(all(e.get("effect_authority") == "NONE" for e in edges),
            "RELATION_AUTHORITY")
    require("Source Git blob: " + blob in bio and
            "WorkID: " + work_id in bio and
            "Authority: NONE" in bio, "BIO_SOURCE_IDENTITY_MISMATCH")
    require(receipt["source"]["human_sha256"] ==
            synth["human_source_sha256"], "HUMAN_SOURCE_DIGEST_MISMATCH")
    human_marker = "# CoPreGeneric R1 | CoSynthVerse, CoBioVerse and CoG_dSide candidate CoTerms"
    require(human_marker in bio, "BIO_ORIGINAL_SOURCE_MARKER_MISSING")
    original_markdown = bio[bio.index(human_marker):]
    require(sha256(original_markdown.encode("utf-8")) ==
            receipt["source"]["human_sha256"], "BIO_ORIGINAL_DIGEST_MISMATCH")
    require(all("**" + t["label"] + "**" in original_markdown for t in terms),
            "BIO_TERM_LOSS")
    require("CoHereNow:" in guide and "Next:" in guide and
            "receipt.json" in guide, "UNUSABLE_FRONT_DOOR")
    require(receipt["loss_ledger"]["cross_projection_equivalence"] == "UNTESTED",
            "INVENTED_EQUIVALENCE")

    return {
        "state": "CI_CROSS_JOB_PACKET_READBACK_VERIFIED_NOT_EXTERNAL_RECEIVER",
        "work_id": work_id,
        "source_git_blob_sha": blob,
        "receipt_sha256": sha256(receipt_bytes),
        "verified_payload_members": 4,
        "receiver_scope": "SAME_GITHUB_ACTIONS_DISTINCT_JOB",
        "external_effects": 0,
        "receiver_readproof": None,
        "nonclaims": sorted(REQUIRED_NONCLAIMS | {
            "NO_PROVIDER_CROSSING",
            "NO_INDEPENDENT_EXTERNAL_RECEIVER_ACK",
            "NO_CANON_RUNTIME_OR_COEX_INFERENCE",
        }),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(verify(args.root), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
