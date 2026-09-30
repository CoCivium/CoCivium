#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import os
import platform
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


def fail(code: str) -> None:
    raise SystemExit(code)


def canonical_sha(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest().upper()


def require_loopback(endpoint: str) -> str:
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme != "http":
        fail("FAIL_ENDPOINT_SCHEME")
    host = parsed.hostname
    if not host:
        fail("FAIL_ENDPOINT_HOST")
    if host.lower() == "localhost":
        return endpoint.rstrip("/")
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        fail("FAIL_ENDPOINT_NOT_LOOPBACK")
    if not addr.is_loopback:
        fail("FAIL_ENDPOINT_NOT_LOOPBACK")
    return endpoint.rstrip("/")


def normalize_model(item: dict[str, Any]) -> dict[str, Any]:
    name = item.get("name")
    model = item.get("model", name)
    digest = item.get("digest")
    size = item.get("size")
    details = item.get("details") or {}

    if not isinstance(name, str) or not name.strip():
        fail("FAIL_MODEL_NAME")
    if not isinstance(model, str) or not model.strip():
        fail("FAIL_MODEL_FIELD")
    if not isinstance(digest, str) or len(digest) != 64:
        fail("FAIL_MODEL_DIGEST")
    try:
        int(digest, 16)
    except ValueError:
        fail("FAIL_MODEL_DIGEST")
    if not isinstance(size, int) or size < 0:
        fail("FAIL_MODEL_SIZE")
    if not isinstance(details, dict):
        fail("FAIL_MODEL_DETAILS")

    return {
        "name": name,
        "model": model,
        "digest": digest.lower(),
        "size": size,
        "details": {
            "parent_model": details.get("parent_model"),
            "format": details.get("format"),
            "family": details.get("family"),
            "families": details.get("families"),
            "parameter_size": details.get("parameter_size"),
            "quantization_level": details.get("quantization_level"),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://127.0.0.1:11434")
    ap.add_argument("--output", required=True)
    ap.add_argument("--timeout-seconds", type=int, default=10)
    args = ap.parse_args()

    endpoint = require_loopback(args.endpoint)
    out = Path(args.output)
    if out.exists():
        fail("FAIL_CLOSED_NO_CLOBBER")

    req = urllib.request.Request(endpoint + "/api/tags", method="GET")
    with urllib.request.urlopen(req, timeout=args.timeout_seconds) as resp:
        if resp.status != 200:
            fail(f"FAIL_TAGS_HTTP_{resp.status}")
        raw = resp.read()

    try:
        envelope = json.loads(raw.decode("utf-8"))
    except Exception:
        fail("FAIL_TAGS_JSON")
    if not isinstance(envelope, dict):
        fail("FAIL_TAGS_OBJECT")
    models_raw = envelope.get("models")
    if not isinstance(models_raw, list):
        fail("FAIL_TAGS_MODELS_LIST")

    models = [normalize_model(x) for x in models_raw if isinstance(x, dict)]
    if len(models) != len(models_raw):
        fail("FAIL_TAGS_MODEL_NOT_OBJECT")
    models = sorted(models, key=lambda x: (x["name"], x["digest"]))

    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        head = None

    state = "PASS_LOCAL_OLLAMA_INVENTORY_READBACK" if models else "HOLD_NO_INSTALLED_MODELS"
    receipt = {
        "schema": "CoModelSubstrateLight.OllamaInventoryReceipt.v0.1",
        "STATE": state,
        "checked_out_head_sha": head,
        "endpoint_class": "LOOPBACK_ONLY",
        "endpoint_path": "/api/tags",
        "runner_os": os.environ.get("RUNNER_OS", platform.system()),
        "runner_arch": os.environ.get("RUNNER_ARCH", platform.machine()),
        "platform_system": platform.system(),
        "platform_machine": platform.machine(),
        "model_count": len(models),
        "models": models,
        "inventory_semantic_sha256": canonical_sha(models),
        "model_selection_state": "UNBOUND_REQUIRES_EXACT_NAME_AND_DIGEST_SELECTION",
        "effect_executions": 0,
        "forbidden_actions": [
            "MODEL_PULL",
            "MODEL_INSTALL",
            "MODEL_DELETE",
            "MODEL_COPY",
            "MODEL_CREATE",
            "INFERENCE"
        ],
        "coverage_boundary": [
            "LOCAL_LOOPBACK_INVENTORY_ONLY",
            "NO_MODEL_EXECUTION",
            "NO_MODEL_SELECTION",
            "NO_EXTERNAL_NETWORK",
            "NO_RUNTIME_OR_AUTHORITY_CHANGE"
        ],
        "nonclaims": [
            "MODEL_LISTING_NE_MODEL_QUALITY",
            "MODEL_NAME_NE_EXACT_MODEL_IDENTITY_WITHOUT_DIGEST",
            "INSTALLED_NE_VALIDATED_FOR_COCIVIUM",
            "INVENTORY_READBACK_NE_MODEL_MATERIALIZATION",
            "LOCAL_NE_TRUSTED",
            "VALIDATION_IS_NOT_ACCEPTANCE"
        ]
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "STATE": state,
        "checked_out_head_sha": head,
        "model_count": len(models),
        "inventory_semantic_sha256": receipt["inventory_semantic_sha256"],
        "model_selection_state": receipt["model_selection_state"],
        "effect_executions": 0
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
