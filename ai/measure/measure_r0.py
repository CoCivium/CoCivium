#!/usr/bin/env python3
"""CoMeasure R0: small, read-only typed unit and derived-measure interpreter.

This is not a scientific measurement instrument, comprehensive SI library,
live telemetry collector, currency exchange service or CoPriMath canon.
Python 3.11+ standard library only.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation, localcontext
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REGISTRY_PATH = HERE / "registry-r0.json"
SOURCE_KEYS = {
    "measure_id", "unit_id", "status", "value", "scope_id", "window_id",
    "observer", "method_revision", "evidence_ref", "epistemic", "uncertainty_state",
}
BASE_DIMENSIONS = {"L", "M", "T", "I", "Theta", "N", "J"}
ALLOWED_DIMENSIONS = BASE_DIMENSIONS | {"Data"}
CONVERTIBLE = {"LINEAR", "AFFINE_POINT", "DELTA"}
SUPPORTED_STATUS = {"OBSERVED", "OBSERVED_ZERO"}
MISSING_STATES = {
    "NOT_OBSERVED", "NOT_MEASURED", "UNKNOWN", "NOT_APPLICABLE", "WITHHELD",
    "FORBIDDEN", "CONTRADICTORY", "BELOW_DETECTION", "EXPIRED",
    "OBSERVED_ABSENT_WITH_SCOPE",
}


class MeasureError(ValueError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise MeasureError(message)


def number(value: Any) -> Decimal:
    require(type(value) in (str, int, float, Decimal), "NUMERIC_VALUE_REQUIRED")
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise MeasureError("INVALID_DECIMAL") from exc
    require(d.is_finite() and len(d.as_tuple().digits) <= 80, "UNBOUNDED_OR_NONFINITE_NUMBER")
    return d


def show(value: Decimal) -> str:
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def validate_registry(reg: dict) -> None:
    require(reg.get("schema") == "CoAll.MeasureCommons.Registry.R0", "INVALID_REGISTRY_SCHEMA")
    require(reg.get("status", "").startswith("PUBLIC_SAFE_CANDIDATE"), "FALSE_RUNTIME_OR_CANON")
    base = reg.get("si_base_dimensions")
    require(type(base) is list and {x["id"] for x in base} == BASE_DIMENSIONS and len(base) == 7,
            "SI_BASE_DIMENSIONS")
    require({x["si_unit"] for x in base} == {"m", "kg", "s", "A", "K", "mol", "cd"},
            "SI_BASE_UNIT_SYMBOLS")
    units = reg.get("unit_registry")
    require(type(units) is list and 7 <= len(units) <= 128, "UNIT_REGISTRY_SIZE")
    ids = [x["id"] for x in units]
    require(len(ids) == len(set(ids)), "DUPLICATE_UNIT_ID")
    for u in units:
        require(type(u["quantity_kind"]) is str and u["quantity_kind"], "UNIT_QUANTITY_KIND")
        require(u["kind"] in {"LINEAR", "DELTA", "AFFINE_POINT", "COUNT", "CONTEXTUAL",
                             "TIME_POINT", "MODEL_DEPENDENT"}, "BAD_UNIT_KIND")
        require(type(u["dimension"]) is dict, "DIMENSION_NOT_OBJECT")
        require(set(u["dimension"]) <= ALLOWED_DIMENSIONS, "UNKNOWN_DIMENSION")
        require(all(type(v) is int and v != 0 and -12 <= v <= 12 for v in
                    u["dimension"].values()), "INVALID_DIMENSION_EXPONENT")
        require(number(u["scale_to_reference"]) > 0, "NONPOSITIVE_SCALE")
        off = number(u["offset_to_reference"])
        require(off == 0 or u["kind"] == "AFFINE_POINT", "OFFSET_ON_NONPOINT")
        if u["kind"] == "COUNT":
            require(not u["dimension"], "COUNT_SI_DIMENSIONS_NOT_ALLOWED")
        require(u["provenance"], "UNIT_PROVENANCE")
    measures = reg.get("measure_registry")
    require(type(measures) is list and measures, "MEASURES_EMPTY")
    names = [m["id"] for m in measures]
    require(len(names) == len(set(names)), "DUPLICATE_MEASURE_ID")
    for m in measures:
        require(type(m["method"]) is str and m["method"].strip() and
                type(m["primary_use"]) is str and m["primary_use"].strip() and
                m["definition_version"] == "r0", "INCOMPLETE_MEASURE_DEFINITION")
        if m["unit_id"] is None:
            require(m["interpretation"] == "ORDINAL", "UNITS_MISSING_WITHOUT_ORDINAL")
        else:
            require(m["unit_id"] in ids, "UNKNOWN_MEASURE_UNIT")
    derived = reg.get("derived_metrics")
    require(type(derived) is list and 1 <= len(derived) <= 24, "DERIVED_INVALID")
    require(len({d["id"] for d in derived}) == len(derived), "DUPLICATE_DERIVED")
    for d in derived:
        require(d["operation"] == "RATIO", "UNSUPPORTED_DERIVATION")
        require(d["numerator"] in names and d["denominator"] in names,
                "DERIVED_UNKNOWN_MEASURE")
        require("same_scope" in d["required"] and "same_window" in d["required"] and
                "positive_denominator" in d["required"], "DERIVED_UNSAFE_JOIN")
        require(d["output_unit"], "DERIVED_UNIT_LABEL_REQUIRED")
    require("UNKNOWN" in reg["null_states"] and "OBSERVED_ZERO" in reg["null_states"],
            "MISSING_VS_ZERO_COLLAPSED")
    require("CI_PASS_NE_RECEIVER_ACK" in reg["nonclaims"], "FALSE_RECEIVER_PROOF")


def indexed(reg: dict, field: str) -> dict:
    return {x["id"]: x for x in reg[field]}


def convert(value: Any, origin: str, target: str, reg: dict) -> dict:
    validate_registry(reg)
    all_units = indexed(reg, "unit_registry")
    require(origin in all_units and target in all_units, "UNKNOWN_UNIT")
    a, b = all_units[origin], all_units[target]
    require(a["quantity_kind"] == b["quantity_kind"], "SEMANTIC_KIND_MISMATCH")
    require(a["dimension"] == b["dimension"], "DIMENSION_MISMATCH")
    require(a["kind"] == b["kind"] and a["kind"] in CONVERTIBLE, "NON_CONVERTIBLE_UNIT_KIND")
    with localcontext() as ctx:
        ctx.prec = 50
        base_value = number(value) * number(a["scale_to_reference"]) + number(a["offset_to_reference"])
        result = (base_value - number(b["offset_to_reference"])) / number(b["scale_to_reference"])
    return {
        "status": "PURE_DEFINITION_CONVERSION",
        "source_value": str(value), "source_unit": origin,
        "converted_value": show(result), "target_unit": target,
        "quantity_kind": a["quantity_kind"],
        "safety": "DEFINITION_ONLY__NO_MEASUREMENT_UNCERTAINTY_ESTIMATE",
    }


def observation_check(obs: dict, reg: dict) -> None:
    require(type(obs) is dict and set(obs) == SOURCE_KEYS, "INVALID_OBSERVATION_FIELDS")
    measures = indexed(reg, "measure_registry")
    units = indexed(reg, "unit_registry")
    require(obs["measure_id"] in measures, "UNKNOWN_MEASURE")
    require(obs["unit_id"] in units, "UNKNOWN_UNIT")
    spec = measures[obs["measure_id"]]
    require(spec["unit_id"] is not None, "ORDINAL_ARITHMETIC_FORBIDDEN")
    require(obs["status"] in SUPPORTED_STATUS or obs["status"] in MISSING_STATES,
            "BAD_MEASUREMENT_STATUS")
    for key in ("scope_id", "window_id", "observer", "method_revision",
                "evidence_ref", "epistemic", "uncertainty_state"):
        require(type(obs[key]) is str and obs[key].strip(), "MISSING_OBSERVATION_CONTEXT_"+key)
    if obs["status"] in MISSING_STATES:
        require(obs["value"] is None, "NULL_STATE_HAS_NUMERIC_VALUE")
        return
    v = number(obs["value"])
    require(obs["status"] != "OBSERVED_ZERO" or v == 0, "FALSE_OBSERVED_ZERO")
    u_src, u_expected = units[obs["unit_id"]], units[spec["unit_id"]]
    require(u_src["quantity_kind"] == u_expected["quantity_kind"], "MEASUREMENT_UNIT_MISMATCH")
    if obs["unit_id"] != spec["unit_id"]:
        convert(obs["value"], obs["unit_id"], spec["unit_id"], reg)


def derive_ratio(derived_id: str, numerator: dict, denominator: dict, reg: dict) -> dict:
    validate_registry(reg)
    d = indexed(reg, "derived_metrics").get(derived_id)
    require(d is not None, "UNKNOWN_DERIVATION")
    observation_check(numerator, reg)
    observation_check(denominator, reg)
    require(numerator["measure_id"] == d["numerator"] and
            denominator["measure_id"] == d["denominator"], "DERIVED_MEASURE_MISMATCH")
    require(numerator["scope_id"] == denominator["scope_id"], "SCOPE_MISMATCH")
    require(numerator["window_id"] == denominator["window_id"], "WINDOW_MISMATCH")
    require(numerator["method_revision"] == denominator["method_revision"],
            "METHOD_REVISION_MISMATCH")
    require(numerator["epistemic"] == denominator["epistemic"], "EPISTEMIC_MISMATCH")
    require(numerator["status"] in SUPPORTED_STATUS and
            denominator["status"] in SUPPORTED_STATUS, "NULL_NOT_ARITHMETIC")
    specs = indexed(reg, "measure_registry")
    a_base = specs[numerator["measure_id"]]["unit_id"]
    b_base = specs[denominator["measure_id"]]["unit_id"]
    a = number(convert(numerator["value"], numerator["unit_id"], a_base, reg)["converted_value"]) if numerator["unit_id"] != a_base else number(numerator["value"])
    b = number(convert(denominator["value"], denominator["unit_id"], b_base, reg)["converted_value"]) if denominator["unit_id"] != b_base else number(denominator["value"])
    require(b > 0, "ZERO_OR_NEGATIVE_DENOMINATOR_UNDEFINED")
    if "same_trial_cohort" in d["required"]:
        require(a >= 0 and a <= b, "SUCCESS_EXCEEDS_TRIALS")
    with localcontext() as ctx:
        ctx.prec = 50
        result = a / b
    return {
        "state": "DERIVED_FROM_DECLARED_OBSERVATIONS__NOT_INDEPENDENTLY_CONFIRMED",
        "id": derived_id,
        "value": show(result),
        "unit_label": d["output_unit"],
        "scope_id": numerator["scope_id"], "window_id": numerator["window_id"],
        "source_evidence": [numerator["evidence_ref"], denominator["evidence_ref"]],
        "epistemic": numerator["epistemic"],
        "uncertainty": "NOT_PROPAGATED__REQUIRES_MODEL",
        "effects": {"writes": 0, "external_calls": 0, "device_actions": 0},
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Read-only CoMeasure typed registry prototype.")
    ap.add_argument("mode", choices=["validate", "convert", "derive"])
    ap.add_argument("--value", default="0")
    ap.add_argument("--from-unit", default="m")
    ap.add_argument("--to-unit", default="km")
    ap.add_argument("--derived-id", default="human_seconds_per_verified_effect")
    ap.add_argument("--observations", type=Path)
    args = ap.parse_args()
    reg = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    validate_registry(reg)
    if args.mode == "validate":
        result = {"result": "PASS_STRUCTURE_ONLY", "units": len(reg["unit_registry"]),
                  "measures": len(reg["measure_registry"]),
                  "derivations": len(reg["derived_metrics"]), "external_effects": 0}
    elif args.mode == "convert":
        result = convert(args.value, args.from_unit, args.to_unit, reg)
    else:
        require(args.observations is not None, "OBSERVATIONS_REQUIRED")
        obs = json.loads(args.observations.read_text(encoding="utf-8"))
        require(obs.get("schema") == "CoAll.MeasureCommons.SyntheticObservations.R0",
                "OBSERVATIONS_SCHEMA")
        result = derive_ratio(args.derived_id, obs["numerator"], obs["denominator"], reg)
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("CoMeasure FAIL_SCOPED:", str(exc), file=__import__("sys").stderr)
        raise SystemExit(1)
