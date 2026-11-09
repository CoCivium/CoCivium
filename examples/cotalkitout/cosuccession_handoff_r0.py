"""CoSuccession R0: bounded, source-only peer handoff with independent receiver evidence.

No external sessions, WhatsApp identities, or effectful leases are controlled here.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Checkpoint:
    work_id: str
    source_head: str
    artifact_hash: str
    checkpoint_id: str
    source_peer: str

@dataclass(frozen=True)
class Handoff:
    checkpoint: Checkpoint
    successor_peer: str
    receiver_peer: str
    receiver_work_id: str
    receiver_artifact_hash: str
    receiver_source_head: str
    receiver_checkpoint_id: str
    receiver_independent: bool
    capability_verified: bool
    scope_authorized: bool
    lease_checkpoint_id: str
    effect_fenced: bool

def assess_handoff(h):
    if not h.scope_authorized:
        return "HOLD_AUTHORITY"
    if not h.capability_verified:
        return "HOLD_CAPABILITY"
    if not h.effect_fenced:
        return "HOLD_LEASE_FENCE"
    if h.lease_checkpoint_id != h.checkpoint.checkpoint_id:
        return "EXPIRED_LEASE"
    if h.receiver_peer in (h.checkpoint.source_peer, h.successor_peer) or not h.receiver_independent:
        return "HOLD_INDEPENDENCE"
    if (h.receiver_work_id, h.receiver_artifact_hash, h.receiver_source_head,
        h.receiver_checkpoint_id) != (h.checkpoint.work_id, h.checkpoint.artifact_hash,
                                       h.checkpoint.source_head, h.checkpoint.checkpoint_id):
        return "HOLD_READBACK"
    return "READY_FOR_AUTHORIZED_HANDOFF"

if __name__ == "__main__":
    import unittest
    from dataclasses import replace
    class Tests(unittest.TestCase):
        def setUp(self):
            cp = Checkpoint("w1", "head1", "hash1", "cp1", "whatsapp-peer")
            self.h = Handoff(cp, "github-worker", "independent-observer", "w1",
                             "hash1", "head1", "cp1", True, True, True, "cp1", True)
        def test_complete_proposal(self):
            self.assertEqual(assess_handoff(self.h), "READY_FOR_AUTHORIZED_HANDOFF")
        def test_no_authority(self):
            self.assertEqual(assess_handoff(replace(self.h, scope_authorized=False)), "HOLD_AUTHORITY")
        def test_no_capability(self):
            self.assertEqual(assess_handoff(replace(self.h, capability_verified=False)), "HOLD_CAPABILITY")
        def test_lease_expiry(self):
            self.assertEqual(assess_handoff(replace(self.h, lease_checkpoint_id="cp0")), "EXPIRED_LEASE")
        def test_no_fence(self):
            self.assertEqual(assess_handoff(replace(self.h, effect_fenced=False)), "HOLD_LEASE_FENCE")
        def test_no_self_ack(self):
            self.assertEqual(assess_handoff(replace(self.h, receiver_peer="github-worker")), "HOLD_INDEPENDENCE")
        def test_no_source_ack(self):
            self.assertEqual(assess_handoff(replace(self.h, receiver_peer="whatsapp-peer")), "HOLD_INDEPENDENCE")
        def test_false_independence(self):
            self.assertEqual(assess_handoff(replace(self.h, receiver_independent=False)), "HOLD_INDEPENDENCE")
        def test_wrong_hash(self):
            self.assertEqual(assess_handoff(replace(self.h, receiver_artifact_hash="wrong")), "HOLD_READBACK")
        def test_wrong_work_id(self):
            self.assertEqual(assess_handoff(replace(self.h, receiver_work_id="w2")), "HOLD_READBACK")
        def test_wrong_head(self):
            self.assertEqual(assess_handoff(replace(self.h, receiver_source_head="head0")), "HOLD_READBACK")
        def test_wrong_checkpoint(self):
            self.assertEqual(assess_handoff(replace(self.h, receiver_checkpoint_id="cp0")), "HOLD_READBACK")
    unittest.main(verbosity=2)
