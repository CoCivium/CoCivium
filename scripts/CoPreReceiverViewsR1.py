#!/usr/bin/env python3
"""CoPreGeneric R1 receiver-native preview projections.

Pure and offline except for explicit caller-chosen local preview writes.
Not a dispatch engine, external receiver ACK, deployment, canon or CoEx.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


SCHEMA = "CoAll.CoPreGeneric.SynthBioGdTerms.R1-candidate"
EXPECTED_NONCLAIMS = {
    "NO_INDEPENDENT_RECEIVER_PICKUP",
    "NOT_GLOBAL_COPRE_CANON",
    "NOT_AGI_OR_SENTIENCE_PROOF",
    "NOT_SPIRITUAL_REVELATION",
}


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def stable_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    ).encode("utf-8")


def project(source_bytes: bytes, human_markdown: str) -> dict:
    """Fail closed and return two genuinely different read-only projections."""
    obj = json.loads(source_bytes)
    if obj.get("schema") != SCHEMA or obj.get("state") != "PUBLIC_DRAFT_PR_NOT_MERGED_NOT_CANON":
        raise ValueError("unqualified CoPre source identity or promotion")
    if obj.get("effect_authority") != "NONE":
        raise ValueError("CoPre source grants effects")
    terms, edges, families = obj["terms"], obj["relations"], obj["families"]
    ids = {term["id"] for term in terms}
    labels = {term["label"] for term in terms}
    if len(terms) != 72 or len(ids) != 72 or len(labels) != 72:
        raise ValueError("unexpected CoPre node count or duplicates")
    if len(edges) != 22 or len(families) != 9:
        raise ValueError("unexpected CoPre graph dimensions")
    if any(t.get("status") != "UNQUALIFIED_PUBLIC_CANDIDATE" or
           t.get("epistemic_class") != "DESIGN_HYPOTHESIS_NOT_FACT" for t in terms):
        raise ValueError("unqualified term promotion")
    if any(r.get("effect_authority") != "NONE" or
           r.get("from") not in ids or r.get("to") not in ids for r in edges):
        raise ValueError("unbound relation or unsafe effect authority")
    if any("**" + label + "**" not in human_markdown for label in labels):
        raise ValueError("human-readable source omits a CoTerm")
    if any("**" + r["type"] + "**" not in human_markdown for r in edges):
        raise ValueError("human-readable source omits a relation")
    if not EXPECTED_NONCLAIMS.issubset(obj.get("nonclaims", [])):
        raise ValueError("required nonclaims absent")
    if len({f["code"] for f in families}) != 9 or any(
        sum(t["group"] == f["code"] for t in terms) != f["term_count"]
        for f in families
    ):
        raise ValueError("family coverage incomplete")

    src_sha = git_blob_sha(source_bytes)
    human_sha = sha256(human_markdown.encode("utf-8"))
    common = {
        "work_id": obj["work_id"],
        "source_git_blob_sha": src_sha,
        "source_schema": SCHEMA,
        "human_source_sha256": human_sha,
        "qualification": "SYNTHETIC_LOCAL_PROJECTION_NOT_INDEPENDENT_RECEIVER",
        "receiver_ack": None,
        "effect_authority": "NONE",
    }
    synth = {
        "schema": "CoAll.CoPre.ReceiverNative.SynthR1",
        **common,
        "receiver_class": "SYNTHETIC_MACHINE",
        "graph": {
            "nodes": terms,
            "relations": edges,
            "families": families,
        },
        "source_refs": obj.get("source_refs", []),
        "epistemic_lanes": obj.get("epistemic_lanes", {}),
        "nonclaims": sorted(EXPECTED_NONCLAIMS),
        "translation_loss": {
            "bio_narrative_not_embedded": True,
            "bio_sha256": human_sha,
            "semantic_equivalence": "NOT_PROVEN",
        },
    }
    bio_prelude = "\n".join([
        "# CoPreGeneric R1 | Human-native recovery preview",
        "",
        "Status: SYNTHETIC LOCAL VIEW. Not consent, receiver acknowledgment, canon, or deployment.",
        "WorkID: " + obj["work_id"],
        "Source Git blob: " + src_sha,
        "Human source SHA-256: " + human_sha,
        "Receiver: synthetic-local-b (test fixture only)",
        "Authority: NONE; revocation and consent never inferred.",
        "Translation loss: typed graph IDs and machine-only metadata are not rendered as a native graph.",
        "Meaning and equivalence require separate authorized receiver review.",
        "",
        "---",
        "",
    ])
    bio = bio_prelude + human_markdown
    return {
        "common": common,
        "synth": synth,
        "bio": bio,
        "loss_ledger": {
            "synth": "HUMAN_NARRATIVE_NOT_EMBEDDED; REFER_TO_BIO_SHA256",
            "bio": "TYPED_GRAPH_IDS_NOT_FULLY_PRESENT; REFER_TO_SYNTH_GRAPH",
            "cross_projection_equivalence": "UNTESTED",
        },
    }


def save_local_preview(root: Path, views: dict) -> dict:
    """Create only two new local preview files, never overwrite prior evidence."""
    root = Path(root)
    if root.exists():
        raise FileExistsError("preview root must be new; no clobber or implicit supersession")
    synth_dir = root / "synthetic-local-a"
    bio_dir = root / "synthetic-local-b"
    synth_dir.mkdir(parents=True, exist_ok=False)
    bio_dir.mkdir(parents=True, exist_ok=False)
    paths = {
        "synth": synth_dir / "copre-r1-synth.json",
        "bio": bio_dir / "copre-r1-bio.md",
    }
    values = {
        "synth": stable_bytes(views["synth"]),
        "bio": views["bio"].encode("utf-8"),
    }
    receipts = {}
    for role in ("synth", "bio"):
        target = paths[role]
        with target.open("xb") as fh:
            fh.write(values[role])
        readback = target.read_bytes()
        if readback != values[role]:
            raise IOError("local preview readback mismatch")
        receipts[role] = {
            "sha256": sha256(readback),
            "bytes": len(readback),
            "work_id": views["common"]["work_id"],
            "source_git_blob_sha": views["common"]["source_git_blob_sha"],
            "receiver_ack": None,
            "effect_authority": "NONE",
            "state": "LOCAL_SYNTHETIC_READBACK_NOT_RECEIVER_PICKUP",
        }
    if receipts["synth"]["sha256"] == receipts["bio"]["sha256"]:
        raise AssertionError("receiver native projections are not distinct")
    return receipts
