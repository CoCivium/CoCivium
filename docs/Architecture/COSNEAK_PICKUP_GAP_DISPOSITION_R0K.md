# CoSneak+ Pickup-Gap Disposition R0K

**State:** `PASS_BOUNDED_PICKUP_GAP_DISPOSITION__DIRECT_PICKUP_NOT_RETROACTIVELY_INVENTED`

## Purpose

R0J exact-bound three sampled PASS objects whose producer-side claims passed while direct receiver pickup for those exact results remained unproven.

R0K asks the next useful question:

> Is each pickup gap still actionable, resolved by a successor relation, or merely a historical nonclaim that should remain explicit?

The answer must preserve the difference between **direct pickup of the original result** and **successor consumption / later lifecycle advancement**.

`SUCCESSOR_ADVANCEMENT_NE_RETROACTIVE_PICKUP`

## 1. CoEncounter R0B independent review

Source:

`docs/Operations/proofs/coencounter-r0b-container-pass-20260924.json`

R0B explicitly states:

`receiver_pickup_of_match_packet = UNPROVEN`

and elects next:

`R0C_EXACT_MATCH_PACKET_PICKUP__CONTRIBUTION_LINEAGE_BINDING__NO_AUTO_ASSIGNMENT`

Later CoEncounter R0C/R0C2 evidence proves exact bounded receiver readproof pickup for the derived match packet.

Disposition:

`SUCCESSOR_CLOSED_NEXT_PICKUP_RUNG__ORIGINAL_R0B_DIRECT_PICKUP_NONCLAIM_REMAINS_HISTORICAL`

Action:

No need to mutate R0B into a stronger claim. Preserve its historical nonclaim and point to the successor proof.

## 2. CoEncounter Yield R0A

Source:

`docs/Operations/proofs/coencounter-yield-r0a-container-pass-20260924.json`

R0A explicitly elects:

`R0B_INDEPENDENT_RECEIVER_REVIEW_OF_ENCOUNTER_YIELD_AND_OPEN_RELATION_ROUTING`

The R0B architecture states that it follows the bounded R0A CoEncounterYield proof. R0C then advances the derived match-packet path to exact receiver pickup.

Disposition:

`SUCCESSOR_LINEAGE_CONSUMED_R0A__DIRECT_PICKUP_OF_R0A_RESULT_STILL_UNPROVEN_AND_NOT_REQUIRED_FOR_ITS_ORIGINAL_CLAIM`

Action:

Keep the original no-pickup nonclaim. The useful relation is successor consumption, not retroactive pickup.

## 3. CoPulse R0F pressure/freshness

Source:

`docs/Operations/proofs/copulse-r0f-container-pass-20260923.json`

R0F proves explicit staleness handling, divergent receiver budgets and exact replay, while preserving:

`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`

Its elected successor is:

`R0G_CAPACITY_SOURCE_PROVENANCE_AND_LIVE_RECEIVER_BINDING_CANARY`

R0G exists and proves source-bound capacity samples tied to live receiver processes plus exact replay and tamper rejection.

However R0G does not retroactively prove direct receiver pickup of the R0F result.

Disposition:

`SUCCESSOR_ADVANCED_RECEIVER_BINDING_AND_PROVENANCE__R0F_DIRECT_PICKUP_REMAINS_UNPROVEN__NO_CURRENT_BLOCKER_UNLESS_R0F_RESULT_REQUIRES_AN_ELECTED_RECEIVER`

Action:

Do not manufacture a readproof for a historical canary merely to make the dashboard greener. If an actual receiver later needs the R0F result, bind that receiver and prove pickup then.

## Result

Three R0J pickup gaps now have explicit dispositions:

- `1` successor closed the specific next pickup rung;
- `1` successor lineage consumed the prior object while direct pickup remained outside the original claim;
- `1` successor advanced a different receiver/provenance dimension while direct pickup remains unproven and currently non-blocking.

No original artifact is rewritten.

No historical nonclaim is erased.

No direct pickup is inferred from successor progress.

## General lifecycle relation

A better lifecycle vocabulary is:

`PRODUCER_PASS`
-> `DELIVERY_CANDIDATE`
-> `DIRECT_PICKUP_PROVEN | DIRECT_PICKUP_UNPROVEN`
-> `SUCCESSOR_CONSUMED | SUCCESSOR_NOT_BOUND`
-> `SEMANTIC_ACCEPTANCE_PROVEN | UNPROVEN`
-> `INTEGRATION_PROVEN | UNPROVEN`

A successor may consume or supersede an object without proving every earlier lifecycle edge.

## CoSneak lesson

The subtle failure is not merely missing pickup.

It is **lifecycle compression**: different transition states being rendered as one green PASS.

Candidate relation:

`COLLAPSED_LIFECYCLE_STATE_HIDES_UNPROVEN_EDGE`

This should become a diagnostic target wherever producer, delivery, pickup, acceptance and integration are collapsed.

## Rails

`SUCCESSOR_ADVANCEMENT_NE_RETROACTIVE_PICKUP`  
`SUCCESSOR_CONSUMPTION_NE_DIRECT_PICKUP`  
`PASS_NE_PICKUP`  
`PICKUP_NE_SEMANTIC_ACCEPTANCE`  
`SEMANTIC_ACCEPTANCE_NE_INTEGRATION`  
`HISTORICAL_NONCLAIM_NE_CURRENT_BLOCKER`  
`NO_RECEIVER_NE_REASON_TO_FABRICATE_PICKUP`  
`COLLAPSED_LIFECYCLE_STATE_HIDES_UNPROVEN_EDGE`  
`VALIDATION_IS_NOT_ACCEPTANCE`
