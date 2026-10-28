# CoModel substrate-light real counterfactual metabolism observation R0

**State:** `REAL_CONTROLLED_COUNTERFACTUAL_OBSERVATION__ADVISORY_ONLY__NO_RUNTIME_NO_CANON`

## Purpose

Feed the first non-synthetic controlled width observation into the substrate-light metabolism policy without granting the controller execution authority.

The source is the exact fan-in receipt from controlled single-vs-parallel workflow run:

`36737453263`

artifact:

`11107178630`

The receipt is preserved byte-for-byte on the PR135 candidate branch.

## Custody

The exact receipt copy is `LANDED`.

The elected receiver is:

`github-actions:PR135_REAL_METABOLISM_OBSERVATION_COMPILER_R0`

The receiver re-downloads the original historical artifact, verifies live artifact identity and archive digest, then requires exact byte equality with the landed copy.

Only after that readback may the receipt be described as:

`PICKED_UP_BY_METABOLISM_COMPILER`

for this bounded receiver.

## Policy handoff

The receipt already proves, for its exact deterministic work object:

```text
single width 1:
  benefit yield = 1
  execution cost = 1

parallel width 3:
  benefit yield = 1
  execution cost = 3
```

Therefore physical widening fails the necessary verified-benefit-gain gate.

The advisory metabolism action is:

`HOLD_PHYSICAL_WIDTH_1_NO_WIDEN`

No pressure metric is invented to reach that result. Pressure measurements would matter if widening were otherwise eligible, but no strict benefit-yield gain exists here.

## What this proves

A real receiver-produced controlled counterfactual can cross the custody boundary into the metabolism policy and produce a bounded advisory action.

It does not prove that the runtime is currently at width 1. The width-1 value is the candidate controller baseline from the R0 metabolism fixture.

It also does not authorize changing any running worker population.

`REAL_COUNTERFACTUAL_OBSERVATION_NE_RUNTIME_STATE`

## Next frontier

The next controlled task should be one where parallel embodiments can plausibly create **complementary** verified benefit rather than duplicate the same deterministic answer set.

Examples include bounded partitioned search, independent defect discovery, or challenger/verifier specialization with an exact scoring surface.

Only a controlled positive-gain receipt should become evidence for widening.

## Rails

`CONTROLLED_CI_COUNTERFACTUAL_NE_REAL_WORLD_BENEFIT`  
`NO_GAIN_IN_THIS_TASK_NE_NO_GAIN_FOR_OTHER_TASKS`  
`ONE_NO_GAIN_OBSERVATION_NE_GLOBAL_SERIAL_DEFAULT`  
`PICKED_UP_BY_METABOLISM_COMPILER_NE_INTEGRATED`  
`ADVISORY_ACTION_NE_RUNTIME_MUTATION`  
`BENEFIT_NE_AUTHORITY`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`
