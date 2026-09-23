#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
V01 = ROOT / "schemas" / "coevo-delta-v0.1.schema.json"
UNION = ROOT / "schemas" / "coevo-delta-v0.2-union-candidate.schema.json"
INTAKE = ROOT / "ai" / "evolution-intake-policy-r0.json"
DELTA_ROOT = ROOT / "ai" / "evolution-deltas"

RICH_FIELDS = {
    "subscription_context","pressure","energet","want_projection",
    "route","close_readiness","nonclaims"
}
EFFECT_FIELDS = {"effect_classes","effect_gate","effect_scope"}
EXPECTED_EFFECT_CLASSES = {
    "NONE","PUBLICATION","PUBLIC_OUTREACH","ACCESS_GRANT","ACCESS_REVOCATION",
    "AUTHORITY_CHANGE","PRIVACY_BOUNDARY","CREDENTIAL","FINANCIAL","RUNTIME",
    "IRREVERSIBLE","UNKNOWN"
}
EXPECTED_EFFECT_GATES = {
    "NOT_APPLICABLE","HELD","REQUIRES_EXPLICIT_HUMAN_GATE",
    "AUTHORIZED_FOR_SCOPE","EXECUTED","UNKNOWN"
}

def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"OBJECT_REQUIRED:{path}")
    return obj

def type_ok(value: Any, spec: Any) -> bool:
    names = spec if isinstance(spec, list) else [spec]
    for name in names:
        if name == "null" and value is None:
            return True
        if name == "string" and isinstance(value, str):
            return True
        if name == "array" and isinstance(value, list):
            return True
        if name == "object" and isinstance(value, dict):
            return True
        if name == "boolean" and isinstance(value, bool):
            return True
        if name == "number" and isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)):
            return True
    return False

def check_value(value: Any, spec: dict[str, Any], path: str, errors: list[str]) -> None:
    if "type" in spec and not type_ok(value, spec["type"]):
        errors.append(f"TYPE:{path}")
        return
    if "enum" in spec and value not in spec["enum"]:
        errors.append(f"ENUM:{path}")
    if isinstance(value, str) and len(value) < int(spec.get("minLength", 0)):
        errors.append(f"MIN_LENGTH:{path}")
    if isinstance(value, list):
        if len(value) < int(spec.get("minItems", 0)):
            errors.append(f"MIN_ITEMS:{path}")
        if spec.get("uniqueItems"):
            canon = [json.dumps(x, sort_keys=True, separators=(",", ":")) for x in value]
            if len(canon) != len(set(canon)):
                errors.append(f"UNIQUE_ITEMS:{path}")
        item_spec = spec.get("items")
        if isinstance(item_spec, dict):
            for i, item in enumerate(value):
                check_value(item, item_spec, f"{path}[{i}]", errors)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in spec and value < spec["minimum"]:
            errors.append(f"MINIMUM:{path}")
        if "maximum" in spec and value > spec["maximum"]:
            errors.append(f"MAXIMUM:{path}")
    if isinstance(value, dict) and "properties" in spec:
        props = spec["properties"]
        for req in spec.get("required", []):
            if req not in value:
                errors.append(f"NESTED_REQUIRED:{path}.{req}")
        if spec.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    errors.append(f"NESTED_ADDITIONAL:{path}.{key}")
        for key, val in value.items():
            if key in props:
                check_value(val, props[key], f"{path}.{key}", errors)

