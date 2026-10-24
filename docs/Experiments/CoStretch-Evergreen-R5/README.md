# CoStretch+ R5 | Evergreen benchmark ledger (public R&D candidate)

**Here now:** A compact, FOSS-oriented experiment ledger, deterministic validator, and virtual experiment sampler. This is **not** an always-on worker, a trillion executed experiments, an independently validated AI benchmark, Andrew receiver acceptance, a product release, or an automated newsletter blast.

This bounded package deliberately distinguishes **what ran**, **what was a synthetic thought experiment**, **what failed**, and **what remains untested**. The `benchmark_evo.jsonl` is public-safe and machine-readable. Original detailed X2 result bytes remain in local custody, not bundled here; its SHA-256 is included for exact-object verification.

## Reproduce locally

Requires Python 3.9+ standard library only, no credentials, network access, package installation, or permission to change any account.

```sh
python3 verify_benchmark_evo.py benchmark_evo.jsonl
python3 virtual_experiments.py --sample 20
```

The tests and full build inputs are retained in the companion R5 archive. Source versions are append-only in intent; do not silently rewrite an observed record. A corrected observation should create a new record with source reference and explicit predecessor.

## Real X2 controlled observation, 2026-10-23 UTC

`CoStretch_R1_Controls` recorded 24 algorithm timing trials on **one Windows workstation**, 3 repetitions per method at each of four duplicate fractions. All exact outputs agreed. `certutil` readback matched SHA-256 `422323ed093697ceb29e42028567234a66d160f6e51d7221cf0dae232c73b344` on the same host.

| Repeated requests | Uncached median | Memoized median | Uncached / memoized |
| --- | ---: | ---: | ---: |
| 0% | 59.091 ms | 85.409 ms | 0.692x (memoization lost) |
| 10% | 83.658 ms | 79.628 ms | 1.051x (marginal) |
| 75% | 67.782 ms | 18.660 ms | 3.632x |
| 93.33% | 50.808 ms | 6.669 ms | 7.619x |

These are bounded local timing observations, **not** CPU-energy measurements, production-traffic throughput, an independent receiver replication, or evidence of a universal speedup. Before promotion: randomized trial order, cold/warm cache controls, larger repetitions, real workloads, resource meter, independent verification, and rollback.

## Trillion turtles, without trillion invoices

The same X2 controls artifact describes `16^10 = 1,099,511,627,776` possible logical addresses and **1,024 rank-mapping roundtrips**. `virtual_experiments.py` samples at most 1,024 deterministic virtual addresses, materializes zero model jobs, and makes zero provider calls. For large-scale execution, use adaptive budgets, one baseline, distinct independent checks, hard privacy/consent gates, correlation discounts, and early stop at diminishing benefit.

## Requested external acceptance thresholds (pending)

The ledger records these as `NOT_RUN` until separately source-proven. A test target is **not** a measured outcome:

| Gate | Target | Evidence needed |
| --- | --- | --- |
| Media still / thumbnail | size >300 KB, thumbnail renders | exact file hash, size, image decode/readback |
| Video black frame | ffprobe metadata; `blackdetect` 0 | exact video input and ffmpeg output; not applicable to still images |
| GitHub | public exact-object URL returns HTTP 200 in <2 seconds | timestamp, target URL, client/region, repeated observations |
| Gmail | recipient's opted-in Primary within <60 seconds | send message ID and receiver-side classification/time, no mass mail |
| Identity | actor/authority and effect ID logged | scoped audit record, no secret export |
| Pi | packet compatibility in <2 seconds | receiver Mac version and test transcript |
| Claude | permitted credential-availability check in <1 second | only Boolean and duration, no key content read or logged |
| Llama / Ollama | public-safe packet parsed in <3 seconds | named existing model, localhost, cold and warm timings, correct schema |

A failed speed gate does not license bypassing privacy, source identity, consent, or authority limits.

## Andrew and alternative substrates

Pi, Claude, Ollama/Qwen, deterministic scripts and other FOSS/local models are *replaceable candidates*, not claimed equal or tested against each other here. Model listing on X2 was read-only; **no local model was inferred or scored**. A real Andrew test must preserve source hashes, unresolved objections, permissions, held actions, and an interruption recovery point across the switch.

## Historical redo without rewriting history

Select the highest-value older artifacts by likely capability sensitivity, recheck original bytes and dated evidence, re-evaluate on a current bounded fixture, and preserve an old-vs-new delta with counterexamples. Do not replay external effects, erase rejected alternatives, or call stale assumptions current.

## Open and respectful by design

FOSS-compatible, no coercion, privacy-by-design, opt-in contact, accessible display where needed, optional wearables, respectful disagreement, no undisclosed model-targeting traps, no fake million-account swarm, no pay-to-participate privilege, and no asset/holding claims. Criticism and regression cases welcome. `LoLs` may mean lots of layers, laughs, love, and learning; jokes are not test evidence.

**Lifecycle:** Working public candidate only. GitHub visibility is not receiver readproof, integration, canon, production runtime, CoEx, or broad public release. Local source proofs and future receiver ACKs are separate milestones.