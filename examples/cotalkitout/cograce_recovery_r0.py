"""CoGrace/CoZombie recovery policy: evidence-scoped, reversible, no provider session control."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Observation:
    work_id: str
    state: str
    age_seconds: int
    deadline_seconds: int
    progress_events: int
    repeated_noop: int
    metric_coverage: float
    receiver_verified: bool
    wake_condition_pending: bool = False
    human_gate_pending: bool = False

@dataclass(frozen=True)
class Peer:
    peer_id: str
    capability_match: bool
    healthy_observed: bool
    capacity_available: bool
    authority_scope_match: bool

def assess(o, peers, min_coverage=0.75):
    if not 0 <= o.metric_coverage <= 1:
        raise ValueError("coverage out of range")
    if o.age_seconds < 0 or o.deadline_seconds < 0:
        raise ValueError("invalid time")
    if o.state in ("DONE", "CLOSED"):
        return {"action": "NO_ACTION", "reason": "TERMINAL"}
    if o.wake_condition_pending or o.state in ("SLEEP", "QUIESCENT"):
        return {"action": "NO_ACTION", "reason": "VALID_WAIT"}
    if o.human_gate_pending:
        return {"action": "HOLD", "reason": "HUMAN_AUTHORITY"}
    if o.metric_coverage < min_coverage:
        return {"action": "OBSERVE_MORE", "reason": "INSUFFICIENT_COVERAGE"}
    if o.age_seconds <= o.deadline_seconds or (o.progress_events > 0 and o.repeated_noop < 3):
        return {"action": "NO_ACTION", "reason": "NO_STALL_PROVEN"}
    if o.repeated_noop < 3 and o.progress_events > 0:
        return {"action": "NO_ACTION", "reason": "PROGRESS_PRESENT"}
    eligible = sorted(p.peer_id for p in peers if p.capability_match and p.healthy_observed
                      and p.capacity_available and p.authority_scope_match)
    if not eligible:
        return {"action": "SUSPEND_UNTIL_TRIGGER", "reason": "NO_ELIGIBLE_PEER"}
    return {"action": "PROPOSE_REVERSIBLE_HANDOFF", "reason": "STALL_CANDIDATE",
            "peer": eligible[0], "requires": ["DURABLE_CHECKPOINT", "LEASE_FENCE",
              "RECEIVER_READBACK", "ROLLBACK_PATH"], "effects": 0}

if __name__ == "__main__":
    import unittest
    class Tests(unittest.TestCase):
        def setUp(self):
            self.stalled = Observation("w1", "WORKING", 100, 10, 0, 5, 0.9, False)
            self.peer = Peer("peer-a", True, True, True, True)
        def test_idle_sleep_not_zombie(self):
            self.assertEqual(assess(Observation("w", "SLEEP", 10000, 10, 0, 0, 1, False), [self.peer])["reason"], "VALID_WAIT")
        def test_coverage_gate(self):
            from dataclasses import replace
            self.assertEqual(assess(replace(self.stalled, metric_coverage=0.2), [self.peer])["action"], "OBSERVE_MORE")
        def test_stall_recovery_is_proposal_only(self):
            result = assess(self.stalled, [self.peer])
            self.assertEqual(result["action"], "PROPOSE_REVERSIBLE_HANDOFF")
            self.assertEqual(result["effects"], 0)
        def test_no_authorized_peer(self):
            self.assertEqual(assess(self.stalled, [Peer("p", True, True, True, False)])["action"], "SUSPEND_UNTIL_TRIGGER")
        def test_human_gate_not_overridden(self):
            from dataclasses import replace
            self.assertEqual(assess(replace(self.stalled, human_gate_pending=True), [self.peer])["action"], "HOLD")
        def test_deadline_not_elapsed(self):
            from dataclasses import replace
            self.assertEqual(assess(replace(self.stalled, age_seconds=2), [self.peer])["action"], "NO_ACTION")
        def test_deterministic_peer_selection(self):
            peers = [Peer("z", True, True, True, True), self.peer]
            self.assertEqual(assess(self.stalled, peers)["peer"], "peer-a")
        def test_invalid_coverage(self):
            from dataclasses import replace
            with self.assertRaises(ValueError):
                assess(replace(self.stalled, metric_coverage=1.2), [self.peer])
    unittest.main(verbosity=2)
