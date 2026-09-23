#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ALLOWED_EFFECT_CLASSES = {"OBSERVE", "PROPOSE", "REVIEW_CHALLENGE"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("contract must be a JSON object")
    return value


def require_loopback(endpoint: str) -> str:
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme != "http":
        raise ValueError("endpoint must use http loopback for R3 canary")
    host = parsed.hostname
    if not host:
        raise ValueError("endpoint hostname missing")
    try:
        addr = ipaddress.ip_address(host)
        if not addr.is_loopback:
            raise ValueError("endpoint must be loopback")
    except ValueError:
        if host.lower() != "localhost":
            raise ValueError("endpoint must be localhost or a loopback IP")
    return endpoint.rstrip("/")


def validate_contract(contract: dict[str, Any]) -> None:
    if contract.get("materialization_state") != "LOGICAL_ONLY":
        raise ValueError("contract must be LOGICAL_ONLY")
    if str(contract.get("uncertainty") or "").strip():
        raise ValueError("contract uncertainty must be empty for R3 canary")
    effects = {str(x) for x in contract.get("effect_classes", [])}
    if not effects or not effects.issubset(ALLOWED_EFFECT_CLASSES):
        raise ValueError(f"effect classes not allowed for R3 canary: {sorted(effects)}")
    if str(contract.get("authority_ceiling", "")).strip() == "":
        raise ValueError("authority_ceiling required")
    if str(contract.get("confidentiality", "PUBLIC")) != "PUBLIC":
        raise ValueError("R3 canary is public-safe only")


def build_prompt(contract: dict[str, Any]) -> str:
    return (
        "You are a bounded CoCivium local worker. Work only on the supplied logical contract. "
        "Do not claim authority, do not execute tools, do not mutate repositories, do not invent receiver pickup, "
        "and preserve uncertainty. Return one JSON object with keys: analysis_summary, proposed_deltas, "
        "contradictions, tests, uncertainty, source_refs, nonclaims.\n\nCONTRACT:\n" +
        json.dumps(contract, sort_keys=True, indent=2, ensure_ascii=False)
    )


def call_ollama(endpoint: str, model: str, prompt: str, timeout_seconds: int) -> dict[str, Any]:
    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.2},
    }).encode("utf-8")
    req = urllib.request.Request(
        endpoint + "/api/generate",
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        if resp.status != 200:
            raise RuntimeError(f"ollama returned HTTP {resp.status}")
        raw = resp.read()
    envelope = json.loads(raw.decode("utf-8"))
    text = envelope.get("response")
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError("ollama response missing JSON text")
    result = json.loads(text)
    if not isinstance(result, dict):
        raise RuntimeError("model response must be a JSON object")
    return {"ollama_envelope": envelope, "worker_result": result}


def selftest() -> int:
    base = {
        "materialization_state": "LOGICAL_ONLY",
        "uncertainty": None,
        "effect_classes": ["PROPOSE"],
        "authority_ceiling": "ADVISORY_ONLY",
        "confidentiality": "PUBLIC",
    }
    validate_contract(dict(base))
    require_loopback("http://127.0.0.1:11434")

    bad = dict(base)
    bad["confidentiality"] = "PRIVATE"
    try:
        validate_contract(bad)
        raise AssertionError("private contract was not rejected")
    except ValueError:
        pass

    bad = dict(base)
    bad["materialization_state"] = "MATERIALIZED"
    try:
        validate_contract(bad)
        raise AssertionError("non-logical contract was not rejected")
    except ValueError:
        pass

    try:
        require_loopback("http://192.0.2.10:11434")
        raise AssertionError("non-loopback endpoint was not rejected")
    except ValueError:
        pass

    print("SELFTEST=PASS_PUBLIC_LOGICAL_ONLY__PRIVATE_REJECTED__NONLOGICAL_REJECTED__NONLOOPBACK_REJECTED")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--contract")
    ap.add_argument("--model")
    ap.add_argument("--output")
    ap.add_argument("--endpoint", default="http://127.0.0.1:11434")
    ap.add_argument("--timeout-seconds", type=int, default=120)
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.contract or not args.model or not args.output:
        raise SystemExit("FAIL_CLOSED__CONTRACT_MODEL_OUTPUT_REQUIRED")

    out = Path(args.output).resolve()
    if out.exists():
        raise SystemExit(f"FAIL_CLOSED__NO_CLOBBER={out}")

    endpoint = require_loopback(args.endpoint)
    contract_path = Path(args.contract).resolve()
    contract_raw = contract_path.read_bytes()
    contract = json.loads(contract_raw.decode("utf-8"))
    if not isinstance(contract, dict):
        raise SystemExit("FAIL_CLOSED__CONTRACT_NOT_OBJECT")
    validate_contract(contract)

    prompt = build_prompt(contract)
    result = call_ollama(endpoint, args.model, prompt, args.timeout_seconds)

    artifact = {
        "schema": "CoLocalModelWorker.R3.v0.1-candidate",
        "state": "LOCAL_MODEL_CANDIDATE_OUTPUT__NO_EFFECT_EXECUTION",
        "contract_sha256": sha256(contract_raw),
        "model": args.model,
        "endpoint_class": "LOOPBACK_ONLY",
        "worker_result": result["worker_result"],
        "effects": {
            "repo_mutations": 0,
            "provider_sessions": 0,
            "public_outreach": 0,
            "authority_changes": 0,
            "credential_changes": 0,
        },
        "nonclaims": [
            "MODEL_OUTPUT_NE_TRUTH",
            "MODEL_OUTPUT_NE_EFFECT_PERMISSION",
            "LOCAL_NE_TRUSTED",
            "CANDIDATE_OUTPUT_NE_RECEIVER_PICKUP",
            "CANDIDATE_OUTPUT_NE_INTEGRATION",
        ],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(artifact, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    out.write_bytes(encoded)

    print(json.dumps({
        "STATE": artifact["state"],
        "OUTPUT": str(out),
        "OUTPUT_SHA256": sha256(encoded),
        "MODEL": args.model,
        "NETWORK_SCOPE": "LOOPBACK_ONLY",
        "EFFECT_EXECUTIONS": 0,
        "NEXT": "RECEIVER_REVIEW_AND_EXACT_READPROOF_BEFORE_ANY_INTEGRATION",
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
