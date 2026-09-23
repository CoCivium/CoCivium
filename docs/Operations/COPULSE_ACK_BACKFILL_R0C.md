# CoPulse Per-Receiver ACK / Backfill Canary R0C

**State:** `PASS_BOUNDED_CONTAINER_LOCAL_SYNTHETIC__ACK_CHAIN_AND_BACKFILL_PROVEN__NOT_X2_NOT_GLOBAL_BUS`

R0C advances the R0B exact readproof boundary into an explicit **receiver-local ACK chain**.

A receiver may commit an ACK cursor only after an exact R0B readproof binds:

- receiver identity;
- exact packet hash;
- selected pulse IDs/cursors;
- proposed ACK cursor.

Subsequent ACK commits bind the exact SHA-256 of the prior ACK object. Cursor regression or receiver-chain substitution fails closed.

## Canary

The bounded two-receiver canary performs two rounds.

Round 1:

- CoUX begins at ACK 0 and commits ACK 3.
- CoTheory begins at ACK 1 and commits ACK 3.

Round 2 uses one extended pulse field:

- CoUX receives only `pulse.fixture.ux.004` and advances 3 -> 4.
- CoTheory receives only `pulse.fixture.theory.005` and advances 3 -> 5.

Thus currentness can diverge safely by receiver role while both consume the same source pulse field.

## Boundary

ACK state is receiver-local, append-only evidence for this canary.

It is not provider context mutation, global consensus, integration, or CoEx.

`ACK_COMMIT_NE_INTEGRATION`  
`RECEIVER_LOCAL_ACK_NE_GLOBAL_ACK`  
`CURSOR_NE_CONTEXT_CONTENT`

## Next

R0D should add CoPressure-aware DIGEST compaction with explicit omitted-count/loss reporting and replay to exact source pulses.


## Bounded execution evidence

The exact R0C scripts matched their branch Git blob hashes before execution. The exact landed R0A router and R0B receiver scripts also matched main. The container-local synthetic canary then proved two independent receiver-local ACK chains across two routing rounds.

Evidence: `docs/Operations/proofs/copulse-r0c-container-pass-20260923.json`.

This proves the bounded ACK-chain/backfill behavior only. It does not prove provider context mutation, integration, X2 runtime, global ACK consensus, or a live global bus.
