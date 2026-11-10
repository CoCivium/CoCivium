"""Isolated autonomy acceptance contract; not a live X2 run.

The injected verifier is a test fixture. Real deployment requires independent
receipt validation, continuity checks, and authorized observation.
"""
import unittest


def evaluate(events, duration_seconds=86400, verify=None):
    if not events:
        return "NO_EVIDENCE"
    if not callable(verify):
        return "UNVERIFIED"
    if any(not isinstance(e.get("at"), (int, float)) or
           isinstance(e.get("at"), bool) for e in events):
        return "INVALID_TIME"
    if any(e["kind"] == "duplicate_effect" for e in events):
        return "DUPLICATE_EFFECT"
    if any(e["kind"] == "human_intervention" for e in events):
        return "NOT_UNATTENDED"
    required = {"handoff", "recovery", "observer_effect", "cobar_visible"}
    verified = [e for e in events if verify(e)]
    if required - {e["kind"] for e in verified}:
        return "INCOMPLETE_PROOF"
    alive = sorted(e["at"] for e in verified if e["kind"] == "seed_alive")
    if len(alive) < 2 or alive[-1] - alive[0] < duration_seconds:
        return "INSUFFICIENT_DURATION"
    return "ACCEPTED_FIXTURE_ONLY"


class AutonomyAcceptanceTests(unittest.TestCase):
    @staticmethod
    def trusted(e):
        # Fixture only. The event cannot certify itself with a verified flag.
        return e.get("receipt") == "fixture-trusted"

    def complete(self):
        return [
            {"kind": "seed_alive", "at": 0, "receipt": "fixture-trusted"},
            {"kind": "handoff", "at": 120, "receipt": "fixture-trusted"},
            {"kind": "recovery", "at": 360, "receipt": "fixture-trusted"},
            {"kind": "observer_effect", "at": 720, "receipt": "fixture-trusted"},
            {"kind": "cobar_visible", "at": 1000, "receipt": "fixture-trusted"},
            {"kind": "seed_alive", "at": 86400, "receipt": "fixture-trusted"},
        ]

    def test_fixture_accepts(self):
        self.assertEqual(evaluate(self.complete(), verify=self.trusted), "ACCEPTED_FIXTURE_ONLY")

    def test_missing_proof_rejected(self):
        e = [x for x in self.complete() if x["kind"] != "observer_effect"]
        self.assertEqual(evaluate(e, verify=self.trusted), "INCOMPLETE_PROOF")

    def test_short_run_rejected(self):
        e = self.complete()
        e[-1]["at"] = 1000
        self.assertEqual(evaluate(e, verify=self.trusted), "INSUFFICIENT_DURATION")

    def test_duplicate_effect_rejected(self):
        e = self.complete() + [{"kind": "duplicate_effect", "at": 900}]
        self.assertEqual(evaluate(e, verify=self.trusted), "DUPLICATE_EFFECT")

    def test_human_intervention_rejected(self):
        e = self.complete() + [{"kind": "human_intervention", "at": 900}]
        self.assertEqual(evaluate(e, verify=self.trusted), "NOT_UNATTENDED")

    def test_self_certification_rejected(self):
        e = self.complete()
        for item in e:
            item["verified"] = True
            item.pop("receipt", None)
        self.assertEqual(evaluate(e, verify=self.trusted), "INCOMPLETE_PROOF")
        self.assertEqual(evaluate(self.complete()), "UNVERIFIED")

    def test_unrelated_late_event_does_not_extend_survival(self):
        e = self.complete()
        e[-1]["at"] = 1000
        e.append({"kind": "unrelated", "at": 100000, "receipt": "fixture-trusted"})
        self.assertEqual(evaluate(e, verify=self.trusted), "INSUFFICIENT_DURATION")


if __name__ == "__main__":
    unittest.main(verbosity=2)
