# Q40 Changed-Contract Local Canary R0S

**State:** `CHANGED_CONTRACT_PREPARED__LOCAL_EXECUTION_NOT_YET_RUN__NO_RUNTIME_AUTHORITY_CHANGE`

## CoHereNow

R0Q proved bounded local inference on X2/Ollama `qwen3:4b`, but its actual strict-JSON result failed semantic acceptance because:

`next_probe = "2024-05-15"`

was merely a date.

R0R then independently proved the stronger semantic contract:

```text
next_probe = {
  kind,
  target,
  evidence_surface,
  expected_evidence,
  negative_evidence,
  stop_condition
}
```

R0S compiles that verifier contract back into the local-model request.

It deliberately does **not** run the model again in GitHub CI and does not pretend preparation is execution.

## Changed contract

The next local output must contain exactly:

```text
action
reason
next_probe
nonclaim
```

where `next_probe` is a structured evidence-producing object.

Allowed probe kinds remain the exact R0R set:

- `READ_EXACT_CURRENTNESS_BINDING`
- `READ_RECEIVER_STATE`
- `READ_PROVENANCE_EDGE`
- `WAIT_FOR_NAMED_WAKE_EVENT`

The required nonclaim remains:

`STALE_FILE_NE_STALE_SEMANTIC_STATE`

## Anti-loop

The changed contract authorizes at most one future local attempt.

That is a **different contract**, not another retry of the rejected prompt.

After that one attempt:

```text
local output
-> strict structure check
-> independent R0R semantic verifier
-> accept or preserve failure
-> stop
```

No "keep asking until the model says something prettier" loop is permitted.

`FAILED_DEED_NE_PERMISSION_TO_RETRY_UNCHANGED`

`ONE_CHANGED_CONTRACT_ATTEMPT_NE_RETRY_LOOP`

## Positive control

R0S carries one synthetic structured currentness probe solely to prove that the compiled contract is satisfiable.

It is not evidence that the local model will produce that object.

`POSITIVE_CONTROL_NE_MODEL_PASS`

## Next gate

Receiver:

`provider-exit-planner`

Action:

`RUN_AT_MOST_ONE_CHANGED_CONTRACT_LOCAL_CANARY_THEN_APPLY_R0R_SEMANTIC_VERIFIER`

Success requires the exact local-model output to pass the verifier independently.

Negative evidence is equally useful: if the changed-contract output fails, preserve it and stop.

## Boundary

R0S performs no:

- local-model inference;
- model pull/install;
- persistent worker install;
- scheduler mutation;
- provider-route disable;
- account closure;
- public effect;
- canon or CoEx promotion.

Q40 remains open.

## Rails

`CONTRACT_CHANGE_NE_LOCAL_MODEL_EXECUTION`  
`PROMPT_READY_NE_MODEL_PASS`  
`POSITIVE_CONTROL_NE_MODEL_PASS`  
`STRICT_OUTPUT_PASS_NE_SEMANTIC_ACCEPTANCE`  
`FAILED_DEED_NE_PERMISSION_TO_RETRY_UNCHANGED`  
`ONE_CHANGED_CONTRACT_ATTEMPT_NE_RETRY_LOOP`  
`COMPILED_DEED_NE_ACCEPTED_WORKER`  
`LOCAL_EXECUTION_NE_PROVIDER_INDEPENDENCE_PROOF`  
`LOCAL_ROUTE_NE_PROVIDER_EXIT_COMPLETE`  
`VALIDATION_IS_NOT_ACCEPTANCE`
