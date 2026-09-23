# CoPulse Two-Receiver Pickup Canary R0B

**State:** `PASS_BOUNDED_CONTAINER_LOCAL_SYNTHETIC__TWO_RECEIVER_PICKUP_PROVEN__NOT_X2_NOT_GLOBAL_BUS`

R0B tests the exact receiver boundary that R0A deliberately refused to fake.

One bounded public pulse field is routed independently to:

- a CoUX receiver with its own ACK cursor;
- a CoTheory receiver with a different ACK cursor.

Each receiver runs as a separate OS process, reads the exact packet bytes, verifies packet SHA-256 and receiver identity, parses selected pulse IDs/cursors, and emits a receiver-produced readproof.

## What can prove PICKED_UP

For the bounded packet only, a receiver readproof may support `PICKED_UP` when it binds:

- receiver identity;
- exact packet SHA-256;
- exact packet ID;
- selected pulse IDs/cursors;
- coverage boundary;
- receiver process identity.

It does not prove integration into a working baseline.

`PICKED_UP_NE_INTEGRATED`

## Independence checks

The canary requires:

- distinct receiver process IDs;
- distinct receiver IDs;
- distinct role profiles;
- the same source pulse-field hash;
- distinct role-specific packet hashes;
- distinct selected pulse sets;
- distinct initial ACK cursors;
- zero shared ACK mutation.

Both processes may still inhabit the same host/failure domain.

`TWO_PROCESSES_NE_TWO_FAILURE_DOMAINS`

## Cursor boundary

R0B records a receiver-proposed ACK cursor but does not mutate shared ACK state.

R0C is the first place an explicit per-receiver ACK commit/backfill cycle should be tested.

## Nonclaims

No provider-session pickup, live global bus, private routing, integration, CoEx, or cross-failure-domain replication is claimed.


## Bounded execution evidence

The exact landed router/receiver/canary scripts were recreated byte-for-byte and their Git blob hashes matched main before execution. A container-local synthetic canary then passed with two distinct receiver processes, distinct profiles, distinct initial ACK cursors, role-specific packet hashes and selected pulse sets, the same pulse-field hash, and zero shared ACK mutation.

Evidence: `docs/Operations/proofs/copulse-r0b-container-pass-20260923.json`.

This proves receiver-relative `PICKED_UP` for the two exact synthetic packets only. It does not prove X2 runtime, provider-session pickup, integration, or a live global bus.
