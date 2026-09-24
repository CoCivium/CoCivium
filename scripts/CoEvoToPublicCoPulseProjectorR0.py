#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ALLOWED_EPISTEMIC = {
    "OBSERVED","INFERRED","HYPOTHESIS","PREDICTED","PLANNED","PREFERRED",
    "METAPHORICAL","MYTHIC","HUMOROUS","COUNTERFACTUAL","UNKNOWN"
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def load_one(path: str) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = Path(path).read_bytes()
    value = json.loads(raw.decode("utf-8"))
    if isinstance(value, dict) and isinstance(value.get("coevo_deltas"), list):
        rows = value["coevo_deltas"]
    elif isinstance(value, dict) and isinstance(value.get("deltas"), list):
        rows = value["deltas"]
    elif isinstance(value, list):
        rows = value
    elif isinstance(value, dict):
        rows = [value]
    else:
        raise ValueError("CoEvo input must be an object, array, or known wrapper")
    if len(rows) != 1 or not isinstance(rows[0], dict):
        raise ValueError("R0 requires exactly one CoEvoDelta object per projection")
    return rows[0], {"sha256": sha256_bytes(raw), "bytes": len(raw)}


def validate_source(delta: dict[str, Any]) -> None:
    required = {
        "delta_id","session_id","observed_at","domain","subject","relation",
        "epistemic_class","source_refs","authority_ceiling","confidentiality",
    }
    missing = sorted(required - set(delta))
    if missing:
        raise ValueError("missing required CoEvo fields: " + ", ".join(missing))
    if delta.get("confidentiality") != "PUBLIC":
        raise ValueError("FAIL_CLOSED__NONPUBLIC_COEVO_FOR_PUBLIC_COPULSE")
    if delta.get("public_safety") != "PUBLIC_SAFE":
        raise ValueError("FAIL_CLOSED__PUBLIC_SAFETY_NOT_PROVEN")
    if not isinstance(delta.get("domain"), list) or not delta["domain"]:
        raise ValueError("domain must be a non-empty array")
    if str(delta.get("epistemic_class")) not in ALLOWED_EPISTEMIC:
        raise ValueError("FAIL_CLOSED__UNKNOWN_EPISTEMIC_CLASS=" + str(delta.get("epistemic_class")))


def compile_pulse(delta: dict[str, Any], cursor: int, recorded_at: str, valid_from: str) -> dict[str, Any]:
    validate_source(delta)
    if cursor < 0:
        raise ValueError("cursor must be non-negative")
    evidence = sorted({str(x) for x in (delta.get("evidence_refs") or []) + (delta.get("source_refs") or [])})
    provenance = sorted({
        "coevo-delta:" + str(delta["delta_id"]),
        *[str(x) for x in (delta.get("source_refs") or [])],
    })
    payload = {
        "source_type": "CoEvoDelta+",
        "source_delta_id": delta["delta_id"],
        "typed_operation": delta.get("typed_operation"),
        "object": delta.get("object"),
        "mutation_class": delta.get("mutation_class"),
        "public_safety": delta.get("public_safety"),
        "source_epistemic_class": delta["epistemic_class"],
        "nonclaims": [
            "COPULSE_NE_COEVO_SOURCE",
            "PROJECTION_NE_SOURCE",
            "ROUTED_NE_PICKED_UP",
        ],
    }
    basis = {
        "source_delta_id": delta["delta_id"],
        "cursor": cursor,
        "subject": delta["subject"],
        "relation_type": delta["relation"],
        "epistemic_class": delta["epistemic_class"],
        "domains": sorted({str(x) for x in delta["domain"]}),
        "recorded_at": recorded_at,
        "valid_from": valid_from,
        "payload": payload,
    }
    pulse_id = "copulse:coevo:" + sha256_bytes(canonical(basis))[:24]
    return {
        "pulse_id": pulse_id,
        "cursor": cursor,
        "subject": delta["subject"],
        "relation_type": delta["relation"],
        "epistemic_class": delta["epistemic_class"],
        "source_identity": "coevo:" + str(delta["delta_id"]),
        "provenance": provenance,
        "event_time": None,
        "observation_time": delta["observed_at"],
        "recorded_at": recorded_at,
        "valid_from": valid_from,
        "valid_to": None,
        "confidence": delta.get("confidence"),
        "assumptions": [],
        "evidence_refs": evidence,
        "authority_ceiling": delta["authority_ceiling"],
        "confidentiality": "PUBLIC",
        "topics": [],
        "wake_conditions": list(delta.get("wake_conditions") or []),
        "supersedes": list(delta.get("supersedes") or []),
        "expiry": None,
        "calibration_disposition": None,
        "content_hash": delta.get("source_operation_sha256") or delta.get("source_projection_file_sha256"),
        "payload": payload,
        "domains": sorted({str(x) for x in delta["domain"]}),
        "target_objects": [],
    }


