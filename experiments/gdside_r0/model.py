"""G_dSide R0: falsifiable multi-objective comparison, NOT a value oracle.

Synthetic scenarios only. Inputs are declared outcome vectors; no cosmology,
religious premise, market facts, causal identification or governance authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

METRICS = ("flourishing", "resilience", "knowledge", "optionality", "cost", "harm")
HIGHER_IS_BETTER = ("flourishing", "resilience", "knowledge", "optionality")
LOWER_IS_BETTER = ("cost", "harm")

@dataclass(frozen=True)
class Candidate:
    name: str
    outcomes: Mapping[str, float]
    rights_violation: bool = False

    def validate(self) -> None:
        if set(self.outcomes) != set(METRICS):
            raise ValueError("METRIC_SCHEMA_MISMATCH")
        if any(not isinstance(v, (float, int)) or not -1e9 < v < 1e9
               for v in self.outcomes.values()):
            raise ValueError("INVALID_FINITE_METRIC")

def dominates(left: Candidate, right: Candidate) -> bool:
    """Strict Pareto dominance on raw comparable metrics; never reward a label."""
    left.validate()
    right.validate()
    if left.rights_violation or right.rights_violation:
        raise ValueError("RIGHTS_GATED_BEFORE_COMPARISON")
    weak = all(left.outcomes[m] >= right.outcomes[m] for m in HIGHER_IS_BETTER)
    weak &= all(left.outcomes[m] <= right.outcomes[m] for m in LOWER_IS_BETTER)
    strict = any(left.outcomes[m] > right.outcomes[m] for m in HIGHER_IS_BETTER)
    strict |= any(left.outcomes[m] < right.outcomes[m] for m in LOWER_IS_BETTER)
    return bool(weak and strict)

def frontier(candidates: list[Candidate]) -> list[str]:
    """Report nondominated options only; violating candidates cannot win."""
    valid = [c for c in candidates if not c.rights_violation]
    for c in candidates:
        c.validate()
    return sorted(c.name for c in valid
                  if not any(dominates(d, c) for d in valid if d is not c))

def interaction(values: Mapping[frozenset[str], float],
                base: frozenset[str], a: str, b: str) -> float:
    """Pair synergy is relative to the supplied value model."""
    if a == b or a in base or b in base:
        raise ValueError("INVALID_DISTINCT_INTERVENTIONS")
    return (values[base | {a,b}] - values[base | {a}]
            - values[base | {b}] + values[base])

SCENARIOS = {
    # The hypothetical future-backcast approach is strictly better here.
    "future_benefit": [
        Candidate("supply", dict(zip(METRICS, (5,4,4,4,5,3)))),
        Candidate("demand", dict(zip(METRICS, (6,5,4,5,5,2)))),
        Candidate("gdside", dict(zip(METRICS, (8,7,6,8,4,1)))),
    ],
    # It loses here. A proof harness must not guarantee its own victory.
    "backcast_overfit": [
        Candidate("supply", dict(zip(METRICS, (7,7,6,7,3,1)))),
        Candidate("demand", dict(zip(METRICS, (5,5,6,5,5,3)))),
        Candidate("gdside", dict(zip(METRICS, (4,3,4,3,6,4)))),
    ],
    "rights_veto": [
        Candidate("supply", dict(zip(METRICS, (4,4,4,4,3,2)))),
        Candidate("gdside", dict(zip(METRICS, (10,10,10,10,1,0))), rights_violation=True),
    ],
}
if __name__ == "__main__":
    import json
    print(json.dumps({"epistemic_class": "SYNTHETIC", "not_runtime": True,
                      "pareto_frontiers": {key: frontier(value) for key, value in SCENARIOS.items()}},
                     sort_keys=True, indent=2))
