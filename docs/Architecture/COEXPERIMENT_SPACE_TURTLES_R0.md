# CoExperimentSpace+ / CoTurtles+ Preview R0

**State:** `CANDIDATE_EXPERIMENT_SPACE_PREVIEW__ZERO_EXECUTION`

## Purpose

Represent a very large space of possible CoCivium experiments without confusing combinatorial possibility with useful, eligible, or executed work.

R0 combines the existing role/session/domain/epistemic registries with experiment axes for family, substrate, evidence mode, fault mode, evaluation focus, scale, concurrency, budget, review recursion, mutation, and historical replay.

The current exact raw Cartesian product is:

`422,730,484,678,656,000`

This is a count of syntactic candidate descriptors only. It is not a claim that the combinations are semantically distinct, useful, affordable, safe, independent, or runnable.

## Why trillions are cheap

The preview uses mixed-radix decoding and deterministic sampling. It never enumerates the full product. A bounded request can inspect at most 100 descriptors regardless of the total raw count.

`RAW_DESCRIPTOR_COUNT_NE_USEFUL_EXPERIMENT_COUNT`

`DESCRIPTOR_NE_EXPERIMENT`

## CoTurtles+ relation

Recursive review remains bounded by the already-published advisory-panel rule:

- runtime nesting depth at most 2;
- at most 2 review rounds;
- all children draw from one aggregate parent budget;
- nesting cannot replenish budget;
- nesting cannot raise authority;
- stop on acceptance, aggregate budget exhaustion, or a full round with no verified material improvement.

The experiment grammar may contain many possible turtle templates. Selecting a template does not materialize a panel.

`TURTLE_TEMPLATE_NE_LIVE_RECURSION`

## Promotion ladder

Candidate descriptors move through explicit gates:

`DESCRIPTOR -> STATIC_VALIDATION -> SHADOW -> MICRO_CANARY -> REPEATED_CANARY -> CROSS_SUBSTRATE_COMPARE -> INDEPENDENCE_AUDIT -> RECEIVER_VALUE_CHECK -> HIGH_BAR_CANDIDATE`

Nothing skips from a large combinatorial count to runtime merely because spare resources exist.

## High-bar gates

Promotion requires explicit evidence for:

- exact input bindings;
- pinned baseline;
- correctness non-regression;
- repeated measurements;
- tail latency and error reporting;
- resource/cost reporting;
- provenance and currentness;
- counterexample or challenge;
- recovery/rollback where applicable;
- independence status;
- receiver value;
- preserved dissent.

A newer or faster result can lose if it creates more proof debt, currentness debt, cost, fragility, or receiver burden.

## CoStretch+ relation

The correct optimization target is not maximum utilization. The useful frontier is where additional resource consumption still creates verified receiver value without unacceptable correctness, latency, proof, coordination, cost, or recovery debt.

Logical scale may grow to billions, trillions, or beyond while the active materialized frontier remains small.

## Example

```sh
python scripts/CoExperimentSpacePreviewR0.py --limit 12 --seed turtles
python scripts/CoExperimentSpacePreviewR0.py \
  --filter operational_role=CHALLENGER \
  --filter turtle_depth=DEPTH_2_MAX \
  --filter experiment_family=FAULT_INJECTION \
  --limit 5
```

R0 reads local public registries, emits JSON, and performs zero experiment execution or external mutation.

## Next

The next useful step is not to execute trillions of experiments. It is to add a deterministic descriptor scorer that prioritizes a tiny frontier by expected information gain, falsifiability, receiver value, novelty, cost, and dependency independence, then run one bounded micro-canary.
