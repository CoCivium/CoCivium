"""Small competing plain-JSON decision engine for finite CoAlienMath R0C fixtures.

Synthetic comparison only. This module intentionally does not import CoPriMath.
It makes no network, file, process, or device calls. The caller supplies parsed JSON.
"""
from __future__ import annotations

import math

NULLS = frozenset({
    "UNKNOWN", "NOT_OBSERVED", "OBSERVED_ZERO", "NOT_APPLICABLE",
    "WITHHELD", "PROVEN_ABSENT_IN_SCOPE",
})


def _real(value):
    return type(value) in (int, float) and math.isfinite(value)


def observation(data):
    if type(data) is not dict or set(data) != {"subject", "quantity_kind", "unit", "value", "null_kind"}:
        raise ValueError("Bad observation shape")
    if any(type(data[key]) is not str or not data[key].strip() for key in ("subject", "quantity_kind", "unit")):
        raise ValueError("Bad typed labels")
    kind, value = data["null_kind"], data["value"]
    if kind is None:
        if not _real(value):
            raise ValueError("Bad real value")
    elif type(kind) is not str or kind not in NULLS:
        raise ValueError("Bad null kind")
    elif kind == "OBSERVED_ZERO":
        if not _real(value) or value != 0:
            raise ValueError("Bad observed zero")
    elif value is not None:
        raise ValueError("Absent result has value")
    return data


def evaluate(row):
    """Return HOLD, ALLOW, BLOCK, TRUE, FALSE, or a finite number/count.

    HOLD is non-acceptance; assertions of truth/authority are not made here.
    """
    if type(row) is not dict or type(row.get("op")) is not str:
        return "HOLD"
    op = row["op"]
    try:
        if op == "observation":
            observation(row["item"])
            return "ALLOW"
        if op == "residual":
            left, right = observation(row["predicted"]), observation(row["observed"])
            if any(left[k] != right[k] for k in ("subject", "quantity_kind", "unit")):
                raise ValueError("Wrong measurand")
            if any(x["null_kind"] not in (None, "OBSERVED_ZERO") for x in (left, right)):
                raise ValueError("Not numeric")
            delta = right["value"] - left["value"]
            if not _real(delta):
                raise ValueError("Nonfinite difference")
            return float(delta)
        if op == "bits":
            a, b = row["p_h"], row["p_not_h"]
            if not _real(a) or not _real(b) or not (0 < a <= 1 and 0 < b <= 1):
                raise ValueError("Bad probabilities")
            val = math.log2(a) - math.log2(b)
            if not math.isfinite(val):
                raise ValueError("Nonfinite evidence")
            return val
        if op == "permission":
            source, target = row["source"], row["target"]
            if any(type(x) is not list or any(type(v) is not str or not v for v in x) for x in (source, target)):
                raise ValueError("Bad permission list")
            return "ALLOW" if set(target) <= set(source) else "BLOCK"
        if op == "witnesses":
            witnesses = row["domains"]
            if type(witnesses) is not list or not witnesses or any(type(v) is not str or not v.strip() for v in witnesses):
                raise ValueError("Bad witness label")
            return len(set(witnesses))
        if op == "decision":
            pairs = row["pairs"]
            if type(pairs) is not list or not pairs:
                raise ValueError("Bad factorization input")
            by_code = {}
            for pair in pairs:
                if type(pair) is not dict or set(pair) != {"code", "decision"}:
                    raise ValueError("Bad pair")
                code, decision = pair["code"], pair["decision"]
                if type(code) is not str or type(decision) is not str:
                    raise ValueError("Bad pair type")
                if code in by_code and by_code[code] != decision:
                    return "FALSE"
                by_code[code] = decision
            return "TRUE"
        if op == "distinguish":
            for key in ("first", "second"):
                if type(row[key]) is not str:
                    raise ValueError("Bad observation")
            return "TRUE" if row["first"] != row["second"] else "FALSE"
    except (ValueError, TypeError, KeyError, OverflowError, ZeroDivisionError):
        return "HOLD"
    return "HOLD"
