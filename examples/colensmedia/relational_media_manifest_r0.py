#!/usr/bin/env python3
"""CoSourceGraph/CoLens media-relationship source projection, R0.

Pure metadata graph; no media fetching, email reading, public posting, model
execution, runtime synchronization, or automatic revision of downstream work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

SHA = re.compile(r"[0-9a-f]{64}\Z")
SAFE_ID = re.compile(r"[a-zA-Z0-9_:.-]{1,128}\Z")
KINDS = {"SOURCE", "DIAGRAM", "AUDIO", "VIDEO", "ARTICLE", "EMAIL_DRAFT",
         "ORB_VIEW", "ACCESSIBLE_TEXT", "RECEIPT", "COUNTEREXAMPLE"}
EDGE_TYPES = {"DERIVED_FROM", "SUPERSEDES", "CHALLENGES", "DESCRIBES",
              "RELATED_TO", "INTENTIONALLY_UNRELATED"}
PARENT_EDGES = {"DERIVED_FROM", "SUPERSEDES"}
PROJECTION_KINDS = {"DIAGRAM", "AUDIO", "VIDEO", "ARTICLE", "EMAIL_DRAFT", "ORB_VIEW"}
RICH_MEDIA = {"DIAGRAM", "AUDIO", "VIDEO"}
NONCLAIMS = ("SOURCE_GRAPH_NE_RUNTIME_SYNC", "DERIVATIVE_NE_CANON",
             "METADATA_RELATION_NE_RECEIVER_ACK", "VISUAL_EDGE_NE_CAUSAL_PROOF",
             "PRIVATE_CONTENT_NE_PUBLIC_SOURCE", "PROPOSED_REVISION_NE_PUBLISHED_UPDATE")


def canonical(obj):
    return json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def audit(manifest):
    if not isinstance(manifest, dict) or manifest.get("schema") != "CoAll.RelationalMediaManifest.R0":
        raise ValueError("BAD_MEDIA_SCHEMA")
    work_id = manifest.get("work_id")
    root_id = manifest.get("root_id")
    nodes, edges = manifest.get("assets"), manifest.get("relations")
    if not isinstance(work_id, str) or not work_id or not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("INVALID_MEDIA_GRAPH")
    if not isinstance(root_id, str) or not SAFE_ID.fullmatch(root_id):
        raise ValueError("INVALID_ROOT_ID")
    if len(nodes) > 100 or len(edges) > 300:
        raise ValueError("GRAPH_BUDGET_EXCEEDED")

    found = {}
    for item in nodes:
        if not isinstance(item, dict):
            raise ValueError("INVALID_ASSET")
        ident, typ = item.get("id"), item.get("kind")
        if not isinstance(ident, str) or not SAFE_ID.fullmatch(ident) or typ not in KINDS:
            raise ValueError("INVALID_ASSET_ID_OR_KIND")
        if ident in found:
            raise ValueError("DUPLICATE_ASSET_ID")
        if item.get("work_id") != work_id:
            raise ValueError("MIXED_WORK_IDS")
        if not isinstance(item.get("source_revision"), str) or not item["source_revision"]:
            raise ValueError("MISSING_SOURCE_REVISION")
        if not isinstance(item.get("sha256"), str) or not SHA.fullmatch(item["sha256"]):
            raise ValueError("INVALID_ASSET_HASH")
        if item.get("visibility") not in ("PUBLIC", "PRIVATE"):
            raise ValueError("INVALID_VISIBILITY")
        if type(item.get("current", False)) is not bool:
            raise ValueError("INVALID_CURRENT_FLAG")
        if item.get("isolation_reason") is not None and not str(item["isolation_reason"]).strip():
            raise ValueError("INVALID_ISOLATION_REASON")
        if item.get("label") is not None and (not isinstance(item["label"], str) or
                len(item["label"]) > 64 or not re.fullmatch(r"[a-zA-Z0-9 +:/.-]+", item["label"])):
            raise ValueError("UNSAFE_DISPLAY_LABEL")
        found[ident] = item

    if root_id not in found or found[root_id]["kind"] != "SOURCE":
        raise ValueError("MISSING_SOURCE_ROOT")
    if sum(node["kind"] == "SOURCE" for node in nodes) != 1:
        raise ValueError("AMBIGUOUS_SOURCE_ROOT")
    current_source = found[root_id]["source_revision"]
    parent_links = {x: [] for x in found}
    relations_seen = set()
    for edge in edges:
        if not isinstance(edge, dict) or edge.get("type") not in EDGE_TYPES:
            raise ValueError("INVALID_RELATION_TYPE")
        src, dst, kind = edge.get("from"), edge.get("to"), edge["type"]
        if src not in found or dst not in found:
            raise ValueError("MISSING_RELATION_ENDPOINT")
        if src == dst:
            raise ValueError("SELF_RELATION")
        if not isinstance(edge.get("evidence_ref"), str) or not edge["evidence_ref"].strip():
            raise ValueError("MISSING_RELATION_EVIDENCE")
        key = (src, dst, kind)
        if key in relations_seen:
            raise ValueError("DUPLICATE_RELATION")
        relations_seen.add(key)
        if kind in PARENT_EDGES:
            parent_links[src].append(dst)
            if found[src]["visibility"] == "PUBLIC" and found[dst]["visibility"] == "PRIVATE":
                raise ValueError("PUBLIC_DERIVED_FROM_PRIVATE")

    if parent_links[root_id]:
        raise ValueError("SOURCE_ROOT_HAS_PARENT")

    # Depth-limited DFS classifies exact lineage, not mere association.
    visiting, visited, connected = set(), set(), {}
    def reaches_root(key):
        if key == root_id:
            return True
        if key in visiting:
            raise ValueError("DERIVATION_CYCLE")
        if key in visited:
            return connected[key]
        visiting.add(key)
        route = False
        for parent in parent_links[key]:
            if reaches_root(parent):
                route = True
        visiting.remove(key)
        visited.add(key)
        connected[key] = route
        return route

    orphans, intentional, stale, a11y = [], [], [], []
    for key, item in found.items():
        if key == root_id:
            continue
        if not reaches_root(key):
            if item.get("isolation_reason"):
                intentional.append(key)
            else:
                orphans.append(key)
        if item.get("current", False) and item["source_revision"] != current_source:
            stale.append(key)
        if item["kind"] in RICH_MEDIA and item.get("current", False):
            twin = item.get("accessibility_twin_id")
            if twin not in found or found[twin]["kind"] != "ACCESSIBLE_TEXT":
                a11y.append(key)
            elif found[twin]["source_revision"] != item["source_revision"]:
                a11y.append(key)

    return {
        "schema": "CoAll.RelationalMediaAudit.R0",
        "work_id": work_id,
        "root_id": root_id,
        "source_revision": current_source,
        "manifest_sha256": sha(canonical(manifest).encode("utf-8")),
        "state": "SOURCE_GRAPH_CANDIDATE_CLEAN" if not (orphans or stale or a11y) else "SOURCE_GRAPH_REVIEW_REQUIRED",
        "asset_count": len(nodes),
        "relation_count": len(edges),
        "orphan_asset_ids": sorted(orphans),
        "intentionally_isolated_asset_ids": sorted(intentional),
        "stale_current_asset_ids": sorted(stale),
        "accessibility_gap_asset_ids": sorted(a11y),
        "nonclaims": list(NONCLAIMS),
    }


def render_markdown(manifest):
    """A deterministic graph and accessible textual twin from the SAME manifest."""
    report = audit(manifest)
    # Public projection must neither list private nodes nor expose full-graph
    # digests/counts that change solely when hidden private state changes.
    public_assets = [n for n in manifest["assets"] if n["visibility"] == "PUBLIC"]
    public_ids = {n["id"] for n in public_assets}
    public_relations = [e for e in manifest["relations"]
                        if e["from"] in public_ids and e["to"] in public_ids]
    projection_sha = sha(canonical({"work_id": report["work_id"],
                                    "root_id": report["root_id"],
                                    "assets": public_assets,
                                    "relations": public_relations}).encode("utf-8"))
    tick = chr(96)
    lines = ["# Relational media view R0", "",
             "**SOURCE-ONLY SYNTHETIC PROJECTION. NOT A SENT EMAIL OR LIVE WORKER.**", "",
             "WorkID: " + tick + report["work_id"] + tick, "Source revision: " + tick + report["source_revision"] + tick,
             "Public projection SHA-256: " + tick + projection_sha + tick, "",
             tick*3 + "mermaid", "flowchart TD"]
    ids = {n["id"]: "N" + str(i) for i, n in enumerate(public_assets)}
    for item in public_assets:
        label = item.get("label") or item["kind"].title()
        lines.append("    " + ids[item["id"]] + '["' + label + '"]')
    for edge in public_relations:
        lines.append("    " + ids[edge["from"]] + " -->|" + edge["type"] + "| " + ids[edge["to"]])
    lines.extend([tick*3, "", "## Accessible text equivalent", ""])
    for item in public_assets:
        related = [edge["type"] + " " + edge["to"] for edge in public_relations
                   if edge["from"] == item["id"]]
        lines.append("- " + tick + item["id"] + tick + " (" + item["kind"] + ", " + item["visibility"] +"): " +
                     (item.get("label") or "asset") + "; " + ("; ".join(related) or "no outgoing relation"))
    visible_orphans = [k for k in report["orphan_asset_ids"] if k in public_ids]
    visible_stale = [k for k in report["stale_current_asset_ids"] if k in public_ids]
    lines.extend(["", "## Evidence ceiling", "",
                  "- Public orphans: " + (", ".join(visible_orphans) or "none in this fixture"),
                  "- Stale public projections: " + (", ".join(visible_stale) or "none in this fixture"),
                  "- Receiver ACK: NOT ESTABLISHED", "- Media bytes or semantic parity: NOT TESTED", ""])
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", type=Path, required=True)
    ap.add_argument("--diagram", type=Path, required=True)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    manifest = json.loads(args.fixture.read_text(encoding="utf-8"))
    diagram = render_markdown(manifest)
    if args.check:
        if not args.diagram.is_file() or args.diagram.read_text(encoding="utf-8") != diagram:
            raise SystemExit("HOLD_DIAGRAM_OUT_OF_SYNC")
    else:
        if args.diagram.exists():
            raise SystemExit("HOLD_NO_CLOBBER")
        args.diagram.write_text(diagram, encoding="utf-8")
    print(json.dumps(audit(manifest), sort_keys=True))


if __name__ == "__main__":
    main()
