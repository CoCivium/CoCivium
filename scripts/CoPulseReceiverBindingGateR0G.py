#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def parse_time(value: str) -> datetime:
    text=value.strip()
    if text.endswith("Z"):
        text=text[:-1]+"+00:00"
    dt=datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError("FAIL_CLOSED__TIMEZONE_REQUIRED")
    return dt.astimezone(timezone.utc)


def load(path: Path) -> tuple[dict[str,Any],bytes]:
    raw=path.read_bytes()
    obj=json.loads(raw.decode("utf-8"))
    if not isinstance(obj,dict):
        raise ValueError("FAIL_CLOSED__BINDING_OBJECT_REQUIRED")
    return obj,raw


def evaluate(binding: dict[str,Any], raw: bytes, evaluated_at: str, max_age_seconds: int) -> dict[str,Any]:
    required=("binding_id","receiver_id","virtual_session_id","embodiment_id","service_identity","route_adapter","observed_route_state","observed_at","currentness_cursor","authority_ceiling","confidentiality","evidence_refs")
    missing=[k for k in required if k not in binding or binding.get(k) in (None,"",[])]
    if missing:
        raise ValueError("FAIL_CLOSED__BINDING_MISSING="+",".join(missing))
    if max_age_seconds < 0:
        raise ValueError("FAIL_CLOSED__NEGATIVE_MAX_AGE")
    age=int((parse_time(evaluated_at)-parse_time(str(binding["observed_at"]))).total_seconds())
    route=str(binding["observed_route_state"])
    if age < 0:
        state="HOLD_FUTURE_RECEIVER_OBSERVATION"
        nxt="REBIND_OBSERVER_TIME_OR_ROUTE_OBSERVATION"
    elif age > max_age_seconds:
        state="HOLD_STALE_RECEIVER_BINDING"
        nxt="REOBSERVE_RECEIVER_ROUTE"
    elif route == "OFFLINE":
        state="HOLD_OFFLINE_RECEIVER"
        nxt="WAIT_FOR_PROVEN_ONLINE_ROUTE_THEN_REOBSERVE"
    elif route == "UNKNOWN":
        state="HOLD_UNKNOWN_RECEIVER_ROUTE"
        nxt="PROVE_ROUTE_STATE"
    elif route == "ONLINE":
        state="PASS_LIVE_RECEIVER_BINDING"
        nxt="ELIGIBLE_FOR_PROVENANCE_BOUND_FRESH_PRESSURE_OPERATIONAL_WEIGHT"
    else:
        raise ValueError("FAIL_CLOSED__INVALID_ROUTE_STATE")
    result={
        "schema":"CoPulseLiveReceiverBindingGate.R0G.v0.1-candidate",
        "state":state,
        "binding_id":binding["binding_id"],
        "receiver_id":binding["receiver_id"],
        "virtual_session_id":binding["virtual_session_id"],
        "embodiment_id":binding["embodiment_id"],
        "service_identity":binding["service_identity"],
        "route_adapter":binding["route_adapter"],
        "observed_route_state":route,
        "observed_at":binding["observed_at"],
        "evaluated_at":evaluated_at,
        "age_seconds":age,
        "max_age_seconds":max_age_seconds,
        "currentness_cursor":binding["currentness_cursor"],
        "binding_input_sha256":sha256_bytes(raw),
        "effects":{
            "receiver_mutation":0,
            "provider_session_mutation":0,
            "ack_cursor_mutation":0,
            "authority_change":0
        },
        "next":nxt,
        "nonclaims":[
            "ROUTE_ONLINE_NE_RECEIVER_PICKUP",
            "LIVE_BINDING_NE_AUTHORITY",
            "EMBODIMENT_NE_IDENTITY",
            "SERVICE_IDENTITY_NE_PERSONAL_LOGIN",
            "CAPABILITY_NE_AUTHORITY"
        ]
    }
    result["binding_gate_sha256"]=sha256_bytes(canonical(result))
    return result


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--binding",required=True)
    ap.add_argument("--evaluated-at",required=True)
    ap.add_argument("--max-age-seconds",type=int,required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    out=Path(a.output).resolve()
    if out.exists():
        raise SystemExit("FAIL_CLOSED__NO_CLOBBER="+str(out))
    try:
        binding,raw=load(Path(a.binding).resolve())
        result=evaluate(binding,raw,a.evaluated_at,a.max_age_seconds)
    except (ValueError,json.JSONDecodeError) as exc:
        raise SystemExit(str(exc))
    out.parent.mkdir(parents=True,exist_ok=True)
    encoded=(json.dumps(result,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
    out.write_bytes(encoded)
    print(json.dumps({
        "STATE":result["state"],
        "OUTPUT":str(out),
        "OUTPUT_SHA256":sha256_bytes(encoded),
        "ROUTE_STATE":result["observed_route_state"],
        "AGE_SECONDS":result["age_seconds"],
        "ACK_CURSOR_MUTATION":0,
        "NEXT":result["next"]
    },separators=(",",":")))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
