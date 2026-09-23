# CoPulse Per-Receiver ACK / Backfill Canary R0C

**State:** `IMPLEMENTATION_CANDIDATE__EXECUTION_EVIDENCE_REQUIRED`

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
