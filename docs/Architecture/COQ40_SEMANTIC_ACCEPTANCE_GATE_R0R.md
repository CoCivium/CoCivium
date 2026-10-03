# Q40 Semantic Acceptance Gate R0R

**State:** `CANDIDATE_SEMANTIC_VERIFIER__NO_LOCAL_RETRY_NO_RUNTIME_AUTHORITY_CHANGE`

## CoHereNow

R0Q proved that X2/Ollama `qwen3:4b` can execute the bounded CoSneak deed and, after one bounded repair, satisfy the strict JSON shape.

It did **not** prove a useful deed.

The returned:

`next_probe = "2024-05-15"`

is a date, not an evidence-producing probe.

R0R therefore does not ask the model again. It makes semantic usefulness independently testable.

## Contract

A candidate deed may be semantically accepted only when it preserves:

- an allowed action: `PROBE` or `PARK`;
- the required nonclaim;
- a nonempty reason;
- a structured `next_probe` object.

The probe object must name:

```text
kind
target
evidence_surface
expected_evidence
negative_evidence
stop_condition
```

Allowed R0 probe kinds are deliberately narrow:

- `READ_EXACT_CURRENTNESS_BINDING`
- `READ_RECEIVER_STATE`
- `READ_PROVENANCE_EDGE`
- `WAIT_FOR_NAMED_WAKE_EVENT`

This prevents a syntactically tidy model response from smuggling an unexplained date, vague suggestion, or endless investigation through the acceptance boundary.

## Two controls

### Actual R0Q local output

The exact recorded R0Q attempt-2 object is rebound from the source fixture.

Expected disposition:

`REJECT: NEXT_PROBE_NOT_STRUCTURED`

No second local retry is authorized merely because the verifier exists.

`FAILED_DEED_NE_PERMISSION_TO_RETRY_UNCHANGED`

### Positive verifier control

A synthetic candidate with an exact currentness-binding probe is expected to pass.

This exists only to prove that the verifier is not a reject-all machine.

`VERIFIER_POSITIVE_CONTROL_NE_MODEL_PASS`

## Meaning

The local/open-model frontier is now more precise:

```text
local inference
  PASS

strict JSON contract
  PASS on bounded retry

semantic evidence-producing deed
  HOLD on actual output

independent verifier shape
  PASS if CI confirms R0R
```

The next earned local test is not "try again until qwen says something nicer."

It is:

1. upgrade the compiler prompt/output contract to emit the structured probe object;
2. perform at most one changed-contract local canary;
3. have this verifier judge it independently;
4. require a receiver/readproof before any recurring worker acceptance.

## Boundary

R0R performs no local inference, worker installation, scheduler mutation, provider-task disable, account action, public effect, canon promotion, or CoEx promotion.

Q40 remains open until an actual local output passes the semantic gate and the elected receiver accepts the exact object.

## Rails

`STRICT_OUTPUT_PASS_NE_SEMANTIC_ACCEPTANCE`  
`SCHEMA_VALID_NE_EVIDENCE_PRODUCING`  
`DATE_NE_PROBE`  
`SEMANTIC_VERIFIER_NE_TRUTH_ORACLE`  
`VERIFIER_POSITIVE_CONTROL_NE_MODEL_PASS`  
`REJECTED_OUTPUT_NE_FAILED_LOCAL_ROUTE`  
`FAILED_DEED_NE_PERMISSION_TO_RETRY_UNCHANGED`  
`COMPILED_DEED_NE_ACCEPTED_WORKER`  
`LOCAL_EXECUTION_NE_PROVIDER_INDEPENDENCE_PROOF`  
`VALIDATION_IS_NOT_ACCEPTANCE`
