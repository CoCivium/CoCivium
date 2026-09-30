#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

MODEL_PATH = Path("fixtures/substrate/model_substrate_light_portable_model_r0.json")


def fail(code):
    raise SystemExit(code)


def canonical_bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest().upper()


def git_blob(ref, path):
    return subprocess.check_output(["git", "rev-parse", f"{ref}:{path}"], text=True).strip()


def infer(params, vector):
    weights = params["weights"]
    bias = params["bias"]
    if len(weights) != len(bias):
        fail("FAIL_PARAMETER_SHAPE")
    logits = []
    for row, b in zip(weights, bias):
        if len(row) != len(vector):
            fail("FAIL_INPUT_SHAPE")
        logits.append(sum(w * x for w, x in zip(row, vector)) + b)
    best = max(range(len(logits)), key=lambda i: logits[i])
    return logits, best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    raw = MODEL_PATH.read_bytes()
    doc = json.loads(raw.decode("utf-8"))
    src = doc["source_bindings"]

    if git_blob("HEAD", src["substrate_doc_path"]) != src["substrate_doc_blob_sha"]:
        fail("FAIL_SUBSTRATE_DOC_BLOB_DRIFT")
    if git_blob("HEAD", src["virtual_session_doc_path"]) != src["virtual_session_doc_blob_sha"]:
        fail("FAIL_VIRTUAL_SESSION_DOC_BLOB_DRIFT")

    outputs = []
    for case in doc["inference_cases"]:
        logits, klass = infer(doc["parameters"], case["input"])
        if logits != case["expected_logits"]:
            fail("FAIL_LOGITS:" + case["id"])
        if klass != case["expected_class"]:
            fail("FAIL_CLASS:" + case["id"])
        outputs.append({
            "id": case["id"],
            "logits": logits,
            "class": klass
        })

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "schema": "CoModelSubstrateLight.PortableReceipt.v0.1",
        "STATE": "PASS_PORTABLE_PARAMETERIZED_MODEL_RECONSTRUCTION",
        "checked_out_head_sha": head,
        "logical_model_id": doc["logical_model_id"],
        "model_kind": doc["model_kind"],
        "model_version": doc["version"],
        "model_pack_sha256": sha256_bytes(raw),
        "parameter_semantic_sha256": sha256_bytes(canonical_bytes(doc["parameters"])),
        "inference_semantic_sha256": sha256_bytes(canonical_bytes(outputs)),
        "inference_case_count": len(outputs),
        "identity_invariants_sha256": sha256_bytes(canonical_bytes(doc["identity_invariants"])),
        "runner_os": os.environ.get("RUNNER_OS", platform.system()),
        "runner_arch": os.environ.get("RUNNER_ARCH", platform.machine()),
        "python_version": platform.python_version(),
        "platform_system": platform.system(),
        "platform_machine": platform.machine(),
        "process_id": os.getpid(),
        "outputs": outputs,
        "coverage_boundary": [
            "SMALL_INTEGER_PARAMETERIZED_MODEL_ONLY",
            "NO_EXTERNAL_MODEL_DOWNLOAD",
            "NO_REAL_LLM_WEIGHTS",
            "NO_PERSISTENT_RUNTIME",
            "NO_AUTHORITY_CHANGE"
        ],
        "nonclaims": doc["nonclaims"]
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "STATE": receipt["STATE"],
        "checked_out_head_sha": head,
        "logical_model_id": receipt["logical_model_id"],
        "runner_os": receipt["runner_os"],
        "runner_arch": receipt["runner_arch"],
        "model_pack_sha256": receipt["model_pack_sha256"],
        "inference_semantic_sha256": receipt["inference_semantic_sha256"]
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
