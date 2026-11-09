#!/usr/bin/env python3
"""Bounded public-source continuity audit. No network, messages, or receiver claims.

Keep existing CoGoAll/AI onramps and the evolution lane index discoverable.
This tool tests source paths, not delivery, semantic adoption, or deployed UX.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

HUBS = (
    "docs/Onramp/COGOALL_PUBLIC_REBOUND_HUB_20261108.md",
    "docs/Onramp/AI_ONRAMP_CATCHUP_HUB_20261108.md",
)
INDEX = "ai/index.json"
LANES = "ai/evolution-lanes.json"
CORE_LINKS = {
    HUBS[0]: (
        HUBS[1], INDEX, LANES, "SESSION_BOOTSTRAP.md",
        "docs/Operations/COGOALL_OUTSTANDING_REGISTER_20261108.md",
    ),
    HUBS[1]: (HUBS[0],),
}
LINK = re.compile(r"\]\(([^)]+)\)")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _relative(root: Path, item: Path) -> str:
    try:
        return item.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError("SOURCE_OUTSIDE_REPOSITORY") from exc


def resolve_local(root: Path, base: Path, raw: str) -> Path | None:
    """Return a path under the source checkout, or None for external/anchors."""
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("EMPTY_SOURCE_LOCATOR")
    ref = raw.strip().split(None, 1)[0]
    if ref.startswith("#"):
        return None
    parsed = urlsplit(ref)
    if parsed.scheme or parsed.netloc or ref.startswith("//"):
        return None
    target = unquote(parsed.path)
    if not target:
        return None
    if target.startswith("/") or "\\" in target or "\x00" in target:
        raise ValueError("UNSAFE_REPOSITORY_LOCATOR")
    location = (base.parent / target).resolve()
    _relative(root, location)
    return location


def audit(root: Path) -> dict:
    root = root.resolve()
    violations: list[str] = []
    missing: set[str] = set()
    inspected: dict[str, str] = {}
    local_links = 0
    targets: set[str] = set()
    link_by_hub: dict[str, set[str]] = {}

    for name in HUBS:
        path = root / name
        if not path.is_file():
            violations.append("MISSING_HUB:" + name)
            continue
        content = path.read_bytes()
        inspected[name] = sha256(content)
        seen: set[str] = set()
        for raw in LINK.findall(content.decode("utf-8")):
            try:
                item = resolve_local(root, path, raw)
            except ValueError as exc:
                violations.append(name + ":" + str(exc))
                continue
            if item is None:
                continue
            target = _relative(root, item)
            seen.add(target)
            local_links += 1
            targets.add(target)
            if not item.exists():
                missing.add(target)
        link_by_hub[name] = seen

    for hub, needed in CORE_LINKS.items():
        for target in needed:
            if target not in link_by_hub.get(hub, set()):
                violations.append("MISSING_CROSS_LINK:" + hub + "->" + target)

    surface_count = 0
    index_path = root / INDEX
    if not index_path.is_file():
        missing.add(INDEX)
    else:
        inspected[INDEX] = sha256(index_path.read_bytes())
        try:
            index = json.loads(index_path.read_text(encoding="utf-8"))
            surfaces = index["current_surfaces"]
            if not isinstance(surfaces, list) or not surfaces:
                raise ValueError("MISSING_MACHINE_SURFACES")
            identities: set[str] = set()
            for entry in surfaces:
                if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not entry["id"]:
                    raise ValueError("INVALID_SURFACE_ID")
                if entry["id"] in identities:
                    raise ValueError("DUPLICATE_SURFACE_ID")
                identities.add(entry["id"])
                if not isinstance(entry.get("path"), str):
                    raise ValueError("INVALID_SURFACE_PATH")
                item = resolve_local(root, root / "index-parent", entry["path"])
                if item is None:
                    raise ValueError("MISSING_SURFACE_PATH")
                target = _relative(root, item)
                if not item.exists():
                    missing.add(target)
                surface_count += 1
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            violations.append("MACHINE_INDEX_INVALID:" + str(exc))

    domain_count = 0
    lanes_path = root / LANES
    if not lanes_path.is_file():
        missing.add(LANES)
    else:
        inspected[LANES] = sha256(lanes_path.read_bytes())
        try:
            lane_data = json.loads(lanes_path.read_text(encoding="utf-8"))
            domains = lane_data["domains"]
            if not isinstance(domains, list) or not domains:
                raise ValueError("EMPTY_EVOLUTION_LANES")
            domain_keys: set[str] = set()
            for row in domains:
                if (not isinstance(row, list) or len(row) != 3
                    or not isinstance(row[0], str) or not row[0].strip()
                    or not isinstance(row[1], list) or not row[1]
                    or not all(isinstance(x, str) and x.strip() for x in row[1])
                    or not isinstance(row[2], str) or not row[2].strip()):
                    raise ValueError("INVALID_EVOLUTION_LANE")
                if row[0] in domain_keys:
                    raise ValueError("DUPLICATE_EVOLUTION_LANE")
                domain_keys.add(row[0])
                domain_count += 1
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            violations.append("EVOLUTION_LANES_INVALID:" + str(exc))

    state = "SOURCE_LINKS_VALIDATED_ONLY" if not missing and not violations else "SOURCE_CONTINUITY_HOLD"
    return {
        "schema": "CoAll.ReboundIntegrity.R0",
        "state": state,
        "coverage": {
            "hubs_inspected": sum(h in inspected for h in HUBS),
            "local_link_occurrences": local_links,
            "unique_local_targets": len(targets),
            "indexed_machine_surfaces": surface_count,
            "declared_evolution_lanes": domain_count,
            "full_historical_coverage": False,
        },
        "source_sha256": dict(sorted(inspected.items())),
        "missing_local_targets": sorted(missing),
        "violations": sorted(violations),
        "nonclaims": [
            "SOURCE_LINK_NE_RECEIVER_ACK",
            "REGISTERED_LANE_NE_RUNNING_WORKER",
            "VALIDATION_NE_SEMANTIC_ADOPTION",
            "NO_RUNTIME_OR_X2_CLAIM",
            "PUBLIC_SOURCE_NE_CROSS_SESSION_SYNC",
            "DISCOVERED_LINKS_NE_COMPLETE_HISTORY",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.root)
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        if args.output.exists():
            raise SystemExit("FAIL_CLOSED_NO_CLOBBER")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(json.dumps({"state": result["state"], "coverage": result["coverage"],
                      "missing": len(result["missing_local_targets"]),
                      "violations": len(result["violations"])}, sort_keys=True))
    return 0 if result["state"] == "SOURCE_LINKS_VALIDATED_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
