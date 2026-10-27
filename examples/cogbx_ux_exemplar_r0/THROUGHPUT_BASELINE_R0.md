# CoGbx / CoSpeedo+ Throughput Evidence and Resource Frontier R0

**Status:** PROPOSED_MEASUREMENT_CONTRACT__NOT_LIVE_FLEET_METRICS__NOT_X2_BENCHMARK  
**Observed:** October 27, 2026

## Answer to the question

**The best qualified historical measurement is an immutable high-watermark; it is not automatically the sustainable operating baseline.** A qualifying record must preserve workload identity, input/output correctness, receiver result, hardware/software/configuration, time window, concurrency, reliability, p95/p99 latency, resource/energy cost when measured, failure domains, source and exact receipt. A current baseline should represent repeatedly sustainable behavior under comparable conditions, not the fastest single burst.

Do not equate:
- peak tokens/second with correct useful results/second;
- more source or device references with available independent capacity;
- a green UI with measured health or recovery;
- an offline no-network browser interaction test with a production workload;
- logical agents with runnable workers, or potential capabilities with licensed authority.

### Qualification classes

| Class | Meaning | May drive capacity planning? |
| --- | --- | --- |
| DISCOVERED | A possible resource, device, connector, document, model or I/O surface was observed or referred to | No |
| SOURCE_PINNED | Source identity, rights, scope and provenance have been retained | Not yet |
| REACHABLE | A suitable authorized runtime or endpoint responds at a measured time | Only as availability, not processing capacity |
| BENCHMARKED | Representative controlled workload meets correctness and repeatability thresholds | Yes, for the exact workload and conditions |
| SUSTAINABLE | Repeated samples satisfy tail-latency, error, resource, cost and recovery limits | Yes, within tested envelope |
| ADOPTED | Independent receiver actually uses the output and can recover it | Yes, for verified usefulness and relevant context |
| STALE / HELD / REVOKED | Data aged out, authority missing or receiver declined | Do not infer current availability |

Every class is scoped by device/receiver/workload/time/privacy. UNKNOWN does not become zero or PASS. Qualification can expire. Do not aggregate across mutually dependent providers as if they were separate failure domains.

### Four distinct performance measures

1. **Historical peak record** `H(workload,environment,scope)`: maximum observed verified rate among immutable qualified receipts, with the measurement window. Useful for exploring future ceilings; never a guarantee of repeatability.
2. **Sustainable operating baseline** `B(workload,environment,scope)`: conservative rate from repeated representative runs under declared correctness, p95/p99 latency, resource cost, privacy, recovery and thermal constraints. This can decrease on evidence of degradation; it is not a promise of monotonically increasing output.
3. **Useful outcome efficiency** `U`: independently receiver-accepted useful results per elapsed time, human effort and appropriately measured resource cost. Keep value, speed, dollars, energy, accessibility and maintenance as a vector, not one magic number.
4. **Qualified capacity frontier** `F`: current source-verified, permissioned, reachable, independent surplus after reserved recovery and fairness headroom, plus explicit blocked/unknown candidates. An I/O port or public page is not automatically a capacity source.

### A bounded, falsifiable promotion rule

For each proposed faster design:
1. Pin a comparable **workload and input dataset**, version, authorization, environmental conditions and resource budget.
2. Run the same correctness/evidence tests and record independent output/receiver relevance.
3. Repeat across samples. Record median and p95/p99 latency, error rate, worst-case recovery and measured actual elapsed time, not synthetic speedups.
4. Check thermal, memory, bandwidth, energy, cost, coordination and human handling. Do not promote if any hard bound regresses.
5. Require a material useful improvement on the chosen Pareto frontier and enough reproducibility for the new **qualified champion**. Preserve the old peak and any failure.
6. Use capacity adaptively: backpressure, fair share, stop/sleep, substitution and a deliberate recovery reserve. High utilization alone is not success.
7. Archive `PASS | FAIL | HELD`, source identities and exact comparison receipt; wake only on an actual material delta.

**No property of this policy launches scheduled tasks or probes unknown devices.** It is a measurement contract, not a runner.

### Every I/O surface can be *considered*, not harvested

Potential contributors include: keyboard, pointer, accessibility device, camera, microphone, optical instrument, network interface, mobile/desktop UI, browser, local file, GitHub, public website, storage, models, agents, sensors, research/media reference, and human/organizational receiver.

