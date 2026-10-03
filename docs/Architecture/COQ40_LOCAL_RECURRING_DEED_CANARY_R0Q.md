# Q40 Local/Open Recurring-Deed Canary R0Q

**State:** `PARTIAL_PASS_LOCAL_MODEL_EXECUTION_AND_STRICT_JSON__SEMANTIC_ACCEPTANCE_HELD`

## Purpose

R0P elected `Q40_COMPILE_RECURRING_DEED_LOCAL`.

R0Q compiles one recurring advisory CoSneak deed into a bounded X2/Ollama task:

> Given a public-safe CoSneak signal, classify whether to `PROBE` or `PARK`, state a reason, name the next probe, and preserve a required nonclaim.

No persistent worker, scheduler, service, startup hook, provider-session mutation, repository mutation, public effect, or authority change was installed.

## Runtime evidence

Machine route: X2.

Local runtime:

- Ollama executable already installed;
- model `qwen3:4b` already installed;
- endpoint loopback only;
- `think=false`;
- bounded `num_ctx=2048`;
- no model pull/install.

Task SHA-256:

`66B273858E4AF05B551B77CFBCE9664DF239C1B4160FCB617242535EFC71082A`

### First attempt

The first bounded attempt used `num_predict=96`.

The local model executed but returned truncated/malformed JSON.

Classification:

`LOCAL_MODEL_EXECUTION_PROVEN__STRICT_OUTPUT_CONTRACT_FAIL`

This is preserved as negative evidence.

`FAILED_OUTPUT_CONTRACT_NE_FAILED_MODEL`

### One bounded repair/retry

The retry tightened the schema, constrained string lengths, fixed the required nonclaim enum, and raised `num_predict` to `192`.

Observed:

`state = PASS_LOCAL_MODEL_STRICT_OUTPUT_CONTRACT`

`elapsed_ms = 2918`

Output SHA-256:

`B6BEC90BB5D063AADE9CD756C96AF02053E4F05AA7E35BA61C727C38FCE5ADDF`

Returned object:

`action = PARK`

`reason = "Artifact LATEST is 90 days old with no current binding"`

`next_probe = "2024-05-15"`

`nonclaim = STALE_FILE_NE_STALE_SEMANTIC_STATE`

The output is syntactically valid and schema-conformant.

## Semantic challenge

The `next_probe` value is merely an unexplained date and does not describe an evidence-producing probe.

Therefore the independent acceptance judgment is:

`STRICT_JSON_PASS__SEMANTIC_DEED_ACCEPTANCE_HOLD`

The model output is not promoted to an accepted worker result.

This is the useful proof:

1. bounded local inference works;
2. strict structured output can pass under resource-bounded settings;
3. strict schema conformance is still insufficient for semantic usefulness;
4. an independent semantic gate is required before a compiled deed can be accepted.

## Q40 disposition

Q40 is **not closed as fully proven**.

Current state:

`LOCAL_ROUTE_EXECUTION = PROVEN_BOUNDED_X2`

`STRICT_OUTPUT_CONTRACT = PROVEN_ON_RETRY`

`USEFUL_RECURRING_DEED_SEMANTIC_ACCEPTANCE = NOT_PROVEN`

`CHATGPT_INDEPENDENCE = NOT_PROVEN`

`PERSISTENT_LOCAL_WORKER = NOT_INSTALLED`

`CROSS_FAILURE_DOMAIN_INDEPENDENCE = NOT_PROVEN`

The next earned rung is a semantic verifier / receiver disposition that fails closed on the current bad `next_probe` and accepts only an evidence-producing probe.

Do not retry the model repeatedly merely to obtain prettier output.

## Rails

`MODEL_RESPONSE_NE_CONTRACT_PASS`  
`STRICT_OUTPUT_PASS_NE_SEMANTIC_ACCEPTANCE`  
`FAILED_OUTPUT_CONTRACT_NE_FAILED_MODEL`  
`LOCAL_EXECUTION_NE_PROVIDER_INDEPENDENCE_PROOF`  
`CHATGPT_ORCHESTRATED_LOCAL_CANARY_NE_CHATGPT_NOT_REQUIRED`  
`LOCAL_NE_INDEPENDENT_UNLESS_FAILURE_DOMAINS_PROVEN`  
`COMPILED_DEED_NE_ACCEPTED_WORKER`  
`ONE_RETRY_NE_RETRY_LOOP`  
`VALIDATION_IS_NOT_ACCEPTANCE`
