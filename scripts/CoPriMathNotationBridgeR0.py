#!/usr/bin/env python3
"""CoPriMath / CoMeasure R0: exact typed quantities and notation projections.

Restricted, standards-informed illustrative bridge, NOT a universal parser,
SI certification, formal proof assistant, scientific result, or live system.
No network, credentials, file writes, external actions, or eval/exec.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from fractions import Fraction
import hashlib
import json
import re
from xml.etree import ElementTree as ET

SCHEMA = "CoPriMath.Measurement.R0"
CANONICAL = "CoPriMath.CanonicalQuantity.R0"
DERIVATION = "CoPriMath.Derivation.R0"
NS = "http://www.w3.org/1998/Math/MathML"

# The dimensions and unit scales form a deliberately tiny SI-based subset.
# These are not arbitrary contextual measures or affine/logarithmic units.
DIMS = {
    "length": {"L": 1},
    "duration": {"T": 1},
    "speed": {"L": 1, "T": -1},
    "ratio": {},
    "probability": {},
}
BASE_UNITS = {
    "length": "m", "duration": "s", "speed": "m/s",
    "ratio": "1", "probability": "1",
}
UNIT_SCALES = {
    "length": {"m": Fraction(1), "km": Fraction(1000)},
    "duration": {"s": Fraction(1), "min": Fraction(60)},
    "speed": {"m/s": Fraction(1), "km/h": Fraction(5, 18)},
    "ratio": {"1": Fraction(1), "%": Fraction(1, 100)},
    "probability": {"1": Fraction(1), "%": Fraction(1, 100)},
}
PRESENT = {"OBSERVED_CLAIM", "EXACT_ZERO_CLAIM"}
MISSING = {
    "UNKNOWN", "NOT_TESTED", "NOT_APPLICABLE", "BELOW_DETECTION",
    "WITHHELD", "CENSORED", "UNDEFINED",
}
FIELDS = {
    "schema", "quantity_kind", "unit", "value", "epistemic_state",
    "source_ref", "observed_at_utc",
}


class Hold(ValueError):
    """One bounded input failed closed without changing source."""


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise Hold(reason)


def exact_fraction(obj: object) -> Fraction:
    require(type(obj) is dict and set(obj) == {"n", "d"}, "INVALID_RATIONAL")
    require(type(obj["n"]) is int and type(obj["d"]) is int,
            "NON_INTEGER_RATIONAL")
    require(obj["d"] > 0, "INVALID_DENOMINATOR")
    require(len(str(obj["n"])) <= 50 and len(str(obj["d"])) <= 50,
            "RATIONAL_SIZE_BUDGET")
    return Fraction(obj["n"], obj["d"])


def rational_record(v: Fraction) -> dict:
    return {"n": v.numerator, "d": v.denominator}


def validate(m: object) -> Fraction | None:
    require(type(m) is dict and set(m) == FIELDS, "INVALID_FIELDS")
    require(m["schema"] == SCHEMA, "BAD_SCHEMA")
    kind = m["quantity_kind"]
    require(type(kind) is str and kind in UNIT_SCALES, "UNSUPPORTED_KIND")
    unit = m["unit"]
    require(type(unit) is str and unit in UNIT_SCALES[kind], "INCOMPATIBLE_UNIT")
    status = m["epistemic_state"]
    require(type(status) is str and status in PRESENT | MISSING,
            "INVALID_EPISTEMIC_STATE")
    source = m["source_ref"]
    require(type(source) is str and 1 <= len(source) <= 256
            and re.fullmatch(r"[A-Za-z][A-Za-z0-9_:/.@#-]*", source),
            "SOURCE_REF_REQUIRED")
    when = m["observed_at_utc"]
    require(type(when) is str and when.endswith("Z"), "UTC_TIMESTAMP_REQUIRED")
    try:
        instant = datetime.fromisoformat(when.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Hold("INVALID_OBSERVATION_TIME") from exc
    require(instant.utcoffset() == timedelta(0), "NON_UTC_OBSERVATION_TIME")
    if status in MISSING:
        require(m["value"] is None, "MISSING_STATE_CANNOT_CARRY_NUMBER")
        return None
    value = exact_fraction(m["value"])
    if status == "EXACT_ZERO_CLAIM":
        require(value == 0, "EXACT_ZERO_REQUIRES_ZERO")
    if kind == "probability":
        # Probability claims must carry a bounded scalar, unlike generic ratio.
        require(0 <= value * UNIT_SCALES[kind][unit] <= 1,
                "PROBABILITY_OUT_OF_RANGE")
    return value


def canonical(m: dict) -> dict:
    """Normalize a typed statement into exact SI-based rational coordinates.

    Source claims remain claims: no instrument was read, no calibration checked.
    The canonical identity retains kind, source and observation time.
    """
    v = validate(m)
    kind = m["quantity_kind"]
    scaled = None if v is None else rational_record(v * UNIT_SCALES[kind][m["unit"]])
    return {
        "schema": CANONICAL,
        "quantity_kind": kind,
        "dimension_vector": DIMS[kind],
        "base_unit": BASE_UNITS[kind],
        "exact_base_value": scaled,
        "epistemic_state": m["epistemic_state"],
        "source_ref": m["source_ref"],
        "observed_at_utc": m["observed_at_utc"],
        "independent_calibration": "NOT_TESTED",
        "source_truth": "CLAIM_ONLY",
    }


def canonical_digest(m: dict) -> str:
    b = json.dumps(canonical(m), sort_keys=True, ensure_ascii=True,
                   separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def convert(m: dict, unit: str) -> dict:
    validate(m)
    kind = m["quantity_kind"]
    require(type(unit) is str and unit in UNIT_SCALES[kind], "INCOMPATIBLE_UNIT")
    require(m["value"] is not None, "NON_NUMERIC_STATE_HOLD")
    v = exact_fraction(m["value"])
    new = v * UNIT_SCALES[kind][m["unit"]] / UNIT_SCALES[kind][unit]
    out = dict(m)
    out["unit"] = unit
    out["value"] = rational_record(new)
    require(canonical_digest(out) == canonical_digest(m),
            "SEMANTIC_DRIFT")
    return out


def derive(operator: str, left: dict, right: dict) -> dict:
    """A tiny explicitly scoped operator table, never arbitrary expression eval."""
    a = canonical(left)
    b = canonical(right)
    require(a["exact_base_value"] is not None
            and b["exact_base_value"] is not None, "NO_VALUE_TO_DERIVE")
    if operator == "ADD":
        require(a["quantity_kind"] == b["quantity_kind"], "KIND_MISMATCH")
        kind = a["quantity_kind"]
        fn = lambda x, y: x + y
    elif operator == "MULTIPLY":
        kinds = frozenset((a["quantity_kind"], b["quantity_kind"]))
        require(kinds == {"speed", "duration"}, "MULTIPLY_SIGNATURE_UNSUPPORTED")
        kind = "length"
        fn = lambda x, y: x * y
    else:
        raise Hold("OPERATOR_NOT_REGISTERED")
    v = fn(exact_fraction(a["exact_base_value"]),
           exact_fraction(b["exact_base_value"]))
    if kind == "probability":
        require(0 <= v <= 1, "PROBABILITY_OUT_OF_RANGE")
    return {
        "schema": DERIVATION,
        "operator": operator,
        "result_kind": kind,
        "base_unit": BASE_UNITS[kind],
        "dimension_vector": DIMS[kind],
        "exact_base_value": rational_record(v),
        "evidence_status": "DERIVED_FROM_UNVERIFIED_SOURCE_CLAIMS",
        "input_semantic_digests": [canonical_digest(left), canonical_digest(right)],
        "effect_authority": "NONE",
        "physical_effects": 0,
        "receiver_ack": "NOT_OBSERVED",
    }


def ascii_projection(m: dict) -> str:
    validate(m)
    if m["value"] is None:
        return m["epistemic_state"] + " [" + m["quantity_kind"] + "]"
    f = exact_fraction(m["value"])
    displayed = str(f.numerator) if f.denominator == 1 else (
        str(f.numerator) + "/" + str(f.denominator))
    return displayed + (" " + m["unit"] if m["unit"] != "1" else " (unitless)") + (
        " [" + m["quantity_kind"] + "; " + m["epistemic_state"] + "]")


def mathml_presentation(m: dict) -> str:
    """Safe presentation-only MathML, NOT OpenMath or Content MathML."""
    validate(m)
    math = ET.Element("math", {"xmlns": NS, "display": "inline"})
    row = ET.SubElement(math, "mrow")
    if m["value"] is None:
        ET.SubElement(row, "mtext").text = m["epistemic_state"]
    else:
        f = exact_fraction(m["value"])
        if f.denominator == 1:
            ET.SubElement(row, "mn").text = str(f.numerator)
        else:
            fraction = ET.SubElement(row, "mfrac")
            ET.SubElement(fraction, "mn").text = str(f.numerator)
            ET.SubElement(fraction, "mn").text = str(f.denominator)
        ET.SubElement(row, "mtext").text = " " + (
            m["unit"] if m["unit"] != "1" else "(unitless)")
    return ET.tostring(math, encoding="unicode")


def fixture(kind: str = "duration", unit: str = "min",
            n: int | None = 2, d: int = 1,
            status: str = "OBSERVED_CLAIM") -> dict:
    return {
        "schema": SCHEMA, "quantity_kind": kind, "unit": unit,
        "value": None if n is None else {"n": n, "d": d},
        "epistemic_state": status,
        "source_ref": "fixture:explicitly-hypothetical",
        "observed_at_utc": "2026-11-10T22:00:00Z",
    }


def main() -> None:
    length = derive("MULTIPLY",
                    fixture("speed", "km/h", 18),
                    fixture("duration", "min", 2))
    example = fixture("duration", "min", 2)
    out = {
        "state": "SYNTHETIC_SOURCE_DEMONSTRATION_ONLY",
        "canonical": canonical(example),
        "ascii": ascii_projection(example),
        "mathml_presentation_only": mathml_presentation(example),
        "derived_length_from_18_kmh_times_2min": length,
        "no_actual_observation_or_credential_or_receiver": True,
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
