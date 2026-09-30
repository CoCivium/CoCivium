# CoModel substrate-light dematerialization canary R0

**State:** `SYNTHETIC_CANARY__NO_RUNTIME_NO_CANON_NO_AUTHORITY_CHANGE`

## Question

Can a logical model role survive:

```text
materialized on substrate A
-> checkpoint
-> dematerialized
-> dormant with no live process
-> rehydrated on substrate B
-> continuity verification
```

without silently changing its identity, reconstruction recipe, authority ceiling, invariants, currentness or provenance?

R0 answers only for a synthetic state machine.

It does not move real model weights, invoke a provider model, claim consciousness continuity, or prove lossless reconstruction.

## Positive path

The fixture:

1. materializes a synthetic logical model role on `substrate:gpu-a`;
2. checkpoints exact currentness;
3. dematerializes;
4. enters a dormant state with no substrate and no live process;
5. rehydrates from the same checkpoint on `substrate:cpu-b`;
6. verifies logical identity, recipe version, authority, invariants, currentness and source provenance.

The canary computes a materialization duty cycle from the timeline rather than merely asserting one.

## Fail-closed challenges

R0 must reject:

- identity drift;
- authority widening;
- invariant drift;
- reconstruction recipe drift;
- currentness regression;
- missing source provenance;
- a supposedly dormant state that still has a live process.

## Interpretation

A PASS supports only:

`LOGICAL_CONTINUITY_CAN_BE_REPRESENTED_ACROSS_A_SYNTHETIC_DEMATERIALIZATION_REHYDRATION_SEQUENCE`

It does not support:

`REAL_MODEL_MIGRATION_IS_SOLVED`

or:

`COMPUTATION_IS_SUBSTRATE_FREE`

## Rails

`ABSTRACT_MODEL_NE_SUBSTRATE_FREE_EXECUTION`  
`MODEL_IDENTITY_NE_ACTIVE_PROCESS`  
`DEMATERIALIZED_NE_NONPHYSICAL`  
`MIGRATION_NE_CONTINUITY_WITHOUT_PROOF`  
`RECONSTRUCTIBLE_NE_LOSSLESS`  
`AUTHORITY_MUST_NOT_WIDEN_ON_REHYDRATION`  
`CURRENTNESS_MUST_NOT_REGRESS_ON_REHYDRATION`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`CANARY_PASS_NE_COEX`
