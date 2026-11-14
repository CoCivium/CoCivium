"""Read-only CoPreGeneric public source graph consistency validator.

Checks graph links, source roots, semantic nonclaims.  It does not fetch
external receivers, deploy apps, mutate files, or certify canon.
"""
from __future__ import annotations
from pathlib import Path
import json

FEDERATION = "ai/copre-seed-path-federation-r0.json"
FABRIC = "ai/copre-seed-path-fabric-r0-20261109.json"
INDEX = "ai/index.json"
REQUIRED_NONCLAIMS = {"NO_INDEPENDENT_RECEIVER_PICKUP", "NO_THREE_WAY_MIRROR", "NO_CANON_PROMOTION"}

def validate(root: Path) -> dict:
    root = Path(root).resolve()
    fed = json.loads((root / FEDERATION).read_text(encoding="utf-8"))
    fabric = json.loads((root / FABRIC).read_text(encoding="utf-8"))
    idx = json.loads((root / INDEX).read_text(encoding="utf-8"))
    if fed.get("schema") != "CoAll.CoPreGeneric.SeedPathFederation.R0":
        raise ValueError("HOLD_FEDERATION_SCHEMA")
    if fabric.get("schema") != "CoAll.CoSeedCoPathFabric.R0-candidate":
        raise ValueError("HOLD_FABRIC_SCHEMA")
    if not REQUIRED_NONCLAIMS.issubset(set(fed.get("nonclaims", []))):
        raise ValueError("HOLD_NONCLAIMS")
    if fed["coseed"]["qualified_semantic_head"] != "UNDETERMINED":
        raise ValueError("HOLD_UNQUALIFIED_CANON_HEAD")
    if any(x.get("status") != "UNVERIFIED_TARGET" for x in fed["elected_destinations"]):
        raise ValueError("HOLD_UNVERIFIED_MIRROR_PROMOTION")
    refs = [fed["root"]["temporary_entry"],fed["root"]["public_bootstrap"],
            fed["root"]["machine_index"],fed["coseed"]["landing"],fed["copath"]["entry"]]
    refs += [x["path"] for x in fed["coseed"]["candidates"]]
    refs += [x["path"] for x in fed["copath"]["paths"] if x["path"] is not None]
    refs += [x["path"] for x in fabric["nodes"]]
    ids = [x["id"] for x in fabric["nodes"]]
    if len(ids) != len(set(ids)):
        raise ValueError("HOLD_DUPLICATE_GRAPH_NODE")
    missing_relations = sorted(set(rel for x in fabric["nodes"] for rel in x["relations"]) - set(ids))
    if missing_relations:
        raise ValueError("HOLD_DANGLING_RELATION: "+",".join(missing_relations))
    for ref in refs:
        if not isinstance(ref,str) or ref.startswith("/") or "\\" in ref or ".." in Path(ref).parts:
            raise ValueError("HOLD_UNSAFE_PUBLIC_PATH")
        target=(root/ref).resolve()
        if not target.is_relative_to(root) or not target.is_file():
            raise ValueError("HOLD_MISSING_PUBLIC_PATH: "+ref)
    indexed={x.get("path") for x in idx["current_surfaces"]}
    if FEDERATION not in indexed or FABRIC not in indexed or fed["root"]["temporary_entry"] not in indexed:
        raise ValueError("HOLD_NOT_DISCOVERABLE")
    if fabric["coverage"]["private_source_census"] != "NOT_RUN":
        raise ValueError("HOLD_UNPROVEN_PRIVATE_CENSUS")
    return {"state":"PUBLIC_SOURCE_GRAPH_LINKS_VERIFIED_NOT_RECEIVER_ACK",
            "graph_files_checked":2,"distinct_paths_checked":len(set(refs)),
            "missing_paths":0,"dangling_relations":0,
            "external_receiver_readproof":"NOT_OBSERVED","canon":"NOT_CERTIFIED"}


def route_from_entry(root: Path, target_id: str, *, max_hops: int = 32) -> dict:
    """Discover a traceable directed-or-reverse path, never invent reciprocal writes.

    Traversing a reverse source link is a *reader navigation option*, not
    evidence of reciprocal delivery, integration or permission.
    """
    if not isinstance(target_id,str) or not target_id or not 0 <= max_hops <= 32:
        raise ValueError("HOLD_INVALID_ROUTE_REQUEST")
    validate(root)
    fabric=json.loads((Path(root)/FABRIC).read_text(encoding="utf-8"))
    nodes={n["id"]:n for n in fabric["nodes"]}
    if target_id not in nodes:
        return {"state":"HELD_UNKNOWN_TARGET","target":target_id,"hops":[]}
    entry="copre-entry"
    pending=[(entry, [])]
    visited={entry}
    for current,path in pending:
        if current==target_id:
            return {"state":"PUBLIC_SOURCE_NAVIGATION_ONLY","target":target_id,
                    "hops":path,"independent_pickup":False,"authority_granted":False}
        if len(path)>=max_hops:
            continue
        forward=[(rel,"FORWARD_DECLARED") for rel in nodes[current]["relations"]]
        reverse=[(n["id"],"REVERSE_DERIVED") for n in fabric["nodes"] if current in n["relations"]]
        for next_id,kind in sorted(forward+reverse):
            if next_id not in visited:
                visited.add(next_id)
                pending.append((next_id,path+[{"from":current,"to":next_id,"traversal":kind,
                                             "source_path":nodes[next_id]["path"]}]))
    return {"state":"HELD_UNREACHABLE_OR_HOP_LIMIT","target":target_id,"hops":[]}


if __name__ == "__main__":
    print(json.dumps(validate(Path(__file__).resolve().parents[1]),sort_keys=True))
