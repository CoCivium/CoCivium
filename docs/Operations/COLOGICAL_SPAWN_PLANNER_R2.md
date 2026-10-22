# CoLogicalSpawnPlanner R2

**State:** `DETERMINISTIC_LOGICAL_SPAWN_PLANNER__NO_LIVE_MATERIALIZATION`

R2 consumes bounded CoEvoDelta+ objects plus the shared evolution-lane and repository-role registries.

It performs:

- required-core type, enum, timestamp and domain validation;
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

Run the identity and input-boundary regressions with:

```sh
python -m unittest discover -s tests -p 'test_logical_spawn_*.py' -v
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

### Required-core input boundary

`validate_delta` checks the required core shared by the v0.1 compatibility anchor
and the v0.2 union candidate. Scalar fields must be actual nonblank strings.
The three required arrays must contain strings; `domain` must contain at least
one known domain. Empty `source_refs` and `target_surfaces` remain permitted by
the anchor schema. Their string items may be empty: presence of a string binding
does not establish usable evidence or a reachable target. The canonical
epistemic, mutation and confidentiality enums are checked without case folding.
Authority remains a free string, never an authority grant.

The nonblank scalar rule is an operational planner guard, stricter than schema
`minLength: 1` (and the schema's unconstrained authority string). The timestamp
check accepts a bounded RFC 3339 form: full calendar date, `T`/`t`, hours/minutes/
seconds, optional decimal fraction, and `Z`/`z` or a numeric `+/-HH:MM` zone.
Calendar-invalid dates, absent zones, year 0000 and leap seconds are held for
review. Exact original timestamp text stays in payload hashes. A valid timestamp
does not establish freshness, chronology, or truth.

Malformed records produce `BLOCKED` diagnostics without coercing a scalar into
an array or interrupting unrelated valid work. Invalid IDs receive deterministic
`INVALID_DELTA_ID:<raw-payload-hash>` references, prefixed with underscores if
needed to avoid a caller-supplied ID. They are isolated from normal equivalence
dedupe, so `false` and `0` cannot alias the valid strings `"False"` and `"0"`.
These references identify a diagnostic record; they do not repair its identity.
All raw fields, including malformed values and unknown extensions, remain in
the identity basis. Existing valid input identities and output plans are unchanged.

Blocked contract projections use only string items from actual arrays and
explicit `INVALID_<FIELD>` placeholders for invalid required scalar displays;
invalid timestamps use `INVALID_OBSERVED_AT`, invalid confidentiality projects
as `UNKNOWN`, and invalid mutation classes project as an empty effect list.
The original input is never rewritten. Placeholders do not identify verified
parents, authority or receivers. Budgets and effect leases remain zero/none,
and blocked groups cannot emit equivalence donations.

This is an extension-preserving **core planner profile**, not complete validation
against either schema. Optional fields, union-only conditional requirements,
source-head resolution, source truth, receiver pickup and effect authorization
remain separate checks. A receiver must validate its applicable full profile
before any authorized materialization.

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