def validate_instance(schema: dict[str, Any], obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    props = schema["properties"]
    for req in schema.get("required", []):
        if req not in obj:
            errors.append(f"REQUIRED:{req}")
    if schema.get("additionalProperties") is False:
        for key in obj:
            if key not in props:
                errors.append(f"ADDITIONAL:{key}")
    for key, value in obj.items():
        if key in props:
            check_value(value, props[key], key, errors)

    if obj.get("mutation_class") == "EFFECT_GATED":
        for req in ("effect_classes","effect_gate"):
            if req not in obj:
                errors.append(f"EFFECT_REQUIRED:{req}")

    if RICH_FIELDS.intersection(obj) and "materiality" not in obj:
        errors.append("RICH_EXTENSION_REQUIRES_MATERIALITY")
    return errors

def fixture_base() -> dict[str, Any]:
    return {
        "delta_id":"fixture.delta",
        "session_id":"fixture.session",
        "observed_at":"2026-09-23T11:46:44Z",
        "domain":["CoOps+"],
        "subject":"fixture",
        "relation":"TESTS",
        "epistemic_class":"OBSERVED",
        "source_refs":["fixture:source"],
        "target_surfaces":["fixture:target"],
        "mutation_class":"PROPOSE",
        "authority_ceiling":"NONE",
        "confidentiality":"PUBLIC",
        "next_receiver":"fixture.receiver"
    }

def main() -> int:
    errors: list[str] = []
    v01 = load(V01)
    union = load(UNION)
    intake = load(INTAKE)

    # Core compatibility: do not mutate the v0.1 contract inside the union candidate.
    if union.get("required") != v01.get("required"):
        errors.append("V01_REQUIRED_SET_CHANGED")
    for key, spec in v01.get("properties", {}).items():
        if union.get("properties", {}).get(key) != spec:
            errors.append(f"V01_PROPERTY_CHANGED:{key}")

    props = union["properties"]
    for key in EFFECT_FIELDS | {"materiality"} | RICH_FIELDS:
        if key not in props:
            errors.append(f"UNION_FIELD_MISSING:{key}")

    effect_classes = set(props["effect_classes"]["items"]["enum"])
    if effect_classes != EXPECTED_EFFECT_CLASSES:
        errors.append("EFFECT_CLASS_ENUM_DRIFT")
    if set(props["effect_gate"]["enum"]) != EXPECTED_EFFECT_GATES:
        errors.append("EFFECT_GATE_ENUM_DRIFT")

    # Real current-main v0.1 deltas must remain accepted by the union candidate.
    existing = sorted(DELTA_ROOT.rglob("*.json")) if DELTA_ROOT.is_dir() else []
    if not existing:
        errors.append("NO_MAIN_DELTA_FIXTURE")
    accepted = 0
    for path in existing:
        obj = load(path)
        e = validate_instance(union, obj)
        if e:
            errors.append(f"MAIN_DELTA_REJECTED:{path.relative_to(ROOT)}:{'|'.join(e)}")
        else:
            accepted += 1

    # Positive legacy fixture.
    legacy = fixture_base()
    if validate_instance(union, legacy):
        errors.append("LEGACY_FIXTURE_REJECTED")

    # Effect-gated negative and positive.
    bad_effect = fixture_base()
    bad_effect["delta_id"] = "fixture.bad_effect"
    bad_effect["mutation_class"] = "EFFECT_GATED"
    if not validate_instance(union, bad_effect):
        errors.append("EFFECT_GATE_NEGATIVE_FALSE_ACCEPT")

    good_effect = dict(bad_effect)
    good_effect["delta_id"] = "fixture.good_effect"
    good_effect["effect_classes"] = ["PUBLICATION"]
    good_effect["effect_gate"] = "HELD"
    good_effect["effect_scope"] = "fixture only"
    if validate_instance(union, good_effect):
        errors.append("EFFECT_GATE_POSITIVE_REJECT")

    # Rich extension must carry materiality.
    bad_rich = fixture_base()
    bad_rich["delta_id"] = "fixture.bad_rich"
    bad_rich["pressure"] = {"attention_debt":1}
    if not validate_instance(union, bad_rich):
        errors.append("RICH_MATERIALITY_NEGATIVE_FALSE_ACCEPT")

    good_rich = dict(bad_rich)
    good_rich["delta_id"] = "fixture.good_rich"
    good_rich["materiality"] = "MATERIAL"
    good_rich["route"] = {
        "required_capabilities":["READ"],
        "candidate_routes":["FILES_LIBRARY"],
        "elected_route":"FILES_LIBRARY",
        "route_reason":"fixture",
        "route_morph_allowed":True,
        "authority_preserved":True
    }
    good_rich["nonclaims"] = ["NOT_RUNTIME","NOT_AUTHORITY"]
    if validate_instance(union, good_rich):
        errors.append("RICH_POSITIVE_REJECT")

    # A rich v0.2 object must be losslessly down-projectable for the v0.1 core.
    extension_fields = EFFECT_FIELDS | {"materiality"} | RICH_FIELDS
    down = {k:v for k,v in good_rich.items() if k not in extension_fields}
    if validate_instance(v01, down):
        errors.append("V02_TO_V01_CORE_PROJECTION_REJECTED")
    for key in v01["required"]:
        if down.get(key) != good_rich.get(key):
            errors.append(f"CORE_PROJECTION_DRIFT:{key}")

    # Intake election: one primary machine surface, docs only as projection/index.
    election = intake.get("election", {})
    if election.get("primary_machine_intake") != "ai/evolution-deltas/<YYYY-MM-DD>/":
        errors.append("PRIMARY_INTAKE_NOT_AI_EVOLUTION_DELTAS")
    secondary = election.get("secondary_projection", {})
    if secondary.get("surface") != "docs/Evolution/deltas/":
        errors.append("DOCS_ALIAS_MISSING")
    if secondary.get("role") != "DOCUMENTATION_INDEX_OR_EXAMPLE_PROJECTION":
        errors.append("DOCS_ALIAS_ROLE_BAD")

    if errors:
        print(f"HOLD_COEVO_CONVERGENCE_R0 errors={len(errors)}")
        for e in errors:
            print(" -", e)
        return 1

    print("PASS_COEVO_CONVERGENCE_R0")
    print(f"main_v01_deltas_accepted={accepted}")
    print("schema_union=V01_CORE_UNCHANGED+PR32_EFFECTS+PR37_RICH_EXTENSIONS")
    print("rich_extension_requires_materiality=true")
    print("effect_gated_requires_effect_fields=true")
    print("primary_intake=ai/evolution-deltas/<YYYY-MM-DD>/")
    print("docs_evolution_deltas=DOCUMENTATION_INDEX_OR_EXAMPLE_PROJECTION")
    print("canon=UNPROVEN")
    print("runtime=UNPROVEN")
    print("authority=NONE")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
