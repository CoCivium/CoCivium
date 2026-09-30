#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path

FIXTURE = Path("fixtures/substrate/model_substrate_light_local_worker_adapter_r0.json")
WORKER = Path("scripts/CoLocalModelWorkerR3.py")
MOCK = Path("tools/mock_ollama_loopback_r0.py")


def fail(code):
    raise SystemExit(code)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest().upper()


def canonical_sha(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def git_blob(ref, path):
    return subprocess.check_output(["git", "rev-parse", f"{ref}:{path}"], text=True).strip()


def wait_for_ready(path, proc, timeout=10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if path.exists():
            return int(path.read_text(encoding="ascii").strip())
        rc = proc.poll()
        if rc is not None:
            fail(f"FAIL_MOCK_SERVER_EARLY_EXIT:{rc}")
        time.sleep(0.05)
    fail("FAIL_MOCK_SERVER_READY_TIMEOUT")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-root", required=True)
    args = ap.parse_args()

    fx = json.loads(FIXTURE.read_text(encoding="utf-8"))
    src = fx["source_bindings"]
    if git_blob("HEAD", src["worker_path"]) != src["worker_blob_sha"]:
        fail("FAIL_WORKER_BLOB_DRIFT")
    if git_blob("HEAD", src["worker_doc_path"]) != src["worker_doc_blob_sha"]:
        fail("FAIL_WORKER_DOC_BLOB_DRIFT")

    root = Path(args.output_root)
    root.mkdir(parents=True, exist_ok=True)
    worker_output = root / "worker-output.json"
    receipt_path = root / "local-worker-receipt.json"

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        contract_path = tdir / "contract.json"
        ready_path = tdir / "ready.txt"
        contract_raw = (json.dumps(fx["contract"], sort_keys=True, indent=2) + "\n").encode("utf-8")
        contract_path.write_bytes(contract_raw)

        server = subprocess.Popen([
            sys.executable,
            str(MOCK),
            "--ready-file", str(ready_path),
            "--port", "0",
            "--expected-model", fx["model_name"],
        ])
        port = wait_for_ready(ready_path, server)

        cmd = [
            sys.executable,
            str(WORKER),
            "--contract", str(contract_path),
            "--model", fx["model_name"],
            "--output", str(worker_output),
            "--endpoint", f"http://127.0.0.1:{port}",
            "--timeout-seconds", "20",
        ]
        completed = subprocess.run(cmd, text=True, capture_output=True)
        if completed.returncode != 0:
            server.kill()
            fail("FAIL_WORKER_EXECUTION:" + completed.stderr[-1000:])

        try:
            server_rc = server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            fail("FAIL_MOCK_SERVER_DID_NOT_EXIT")
        if server_rc != 0:
            fail(f"FAIL_MOCK_SERVER_EXIT:{server_rc}")

    raw = worker_output.read_bytes()
    artifact = json.loads(raw.decode("utf-8"))

    if artifact.get("schema") != "CoLocalModelWorker.R3.v0.1-candidate":
        fail("FAIL_WORKER_SCHEMA")
    if artifact.get("state") != "LOCAL_MODEL_CANDIDATE_OUTPUT__NO_EFFECT_EXECUTION":
        fail("FAIL_WORKER_STATE")
    if artifact.get("contract_sha256") != sha256(contract_raw):
        fail("FAIL_CONTRACT_SHA")
    if artifact.get("model") != fx["model_name"]:
        fail("FAIL_MODEL_BIND")
    if artifact.get("endpoint_class") != "LOOPBACK_ONLY":
        fail("FAIL_ENDPOINT_CLASS")
    if artifact.get("worker_result") != fx["expected_worker_result"]:
        fail("FAIL_WORKER_RESULT")
    if artifact.get("effects") != fx["expected_effects"]:
        fail("FAIL_EFFECTS")
    if not set(fx["required_worker_nonclaims"]).issubset(set(artifact.get("nonclaims", []))):
        fail("FAIL_WORKER_NONCLAIMS")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "schema": "CoModelSubstrateLight.LocalWorkerAdapterReceipt.v0.1",
        "STATE": "PASS_LOCAL_WORKER_LOOPBACK_ADAPTER_R0",
        "checked_out_head_sha": head,
        "runner_os": os.environ.get("RUNNER_OS", platform.system()),
        "runner_arch": os.environ.get("RUNNER_ARCH", platform.machine()),
        "platform_system": platform.system(),
        "platform_machine": platform.machine(),
        "python_version": platform.python_version(),
        "worker_blob_sha": src["worker_blob_sha"],
        "worker_doc_blob_sha": src["worker_doc_blob_sha"],
        "contract_sha256": sha256(contract_raw),
        "worker_output_sha256": sha256(raw),
        "worker_result_semantic_sha256": canonical_sha(artifact["worker_result"]),
        "effect_execution_total": sum(artifact["effects"].values()),
        "network_scope": "LOOPBACK_ONLY",
        "receiver_class": "DETERMINISTIC_OLLAMA_PROTOCOL_MOCK",
        "coverage_boundary": [
            "REAL_COLOCALMODELWORKERR3_CODE_PATH",
            "DETERMINISTIC_LOOPBACK_PROTOCOL_RECEIVER",
            "NO_REAL_MODEL_INFERENCE",
            "NO_EXTERNAL_NETWORK",
            "NO_RUNTIME_OR_AUTHORITY_CHANGE"
        ],
        "nonclaims": fx["nonclaims"],
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "STATE": receipt["STATE"],
        "checked_out_head_sha": head,
        "runner_os": receipt["runner_os"],
        "runner_arch": receipt["runner_arch"],
        "contract_sha256": receipt["contract_sha256"],
        "worker_output_sha256": receipt["worker_output_sha256"],
        "worker_result_semantic_sha256": receipt["worker_result_semantic_sha256"],
        "effect_execution_total": receipt["effect_execution_total"],
        "network_scope": receipt["network_scope"],
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
