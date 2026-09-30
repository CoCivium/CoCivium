# CoModel substrate-light closed-loop metabolism R0

**State:** `SYNTHETIC_RECEIPT_BACKED_CLOSED_LOOP_METABOLISM__NO_RUNTIME_NO_CANON_NO_AUTHORITY_CHANGE`

## Purpose

Turn the one-shot measured-benefit physical-width election into a bounded closed loop:

```text
observe receipt-backed outcome
-> recompute benefit + pressure
-> elect width
-> run another bounded wave
-> observe another receipt
-> widen / hold / contract
```

R0 adds hysteresis and cooldown so one noisy observation cannot repeatedly reverse physical width.

## State

The loop carries only:

- logical branch count;
- physical width;
- widen streak;
- contract streak;
- transition cooldown.

Logical branch count remains `3` throughout this fixture.

Physical width may be `1` or `3`.

## Hysteresis

### Widening

Physical width may widen from 1 to 3 only after **two consecutive** observations where:

- qualified benefit per verified deed is at least 10% above the single-width baseline;
- counterfactual confidence meets the existing floor;
- every hard pressure/cost budget passes.

One strong wave is therefore evidence, not permission to flap.

### Contraction

A hard-budget breach contracts width 3 -> 1 immediately.

A mere loss of verified-benefit advantage requires **two consecutive no-gain observations** before contraction.

This separates safety/pressure contraction from ordinary performance noise.

### Cooldown

Every width transition starts a one-wave cooldown.

During cooldown:

- non-safety reversal is blocked;
- streaks reset;
- hard-budget contraction may still occur.

## Receipt binding

Every wave carries a unique synthetic `wave_receipt_sha256`.

The validator requires:

- 64-hex receipt form;
- one receipt per observation;
- unique receipts;
- receipt inclusion in the transition ledger.

These are synthetic receipt identifiers, not receiver-produced custody receipts.

`SYNTHETIC_WAVE_RECEIPT_NE_REAL_RECEIVER_RECEIPT`

## Demonstrated sequence

The 11-wave fixture proves:

1. one strong wave does not widen;
2. a second strong wave widens 1 -> 3;
3. cooldown blocks immediate reversal;
4. one weak-yield wave does not contract;
5. a second weak-yield wave contracts 3 -> 1;
6. cooldown blocks immediate re-widening;
7. two later strong waves widen again;
8. receiver-pressure breach contracts immediately despite cooldown;
9. cooldown prevents immediate re-widening;
10. low counterfactual confidence holds width 1.

Final width is 1 while logical branch count remains 3.

## Why this matters

The architecture can now represent **logical breadth with metabolic physical embodiment**:

```text
logical work remains broad
physical embodiment breathes
proof/pressure receipts regulate the breathing
```

That is a stronger control shape than either always-on agents or stateless one-shot routing.

Still, this is a synthetic state machine. No runtime daemon or scheduler is created.

## Next frontier

The next bounded frontier is replacing synthetic wave observations with **real receiver-produced receipts** from safe model/CI work, while keeping width transitions advisory until a runtime authority surface explicitly accepts them.

## Rails

`RECEIPT_BACKED_OBSERVATION_BEFORE_WIDTH_REVISION`  
`HARD_BUDGET_BREACH_CONTRACTS_IMMEDIATELY`  
`HYSTERESIS_BEFORE_NONSAFETY_WIDTH_TRANSITION`  
`TRANSITION_COOLDOWN_BLOCKS_NONSAFETY_REVERSAL`  
`LOGICAL_PARALLELITY_NE_PHYSICAL_WIDTH`  
`SYNTHETIC_WAVE_RECEIPT_NE_REAL_RECEIVER_RECEIPT`  
`HYSTERESIS_NE_OPTIMAL_CONTROL`  
`BENEFIT_OBSERVED_NE_BENEFIT_CAUSED`  
`BENEFIT_NE_AUTHORITY`  
`CLOSED_LOOP_CANARY_NE_RUNTIME_SCHEDULER`  
`VALIDATION_IS_NOT_ACCEPTANCE`
