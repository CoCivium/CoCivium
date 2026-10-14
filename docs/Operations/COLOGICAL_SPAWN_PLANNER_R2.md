# CoLogicalSpawnPlanner R2

**State:** `DETERMINISTIC_LOGICAL_SPAWN_PLANNER__NO_LIVE_MATERIALIZATION`

R2 consumes bounded CoEvoDelta+ objects plus the shared evolution-lane and repository-role registries.

It performs:

- domain validation;
- public/private target collision checks;
- exact deterministic dedupe-key generation;
- donation of equivalent deltas into one logical primary;
- collision-domain grouping;
- role election;
- logical CoSpawn contract compilation.

It does **not** start model workers, provider sessions, browser tabs, repository mutations, or effect leases.

## Decision order

`VALIDATE -> DEDUPE -> DONATE -> COLLISION_GROUP -> LOGICAL_RESERVE`

Live materialization remains R3.

## Fixture result

The synthetic fixture is designed to yield:

- 3 input deltas;
- 2 logical contracts;
- 1 dedupe donation;
- 1 collision group;
- the public UX contract as `LOGICAL_ONLY`;
- the private-to-public CoTheoryAll target as `BLOCKED`.

This checks the important failure mode: useful automation must refuse a confidentiality collision before any live worker or repository mutation exists.

## Rails

`SPAWN_NE_NEW_CHAT`  
`LOGICAL_RESERVE_NE_LIVE_WORKER`  
`DEDUPE_NE_DELETE`  
`CONFIDENTIALITY_COLLISION_NE_AUTO_ROUTE`  
`MODEL_NE_AUTHORITY`


## R2A confidentiality bind

CoSpawn contracts preserve the source delta's confidentiality class explicitly. This is required before any later worker materialization so a private logical task cannot silently default to public.

`CONFIDENTIALITY_MUST_SURVIVE_ROUTING`


## R2B waitless effect/work split

An effect gate is not automatically a work gate.

When a valid delta uses `mutation_class = EFFECT_GATED`, R2B elects a `VERIFIER`
contract with `materialization_state = SHADOW` and `effect_lease = NONE`.
The effect remains held, while bounded read-only verification, simulation,
dependency preparation, contradiction search, and evidence work may continue.

Validation failures remain `BLOCKED`. In particular, confidentiality collisions,
unknown domains, and malformed required fields do not become shadow work merely
because useful work might exist nearby.

`EFFECT_GATED_NE_WORK_BLOCKED`  
`SHADOW_WORK_NE_EFFECT_AUTHORITY`  
`BLOCKED_EDGE_NE_BLOCKED_GRAPH`  
`ROLLBACK_CAPABLE_NE_AUTHORIZED`

### Virtual armada relation

Many logical contracts may exist concurrently without materializing many workers.
Prefer many bounded logical/shadow work units, aggressive dedupe/fan-in, and very
few elected actuators per collision domain.

`VIRTUAL_ARMADA_NE_PROVIDER_TAB_ARMADA`  
`VIRTUAL_ARMADA_NE_AUTHORITY_MULTIPLICATION`  
`MANY_WATCHERS_ONE_ELECTED_ACTUATOR`

### Beacon / pulse boundary

A beacon, bootstrap pointer, or CoPulse currentness object may expose this policy
to a qualified receiver. It does not itself grant effect authority or prove pickup.

`BEACON_NE_AUTHORITY`  
`DELIVERY_NE_PICKUP`  
`PICKUP_NE_INTEGRATION`
