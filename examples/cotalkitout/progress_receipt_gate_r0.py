"""CoGoAll unattended-progress receipt gate R0.

A scheduler tick is not a work effect. Classify source-bound evidence and
fail closed when NO_UPDATE hides unchecked work or missing provenance.
Pure deterministic classifier, no agent execution or new authority.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

Disposition = Literal["VERIFIED_PROGRESS", "VERIFIED_NO_DELTA",
                      "WAITING_ON_EVENT", "NO_PROGRESS_EVIDENCE", "AWAITING_RECEIVER_PROOF"]

@dataclass(frozen=True)
class Pulse:
    work_id: str
    source_revision: str
    observed_at_utc: str
    wake_id: str
    source_checked: bool
    due_work: bool
    eligible_work: bool
    execution_attempted: bool
    output_digest: str = ""
    effect_receipt: str = ""
    receiver_readback: str = ""
    next_wake: str = ""
    blocked_reason: str = ""
    claimed_no_update: bool = False

def classify(p: Pulse) -> dict:
    if not p.wake_id or not p.work_id or not p.source_revision or not p.observed_at_utc:
        return {"disposition": "NO_PROGRESS_EVIDENCE", "reason": "UNBOUND_WAKE_OR_SOURCE"}
    if not p.source_checked:
        return {"disposition": "NO_PROGRESS_EVIDENCE", "reason": "SOURCE_NOT_CHECKED"}
    if p.execution_attempted:
        if not p.output_digest or not p.effect_receipt:
            return {"disposition": "NO_PROGRESS_EVIDENCE", "reason": "EXECUTION_NO_RECEIPT"}
        if not p.receiver_readback:
            return {"disposition": "AWAITING_RECEIVER_PROOF", "reason": "EFFECT_NOT_INDEPENDENTLY_READ"}
        return {"disposition": "VERIFIED_PROGRESS", "reason": "SOURCE_AND_RECEIVER_BOUND"}
    if p.eligible_work:
        return {"disposition": "NO_PROGRESS_EVIDENCE", "reason": "ELIGIBLE_WORK_UNATTEMPTED"}
    if p.due_work and not p.blocked_reason:
        return {"disposition": "NO_PROGRESS_EVIDENCE", "reason": "DUE_WORK_UNACCOUNTED"}
    if not p.next_wake:
        return {"disposition": "NO_PROGRESS_EVIDENCE", "reason": "NO_NEXT_WAKE"}
    if p.due_work:
        return {"disposition": "WAITING_ON_EVENT", "reason": p.blocked_reason}
    return {"disposition": "VERIFIED_NO_DELTA", "reason": "CURRENT_SOURCE_NO_ELIGIBLE_DELTA"}

if __name__ == "__main__":
    from dataclasses import asdict
    import json
    # A synthetic, source-qualified no-change input, NOT a real scheduler receipt.
    example = Pulse(work_id="fixture:one",source_revision="fixture:sha",
                    observed_at_utc="2026-11-08T22:35:00Z",wake_id="fixture:wake",
                    source_checked=True,due_work=False,eligible_work=False,
                    execution_attempted=False,next_wake="fixture:external-event",
                    claimed_no_update=True)
    print(json.dumps({"synthetic_fixture_only":True,"input":asdict(example),
                      "result":classify(example)},sort_keys=True))
