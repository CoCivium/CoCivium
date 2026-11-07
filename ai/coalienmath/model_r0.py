"""CoAlienMath public R0: limited, synthetic mathematical examples.

These functions do not attest to live hardware, source truth, or consciousness.
Standard-library only; no file, network, environment, or process access.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite, log2
from typing import Callable, Hashable, Iterable, TypeVar

T = TypeVar("T")


class NullKind(str, Enum):
    UNKNOWN = "UNKNOWN"
    NOT_OBSERVED = "NOT_OBSERVED"
    OBSERVED_ZERO = "OBSERVED_ZERO"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    WITHHELD = "WITHHELD"
    PROVEN_ABSENT_IN_SCOPE = "PROVEN_ABSENT_IN_SCOPE"


@dataclass(frozen=True)
class QualifiedObservation:
    subject: str
    quantity_kind: str
    unit: str
    value: float | None
    null_kind: NullKind | None = None

    def __post_init__(self) -> None:
        if not self.subject or not self.quantity_kind or not self.unit:
            raise ValueError("Missing subject, quantity kind, or unit")
        if self.null_kind is None:
            if isinstance(self.value, bool) or not isinstance(self.value, (float, int)):
                raise ValueError("Numeric observation requires finite nonboolean value")
            if not isfinite(self.value):
                raise ValueError("Nonfinite observation forbidden")
        elif self.null_kind is NullKind.OBSERVED_ZERO:
            if self.value != 0 or isinstance(self.value, bool):
                raise ValueError("Observed-zero must carry numeric zero")
        elif self.value is not None:
            raise ValueError("Non-numeric null state cannot carry a numeric value")


def numeric_residual(predicted: QualifiedObservation, observed: QualifiedObservation) -> float:
    """Return signed residual for a finite toy comparable numeric sample.

    This fragment does not validate time windows, uncertainty, provenance or
    observer independence, so it cannot qualify production measurements.
    """
    comparable = (
        predicted.subject == observed.subject
        and predicted.quantity_kind == observed.quantity_kind
        and predicted.unit == observed.unit
    )
    if not comparable:
        raise ValueError("Incompatible measurands or units")
    if predicted.null_kind not in (None, NullKind.OBSERVED_ZERO):
        raise ValueError("Prediction is null or withheld")
    if observed.null_kind not in (None, NullKind.OBSERVED_ZERO):
        raise ValueError("Observed outcome is null or withheld")
    if predicted.value is None or observed.value is None:
        raise ValueError("Numeric observation missing despite declared non-null state")
    return float(observed.value - predicted.value)


def decision_preserving(
    states: Iterable[T],
    encode: Callable[[T], Hashable],
    decide: Callable[[T], Hashable],
) -> bool:
    """Finite decision-factorization criterion over explicitly supplied cases."""
    decisions_by_code: dict[Hashable, Hashable] = {}
    for state in states:
        code, answer = encode(state), decide(state)
        if code in decisions_by_code and decisions_by_code[code] != answer:
            return False
        decisions_by_code[code] = answer
    return True


def authorized_transform(source_permissions: frozenset[str], target_permissions: frozenset[str]) -> bool:
    """Projection is authorized only when it does not grant extra permissions."""
    return target_permissions <= source_permissions


def distinguishable_by(world_a: T, world_b: T, observation: Callable[[T], Hashable]) -> bool:
    """Separate two candidates only if a supplied observation has different outputs."""
    return observation(world_a) != observation(world_b)


def count_failure_domains(witness_domains: Iterable[str]) -> int:
    """Deduplicate claimed witnesses by their explicitly assigned failure domain."""
    domains = list(witness_domains)
    if not domains or any(not x for x in domains):
        raise ValueError("Independent domains cannot be inferred from missing labels")
    return len(set(domains))


def likelihood_evidence_bits(p_e_given_h: float, p_e_given_not_h: float) -> float:
    """Log likelihood ratio in bits, only with specified valid probabilities.

    This is not a probability of truth and must not be summed over dependent
    observations without a joint or conditional model.
    """
    probs = (p_e_given_h, p_e_given_not_h)
    if any(isinstance(p, bool) or not isinstance(p, (int, float)) or not isfinite(p) or p <= 0 or p > 1 for p in probs):
        raise ValueError("Likelihoods must be finite nonzero probabilities")
    return log2(p_e_given_h / p_e_given_not_h)


def gauge_equivalent(quantity: float, gains: tuple[float, ...], scale: float) -> bool:
    """Algebraic non-identifiability example e_i = a_i * x."""
    if scale == 0 or not all(isfinite(y) for y in (quantity, *gains, scale)):
        raise ValueError("Invalid calibration scale")
    original = tuple(g * quantity for g in gains)
    reparameterized = tuple((g / scale) * (quantity * scale) for g in gains)
    return all(abs(a - b) <= 1e-10 for a, b in zip(original, reparameterized))


def three_binary_inequalities_globally_satisfiable() -> bool:
    """Each inequality over {0,1} is possible, but the odd cycle is not."""
    return any(a != b and b != c and c != a for a in (0, 1) for b in (0, 1) for c in (0, 1))
