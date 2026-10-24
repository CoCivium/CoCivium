# CoDoodle+ / CoNex+ R0 reference generator

A dependency-free Node.js reference implementation for the candidate-generation side of the [CoDoodle+ / CoNex+ Experiment Launcher R0](../../docs/Architecture/CODOODLE_CONEX_EXPERIMENT_LAUNCHER_R0_20261024.md).

It deliberately **does not** launch experiments, spawn workers, call models, access providers, publish, or mutate external state.

## Run

```sh
node examples/codoodle-conex/smoke.mjs
```

The smoke test checks deterministic replay, seed variation, >=12 operators, candidate-only authority, dedupe, selector cap <=32, reserved null/inverse/challenge-style lanes, invalid limits, and a local generation timing receipt.

A timing result is a property of the named machine/runtime/workload only. It is not a universal throughput claim.

`CANDIDATE_NE_EXECUTED` · `MICROSECOND_TARGET_NE_MEASURED_THROUGHPUT` · `RANDOM_NE_AUTHORITY`
