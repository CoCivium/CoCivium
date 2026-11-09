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
    eligibility_census_complete: bool = False
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
    if r.worker_triggered is not True:
        return "TRIGGER_MISSING"
    # A zero count is meaningful only after source + work eligibility are qualified.
    # Unknown, negative, boolean or unchecked counts are NOT an empty queue.
    if not isinstance(r.source_revision, str) or not r.source_revision.strip():
        return "BLOCKED_STALE_SOURCE"
    if r.eligibility_census_complete is not True:
        return "UNKNOWN_ELIGIBILITY"
    if (isinstance(r.pending_eligible_work, bool)
            or not isinstance(r.pending_eligible_work, int)
            or r.pending_eligible_work < 0):
        return "UNKNOWN_ELIGIBILITY"
    if r.pending_eligible_work == 0:
        return "NO_ELIGIBLE_ACTION"
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
                eligibility_census_complete=True,
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

    def test_zero_without_source_cannot_be_healthy_idle(self):
        self.assertEqual(classify(self.make(pending_eligible_work=0, source_revision="")), "BLOCKED_STALE_SOURCE")

    def test_zero_with_blank_source_cannot_be_healthy_idle(self):
        self.assertEqual(classify(self.make(pending_eligible_work=0, source_revision="   ")), "BLOCKED_STALE_SOURCE")

    def test_zero_without_qualified_eligibility_is_unknown(self):
        self.assertEqual(classify(self.make(pending_eligible_work=0, eligibility_census_complete=False)), "UNKNOWN_ELIGIBILITY")

    def test_pending_without_qualified_eligibility_is_unknown(self):
        self.assertEqual(classify(self.make(pending_eligible_work=1, eligibility_census_complete=False)), "UNKNOWN_ELIGIBILITY")

    def test_negative_work_count_does_not_mean_idle(self):
        self.assertEqual(classify(self.make(pending_eligible_work=-1)), "UNKNOWN_ELIGIBILITY")

    def test_boolean_work_count_is_not_an_integer_count(self):
        self.assertEqual(classify(self.make(pending_eligible_work=False)), "UNKNOWN_ELIGIBILITY")

    def test_text_work_count_is_not_an_integer_count(self):
        self.assertEqual(classify(self.make(pending_eligible_work="0")), "UNKNOWN_ELIGIBILITY")

    def test_claimed_receipt_cannot_override_missing_census(self):
        self.assertEqual(classify(self.make(eligibility_census_complete=False,
                            new_effects=1, independent_readback=True,
                            receipt_refs=("alleged-receipt",))), "UNKNOWN_ELIGIBILITY")

    def test_non_boolean_worker_trigger_is_not_proof(self):
        self.assertEqual(classify(self.make(worker_triggered="yes")), "TRIGGER_MISSING")


if __name__ == "__main__":
    unittest.main()
