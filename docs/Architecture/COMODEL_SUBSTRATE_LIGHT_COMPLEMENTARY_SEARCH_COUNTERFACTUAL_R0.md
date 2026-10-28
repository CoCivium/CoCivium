# CoModel substrate-light complementary search counterfactual R0

**State:** `CONTROLLED_COMPLEMENTARY_SEARCH_SINGLE_VS_PARALLEL_CI_CANARY__NO_RUNTIME_NO_CANON_NO_AUTHORITY_CHANGE`

## Purpose

Test a controlled task where physical width 3 can plausibly earn **additional unique verified benefit**, unlike the prior duplicate-computation control.

The logical work object is one bounded partitioned search:

> find all integers divisible by 7 across three disjoint four-record shards during one receiver lease.

Each receiver may inspect:

- at most four records;
- exactly one shard;
- during one bounded lease.

## Treatments

```text
width 1:
  S0 -> shard A

width 3:
  P0 -> shard A
  P1 -> shard B
  P2 -> shard C
```

The exact target set is:

`7, 14, 21`

The receiver code derives targets using the predicate itself rather than reading a target label.

## Scoring

One **unique correct target discovered** is one qualified benefit unit.

One completed logical search wave is one verified deed for the treatment.

Execution cost is tracked separately as receiver leases.

Expected controlled result:

```text
single width 1:
  unique targets = 1
  benefit yield per logical wave = 1
  execution cost = 1

parallel width 3:
  unique targets = 3
  benefit yield per logical wave = 3
  execution cost = 3
```

Thus the fixture is designed to demonstrate **coverage gain**, not efficiency gain.

`PARALLEL_COVERAGE_GAIN_NE_PARALLEL_EFFICIENCY_GAIN`

## Why widening is still not authorized

A positive benefit gate is necessary but not sufficient.

The existing CoBenefit+/CoOomph policy also requires evidence that:

- receiver pressure;
- proof debt;
- collision risk;
- human-attention cost;
- compute cost

remain within their hard budgets.

This counterfactual does not measure those pressure budgets.

Therefore the expected advisory result is:

`POSITIVE_VERIFIED_COVERAGE_GAIN__PRESSURE_BUDGET_EVIDENCE_REQUIRED_BEFORE_WIDENING`

and:

`physical_width_change_authorized = false`

A controller that widens merely because the benefit graph improved would be performing the distributed-systems equivalent of buying three excavators before checking whether there is room on the site.

## Custody

Each of the four receiver jobs emits an exact receipt.

Fan-in downloads all four and emits exact content-hash readproof.

A PASS supports:

`PICKED_UP_BY_COMPLEMENTARY_COUNTERFACTUAL_COMPILER`

for those four exact workflow receipts only.

No integration or runtime mutation follows.

## Interpretation

A PASS supports only this bounded statement:

`PARTITIONED_PARALLEL_SEARCH_CAN_INCREASE_UNIQUE_VERIFIED_COVERAGE_PER_LOGICAL_WAVE_WHEN_RECEIVER_LEASES_COVER_COMPLEMENTARY_DISJOINT_SHARDS`

It does not support:

- parallel efficiency gain;
- generalized real-world utility;
- arbitrary model ensemble benefit;
- permission to widen runtime workers;
- canon or CoEx.

## Next frontier

If this positive benefit canary passes, feed its exact fan-in receipt to the metabolism observer together with **measured pressure-budget evidence**.

Only then can an advisory widening decision become eligible.

## Rails

`PARALLEL_COVERAGE_GAIN_NE_PARALLEL_EFFICIENCY_GAIN`  
`BENEFIT_PER_LOGICAL_WAVE_NE_BENEFIT_PER_COMPUTE`  
`CONTROLLED_CI_COUNTERFACTUAL_NE_REAL_WORLD_BENEFIT`  
`POSITIVE_GAIN_IN_THIS_TASK_NE_POSITIVE_GAIN_FOR_OTHER_TASKS`  
`PRESSURE_METRICS_ABSENT_NE_PRESSURE_BUDGET_PASS`  
`BENEFIT_NE_AUTHORITY`  
`PICKED_UP_BY_COMPLEMENTARY_COUNTERFACTUAL_COMPILER_NE_INTEGRATED`  
`POSITIVE_COVERAGE_GAIN_NE_RUNTIME_WIDEN_PERMISSION`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`
