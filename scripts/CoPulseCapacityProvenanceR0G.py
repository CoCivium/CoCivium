#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def load(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    obj = json.loads(raw.decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("FAIL_CLOSED__JSON_OBJECT_REQUIRED")
    return obj, raw


def verify(pressure: dict[str, Any], pressure_raw: bytes, prov: dict[str, Any]) -> dict[str, Any]:
    for key in ("sample_id","receiver_id","capacity_source"):
        if pressure.get(key) != prov.get(key):
            raise ValueError("FAIL_CLOSED__PROVENANCE_BINDING_MISMATCH=" + key)
    actual = sha256_bytes(pressure_raw)
    if actual != prov.get("pressure_input_sha256"):
        raise ValueError("FAIL_CLOSED__PRESSURE_HASH_MISMATCH")
    source = prov.get("capacity_source")
    evidence = prov.get("evidence_refs") or []
    if not evidence:
        raise ValueError("FAIL_CLOSED__EVIDENCE_REFS_REQUIRED")
    if source == "MEASURED":
        if not prov.get("source_object_ref") or not prov.get("source_object_sha256"):
            raise ValueError("FAIL_CLOSED__MEASURED_SOURCE_OBJECT_REQUIRED")
        state = "PASS_MEASURED_CAPACITY_PROVENANCE_BOUND"
    elif source == "DECLARED":
        if not prov.get("source_object_ref"):
            raise ValueError("FAIL_CLOSED__DECLARATION_REF_REQUIRED")
        state = "PASS_DECLARED_CAPACITY_PROVENANCE_BOUND"
    elif source == "SYNTHETIC_FIXTURE":
        state = "PASS_SYNTHETIC_CAPACITY_PROVENANCE_BOUND"
    else:
        raise ValueError("FAIL_CLOSED__UNKNOWN_CAPACITY_SOURCE")

    result = {
        "schema": "CoPulseCapacityProvenanceVerification.R0G.v0.1-candidate",
        "state": state,
        "sample_id": pressure["sample_id"],
        "receiver_id": pressure["receiver_id"],
        "capacity_source": source,
        "pressure_input_sha256": actual,
        "provenance_id": prov.get("provenance_id"),
        "source_identity": prov.get("source_identity"),
        "source_method": prov.get("source_method"),
        "source_object_ref": prov.get("source_object_ref"),
        "source_object_sha256": prov.get("source_object_sha256"),
        "evidence_refs": list(evidence),
        "effects": {
            "pressure_mutation": 0,
            "receiver_context_mutation": 0,
            "ack_cursor_mutation": 0,
            "authority_change": 0
        },
        "next": "FRESHNESS_GATE_THEN_LIVE_RECEIVER_BINDING_BEFORE_OPERATIONAL_WEIGHT",
        "nonclaims": [
            "PROVENANCE_NE_MEASUREMENT_ACCURACY",
            "PROVENANCE_NE_LIVE_RECEIVER_BINDING",
            "CAPACITY_SOURCE_NE_AUTHORITY",
            "DECLARATION_NE_MEASUREMENT"
        ]
    }
    result["verification_sha256"] = sha256_bytes(canonical(result))
    return result


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--pressure",required=True)
    ap.add_argument("--provenance",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    out=Path(a.output).resolve()
    if out.exists():
        raise SystemExit("FAIL_CLOSED__NO_CLOBBER="+str(out))
    try:
        pressure,raw=load(Path(a.pressure).resolve())
        prov,_=load(Path(a.provenance).resolve())
        result=verify(pressure,raw,prov)
    except (ValueError,json.JSONDecodeError) as exc:
        raise SystemExit(str(exc))
    out.parent.mkdir(parents=True,exist_ok=True)
    encoded=(json.dumps(result,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
    out.write_bytes(encoded)
    print(json.dumps({
        "STATE":result["state"],
        "OUTPUT":str(out),
        "OUTPUT_SHA256":sha256_bytes(encoded),
        "CAPACITY_SOURCE":result["capacity_source"],
        "ACK_CURSOR_MUTATION":0,
        "NEXT":result["next"]
    },separators=(",",":")))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
