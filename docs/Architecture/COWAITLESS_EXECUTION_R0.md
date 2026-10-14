# CoWaitlessExecution+ R0

**State:** `CANDIDATE_PUBLIC_POLICY__NOT_RUNTIME_ADOPTION`

## Rule

`NO_SAFE_WORK_WAITS_FOR_AN_UNRELATED_GATE`

A blocked dependency or held effect is a relation on an edge, not permission to
freeze the whole graph.

## Admission dimensions

Evaluate independently:

`effect_permission x work_permission x authority_currentness x collision_state x confidentiality x recovery_quality x receiver_currentness`

A rollback path may improve recovery quality. It does not create authority.

`ROLLBACK_CAPABLE_NE_AUTHORIZED`

## Work states

- `LOGICAL_ONLY`: bounded eligible logical work; no live embodiment implied.
- `SHADOW`: bounded verification/simulation/evidence work while downstream
  effects remain held and the effect lease is `NONE`.
- `BLOCKED`: the work itself is invalid or unsafe to continue, for example a
  confidentiality collision, unknown domain, malformed contract, or ambiguous
  authority/collision boundary.

`EFFECT_GATED_NE_WORK_BLOCKED`
`SHADOW_WORK_NE_EFFECT_AUTHORITY`
`HELD_EFFECT_NE_HELD_GRAPH`

## Virtual armada

CoVirtualArmada+ is a scheduling relation, not a claim of thousands of live
machines or provider sessions.

Prefer:

`many logical work units -> dedupe/fan-in -> many passive verifiers/watchers -> few elected actuators -> exact receipts`

No clone, model, virtual session, process, or provider tab receives extra
authority because replicas exist.

`VIRTUAL_ARMADA_NE_PROVIDER_TAB_ARMADA`
`VIRTUAL_ARMADA_NE_AUTHORITY_MULTIPLICATION`
`MANY_WATCHERS_ONE_ELECTED_ACTUATOR`

## Beacon and pulse pull

A bootstrap beacon can advertise currentness and durable pointers. CoPulse may
route receiver-relative currentness after a receiver's last ACK cursor. Neither
is a command-authority primitive.

A qualified pull chain is:

`DISCOVER -> BIND_SOURCE_CURRENTNESS -> FILTER_BY_ROLE/SUBSCRIPTION -> READ_EXACT_OBJECT -> RECEIVER_READPROOF -> CLASSIFY_WORK/EFFECT -> EXECUTE_ONLY_WITHIN_AUTHORITY`

`BEACON_NE_AUTHORITY`
`POINTER_NE_ACK`
`DELIVERY_NE_PICKUP`
`PICKUP_NE_INTEGRATION`
`WAKE_REQUIRES_BOUND_MATERIAL_RELATION`

The legacy CoBusMirror CoBeacon remains pointer lineage. It must not override
newer repository-bound currentness or effect authority merely because a client
can fetch it.

## Human gates

A human gate is local to the effect that actually requires it. Independent safe
work continues.

`HUMAN_GATE_NE_GLOBAL_WAIT`
`BLOCKED_EDGE_NE_BLOCKED_GRAPH`
`WAIT_WITHOUT_WAKE_CONDITION_NE_VALID_PROTOCOL`

## Runtime boundary

This policy does not prove X2, CoBar, CoStead, provider sessions, local models,
or any other receiver currently enforce it. Runtime adoption requires an exact
adapter, current authority, receiver pickup/readproof, and effect-appropriate
acceptance evidence.
