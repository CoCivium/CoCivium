"""CoTalkItOut+ R0: bounded peer decision policy for durable work objects.

Advisory-only. Does not spawn provider sessions, invoke models, run tools,
claim receiver ACK, grant privileges, or mutate native rickBar/X2.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

Verdict = Literal["ACT_PROPOSAL", "CHALLENGE", "HOLD", "ESCALATE", "QUIET"]
VALID_EVIDENCE = {"SOURCE_LANDED", "CI_PASS", "RECEIVER_ACK", "RUNTIME_EFFECT"}
MAX_PEERS = 12
MAX_ROUNDS = 3

@dataclass(frozen=True)
class Proposal:
    peer: str
    option: str
    evidence_ref: str
    evidence_class: str
    risk: str = "REVERSIBLE"
    claimed_verifier: str = ""

@dataclass(frozen=True)
class Work:
    work_id: str
    source_revision: str
    blocker: str
    options: tuple[Proposal, ...]
    prior_rounds: int = 0
    budget_remaining: int = 1
    external_change: bool = False
    independent_ack: bool = False
    elected_actuator: str = ""
    authority_present: bool = False

def decide(work: Work) -> dict:
    """Choose one next *recommendation*, preserving dissent and proof boundaries.

    ACT_PROPOSAL means recommended bounded action, never physical execution.
    All unsafe conflicting effects remain human/authorized-receiver gated.
    """
    if not work.work_id or not work.source_revision:
        raise ValueError("MISSING_WORK_OR_SOURCE")
    if len(work.options) > MAX_PEERS or work.prior_rounds < 0 or work.budget_remaining < 0:
        raise ValueError("INVALID_BOUNDS")
    if any(not p.peer or not p.option or not p.evidence_ref or
           p.evidence_class not in VALID_EVIDENCE or
           p.risk not in {"READ_ONLY", "REVERSIBLE", "IRREVERSIBLE"} for p in work.options):
        raise ValueError("UNBOUND_PROPOSAL")
    if len({p.peer for p in work.options}) != len(work.options):
        raise ValueError("DUPLICATE_PEER")
    disagreement = len({p.option for p in work.options}) > 1
    receipts = sorted({p.evidence_ref for p in work.options})
    base = dict(work_id=work.work_id, source_revision=work.source_revision,
                receipts=receipts, disagreement=disagreement,
                no_effect_executed=True, receiver_ack="PROVEN" if work.independent_ack else "UNPROVEN")
    if work.blocker in {"NO_AUTHORIZED_RECEIVER", "MISSING_CONSENT", "NO_NATIVE_ROLLBACK"}:
        return dict(base, verdict="HOLD", reason=work.blocker, next_trigger="AUTHENTICATED_CAPABILITY_CHANGE")
    if any(p.risk == "IRREVERSIBLE" for p in work.options) and not work.authority_present:
        return dict(base, verdict="ESCALATE", reason="REAL_AUTHORITY_REQUIRED", next_trigger="AUTHORIZATION")
    if not work.options:
        return dict(base, verdict="QUIET", reason="NO_SUPPORTED_DELTA", next_trigger="NEW_SOURCE_OR_EVENT")
    if work.budget_remaining == 0 or work.prior_rounds >= MAX_ROUNDS:
        return dict(base, verdict="HOLD", reason="BOUNDED_DISCUSSION_EXHAUSTED", next_trigger="NEW_EVIDENCE")
    if disagreement:
        if not work.external_change and work.prior_rounds > 0:
            return dict(base, verdict="QUIET", reason="UNCHANGED_DISAGREEMENT", next_trigger="NEW_EVIDENCE")
        return dict(base, verdict="CHALLENGE", reason="DISAGREEMENT_NEEDS_DISCRIMINATING_TEST",
                    next_trigger="ONE_BOUNDED_INDEPENDENT_TEST")
    # One elected actuator is necessary for any planned effect. No session elected by label.
    if not work.elected_actuator or work.elected_actuator not in {p.peer for p in work.options}:
        return dict(base, verdict="HOLD", reason="NO_VALID_FENCED_ACTUATOR", next_trigger="LEASE_ELECTION")
    return dict(base, verdict="ACT_PROPOSAL", reason="ONE_BOUNDED_REVIEWED_OPTION",
                next_trigger="EFFECT_AND_INDEPENDENT_READBACK_REQUIRED")

def projection(decision: dict) -> dict:
    """Minimal one-rail rickBar projection from a validated decision, not its runtime."""
    if decision["verdict"] not in {"ACT_PROPOSAL","CHALLENGE","HOLD","ESCALATE","QUIET"}:
        raise ValueError("UNKNOWN_VERDICT")
    return {"work_id":decision["work_id"], "state":decision["verdict"],
            "reason":decision["reason"], "next_trigger":decision["next_trigger"],
            "source_revision":decision["source_revision"],
            "evidence_count":len(decision["receipts"]),
            "dissent":decision["disagreement"],
            "receiver_ack":decision["receiver_ack"],
            "native_effect":False}
