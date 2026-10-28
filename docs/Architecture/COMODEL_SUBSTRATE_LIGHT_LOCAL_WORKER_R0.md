# CoModel substrate-light x CoLocalModelWorkerR3 adapter canary R0

**State:** `DETERMINISTIC_LOOPBACK_ADAPTER_QUALIFICATION__NO_REAL_MODEL_NO_RUNTIME_NO_CANON`

## Purpose

Reuse the existing `CoLocalModelWorkerR3` adapter rather than minting another local-model path.

The main-branch operations document currently states:

`ADAPTER_READY__OLLAMA_CANARY_NOT_YET_RUN_ON_X2`

R0 deliberately does **not** erase that boundary.

Instead, it qualifies the existing adapter code path across three GitHub-hosted runner OS classes against a deterministic loopback receiver implementing only the bounded Ollama-compatible `/api/generate` contract needed by R3.

## What actually runs

On Linux, Windows and macOS independently:

1. exact-bind the existing worker Git blob;
2. exact-bind its operations-document Git blob;
3. materialize one PUBLIC / LOGICAL_ONLY / REVIEW_CHALLENGE contract;
4. start one local loopback-only deterministic protocol receiver;
5. execute the real `scripts/CoLocalModelWorkerR3.py` worker;
6. require one JSON candidate output;
7. prove all effect counters remain zero;
8. hash the exact contract, worker output and semantic worker result;
9. fan in all three receiver receipts.

The deterministic receiver is test infrastructure, not a model.

## Why this belongs in the substrate-light lane

It tests a practical embodiment boundary:

```text
one logical work contract
-> same existing model adapter
-> distinct OS embodiments
-> exact same bounded candidate artifact
-> zero effect execution
```

That contracts the gap between abstract substrate portability and the already-existing Ollama adapter while preserving the real-runtime gate.

## Real-model gate remains

A genuine Ollama/local-model canary still requires:

- an authorized machine execution route;
- an already-installed local model;
- exact model identity/version/digest where available;
- loopback runtime readback;
- one public-safe low-effect contract;
- exact output receipt;
- receiver readproof;
- independent comparison before integration.

No model install or pull is authorized by this R0 canary.

## Rails

`MOCK_OLLAMA_NE_REAL_OLLAMA_RUNTIME`  
`ADAPTER_PROTOCOL_PASS_NE_REAL_MODEL_MATERIALIZATION`  
`LOCAL_NE_TRUSTED`  
`MODEL_OUTPUT_NE_TRUTH`  
`MODEL_OUTPUT_NE_EFFECT_PERMISSION`  
`RUNNER_OS_DIVERSITY_NE_HARDWARE_DIVERSITY`  
`CROSS_OS_ADAPTER_PASS_NE_MODEL_MIGRATION`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`ADAPTER_PASS_NE_COEX`
