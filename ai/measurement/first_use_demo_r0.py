#!/usr/bin/env python3
"""Public-safe CoMeasure/CoSpeedo first use, with synthetic observations only.

Uses the existing R0.1.2 registry and observation-domain gate.  Nothing is
transmitted, installed, sampled from a device, or written to disk.
"""
import hashlib
import json
from pathlib import Path

from observation_domain_r0 import validate_observation_domain
from verify_registry_r0_1 import parse_strict_json

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "registry_r0_1.json"


def observation(registry, metric_id, value, **changes):
    spec = next(m for m in registry["metric_families"] if m["id"] == metric_id)
    result = {
        "metric_id": metric_id,
        "quantity_kind": spec["quantity_kind"],
        "value_state": "MEASURED",
        "value": value,
        "unit_id": spec["unit_id"],
        "observed_at_utc": "2026-11-08T00:00:00Z",
        "observer_id": "synthetic:public-first-use",
        "source_id": "synthetic:made-up-example-not-a-measurement",
        "source_sha256": "a" * 64,  # Demonstrates format, NOT an authentic source hash.
        "interval_or_window": "synthetic:window-1",
        "uncertainty_kind": "NOT_ESTIMATED",
        "uncertainty_value_or_null": None,
        "method_or_null": "synthetic:illustration-not-calibration",
        "authority_scope": "synthetic:no-real-world-authority",
        "comparison_baseline_or_null": None,
    }
    result.update(changes)
    return result


def subset_counts(numerator, denominator, **changes):
    result = {
        "numerator": numerator,
        "denominator": denominator,
        "window_id": "synthetic:window-1",
        "scope_id": "synthetic:public-first-use",
        "count_kind": "qualified_delivery_and_exact_object_ack",
    }
    result.update(changes)
    return result


def main():
    source_bytes = SOURCE.read_bytes()
    registry = parse_strict_json(source_bytes.decode("utf-8-sig"))
    pickup = "CoMx.receiver_pickup_fraction"
    touch = "CoUX.human_touch_count"
    rate = "CoSpeedo.verified_useful_delta_rate"

    # Expected verdict is explicit; a rejected case passing is a failed demo.
    cases = [
        ("synthetic_3_of_4", pickup, "3/4", subset_counts("3", "4"), {}, "DOMAIN_CONSISTENT_ONLY"),
        ("fraction_exceeds_one", pickup, "5/4", subset_counts("5", "4"), {}, "FRACTION_ABOVE_ONE"),
        ("zero_denominator_not_zero_rate", pickup, "0", subset_counts("0", "0"), {}, "ZERO_DENOMINATOR_UNDEFINED"),
        ("wrong_window", pickup, "3/4", subset_counts("3", "4", window_id="synthetic:wrong-window"), {}, "WINDOW_MISMATCH"),
        ("two_synthetic_touches", touch, "2", None, {}, "DOMAIN_CONSISTENT_ONLY"),
        ("half_a_touch_rejected", touch, "1/2", None, {}, "FRACTIONAL_EVENT_COUNT"),
        ("unknown_is_not_zero", touch, "0", None, {"value_state": "UNKNOWN"}, "NULL_IS_NOT_ZERO"),
        ("illustrative_one_per_minute", rate, "1/60", None, {}, "DOMAIN_CONSISTENT_ONLY"),
    ]
    outcomes = []
    for name, metric_id, value, counts, edits, expected in cases:
        try:
            checked = validate_observation_domain(
                observation(registry, metric_id, value, **edits),
                registry,
                counts=counts,
            )
            observed = checked["state"]
        except ValueError as exc:
            observed = str(exc)
        passed = expected in observed
        outcomes.append({"case": name, "expected": expected, "observed": observed, "pass": passed})

    result = {
        "schema": "CoMeasure.PublicFirstUse.SyntheticR0",
        "scope": "SYNTHETIC_DOMAIN_DEMO_ONLY",
        "co_here_now": "Synthetic inputs tested; no real receiver pickup was attempted or proven.",
        "registry_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "passed": sum(x["pass"] for x in outcomes),
        "total": len(outcomes),
        "cases": outcomes,
        "next_proof": "Independent authenticated receiver reads a real permitted source and records its own exact-object ACK.",
        "nonclaims": [
            "NOT_REAL_RECEIVER_ACK", "NOT_LIVE_COSPEEDO", "NOT_LIVE_COORB",
            "NOT_REAL_TELEMETRY", "NOT_AUTHENTICATED_SOURCE", "NOT_CANON",
            "NOT_PRODUCTION_DEPLOYMENT", "NOT_SI_CERTIFIED",
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["passed"] != result["total"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
