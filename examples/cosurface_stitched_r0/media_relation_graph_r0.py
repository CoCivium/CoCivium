"""CoAll cross-media relation graph R0.

Pure, deterministic, stdlib-only evidence-aware index and projections.
Does not ingest mail, edit media, open tools, or assert receiver ACK.
"""
from dataclasses import dataclass
from typing import Tuple

MEDIA = frozenset({"diagram", "video", "audio", "email_draft", "email_sent",
                   "research", "code", "test", "receipt", "coorb_view"})
RELATIONS = frozenset({"DERIVED_FROM", "EXPLAINS", "DEMONSTRATES", "CHALLENGES",
                       "TESTS", "SUPERSEDES", "REFERENCES", "PROJECTS",
                       "REQUIRES", "RESPONDS_TO"})


@dataclass(frozen=True)
class Artifact:
    artifact_id: str
    kind: str
    revision: str
    source_hash: str
    scope: str = "PUBLIC"  # PUBLIC or RESTRICTED


@dataclass(frozen=True)
class Relation:
    source_id: str
    predicate: str
    target_id: str
    source_revision: str
    target_revision: str
    evidence_ref: str
    status: str = "PROPOSED"  # PROPOSED or VERIFIED


def audit(artifacts: Tuple[Artifact, ...], relations: Tuple[Relation, ...]):
    """Detect orphan risks without inventing edges or elevating self-claims."""
    index, errors = {}, []
    for a in artifacts:
        if not a.artifact_id or a.artifact_id in index:
            errors.append(("DUPLICATE_OR_MISSING_ID", a.artifact_id))
        if a.kind not in MEDIA or not a.revision or not a.source_hash:
            errors.append(("INCOMPLETE_ARTIFACT", a.artifact_id))
        if a.scope not in ("PUBLIC", "RESTRICTED"):
            errors.append(("BAD_SCOPE", a.artifact_id))
        index[a.artifact_id] = a
    connected = set()
    for e in relations:
        if e.source_id not in index or e.target_id not in index:
            errors.append(("DANGLING_EDGE", e.source_id))
            continue
        source, target = index[e.source_id], index[e.target_id]
        if e.predicate not in RELATIONS:
            errors.append(("UNTYPED_RELATION", e.source_id))
        if e.source_revision != source.revision or e.target_revision != target.revision:
            errors.append(("STALE_RELATION", e.source_id))
        if e.status not in ("PROPOSED", "VERIFIED"):
            errors.append(("INVALID_RELATION_STATUS", e.source_id))
        if e.status == "VERIFIED" and not e.evidence_ref:
            errors.append(("UNRECEIPTED_RELATION", e.source_id))
        # A public projection of restricted content needs its own approved
        # declassification/redaction evidence, not an ordinary typed edge.
        if e.predicate == "PROJECTS" and source.scope == "RESTRICTED" and target.scope == "PUBLIC":
            errors.append(("SCOPE_LEAK_CANDIDATE", e.source_id))
        connected.add(e.source_id)
        connected.add(e.target_id)
    orphans = sorted(set(index) - connected)
    return {"errors": sorted(errors), "orphans": orphans,
            "connected_count": len(connected),
            "verdict": "HOLD" if errors else "STRUCTURALLY_VALID",
            "semantic_validation": "NOT_PROVEN",
            "receiver_ack": "NOT_PROVEN"}


def diagram(artifacts: Tuple[Artifact, ...], relations: Tuple[Relation, ...]):
    """Graphviz DOT text, same IDs and relationships as machine graph."""
    checked = audit(artifacts, relations)
    if checked["errors"]:
        raise ValueError("graph not structurally valid")
    lines = ["digraph CoMediaR0 {", '  graph [label="Candidate relations, not live runtime"];']
    for a in sorted(artifacts, key=lambda x: x.artifact_id):
        label = a.kind + " " + a.artifact_id
        lines.append('  "{}" [label="{}"];'.format(a.artifact_id, label))
    for e in sorted(relations, key=lambda x: (x.source_id, x.predicate, x.target_id)):
        lines.append('  "{}" -> "{}" [label="{}:{}"];'.format(
            e.source_id, e.target_id, e.predicate, e.status))
    lines.append("}")
    return "\n".join(lines)


def fixture():
    """Synthetic research->test->diagram->outreach chain, never actual mail."""
    items = (
        Artifact("research1", "research", "r1", "sha-research"),
        Artifact("test1", "test", "r1", "sha-test"),
        Artifact("diagram1", "diagram", "r1", "sha-diagram"),
        Artifact("draft1", "email_draft", "r1", "sha-draft", "RESTRICTED"),
    )
    edges = (
        Relation("test1", "TESTS", "research1", "r1", "r1", "ci-1", "VERIFIED"),
        Relation("diagram1", "EXPLAINS", "test1", "r1", "r1", "", "PROPOSED"),
        Relation("draft1", "REFERENCES", "diagram1", "r1", "r1", "", "PROPOSED"),
    )
    return items, edges
