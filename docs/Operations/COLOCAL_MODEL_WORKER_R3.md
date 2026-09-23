# CoLocalModelWorker R3

**State:** `ADAPTER_READY__OLLAMA_CANARY_NOT_YET_RUN_ON_X2`

This is the first deliberately narrow local-model materialization adapter beneath CoSpawnEcology+.

It accepts exactly one public-safe, unblocked, `LOGICAL_ONLY` CoSpawn contract and may call an already-running Ollama-compatible endpoint on **loopback only**.

## Allowed R3 effect classes

- `OBSERVE`
- `PROPOSE`
- `REVIEW_CHALLENGE`

The worker emits candidate JSON only.

It cannot mutate repositories, create provider sessions, perform public outreach, change credentials, or grant authority.

## Network boundary

R3 accepts only:

- `127.0.0.0/8`
- `::1`
- `localhost`

It does not install or pull a model. The named model must already exist in the local runtime.

## Confidentiality boundary

R3 is deliberately **PUBLIC-only**.

Private/restricted/unknown contracts fail closed. Later private local-model materialization requires separate proof of local model/runtime custody, logging behavior, storage paths, and receiver policy.

## Self-test

`--selftest` proves the static gates without requiring Ollama:

- public logical contract accepted;
- private contract rejected;
- already-materialized contract rejected;
- non-loopback endpoint rejected.

This repository version was syntax-compiled and its self-test passed before landing, but that is not an X2 runtime/Ollama canary.

## Next

When the X2 direct machine route returns:

1. identify an already-installed local model;
2. run `--selftest`;
3. materialize **one** public-safe low-effect contract;
4. exact-hash the output;
5. require receiver readproof;
6. compare with an independent verifier before any integration.

`LOCAL_NE_TRUSTED`  
`MODEL_OUTPUT_NE_TRUTH`  
`MODEL_OUTPUT_NE_EFFECT_PERMISSION`  
`CANDIDATE_OUTPUT_NE_PICKUP`
