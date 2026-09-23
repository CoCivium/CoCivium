#!/usr/bin/env python3
"""CoSessionShadowLedger R1

Deterministic shadow lifecycle/label compiler.
No provider-session creation, rename, close, browser automation, public outreach,
authority elevation, or external network access.

Input: JSON array or {"observations":[...]}.
Output: JSON ledger written to --output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


PROJECTIONS = {
    "UNORIENTED","BOOTSTRAPPING","ACTIVE","WORKING","CHALLENGING","WAITING",
    "QUIESCENT","COTWILIGHT","EXTERNALIZING","SUCCESSOR_READY","CLOSE_SAFE",
    "DORMANT","REAWAKENED","DEGRADED","RECOVERY","SUPERSEDED"
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def boolish(v: Any) -> bool:
    return v is True


def project(obs: dict[str, Any]) -> tuple[str, str]:
    explicit = obs.get("projection")
    if isinstance(explicit, str) and explicit in PROJECTIONS:
        return explicit, "EXPLICIT_SOURCE_PROJECTION"

    if boolish(obs.get("superseded")):
        return "SUPERSEDED", "SUPERSEDED_TRUE"
    if boolish(obs.get("recovery_required")):
        return "RECOVERY", "RECOVERY_REQUIRED_TRUE"
    if str(obs.get("currentness","")).upper() in {"DEGRADED","STALE","UNKNOWN_STALE"}:
        return "DEGRADED", "CURRENTNESS_DEGRADED"
    if boolish(obs.get("tab_close_safe")):
        return "CLOSE_SAFE", "TAB_CLOSE_SAFE_TRUE"
    if boolish(obs.get("successor_ready")):
        return "SUCCESSOR_READY", "SUCCESSOR_READY_TRUE"
    if boolish(obs.get("externalizing")):
        return "EXTERNALIZING", "EXTERNALIZING_TRUE"
    if boolish(obs.get("cotwilight")):
        return "COTWILIGHT", "COTWILIGHT_TRUE"
    if boolish(obs.get("quiescent")):
        return "QUIESCENT", "QUIESCENT_TRUE"
    if boolish(obs.get("waiting")):
        return "WAITING", "WAITING_TRUE"
    if boolish(obs.get("challenging")):
        return "CHALLENGING", "CHALLENGING_TRUE"

    work_state = str(obs.get("work_state","")).upper()
    if work_state in {"WORKING","ACTIVE_WORK","IN_PROGRESS"}:
        return "WORKING", "WORK_STATE_ACTIVE"
    if work_state in {"ACTIVE","READY"}:
        return "ACTIVE", "WORK_STATE_READY"
    if work_state in {"DORMANT","SLEEPING"}:
        return "DORMANT", "WORK_STATE_DORMANT"

    return "UNORIENTED", "INSUFFICIENT_EVIDENCE"


def label_for(obs: dict[str, Any], projection: str) -> str:
    role = str(obs.get("role") or "UnboundRole")
    sid = str(obs["session_id"])
    if projection == "CLOSE_SAFE":
        return f".close-ok {{{role}; durable frontier continues elsewhere}} [{sid}]"
    if projection == "COTWILIGHT":
        return f".twilight {{{role}; externalizing/succession}} [{sid}]"
    if projection == "DORMANT":
        return f".dormant {{{role}; wake-condition only}} [{sid}]"
    if projection == "DEGRADED":
        return f".degraded {{{role}; currentness/recovery required}} [{sid}]"
    return f".{projection.lower()} {{{role}}} [{sid}]"


def compile_ledger(source: Any, source_ref: str, source_sha256: str) -> dict[str, Any]:
    observations = source.get("observations") if isinstance(source, dict) else source
    if not isinstance(observations, list):
        raise ValueError("input must be a JSON array or object with observations[]")

    rows: list[dict[str, Any]] = []
    signals: list[dict[str, Any]] = []

    for idx, obs in enumerate(observations):
        if not isinstance(obs, dict):
            raise ValueError(f"observation[{idx}] is not an object")
        for req in ("session_id","observed_at","observer","work_state",
                    "evidence_state","authority_ceiling","currentness"):
            if not obs.get(req):
                raise ValueError(f"observation[{idx}] missing {req}")

        projection, basis = project(obs)
        candidate = label_for(obs, projection)
        prior = obs.get("prior_label")
        evidence_refs = list(obs.get("source_refs") or [])
        evidence_refs.append(f"input:{source_ref}#observation={idx}")

        row = {
            "session_id": obs["session_id"],
            "observed_at": obs["observed_at"],
            "observer": obs["observer"],
            "projection": projection,
            "projection_basis": basis,
            "role": obs.get("role"),
            "work_state": obs["work_state"],
            "evidence_state": obs["evidence_state"],
            "authority_ceiling": obs["authority_ceiling"],
            "currentness": obs["currentness"],
            "close_safety": "PROVEN_TRUE" if boolish(obs.get("tab_close_safe")) else str(obs.get("close_safety") or "UNPROVEN"),
            "successor_state": obs.get("successor_state"),
            "wake_conditions": list(obs.get("wake_conditions") or []),
            "candidate_label": candidate,
            "provider_visible_label_mutation": "NOT_AUTHORIZED",
            "source_refs": evidence_refs,
            "nonclaims": [
                "LIFECYCLE_LABEL_NE_LIFECYCLE_TRUTH",
                "AUTO_LABEL_SIGNAL_NE_PROVIDER_UI_MUTATION",
                "SESSION_STATE_NE_WORK_STATE_NE_EVIDENCE_STATE",
                "NO_PROVIDER_SESSION_MUTATION"
            ]
        }
        rows.append(row)

        if prior != candidate:
            payload = json.dumps(
                {"session_id":obs["session_id"],"observed_at":obs["observed_at"],
                 "prior_label":prior,"candidate_label":candidate,"basis":basis},
                sort_keys=True,separators=(",",":")
            ).encode("utf-8")
            signals.append({
                "signal_id":"colabel:"+sha256_bytes(payload)[:24],
                "session_id":obs["session_id"],
                "observed_at":obs["observed_at"],
                "trigger_class":"LIFECYCLE_PROJECTION_CHANGED_OR_LABEL_ABSENT",
                "prior_label":prior,
                "candidate_label":candidate,
                "evidence_refs":evidence_refs,
                "confidence":1.0 if basis != "INSUFFICIENT_EVIDENCE" else 0.25,
                "visible_ui_mutation_authorized":False,
                "provider_effect_state":"NOT_REQUESTED",
                "nonclaims":[
                    "LABEL_SIGNAL_NE_PROVIDER_TITLE_CHANGE",
                    "LABEL_NE_AUTHORITY",
                    "SIGNAL_NE_RECEIVER_PICKUP"
                ]
            })

    rows.sort(key=lambda x:(str(x["session_id"]),str(x["observed_at"])))
    signals.sort(key=lambda x:(str(x["session_id"]),str(x["observed_at"])))

    return {
        "schema":"CoSessionShadowLedger.R1.v0.1-candidate",
        "state":"SHADOW_LEDGER_COMPILED__NO_PROVIDER_MUTATION",
        "coverage":{
            "observation_count":len(rows),
            "global_active_session_census":"UNPROVEN",
            "source_ref":source_ref,
            "source_sha256":source_sha256
        },
        "sessions":rows,
        "label_signals":signals,
        "effects":{
            "provider_session_create":0,
            "provider_title_mutation":0,
            "provider_tab_close":0,
            "authority_changes":0,
            "public_outreach":0
        },
        "next":"R2_LOGICAL_SPAWN_ECOLOGY_AND_DEDUPE_COLLISION_FIXTURES",
        "nonclaims":[
            "DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY",
            "LIFECYCLE_LABEL_NE_LIFECYCLE_TRUTH",
            "DELIVERY_NE_PICKUP",
            "NO_GLOBAL_ACTIVE_SESSION_CENSUS",
            "NO_PROVIDER_SESSION_MUTATION"
        ]
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    src = Path(args.input).resolve()
    out = Path(args.output).resolve()
    if out.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out}")

    raw = src.read_bytes()
    source = json.loads(raw.decode("utf-8"))
    ledger = compile_ledger(source, str(src), sha256_bytes(raw))

    out.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(ledger,indent=2,ensure_ascii=False)+"\n").encode("utf-8")
    out.write_bytes(encoded)

    print(json.dumps({
        "STATE":ledger["state"],
        "OUTPUT":str(out),
        "OUTPUT_SHA256":sha256_bytes(encoded),
        "SESSIONS":len(ledger["sessions"]),
        "LABEL_SIGNALS":len(ledger["label_signals"]),
        "PROVIDER_MUTATIONS":0,
        "NEXT":ledger["next"]
    },separators=(",",":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
