"""CoLUE+ immutable draft revision lineage and bounded CoEv proof gate R0.

This is purely source-only synthetic validation. It never accesses Gmail, reads
private email content, changes a draft, sends, subscribes or grants approval.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from outreach_stage_gate_r0 import DraftEvidence, evaluate

SHA = re.compile(r"[0-9a-f]{64}\Z")
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")
MAX_REVISIONS = 32


@dataclass(frozen=True)
class DraftRevision:
    work_id: str
    mailbox_id: str
    draft_id: str
    revision_id: str
    predecessor_id: str | None
    content_sha256: str
    change_reason_ref: str
    evidence_ref: str


def _required_id(value: object, kind: str) -> None:
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ValueError("HOLD_BAD_" + kind)


def analyze(revisions: tuple[DraftRevision, ...], gate: DraftEvidence) -> dict:
    """Test a single linear WorkID lineage, with no trust promotion.

    Revision provenance is caller-supplied; this is neither an authenticated
    mailbox snapshot nor a substitute for provider receipts. Parent pointers
    must form one gapless, ordered chain, including the root. That prevents
    a newer draft from silently dropping an intermediate version.
    """
    if not isinstance(revisions, tuple) or not (1 <= len(revisions) <= MAX_REVISIONS):
        raise ValueError("HOLD_REVISION_BUDGET_OR_TYPE")
    if not isinstance(gate, DraftEvidence):
        raise TypeError("DraftEvidence required")

    seen = set()
    prior = None
    for revision in revisions:
        if not isinstance(revision, DraftRevision):
            raise ValueError("HOLD_MALFORMED_REVISION")
        for name in ("work_id", "mailbox_id", "draft_id", "revision_id"):
            _required_id(getattr(revision, name), "REVISION_ID")
        for name in ("change_reason_ref", "evidence_ref"):
            _required_id(getattr(revision, name), "PROVENANCE_REF")
        if not isinstance(revision.content_sha256, str) or not SHA.fullmatch(revision.content_sha256):
            raise ValueError("HOLD_BAD_CONTENT_DIGEST")
        if revision.revision_id in seen:
            raise ValueError("HOLD_DUPLICATE_REVISION")
        seen.add(revision.revision_id)
        if (revision.work_id != gate.work_id
                or revision.mailbox_id != gate.draft_mailbox_id
                or revision.draft_id != gate.draft_id):
            raise ValueError("HOLD_MIXED_WORK_MAILBOX_OR_DRAFT")
        if prior is None:
            if revision.predecessor_id is not None:
                raise ValueError("HOLD_ROOT_HAS_PREDECESSOR")
        elif revision.predecessor_id != prior.revision_id:
            raise ValueError("HOLD_GAP_CYCLE_OR_SILENT_SUPERSESSION")
        prior = revision

    head = revisions[-1]
    stage = evaluate(gate)
    holds = list(stage["holds"])
    if gate.source_revision != head.revision_id or gate.current_source_revision != head.revision_id:
        holds.append("HOLD_UNBOUND_CURRENT_REVISION")
    if gate.content_sha256 != head.content_sha256:
        holds.append("HOLD_UNBOUND_CURRENT_CONTENT")

    # Hash the synthetic *metadata*, not message text or recipient details.
    meta = [
        {"revision_id": r.revision_id, "predecessor_id": r.predecessor_id,
         "content_sha256": r.content_sha256,
         "change_reason_ref": r.change_reason_ref, "evidence_ref": r.evidence_ref}
        for r in revisions
    ]
    lineage_digest = hashlib.sha256(
        json.dumps(meta, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    no_content_delta = (
        len(revisions) > 1
        and revisions[-1].content_sha256 == revisions[-2].content_sha256
    )
    return {
        "schema": "CoLUE.DraftRevisionLineage.R0",
        "work_id": head.work_id,
        "state": "STAGED_HELD" if holds else "SOURCE_STAGE_ELIGIBLE_NOT_SENT",
        "holds": sorted(set(holds)),
        "revision_count": len(revisions),
        "head_revision": head.revision_id,
        "head_content_sha256": head.content_sha256,
        "lineage_metadata_sha256": lineage_digest,
        "recursion_result": (
            "IDEMPOTENT_NO_CONTENT_CHANGE"
            if no_content_delta else "CONTENT_CHANGED_QUALITY_NOT_PROVEN"
        ),
        "next_safe_action": (
            sorted(set(holds))[0] if holds
            else "REQUIRE_INDEPENDENT_PROVIDER_EFFECT_AND_RECEIPT"
        ),
        "provider_effect": "NONE",
        "delivery_verified": False,
        "recipient_acceptance_verified": False,
        "evidence_status": "CALLER_SUPPLIED_SOURCE_ONLY",
        "nonclaims": [
            "DRAFT_REVISION_NE_SENT_EMAIL",
            "CONTENT_CHANGE_NE_IMPROVEMENT",
            "LINEAGE_HASH_NE_AUTHENTICATED_MAILBOX_READBACK",
            "EVALUATOR_NE_PROVIDER_AUTHORITY",
            "NO_DELIVERY_OR_RECIPIENT_ACK",
            "SENT_RECORDS_ARE_SEPARATE_IMMUTABLE_EVENTS",
        ],
    }
