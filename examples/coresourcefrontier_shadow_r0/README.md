# CoResourceFrontier+ R0A | Regenerative mesh shadow canary

**Status:** `CANDIDATE_SHADOW_TEST__NO_RUNTIME__NO_OS_ACTION__NO_NETWORK__NO_SEND__NO_PHYSICAL_ENERGY_HARVEST`

This fulfills one bounded part of the existing [CoResourceFrontier+ next-test contract](../../docs/Architecture/CORESOURCE_FRONTIER_ALLOCATOR_R0.md). It is **not** a new resource allocator or global scheduler. It complements [CoOmni resource pooling](../../docs/Architecture/COOMNI_CONTEXT_RESOURCE_FABRIC_R0_20261024.md), [CoMetaTrainable+](https://github.com/CoCivium/CoSteward/blob/main/docs/session_backchannel/evolution/CoMetaTrainable_CoObject_Relations_20261017_R0.json), [CoSubscriptionEcology+](../../docs/Architecture/COSUBSCRIPTION_ECOLOGY_R0.md), [CoAllPulseField+](../../docs/Architecture/COALL_PULSEFIELD_COTIME_R0.md) and the [CoAllBloom/CoOrbWare review candidate](../../docs/Architecture/COALLBLOOM_SUBSTRATE_OS_SUPERFRAME_R0_20261026.md).

## Core idea

A CoObject, CoTerm, relation, source, candidate model or other *typed* entity MAY carry a dormant improvement opportunity, a receiver, a source/version identity and a bounded wake predicate. It need not run a process, hold a lease or emit updates while idle. Actual physical energy is not obtained from symbols, unknowns or mere naming.

```
source object or relation + exact scoped ref + wake condition
 -> typed candidate questions (include inverse / null / contrary / else)
 -> identity + provenance + permission + receiver + privacy + currentness check
 -> deduplicate only exact same source/version/receiver/scope work
 -> resource-eligible finite selector with reserve floors
 -> one read-only shadow plan, never an effect
 -> compact recipient-specific view / passive publication pointer
 -> independent receiver proof (later) / return signal
 -> requalify, archive, sleep, or retire
```

### Fractal sharing without a broadcast storm

The same record shape MAY be projected at an object, task, device, LAN, cluster, organization or global level. But that does not imply identical permission at each level. Local resources retain their reserve; eligible objects publish only *references* or compact deltas to explicitly interested receivers, limited by confidentiality, authority, TTL/wake and fanout. A legitimate **no** is a resource-preserving outcome. Evidence and rights do not widen through relaying.

### Resource vectors: do not sum incompatible units

This canary tracks `cpu_units`, `energy_estimate_units`, and `attention_units` **separately**. All three are invented fixture units, **not measured CPU time, joules or minutes**. The synthetic receiver-value proxy is declared within one scenario and is not a universal conversion from consent, trust, monetary value, spiritual meaning or energy. Never optimize everybody using one cross-domain scalar.

An eligible source of real harvested physical energy requires a separately validated instrumented physical experiment, measurement uncertainty, conversion losses, safety/rights and accounting. This R0 categorically holds every `PHYSICAL_ENERGY_HARVEST` task, even if its claimed proxy is enormous.

### Faults and recovery

An unavailable resource is not chosen. The same source/version scoped reference can move from one fictional resource candidate to another without changing its source identity. That is **shadow failover planning**, not actual fault repair, restart, resource rebalancing or OS recovery. Real self-repair requires a bounded lease, verified checkpoint, health observation, independent readback, safe rollback and receiver acceptance.

## Reproduce offline

From this directory with Python 3.9+ (stdlib only):

```
python -m unittest -v test_shadow_allocator
python shadow_allocator.py > regenerated_comparison.json
```

`fixture.json` has **17 purely synthetic tasks** and three fictitious nodes. The script compares exactly six policies in one bounded scenario: `first_n`, seeded `random`, `keyword`, `evidence`, `novelty`, and `challenge`. It never sends mail, opens sockets, runs a worker, reads X1/X2, acquires real leases, or starts a persistent loop. The `route_event` function returns opt-in receiver IDs **in memory only**, with an explicit fanout cap. The regeneration script `make_fixture.py` documents how the synthetic inputs were made; the exact fixture committed in this directory remains the test input.

The demo's `max_wave=3` and resource reserve floors prevent mass activation. The allocator's list is sorted deterministically. Duplicates are suppressed only when source hash, version, scope, privacy and recipient are identical; distinct evidence is kept even if it addresses the same question.

## Test report: synthetic only

- Local run: **35/35 Python unittest checks passed**.
- Six policy comparisons complete and deterministic.
- The measured objects are code execution/test outputs, not proof of CoCivium's benefit to external readers.

| Policy | Chosen tasks | Projected value units | CPU units | Energy estimate units | Attention units |
| --- | --- | ---: | ---: | ---: | ---: |
| first_n | 3 | 25 | 9 | 9 | 2 |
| random (seed 17) | 3 | 27 | 9 | 9 | 2 |
| keyword | 3 | 24 | 8 | 8 | 1 |
| evidence | 3 | 26 | 7 | 7 | 1 |
| novelty | 3 | 18 | 7 | 7 | 1 |
| challenge | 3 | 18 | 7 | 7 | 1 |

Within *this* synthetic receiver-value/cost space, `random` and `evidence` form a two-choice Pareto frontier. This **does not establish** that random allocation outperforms any policy in a real service. Neither forecasted receiver value nor estimated energy units are real-world measurements. Each policy is a prospective strategy to challenge, not settled truth. Future experiments must include independent reader outcomes, unbiased baselines, realistic workloads, fairness, errors, source quality, net compute cost, recovery burden and tail latency.

### Critical holds exercised

- Unconsented high-priority tasks: **HELD**.
- External email task: **HELD**.
- Claim of physical energy from an unverified source: **HELD**.
- Unknown recipient / private material: **HELD**.
- Missing exact source / stale data / unwoken task: **HELD or DORMANT**.
- Offline source / invalid resource reserve: **not selected**.
- Excessive cost: **HELD**.
- Exact duplicate: **one proposed slot**.
- Refusal/no group consent: **no route**.
- Loss of preferred fictional resource: **candidate fallback retains scoped source identity**.

## What this cannot claim

No installed X1/X2 or CoStead agent; no legitimate live global bus, energy-harvesting machinery, living custom model, recipient ACK, global optimum, perpetual motion, always-running background worker, contact-list broadcast, or independent restoration. `test_result.txt` and `comparison_receipt.json` are sample **local synthetic test receipts**, not certification of deployment or future correctness. When provider sessions are overloaded, the desired outcome may simply be *fewer active processes*.

**Next safe independent proof:** replay one rights-cleared object and two qualified resource offers on an independently authorized receiver; compare selected/held plans with actual source readback, reserve, no-duplicate, rollback and recovered state. X2 can be used later **only** after its remote route and foreground latency are measured. Until then, this works on any ordinary Python-capable machine and requires no X1 or X2 intervention.

`ADDRESSABLE_NE_ACTIVE` | `RESOURCE_ESTIMATE_NE_PHYSICAL_ENERGY` | `SHADOW_PLAN_NE_LEASE` | `SAME_GLU_REF_NE_SHARED_AUTHORITY` | `CONSENT_NE_TRANSPORT_PERMISSION` | `FANOUT_NE_BROADCAST` | `FAILOVER_PLAN_NE_RECOVERY_PROOF` | `UNKNOWN_NE_FREE_ENERGY` | `SYMBOLIC_NE_PHYSICAL` | `SIMULATED_WIN_NE_REAL_BENEFIT`.
