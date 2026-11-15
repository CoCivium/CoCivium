"""Front-awareness contract: a front is never alive merely because it has an issue.

Pure, synthetic and side-effect-free. One elected actuator per collision domain.
"""
from dataclasses import dataclass
import unittest


@dataclass(frozen=True)
class Front:
    front_id: str
    source_revision: str
    pending_work: bool
    last_effect_receipt: str = ""
    last_verified_at: int | None = None
    next_wake_at: int | None = None
    observer_checked_at: int | None = None
    observer_ttl: int = 3600
    blocked_reason: str = ""
    authority: str = "READ_ONLY"
    actuator_id: str = ""
    collision_domain: str = ""


def evaluate(front, *, now):
    """Classify proof and next-wake independently; never invent a worker heartbeat."""
    if not front.front_id or not front.source_revision:
        return ("INVALID_SOURCE", "HOLD")
    if (front.observer_checked_at is None or front.observer_checked_at > now
            or front.observer_ttl <= 0 or now - front.observer_checked_at > front.observer_ttl):
        return ("STALE_OR_UNOBSERVED", "PROBE")
    if front.blocked_reason:
        return ("BLOCKED", "RETRY_AT_WAKE" if front.next_wake_at is not None else "HOLD")
    if front.last_effect_receipt and front.last_verified_at is not None and front.last_verified_at <= now:
        state = "VERIFIED_DELTA"
    else:
        state = "NO_VERIFIED_DELTA"
    if not front.pending_work:
        return (state, "GRACE")
    if front.next_wake_at is not None and now < front.next_wake_at:
        return (state, "WAIT_FOR_WAKE")
    if front.authority not in ("READ_ONLY", "REVERSIBLE"):
        return (state, "AUTHORITY_GATE")
    return (state, "ELECT_ONE_ACTUATOR")


def elect(fronts, *, now):
    """One eligible candidate per collision domain; deterministic ordering."""
    selected, held, domains = [], [], set()
    for front in sorted(fronts, key=lambda f: (f.collision_domain, f.front_id)):
        state, action = evaluate(front, now=now)
        if action != "ELECT_ONE_ACTUATOR":
            held.append((front.front_id, state, action))
            continue
        if not front.collision_domain or not front.actuator_id:
            held.append((front.front_id, state, "MISSING_ACTUATOR_BINDING"))
            continue
        if front.collision_domain in domains:
            held.append((front.front_id, state, "COLLISION_HOLD"))
            continue
        domains.add(front.collision_domain)
        selected.append((front.front_id, front.actuator_id, front.source_revision))
    return {"selected": selected, "held": held}


class FrontAwarenessTests(unittest.TestCase):
    base = dict(front_id="orb", source_revision="sha1", pending_work=True,
                observer_checked_at=100, next_wake_at=100,
                actuator_id="worker-a", collision_domain="orb-source")

    def f(self, **kwargs):
        return Front(**{**self.base, **kwargs})

    def test_missing_source_not_alive(self):
        self.assertEqual(evaluate(self.f(source_revision=""), now=101)[0], "INVALID_SOURCE")

    def test_stale_observer_not_current(self):
        self.assertEqual(evaluate(self.f(observer_checked_at=1, observer_ttl=10), now=101)[0],
                         "STALE_OR_UNOBSERVED")

    def test_healthy_idle_preserves_grace(self):
        self.assertEqual(evaluate(self.f(pending_work=False), now=101)[1], "GRACE")

    def test_pending_work_and_no_receipt_not_claimed_done(self):
        self.assertEqual(evaluate(self.f(), now=101), ("NO_VERIFIED_DELTA", "ELECT_ONE_ACTUATOR"))

    def test_receipt_is_distinct_from_scheduling(self):
        state, action = evaluate(self.f(last_effect_receipt="receipt", last_verified_at=101,
                                        next_wake_at=200), now=101)
        self.assertEqual((state, action), ("VERIFIED_DELTA", "WAIT_FOR_WAKE"))

    def test_blocked_requires_explicit_wake(self):
        self.assertEqual(evaluate(self.f(blocked_reason="BRIDGE_OFFLINE", next_wake_at=None),
                                  now=101), ("BLOCKED", "HOLD"))

    def test_nonreversible_requires_gate(self):
        self.assertEqual(evaluate(self.f(authority="PUBLIC_RELEASE"), now=101)[1],
                         "AUTHORITY_GATE")

    def test_no_duplicate_actuator_on_shared_domain(self):
        a, b = self.f(front_id="a"), self.f(front_id="b", actuator_id="worker-b")
        election = elect((b, a), now=101)
        self.assertEqual(len(election["selected"]), 1)
        self.assertEqual(election["held"][0][2], "COLLISION_HOLD")

    def test_distinct_domains_can_run_in_parallel(self):
        a, b = self.f(front_id="a"), self.f(front_id="b",
                             actuator_id="worker-b", collision_domain="other")
        self.assertEqual(len(elect((a, b), now=101)["selected"]), 2)

    def test_unbound_actuator_must_hold(self):
        self.assertEqual(elect((self.f(actuator_id=""),), now=101)["held"][0][2],
                         "MISSING_ACTUATOR_BINDING")

    def test_stale_event_does_not_override_currentness(self):
        self.assertEqual(evaluate(self.f(last_effect_receipt="r", last_verified_at=100,
                                         observer_checked_at=1, observer_ttl=10), now=101)[0],
                         "STALE_OR_UNOBSERVED")


if __name__ == "__main__":
    unittest.main()
