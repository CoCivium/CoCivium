# CoAll In-Flight Revocation R0

**State:** `CANDIDATE__SYNTHETIC_INFLIGHT_REVOCATION_POLICY__NO_REAL_EXECUTION`

## Purpose

The existing resource-lease canary proves revocation before execution invalidates future use.

This companion canary covers the harder case: revocation arrives after a bounded task has already started.

The policy distinguishes work by interruption semantics instead of pretending every operation can stop instantly.

`REVOCATION_RECEIVED_NE_INSTANT_PHYSICAL_STOP`

## Interruption classes

A leased work unit SHOULD declare one of:

- `NOT_STARTED`
- `CHECKPOINTABLE`
- `ATOMIC_SAFE_COMPLETE`
- `EXTERNAL_HIGH_EFFECT`

### NOT_STARTED

Do not begin after revocation.

### CHECKPOINTABLE

Stop at the next safe checkpoint. Do not begin another work unit.

### ATOMIC_SAFE_COMPLETE

If stopping mid-operation would create a worse or inconsistent state, complete only the already-started atomic unit required to reach a safe boundary, then stop.

### EXTERNAL_HIGH_EFFECT

Fail closed unless the exact effect adapter has a separately proven safe-abort or rollback contract.

`IN_FLIGHT_NE_PERMISSION_TO_EXPAND_SCOPE`

`SAFE_COMPLETION_NE_NEW_WORK`

`HIGH_EFFECT_REVOCATION_REQUIRES_PROVEN_ABORT_OR_ROLLBACK`

## Partial output

A partial result after revocation remains incomplete and inherits the original confidentiality / retention ceiling.

`PARTIAL_NE_COMPLETE`

`PARTIAL_OUTPUT_NE_PUBLICATION_AUTHORITY`

## Receipts

Already validly completed work remains part of history.

Revocation prevents future use. It does not rewrite provenance.

`REVOCATION_NE_HISTORY_ERASURE`

`REVOCATION_NE_RETROACTIVE_INVALIDATION_OF_PRIOR_VALID_EFFECT`

## First safe canary

The synthetic cases prove:

1. unstarted work is blocked;
2. checkpointable work stops at the next safe checkpoint;
3. atomic work may complete only its already-started atomic unit;
4. external high-effect work without a proven abort contract is held;
5. prior valid receipts remain valid historical evidence;
6. partial output gains no publication authority.

No real compute, messaging, storage, financial, device, or external effect is executed.
