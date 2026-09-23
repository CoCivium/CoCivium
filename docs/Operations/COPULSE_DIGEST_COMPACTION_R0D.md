# CoPulse CoPressure-Aware DIGEST Compaction R0D

**State:** `PASS_BOUNDED_CONTAINER_LOCAL_SYNTHETIC__EXPLICIT_LOSS_REPORT__EXACT_REPLAY__NOT_GLOBAL_BUS`

R0D reduces receiver-facing currentness load without deleting or silently collapsing source pulses.

The control relation is:

`R0A receiver packet -> CoPressure policy -> lossy DIGEST projection -> explicit loss report -> exact replay manifest -> source packet`

HOT and WARM entries remain individually visible. DIGEST entries may be compacted according to bounded pressure:

- LOW: no DIGEST compaction.
- MODERATE: deterministic chunks of three DIGEST entries.
- HIGH: all DIGEST entries in one bounded group.
- DEGRADED: same maximum compaction as HIGH for this first canary.

This is a UX/currentness projection policy, not an ontological claim about importance.

## Loss contract

Every compacted group preserves:

- exact source pulse IDs;
- exact cursors;
- source packet indices;
- canonical per-entry SHA-256 hashes;
- unioned domains/topics;
- relation-type counts;
- epistemic-class counts.

The projection explicitly reports fields omitted from its compact view. The exact source packet remains bound and unmodified.

`COMPACTION_NE_DELETION`
`DIGEST_NE_SEMANTIC_EQUIVALENCE`
`REPLAYABILITY_NE_SOURCE_RETIREMENT_AUTHORITY`

R0D does not generate an AI summary. This first rung is mechanical and deterministic so projection loss is inspectable rather than charmingly improvised by a language model.

## Exact replay

`CoPulseDigestReplayR0D.py` verifies the source packet hash, each replay-manifest identity, source index, cursor and canonical entry hash, then reconstructs the exact original DIGEST sequence.

Replay proves exact source-entry recoverability for the bound packet. It does not prove integration, CoEx, or authority to retire the source.

## Bounded canary

Synthetic source:

- 8 selected entries total;
- 1 HOT;
- 1 WARM;
- 6 DIGEST.

Observed results:

- LOW: 8 visible items, 0 digest groups;
- MODERATE: 4 visible items, 2 digest groups;
- HIGH: 3 visible items, 1 digest group;
- DEGRADED: 3 visible items, 1 digest group;
- all 6 DIGEST entries replayed exactly under every compacting pressure;
- source packet unchanged;
- ACK cursor mutation = 0.

Execution proof:
`docs/Operations/proofs/copulse-r0d-container-pass-20260923.json`

## Next

R0E should prove receiver pickup and ACK behavior for a compacted digest projection while preserving exact source replay drill-down.

`COMPACTION_NE_RECEIVER_PICKUP`
`CANDIDATE_DELIVERED_CURSOR_NE_ACK_CURSOR`
`LOCAL_CANARY_NE_LIVE_GLOBAL_BUS`
