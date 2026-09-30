# CoModel substrate-light exact-bound Ollama execution wrapper R0

**State:** `EXACT_NAME_DIGEST_BOUND_EXECUTION_PATH_READY__REAL_X2_RUN_UNPROVEN`

## Purpose

Prevent the first real local-model canary from silently executing a different model than the one whose inventory identity was reviewed.

The wrapper requires an explicit:

`model name + locally reported Ollama digest`

and verifies that same exact pair both **before and after** one bounded `CoLocalModelWorkerR3` call.

## Execution shape

```text
GET /api/tags
-> require exactly one name+digest match
-> run one PUBLIC / LOGICAL_ONLY worker call
-> GET /api/tags again
-> require same exact model record
-> require inventory semantic hash unchanged
-> emit bound-run receipt
```

If the exact pair is missing, duplicated, changed, or the inventory drifts, the wrapper fails closed.

## Authority and effects

The underlying worker remains limited to:

- `OBSERVE`
- `PROPOSE`
- `REVIEW_CHALLENGE`

The bound-run receipt requires total effect execution = 0.

The wrapper has no code path to pull or install a model.

## Identity boundary

The Ollama-reported digest is an exact runtime inventory anchor for this bounded canary.

It is **not** claimed to be a universal identity for every serialization, quantization, model family, provider embodiment, or future substrate.

`OLLAMA_REPORTED_DIGEST_NE_UNIVERSAL_MODEL_IDENTITY`

Likewise, stable model identity does not imply deterministic output or model quality.

## CI qualification

CI exercises the exact wrapper on Linux, Windows and macOS against a deterministic loopback receiver that implements:

- `GET /api/tags`
- `POST /api/generate`

The mock exposes two models but the wrapper must execute only the explicitly named and digest-bound one.

That proves the binding protocol and fail-closed execution path, not real-model inference.

## Real machine gate

When an authorized machine route exists:

1. run the read-only inventory preflight;
2. select one already-installed candidate by exact name+digest;
3. provide the pair explicitly to this wrapper;
4. execute one PUBLIC / LOGICAL_ONLY bounded contract;
5. preserve pre/post inventory receipts and exact worker-output hash;
6. require an elected receiver readproof before any `PICKED_UP` claim;
7. require explicit acceptance before `INTEGRATED`.

## Rails

`MODEL_NAME_NE_EXACT_MODEL_IDENTITY_WITHOUT_DIGEST`  
`OLLAMA_REPORTED_DIGEST_NE_UNIVERSAL_MODEL_IDENTITY`  
`DIGEST_STABILITY_NE_MODEL_QUALITY`  
`DIGEST_STABILITY_NE_DETERMINISTIC_OUTPUT`  
`BOUND_RUN_NE_RECEIVER_PICKUP`  
`BOUND_RUN_NE_RUNTIME_INTEGRATION`  
`NO_MODEL_PULL_OR_INSTALL`  
`LOCAL_NE_TRUSTED`  
`VALIDATION_IS_NOT_ACCEPTANCE`
