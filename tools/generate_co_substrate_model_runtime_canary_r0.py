#!/usr/bin/env python3
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper

OUT_MODEL=Path("model-runtime-canary.onnx")
OUT_MANIFEST=Path("model-runtime-canary-manifest.json")
FIXTURE=Path("fixtures/substrate/co_substrate_cross_host_object_r0.json")

def sha256_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(65536),b""):
            h.update(chunk)
    return h.hexdigest().upper()

def main():
    fixture=json.loads(FIXTURE.read_text(encoding="utf-8"))
    input_value=np.array([[1.0,2.0,3.0]],dtype=np.float32)
    weights=np.array([[1.0,-1.0],[2.0,0.5],[0.25,3.0]],dtype=np.float32)
    bias=np.array([0.5,-2.0],dtype=np.float32)

    x=helper.make_tensor_value_info("x",TensorProto.FLOAT,[1,3])
    y=helper.make_tensor_value_info("y",TensorProto.FLOAT,[1,2])
    w=numpy_helper.from_array(weights,name="W")
    b=numpy_helper.from_array(bias,name="B")
    nodes=[
        helper.make_node("MatMul",["x","W"],["m"]),
        helper.make_node("Add",["m","B"],["y"]),
    ]
    graph=helper.make_graph(nodes,"CoSubstrateModelRuntimeCanary",[x],[y],[w,b])
    model=helper.make_model(graph,producer_name="CoCivium",opset_imports=[helper.make_opsetid("",13)])
    model.ir_version=min(model.ir_version,10)
    onnx.save(model,OUT_MODEL)

    expected=(input_value @ weights + bias).tolist()
    fixture_semantic=json.dumps(fixture,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    manifest={
        "schema":"CoSubstrateIndependence.ModelRuntimeCanary.R0",
        "state":"CI_MODEL_RUNTIME_DIVERSITY_CANARY__NOT_LLM_NOT_PRODUCTION",
        "model_sha256":sha256_file(OUT_MODEL),
        "fixture_semantic_sha256":hashlib.sha256(fixture_semantic).hexdigest().upper(),
        "input":input_value.tolist(),
        "expected_output":expected,
        "authority_state":fixture["authority_state"],
        "pr_head_sha":os.environ.get("CO_PR_HEAD_SHA",""),
        "pr_base_sha":os.environ.get("CO_PR_BASE_SHA",""),
        "nonclaims":[
            "INFERENCE_ENGINE_DIVERSITY_NE_LLM_RUNTIME_DIVERSITY",
            "CI_MODEL_CANARY_NE_X2_LOCAL_MODEL_HANDOFF",
            "NUMERIC_OUTPUT_MATCH_NE_AGENT_IDENTITY"
        ]
    }
    OUT_MANIFEST.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(manifest,separators=(",",":"),sort_keys=True))

if __name__=="__main__":
    main()
