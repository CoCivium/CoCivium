"""CoFuture pull-vector R0: deterministic synthetic Pareto evaluator.

Source-level experiment only. No future causation, model authority, real-world
measurement, or independent receiver acceptance is implied.
"""
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Axis:
    id: str
    unit: str
    direction: str  # MAX or MIN
    horizon_days: int
    evidence_ref: str

    def validate(self):
        if not self.id or not self.unit or not self.evidence_ref:
            raise ValueError("missing axis identity, unit, or evidence")
        if self.direction not in ("MAX", "MIN") or self.horizon_days <= 0:
            raise ValueError("invalid direction or horizon")


@dataclass(frozen=True)
class Measure:
    axis_id: str
    unit: str
    value: float


@dataclass(frozen=True)
class Future:
    id: str
    lens: str
    measures: tuple
    consent: bool
    rights_ok: bool
    safety_ok: bool
    source_ref: str


def evaluate(axes, futures):
    """Return eligible nondominated alternatives, preserving value dimensions.

    Missing or mismatched observations are rejected, not estimated.
    Comparisons are strictly among alternatives using identical declared axes.
    """
    if not axes or not futures:
        raise ValueError("axes and futures required")
    for axis in axes:
        axis.validate()
    names = [a.id for a in axes]
    if len(names) != len(set(names)):
        raise ValueError("duplicate axis identity")
    axis_map = {a.id: a for a in axes}
    valid = []
    rejected = {}
    seen = set()
    for future in futures:
        if not future.id or future.id in seen:
            raise ValueError("missing or duplicate future identity")
        seen.add(future.id)
        if not future.consent or not future.rights_ok or not future.safety_ok:
            rejected[future.id] = "HARD_CONSTRAINT"
            continue
        if not future.source_ref or not future.lens:
            rejected[future.id] = "PROVENANCE_MISSING"
            continue
        measurements = {m.axis_id: m for m in future.measures}
        if len(measurements) != len(future.measures) or set(measurements) != set(axis_map):
            rejected[future.id] = "MISSING_OR_DUPLICATE_MEASURE"
            continue
        if any(m.unit != axis_map[k].unit or not isinstance(m.value, (int, float))
               or isinstance(m.value, bool) or not isfinite(m.value)
               for k, m in measurements.items()):
            rejected[future.id] = "UNIT_OR_VALUE_INVALID"
            continue
        valid.append((future, measurements))

    def dominates(left, right):
        better = False
        for axis in axes:
            x = left[axis.id].value
            y = right[axis.id].value
            signed = x-y if axis.direction == "MAX" else y-x
            if signed < 0:
                return False
            if signed > 0:
                better = True
        return better

    frontier = []
    dominated_by = {}
    for candidate, values in valid:
        dominators = sorted(other.id for other, others in valid
                            if other.id != candidate.id and dominates(others, values))
        if dominators:
            dominated_by[candidate.id] = dominators
        else:
            frontier.append(candidate.id)
    return {"frontier": sorted(frontier), "dominated_by": dominated_by,
            "rejected": rejected, "eligible_count": len(valid),
            "mode": "SYNTHETIC_PARETO_ONLY"}


if __name__ == "__main__":
    import unittest

    AXES = (Axis("habitat", "index", "MAX", 365, "source:h"),
            Axis("cost", "CAD", "MIN", 365, "source:c"))

    def f(name, habitat=3, cost=100, lens="HYBRID", **kw):
        args = dict(consent=True, rights_ok=True, safety_ok=True,
                    source_ref="fixture:synthetic")
        args.update(kw)
        return Future(name, lens, (Measure("habitat", "index", habitat),
                                   Measure("cost", "CAD", cost)), **args)

    class Tests(unittest.TestCase):
        def test_dominance(self):
            r=evaluate(AXES, [f("a", 4, 80), f("b", 3, 100)])
            self.assertEqual(r["frontier"], ["a"])
            self.assertEqual(r["dominated_by"]["b"], ["a"])

        def test_incomparable_are_both_retained(self):
            r=evaluate(AXES, [f("high-habitat", 5, 150),
                              f("low-cost", 3, 70)])
            self.assertEqual(r["frontier"], ["high-habitat", "low-cost"])

        def test_gdside_can_lose(self):
            r=evaluate(AXES, [f("gd", 2, 130, lens="G_D_SIDE"),
                              f("supply", 4, 80, lens="SUPPLY")])
            self.assertEqual(r["frontier"], ["supply"])
            self.assertIn("supply", r["dominated_by"]["gd"])

        def test_mismatched_unit_rejected_not_converted(self):
            bad=Future("bad", "DEMAND",
                       (Measure("habitat", "index", 4),
                        Measure("cost", "USD", 80)),
                       True, True, True, "fixture")
            self.assertEqual(evaluate(AXES, [bad])["rejected"]["bad"],
                             "UNIT_OR_VALUE_INVALID")

        def test_missing_measure_not_fabricated(self):
            bad=Future("bad", "DEMAND", (Measure("habitat", "index", 4),),
                       True, True, True, "fixture")
            self.assertEqual(evaluate(AXES, [bad])["rejected"]["bad"],
                             "MISSING_OR_DUPLICATE_MEASURE")

        def test_hard_constraints_precede_ranking(self):
            r=evaluate(AXES, [f("unsafe", 1000, 0, consent=False),
                              f("safe", 1, 100)])
            self.assertEqual(r["frontier"], ["safe"])
            self.assertEqual(r["rejected"]["unsafe"], "HARD_CONSTRAINT")

        def test_no_provenance_rejected(self):
            self.assertEqual(evaluate(AXES, [f("x", source_ref="")])
                             ["rejected"]["x"], "PROVENANCE_MISSING")

        def test_invalid_horizon_refused(self):
            with self.assertRaises(ValueError):
                evaluate((Axis("x", "kg", "MAX", 0, "fixture"),),
                         [Future("x", "HYBRID", (Measure("x", "kg", 1),),
                                 True, True, True, "fixture")])

        def test_duplicate_axes_refused(self):
            with self.assertRaises(ValueError):
                evaluate((AXES[0], AXES[0]), [f("x")])

        def test_nan_not_a_measurement(self):
            self.assertEqual(evaluate(AXES, [f("x", habitat=float("nan"))])
                             ["rejected"]["x"], "UNIT_OR_VALUE_INVALID")

    unittest.main(verbosity=2)
