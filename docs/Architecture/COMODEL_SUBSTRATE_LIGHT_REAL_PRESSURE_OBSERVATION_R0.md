# CoModel substrate-light real pressure observation R0

**State:** `RAW_PRESSURE_OBSERVATION + WIDTH_SEMANTIC_CORRECTION__NO_RUNTIME_NO_CANON`

## Purpose

Measure what the positive complementary-search counterfactual actually did at the GitHub-hosted execution layer, instead of treating a declared matrix width as proof of simultaneous physical width.

The source counterfactual showed genuine unique coverage gain from three complementary receiver leases.

This R0 asks a different question:

> how many of those receiver jobs were actually simultaneous, what queue/wall-time evidence exists, and can those raw observations be translated into the current CoBenefit+/CoOomph hard-budget units?

## Exact source

Workflow run:

`36746050561`

Source fan-in artifact:

`11112796491`

Exact source receipt SHA-256:

`2D3DDE96B4FB864DBDCC1DA8BE08F050ACA5ED9911BFF1C24717D30E11B937C0`

The exact receipt is copied to the candidate branch and re-read by:

`github-actions:PR135_REAL_PRESSURE_OBSERVATION_COMPILER_R0`

## Width correction

The counterfactual receipt labels the parallel treatment physical width as `3`.

Live GitHub job metadata is the authority for observed execution concurrency.

R0 computes concurrency from job start/completion intervals using half-open intervals `[start,end)`.

Therefore:

`REQUESTED_WIDTH_NE_OBSERVED_CONCURRENCY`

If GitHub schedules only two of the three receiver jobs at once, the correct statement becomes:

`REQUESTED_WIDTH_3__OBSERVED_MAX_CONCURRENCY_2`

The positive coverage result can remain valid for **three complementary receiver leases within one workflow wave**, while the literal simultaneous-width claim is downgraded.

## Raw observables

The compiler records:

- requested receiver width;
- observed maximum concurrent parallel receiver jobs;
- queue wait per receiver job;
- wall time per receiver job;
- total receiver job wall seconds;
- end-to-end parallel receiver span;
- fan-in queue/wall time;
- missing exact readproof count;
- observed replica/shard assignment collisions;
- whether human-attention or energy measurements exist.

These are raw observations, not automatically policy metrics.

## Calibration boundary

The existing synthetic CoBenefit+/CoOomph policy uses abstract hard-budget fields:

- `receiver_pressure`
- `proof_debt`
- `collision_risk`
- `human_attention_cost`
- `compute_cost`

Their R0 units were never calibrated to GitHub queue seconds, runner wall seconds, receiver leases, or human-attention telemetry.

So this bridge does **not** silently compare seconds to an abstract threshold and call it science.

Each translation remains explicit:

`RAW_OBSERVABLE -> UNMAPPED/UNMEASURED -> POLICY_BUDGET`

until a calibration contract exists.

## Expected advisory consequence

Even with positive coverage benefit, widening remains held if all hard budgets are not proven to pass.

Expected advisory state:

`HOLD_PRESSURE_BUDGET_TRANSLATION_UNCALIBRATED`

No runtime width mutation is authorized.

## Rails

`REQUESTED_WIDTH_NE_OBSERVED_CONCURRENCY`  
`DECLARED_WIDTH_NE_OBSERVED_SIMULTANEOUS_WIDTH`  
`JOB_WALL_SECONDS_NE_COMPUTE_ENERGY`  
`QUEUE_WAIT_NE_GLOBAL_RECEIVER_PRESSURE`  
`ZERO_OBSERVED_COLLISION_NE_ZERO_COLLISION_RISK`  
`MISSING_READPROOFS_0_NE_ZERO_PROOF_DEBT_ON_ALL_SURFACES`  
`UNMEASURED_HUMAN_ATTENTION_NE_ZERO_HUMAN_ATTENTION_COST`  
`RAW_OBSERVABLE_NE_POLICY_BUDGET_UNIT`  
`POSITIVE_COVERAGE_GAIN_NE_PROVEN_WIDTH_3_SIMULTANEITY`  
`PRESSURE_OBSERVATION_NE_RUNTIME_WIDEN_PERMISSION`  
`PICKED_UP_BY_PRESSURE_COMPILER_NE_INTEGRATED`  
`VALIDATION_IS_NOT_ACCEPTANCE`
