"""Synthetic-only CoDesktop R5 supervisor contract tests (no OS/process effects)."""
import unittest
from dataclasses import dataclass


@dataclass
class Worker:
    name: str
    endpoint_ready: bool
    process_present: bool
    stopped_by_user: bool = False
    restart_attempts: int = 0
    max_attempts: int = 1


class SupervisorModel:
    def __init__(self):
        self.leases = set()
        self.receipts = []

    def reconcile(self, worker, *, owner, observer_fresh=True):
        if worker.stopped_by_user:
            decision = "USER_STOP_HOLD"
        elif worker.process_present and worker.endpoint_ready:
            decision = "HEALTHY"
        elif worker.restart_attempts >= worker.max_attempts:
            decision = "CRASH_LOOP_HOLD"
        elif any(name == worker.name and existing_owner != owner for name, existing_owner in self.leases):
            decision = "DUPLICATE_OWNER_HOLD"
        else:
            self.leases.add((worker.name, owner))
            worker.restart_attempts += 1
            decision = "RESTART_ATTEMPT_ONLY"
        receipt = {"worker": worker.name, "owner": owner, "decision": decision,
                   "observer": "FRESH" if observer_fresh else "STALE",
                   "effect_verified": False}
        self.receipts.append(receipt)
        return receipt


class ContractTests(unittest.TestCase):
    def test_healthy_not_restarted(self):
        w = Worker("r5", True, True)
        self.assertEqual(SupervisorModel().reconcile(w, owner="os")["decision"], "HEALTHY")
        self.assertEqual(w.restart_attempts, 0)

    def test_crashed_worker_bounded_attempt(self):
        s, w = SupervisorModel(), Worker("r5", False, False)
        self.assertEqual(s.reconcile(w, owner="os")["decision"], "RESTART_ATTEMPT_ONLY")
        self.assertEqual(s.reconcile(w, owner="os")["decision"], "CRASH_LOOP_HOLD")
        self.assertEqual(w.restart_attempts, 1)

    def test_user_stop_is_authoritative(self):
        w = Worker("r5", False, False, stopped_by_user=True)
        self.assertEqual(SupervisorModel().reconcile(w, owner="os")["decision"], "USER_STOP_HOLD")
        self.assertEqual(w.restart_attempts, 0)

    def test_stale_observer_is_not_host_off(self):
        r = SupervisorModel().reconcile(Worker("r5", True, True), owner="os", observer_fresh=False)
        self.assertEqual((r["observer"], r["decision"]), ("STALE", "HEALTHY"))

    def test_process_present_endpoint_down_is_not_healthy(self):
        r = SupervisorModel().reconcile(Worker("r5", False, True), owner="os")
        self.assertEqual(r["decision"], "RESTART_ATTEMPT_ONLY")

    def test_duplicate_owner_is_held(self):
        s = SupervisorModel()
        w = Worker("r5", False, False, max_attempts=3)
        s.reconcile(w, owner="a")
        self.assertEqual(s.reconcile(w, owner="b")["decision"], "DUPLICATE_OWNER_HOLD")
        self.assertEqual(w.restart_attempts, 1)

    def test_attempt_does_not_claim_effect(self):
        r = SupervisorModel().reconcile(Worker("r5", False, False), owner="os")
        self.assertFalse(r["effect_verified"])

    def test_each_decision_has_receipt(self):
        s = SupervisorModel()
        w = Worker("r5", True, True)
        s.reconcile(w, owner="os")
        s.reconcile(w, owner="os")
        self.assertEqual(len(s.receipts), 2)


if __name__ == "__main__":
    unittest.main()
