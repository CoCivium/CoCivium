# CoRel+ / CoBraid+ | Causal Frontier R0

**State:** PUBLIC_SAFE_SOURCE_CANDIDATE__NO_LIVE_WORKERS__NO_DEPLOYMENT__NO_RECEIVER_ACK  
**Date:** 2026-11-10. **Parent:** CoPreGeneric `CoPre.md`; [CoWaitlessExecution](../../docs/Architecture/COWAITLESS_EXECUTION_R0.md); [CoLogicalSpawnPlanner R2](../../docs/Operations/COLOGICAL_SPAWN_PLANNER_R2.md). This is a deterministic planning **overlay**, not another scheduling service.

## Why this small test exists

The user asks that existing fully reasoned causal chains (CoRel/CoBraid) become operationally reusable, with sequential dependencies and parallel independent progress, rather than endless CoPre repasting. Existing planner R2 validates and deduplicates logical contracts but does not elect a dependency-ready DAG frontier. Existing due-work catch-up tests have no durable real work receiver. This candidate fills only the *causal selection* gap. All consequential effects remain held.

`ONE_SOURCE -> TYPED_DEPENDENCIES -> QUALIFIED_PARALLEL_READ_ONLY_PROPOSALS -> ONE_ELECTED_ACTUATOR_PER_COLLISION_DOMAIN (future; not here) -> RECEIVER_READPROOF`

## Evidence-limited example

Synthetic seven-node WorkID:
- `seed` has a **declared** completion receipt, explicitly **not independently verified**.
- `source_check`, `challenge`, `media` are disjoint read-only candidates and may be proposed in a three-wide logical parallel frontier.
- `outreach` depends on incomplete source-check and is `EFFECT_GATED`.
- `receiver_result` depends on outreach and remains deferred.
- `other` shares a collision domain with source-check, so is not elected concurrently.

The 23 adversarial tests cover source/ID validation, deterministic reordering, cycles, missing/self dependencies, event/receipt contradictions, collision caps, logical budgets, held edges, effect gates, and explicit zero external effects.

**CH03 | False causal completion:** A task labelled `DECLARED_DONE` must not depend on a task still labelled `CANDIDATE` or `HELD`. The planner now rejects such input as `DECLARED_DONE_WITH_INCOMPLETE_PREREQUISITE`, rather than letting an impossible completion order open downstream proposals. Even when a declared parent is also labelled done, the receipt remains **unverified** until independent receiver proof; the planner still grants no effect authority. This is a syntactic consistency guard, not proof that the underlying causal relationship is true.

Run **locally with Python standard library** (review source first):

```sh
python -B -m unittest discover -s tests -p 'test_corel_braid_frontier_r0.py' -v
```

The existing [CoWaitless Shadow Canary](../../.github/workflows/cowaitless-shadow-canary.yml) runs this test in its existing CI workflow. No new cron, bot, provider session, live process or authority.

## What this does not prove

- The displayed DAG is a **declared** dependency order, not demonstrated scientific causal validity.
- A source hash supplied in JSON is a **claim**, not independent source readback.
- A `DECLARED_DONE` receipt is unverified until receiver-origin proof exists.
- The plan does not start workers or know which model, device or user can carry an election.
- Two logical candidates do not constitute two actually independent physical or provider failure domains.
- A green CI test does not grant public outreach, credential use, spending or real-world effect authority.
- There is no CoStead/X2 integration, true no-Rick-relay handoff, >24-hour survival, CoEx or canon promotion.

## Next qualification

Have the **existing** logical spawn and CoMVP/CoPre pilot owners test a single real, public-safe WorkID graph with exact current source readback, explicit authority, a durable receiver, no duplicate effects, and independent first-use. Then compare sequential-first-N vs dependency-aware shadow selection by actual useful outcomes and human attention saved. If the extension adds no measurable value, retire it.

`NO_SAFE_WORK_WAITS_FOR_AN_UNRELATED_GATE` · `LOGICAL_PARALLELISM_NE_EXECUTED_PARALLELISM` · `CLAIMED_RECEIPT_NE_RECEIVER_ACK` · `BRANCH_NE_CANON`
