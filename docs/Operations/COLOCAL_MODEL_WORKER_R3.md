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

## 2026-11-13 | X2 live endpoint readiness probe

**New read-only native evidence:** X2's authorized remote bridge was online. Shell-free file metadata found an existing Ollama executable and model manifest directories. A shell-free HTTP GET to the documented loopback endpoint (`http://127.0.0.1:11434/api/tags`) returned **`ECONNREFUSED`**. No `ollama` process was present in the contemporaneous bounded process inventory. No process was started, no scheduled task toggled, and no Desktop Commander terminal session opened.

**State:** `OLLAMA_INSTALLED_AND_MANIFESTS_PRESENT__LOOPBACK_SERVER_UNAVAILABLE_AT_OBSERVATION`; R3's actual X2 model canary remains **NOT RUN**. This direct probe narrows the blocker but does not prove an installation problem, a specific root cause, the absence of other endpoints, or an acceptable UI.

[Public-safe typed observation bundled with a separate CoFront receiver proof](../../ai/currentness/cotalkitout-cofront-byte-receiver-r0-20261113.json). The next safe action is an authorized, **non-foreground** service recovery using an existing elected owner and rollback path, followed by a single public-only R3 WorkID canary. No additional PS7 popup-producing runner should be introduced while the [CoDesktop focus incident #181](https://github.com/CoCivium/CoCivium/issues/181) remains unresolved.
