"""CoMedia retro-backfill R0: bounded read-only media custody candidates.

Explicit local roots only. The output is PRIVATE by default and may contain
absolute local paths; NEVER commit a generated manifest without privacy review.
This does not interpret visual meaning, copy media, upload, publish, or adopt
anything into CoSeed/CoPath. Symlinks are never followed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

MEDIA_EXTENSIONS = {
    ".png": "image", ".jpg": "image", ".jpeg": "image", ".webp": "image",
    ".gif": "image", ".svg": "diagram", ".drawio": "diagram",
    ".mp4": "video", ".webm": "video", ".mov": "video",
    ".mp3": "audio", ".wav": "audio", ".flac": "audio",
    ".pdf": "document", ".pptx": "presentation",
}
SCHEMA = "CoMedia.RetroBackfill.R0"


def candidates(roots, *, max_files):
    """Yield at most max_files+1 regular candidate paths in stable order."""
    for root in sorted({str(Path(p).absolute()) for p in roots}):
        path = Path(root)
        if path.is_symlink() or not path.exists():
            continue
        if path.is_file():
            if path.suffix.lower() in MEDIA_EXTENSIONS:
                yield path
            continue
        if not path.is_dir():
            continue
        for directory, subdirs, files in os.walk(path, topdown=True, followlinks=False):
            subdirs[:] = sorted(d for d in subdirs
                                if not (Path(directory) / d).is_symlink())
            for name in sorted(files):
                item = Path(directory) / name
                if not item.is_symlink() and item.suffix.lower() in MEDIA_EXTENSIONS:
                    yield item


def inspect(roots, *, max_files=100, max_bytes_per_file=50_000_000):
    if not roots or max_files < 1 or max_bytes_per_file < 1:
        raise ValueError("explicit roots and positive budgets required")
    records, skipped, seen_hashes = [], [], {}
    truncated = False
    for path in candidates(roots, max_files=max_files):
        if len(records) + len(skipped) >= max_files:
            truncated = True
            break
        try:
            stat = path.stat()
            if not path.is_file() or stat.st_size > max_bytes_per_file:
                skipped.append({"path": str(path), "reason": "TOO_LARGE_OR_NOT_REGULAR"})
                continue
            hasher = hashlib.sha256()
            with path.open("rb") as stream:
                while True:
                    block = stream.read(1024 * 1024)
                    if not block:
                        break
                    hasher.update(block)
            sha = hasher.hexdigest()
            previous = seen_hashes.get(sha)
            if previous is None:
                seen_hashes[sha] = str(path)
            records.append({
                "source_path": str(path),
                "kind": MEDIA_EXTENSIONS[path.suffix.lower()],
                "bytes": stat.st_size, "sha256": sha,
                "duplicate_of_path": previous,
                "custody": "VERIFIED_LOCAL",
                "semantic_review": "NOT_SEMANTICALLY_REVIEWED",
                "inspiration": "CANDIDATE_UNREVIEWED",
                "co_seed_adoption": "NOT_PROVEN",
                "co_path_adoption": "NOT_PROVEN",
                "receiver_ack": "NOT_PROVEN",
                "publication": "NOT_AUTHORIZED",
            })
        except (OSError, ValueError):
            skipped.append({"path": str(path), "reason": "UNREADABLE_OR_CHANGED"})
    return {
        "schema": SCHEMA,
        "coverage": {"explicit_roots": list(roots), "bounded_max_files": max_files,
                     "max_bytes_per_file": max_bytes_per_file,
                     "truncated": truncated, "complete_history": False},
        "media": records,
        "skipped": skipped,
        "hashes": {"duplicate_content_candidates": sum(
            r["duplicate_of_path"] is not None for r in records)},
        "eligible_next_transitions": ["PRIVATE_SEMANTIC_REVIEW", "PERMISSION_REVIEW"],
        "nonclaims": [
            "LOCAL_IS_NOT_LANDED", "VALIDATION_IS_NOT_ACCEPTANCE",
            "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
            "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
            "HASHING_IS_NOT_SEMANTIC_INGESTION",
            "DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY",
        ],
        "privacy": "PRIVATE_MANIFEST_DO_NOT_PUBLICLY_COMMIT",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True,
                        help="Explicit bounded file/directory root; repeatable")
    parser.add_argument("--output", required=True,
                        help="PRIVATE manifest JSON output; never a public repository path")
    parser.add_argument("--max-files", type=int, default=100)
    parser.add_argument("--max-bytes-per-file", type=int, default=50_000_000)
    args = parser.parse_args()
    report = inspect(args.input, max_files=args.max_files,
                     max_bytes_per_file=args.max_bytes_per_file)
    output = Path(args.output)
    if output.exists():
        raise SystemExit("Refusing to overwrite existing manifest")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
    print(json.dumps({"schema": SCHEMA,
                      "verified_local": len(report["media"]),
                      "skipped": len(report["skipped"]),
                      "truncated": report["coverage"]["truncated"],
                      "private_manifest": True}))


if __name__ == "__main__":
    main()
