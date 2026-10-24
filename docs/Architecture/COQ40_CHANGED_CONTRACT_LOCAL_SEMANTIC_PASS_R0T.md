# Q40 Changed-Contract Local Semantic Pass R0T

**State:** `PASS_Q40_CHANGED_CONTRACT_LOCAL_SEMANTIC_ACCEPTANCE__BOUNDED_CANARY_ONLY`

## Purpose

R0S authorized exactly one changed-contract local attempt after R0Q's strict-JSON but semantically useless `next_probe`.

R0T executes that single bounded attempt on X2/Ollama `qwen3:4b` and independently applies the R0R semantic acceptance rules.

No second changed-contract attempt is authorized or needed for this canary.

## Runtime

Route:

`X2 -> loopback Ollama -> qwen3:4b`

Bounds:

- `think=false`
- `num_ctx=2048`
- `num_predict=320`
- model already installed
- no model pull/install
- no persistent worker
- no scheduler/service/startup hook
- no provider-route disable
- no public effect
- no authority change

Observed elapsed time:

`3893 ms`

Exact local receipt SHA-256:

`81503F0174561B1D332B8BB6A1891EBE2481B0E71CE1E1AE626A5B856BA5DC93`

## Exact candidate

```json
{
  "action": "PROBE",
  "reason": "Artifact LATEST is 90 days old with no current binding",
  "next_probe": {
    "kind": "READ_PROVENANCE_EDGE",
    "target": "LATEST",
    "evidence_surface": "PROVENANCE_EDGE",
    "expected_evidence": "binding_event",
    "negative_evidence": "no_binding_event",
    "stop_condition": "binding_event_found"
  },
  "nonclaim": "STALE_FILE_NE_STALE_SEMANTIC_STATE"
}
```

## Acceptance

Strict JSON:

`PASS`

Changed output structure:

`PASS`

R0R semantic rules:

`PASS`

Semantic acceptance:

`PASS_BOUNDED_DEED_CANDIDATE`

Reasons rejected:

`0`

This is the first bounded Q40 result in this lane where local inference, strict structure, and independent semantic deed acceptance all pass on the actual local output.

## What this proves

`LOCAL_MODEL_EXECUTION = PROVEN_BOUNDED_X2`

`STRICT_OUTPUT_CONTRACT = PROVEN`

`STRUCTURED_EVIDENCE_PROBE = PROVEN_ON_ACTUAL_OUTPUT`

`INDEPENDENT_SEMANTIC_DEED_ACCEPTANCE = PROVEN_BOUNDED`

## What this does not prove

It does **not** prove:

- model truth;
- receiver execution of the proposed probe;
- semantic acceptance across arbitrary deeds;
- integration;
- persistent local worker operation;
- background autonomy;
- ChatGPT independence;
- provider-exit completion;
- host/site/power/network/credential failure-domain independence.

The canary itself was orchestrated from this provider session.

`CHATGPT_ORCHESTRATED_LOCAL_CANARY_NE_CHATGPT_NOT_REQUIRED`

## Q40 disposition

Q40 can now close for this bounded proof target:

> one recurring advisory deed with an exact changed input/output contract can execute on the existing local/open route and produce an independently accepted evidence-producing deed candidate.

A stronger successor question remains:

> Can a machine-owned local worker receive a pre-existing signed task and emit a signed/hashed accepted receipt without ChatGPT orchestrating the run?

That successor is distinct from Q40's bounded compilation proof.

## Rails

`MODEL_OUTPUT_NE_TRUTH`  
`STRICT_OUTPUT_PASS_NE_GLOBAL_SEMANTIC_RELIABILITY`  
`SEMANTIC_ACCEPTANCE_NE_RECEIVER_EXECUTION`  
`ACCEPTED_DEED_NE_INTEGRATED_WORKER`  
`CHATGPT_ORCHESTRATED_LOCAL_CANARY_NE_CHATGPT_NOT_REQUIRED`  
`LOCAL_ROUTE_NE_PROVIDER_EXIT_COMPLETE`  
`LOCAL_NE_INDEPENDENT_UNLESS_FAILURE_DOMAINS_PROVEN`  
`ONE_CHANGED_CONTRACT_ATTEMPT_NE_RETRY_LOOP`  
`VALIDATION_IS_NOT_ACCEPTANCE`
