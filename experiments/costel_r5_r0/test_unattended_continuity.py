"""Unattended continuity: classify evidence, not cheerful scheduler states.

Synthetic only; does not connect to an automation service or X2.
"""
from dataclasses import dataclass
import unittest


@dataclass(frozen=True)
class RunEvidence:
    work_id: str
    pending_eligible_work: int
    worker_triggered: bool
    source_revision: str = ""
    capability_probe: str = "UNPROBED"
    authority_allowed: bool = True
    duplicate_lease: bool = False
    stopped: bool = False
    receipt_refs: tuple = ()
    independent_readback: bool = False
    new_effects: int = 0
    reason: str = ""
    next_wake: str = ""


def classify(r):
    """A no_update transport status is never sufficient for progress."""
    if not r.work_id:
        return "INVALID_WORK_ID"
    if r.stopped:
        return "STOPPED"
    if r.duplicate_lease:
        return "SKIPPED_DUPLICATE"
    if not r.worker_triggered:
        return "TRIGGER_MISSING"
    if r.pending_eligible_work == 0:
        return "NO_ELIGIBLE_ACTION"
    if not r.source_revision:
        return "BLOCKED_STALE_SOURCE"
    if not r.authority_allowed:
        return "BLOCKED_AUTHORITY"
    if r.capability_probe != "READY":
        return "BLOCKED_CONNECTOR" if r.capability_probe == "OFFLINE" else "UNKNOWN_CAPABILITY"
    if r.new_effects > 0 and r.receipt_refs and r.independent_readback:
        return "VERIFIED_PROGRESS"
    if r.new_effects > 0:
        return "EFFECT_UNVERIFIED"
    if r.reason == "NO_NEW_EVIDENCE" and r.next_wake:
        return "NO_NEW_EVIDENCE"
    return "CONTINUITY_DEBT"


class ContinuityTests(unittest.TestCase):
    base = dict(work_id="work-1", pending_eligible_work=1,
                worker_triggered=True, source_revision="sha-123",
                capability_probe="READY", next_wake="scheduled-next")

    def make(self, **kwargs):
        return RunEvidence(**{**self.base, **kwargs})

    def test_no_update_with_pending_work_is_debt(self):
        self.assertEqual(classify(self.make()), "CONTINUITY_DEBT")

    def test_healthy_idle_with_empty_queue(self):
        self.assertEqual(classify(self.make(pending_eligible_work=0)), "NO_ELIGIBLE_ACTION")

    def test_connector_down_requires_explicit_block(self):
        self.assertEqual(classify(self.make(capability_probe="OFFLINE")), "BLOCKED_CONNECTOR")

    def test_unprobed_capability_is_unknown(self):
        self.assertEqual(classify(self.make(capability_probe="UNPROBED")), "UNKNOWN_CAPABILITY")

    def test_stale_source_blocks(self):
        self.assertEqual(classify(self.make(source_revision="")), "BLOCKED_STALE_SOURCE")

    def test_duplicate_lease_is_not_progress(self):
        self.assertEqual(classify(self.make(duplicate_lease=True)), "SKIPPED_DUPLICATE")

    def test_stop_has_precedence(self):
        self.assertEqual(classify(self.make(stopped=True, new_effects=1)), "STOPPED")

    def test_authority_gate(self):
        self.assertEqual(classify(self.make(authority_allowed=False)), "BLOCKED_AUTHORITY")

    def test_unacknowledged_effect_not_verified(self):
        self.assertEqual(classify(self.make(new_effects=1, receipt_refs=("receipt",))), "EFFECT_UNVERIFIED")

    def test_receiver_readback_required(self):
        self.assertEqual(classify(self.make(new_effects=1, independent_readback=True)), "EFFECT_UNVERIFIED")

    def test_verified_progress_is_explicit(self):
        self.assertEqual(classify(self.make(new_effects=1, independent_readback=True,
                                             receipt_refs=("exact-object-readback",))), "VERIFIED_PROGRESS")

    def test_no_new_evidence_with_next_wake(self):
        self.assertEqual(classify(self.make(reason="NO_NEW_EVIDENCE")), "NO_NEW_EVIDENCE")

    def test_no_new_evidence_without_wake_is_debt(self):
        self.assertEqual(classify(self.make(reason="NO_NEW_EVIDENCE", next_wake="")), "CONTINUITY_DEBT")


if __name__ == "__main__":
    unittest.main()
