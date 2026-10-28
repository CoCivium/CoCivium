# CoModel substrate-light measured-benefit / CoOomph parallelism R0

**State:** `SYNTHETIC_MEASURED_BENEFIT_PARALLELISM_CANARY__NO_RUNTIME_NO_CANON_NO_AUTHORITY_CHANGE`

## Purpose

The previous multi-embodiment fan-in intentionally elected no winner for the default parallelism policy.

This R0 supplies a bounded external criterion from existing CoBenefit+ / CoOomph+ and dynamic-wave doctrine:

```text
widen physical embodiment only when

qualified benefit per verified deed strictly improves
AND receiver pressure <= budget
AND proof debt <= budget
AND collision risk <= budget
AND human-attention cost <= budget
AND compute cost <= budget
AND counterfactual confidence >= floor
```

Otherwise the logical branches may remain distinct while physical execution serializes.

## Logical parallelity is not physical width

R0 keeps:

`logical_branch_count = 3`

through every scenario.

The elected physical width may be:

- `3` when measured synthetic benefit justifies widening;
- `1` when pressure, proof, collision, attention, compute or insufficient yield blocks widening;
- `1` with an explicit measurement HOLD when counterfactual confidence is too low.

Thus:

`MASSIVE_PARALLELITY_NE_MASSIVE_SIMULTANEOUS_MATERIALIZATION`

and:

`LOGICAL_LANE_NE_WORKER`

become executable constraints rather than slogans.

## Six scenarios

1. **Verified yield improves and every hard budget passes**
   - physical width widens from 1 to 3.

2. **Yield improves but receiver pressure is too high**
   - logical width stays 3;
   - physical width serializes to 1.

3. **No strict verified-benefit yield gain**
   - physical width remains 1.

4. **Benefit looks large but counterfactual confidence is below floor**
   - widening is held for better measurement.

5. **Proof debt and collision risk are too high**
   - physical execution serializes.

6. **Human-attention and compute costs exceed budget**
   - physical execution serializes.

No scenario may infer authority from benefit.

## Why hard budgets instead of one magic score

R0 deliberately avoids a single weighted utility number that could trade privacy, proof quality or receiver capacity against compute convenience.

Hard constraints remain hard.

The benefit comparison occurs only after the confidence floor and before widening; budget failures still block widening even when the synthetic benefit yield is higher.

This keeps:

`BENEFIT_NE_AUTHORITY`

and avoids turning CoOomph into “more GPUs because graph went up.”

## Donor contraction

R0 exact-binds:

- `docs/Operations/COPARTICIPANT_EDGE_EVOLUTION_R0.md`
- `COEVO.PR90.CONOD_DYNAMIC_WAVE.UNIQUE_FANIN.R0`
- the PR135 multi-embodiment fixture

It extends those landed/candidate relations instead of creating another scheduling ontology.

## What a PASS means

A PASS supports only:

`SYNTHETIC_PHYSICAL_WIDTH_CAN_BE_ELECTED_FROM_QUALIFIED_BENEFIT_AND_HARD_PRESSURE_BUDGETS_WITHOUT_COLLAPSING_LOGICAL_PARALLELITY`

It does not prove:

- real-world benefit;
- causal attribution of benefit;
- runtime scheduling;
- optimal cost weights;
- energy efficiency;
- real model ensemble superiority;
- receiver acceptance.

## Rails

`SYNTHETIC_BENEFIT_UNITS_NE_REAL_WORLD_UTILITY`  
`BENEFIT_OBSERVED_NE_BENEFIT_CAUSED`  
`BENEFIT_NE_AUTHORITY`  
`COOOMPH_NE_MAX_COMPUTE`  
`MASSIVE_PARALLELITY_NE_MASSIVE_SIMULTANEOUS_MATERIALIZATION`  
`SOURCE_EMISSION_RATE_NE_RECEIVER_CAPACITY`  
`LOGICAL_LANE_NE_WORKER`  
`ACCELERATION_NE_PROGRESS`  
`VALIDATION_IS_NOT_ACCEPTANCE`
