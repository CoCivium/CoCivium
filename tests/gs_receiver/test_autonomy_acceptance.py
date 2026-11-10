"""Acceptance logic for unattended autonomy evidence, not a live X2 run."""
import unittest


def evaluate(events, duration_seconds=86400):
    """Fail closed when any required independent evidence is absent."""
    if not events:
        return "NO_EVIDENCE"
    ordered = sorted(events, key=lambda e: e["at"])
    if ordered[-1]["at"] - ordered[0]["at"] < duration_seconds:
        return "INSUFFICIENT_DURATION"
    required = {"seed_alive", "handoff", "recovery", "observer_effect", "cobar_visible"}
    verified = {e["kind"] for e in ordered if e.get("verified") is True}
    if required - verified:
        return "INCOMPLETE_PROOF"
    if any(e["kind"] == "duplicate_effect" for e in ordered):
        return "DUPLICATE_EFFECT"
    if any(e["kind"] == "human_intervention" for e in ordered):
        return "NOT_UNATTENDED"
    return "ACCEPTED_FIXTURE_ONLY"


class AutonomyAcceptanceTests(unittest.TestCase):
    def complete(self):
        return [
            {"kind": "seed_alive", "at": 0, "verified": True},
            {"kind": "handoff", "at": 120, "verified": True},
            {"kind": "recovery", "at": 360, "verified": True},
            {"kind": "observer_effect", "at": 720, "verified": True},
            {"kind": "cobar_visible", "at": 86400, "verified": True},
        ]

    def test_fixture_accepts(self):
        self.assertEqual(evaluate(self.complete()), "ACCEPTED_FIXTURE_ONLY")

    def test_missing_proof_rejected(self):
        e = [x for x in self.complete() if x["kind"] != "observer_effect"]
        self.assertEqual(evaluate(e), "INCOMPLETE_PROOF")

    def test_short_run_rejected(self):
        e = self.complete()
        e[-1]["at"] = 1000
        self.assertEqual(evaluate(e), "INSUFFICIENT_DURATION")

    def test_duplicate_effect_rejected(self):
        e = self.complete() + [{"kind": "duplicate_effect", "at": 900}]
        self.assertEqual(evaluate(e), "DUPLICATE_EFFECT")

    def test_human_intervention_rejected(self):
        e = self.complete() + [{"kind": "human_intervention", "at": 900}]
        self.assertEqual(evaluate(e), "NOT_UNATTENDED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
