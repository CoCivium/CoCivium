"""G_dSide R0: falsifiable multi-objective comparison, NOT a value oracle.

Synthetic scenarios only. Inputs are declared outcome vectors; no cosmology,
religious premise, market facts, causal identification or governance authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

METRICS = ("flourishing", "resilience", "knowledge", "optionality", "cost", "harm")
HIGHER_IS_BETTER = ("flourishing", "resilience", "knowledge", "optionality")
LOWER_IS_BETTER = ("cost", "harm")

# These are deliberately synthetic and NOT evidence of real cultural consent,
# universal units, cross-community equivalence, or future causation.
SYNTHETIC_METRIC_CONTRACTS = {
    metric: f"fixture:gdside-r0:{metric}:unitless-index:v1"
    for metric in METRICS
}
SYNTHETIC_AFFECTED_SCOPE = "fixture:one-affected-population"
SYNTHETIC_RIGHTS_CONTEXT = "fixture:no-real-world-rights-granted"

@dataclass(frozen=True)
class Candidate:
    name: str
    outcomes: Mapping[str, float]
    rights_violation: bool = False
    # A shared word or metric label is not a shared measurement contract.
    metric_contracts: Mapping[str, str] = field(default_factory=dict)
    affected_scope: str = ""
    rights_context: str = ""
    cultural_transfer: bool = False
    source_community_ref: str = ""
    consent_ref: str = ""
    benefit_return_ref: str = ""

    def validate(self) -> None:
        if set(self.outcomes) != set(METRICS):
            raise ValueError("METRIC_SCHEMA_MISMATCH")
        if any(not isinstance(v, (float, int)) or not -1e9 < v < 1e9
               for v in self.outcomes.values()):
            raise ValueError("INVALID_FINITE_METRIC")
        if (set(self.metric_contracts) != set(METRICS) or
            any(not isinstance(v, str) or not v.strip()
                for v in self.metric_contracts.values())):
            raise ValueError("METRIC_CONTRACT_REQUIRED")
        if (not isinstance(self.affected_scope, str) or
            not self.affected_scope.strip() or
            not isinstance(self.rights_context, str) or
            not self.rights_context.strip()):
            raise ValueError("SITUATED_SCOPE_REQUIRED")
        # Strings are synthetic provenance pointers, NOT authenticated grants.
        # An appropriated symbol with intact wording can still transfer power,
        # benefit, and refusal rights. Missing provenance must HOLD.
        if not isinstance(self.cultural_transfer, bool):
            raise ValueError("CULTURAL_TRANSFER_CLASS_REQUIRED")
        if self.cultural_transfer and any(
            not isinstance(ref, str) or not ref.strip()
            for ref in (self.source_community_ref, self.consent_ref,
                        self.benefit_return_ref)
        ):
            raise ValueError("CULTURAL_TRANSFER_PROVENANCE_REQUIRED")


def same_comparison_contract(left: Candidate, right: Candidate) -> bool:
    return (left.metric_contracts == right.metric_contracts and
            left.affected_scope == right.affected_scope and
            left.rights_context == right.rights_context)


def dominates(left: Candidate, right: Candidate) -> bool:
    """Strict Pareto dominance only within one declared situated contract."""
    left.validate()
    right.validate()
    if left.rights_violation or right.rights_violation:
        raise ValueError("RIGHTS_GATED_BEFORE_COMPARISON")
    if not same_comparison_contract(left, right):
        raise ValueError("INCOMMENSURABLE_CONTEXT")
    weak = all(left.outcomes[m] >= right.outcomes[m] for m in HIGHER_IS_BETTER)
    weak &= all(left.outcomes[m] <= right.outcomes[m] for m in LOWER_IS_BETTER)
    strict = any(left.outcomes[m] > right.outcomes[m] for m in HIGHER_IS_BETTER)
    strict |= any(left.outcomes[m] < right.outcomes[m] for m in LOWER_IS_BETTER)
    return bool(weak and strict)


def frontier(candidates: list[Candidate]) -> list[str]:
    """Do not silently combine community/rights/measurement contexts."""
    for candidate in candidates:
        candidate.validate()
    valid = [c for c in candidates if not c.rights_violation]
    if valid and any(not same_comparison_contract(valid[0], c)
                     for c in valid[1:]):
        raise ValueError("INCOMMENSURABLE_CONTEXT")
    return sorted(c.name for c in valid
                  if not any(dominates(d, c) for d in valid if d is not c))


def interaction(values: Mapping[frozenset[str], float],
                base: frozenset[str], a: str, b: str) -> float:
    """Pair synergy is relative to the supplied value model."""
    if a == b or a in base or b in base:
        raise ValueError("INVALID_DISTINCT_INTERVENTIONS")
    return (values[base | {a,b}] - values[base | {a}]
            - values[base | {b}] + values[base])

def synthetic_candidate(name: str, values: tuple[float, ...], **kwargs) -> Candidate:
    """Explicit shared fixture contract; no real permissions or observations."""
    if len(values) != len(METRICS):
        raise ValueError("SYNTHETIC_VECTOR_LENGTH_MISMATCH")
    return Candidate(
        name, dict(zip(METRICS, values)),
        metric_contracts=dict(SYNTHETIC_METRIC_CONTRACTS),
        affected_scope=SYNTHETIC_AFFECTED_SCOPE,
        rights_context=SYNTHETIC_RIGHTS_CONTEXT,
        **kwargs,
    )


SCENARIOS = {
    "future_benefit": [
        synthetic_candidate("supply", (5,4,4,4,5,3)),
        synthetic_candidate("demand", (6,5,4,5,5,2)),
        synthetic_candidate("gdside", (8,7,6,8,4,1)),
    ],
    "backcast_overfit": [
        synthetic_candidate("supply", (7,7,6,7,3,1)),
        synthetic_candidate("demand", (5,5,6,5,5,3)),
        synthetic_candidate("gdside", (4,3,4,3,6,4)),
    ],
    "rights_veto": [
        synthetic_candidate("supply", (4,4,4,4,3,2)),
        synthetic_candidate("gdside", (10,10,10,10,1,0),
                            rights_violation=True),
    ],
}

if __name__ == "__main__":
    import json
    print(json.dumps({"epistemic_class": "SYNTHETIC", "not_runtime": True,
                      "pareto_frontiers": {key: frontier(value) for key, value in SCENARIOS.items()}},
                     sort_keys=True, indent=2))
