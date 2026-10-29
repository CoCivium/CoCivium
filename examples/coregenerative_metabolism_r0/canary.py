#!/usr/bin/env python3
"""CoRegenerativeMetabolism R0: finite synthetic anti-drain and control comparison.

No runtime, public recipient, ET detector, energetic field, or financial result is inferred.
These unitless toy variables are not interchangeable with physical energy or wellbeing.
"""
import json
from pathlib import Path

STEPS = 24
SCHEMA = "CoAll.CoRegenerativeMetabolism.SyntheticCanary.R0"


def clamp(x, lo, hi):
    return min(hi, max(lo, x))


def decay_only():
    amplitude = 1.0
    out = []
    for cycle in range(STEPS):
        amplitude *= 0.84
        out.append({"cycle": cycle + 1, "activity": round(amplitude, 8),
                    "useful_proxy": round(amplitude * 0.82, 8)})
    return {"case": "PASSIVE_DAMPING", "evidence_class": "SYNTHETIC",
            "status": "NO_DRIVE", "series": out}


def uncorrected_feedback():
    amplitude = 1.0
    error = 0.12
    out = []
    for cycle in range(STEPS):
        # Deliberate failure fixture: rising activity has no resource ledger or limiter.
        amplitude *= 1.28
        error = clamp(error + 0.045, 0, 1)
        out.append({"cycle": cycle + 1, "activity": round(amplitude, 8),
                    "error_proxy": round(error, 8),
                    "useful_proxy": round(amplitude * (1 - error), 8),
                    "beyond_safe_activity_limit": amplitude > 2.1})
    return {"case": "UNLIMITED_GAIN_WITHOUT_CORRECTION", "evidence_class": "SYNTHETIC",
            "status": "EXPECTED_UNSAFE_REFERENCE", "series": out}


def bounded_regeneration(shock_cycle=None):
    amplitude = 1.0
    error = 0.25
    budget = 2.0
    resource_input = 0.33
    maintenance_cost = 0.02
    receiver_feedback = 0.72  # fixed synthetic fixture, never a human measurement
    out = []
    for cycle in range(STEPS):
        if shock_cycle is not None and cycle + 1 == shock_cycle:
            error = clamp(error + 0.65, 0, 1)
        # A bad-quality observation pauses additional driving, but not correction.
        drive = 0.0 if error > 0.45 else min(0.28, max(0, budget + resource_input - 1.0))
        gain_per_input = (0.60 + 0.40 * receiver_feedback) * (1 - error)
        next_amplitude = clamp(0.86 * amplitude + drive * gain_per_input, 0.0, 2.1)
        correction = 0.18 if error > 0.35 else 0.015
        error = clamp(0.78 * error + 0.04 - correction, 0, 1)
        budget += resource_input - drive - maintenance_cost
        amplitude = next_amplitude
        out.append({
            "cycle": cycle + 1,
            "activity": round(amplitude, 8),
            "error_proxy": round(error, 8),
            "useful_proxy": round(amplitude * (1 - error), 8),
            "funded_input": resource_input,
            "drive_spend": round(drive, 8),
            "maintenance_spend": maintenance_cost,
            "available_budget": round(budget, 8),
            "correction_mode": "EXPLICIT_ERROR_DAMPING" if correction > 0.015 else "BASELINE"
        })
    return {
        "case": "BOUNDED_REGENERATIVE_LOOP" if shock_cycle is None else "BOUNDED_WITH_SYNTHETIC_SHOCK",
        "evidence_class": "SYNTHETIC",
        "status": "BOUNDED_TOY_MODEL_NOT_REAL_WORLD_PROOF",
        "inputs": {"steps": STEPS, "initial_amplitude": 1.0, "initial_error": 0.25,
                   "initial_budget": 2.0, "funded_external_input_per_cycle": resource_input,
                   "maintenance_cost_per_cycle": maintenance_cost,
                   "receiver_feedback_fixture": receiver_feedback,
                   "amplitude_limit": 2.1, "resource_reserve": 1.0, "shock_cycle": shock_cycle},
        "series": out
    }


def execute():
    cohort = json.loads((Path(__file__).resolve().parent / "cohort.json").read_text(encoding="utf-8"))
    assert cohort["asset_count"] == len(cohort["assets"]) == 12
    scenarios = [decay_only(), uncorrected_feedback(), bounded_regeneration(),
                 bounded_regeneration(shock_cycle=8)]
    last = scenarios[2]["series"]
    return {
        "schema": SCHEMA,
        "scope": "UNIT_TEST_FIXTURE_WITH_NO_REAL_RECEIVERS_OR_PHYSICAL_ENERGY_CLAIMS",
        "source_cohort_count": len(cohort["assets"]),
        "scenarios": scenarios,
        "comparison": {
            "passive_final_activity": scenarios[0]["series"][-1]["activity"],
            "uncorrected_final_activity": scenarios[1]["series"][-1]["activity"],
            "bounded_final_activity": last[-1]["activity"],
            "bounded_final_useful_proxy": last[-1]["useful_proxy"],
            "bounded_peak_activity": max(x["activity"] for x in last),
            "bounded_min_budget": min(x["available_budget"] for x in last),
            "bounded_max_error": max(x["error_proxy"] for x in last)
        },
        "nonclaims": ["SYNTHETIC_READER_FEEDBACK_NE_ACTUAL_RECEIVER_USE",
                      "REGENERATION_NE_UNLIMITED_ENERGY",
                      "STABLE_LIMIT_CYCLE_NE_DEAD_SYSTEM",
                      "SUSTAINED_ACTIVITY_NE_VERIFIED_IMPACT",
                      "RUNAWAY_ACTIVITY_NE_BENEFIT",
                      "MODEL_PASS_NE_PHYSICS_GD_ET_PROOF",
                      "SOURCE_PRESENT_NE_RUNTIME",
                      "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF"]
    }


if __name__ == "__main__":
    print(json.dumps(execute(), indent=2, sort_keys=True))
