# CoFlowBaseline R0 | Record vs. repeatable baseline

**Scope:** A small, provider-free, privacy-neutral illustration of the existing CoStretch benchmark contract. There are **zero real X2 measurements**, **zero live model calls**, and **zero third-party receiver observations**. `X2-SYNTHETIC` is an illustrative device-class label only.

## Reproduce

Python 3.9+ standard library only:

```sh
python3 -m unittest discover -s tests -v
python3 coflow_baseline.py
```

This writes `summary.json`, `benchmark_evo.jsonl`, and `HEAD.sha256`. Repeated runs generate the same bytes. The record ledger is integrity-linked but is **not a signature or independent truth proof**.

## Rule

First match exact workload, dataset, device class, and quality contract. Then count only runs with both quality/currentness gates and a declared synthetic receiver ACK. Classify:

- **Historical record**: fastest qualified individual trial in that matched context.
- **Observed repeat-min**: lowest accepted-outcome rate from at least three qualified runs of one candidate. It is a conservative *sample statistic*, not a verified service-level floor or a statistical confidence bound.
- **Throughput-only gate**: another candidate's repeat-min may be higher, lower, or held relative to the baseline. This comparison cannot establish superiority in cost, energy, error risk, human attention, or long-horizon stability.
- **Held/negative observations**: preserve the biggest burst even if it is not repeatable, preserve a missing receiver or bad quality result without crediting its output, and separate runs conducted on different devices.

### Synthetic outcome

For the fixture's X2-labeled context, the historical single-trial peak is **10 accepted outcomes/second** but the three-run baseline's repeat-min is **2/second**. The three-run candidate repeat-min is **3/second**. A 200/second run on a different synthetic device is **not compared**. An unacknowledged apparent 500/second run is **not qualified**.

None of these represent actual CoCivium, X2, Claude, Pi, Llama, other devices, or real user productivity.

## Fit into existing CoCivium, not another control plane

The upstream source for this experiment is:

- [CoStretch Benchmark Plan R0](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COSTRETCH_BENCHMARK_PLAN_R0.md): repeated comparison, quality, p95/p99, cost/energy, Pareto-like champions, stop conditions.
- [CoResourceAttractor R0](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/CORESOURCE_ATTRACTOR_R0.md): source inventory, provenance, currentness, rights/consent, alternatives, negative and missing resources.
- [CoFlow Delta Unblocking R0](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COFLOW_DELTA_UNBLOCKING_R0_20261026.md): publication versus receiver return, fan-out/fan-in, closure, user relay, recovered work.
- [CoFleetProjection R4A](https://github.com/CoCivium/CoCivium/blob/main/docs/UX/COFLEET_PROJECTION_COMPILER_R4A.md): bounded device/surface view, with coverage and UNKNOWN instead of invented global counts.

Recommended real-world path: independently label one consented end-to-end task class, pin dataset/quality/environment, measure verified receiver outcomes over repeated runs, measure p95/p99 and time/cost/energy where instrumented, compare against a competent baseline, and stop rather than expand when human attention, error rate, stale results or coordination debt exceed value.

## Inventory and I/O contract proposal

Represent each accessible resource with `id, source, provenance, currentness, capabilities, environment, authority, privacy_class, cost, failure_domain, alternatives, proof_status, owner/receiver, exit_path`. For anything not actually inspected, use `REFERENCED_NOT_VISIBLE`, `AVAILABLE_UNVERIFIED`, `BLOCKED`, `INTENTIONALLY_ABSENT`, or `UNKNOWN`, never synthetic access.

For each I/O stage, measure `enqueued -> admitted -> processed -> correct -> receipted -> recipient accepted -> receiver benefited`, including retries, duplicates, timeouts, lost context and deferred work. Counts at earlier stages must never silently become counts at later stages. Measure queue age, actual device/receiver health and recovery per stage. **Do not** scan private devices, read clipboard contents, capture screenshots, inspect contact lists or track people without scoped consent.

The resource inventory should be *federated and selectively queried*, not indiscriminately copied. A performance high-watermark is a requalification target, not a guarantee, entitlement or permission to run more jobs.

`HIGHEST_SEEN_NE_SUSTAINABLE | BEST_SPEED_NE_BEST_OUTCOME | PRODUCED_NE_DELIVERED | INVENTORIED_NE_AUTHORIZED | SOURCE_NE_RECEIVER`
