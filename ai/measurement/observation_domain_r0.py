#!/usr/bin/env python3
"""R0.1.2 CoMeasure observation-domain gate (public-safe research candidate).

This checks *internal numerical admissibility*, not real observation, source
signatures, operator identities, SI calibration, or receiver ACKs.  In particular,
Fraction-based unit conversion does not make an empirical claim credible.
"""
from datetime import datetime, timezone
from fractions import Fraction
import re

from verify_registry_r0_1 import validate_registry, require

PROFILE = {
    "CoTime.source_age": ("signed", "duration"),
    "CoSpeedo.verified_useful_delta_rate": ("nonnegative", "event_rate"),
    "CoMx.receiver_pickup_fraction": ("bounded_subset", "fraction_of_whole"),
    "CoUX.human_touch_count": ("nonnegative_integer", "event_count"),
    "CoResilience.mean_time_to_restore": ("nonnegative", "duration"),
    "CoEnergy.useful_delta_per_joule": ("nonnegative", "event_per_energy"),
    "CoReach.failure_domain_coverage": ("nonnegative_integer", "failure_domain_count"),
}

OBS_KEYS = {
    "metric_id", "quantity_kind", "value_state", "value", "unit_id",
    "observed_at_utc", "observer_id", "source_id", "source_sha256",
    "interval_or_window", "uncertainty_kind", "uncertainty_value_or_null",
    "method_or_null", "authority_scope", "comparison_baseline_or_null",
}
COUNT_KEYS = {"numerator", "denominator", "window_id", "scope_id", "count_kind"}


def exact_number(raw, label):
    require(type(raw) is str and 0 < len(raw) <= 80, (label, "EXACT_STRING_REQUIRED"))
    require(bool(re.fullmatch(r"-?(?:\d+)(?:/\d+|\.\d+)?", raw)), (label, "DECIMAL_OR_RATIONAL_REQUIRED"))
    try:
        return Fraction(raw)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError("HOLD_INVALID_EXACT_NUMBER: " + label) from exc


def nonnegative_integer(raw, label):
    value = exact_number(raw, label)
    require(value >= 0 and value.denominator == 1, (label, "NONNEGATIVE_INTEGER_REQUIRED"))
    return value


def validate_observation_domain(observation, registry, *, counts=None):
    """Return a scoped domain check; never certify evidence or a benchmark winner."""
    validate_registry(registry)
    require(type(observation) is dict and set(observation) == OBS_KEYS, "OBSERVATION_ENVELOPE")
    metric_id = observation["metric_id"]
    require(metric_id in PROFILE, "UNSUPPORTED_METRIC_ID")
    policy, expected_kind = PROFILE[metric_id]
    specs = {m["id"]: m for m in registry["metric_families"]}
    require(metric_id in specs, "UNREGISTERED_METRIC")
    spec = specs[metric_id]
    require(spec["quantity_kind"] == expected_kind, "METRIC_PROFILE_KIND_MISMATCH")
    require(observation["quantity_kind"] == expected_kind, "OBSERVED_QUANTITY_KIND_MISMATCH")
    require(observation["unit_id"] == spec["unit_id"], "OBSERVED_UNIT_MUST_MATCH_METRIC")
    require(observation["value_state"] in ("MEASURED", "OBSERVED_ZERO"), "NULL_IS_NOT_ZERO")
    for key in ("observed_at_utc", "observer_id", "source_id", "interval_or_window", "uncertainty_kind", "authority_scope"):
        require(type(observation[key]) is str and bool(observation[key].strip()), (key,"REQUIRED"))
    require(type(observation["source_sha256"]) is str and
            re.fullmatch(r"[a-f0-9]{64}", observation["source_sha256"]) is not None,
            "SOURCE_HASH_FORMAT")
    for key in ("method_or_null", "comparison_baseline_or_null"):
        v = observation[key]
        require(v is None or (type(v) is str and bool(v.strip())), (key,"OPTIONAL_STRING"))
    require(observation["uncertainty_kind"] in
            ("NOT_ESTIMATED", "REPORTED_STD", "REPORTED_HALF_WIDTH"),
            "UNKNOWN_UNCERTAINTY_KIND")
    if observation["uncertainty_kind"] == "NOT_ESTIMATED":
        require(observation["uncertainty_value_or_null"] is None,
                "UNESTIMATED_UNCERTAINTY_HAS_VALUE")
    else:
        require(observation["uncertainty_value_or_null"] is not None,
                "REPORTED_UNCERTAINTY_MISSING")
        require(exact_number(observation["uncertainty_value_or_null"], "uncertainty") >= 0,
                "NEGATIVE_UNCERTAINTY")
    try:
        instant = datetime.fromisoformat(observation["observed_at_utc"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("HOLD_INVALID_OBSERVATION_TIMESTAMP") from exc
    require(instant.tzinfo is not None and instant.utcoffset().total_seconds() == 0,
            "OBSERVATION_TIMESTAMP_NOT_UTC")
    value = exact_number(observation["value"], "value")
    if observation["value_state"] == "OBSERVED_ZERO":
        require(value == 0, "FALSE_OBSERVED_ZERO")
    if policy != "signed":
        require(value >= 0, "NEGATIVE_OUTCOME")
    if policy == "nonnegative_integer":
        require(value.denominator == 1, "FRACTIONAL_EVENT_COUNT")
    if policy == "bounded_subset":
        require(value <= 1, "FRACTION_ABOVE_ONE")
        require(type(counts) is dict and set(counts) == COUNT_KEYS, "SUBSET_COUNTS_REQUIRED")
        require(type(counts["scope_id"]) is str and bool(counts["scope_id"]), "SCOPE_REQUIRED")
        require(counts["window_id"] == observation["interval_or_window"], "WINDOW_MISMATCH")
        require(counts["count_kind"] == "qualified_delivery_and_exact_object_ack", "COUNT_KIND_MISMATCH")
        n = nonnegative_integer(counts["numerator"], "numerator")
        d = nonnegative_integer(counts["denominator"], "denominator")
        require(d > 0, "ZERO_DENOMINATOR_UNDEFINED")
        require(n <= d, "ACKS_EXCEED_QUALIFIED_DELIVERIES")
        require(value == n / d, "FRACTION_COUNTS_DISAGREE")
    else:
        require(counts is None, "UNEXPECTED_COUNT_CONTEXT")
    return {
        "state": "DOMAIN_CONSISTENT_ONLY",
        "metric_id": metric_id, "quantity_kind": expected_kind,
        "unit_id": spec["unit_id"], "value_exact": str(value),
        "nonclaims": ["NO_SOURCE_AUTHENTICATION", "NO_INDEPENDENT_RECEIVER_ACK",
                      "NO_UNCERTAINTY_PROPAGATION", "NOT_SI_CERTIFIED",
                      "NO_CAUSAL_OR_PUBLIC_BENCHMARK_CLAIM"],
    }