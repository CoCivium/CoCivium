#!/usr/bin/env python3
"""CoMeasure scoped CoMx pickup adapter R0.1 (research draft, no effects).

The frozen R0 observation converter and CoLockStep baseline stay unchanged.
This opt-in boundary binds the population of a displayed pickup fraction to
the population underlying its counts. Caller strings are NOT authentication,
real delivery, distinct event proofs, or independent receiver ACK.
"""
from copy import deepcopy
import re

from observation_domain_r0 import OBS_KEYS, validate_observation_domain

SCOPED_METRIC = "CoMx.receiver_pickup_fraction"
POPULATION_FIELD = "population_scope_id"
SCOPE_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9:._-]{0,127}\Z")


def require(condition, reason):
    if not condition:
        raise ValueError("HOLD_COSCOPE_" + reason)


def _scope(value, reason):
    require(type(value) is str and SCOPE_PATTERN.fullmatch(value) is not None,
            reason)
    return value


def validate_scoped_pickup(observation, registry, *, counts):
    """Check declared population consistency, then old numeric domain gate.

    A pass is only coherent caller-supplied data. It cannot verify that the
    counts were actually measured in the declared population or window.
    """
    require(type(observation) is dict, "OBSERVATION_NOT_OBJECT")
    require(set(observation) == OBS_KEYS | {POPULATION_FIELD},
            "EXACT_SCOPED_ENVELOPE_REQUIRED")
    require(observation.get("metric_id") == SCOPED_METRIC,
            "UNSUPPORTED_SCOPED_METRIC")
    require(type(counts) is dict, "COUNTS_NOT_OBJECT")
    observation_scope = _scope(observation[POPULATION_FIELD],
                               "OBSERVATION_SCOPE_INVALID")
    count_scope = _scope(counts.get("scope_id"), "COUNT_SCOPE_INVALID")
    require(observation_scope == count_scope, "POPULATION_SCOPE_MISMATCH")

    # Do not mutate inputs. Existing validator enforces the numeric,
    # quantity-kind, UTC/window, bounded-subset and source-format constraints.
    base = {k: v for k, v in observation.items() if k != POPULATION_FIELD}
    domain = validate_observation_domain(base, registry, counts=counts)
    require(domain["state"] == "DOMAIN_CONSISTENT_ONLY",
            "UPSTREAM_DOMAIN_NOT_QUALIFIED")
    result = deepcopy(domain)
    result["state"] = "DOMAIN_AND_POPULATION_CONSISTENT_ONLY"
    result[POPULATION_FIELD] = observation_scope
    result["nonclaims"] = list(domain["nonclaims"]) + [
        "SCOPE_ID_CLAIM_NE_AUTHENTICATED_POPULATION",
        "MATCHING_SCOPE_STRINGS_NE_DISTINCT_EVENT_PROOF",
        "NO_INDEPENDENT_RECEIVER_READPROOF",
    ]
    return result
