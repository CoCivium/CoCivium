"""CoMap/CoNav R0: recursive diagram-of-diagrams from typed existing artifacts.

Structural navigation only, not live telemetry or authorization. Media capture
is an opt-in lineage proposal; private material is never silently published.
"""
from dataclasses import dataclass
from typing import Tuple
from media_relation_graph_r0 import Artifact, Relation, audit


@dataclass(frozen=True)
class MapNode:
    node_id: str
    label: str
    artifact_ids: Tuple[str, ...] = ()
    child_ids: Tuple[str, ...] = ()
    scope: str = "PUBLIC"


@dataclass(frozen=True)
class Inspiration:
    source_artifact_id: str
    proposed_target_id: str
    rationale: str
    author_scope: str = "PRIVATE"
    authorized: bool = False
    evidence_ref: str = ""


def validate_map(nodes: Tuple[MapNode, ...], artifacts: Tuple[Artifact, ...],
                 relations: Tuple[Relation, ...]):
    graph = audit(artifacts, relations)
    errors = list(graph["errors"])
    known = {a.artifact_id: a for a in artifacts}
    node_index = {}
    for node in nodes:
        if not node.node_id or node.node_id in node_index:
            errors.append(("DUPLICATE_OR_MISSING_MAP_NODE", node.node_id))
        if node.scope not in ("PUBLIC", "RESTRICTED"):
            errors.append(("INVALID_MAP_SCOPE", node.node_id))
        node_index[node.node_id] = node
    for node in nodes:
        for artifact_id in node.artifact_ids:
            if artifact_id not in known:
                errors.append(("MISSING_ARTIFACT", node.node_id))
            elif node.scope == "PUBLIC" and known[artifact_id].scope == "RESTRICTED":
                errors.append(("PRIVATE_ARTIFACT_IN_PUBLIC_MAP", node.node_id))
        for child_id in node.child_ids:
            if child_id not in node_index:
                errors.append(("MISSING_CHILD_MAP", node.node_id))
            elif node.scope == "PUBLIC" and node_index[child_id].scope == "RESTRICTED":
                errors.append(("PRIVATE_CHILD_IN_PUBLIC_MAP", node.node_id))

    visiting, visited = set(), set()
    def walk(node_id):
        if node_id in visiting:
            errors.append(("RECURSIVE_CYCLE", node_id))
            return
        if node_id in visited:
            return
        visiting.add(node_id)
        for child_id in node_index[node_id].child_ids:
            if child_id in node_index:
                walk(child_id)
        visiting.remove(node_id)
        visited.add(node_id)
    for node_id in sorted(node_index):
        walk(node_id)
    return {"verdict": "HOLD" if errors else "STRUCTURALLY_VALID",
            "errors": sorted(set(errors)),
            "semantic_validation": "NOT_PROVEN",
            "runtime_navigation": "NOT_PROVEN"}


def nested_projection(nodes, artifacts, relations, *, root_id):
    """A small machine-readable view for a renderer, with no hidden children."""
    state = validate_map(nodes, artifacts, relations)
    if state["errors"]:
        raise ValueError("map contains invalid or private references")
    index = {node.node_id: node for node in nodes}
    if root_id not in index:
        raise ValueError("unknown root")
    def branch(node_id):
        node = index[node_id]
        return {"id": node.node_id, "label": node.label,
                "artifacts": list(node.artifact_ids),
                "children": [branch(child) for child in node.child_ids]}
    return {"schema": "CoMap.NestedNavigation.R0", "root": branch(root_id),
            "evidence": "STRUCTURAL_ONLY_NOT_X2_RUNTIME"}


def classify_inspiration(item, artifacts):
    """Never convert visual similarity into source ownership or distribution."""
    index = {a.artifact_id: a for a in artifacts}
    if item.source_artifact_id not in index:
        return "SOURCE_MISSING"
    if not item.proposed_target_id or not item.rationale:
        return "INCOMPLETE_PROPOSAL"
    if not item.authorized:
        return "PRIVATE_INSPIRATION_PROPOSED"
    if index[item.source_artifact_id].scope == "RESTRICTED":
        return "RESTRICTED_SOURCE_REVIEW"
    if not item.evidence_ref:
        return "NO_PROVENANCE"
    return "ELIGIBLE_FOR_REVIEW_NOT_PUBLISHED"
