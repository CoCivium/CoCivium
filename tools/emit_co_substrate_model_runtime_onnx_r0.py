#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import onnxruntime as ort

MODEL=Path("model-runtime-canary.onnx")
MANIFEST=Path("model-runtime-canary-manifest.json")

def sha256_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(65536),b""):
            h.update(chunk)
    return h.hexdigest().upper()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    m=json.loads(MANIFEST.read_text(encoding="utf-8"))
    if sha256_file(MODEL)!=m["model_sha256"]:
        raise SystemExit("FAIL: model digest mismatch")
    sess=ort.InferenceSession(str(MODEL),providers=["CPUExecutionProvider"])
    result=sess.run(None,{"x":np.array(m["input"],dtype=np.float32)})[0]
    expected=np.array(m["expected_output"],dtype=np.float32)
    if not np.allclose(result,expected,rtol=0,atol=1e-6):
        raise SystemExit(f"FAIL: output mismatch {result.tolist()} != {expected.tolist()}")
    att={
        "schema":"CoSubstrateIndependence.ModelRuntimeAttestation.R0",
        "engine":"onnxruntime",
        "engine_version":ort.__version__,
        "model_sha256":m["model_sha256"],
        "fixture_semantic_sha256":m["fixture_semantic_sha256"],
        "input":m["input"],
        "output":result.tolist(),
        "authority_state":m["authority_state"],
        "pr_head_sha":m["pr_head_sha"],
        "pr_base_sha":m["pr_base_sha"],
        "accepted_for_scope":True,
        "scope":"DETERMINISTIC_INFERENCE_CONTINUITY_FOR_DECLARED_CANARY",
        "nonclaims":m["nonclaims"]
    }
    Path(args.out).write_text(json.dumps(att,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(att,separators=(",",":"),sort_keys=True))

if __name__=="__main__":
    main()
