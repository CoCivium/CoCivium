#!/usr/bin/env python3
"""CoStretch+ R1: offline index-only illustration (not a research benchmark).
No model calls, network use, sessions, or actual experimental execution.
"""
from math import prod

DIMENSIONS = (
    ("role", 8), ("substrate", 5), ("effect", 4), ("authority", 4),
    ("confidentiality", 3), ("model_family", 6), ("source_family", 6),
    ("task_type", 8), ("verification", 5), ("resource_policy", 6),
    ("experiment", 6), ("storage", 6), ("view", 5), ("fault", 5),
    ("time_window", 4), ("context", 4), ("observer_frame", 7),
    ("coding_scheme", 6), ("counterfactual", 5),
)


def capacity():
    return prod(size for _, size in DIMENSIONS)


def unrank(index):
    cap = capacity()
    if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < cap:
        raise ValueError("INDEX_OUT_OF_RANGE")
    result = {}
    for name, size in reversed(DIMENSIONS):
        index, digit = divmod(index, size)
        result[name] = digit
    return {name: result[name] for name, _ in DIMENSIONS}


def rank(digits):
    if set(digits) != {name for name, _ in DIMENSIONS}:
        raise ValueError("DIMENSIONS_MISMATCH")
    index = 0
    for name, size in DIMENSIONS:
        digit = digits[name]
        if isinstance(digit, bool) or not isinstance(digit, int) or not 0 <= digit < size:
            raise ValueError("INVALID_DIGIT")
        index = index * size + digit
    return index


if __name__ == "__main__":
    import json
    n = capacity()
    witness = {str(i): rank(unrank(i)) for i in (0, n // 2, n - 1)}
    assert all(int(k) == v for k, v in witness.items())
    print(json.dumps({
        "logical_combinations": n,
        "witness_indices": witness,
        "actual_experiments_run": 0,
        "provider_requests": 0,
        "warning": "Index capacity is not research output or scalability evidence.",
    }, indent=2))
