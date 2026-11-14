"""CoFuturePull R0: deterministic synthetic forecast-vs-static tests.

A toy decision comparison, NOT an economic law, live forecasting, or G_d evidence.
The planner sees an imperfect signal of next-period need. Outcomes are scored
against independently specified realized need and resource cost.
"""
import unittest
from dataclasses import dataclass


@dataclass(frozen=True)
class Dimension:
    name: str
    unit: str
    target: float


@dataclass(frozen=True)
class FutureEnvelope:
    dimensions: tuple
    max_cost: float
    maximum_rights_violations: int = 0

    def validate(self, observed):
        if not self.dimensions or self.max_cost < 0:
            raise ValueError("invalid future envelope")
        for d in self.dimensions:
            if not d.unit or d.name not in observed:
                raise ValueError("unit or observation missing")
            if observed[d.name][1] != d.unit:
                raise ValueError("incompatible units")
        return True


def choose(static_need, signal, *, adaptive, capacity=12):
    """A bounded forecast-driven action; signal is not guaranteed correct."""
    desired = signal if adaptive else static_need
    return max(0, min(capacity, desired))


def outcome(action, realized_need, *, reserve=12):
    """Toy loss: unmet need dominates waste; rights require need >= 6 supplied."""
    unmet = max(0, realized_need - action)
    waste = max(0, action - realized_need)
    return {
        "loss": 3 * unmet + waste + 0.1 * action,
        "rights_violations": int(realized_need >= 6 and action < 6),
        "remaining_units": reserve - action,
    }


def compare(scenarios):
    """Same capacity/observations and budgets for both policies."""
    rows = []
    for realized, signal in scenarios:
        static = choose(6, signal, adaptive=False)
        adaptive = choose(6, signal, adaptive=True)
        rows.append({
            "realized_need": realized, "signal": signal,
            "static_action": static, "adaptive_action": adaptive,
            "static": outcome(static, realized), "adaptive": outcome(adaptive, realized),
        })
    return {
        "rows": rows,
        "static_total_loss": sum(r["static"]["loss"] for r in rows),
        "adaptive_total_loss": sum(r["adaptive"]["loss"] for r in rows),
        "interpretation": "SYNTHETIC_ASSUMPTION_DEPENDENT_COMPARISON",
    }


class FuturePullTests(unittest.TestCase):
    def test_typed_envelope_valid(self):
        f = FutureEnvelope((Dimension("stock", "resource_units", 8),), 4)
        self.assertTrue(f.validate({"stock": (9, "resource_units")}))

    def test_incompatible_units_rejected(self):
        f = FutureEnvelope((Dimension("stock", "resource_units", 8),), 4)
        with self.assertRaises(ValueError):
            f.validate({"stock": (9, "usd")})

    def test_unknown_dimension_rejected(self):
        f = FutureEnvelope((Dimension("stock", "resource_units", 8),), 4)
        with self.assertRaises(ValueError):
            f.validate({})

    def test_bounded_action(self):
        self.assertEqual(choose(6, 1000, adaptive=True), 12)
        self.assertEqual(choose(6, -1000, adaptive=True), 0)

    def test_accurate_forecast_can_help(self):
        result = compare([(10, 10), (3, 3)])
        self.assertLess(result["adaptive_total_loss"], result["static_total_loss"])

    def test_misleading_forecast_can_harm(self):
        result = compare([(10, 2), (3, 12)])
        self.assertGreater(result["adaptive_total_loss"], result["static_total_loss"])

    def test_no_oracle_when_signal_equals_static(self):
        result = compare([(10, 6), (2, 6)])
        self.assertEqual(result["adaptive_total_loss"], result["static_total_loss"])

    def test_rights_violation_is_separate_from_scalar_loss(self):
        result = compare([(10, 2)])
        self.assertEqual(result["rows"][0]["adaptive"]["rights_violations"], 1)
        self.assertEqual(result["rows"][0]["static"]["rights_violations"], 0)

    def test_deterministic_comparison(self):
        self.assertEqual(compare([(10, 10), (3, 3)]), compare([(10, 10), (3, 3)]))


if __name__ == "__main__":
    unittest.main()
