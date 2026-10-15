# CoModel substrate-light portability canary R0

**State:** `BOUNDED_PARAMETERIZED_MODEL_PORTABILITY_CANARY__NO_LLM_NO_RUNTIME_NO_CANON`

## Purpose

Advance one rung beyond the synthetic lifecycle state machine without pretending we have migrated a real language model.

R0 stores one small **parameterized integer model** as a durable exact model pack, then independently reconstructs and executes it on three GitHub-hosted runner OS classes:

- Linux;
- Windows;
- macOS.

Each runner must independently produce the same:

- logical model identifier;
- model-pack SHA-256;
- parameter semantic SHA-256;
- inference semantic SHA-256;
- invariant SHA-256;
- five exact inference results.

A fourth fan-in job compares all receiver receipts.

## Why this is useful

This proves more than a hand-written lifecycle diagram:

```text
one durable model representation
-> independent materializations
-> different execution environments
-> same bounded model semantics
```

It still proves much less than LLM or neural-model migration.

The canary deliberately uses integer arithmetic so floating-point implementation differences cannot masquerade as substrate semantics.

## Model

The model is a two-class integer linear argmax model:

```text
logits = W*x + b
class  = argmax(logits)
```

This is an actual parameterized computation, but tiny enough to audit completely.

No external model is downloaded and no package beyond Python is required.

## Interpretation

A successful fan-in supports:

`BOUNDED_PARAMETERIZED_MODEL_CAN_BE_RECONSTRUCTED_WITH_IDENTICAL_SEMANTICS_ACROSS_THREE_RUNNER_OS_CLASSES`

It does not support:

- LLM migration;
- neural-weight portability in general;
- identical physical hardware;
- identical internal execution;
- persistent runtime integration;
- lossless reconstruction of arbitrary models;
- personhood or continuity-of-consciousness claims.

## Next after PASS

Only after this canary passes should the frontier move to an actual open neural model or local Ollama-backed model when an authorized execution route is available.

## Rails

`PARAMETERIZED_MODEL_NE_LARGE_LANGUAGE_MODEL`  
`RUNNER_OS_DIVERSITY_NE_HARDWARE_DIVERSITY`  
`PORTABLE_INFERENCE_NE_WEIGHT_MIGRATION_SOLVED`  
`SAME_OUTPUT_NE_SAME_INTERNAL_EXECUTION`  
`MODEL_PACK_HASH_NE_PERSONHOOD_OR_IDENTITY_TOTALITY`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`PORTABILITY_PASS_NE_COEX`
