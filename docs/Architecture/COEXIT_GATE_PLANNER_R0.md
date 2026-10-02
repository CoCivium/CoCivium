# CoExitGate Planner R0

**State:** `CANDIDATE_EXIT_GATE_PLANNER__NO_DESTRUCTIVE_EFFECTS`

## Purpose

The provider-exit branch now has enough evidence that the next problem is orchestration, not more doctrine.

R0 reads the account-retirement gate and classifies each unsatisfied predicate by the kind of capability needed to prove it:

- `GITHUB_ONLY`
- `LIVE_LOCAL_OR_NODE_ROUTE`
- `INDEPENDENT_FAILURE_DOMAIN`
- `PROVIDER_ACCOUNT_CENSUS`
- `HUMAN_AUTHORITY_OR_ACCOUNT_OWNER`
- `MULTI_SURFACE_COMPOSITE`

It then elects the highest-value **currently actionable** proof lane without pretending blocked lanes are complete.

`UNMET_GATE_NE_SAME_KIND_OF_WORK`

`BLOCKED_GATE_NE_RETRY_FOREVER`

## Current classification

The current retirement gate has four satisfied predicates and nine unsatisfied predicates.

The remaining predicates are not all solvable from one GitHub session:

- complete unique-state census needs provider/account/session inventory;
- private offsite custody needs an independent failure domain;
- alternate public bootstrap needs a second host or equivalent export/custody route;
- credential independence needs ownership/credential mapping;
- failure-domain diversity needs at least one non-GitHub/non-local proof;
- billing/revocation map needs account-owner evidence;
- provider-independent reasoning needs a live non-provider model/worker route;
- primary Git-host independence needs a second host/export proof;
- primary local-site independence needs a live alternate execution/custody route.

Therefore the planner must be able to emit `HOLD_ROUTE_UNAVAILABLE` instead of manufacturing work that cannot satisfy the gate.

## Election rule

Prefer:

1. a proof that closes a retirement gate;
2. then a proof that unlocks several other gates;
3. then a proof that reduces dependency pressure;
4. then a preparatory artifact only when it has a named receiver and later proof path.

Do not add more adjacent architecture merely because the main lane is blocked.

`PREPARATION_NE_GATE_CLOSURE`

`DOC_ADDED_NE_DEPENDENCY_REDUCED`

## Current elected lane

Under currently evidenced capabilities, no unsatisfied retirement predicate can be honestly closed by GitHub-only work.

The planner therefore elects:

`NEXT = HOLD_FOR_INDEPENDENT_ROUTE_OR_ACCOUNT_CENSUS`

with two wake families:

- `LIVE_NON_PROVIDER_ROUTE_AVAILABLE`
- `ACCOUNT_OR_SESSION_CENSUS_ROUTE_AVAILABLE`

This is a productive HOLD, because it prevents another layer of decorative migration paperwork.

## Rails

`UNMET_GATE_NE_SAME_KIND_OF_WORK`  
`BLOCKED_GATE_NE_RETRY_FOREVER`  
`PREPARATION_NE_GATE_CLOSURE`  
`DOC_ADDED_NE_DEPENDENCY_REDUCED`  
`GITHUB_ONLY_NE_FAILURE_DOMAIN_INDEPENDENCE`  
`HOLD_ROUTE_UNAVAILABLE_NE_PROJECT_STALLED`  
`EXIT_GATE_PASS_NE_DELETION_AUTHORITY`  
`VALIDATION_IS_NOT_ACCEPTANCE`
