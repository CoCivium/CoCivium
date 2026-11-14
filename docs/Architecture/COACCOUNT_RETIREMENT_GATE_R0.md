# CoAccount Retirement Gate R0

**State:** `CANDIDATE_EXIT_GATE__CURRENT_RESULT_HOLD`

## Purpose

The provider-exit work now has enough components that the next useful step is contraction: compile them into one machine-readable retirement decision instead of adding more adjacent doctrine.

R0 answers only:

`IS_ACCOUNT_RETIREMENT_EVIDENCE_SUFFICIENT_NOW?`

It does not close sessions, cancel billing, revoke credentials, delete data, or delete any account.

## Required gates

Account retirement requires all of:

1. `UNIQUE_STATE_CENSUS_COMPLETE`
2. `INDEPENDENT_BOOTSTRAP_PROVEN`
3. `PRIVATE_OFFSITE_CUSTODY_PROVEN`
4. `PUBLIC_BOOTSTRAP_ALTERNATE_PROVEN`
5. `RECEIVER_PICKUP_PROVEN`
6. `CREDENTIAL_INDEPENDENCE_PROVEN`
7. `FAILURE_DOMAIN_DIVERSITY_PROVEN`
8. `HUMAN_RECOVERY_PROVEN`
9. `REVOCATION_AND_BILLING_MAP_COMPLETE`
10. `EXCEPTION_REGISTER_ACCEPTED`
11. `PROVIDER_INDEPENDENT_REASONING_ROUTE_PROVEN`
12. `PRIMARY_GIT_HOST_NOT_REQUIRED_PROVEN`
13. `PRIMARY_LOCAL_SITE_NOT_REQUIRED_PROVEN`

The clean-room reader canary advances orientation portability but does not satisfy the broader gates by itself.

`SELF_CONTAINED_ORIENTATION_NE_ACCOUNT_RETIREMENT_READINESS`

## Current bounded result

At the exact candidate lineage used by this gate:

- self-contained clean-room orientation: proven by CI on the prior exact head;
- provider transcript not required for packet reading: proven for that packet;
- X2 not required for packet reading: proven for that packet;
- repository worktree not required for packet reading: proven for that packet.

Still unproven or incomplete:

- complete unique-state/session census;
- live private offsite custody;
- independent public/bootstrap mirror;
- provider-independent reasoning route;
- credential/billing/ownership map;
- second/third independent failure-domain readproof;
- primary Git host independence;
- primary local-site independence;
- complete provider-data/session drain.

Therefore:

`ACCOUNT_RETIREMENT_STATE = HOLD_NOT_EXIT_READY`

## Why HOLD is progress

The point of the gate is to make the stopping condition explicit.

A HOLD with named unmet predicates is more useful than another persuasive paragraph saying migration "should be fine."

`EXPLICIT_HOLD_NE_FAILURE`

`UNMET_GATE_NE_RESTART_DISCOVERY_EVERYWHERE`

Each missing predicate can now become an independently provable lane.

## Rails

`SELF_CONTAINED_ORIENTATION_NE_ACCOUNT_RETIREMENT_READINESS`  
`CLOSE_SAFE_NE_ACCOUNT_DELETE_SAFE`  
`DRAINED_NE_DELETE_SAFE`  
`HOLD_NOT_EXIT_READY_NE_PERMANENT_DEPENDENCY`  
`EXIT_GATE_PASS_NE_DELETION_AUTHORITY`  
`ACCOUNT_RETIREMENT_REQUIRES_EXPLICIT_AUTHORITY`  
`VALIDATION_IS_NOT_ACCEPTANCE`
