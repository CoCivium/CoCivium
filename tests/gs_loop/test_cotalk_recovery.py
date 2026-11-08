"""Synthetic CoTalkItOut stalled-worker recovery using existing GS guards and Seed.

This is isolated test-only orchestration, not a deployed multi-agent or X2 service.
"""
import os
import sqlite3
import tempfile
import unittest

from test_durable_seed import DurableSeed
from test_loop_guard import LoopGuard


class RecoveryCoordinator:
    """A bounded fixture: no external model/session access or authority elevation."""

    def __init__(self, seed, seed_id="co-seed"):
        self.seed = seed
        self.seed_id = seed_id
        self.guard = LoopGuard(max_repeats=2, max_steps=12)
        self.blocker_id = None
        self.epoch = self.seed.elect(seed_id)
        self.status = "HEALTHY_IDLE"

    def observe(self, fingerprint=None, progress=False, expected_to_work=False):
        if not expected_to_work:
            return self.status
        state = self.guard.observe(fingerprint, verified_progress=progress)
        if state == "PROGRESS":
            self.status = "HEALTHY_ACTIVE"
        elif state.startswith("SUSPENDED"):
            self.status = "STALLED"
            # Deterministic blocker ID: repeated notifications do not spawn work.
            self.blocker_id = self.seed_id + ":stalled:" + str(self.epoch)
        else:
            self.status = "HEALTHY_ACTIVE"
        return self.status

    def handoff(self, permitted, receiver_readback):
        if self.status != "STALLED" or not permitted:
            return "DENIED"
        next_epoch = self.seed.elect(self.seed_id)
        if not receiver_readback:
            self.status = "WAITING_ON_EVENT"
            return "ACK_UNPROVEN"
        self.epoch = next_epoch
        self.status = "RECOVERING"
        return "HANDOFF_READBACK_CONFIRMED"


class CoTalkRecoveryTests(unittest.TestCase):
    def test_healthy_idle_does_not_trigger_rescue(self):
        with tempfile.TemporaryDirectory() as d:
            seed = DurableSeed(os.path.join(d, "seed.sqlite"))
            coordinator = RecoveryCoordinator(seed)
            for _ in range(20):
                self.assertEqual(coordinator.observe("idle", expected_to_work=False), "HEALTHY_IDLE")
            self.assertIsNone(coordinator.blocker_id)
            seed.close()

    def test_stalled_duplicate_signals_have_one_blocker(self):
        with tempfile.TemporaryDirectory() as d:
            seed = DurableSeed(os.path.join(d, "seed.sqlite"))
            coordinator = RecoveryCoordinator(seed)
            states = [coordinator.observe("repeated", expected_to_work=True) for _ in range(10)]
            self.assertEqual(states[2], "STALLED")
            self.assertEqual(set(states[2:]), {"STALLED"})
            self.assertEqual(coordinator.blocker_id, "co-seed:stalled:1")
            seed.close()

    def test_handoff_fences_predecessor_and_survives_restart(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "seed.sqlite")
            seed = DurableSeed(path)
            coordinator = RecoveryCoordinator(seed)
            for _ in range(3):
                coordinator.observe("stuck", expected_to_work=True)
            old_epoch = coordinator.epoch
            self.assertEqual(coordinator.handoff(True, True), "HANDOFF_READBACK_CONFIRMED")
            self.assertEqual(seed.commit("co-seed", old_epoch, "old-effect", "stale"), "FENCED")
            self.assertEqual(seed.commit("co-seed", coordinator.epoch, "new-effect", "synthetic"), "COMMITTED")
            seed.close()
            reopened = DurableSeed(path)
            row = reopened.db.execute("SELECT epoch FROM seed WHERE id=?", ("co-seed",)).fetchone()
            self.assertEqual(row[0], old_epoch + 1)
            self.assertEqual(reopened.db.execute("SELECT COUNT(*) FROM receipts").fetchone()[0], 1)
            reopened.close()

    def test_no_unauthorized_handoff(self):
        with tempfile.TemporaryDirectory() as d:
            seed = DurableSeed(os.path.join(d, "seed.sqlite"))
            coordinator = RecoveryCoordinator(seed)
            for _ in range(3):
                coordinator.observe("stuck", expected_to_work=True)
            self.assertEqual(coordinator.handoff(False, True), "DENIED")
            self.assertEqual(seed.db.execute("SELECT epoch FROM seed").fetchone()[0], 1)
            seed.close()

    def test_unverified_readback_is_not_a_success(self):
        with tempfile.TemporaryDirectory() as d:
            seed = DurableSeed(os.path.join(d, "seed.sqlite"))
            coordinator = RecoveryCoordinator(seed)
            for _ in range(3):
                coordinator.observe("stuck", expected_to_work=True)
            self.assertEqual(coordinator.handoff(True, False), "ACK_UNPROVEN")
            self.assertEqual(coordinator.status, "WAITING_ON_EVENT")
            seed.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
