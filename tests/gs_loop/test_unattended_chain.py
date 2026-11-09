"""Fail-closed synthetic unattended-progress chain. No X2 or external receiver claim."""
import unittest

STEPS = ("wake", "source", "selection", "authority", "lease",
         "execution", "receipt", "readback", "checkpoint", "next_wake", "projection")

class ProgressChain:
    def __init__(self):
        self.events = {}
    def record(self, step, evidence=None):
        if step not in STEPS:
            raise ValueError("unknown step")
        if not isinstance(evidence, str) or not evidence.strip():
            raise ValueError("exact evidence reference required")
        index = STEPS.index(step)
        if index and STEPS[index - 1] not in self.events:
            raise ValueError("predecessor has no evidence")
        self.events[step] = evidence
    @property
    def state(self):
        if not self.events:
            return "NOT_STARTED"
        if len(self.events) == len(STEPS):
            return "SYNTHETIC_CHAIN_COMPLETE"
        return "AWAITING_" + STEPS[len(self.events)].upper()
    @property
    def verified_effect(self):
        return "readback" in self.events and "receipt" in self.events

class TestUnattendedChain(unittest.TestCase):
    def test_scheduler_only_is_not_progress(self):
        p = ProgressChain()
        p.record("wake", "scheduler-run-1")
        self.assertEqual(p.state, "AWAITING_SOURCE")
        self.assertFalse(p.verified_effect)

    def test_no_update_without_source_is_not_verified(self):
        p = ProgressChain()
        p.record("wake", "scheduled-1")
        with self.assertRaises(ValueError):
            p.record("selection", "no-change")
        self.assertFalse(p.verified_effect)

    def test_missing_evidence_rejected(self):
        p = ProgressChain()
        with self.assertRaises(ValueError):
            p.record("wake", "")
        with self.assertRaises(ValueError):
            p.record("wake", None)

    def test_missing_receiver_readback_blocks_effect(self):
        p = ProgressChain()
        for step in STEPS[:7]:
            p.record(step, "mock:" + step)
        self.assertEqual(p.state, "AWAITING_READBACK")
        self.assertFalse(p.verified_effect)
        with self.assertRaises(ValueError):
            p.record("checkpoint", "mock:checkpoint")

    def test_full_synthetic_chain_is_not_runtime_proof(self):
        p = ProgressChain()
        for step in STEPS:
            p.record(step, "mock:" + step)
        self.assertTrue(p.verified_effect)
        self.assertEqual(p.state, "SYNTHETIC_CHAIN_COMPLETE")
        self.assertNotEqual(p.state, "RUNTIME_VERIFIED")

    def test_deduplicated_replay(self):
        p = ProgressChain()
        p.record("wake", "run-1")
        p.record("wake", "run-1")
        self.assertEqual(len(p.events), 1)

    def test_invalid_step(self):
        with self.assertRaises(ValueError):
            ProgressChain().record("canon", "unearned")

if __name__ == "__main__":
    unittest.main(verbosity=2)
