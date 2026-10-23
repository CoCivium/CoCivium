# CoStretch+ / CoTurtle+ reproducible experiment R1

**State:** bounded offline experiment; not a distributed deployment, certification, CoAll canon, or sustained-capacity proof.

This is a small **FOSS** Python 3 standard-library fixture to test three questions:

1. Can an enormous *logical* candidate space be addressed without creating enormous numbers of processes?
2. Do bounded parallel work queues preserve exact outputs and fail closed when a worker fails?
3. Can a long provenance chain be checkpointed, resumed, and tampering detected?

**Included files:** `costretch_r1.py`, `tests/test_costretch.py`, `output/benchmark_evo.jsonl` (one witnessed run), `manifest.json`, and a public-safe design note under `docs/`.

## Reproduce

```sh
python3 -m unittest discover -v -s tests
python3 costretch_r1.py --output output/my_unique_new_run.jsonl
```

The output path must not already exist. No credentials, external data, network access, model calls, device access, or persistent services are required. The test's maximum actual thread count is **four**.

## Reading `benchmark_evo.jsonl`

Each line records `schema`, `test`, `status`, `proof_class`, `observed`, `expected`, `boundary`, and `run_utc`.

- `PASS` with `ISOLATED_WORKBENCH_TEST` means only the stated bounded check passed.
- `FAIL` with `UNSUPPORTED_GENERALIZATION`, `UNPROVEN_CLAIM_GATE`, or `NOT_MEASURED` means the broader claimed result is **not supported**. It is intentionally preserved as a negative outcome, not counted as a failed unit test.
- A passing simulation or isolated benchmark does **not** prove sustainable capacity, energy savings, real provider independence, cross-device deployment, or a trillion simultaneous workers.

The logical grid has **12 axes x 10 candidate options = 10^12 addressable configurations**. Only 1,030 indices are sampled. This test does not enumerate all configurations and does not instantiate a trillion workers.

## Next tests

Run R2 representative CoWork queue workloads, R3 actual process-loss recovery on a permitted local sandbox, R4 independently evidenced provider-neutral receiver rebind, and R5 measured energy/latency/Pareto frontiers. Separate consent and safety gates apply to hardware, accounts, bystanders, and external effects.

**Licensing:** This file set is intended for contribution under the parent `CoCivium/CoCivium` repository's GNU GPL version 3 license. No third-party models or private corpora are bundled.
