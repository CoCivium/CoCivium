# CoPulse Pressure Freshness + Multi-Receiver Capacity Canary R0F

**State:** `CANDIDATE__BOUNDED_PASS__EXPLICIT_STALENESS_GATE__DIVERGENT_RECEIVER_BUDGETS`

## Purpose

Extend R0E with two missing receiver-relative properties:

1. a pressure/capacity sample must be fresh at an explicitly bound evaluation time before it may influence DIGEST budget election;
2. two receivers observing the same pulse field may legitimately elect different DIGEST budgets because receiver capacity and ACK state are local relations, not global constants.

`OBSERVER_TIME_NE_GLOBAL_TIME`  
`DIVERGENT_BUDGETS_NE_INCONSISTENCY`

## Freshness contract

R0F never calls an implicit wall clock.

The caller binds:

- `evaluated_at`;
- `max_age_seconds`;
- `max_future_skew_seconds`.

For:

`AGE_SECONDS = EVALUATED_AT - SAMPLED_AT`

the gate emits:

- `PASS_FRESH_PRESSURE_SAMPLE` when the sample is inside the bounded age/skew window;
- `HOLD_STALE_PRESSURE_SAMPLE` when too old;
- `HOLD_FUTURE_PRESSURE_SAMPLE` when implausibly ahead of the bound observer time.

Stale/future samples stop before R0E budget election.

Freshness is not proof that the capacity measurement is accurate.

## Multi-receiver relation

The bounded canary uses one six-pulse source field:

- cursor 1: HOT
- cursor 2: WARM
- cursors 3-6: DIGEST

Receiver A:

- last ACK cursor 2;
- fresh capacity sample;
- selected set = cursors 3-6;
- elected DIGEST budget = 4.

Receiver B:

- last ACK cursor 0;
- fresh capacity sample;
- selected set = cursors 1-6;
- elected DIGEST budget = 1.

Receiver C:

- last ACK cursor 0;
- stale capacity sample;
- R0E budget election is not run.

A and B bind the exact same source pulse-field SHA-256 while preserving independent ACK state.

Both fresh receivers must run R0D exact replay for every selected DIGEST source object.

## Machine objects

- freshness schema: `schemas/copulse-pressure-freshness-v0.1.schema.json`
- freshness policy: `ai/copulse-pressure-freshness-policy.json`
- freshness gate: `scripts/CoPulseReceiverPressureFreshnessR0F.py`
- canary: `scripts/CoPulseMultiReceiverPressureFreshnessCanaryR0F.py`
- downstream budget election: R0E
- downstream loss/replay: R0D

Execution evidence:

`docs/Operations/proofs/copulse-r0f-container-pass-20260923.json`

Observed bounded PASS:

- exact landed R0F/R0E/R0D script blobs and freshness-schema blob matched before execution;
- freshness schema validation: 3/3 objects PASS;
- shared pulse-field SHA-256: `4066B95E3CF3A6A1C8CF766A59C5C554C646F6C7868F1885CDB11ABCFA8641EE`;
- Receiver A: ACK 2, pressure age 20s, budget 4, LIGHT, exact replay of 4 DIGEST source objects;
- Receiver B: ACK 0, pressure age 20s, budget 1, HIGH, exact replay of 4 DIGEST source objects;
- Receiver C: pressure age 900s, `HOLD_STALE_PRESSURE_SAMPLE`, R0E never executed;
- ACK/provider-session/authority/source-delete/receiver-context effects: 0;
- canary result SHA-256: `FFEDA758EB8B709B2737B646AC69845844BF2F16A2FB807FBD5C9B1048430B42`.

## Boundary

R0F does not yet prove:

- that MEASURED/DECLARED capacity sources are authentic;
- live receiver-instance binding;
- X2 runtime;
- provider-session mutation;
- private/restricted pressure transport;
- integration or CoEx.

## Next

`R0G_CAPACITY_SOURCE_PROVENANCE_AND_LIVE_RECEIVER_BINDING_CANARY`

## Rails

`FRESHNESS_NE_TRUTH`  
`FRESH_SAMPLE_NE_CAPACITY_ACCURACY_PROOF`  
`STALE_SAMPLE_NE_ZERO_CAPACITY`  
`PRESSURE_SAMPLE_NE_AUTHORITY`  
`OBSERVER_TIME_NE_GLOBAL_TIME`  
`DIVERGENT_BUDGETS_NE_INCONSISTENCY`  
`INDEPENDENT_ACK_NE_GLOBAL_ACK`
