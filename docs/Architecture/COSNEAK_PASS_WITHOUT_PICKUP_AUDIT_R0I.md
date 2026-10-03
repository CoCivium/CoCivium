# CoSneak+ PASS Without Pickup Audit R0I

**State:** `PASS_BOUNDED_PASS_CLAIM_PICKUP_AUDIT__SAMPLED_SCOPE_ONLY`

## Why

R0F elected `Q07_PASS_WITHOUT_PICKUP` as the highest-value next bounded proof.

This audit samples five existing PASS-bearing evidence objects from main and classifies receiver pickup only where the sampled object itself contains exact receiver readproof/pickup evidence.

The question is not whether the producer-side work passed. It is whether a distinct intended receiver pickup is proven.

`PASS_NE_PICKUP`

`PRODUCER_SUCCESS_NE_RECEIVER_SUCCESS`

## Sample

### 1. CoEncounter R0C2 receiver qualification gate

Path:

`docs/Operations/proofs/coencounter-r0c2-receiver-qualification-gate-pass-20260924.json`

Producer state is PASS and the artifact contains explicit `receiver_readproof_sha256` values plus `bounded_pickups: 1` for each positive replay.

Classification:

`PICKUP_PROVEN_BOUNDED_SYNTHETIC`

It still does not prove semantic acceptance or integration.

### 2. CoPulse R0C ACK/backfill

Path:

`docs/Operations/proofs/copulse-r0c-container-pass-20260923.json`

The artifact binds per-receiver `round2_readproof_sha256` values and explicitly states:

`packet_pickup = PROVEN_FOR_BOUNDED_SYNTHETIC_RECEIVER_PACKETS`

Classification:

`PICKUP_PROVEN_BOUNDED_SYNTHETIC`

### 3. CoPulse R0F pressure/freshness

Path:

`docs/Operations/proofs/copulse-r0f-container-pass-20260923.json`

The producer canary passes and proves freshness gates, divergent budgets and exact replay. The artifact does **not** itself bind an exact receiver pickup/readproof for the R0F result and explicitly preserves:

`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`

Classification:

`PASS_WITH_PICKUP_UNPROVEN_FOR_THIS_RESULT`

### 4. CoEncounter R0B independent review

Path:

`docs/Operations/proofs/coencounter-r0b-container-pass-20260924.json`

The result passes independent review/routing, while lifecycle evidence explicitly says:

`receiver_pickup_of_match_packet = UNPROVEN`

Classification:

`PASS_WITH_PICKUP_UNPROVEN`

### 5. CoEncounter Yield R0A

Path:

`docs/Operations/proofs/coencounter-yield-r0a-container-pass-20260924.json`

The producer canary passes bounded contribution/yield checks, but explicitly preserves:

`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`

No distinct receiver readproof is bound in this artifact.

Classification:

`PASS_WITH_PICKUP_UNPROVEN`

## Result

Sample size: `5`

- pickup proven: `2`
- PASS with pickup unproven: `3`
- semantic acceptance proven: `0`
- integration proven by this audit: `0`

Therefore the sampled scope disproves the tempting inference:

`PASS -> PICKUP`

The stronger relation is:

`PASS -> PRODUCER-SIDE CLAIM SATISFIED`

and separately:

`EXACT RECEIVER READPROOF -> BOUNDED PICKUP PROVEN`

## CoSneak interpretation

This is a real CoSneak class:

`PASS_WITHOUT_PICKUP_VISIBILITY`

It can quietly create the appearance of completed work while the receiver boundary remains unproven.

The fix is **not** to downgrade every PASS. The fix is to type the lifecycle state explicitly.

Candidate lifecycle fields:

`producer_state | delivery_state | pickup_state | semantic_acceptance_state | integration_state | currentness`

## Retirement condition

Q07 closes for this sampled scope because every sampled object is now one of:

- pickup-proven; or
- explicitly classified pickup-unproven.

The broader repository question remains open for future bounded samples.

`SAMPLED_SCOPE_CLOSED_NE_GLOBAL_CENSUS_COMPLETE`

## Rails

`PASS_NE_PICKUP`  
`PRODUCER_SUCCESS_NE_RECEIVER_SUCCESS`  
`DELIVERY_NE_PICKUP`  
`PICKUP_NE_SEMANTIC_ACCEPTANCE`  
`READPROOF_NE_INTEGRATION`  
`SAMPLED_SCOPE_CLOSED_NE_GLOBAL_CENSUS_COMPLETE`  
`VALIDATION_IS_NOT_ACCEPTANCE`