Each is first a **candidate source, sink, observer, transformation, evidence, carrier, bottleneck, maintenance obligation or failure domain**, possibly several. To qualify for automated ingestion or actuation requires explicit scope, consent/rights, provenance, purpose, privacy and capture minimization, anti-duplication, freshness, reliability and an effect-specific authority check. Personal device input, surveillance, messages, research media and public feeds do not become pooled assets merely because reachable.

### Non-crown inventory federation

Use typed **descriptors and content/source hashes** to represent a potentially enormous addressable inventory. Resource catalogs need not broadcast private data, duplicate payloads or centralize credentials. Work objects and their receipts must survive a disconnected node, wrong/stale report or supplier exit. Count *independent failure domains* only after testing them.

Separate:
- `GLOBAL_DISCOVERABLE_CANDIDATE` from `LOCAL_QUALIFIED_AND_PERMITTED`.
- `CANDIDATE_THROUGHPUT` from `CURRENT_BENCHMARKED`.
- `RUNTIME_WORKERS` from `LOGICAL_SESSIONS`.
- `DEVICE_DISPLAYED` from `DEVICE_REACHABLE`.
- `APPROXIMATE_RESOURCE_ID` from `EXACT_RECEIVER_READPROOF`.

### What X2 and CoGbx should show

The existing CoGbx exemplar now presents four explicit **NOT MEASURED / UNQUALIFIED** counters, rather than inventing a global throughput graph. A future authorized current X2 adapter may show a compact ribbon:

`NOW [verified useful outcomes] | PEAK [context and source] | SUSTAIN [sample window] | P95 [measured] | RECOVERY [actual] | RESOURCE HEADROOM [qualified] | HUMAN RELAY [measured]`

Every number must drill down to a pinned, current receipt. Unknown or old information stays UNKNOWN/STALE; colors alone are not evidence. CoBar/CoOrb for X2 should start as a calm optional surface. A phone can show only NOW, UNKNOWN, NEXT and RECOVER; a text/headless client must be able to reconstruct the same values.

The current Desktop Commander integration reported X2 **offline** during this turn. That is an observer path status, not proof that X2 itself is powered off. Do not show a live X2 throughput until an authorized local process supplies actual measurements.

### Concrete regressions to test later

1. A one-second peak that causes minutes of cleanup must not replace a sustainable baseline.
2. A twice-as-fast but incorrect result must lose on the qualified frontier.
3. A group of identical cloud endpoints is not three independent failover families.
4. A disconnected X2 changes currentness to UNKNOWN, not zero and not green.
5. A pre-existing screenshot or GitHub test PASS does not count as current device adoption.
6. A resource added by an unauthorized connector cannot become pool capacity.
7. A zero-receiver-acceptance result is not a proven useful outcome, regardless of tokens/sec.
8. A faster runner must preserve p95/p99 and recovery ceilings.
9. A private I/O or sensor source must not be copied to a public inventory.
10. A stale high-watermark remains part of historical lineage but cannot be treated as current.
11. Independent tests must establish failure-domain diversity for the federation.
12. Dormancy or retirement can improve efficiency; growth is not necessarily more active processes.

## Source relations

- [CoStretch Benchmark Plan](../../docs/Architecture/COSTRETCH_BENCHMARK_PLAN_R0.md): Pareto-like champion, not fastest-wins.
- [CoFleet Human-Time Acceleration](../../docs/Operations/COFLEET_HUMAN_TIME_ACCELERATION_R0_20261024.md): minimize calendar time to a trustworthy device presence.
- [CoFractal Energetic Metabolism](../../docs/Architecture/COFRACTAL_ENERGETIC_METABOLISM_SUPERFRAME_R0_20261027.md): energy/cost/maintenance and gap resources.
- [CoVirtualSession Morphology](../../docs/Architecture/COVIRTUAL_SESSION_MORPHOLOGY_R0.md): logical identities differ from active workers.
- [CoGbx universal UX exemplar](../../docs/Architecture/COGBX_UNIVERSAL_UX_EXEMPLAR_R0_20261027.md): X2-first, device-neutral, proof-safe and non-capturable.

**R0 state:** source policy and prototype labels only, no current throughput telemetry, infinite computation, automatic resource harvest or live provider/device federation.

`PEAK_NE_BASELINE | PEAK_NE_SUSTAINED | RESOURCE_DISCOVERY_NE_PERMISSION | ADDRESSABLE_NE_ACTIVE | SUSTAINABLE_NE_MAX_UTILIZATION | GLOBAL_CANDIDATES_NE_GLOBAL_CAPACITY | RECEIPT_COUNT_NE_USEFUL_OUTPUT | REGRESSION_NE_ERASED_HISTORY`.
