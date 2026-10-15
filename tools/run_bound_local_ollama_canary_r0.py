#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def fail(code: str) -> None:
    raise SystemExit(code)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def canonical_sha(obj) -> str:
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail("FAIL_JSON_OBJECT")
    return value


def exact_model(receipt: dict, name: str, digest: str) -> dict:
    matches = [
        m for m in receipt.get("models", [])
        if m.get("name") == name and str(m.get("digest", "")).lower() == digest.lower()
    ]
    if len(matches) != 1:
        fail(f"FAIL_EXACT_MODEL_BIND_COUNT:{len(matches)}")
    return matches[0]


def run_checked(cmd: list[str]) -> subprocess.CompletedProcess:
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.returncode != 0:
        fail("FAIL_SUBPROCESS:" + p.stderr[-1200:])
    return p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default="http://127.0.0.1:11434")
    ap.add_argument("--model-name", required=True)
    ap.add_argument("--model-digest", required=True)
    ap.add_argument("--contract", required=True)
    ap.add_argument("--worker-output", required=True)
    ap.add_argument("--receipt-output", required=True)
    ap.add_argument("--timeout-seconds", type=int, default=120)
    args = ap.parse_args()

    digest = args.model_digest.lower()
    if len(digest) != 64:
        fail("FAIL_MODEL_DIGEST_LENGTH")
    try:
        int(digest, 16)
    except ValueError:
        fail("FAIL_MODEL_DIGEST_HEX")

    worker_output = Path(args.worker_output).resolve()
    receipt_output = Path(args.receipt_output).resolve()
    if worker_output.exists() or receipt_output.exists():
        fail("FAIL_CLOSED_NO_CLOBBER")

    contract_path = Path(args.contract).resolve()
    contract_raw = contract_path.read_bytes()
    contract = json.loads(contract_raw.decode("utf-8"))
    if not isinstance(contract, dict):
        fail("FAIL_CONTRACT_OBJECT")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        pre_path = tdir / "inventory-pre.json"
        post_path = tdir / "inventory-post.json"

        run_checked([
            sys.executable,
            "tools/preflight_local_ollama_inventory_r0.py",
            "--endpoint", args.endpoint,
            "--output", str(pre_path),
            "--timeout-seconds", str(min(args.timeout_seconds, 30)),
        ])
        pre = load_json(pre_path)
        if pre.get("STATE") != "PASS_LOCAL_OLLAMA_INVENTORY_READBACK":
            fail("FAIL_PRE_INVENTORY_STATE")
        pre_model = exact_model(pre, args.model_name, digest)

        run_checked([
            sys.executable,
            "scripts/CoLocalModelWorkerR3.py",
            "--contract", str(contract_path),
            "--model", args.model_name,
            "--output", str(worker_output),
            "--endpoint", args.endpoint,
            "--timeout-seconds", str(args.timeout_seconds),
        ])

        worker_raw = worker_output.read_bytes()
        worker = json.loads(worker_raw.decode("utf-8"))
        if worker.get("state") != "LOCAL_MODEL_CANDIDATE_OUTPUT__NO_EFFECT_EXECUTION":
            fail("FAIL_WORKER_STATE")
        if worker.get("model") != args.model_name:
            fail("FAIL_WORKER_MODEL_NAME")
        if worker.get("contract_sha256") != sha256(contract_raw):
            fail("FAIL_WORKER_CONTRACT_SHA")
        if sum(int(v) for v in worker.get("effects", {}).values()) != 0:
            fail("FAIL_WORKER_EFFECT_EXECUTED")

        run_checked([
            sys.executable,
            "tools/preflight_local_ollama_inventory_r0.py",
            "--endpoint", args.endpoint,
            "--output", str(post_path),
            "--timeout-seconds", str(min(args.timeout_seconds, 30)),
        ])
        post = load_json(post_path)
        if post.get("STATE") != "PASS_LOCAL_OLLAMA_INVENTORY_READBACK":
            fail("FAIL_POST_INVENTORY_STATE")
        post_model = exact_model(post, args.model_name, digest)

    if pre_model != post_model:
        fail("FAIL_MODEL_RECORD_DRIFT")
    if pre.get("inventory_semantic_sha256") != post.get("inventory_semantic_sha256"):
        fail("FAIL_INVENTORY_DRIFT")

    receipt = {
        "schema": "CoModelSubstrateLight.BoundOllamaRunReceipt.v0.1",
        "STATE": "PASS_BOUND_LOCAL_OLLAMA_MODEL_RUN",
        "checked_out_head_sha": head,
        "endpoint_class": "LOOPBACK_ONLY",
        "selected_model": {
            "name": args.model_name,
            "digest": digest,
            "reported_model_record": pre_model,
        },
        "pre_inventory_semantic_sha256": pre["inventory_semantic_sha256"],
        "post_inventory_semantic_sha256": post["inventory_semantic_sha256"],
        "inventory_stable": True,
        "contract_sha256": sha256(contract_raw),
        "worker_output_sha256": sha256(worker_raw),
        "worker_result_semantic_sha256": canonical_sha(worker["worker_result"]),
        "effect_execution_total": 0,
        "model_pull_or_install_performed": False,
        "coverage_boundary": [
            "ONE_EXPLICIT_NAME_PLUS_DIGEST_BIND",
            "ONE_PUBLIC_LOGICAL_ONLY_WORKER_CALL",
            "PRE_AND_POST_LOOPBACK_INVENTORY_READBACK",
            "NO_MODEL_PULL_OR_INSTALL",
            "NO_AUTHORITY_CHANGE",
        ],
        "nonclaims": [
            "OLLAMA_REPORTED_DIGEST_NE_UNIVERSAL_MODEL_IDENTITY",
            "DIGEST_STABILITY_NE_MODEL_QUALITY",
            "DIGEST_STABILITY_NE_DETERMINISTIC_OUTPUT",
            "BOUND_RUN_NE_RECEIVER_PICKUP",
            "BOUND_RUN_NE_RUNTIME_INTEGRATION",
            "LOCAL_NE_TRUSTED",
            "MODEL_OUTPUT_NE_TRUTH",
            "VALIDATION_IS_NOT_ACCEPTANCE",
        ],
    }
    receipt_output.parent.mkdir(parents=True, exist_ok=True)
    receipt_output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "STATE": receipt["STATE"],
        "checked_out_head_sha": head,
        "model_name": args.model_name,
        "model_digest": digest,
        "inventory_stable": True,
        "contract_sha256": receipt["contract_sha256"],
        "worker_output_sha256": receipt["worker_output_sha256"],
        "worker_result_semantic_sha256": receipt["worker_result_semantic_sha256"],
        "effect_execution_total": 0,
        "model_pull_or_install_performed": False,
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
