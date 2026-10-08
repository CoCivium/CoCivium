#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import openvino as ov
from importlib.metadata import version

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
    core=ov.Core()
    model=core.read_model(str(MODEL))
    compiled=core.compile_model(model,"CPU")
    inp=compiled.input(0)
    out=compiled.output(0)
    result=compiled({inp:np.array(m["input"],dtype=np.float32)})[out]
    expected=np.array(m["expected_output"],dtype=np.float32)
    if not np.allclose(result,expected,rtol=0,atol=1e-6):
        raise SystemExit(f"FAIL: output mismatch {result.tolist()} != {expected.tolist()}")
    att={
        "schema":"CoSubstrateIndependence.ModelRuntimeAttestation.R0",
        "engine":"openvino",
        "engine_version":version("openvino"),
        "model_sha256":m["model_sha256"],
        "fixture_semantic_sha256":m["fixture_semantic_sha256"],
        "input":m["input"],
        "output":np.asarray(result,dtype=np.float32).tolist(),
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
