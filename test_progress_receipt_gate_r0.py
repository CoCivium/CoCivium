"""Synthetic causality checks; no actual scheduler or receiver is spoofed."""
import unittest
from dataclasses import replace
from examples.cotalkitout.progress_receipt_gate_r0 import Pulse, classify

def base(**updates):
    p = Pulse(work_id="w1",source_revision="sha1",observed_at_utc="2026-11-08T22:32:00Z",
              wake_id="wake1",source_checked=True,due_work=False,eligible_work=False,
              execution_attempted=False,next_wake="trigger:source-update",claimed_no_update=True)
    return replace(p,**updates)

class Tests(unittest.TestCase):
    def test_true_no_change_with_source_and_wake(self):
        self.assertEqual(classify(base())["disposition"],"SOURCE_CLAIMED_NO_DELTA")
    def test_no_update_without_check_fails(self):
        self.assertEqual(classify(base(source_checked=False))["reason"],"SOURCE_NOT_CHECKED")
    def test_due_eligible_work_cannot_claim_idle(self):
        self.assertEqual(classify(base(due_work=True,eligible_work=True))["reason"],"ELIGIBLE_WORK_UNATTEMPTED")
    def test_due_unexplained_work_cannot_claim_idle(self):
        self.assertEqual(classify(base(due_work=True))["reason"],"DUE_WORK_UNACCOUNTED")
    def test_no_next_trigger_fails(self):
        self.assertEqual(classify(base(next_wake=""))["reason"],"NO_NEXT_WAKE")
    def test_due_blocked_work_is_held_not_success(self):
        self.assertEqual(classify(base(due_work=True,blocked_reason="X2_RECEIVER_UNAVAILABLE"))["disposition"],"WAITING_ON_EVENT")
    def test_work_without_receipt_not_success(self):
        self.assertEqual(classify(base(execution_attempted=True,claimed_no_update=False))["reason"],"EXECUTION_NO_RECEIPT")
    def test_receipt_without_receiver_readback_not_success(self):
        d=classify(base(execution_attempted=True,claimed_no_update=False,output_digest="sha256:fixture",effect_receipt="fixture:receipt"))
        self.assertEqual(d["disposition"],"AWAITING_RECEIVER_PROOF")
    def test_full_caller_proof_is_only_structurally_classified(self):
        d=classify(base(execution_attempted=True,claimed_no_update=False,output_digest="sha256:fixture",
                        effect_receipt="fixture:receipt",receiver_readback="fixture:ack"))
        self.assertEqual(d["disposition"],"STRUCTURALLY_REPORTED_EFFECT")
    def test_missing_identity_fails(self):
        self.assertEqual(classify(base(source_revision=""))["reason"],"UNBOUND_WAKE_OR_SOURCE")

    def test_executed_work_must_name_next_wake(self):
        d=classify(base(execution_attempted=True,claimed_no_update=False,next_wake="",
                        output_digest="sha256:fixture",effect_receipt="fixture:receipt",
                        receiver_readback="fixture:ack"))
        self.assertEqual(d["reason"],"NO_NEXT_WAKE")
    def test_cannot_claim_no_update_and_work_effect(self):
        d=classify(base(execution_attempted=True,claimed_no_update=True,
                        output_digest="sha256:fixture",effect_receipt="fixture:receipt",
                        receiver_readback="fixture:ack"))
        self.assertEqual(d["reason"],"CONTRADICTORY_NO_UPDATE_AND_EXECUTION")
    def test_no_delta_requires_explicit_caller_claim(self):
        self.assertEqual(classify(base(claimed_no_update=False))["reason"],"NO_DELTA_CLAIM_MISSING")

if __name__=="__main__":
    unittest.main()
