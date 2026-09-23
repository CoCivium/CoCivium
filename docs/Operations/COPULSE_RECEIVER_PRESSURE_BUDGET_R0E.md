# CoPulse Receiver-Pressure DIGEST Budget Election R0E

**State:** `CANDIDATE__RECEIVER_CAPACITY_DERIVED_BUDGET__R0D_REPLAY_REQUIRED`

## Purpose

Replace R0D's caller-supplied DIGEST budget with a deterministic budget derived from a bounded receiver pressure/capacity sample.

R0E keeps pressure as a vector. It does not collapse receiver state into a universal scalar score.

`COPRESSURE_VECTOR_NE_UNIVERSAL_SCORE`

## Capacity relation

For one exact CoPulse receiver packet:

`NON_DIGEST_OCCUPANCY = HOT_COUNT + WARM_COUNT`

`FREE_DIGEST_SLOTS = max(0, MAX_CURRENTNESS_ITEMS - NON_DIGEST_OCCUPANCY)`

`ELECTED_DIGEST_BUDGET = min(DIGEST_COUNT, FREE_DIGEST_SLOTS, MAX_DIGEST_SUMMARIES)`

HOT and WARM occupancy is reserved before any DIGEST budget is elected.

If DIGEST exists but no slot remains, state is:

`HOLD_DIGEST_CAPACITY_EXHAUSTED`

The DIGEST source is held for later currentness/backfill. It is not silently discarded.

## Pressure tiers

The tiers are descriptive projections of the vector, not authority or global health scores:

- `NO_DIGEST`: no DIGEST entries exist;
- `SATURATED`: DIGEST exists and free DIGEST slots are zero;
- `HIGH`: one summary slot is available for multiple DIGEST entries;
- `MODERATE`: more than one but fewer than all DIGEST entries can remain as summaries;
- `LIGHT`: budget is at least the DIGEST source count.

## Machine objects

- pressure input: `schemas/copulse-receiver-pressure-v0.1.schema.json`
- election output: `schemas/copulse-digest-budget-election-v0.1.schema.json`
- policy: `ai/copulse-digest-pressure-policy.json`
- election script: `scripts/CoPulseReceiverPressureBudgetR0E.py`
- canary: `scripts/CoPulseReceiverPressureBudgetCanaryR0E.py`

Any nonzero elected budget must be executed through R0D compaction and exact replay before omitted source detail may be treated as recoverable.

## Bounded canary

The canary uses one packet with:

- HOT = 1
- WARM = 1
- DIGEST = 4

Four synthetic receiver-capacity samples elect:

- capacity 6 -> free DIGEST slots 4 -> budget 4 -> LIGHT;
- capacity 4 -> free DIGEST slots 2 -> budget 2 -> MODERATE;
- capacity 3 -> free DIGEST slot 1 -> budget 1 -> HIGH;
- capacity 2 -> free DIGEST slots 0 -> budget 0 -> SATURATED/HOLD.

For budgets 4, 2 and 1, the canary must run R0D compaction plus exact replay and recover all four source DIGEST objects.

For budget 0, no compaction runs. DIGEST remains held.

Execution evidence is recorded under:

`docs/Operations/proofs/copulse-r0e-container-pass-20260923.json`

Observed bounded PASS:

- exact branch script/schema Git blobs matched before execution;
- input/output schemas validated for all four pressure cases;
- elected budgets: `4 -> 2 -> 1 -> 0` as available capacity fell;
- LIGHT budget 4 replayed all 4 DIGEST source objects exactly;
- MODERATE budget 2 replayed all 4 exactly;
- HIGH budget 1 replayed all 4 exactly;
- SATURATED budget 0 held DIGEST and did not run compaction;
- canary result SHA-256: `E6DB919CBE90940950AD5049086B02414A2DF5760F68A726E9EB679464DB8D08`;
- ACK/provider-session/authority/source-delete/receiver-context effects: 0.

## Boundary

R0E does not yet prove:

- freshness/staleness expiry of a pressure sample;
- multi-receiver pressure divergence on one live pulse field;
- X2 runtime;
- provider-session mutation;
- private/restricted routing;
- integration or CoEx.

## Next

`R0F_STALENESS_AND_MULTI_RECEIVER_CAPACITY_ELECTION_CANARY`

## Rails

`COPRESSURE_VECTOR_NE_UNIVERSAL_SCORE`  
`CAPACITY_NE_AUTHORITY`  
`BUDGET_NE_PERMISSION_TO_DELETE`  
`ZERO_CAPACITY_NE_SILENT_DROP`  
`HOT_WARM_NE_DIGEST`  
`COMPACTION_NE_DELETION`  
`EXPLICIT_LOSS_NE_ZERO_LOSS`
