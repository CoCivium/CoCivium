# CoModel substrate-light multi-embodiment branch/fan-in R0

**State:** `SYNTHETIC_MULTI_EMBODIMENT_BRANCH_FANIN__NO_RUNTIME_NO_CANON_NO_AUTHORITY_CHANGE`

## Purpose

Prove the next implication of substrate-light identity:

> one logical work lane may temporarily branch into multiple embodiments without becoming multiple logical identities, and may fan back in without erasing disagreement or replaying completed work.

This R0 is synthetic. It does not run multiple real models.

## Shape

```text
one logical lane
   |
   +-> risk-minimizer embodiment
   +-> option-explorer embodiment
   +-> proof-verifier embodiment
   |
   v
exact branch receipts
   |
   v
fanin
   +-> preserve shared assertions
   +-> preserve unique branch claims
   +-> preserve conflicting decision candidates
   +-> elect no winner
   +-> continue one logical lane
```

All three embodiments inherit the same:

- logical lane ID;
- completed-step boundary;
- authority ceiling;
- confidentiality;
- effect ceiling;
- candidate head.

Each gets a distinct embodiment ID, lens, route class and **synthetic** failure-domain label.

The labels do not prove physical independence.

`SYNTHETIC_FAILURE_DOMAIN_LABEL_NE_PHYSICAL_INDEPENDENCE`

## Disagreement test

The three branches deliberately disagree on:

`DEFAULT_PARALLEL_EMBODIMENT_POLICY`

Candidates:

- `SINGLE_BY_DEFAULT`
- `ADAPTIVE_PARALLEL_ALLOWED`
- `HOLD_UNTIL_MEASURED_BENEFIT`

Fan-in must retain all three with exact branch provenance.

It must not select:

- newest branch;
- majority branch;
- lexicographically first branch;
- allegedly smartest branch;
- whatever happened to finish fastest.

Humans have invented enough electoral systems for software to improvise another one accidentally.

The resulting next gate is:

`EXTERNAL_CRITERION_OR_MEASURED_BENEFIT_REQUIRED_BEFORE_POLICY_ELECTION`

## Continuity test

Fan-in must preserve:

`continuation_lane_id == original logical_lane_id`

and:

`replayed_completed_step_ids == []`

Thus route/embodiment branching is downstream of logical work identity.

`LOGICAL_LANE_NE_EXECUTION_ROUTE`

## Relation to existing donors

This R0 contracts with:

- provider-neutral route election;
- CoParticipantEdge / CoOomph logical-parallelity doctrine;
- substrate-light embodiment election.

It does not create another generic orchestration ontology.

## What this unlocks later

If the bounded pattern survives real-model tests, later forms may include:

- challenger / verifier / synthesizer model ensembles;
- privacy-separated local and provider branches;
- different model families behind one work identity;
- branch-specific capability specialists;
- failure-domain-diverse replicas;
- bounded independent review before integration;
- measured-benefit routing of parallel embodiments;
- aggressive retirement of branches after durable fan-in.

## Rails

`MULTIPLE_EMBODIMENTS_NE_MULTIPLE_IDENTITIES`  
`FANIN_NE_CONSENSUS`  
`FANIN_NE_TRUTH`  
`BRANCH_COUNT_NE_EVIDENCE_WEIGHT`  
`DISAGREEMENT_NE_FAILURE`  
`ROUTE_CHANGE_NE_REPLAY_COMPLETED_WORK`  
`LOGICAL_LANE_NE_EXECUTION_ROUTE`  
`SYNTHETIC_FAILURE_DOMAIN_LABEL_NE_PHYSICAL_INDEPENDENCE`  
`MULTI_EMBODIMENT_CANARY_NE_RUNTIME_SCHEDULER`  
`VALIDATION_IS_NOT_ACCEPTANCE`
