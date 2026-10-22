# CoLogicalSpawnPlanner R2

**State:** `DETERMINISTIC_LOGICAL_SPAWN_PLANNER__NO_LIVE_MATERIALIZATION`

R2 consumes bounded CoEvoDelta+ objects plus the shared evolution-lane and repository-role registries.

It performs:

- domain validation;
- public/private target collision checks;
- exact payload dedupe, including source, authority, and extension fields;
- donation of equivalent deltas into one logical primary;
- collision-domain grouping and ambiguous-body blocking;
- role election;
- logical CoSpawn contract compilation.

It does **not** start model workers, provider sessions, browser tabs, repository mutations, or effect leases.

## Decision order

`VALIDATE_IDENTITIES -> COMPARE_CLAIM_BODIES -> EXACT_DEDUPE -> LOGICAL_RESERVE`

Live materialization remains R3.

## Fixture result

The synthetic fixture is designed to yield:

- 3 input deltas;
- 3 logical contracts;
- 0 dedupe donations;
- 1 collision group;
- the two public UX observations as separate `LOGICAL_ONLY` contracts;
- the private-to-public CoTheoryAll target as `BLOCKED`.

The UX observations differ in session, time, evidence and annotations. They remain
separate rather than being declared equivalent. The fixture also checks that a
confidentiality collision is refused before any live worker or mutation exists.

## Exact identity and ambiguous claims

Equivalence donation requires the same canonical JSON body in every field except
`delta_id`. Types, absent fields, array order, source references, observations,
authority, receivers, and unknown extension fields all participate. A repeated
identical record identifier produces no self-donation. Reusing an identifier with
a different payload blocks every contract containing that identifier, preserving
the union of validation failures across its occurrences.
Blocked groups emit no equivalence donations, so an ambiguous identifier cannot
leave a usable-looking handoff edge.

The older domain/subject/relation/targets/confidentiality key remains a coarse
review slot. It cannot establish equivalence. Within that slot, differing claim
bodies remain separate and receive `AMBIGUOUS_CLAIM_BODY_REQUIRES_RECONCILIATION`.
Such contracts are `BLOCKED`; the planner does not select an older or newer claim.
Ambiguity here does not prove a logical contradiction: the records may describe
successive states or legitimate alternatives that require an explicit rule.

For this body comparison only, root-level `delta_id`, `session_id`, `observed_at`,
`source_refs`, `confidence`, `tests`, `risks`, and `wake_conditions` are excluded,
and domain/target list ordering is normalized. Those fields still participate in
exact dedupe. Nested fields with these names remain part of the claim body.
Unknown fields are retained by default. The exclusions are a bounded planner
policy: tests, risks and wake conditions are annotations in this implementation,
not enforced execution preconditions.

Source references are opaque bindings. A changed head encoded only inside a
reference remains a separate input but is not automatically blocked by this body
comparison. The planner does not resolve source heads, establish currentness,
check leases, or verify a live receiver. Those require receiver-side verification.

This correction changes dedupe, idempotency and spawn identifiers. Regenerate
bounded logical plans from their pinned inputs; do not infer permission to repeat
previous effects from a changed identifier. Live materialization and adoption
remain separate verification steps.

Run the identity regressions with:

```sh
python -m unittest discover -s tests -p test_logical_spawn_identity.py -v
python scripts/CoLogicalSpawnPlannerWaitlessCanaryR2B.py
```

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
unknown domains, and missing required fields detected by `validate_delta` do not become shadow work merely
because useful work might exist nearby.

`validate_delta` is not a full input schema validator. It does not enforce all
field types, nonempty collections, or whitespace-only values. This identity
repair does not establish that every `LOGICAL_ONLY` input is structurally valid;
a receiver must still validate its inputs before any authorized materialization.

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
