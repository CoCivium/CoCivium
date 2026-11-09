"""CoPullVector R0: synthetic counterfactual comparison; no real-world prediction or authority."""
from dataclasses import dataclass
from math import isfinite
import unittest

DIMENSIONS = ('agency', 'resilience', 'discovery')

@dataclass(frozen=True)
class Estimate:
    mean: float
    uncertainty: float
    def __post_init__(self):
        if not all(isfinite(v) for v in (self.mean, self.uncertainty)) or self.uncertainty < 0:
            raise ValueError('invalid estimate')

@dataclass(frozen=True)
class Action:
    name: str
    deltas: dict
    cost: float
    allowed: bool = True
    def __post_init__(self):
        if set(self.deltas) != set(DIMENSIONS) or not isfinite(self.cost) or self.cost < 0:
            raise ValueError('invalid dimensions or cost')
        if any(not isinstance(e, Estimate) for e in self.deltas.values()):
            raise TypeError('each dimension must have an Estimate')

def frontier(actions):
    """Conservative Pareto frontier using means, among authorized actions only.

    Pareto membership is *not* independent proof of merit; uncertainty is retained.
    """
    eligible = [a for a in actions if a.allowed]
    def dominates(b, a):
        advantages = [b.deltas[k].mean >= a.deltas[k].mean for k in DIMENSIONS]
        return all(advantages) and any(b.deltas[k].mean > a.deltas[k].mean for k in DIMENSIONS)
    return [a.name for a in eligible if not any(dominates(b, a) for b in eligible if b.name != a.name)]

def rank(actions, weights, budget):
    if set(weights) != set(DIMENSIONS) or any(not isfinite(w) or w < 0 for w in weights.values()):
        raise ValueError('invalid weights')
    if not isfinite(budget) or budget < 0:
        raise ValueError('invalid budget')
    eligible = [a for a in actions if a.allowed and a.cost <= budget]
    results = []
    for a in eligible:
        score = sum(weights[k] * a.deltas[k].mean for k in DIMENSIONS)
        error_bound = sum(weights[k] * a.deltas[k].uncertainty for k in DIMENSIONS)
        results.append((a.name, round(score, 4), round(error_bound, 4)))
    return sorted(results, key=lambda x: (-x[1], x[0]))

FIXTURE = [
    Action('A_access', {'agency': Estimate(4, 1), 'resilience': Estimate(0, 2), 'discovery': Estimate(1, 1)}, 3),
    Action('B_resilience', {'agency': Estimate(1, 1), 'resilience': Estimate(5, 1), 'discovery': Estimate(0, 2)}, 4),
    Action('C_discovery', {'agency': Estimate(0, 2), 'resilience': Estimate(1, 1), 'discovery': Estimate(6, 3)}, 5),
]

class CoPullTests(unittest.TestCase):
    def test_fixture_and_frontier(self):
        self.assertEqual(frontier(FIXTURE), ['A_access', 'B_resilience', 'C_discovery'])
    def test_conflicting_goals_change_rank(self):
        self.assertEqual(rank(FIXTURE, {'agency': 1, 'resilience': 0, 'discovery': 0}, 5)[0][0], 'A_access')
        self.assertEqual(rank(FIXTURE, {'agency': 0, 'resilience': 1, 'discovery': 0}, 5)[0][0], 'B_resilience')
        self.assertEqual(rank(FIXTURE, {'agency': 0, 'resilience': 0, 'discovery': 1}, 5)[0][0], 'C_discovery')
    def test_budget_and_consent_hard_gate(self):
        self.assertEqual([row[0] for row in rank(FIXTURE, dict.fromkeys(DIMENSIONS, 1), 3)], ['A_access'])
        denied = Action('prohibited', {k: Estimate(100, 0) for k in DIMENSIONS}, 0, False)
        self.assertNotIn('prohibited', [x[0] for x in rank(FIXTURE + [denied], dict.fromkeys(DIMENSIONS, 1), 100)])
    def test_uncertainty_remains_explicit(self):
        row = rank(FIXTURE, dict.fromkeys(DIMENSIONS, 1), 5)[0]
        self.assertEqual(row, ('C_discovery', 7, 6))
    def test_invalid_units_or_estimates_rejected(self):
        with self.assertRaises(ValueError): Estimate(1, -1)
        with self.assertRaises(ValueError): rank(FIXTURE, {'agency': 1}, 5)
        with self.assertRaises(ValueError): Action('bad', {'agency': Estimate(1, 1)}, 1)
    def test_no_dominance_from_strictly_worse_action(self):
        weak = Action('weak', {k: Estimate(-100, 1) for k in DIMENSIONS}, 1)
        self.assertNotIn('weak', frontier(FIXTURE + [weak]))

if __name__ == '__main__':
    unittest.main(verbosity=2)
