#!/usr/bin/env python3
"""Public-only CoMap atlas and retro media candidate index. NO runtime effects."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

from relational_media_manifest_r0 import audit

SCHEMA = "CoMap.RetroAtlas.PublicMedia.R0"
ROOTS = ("examples/colensmedia/", "examples/comap/",
         "examples/coorbmembrane_r0/", "examples/covisual_finder_r1/")
SUFFIXES = {".md", ".html", ".svg", ".png", ".jpg", ".jpeg",
            ".webp", ".gif", ".pdf", ".mp4", ".webm", ".mp3", ".wav"}
MAX_FILES = 160
MAX_BYTES = 3_000_000
DISPLAY_LIMIT = 14
SAFE_LABEL = re.compile(r"[a-zA-Z0-9 +/_.:-]{1,100}\Z")
SAFE_FRONT = re.compile(r"[a-z][a-z0-9-]{1,96}\Z")
STATES = {"proposed", "source_committed", "tests_executed",
          "independently_observed", "released"}


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def in_scope(relative: str) -> bool:
    if not isinstance(relative, str) or "\\" in relative or "\x00" in relative:
        return False
    path = PurePosixPath(relative)
    return (not path.is_absolute()
            and all(part not in ("", ".", "..") for part in path.parts)
            and any(relative.startswith(r) for r in ROOTS)
            and path.suffix.lower() in SUFFIXES)


def tracked_public_paths(root: Path) -> list[str]:
    """Scan one bounded, already-public Git checkout. Never private devices."""
    proc = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--", *ROOTS],
        capture_output=True, timeout=12, check=True)
    paths = [p.decode("utf-8") for p in proc.stdout.split(b"\0") if p]
    return sorted(p for p in paths if in_scope(p))


def read_public_file(root: Path, relative: str) -> bytes:
    if not in_scope(relative):
        raise ValueError("HOLD_UNAUTHORIZED_OR_UNSCOPED_MEDIA_PATH")
    current = root
    for part in PurePosixPath(relative).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("HOLD_SYMLINK_MEDIA_SOURCE")
    if not current.is_file():
        raise ValueError("HOLD_MEDIA_SOURCE_MISSING")
    if not 0 < current.stat().st_size <= MAX_BYTES:
        raise ValueError("HOLD_MEDIA_SOURCE_SIZE")
    blob = current.read_bytes()
    if not 0 < len(blob) <= MAX_BYTES:
        raise ValueError("HOLD_MEDIA_SOURCE_SIZE")
    return blob


def inventory(root: Path, paths: list[str], prior: dict | None = None) -> dict:
    """Idempotent byte-level inventory. Unreviewed candidates never self-promote."""
    if (not isinstance(paths, list) or len(paths) > MAX_FILES
            or len(paths) != len(set(paths))):
        raise ValueError("HOLD_MEDIA_SCAN_SCOPE_OR_DUPLICATE")
    earlier = [] if prior is None else prior.get("candidates")
    if prior is not None and (not isinstance(prior, dict)
                              or prior.get("schema") != SCHEMA
                              or not isinstance(earlier, list)):
        raise ValueError("HOLD_PRIOR_INDEX_SCHEMA")
    stored = {}
    for record in earlier:
        if (not isinstance(record, dict)
                or not in_scope(record.get("source_path"))
                or not isinstance(record.get("sha256"), str)
                or not re.fullmatch(r"[a-f0-9]{64}", record["sha256"])
                or record.get("semantic_coverage") != "NOT_SEMANTICALLY_REVIEWED"
                or record.get("inspiration_edges") != []):
            raise ValueError("HOLD_PRIOR_INDEX_AUTHORITY_OR_INTEGRITY")
        key = (record["source_path"], record["sha256"])
        if key in stored:
            raise ValueError("HOLD_PRIOR_DUPLICATE")
        stored[key] = record.copy()

    active = []
    added = 0
    for relative in sorted(paths):
        blob = read_public_file(root, relative)
        checksum = sha(blob)
        key = (relative, checksum)
        if key not in stored:
            predecessors = sorted(
                value for old_path, value in stored if old_path == relative)
            stored[key] = {
                "source_path": relative, "sha256": checksum,
                "byte_count": len(blob), "custody": "PUBLIC_REPO_CHECKOUT",
                "lifecycle": "VERIFIED_LOCAL",
                "semantic_coverage": "NOT_SEMANTICALLY_REVIEWED",
                "inspiration_state": "UNREVIEWED_INSPIRATION_CANDIDATE",
                "inspiration_edges": [],
                "possible_predecessor_hashes": predecessors,
                "rights_review": "NOT_PERFORMED",
                "receiver_readproof": None,
            }
            added += 1
        active.append(key)
    candidates = sorted(stored.values(),
                        key=lambda x: (x["source_path"], x["sha256"]))
    return {
        "schema": SCHEMA,
        "scope": "GIT_TRACKED_PUBLIC_REPO_BOUNDED_PATHS_ONLY",
        "roots": list(ROOTS), "candidates": candidates,
        "current_source_keys": [
            {"source_path": p, "sha256": h} for p, h in sorted(active)],
        "new_candidates": added,
        "historical_candidates_retained": len(candidates)-len(active),
        "semantic_coverage": "NOT_SEMANTICALLY_REVIEWED",
        "all_prior_media_covered": False,
        "co_seed_or_path_links_verified": False,
        "inspiration_edges_promoted": 0,
        "actual_receiver_ack": False,
        "nonclaims": [
            "LOCAL_IS_NOT_LANDED",
            "HASHING_IS_NOT_SEMANTIC_INGESTION",
            "DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY",
            "PUBLIC_SOURCE_NE_PERMISSION_TO_REPUBLISH",
            "INSPIRATION_CANDIDATE_NE_CANON",
            "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
            "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
        ],
    }


def safe(value: str) -> str:
    if not isinstance(value, str) or not SAFE_LABEL.fullmatch(value):
        raise ValueError("HOLD_UNSAFE_ATLAS_LABEL")
    return value


def atlas(frontier: dict, manifest: dict, scan: dict) -> str:
    """Nested Mermaid and text, from same public inputs; no invented links."""
    if (not isinstance(frontier, dict)
            or frontier.get("schema") != "cocivium.frontier-index.r0"
            or not isinstance(frontier.get("fronts"), list)
            or not 0 < len(frontier["fronts"]) <= 50):
        raise ValueError("HOLD_FRONTIER_SCHEMA_OR_BUDGET")
    if not isinstance(scan, dict) or scan.get("schema") != SCHEMA:
        raise ValueError("HOLD_RETRO_INDEX_SCHEMA")
    checked = audit(manifest)
    root = next(x for x in manifest["assets"] if x["id"] == manifest["root_id"])
    if root["visibility"] != "PUBLIC":
        raise ValueError("HOLD_PRIVATE_SOURCE_ROOT")
    public = [x for x in manifest["assets"] if x["visibility"] == "PUBLIC"]
    visible_ids = {x["id"] for x in public}
    visible_edges = [e for e in manifest["relations"]
                     if e["from"] in visible_ids and e["to"] in visible_ids]
    lines = [
        "# CoMap / CoNav atlas of atlases R0", "",
        "**SOURCE-ONLY PUBLIC PROJECTION. NO X2 OR LIVE RECEIVER ACK.**", "",
        "One derived view of existing public evidence fronts, a CoLens WorkID,",
        "and a bounded retro scan. Proximity is not a verified relationship.", "",
        "~~~mermaid", "flowchart TB",
        '  subgraph COALL["CoAll atlas of atlases"]',
        '    subgraph F["Evidence fronts / one existing index"]',
    ]
    names = set()
    for i, f in enumerate(frontier["fronts"]):
        fid, state = f.get("id"), f.get("status")
        if (not isinstance(fid, str) or not SAFE_FRONT.fullmatch(fid)
                or fid in names or state not in STATES):
            raise ValueError("HOLD_INVALID_FRONT_OR_DUPLICATE")
        names.add(fid)
        lines.append('      F'+str(i)+'["'+safe(fid+" : "+state)+'"]')
    lines += ["    end", '    subgraph M["One CoSourceGraph media WorkID"]']
    groups = (
        ("S", "Source / claims", {"SOURCE", "ARTICLE", "COUNTEREXAMPLE"}),
        ("V", "Visual / Orb", {"DIAGRAM", "ORB_VIEW"}),
        ("A", "Audio / video", {"AUDIO", "VIDEO"}),
        ("T", "Accessible text", {"ACCESSIBLE_TEXT"}),
        ("R", "Other public", {"RECEIPT", "EMAIL_DRAFT"}),
    )
    ids = {}
    for group_id, title, kinds in groups:
        chosen = [x for x in public if x["kind"] in kinds]
        if not chosen:
            continue
        lines.append('      subgraph '+group_id+'["'+title+'"]')
        for asset in chosen:
            node = "M"+str(len(ids))
            ids[asset["id"]] = node
            lines.append('        '+node+'["'+safe(asset.get("label") or asset["kind"])+'"]')
        lines.append("      end")
    lines += ["    end",
              '    subgraph RETRO["Previously published media / UNREVIEWED"]']
    active = {(x["source_path"], x["sha256"])
              for x in scan["current_source_keys"]}
    current = [x for x in scan["candidates"]
               if (x["source_path"], x["sha256"]) in active]
    for i, item in enumerate(current[:DISPLAY_LIMIT]):
        p = item["source_path"]
        name = p.split("/")[1]+"/"+PurePosixPath(p).name
        lines.append('      R'+str(i)+'["'+safe(name+" : candidate")+'"]')
    lines += ["    end", "  end"]
    for edge in visible_edges:
        lines.append("  "+ids[edge["from"]]+" -->|"+safe(edge["type"])+
                     "| "+ids[edge["to"]])
    lines += ["~~~", "", "## Accessible textual navigation", "",
              "Unconnected groups remain unconnected. No inferred CoSeed links.",
              "", "### Evidence fronts"]
    for f in frontier["fronts"]:
        gate = (f.get("next_gate") or "unknown").replace("\n", " ")
        lines.append("- "+f["id"]+" : "+f["status"]+"; gate: "+gate[:170])
    lines += ["", "### CoLens public media WorkID: "+checked["work_id"]]
    for item in public:
        links = [e["type"]+" "+e["to"] for e in visible_edges
                 if e["from"] == item["id"]]
        lines.append("- "+item["id"]+" ("+item["kind"]+"): "+
                     (item.get("label") or item["kind"])+
                     "; relations: "+("; ".join(links) or "none"))
    lines += ["", "### Retrospective candidates / no semantic assertions"]
    for x in current[:DISPLAY_LIMIT]:
        p = x["source_path"]
        lines.append("- ["+p+"]("+
                     "https://github.com/CoCivium/CoCivium/blob/main/"+p+
                     ") : SHA-256 "+x["sha256"]+"; unreviewed")
    lines += ["", "Additional public candidates omitted from this VIEW: "+
              str(max(0, len(current)-DISPLAY_LIMIT))+
              "; retained in the bounded machine index.",
              "Verified CoSeed/CoPath inspiration links: ZERO.",
              "Independent X2 receiver ACK: NOT ESTABLISHED.",
              "All historical media covered: NOT ESTABLISHED.", ""]
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--frontier", default=
                   "docs/Evolution/FRONTIER_EVIDENCE_INDEX_R0.json")
    p.add_argument("--media", default=
                   "examples/colensmedia/relational_media_fixture_r0.json")
    p.add_argument("--index-out", required=True)
    p.add_argument("--atlas-out", required=True)
    args = p.parse_args()
    root = Path(args.root).resolve()
    scan = inventory(root, tracked_public_paths(root))
    frontier = json.loads((root/args.frontier).read_text(encoding="utf-8"))
    media = json.loads((root/args.media).read_text(encoding="utf-8"))
    diagram = atlas(frontier, media, scan)
    destinations = (Path(args.index_out), Path(args.atlas_out))
    if destinations[0] == destinations[1] or any(d.exists() for d in destinations):
        raise SystemExit("HOLD_NO_CLOBBER")
    for d in destinations:
        d.parent.mkdir(parents=True, exist_ok=True)
    destinations[0].write_text(json.dumps(scan, sort_keys=True, indent=2)+"\n",
                               encoding="utf-8")
    destinations[1].write_text(diagram, encoding="utf-8")
    print(json.dumps({
        "state": "PUBLIC_SOURCE_CANDIDATES_SCANNED",
        "count": len(scan["current_source_keys"]),
        "semantic_coverage": scan["semantic_coverage"],
        "atlas_sha256": sha(diagram.encode("utf-8")),
        "receiver_ack": False,
        "private_or_unmounted_history": "NOT_DISCOVERED",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
