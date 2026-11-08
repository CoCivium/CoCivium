"""Synthetic CoGrace/CoZombie peer-recovery policy tests. No OS or network effects."""
import unittest
from dataclasses import dataclass


@dataclass(frozen=True)
class Observation:
    pending_authorized_work: bool = False
    stopped_by_user: bool = False
    checkpoint_exists: bool = False
    wake_scheduled: bool = False
    observer_fresh: bool = False
    endpoint_ready: bool = False
    lease_expired: bool = False
    independent_failure: bool = False
    duplicate_actuator: bool = False
    evidence_conflict: bool = False
    meaningful_receipts: int = 0
    repeated_messages: int = 0
    sensitive_capture_consented: bool = False


def classify(o):
    """Conservative pure decision function; never equate missing signal with failure."""
    if o.stopped_by_user:
        return "USER_STOP_HOLD"
    if o.duplicate_actuator or o.evidence_conflict:
        return "QUARANTINE"
    if not o.pending_authorized_work:
        if o.checkpoint_exists and o.wake_scheduled and o.observer_fresh:
            return "QUIET_HEALTHY"
        return "UNKNOWN"
    if o.endpoint_ready and o.observer_fresh and o.meaningful_receipts:
        return "BUSY_USEFUL"
    if o.lease_expired and o.independent_failure and o.checkpoint_exists:
        return "RECOVERY_ELIGIBLE"
    if o.repeated_messages >= 10 and o.meaningful_receipts == 0:
        return "BUSY_UNPRODUCTIVE"
    return "UNKNOWN"


class SyntheticRecovery:
    """Single-fenced-actuator model with receiver-owned deduplication."""
    def __init__(self):
        self.lease_epoch = 0
        self.effects = set()
        self.receipts = []

    def transfer(self, o, work_id, effect_id, *, peer_authorized, receiver_available):
        status = classify(o)
        if status != "RECOVERY_ELIGIBLE" or not peer_authorized:
            return {"status": "HOLD", "effect_verified": False}
        self.lease_epoch += 1
        token = (work_id, self.lease_epoch)
        if not receiver_available:
            return {"status": "HOLD_RECEIVER_UNAVAILABLE", "token": token,
                    "effect_verified": False}
        key = (work_id, effect_id)
        if key in self.effects:
            return {"status": "DEDUPED", "token": token, "effect_verified": False}
        self.effects.add(key)
        receipt = {"status": "RECEIVER_READBACK_SYNTHETIC", "token": token,
                   "effect_verified": True, "effect_id": effect_id}
        self.receipts.append(receipt)
        return receipt


class CoGraceRecoveryTests(unittest.TestCase):
    def test_quiet_grace_does_not_trigger_recovery(self):
        o = Observation(checkpoint_exists=True, wake_scheduled=True, observer_fresh=True)
        self.assertEqual(classify(o), "QUIET_HEALTHY")
        self.assertFalse(SyntheticRecovery().transfer(
            o, "w1", "e1", peer_authorized=True, receiver_available=True)["effect_verified"])

    def test_stale_observer_alone_is_unknown(self):
        o = Observation(checkpoint_exists=True, wake_scheduled=True)
        self.assertEqual(classify(o), "UNKNOWN")

    def test_busy_without_outcome_is_not_healthy(self):
        o = Observation(pending_authorized_work=True, repeated_messages=10)
        self.assertEqual(classify(o), "BUSY_UNPRODUCTIVE")

    def test_positive_receipt_requires_fresh_observer(self):
        o = Observation(pending_authorized_work=True, endpoint_ready=True,
                        observer_fresh=True, meaningful_receipts=1)
        self.assertEqual(classify(o), "BUSY_USEFUL")
        self.assertEqual(classify(Observation(pending_authorized_work=True,
            endpoint_ready=True, meaningful_receipts=1)), "UNKNOWN")

    def test_two_independent_failure_signals_and_checkpoint_needed(self):
        base = dict(pending_authorized_work=True, lease_expired=True,
                    independent_failure=True, checkpoint_exists=True)
        self.assertEqual(classify(Observation(**base)), "RECOVERY_ELIGIBLE")
        for missing in ("lease_expired", "independent_failure", "checkpoint_exists"):
            self.assertNotEqual(classify(Observation(**{**base, missing: False})),
                                "RECOVERY_ELIGIBLE")

    def test_fenced_handoff_and_receiver_dedup(self):
        o = Observation(pending_authorized_work=True, lease_expired=True,
                        independent_failure=True, checkpoint_exists=True)
        runner = SyntheticRecovery()
        a = runner.transfer(o, "w1", "effect", peer_authorized=True,
                            receiver_available=True)
        b = runner.transfer(o, "w1", "effect", peer_authorized=True,
                            receiver_available=True)
        self.assertTrue(a["effect_verified"])
        self.assertEqual(b["status"], "DEDUPED")
        self.assertEqual(len(runner.effects), 1)
        self.assertEqual(len(runner.receipts), 1)

    def test_no_receiver_means_no_effect(self):
        o = Observation(pending_authorized_work=True, lease_expired=True,
                        independent_failure=True, checkpoint_exists=True)
        runner = SyntheticRecovery()
        self.assertEqual(runner.transfer(o, "w1", "effect", peer_authorized=True,
            receiver_available=False)["status"], "HOLD_RECEIVER_UNAVAILABLE")
        self.assertFalse(runner.effects)

    def test_no_peer_authority_means_no_handoff(self):
        o = Observation(pending_authorized_work=True, lease_expired=True,
                        independent_failure=True, checkpoint_exists=True)
        self.assertEqual(SyntheticRecovery().transfer(o, "w1", "e1",
            peer_authorized=False, receiver_available=True)["status"], "HOLD")

    def test_stop_overrides_failure_signals(self):
        o = Observation(pending_authorized_work=True, lease_expired=True,
                        independent_failure=True, checkpoint_exists=True,
                        stopped_by_user=True)
        self.assertEqual(classify(o), "USER_STOP_HOLD")

    def test_duplicate_or_conflicting_authority_quarantined(self):
        for kwargs in ({"duplicate_actuator": True}, {"evidence_conflict": True}):
            self.assertEqual(classify(Observation(**kwargs)), "QUARANTINE")

    def test_false_heartbeat_does_not_prove_useful(self):
        o = Observation(pending_authorized_work=True, observer_fresh=True,
                        endpoint_ready=True, meaningful_receipts=0,
                        repeated_messages=12)
        self.assertEqual(classify(o), "BUSY_UNPRODUCTIVE")

    def test_sensitive_capture_not_enabled_by_assistance(self):
        o = Observation(pending_authorized_work=True, lease_expired=True,
                        independent_failure=True, checkpoint_exists=True)
        self.assertFalse(o.sensitive_capture_consented)
        self.assertEqual(classify(o), "RECOVERY_ELIGIBLE")


if __name__ == "__main__":
    unittest.main()
