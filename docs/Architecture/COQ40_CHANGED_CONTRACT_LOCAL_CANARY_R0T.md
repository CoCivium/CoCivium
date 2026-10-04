# Q40 Changed-Contract Local Canary R0T

**State:** `PASS_CHANGED_CONTRACT_LOCAL_OUTPUT_AND_SEMANTIC_GATE__BOUNDED_CANARY_ONLY`

R0S authorized at most one changed-contract local canary. R0T executed exactly one on X2 against the already-installed loopback Ollama `qwen3:4b` route.

The output contract required:

`action | reason | next_probe{kind,target,evidence_surface,expected_evidence,negative_evidence,stop_condition} | nonclaim`

Runtime bounds:

- `think=false`
- `num_ctx=2048`
- `num_predict=320`
- `keep_alive=0`
- loopback endpoint only
- no model install/pull
- no persistent worker/service/scheduler/startup hook
- no public or authority effect

Observed:

`elapsed_ms = 4887`

`strict_structure = true`

`semantic_acceptance = true`

Output SHA-256:

`7DD9247E587BEC3FEBAB69BE0292E695693BC2C2A71ED9BE5490D3679A062639`

The model elected `PROBE` with a structured `EXACT_CURRENTNESS_READ` and preserved:

`STALE_FILE_NE_STALE_SEMANTIC_STATE`

This advances Q40 from syntax-only local execution to one bounded local model output accepted by the structured semantic gate.

It still does **not** prove:

- model output truth;
- execution of the proposed probe;
- receiver pickup/integration;
- a persistent recurring worker;
- ChatGPT-independent orchestration;
- provider-exit completeness;
- cross-host/site/power/network/credential independence.

Current Q40 ladder:

`LOCAL_EXECUTION = PROVEN`

`STRICT_STRUCTURED_OUTPUT = PROVEN`

`STRUCTURED_SEMANTIC_GATE_ACCEPTANCE = PROVEN_ON_ONE_CHANGED-CONTRACT CANARY`

`PROBE_EXECUTION = NOT RUN`

`PERSISTENT_WORKER = NOT INSTALLED`

`CHATGPT_INDEPENDENCE = NOT PROVEN`

The next earned rung is not another model call. It is deterministic execution/verification of the elected read-only probe, followed by receiver disposition.

Rails:

`MODEL_OUTPUT_NE_TRUTH`  
`SEMANTIC_GATE_NE_TRUTH_ORACLE`  
`ACCEPTED_DEED_NE_EXECUTED_PROBE`  
`ONE_CANARY_NE_RECURRING_WORKER`  
`CHATGPT_ORCHESTRATED_LOCAL_CANARY_NE_CHATGPT_NOT_REQUIRED`  
`LOCAL_NE_INDEPENDENT_UNLESS_FAILURE_DOMAINS_PROVEN`  
`VALIDATION_IS_NOT_ACCEPTANCE`
