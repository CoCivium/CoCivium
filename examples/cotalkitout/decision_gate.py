"""CoTalkItOut R0: bounded decision gate, not autonomous authority or multi-agent runtime."""
from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class Proposal:
    work_id: str
    decision_id: str
    source_refs: Tuple[str, ...]
    alternatives: Tuple[str, ...]
    objections: Tuple[str, ...]
    experiment: str
    effect: str
    authorized_effects: Tuple[str, ...]
    evidence_refs: Tuple[str, ...] = ()
    verified_result: bool = False

def route(proposal: Proposal, verified_evidence=()):
    """Return a decision classification without executing any requested effect."""
    if not proposal.work_id or not proposal.decision_id or not proposal.source_refs:
        return {"state":"HELD","reason":"identity_or_provenance_missing"}
    if len(set(proposal.alternatives)) < 2:
        return {"state":"TALK","reason":"competing_alternative_missing"}
    if proposal.objections and not proposal.experiment:
        return {"state":"TALK","reason":"objection_without_discriminating_test"}
    if proposal.effect not in proposal.authorized_effects:
        return {"state":"HELD","reason":"effect_not_authorized"}
    if not proposal.experiment and not proposal.evidence_refs:
        return {"state":"TALK","reason":"no_test_or_evidence"}
    if not proposal.verified_result:
        return {"state":"TEST","reason":"run_bounded_experiment","experiment":proposal.experiment}
    if not proposal.evidence_refs:
        return {"state":"HELD","reason":"verified_result_without_receipt"}
    # The verifier's observations are supplied separately from the proposer.
    # Matching strings alone do not prove independent receipt authenticity;
    # the caller must obtain these from its trusted verifier boundary.
    trusted = set(verified_evidence)
    if not trusted or not set(proposal.evidence_refs).issubset(trusted):
        return {"state":"HELD","reason":"independent_verifier_evidence_missing"}
    return {"state":"QUALIFIED","reason":"verified_result_with_independent_evidence",
            "receipt_refs":proposal.evidence_refs}
