# CoPulse CoPressure DIGEST Compaction / Replay Canary R0D

**State:** `CANDIDATE__DIGEST_ONLY_COMPACTION__EXPLICIT_LOSS__EXACT_REPLAY_REQUIRED`

## Purpose

Advance R0C receiver-local ACK/backfill into a bounded CoPressure-aware DIGEST representation.

R0D compresses only entries already classified `DIGEST`. HOT and WARM entries pass through byte-semantic JSON objects unchanged.

The first rung deliberately avoids semantic summarization. It compacts representation, not meaning.

`SUMMARY_NE_SOURCE`

## Pressure contract

The caller supplies a positive `digest_budget`.

The budget limits **DIGEST summary objects only**. It never grants permission to compress HOT/WARM entries.

When DIGEST source count exceeds the budget, source entries are replaced in the compacted representation by deterministic digest summaries.

Each summary preserves:

- cursor range;
- domains/topics;
- epistemic-class set;
- relation-type set;
- source-identity set;
- subject count;
- exact source manifest of pulse IDs/cursors;
- canonical SHA-256 of every omitted source entry.

It does not pretend those aggregates reproduce the omitted source semantics.

## Loss report

Every compacted packet records:

- input DIGEST count;
- summary count;
- source entries omitted as individual entries;
- representation-item reduction;
- fields preserved only as aggregates;
- fields omitted from digest semantics;
- exact source packet SHA-256;
- replay requirement.

`EXPLICIT_LOSS_NE_ZERO_LOSS`

## Exact replay

`scripts/CoPulseDigestReplayR0D.py` requires the exact hash-bound source packet.

It verifies each source-manifest pulse ID, cursor and canonical entry SHA-256, then replays the exact decoded DIGEST source objects.

Replay proves source-object recovery for the bounded packet. It is not integration or ACK.

## Reference implementation

- `scripts/CoPulseDigestCompactorR0D.py`
- `scripts/CoPulseDigestReplayR0D.py`
- `scripts/CoPulseDigestCompactionCanaryR0D.py`

## Bounded canary

Synthetic packet:

- HOT: 1
- WARM: 1
- DIGEST: 4
- DIGEST budget: 1

Required result:

- HOT/WARM exact passthrough: 2
- DIGEST summaries: 1
- DIGEST source entries omitted inline: 4
- representation item reduction: 3
- exact replayed DIGEST entries: 4
- semantic summary generation: 0
- source deletion: 0
- ACK mutation: 0

Execution evidence is recorded under:

`docs/Operations/proofs/copulse-r0d-container-pass-20260923.json`

## Boundary

R0D does not prove:

- provider-session context mutation;
- live global currentness;
- semantic-summary quality;
- private/restricted compaction;
- integration;
- CoEx;
- source deletion;
- global ACK consensus.

## Next

`R0E_RECEIVER_PRESSURE_POLICY_AND_MULTI_DIGEST_BUDGET_REPLAY_CANARY`

R0E should bind budget election to explicit receiver pressure/capacity rather than a caller-supplied integer, while keeping exact replay and loss accounting mandatory.

## Rails

`COMPACTION_NE_DELETION`  
`SUMMARY_NE_SOURCE`  
`EXPLICIT_LOSS_NE_ZERO_LOSS`  
`HOT_WARM_NE_DIGEST`  
`REPLAY_NE_ACK`  
`REPLAY_NE_INTEGRATION`
