#!/usr/bin/env python3
"""CoImage R0: bounded, read-only tracked-image discovery. No remote crawling.

All outputs are candidate relations, not verified visual semantics, licenses,
receiver approvals or permission to distribute the underlying asset.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

SCHEMA = "CoImage.TrackedVisualCandidateCensus.R0"
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg", ".tif", ".tiff"}
TOPIC_TOKENS = {
    "orb": "CoOrbWare", "map": "CoMap", "diagram": "CoDiagram",
    "glyph": "CoGlyph", "mouse": "CoInput", "thumb": "CoPayload",
    "laser": "CoTheoryAll", "fractal": "CoTheoryAll", "science": "CoResearch",
    "signal": "CoResearch", "video": "CoMedia", "icon": "CoFrontDoor",
    "logo": "CoFrontDoor", "evo": "CoEvoAll", "model": "CoModelWare",
}
MAX_FILES = 400
MAX_ONE_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 64 * 1024 * 1024


def git(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, timeout=15
    ).stdout


def image_signature(ext: str, head: bytes) -> bool:
    if ext == ".png":
        return head.startswith(b"\x89PNG\r\n\x1a\n")
    if ext in (".jpg", ".jpeg"):
        return head.startswith(b"\xff\xd8\xff")
    if ext == ".gif":
        return head.startswith((b"GIF87a", b"GIF89a"))
    if ext == ".webp":
        return head.startswith(b"RIFF") and head[8:12] == b"WEBP"
    if ext == ".bmp":
        return head.startswith(b"BM")
    if ext in (".tif", ".tiff"):
        return head.startswith((b"II*\x00", b"MM\x00*"))
    if ext == ".svg":
        return b"<svg" in head[:4096].lower()
    return False


def tokenize(filename: str) -> list[str]:
    import re
    return sorted(set(re.findall(r"[a-z0-9]+", filename.lower())))


def scan(root: Path, max_files: int = MAX_FILES, max_one: int = MAX_ONE_BYTES,
         max_total: int = MAX_TOTAL_BYTES) -> dict:
    if not root.is_dir():
        raise ValueError("root is not a directory")
    if not (0 <= max_files <= MAX_FILES and 0 <= max_one <= MAX_ONE_BYTES
            and 0 <= max_total <= MAX_TOTAL_BYTES):
        raise ValueError("bounds exceed the audited R0 ceiling")
    raw = git(root, "ls-files", "-z", "--cached", "--full-name")
    paths = sorted({os.fsdecode(x) for x in raw.split(b"\x00") if x})
    images = [p for p in paths if Path(p).suffix.lower() in EXTENSIONS]
    try:
        commit = git(root, "rev-parse", "HEAD").decode().strip()
    except subprocess.CalledProcessError:
        commit = None
    candidates, unexamined = [], []
    examined_bytes = 0
    for idx, relative in enumerate(images):
        if idx >= max_files:
            unexamined.append({"path": relative, "reason": "FILE_COUNT_CAP"})
            continue
        file_path = root / relative
        ext = file_path.suffix.lower()
        # A Git-tracked path may be a symlink. Never follow it out of scope.
        if file_path.is_symlink():
            unexamined.append({"path": relative, "reason": "SYMLINK_NOT_FOLLOWED"})
            continue
        try:
            if not file_path.is_file() or not file_path.resolve().is_relative_to(root.resolve()):
                unexamined.append({"path": relative, "reason": "NOT_READABLE_REGULAR_FILE"})
                continue
            size = file_path.stat().st_size
            if size > max_one or examined_bytes + size > max_total:
                unexamined.append({"path": relative, "reason": "BYTE_BUDGET_CAP", "bytes": size})
                continue
            # Bound memory. Hash actual file bytes once; no external process or renderer.
            data = file_path.read_bytes()
        except OSError:
            unexamined.append({"path": relative, "reason": "READ_FAILED"})
            continue
        examined_bytes += len(data)
        digest = hashlib.sha256(data).hexdigest()
        terms = tokenize(file_path.stem)
        topics = sorted({v for k, v in TOPIC_TOKENS.items() if k in terms})
        signature_ok = image_signature(ext, data[:4096])
        candidates.append({
            "asset_id": "git-sha256:" + digest,
            "source_path": relative.replace("\\", "/"),
            "source_commit": commit,
            "extension": ext,
            "byte_count": len(data),
            "sha256": digest,
            "format_header": "PLAUSIBLE_NOT_FULLY_DECODED" if signature_ok else "SUSPECT",
            "candidate_topics_from_filename_only": topics,
            "relation_candidates_not_facts": [
                "POSSIBLE_PRIOR_ART", "POSSIBLE_CONTRADICTION",
                "POSSIBLE_ALTERNATIVE_RENDER", "ACCESSIBLE_DESCRIPTION_NEEDED",
            ],
            "license": "UNVERIFIED", "attribution": "UNKNOWN",
            "privacy": "REVIEW_REQUIRED", "publication": "HOLD",
            "semantic_visual_review": "NOT_PERFORMED",
            "accessible_description": None,
            "routing": "PRIVATE_OR_DRAFT_REVIEW_ONLY",
        })
    same_bytes = {}
    for item in candidates:
        same_bytes.setdefault(item["sha256"], []).append(item["source_path"])
    duplicates = [
        {"sha256": sha, "paths": sorted(paths)}
        for sha, paths in sorted(same_bytes.items()) if len(paths) > 1
    ]
    return {
        "schema": SCHEMA,
        "state": "SCOPED_GIT_IMAGE_BYTES_CANDIDATES_ONLY__NO_RELEASE",
        "source_commit": commit, "search_scope": "GIT_TRACKED_FILES_IN_SELECTED_REPOSITORY_ONLY",
        "limits": {"max_files": max_files, "max_one_bytes": max_one,
                   "max_total_bytes": max_total},
        "discovered_image_paths": len(images),
        "hashed_candidate_count": len(candidates),
        "bytes_hashed": examined_bytes,
        "unexamined_count": len(unexamined),
        "negative_knowledge": unexamined,
        "duplicate_byte_groups": duplicates,
        "candidates": candidates,
        "effects": {"network_requests": 0, "files_written": 0, "models_called": 0,
                    "images_redistributed": 0, "messages_sent": 0},
        "next": "HUMAN_OR_AUTHORIZED_MODEL_VISUAL_REVIEW_PLUS_ORIGINAL_RIGHTS_CONFIRMATION",
        "nonclaims": [
            "TRACKED_IMAGE_PATHS_NE_ALL_RESEARCHABLE_IMAGES",
            "IMAGE_BYTES_NE_SEMANTIC_VISUAL_INSPECTION",
            "SOURCE_COMMIT_NE_CREATOR_LICENSE",
            "SAME_SHA_NE_SAME_PROVENANCE_OR_RIGHTS",
            "CANDIDATE_RELATION_NE_FACT_OR_SCIENTIFIC_PROOF",
            "FILE_HEADER_NE_FULL_SAFE_DECODING",
            "FILENAME_TOPIC_NE_IMAGE_CONTENT",
            "NO_AUTOMATED_CRAWL_DOWNLOAD_OR_BROADCAST",
            "INDEX_NE_RECEIVER_ACK_OR_RUNTIME_DEPLOYMENT",
            "FINITE_CONTEXT_NE_UNLIMITED_TOKENS",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--max-files", type=int, default=MAX_FILES)
    parser.add_argument("--max-one-bytes", type=int, default=MAX_ONE_BYTES)
    parser.add_argument("--max-total-bytes", type=int, default=MAX_TOTAL_BYTES)
    args = parser.parse_args()
    output = scan(args.root, args.max_files, args.max_one_bytes, args.max_total_bytes)
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
