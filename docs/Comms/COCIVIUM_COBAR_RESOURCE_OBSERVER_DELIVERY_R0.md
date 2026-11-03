# CoCivium CoBar Resource Observer Delivery Capsule R0

**State:** `CANDIDATE_MACHINE_CONSUMABLE_HANDOFF__NO_LOCAL_PICKUP_NO_RUNTIME_ADOPTION`

## CoHereNow

PR137 already proves:

```text
resource interface
-> exact GitHub receiver readproof
-> CoCivium observer projection
```

The remaining gap is the local visible journey:

```text
observer projection
-> current authorized CoBar receiver
-> Rick-visible readback
```

R0 packages the exact observer projection into a machine-consumable delivery capsule so that a future local receiver can pick it up without Rick downloading, copying, pasting, or relaying hashes.

## What the capsule binds

The capsule requires the exact:

- observer projection SHA-256;
- PR137 head SHA;
- source commit time;
- source receiver identity;
- source receipt SHA-256;
- CoHereNow / Meaning / NextSafeAction / Evidence payload.

It targets:

`CURRENT_AUTHORIZED_LOCAL_COBAR_RECEIVER`

but does not claim that receiver is currently reachable from this GitHub execution surface.

## Pickup proof

A local receiver may claim `PICKED_UP_BY_CURRENT_COBAR_RECEIVER` only after emitting:

- receiver identity;
- exact projection SHA-256;
- source head SHA;
- source commit time;
- receiver read timestamp;
- exact payload readback.

A pointer, artifact URL, path, or browser visibility is not pickup.

`POINTER_NE_ACK`

`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`

## UX proof

Even exact CoBar pickup is not enough for UX acceptance.

The target journey still requires:

`Rick-visible readback`

on the current observer surface.

Until that exists:

`UX_ACCEPTANCE_UNPROVEN`

## No user transport

The contract explicitly sets:

`user_relay_required = false`

The intended receiver must fetch or receive the exact capsule/projection through an authorized machine route.

Rick is not the checksum courier. Humanity has already invented enough unpaid middle-management roles.

## Current boundary

This R0 performs no:

- local filesystem write;
- CoBar mutation;
- CoBar launch;
- browser/UI manipulation;
- runtime adoption;
- external effect;
- canon or CoEx promotion.

It only produces a current-head-bound delivery capsule artifact.

## Rails

`CAPSULE_NE_COBAR_PICKUP`  
`ARTIFACT_VISIBLE_NE_LANDED_AT_LOCAL_COBAR`  
`POINTER_NE_ACK`  
`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`  
`COBAR_PICKUP_NE_RICK_VISIBLE_READBACK`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`UX_ACCEPTANCE_UNPROVEN_UNTIL_VISIBLE_READBACK`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`
