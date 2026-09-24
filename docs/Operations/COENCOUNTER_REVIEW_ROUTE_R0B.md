# CoEncounter independent review + Open Relation routing R0B

**State:** `IMPLEMENTATION_CANDIDATE__EXECUTION_EVIDENCE_REQUIRED`

R0B follows the bounded R0A CoEncounterYield proof.

It tests two distinct things without silently conflating them:

1. independent receivers may inspect the same exact encounter-yield fixture;
2. an OPEN relation may produce a **match candidate** only when explicit capability, interest, consent, authority, cost, and currentness gates all pass.

The matching relation is deliberately:

`open relation x available capability x interest x consent x authority x cost x currentness -> bounded candidate deed`

A match is not an assignment.

`MATCH_NE_ASSIGNMENT_AUTHORITY`

## Fixture

Three receiver processes inspect the same exact R0A encounter fixture:

- a current, capable, interested, consenting, low-cost CoUX receiver;
- a current/capable receiver whose cost exceeds the bounded policy;
- a capable/low-cost receiver whose currentness is stale.

Expected result:

- first receiver -> `MATCH_CANDIDATE`;
- second -> `HELD(cost_ok=false)`;
- third -> `HELD(currentness_ok=false)`.

All three perform structural review only. Semantic acceptance/truth remains unproven.

## Effect boundary

R0B performs no:

- assignment;
- participant notification;
- repository mutation;
- provider-session mutation;
- authority increase.

The candidate deed is `PROPOSE_OPEN_RELATION_TRANSFORMATION` with `execution_authorized=false`.

## Next

R0C should turn the elected match candidate into an exact receiver packet, require receiver-produced readproof before `PICKED_UP`, and bind any later accepted contribution into CoContributionLineage+ without auto-assignment.

## Rails

`STRUCTURAL_REVIEW_NE_SEMANTIC_ACCEPTANCE`  
`INDEPENDENT_REVIEW_NE_TRUTH`  
`MATCH_NE_ASSIGNMENT_AUTHORITY`  
`AVAILABLE_CAPABILITY_NE_FREE_COMPUTE`  
`ROUTE_CANDIDATE_NE_PICKUP`  
`SENSING_SCALE_NE_AUTHORITY_SCALE`
