#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

FIXTURE = Path("fixtures/substrate/model_substrate_light_bound_ollama_mock_r0.json")
SERVER = Path("tools/mock_bound_ollama_runtime_r0.py")
WRAPPER = Path("tools/run_bound_local_ollama_canary_r0.py")

def fail(code):
    raise SystemExit(code)

def wait_ready(path, proc, timeout=10.0):
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
    root = Path(args.output_root)
    root.mkdir(parents=True, exist_ok=True)
    worker_output = root / "bound-worker-output.json"
    receipt_output = root / "bound-ollama-receipt.json"

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        ready = tdir / "ready.txt"
        contract = tdir / "contract.json"
        contract.write_bytes((json.dumps(fx["contract"], indent=2, sort_keys=True) + "\n").encode("utf-8"))
        proc = subprocess.Popen([
            sys.executable,
            str(SERVER),
            "--fixture", str(FIXTURE),
            "--ready-file", str(ready),
            "--port", "0"
        ])
        port = wait_ready(ready, proc)
        completed = subprocess.run([
            sys.executable,
            str(WRAPPER),
            "--endpoint", f"http://127.0.0.1:{port}",
            "--model-name", fx["selected_model"]["name"],
            "--model-digest", fx["selected_model"]["digest"],
            "--contract", str(contract),
            "--worker-output", str(worker_output),
            "--receipt-output", str(receipt_output),
            "--timeout-seconds", "20"
        ], text=True, capture_output=True)
        proc.kill()
        proc.wait(timeout=5)
        if completed.returncode != 0:
            fail("FAIL_BOUND_WRAPPER:" + completed.stderr[-1200:])

    receipt = json.loads(receipt_output.read_text(encoding="utf-8"))
    worker = json.loads(worker_output.read_text(encoding="utf-8"))
    if receipt["STATE"] != "PASS_BOUND_LOCAL_OLLAMA_MODEL_RUN":
        fail("FAIL_RECEIPT_STATE")
    if receipt["selected_model"]["name"] != fx["selected_model"]["name"]:
        fail("FAIL_SELECTED_NAME")
    if receipt["selected_model"]["digest"] != fx["selected_model"]["digest"]:
        fail("FAIL_SELECTED_DIGEST")
    if receipt["inventory_stable"] is not True:
        fail("FAIL_INVENTORY_STABILITY")
    if receipt["effect_execution_total"] != 0:
        fail("FAIL_EFFECT_COUNT")
    if receipt["model_pull_or_install_performed"] is not False:
        fail("FAIL_PULL_INSTALL_FLAG")
    if worker["worker_result"] != fx["expected_worker_result"]:
        fail("FAIL_WORKER_RESULT")

    print(json.dumps({
        "STATE": "PASS_BOUND_OLLAMA_PROTOCOL_CANARY_R0",
        "checked_out_head_sha": receipt["checked_out_head_sha"],
        "model_name": receipt["selected_model"]["name"],
        "model_digest": receipt["selected_model"]["digest"],
        "inventory_stable": receipt["inventory_stable"],
        "contract_sha256": receipt["contract_sha256"],
        "worker_output_sha256": receipt["worker_output_sha256"],
        "worker_result_semantic_sha256": receipt["worker_result_semantic_sha256"],
        "effect_execution_total": receipt["effect_execution_total"],
        "model_pull_or_install_performed": receipt["model_pull_or_install_performed"]
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
