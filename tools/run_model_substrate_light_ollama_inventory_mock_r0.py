#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

FIXTURE = Path("fixtures/substrate/model_substrate_light_ollama_inventory_mock_r0.json")
MOCK = Path("tools/mock_ollama_tags_loopback_r0.py")
PREFLIGHT = Path("tools/preflight_local_ollama_inventory_r0.py")

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
    receipt = root / "ollama-inventory-receipt.json"

    with tempfile.TemporaryDirectory() as td:
        ready = Path(td) / "ready.txt"
        server = subprocess.Popen([
            sys.executable,
            str(MOCK),
            "--fixture", str(FIXTURE),
            "--ready-file", str(ready),
            "--port", "0"
        ])
        port = wait_ready(ready, server)
        completed = subprocess.run([
            sys.executable,
            str(PREFLIGHT),
            "--endpoint", f"http://127.0.0.1:{port}",
            "--output", str(receipt),
            "--timeout-seconds", "10"
        ], text=True, capture_output=True)
        if completed.returncode != 0:
            server.kill()
            fail("FAIL_PREFLIGHT:" + completed.stderr[-1000:])
        try:
            rc = server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            fail("FAIL_MOCK_SERVER_DID_NOT_EXIT")
        if rc != 0:
            fail(f"FAIL_MOCK_SERVER_EXIT:{rc}")

    got = json.loads(receipt.read_text(encoding="utf-8"))
    exp = fx["expected"]
    if got["STATE"] != "PASS_LOCAL_OLLAMA_INVENTORY_READBACK":
        fail("FAIL_RECEIPT_STATE")
    if got["model_count"] != exp["model_count"]:
        fail("FAIL_MODEL_COUNT")
    if got["model_selection_state"] != exp["model_selection_state"]:
        fail("FAIL_SELECTION_STATE")
    if got["effect_executions"] != exp["effect_executions"]:
        fail("FAIL_EFFECT_COUNT")
    expected_pairs = sorted((x["name"], x["digest"]) for x in fx["models"])
    got_pairs = sorted((x["name"], x["digest"]) for x in got["models"])
    if got_pairs != expected_pairs:
        fail("FAIL_MODEL_IDENTITY_SET")

    print(json.dumps({
        "STATE": "PASS_OLLAMA_INVENTORY_PREFLIGHT_PROTOCOL_R0",
        "checked_out_head_sha": got["checked_out_head_sha"],
        "model_count": got["model_count"],
        "inventory_semantic_sha256": got["inventory_semantic_sha256"],
        "model_selection_state": got["model_selection_state"],
        "effect_executions": got["effect_executions"]
    }, separators=(",", ":")))

if __name__ == "__main__":
    main()
