# CoAll Resource-Field Compaction R0

**State:** `SYNTHETIC_OPTION_SPACE_COMPACTION__NO_REAL_RESOURCE_USE_NO_RUNTIME_AUTHORITY`

## Lead

A larger opt-in resource field is useful only if CoAll can avoid drowning in its own possible combinations.

As valid grants accumulate, the number of candidate compositions can grow much faster than raw resource count. R0 adds a bounded `CoResourceFieldCompaction+` layer:

```text
raw grants
-> active/current authority filter
-> narrow substitutability groups
-> dominance pruning
-> diversity-preserving frontier
-> composition search
```

The objective is not to erase resources. It is to keep obviously inferior same-scope alternatives out of the hot search frontier while preserving provenance and independent routes.

## Safe dominance

A candidate resource may dominate another only when both belong to the same explicit substitutability group and match on:

- resource class;
- purpose;
- privacy scope;
- owner;
- failure domain.

Within that narrow cell, A may prune B from active search when:

- capacity(A) >= capacity(B);
- reliability(A) >= reliability(B);
- cost(A) <= cost(B);
- at least one relation is strict.

This prevents a giant contributor from suppressing a smaller independent failure domain merely by being bigger.

`UNIQUE_FAILURE_DOMAIN_NE_DOMINATED_BY_BIGGER_DONOR`

`SAME_OWNER_REQUIRED_FOR_DOMINANCE_PRUNE`

`SAME_FAILURE_DOMAIN_REQUIRED_FOR_DOMINANCE_PRUNE`

## Synthetic result

The fixture contains 15 resource records.

Three are excluded before compaction because they are revoked, merely offered, or stale.

Of 12 eligible resources, three same-domain predecessors are dominated:

- `C-B1-OLD`;
- `C-D1-SHADOW`;
- `S-C1-OLD`.

Nine remain on the active frontier.

For a four-class public correspondence pipeline, the simple Cartesian candidate upper bound contracts from:

```text
1 discovery
x 5 compute
x 3 storage
x 2 attention
= 30 candidate tuples
```

to:

```text
1 x 3 x 2 x 2
= 12 candidate tuples
```

That is a 60% reduction in this bounded candidate-product measure.

`CARTESIAN_CANDIDATE_COUNT_NE_FEASIBLE_COMPOSITION_COUNT`

## What must remain unchanged

R0 requires compaction to preserve:

- every distinct failure-domain route represented before pruning;
- public pipeline feasibility;
- distributed-compute feasibility;
- public-mirror feasibility;
- the fact that the private draft task remains incomplete without private review authority.

A dominated record remains historical provenance and may still matter for archaeology, rollback, or a future scope where the dominance relation no longer holds.

`COMPACTION_NE_DELETION_OF_PROVENANCE`

`DOMINATED_FOR_SCOPE_NE_GLOBALLY_USELESS`

## Why this matters at scale

With thousands or millions of grants, naïvely expanding every compatible tuple is not a scheduler. It is a denial-of-service attack performed by combinatorics.

Future compaction can add additional safe layers such as:

- exact duplicate collapse by content/resource identity;
- stale-route retirement;
- scope-equivalence classes;
- Pareto frontiers over capacity/reliability/cost/latency/energy;
- locality and privacy partitions;
- bounded top-k per independent failure domain;
- cached composition motifs;
- negative-knowledge pruning for impossible task/resource relations;
- demand-conditioned wake/sleep;
- receiver-pressure-aware frontier width.

Each layer must preserve the reason an option was removed and the condition under which it becomes relevant again.

## Relation to "x a zillion"

The positive network effect is not simply:

`MORE_USERS -> MORE_COMPUTE`

It is closer to:

`MORE_VALID_GRANTS -> MORE_DISTINCT_CAPABILITIES -> MORE_POSSIBLE_SAFE_COMPOSITIONS`

while compaction supplies the counter-force:

`MORE_OPTIONS -> MORE_EQUIVALENCE/Dominance_RELATIONS -> SMALLER_HOT_FRONTIER`

That balance lets the option reservoir grow without forcing the active scheduler to materialize every possible relation.

## Current boundary

This canary operates only on synthetic resource descriptions.

It performs no real compute, storage, network, model, messaging, human-attention, financial, credential, device, sensor, or public effect.

No grant is promoted, leased, executed, integrated, made canonical, or given governance weight.

## Rails

`COMPACTION_NE_DELETION_OF_PROVENANCE`  
`DOMINATED_FOR_SCOPE_NE_GLOBALLY_USELESS`  
`SAME_FAILURE_DOMAIN_REQUIRED_FOR_DOMINANCE_PRUNE`  
`SAME_OWNER_REQUIRED_FOR_DOMINANCE_PRUNE`  
`SAME_PRIVACY_AND_PURPOSE_REQUIRED_FOR_DOMINANCE_PRUNE`  
`UNIQUE_FAILURE_DOMAIN_NE_DOMINATED_BY_BIGGER_DONOR`  
`CARTESIAN_CANDIDATE_COUNT_NE_FEASIBLE_COMPOSITION_COUNT`  
`OPTION_SPACE_REDUCTION_NE_EXECUTION_AUTHORITY`  
`COMPACTION_NE_TRUTH`  
`RESOURCE_CONTRIBUTION_NE_GOVERNANCE_AUTHORITY`  
`VALIDATION_IS_NOT_ACCEPTANCE`
