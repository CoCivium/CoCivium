# CoMixFactorBench+ R0: constraint-first joins and source-delta recomputation

**State:** `LOCAL_SYNTHETIC_POLICY_BENCHMARK_ONLY__NOT_X2_RUNTIME__NOT_GLOBAL_SYNC`  
**Observed:** 2026-11-03  
**Host:** existing CoAllBloom / CoDoodle-CoNex candidate PR #303. No new scheduler, ontology, bus, or live model.

## Why

A combinatorial index is not useful work. The prior CoDoodle/CoNex R1 demonstrates a 2.25-trillion-address syntactic space, bounded sampling, deterministic scores and no worker launch. CoAllBloom first proof demonstrates typed alternative generation and one elected shadow task. Neither establishes useful end-to-end combination throughput, incremental change cost or global cross-receiver synchronization.

This successor asks a narrower, falsifiable question: **can we retain the exact same qualified synthetic publication/inquiry projections while reducing wasted Cartesian work and reusing unchanged source partitions?**

## Method

All three strategies use exactly the same fixed public synthetic fixture: 8 *explicitly declared* reader interests/media capabilities, 5 interpretation lenses, 6 evidence classes, 4 media types, 3 time classes, 3 privacy classes, 3 action classes, and variable source count. The product is a *logical address space*; most descriptors are disallowed.

1. **Exhaustive Cartesian:** construct and qualify each possible tuple.
2. **Constraint-first:** push receiver selection, epistemic, modality, privacy and authority filters before the join.
3. **Incremental source-index update:** on one version change, replace only the changed source's partition using copy-on-write. This measures index maintenance, **not** flattening/serializing/fanout to every receiver.

The first two produce a byte-identical SHA-256 digest over the **same sorted output tuples** at each size, not merely equal counts. The updated indexed result is independently flattened after timing and compared to a complete source rebuild. The tested privacy/authority model emits only `PUBLIC` synthetic projection candidates; `PUBLISH` is never admitted. `CHALLENGE` means unsent local proposal, not outreach.

| Source count | Raw syntactic tuples | Qualified tuples | Exhaustive median | Constraint-first median | Full equivalent-join speedup |
|---:|---:|---:|---:|---:|---:|
| 4 | 103,680 | 2,048 | 14.0649 ms | 0.1699 ms | 82.78x |
| 16 | 414,720 | 8,192 | 49.1314 ms | 1.6324 ms | 30.10x |
| 48 | 1,244,160 | 24,576 | 141.3299 ms | 3.5751 ms | 39.53x |

At 48 sources, full factorized rebuild after one source version change took 3.3149 ms median; copy-on-write **index maintenance only** took 0.0396 ms median (83.71x). This is an *interface-cost comparison*: consumers that require an all-results flat list still incur flattening and possible transmission costs. Nothing is cached across independent machines, nothing uses a live database or queue, and no model/reader is invoked. Timing is 5 repetitions per strategy on one shared container; OS scheduling, allocation and CPU cache cause variation. Re-run on the intended host before tuning anything.

## Reproduce

From this directory, using Python 3.10+ standard library:

```sh
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 CoMixFactorBenchR0.py --repeat 5
```

`--output <new-file.json>` is exclusive create and exact byte-readback. Never overwrite a prior measurement; compare source/hash/machine/environment and retain failed controls. The checked-in `benchmark_r0.json` records the original measured environment and raw medians/p95 values. The detector does not install a service or schedule a future job.

## What remains to prove

- **Correctness of the policy itself:** these are illustrative categories, not universal truth or a validated theology/science taxonomy.
- **Real joins:** actual CoPulse/CoQuanta work objects with source IDs, revocation, permissions, version and time metadata; real late or reordered deltas; no cross-ring leakage.
- **Better methods:** compare against indexed database joins, query planning, semi-joins, compiled/columnar selection, materialized views, dependency invalidation and workload-specific adaptive plans. Do not assume Python loops are the real bottleneck.
- **End-to-end UX:** first-use comprehension, independent challenger output, source provenance, receiver readproof, change-to-useful-output p50/p95/p99, CPU/energy, focus theft, number of user relays and false greens.
- **Distributed currentness:** CoPulse R0 explicitly reports `NO_LIVE_GLOBAL_BUS`. Async pending, scoped sync, offline/partitioned, conflict and replay states must be proven per receiver. A faster local join does not update idle provider models or establish global sync.

One next bounded proof belongs in **existing CoPulse/CoRelationalAutocycle**: source-version change -> privacy/authority-filtered incremental projection -> two independent receiver subscriptions -> exact readproof or scoped ASYNC_PENDING -> backfill -> challenge, without Rick ferrying the update. Preserve one elected actuator for any side effect; no auto-publishing or faith-based targeting.

**Donors:**
- `examples/codoodle_conex_r1/CoDoodleNexR1.py` (main-branch Git blob `ab3edf053b7027a6d124830c3d96bbdd675b4963`)
- `examples/codoodle_conex_r1/coallbloom_r0/bloom.py` (PR #303 source Git blob `4bdb6a3e2ded2f9c48f411a6050c93e7fa2c5dc7`)
- `docs/Architecture/COZILLION_GENERATIVE_RELATION_GRAMMAR_R0_20261026.md` (main Git blob `2b6734e52459b7e76db1c8bf5d871f4af3083932`)
- `docs/Architecture/COALL_PULSEFIELD_COTIME_R0.md` (main Git blob `af881fd2eebdd249c16c279a46003bd3836b96cf`)

**Rails:** `COMBINATIONS_NE_USEFUL_COMPLETIONS` · `SPEEDUP_NE_PRODUCT_BENEFIT` · `INDEX_UPDATE_NE_GLOBAL_SYNC` · `SYNC_FOR_SCOPE_NE_ALL_CONTENT_SYNC` · `READER_CHOICE_NE_SENSITIVE_PROFILING` · `PREDICTED_NE_OBSERVED` · `UNKNOWN_NE_ABSENT` · `FAITH_NE_EMPIRICAL_PROOF` · `NO_SEND_WITHOUT_AUTHORITY` · `LOCAL_TEST_NE_X2_RUNTIME` · `GITHUB_SOURCE_NE_RECEIVER_ACK` · `RICK_NE_HEARTBEAT`.