def selftest() -> int:
    base = {
        "delta_id":"d1","session_id":"S","observed_at":"2026-09-23T12:00:00Z",
        "domain":["CoLex+"],"subject":"CoTerm+","relation":"qualifies",
        "epistemic_class":"HUMOROUS","source_refs":["src:1"],"evidence_refs":["ev:1"],
        "authority_ceiling":"CANDIDATE_ONLY","confidentiality":"PUBLIC","public_safety":"PUBLIC_SAFE",
        "mutation_class":"PROPOSE","typed_operation":"QUALIFY","object":"example","confidence":0.9,
        "wake_conditions":[],"supersedes":[]
    }
    p1 = compile_pulse(base, 7, "2026-09-23T12:01:00Z", "2026-09-23T12:00:00Z")
    p2 = compile_pulse(base, 7, "2026-09-23T12:01:00Z", "2026-09-23T12:00:00Z")
    assert p1 == p2
    assert p1["epistemic_class"] == "HUMOROUS"
    assert p1["cursor"] == 7
    private = dict(base)
    private["confidentiality"] = "PRIVATE"
    try:
        compile_pulse(private, 8, "2026-09-23T12:02:00Z", "2026-09-23T12:02:00Z")
        raise AssertionError("private source should fail public projector")
    except ValueError as exc:
        assert "NONPUBLIC" in str(exc)
    unsafe = dict(base)
    unsafe["public_safety"] = "UNKNOWN"
    try:
        compile_pulse(unsafe, 9, "2026-09-23T12:03:00Z", "2026-09-23T12:03:00Z")
        raise AssertionError("public safety must be proven")
    except ValueError as exc:
        assert "PUBLIC_SAFETY" in str(exc)
    print("SELFTEST=PASS_DETERMINISTIC__EPISTEMIC_CLASS_PRESERVED__NONPUBLIC_AND_UNSAFE_FAIL_CLOSED")
    print("PULSE_ID=" + p1["pulse_id"])
    print("PULSE_SHA256=" + sha256_bytes(canonical(p1)))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--coevo")
    ap.add_argument("--cursor", type=int)
    ap.add_argument("--recorded-at")
    ap.add_argument("--valid-from")
    ap.add_argument("--output")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.coevo is None or args.cursor is None or not args.recorded_at or not args.valid_from or not args.output:
        raise SystemExit("FAIL_CLOSED__COEVO_CURSOR_RECORDED_AT_VALID_FROM_OUTPUT_REQUIRED")
    delta, source_meta = load_one(args.coevo)
    try:
        pulse = compile_pulse(delta, args.cursor, args.recorded_at, args.valid_from)
    except ValueError as exc:
        raise SystemExit(str(exc))
    wrapper = {
        "pulses":[pulse],
        "projection_receipt":{
            "projector":"CoEvoToPublicCoPulseProjector.R0",
            "source":source_meta,
            "source_delta_id":delta["delta_id"],
            "pulse_id":pulse["pulse_id"],
            "cursor":pulse["cursor"],
            "effects":{"delivery":0,"ack_cursor_advance":0,"receiver_pickup_claim":0,"authority_change":0},
            "next":"COPULSE_SUBSCRIPTION_ROUTER_R0A_THEN_EXACT_RECEIVER_READPROOF_BEFORE_ACK_CURSOR_ADVANCE",
            "nonclaims":["PROJECTION_NE_DELIVERY","DELIVERY_NE_PICKUP","CANDIDATE_DELIVERED_CURSOR_NE_ACK_CURSOR"]
        }
    }
    out = Path(args.output)
    if out.exists():
        raise SystemExit("FAIL_CLOSED__NO_CLOBBER=" + str(out))
    out.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(wrapper, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    out.write_bytes(encoded)
    print("STATE=PASS_COEVO_TO_PUBLIC_COPULSE_R0")
    print("OUTPUT=" + str(out))
    print("OUTPUT_SHA256=" + sha256_bytes(encoded))
    print("PULSE_ID=" + pulse["pulse_id"])
    print("CURSOR=" + str(pulse["cursor"]))
    print("DELIVERY=0")
    print("ACK_CURSOR_ADVANCE=0")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
