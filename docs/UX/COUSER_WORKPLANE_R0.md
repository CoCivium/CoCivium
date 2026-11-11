# CoUserWorkplane+ / Invisible Session Fabric R0

**State:** `CANDIDATE_UX_CONTROL_CONTRACT__NO_RUNTIME_BINDING`

## CoHereNow

The user should not manage provider tabs, session fleets, worker queues, or model embodiments.

The mature default is:

```text
user
  -> CoBar / workspace / module
  -> CoHereNow + Meaning + exceptions + outbound momentum
  -> hidden logical-session fabric
  -> temporary machine embodiments only when useful
```

Provider sessions, virtual sessions, model runtimes, CI jobs, local workers, mirrors and shadow workers are implementation details unless a material exception requires drill-down.

`USER_WORKSPACE_NE_PROVIDER_SESSION`

`VIRTUAL_SESSION_NE_PROVIDER_TAB`

`RICK_NE_HEARTBEAT`

## Almost all sessions should disappear from the user's face

A user-visible session is justified only when conversation itself is the product or when a human decision genuinely benefits from a conversational surface.

Everything else should prefer:

- virtual-session records;
- event/pulse currentness;
- task objects;
- bounded workers;
- watcher predicates;
- dormant reconstructible contexts;
- background CI/service jobs;
- mirrors and replicas;
- exception-driven materialization.

The target is not zero material sessions. The target is **zero routine session-management burden**.

## CoBar is the observer/control projection

A user's CoBar may remain persistently visible because it is not one backend session. It is a projection over:

- active workspaces;
- current modules;
- outbound work/momentum;
- blockers;
- material exceptions;
- currentness;
- pressure/flow health;
- effect leases;
- evidence drill-down.

Raw session IDs and receipts stay behind drill-down.

## No manual cycling doctrine

Routine work must not require the user to:

- wake old chats;
- type heartbeat prompts;
- cycle tabs to keep workers alive;
- compare stale session titles;
- decide which model/provider should continue;
- relay artifacts between known surfaces;
- repeatedly ask whether work is stalled.

The system should wake, route, checkpoint, fan in, sleep and recover through machine-owned currentness and bounded receiver contracts.

A human turn is for intent, judgment, creativity, authority or exception handling.

## Flow assurance, not activity theatre

The user should not be reassured by worker count.

The system should measure whether work is actually moving:

```text
currentness age
queue age
fan-in drain rate
receiver backlog
proof debt
collision pressure
materialization load
outbound delivery state
```

If discovery creates work faster than fan-in can compact and receivers can consume it, the system should contract discovery, dedupe, fan in, cool subscriptions and retire descendant-satisfied work.

`WORKER_COUNT_NE_PROGRESS`

`FLOW_HEALTH_NE_ACTIVITY_COUNT`

`MASSIVE_PARALLELITY_NE_MASSIVE_SIMULTANEOUS_MATERIALIZATION`

## Stalls should become exceptions automatically

Examples:

- currentness older than its bound;
- queue age beyond SLA;
- zero fan-in drain while backlog grows;
- receiver pickup failure;
- delivery stuck without proof;
- effect lease contention;
- repeated collision/rollback;
- provider/local route unavailable with no safe alternate;
- target audience unbound.

These should raise one material exception in CoBar rather than requiring the user to inspect dozens of invisible workers.

## "Ready" must mean something useful

Human UX suffers when software says **Ready** but still expects the human to transport or send the thing.

Candidate presentation vocabulary:

```text
PREPARED   = artifact/work is composed but not routed
QUEUED     = machine-owned send is bound but not yet sent
SENT       = outbound send/effect attempt acknowledged
DELIVERED  = reached elected destination/surface
PICKED_UP  = receiver exact-object readproof exists
INTEGRATED = receiver accepted it into a working baseline
```

For user-facing surfaces, `READY` may be used only when:

- no human transport is required;
- the machine-owned next step is already bound;
- the work is at least SENT or durably available to the elected receiver.

Thus a draft waiting for Rick to copy/paste is **PREPARED**, not READY.

`READY_NE_PREPARED`

Still:

`SENT_NE_DELIVERED`

`DELIVERY_NE_PICKUP`

## Outbound momentum

Sites, nodes, services, modules and outreach objects should carry a compact momentum envelope:

```text
object
target audience / receiver
current delivery state
last proof timestamp
next machine-owned action
stall predicate / SLA
alternate route
effect authority
evidence pointer
```

This permits CoBar to answer the question that actually matters:

> Is it moving toward the intended receiver, or is it stuck?

A SENT object is moving, but that does not prove the audience read or accepted it.

`OUTBOUND_MOMENTUM_NE_AUDIENCE_PICKUP`

## Massive parallelism without user anxiety

Logical work may be very broad while physical embodiment remains adaptive.

The system should parallelize where it increases verified yield, but apply backpressure when:

- receiver backlog rises;
- fan-in lags discovery;
- proof debt grows;
- collisions increase;
- provider pressure rises;
- attention debt rises.

The user should see only the resulting health state and material exceptions.

## Sites / nodes / services / CoModules

The same workplane should unify:

- CoBar;
- CoModules;
- public sites;
- private nodes;
- local/open-model workers;
- provider workers;
- CI/services;
- outreach;
- correspondence fronts;
- mirrors;
- watchers;
- emergency/disaster-response modules.

They are not separate kingdoms. They are projections and participants in one relational work fabric with different authority and confidentiality envelopes.

## Current boundary

Existing architecture already supports much of this semantically:

- CoVirtualSession+ says many virtual sessions -> few embodiments -> fewer user-visible sessions.
- CoSessionAutocycle+ says routine human heartbeat is not required.
- RickBar R4 says the user should interact with work, fronts, exceptions and currentness rather than provider-session walls.

What remains unproven is the live runtime binding that actually hides and orchestrates all of these surfaces end to end.

This R0 therefore proves a **policy/UX canary only**, not deployment.

## Rails

`USER_WORKSPACE_NE_PROVIDER_SESSION`  
`VIRTUAL_SESSION_NE_PROVIDER_TAB`  
`RICK_NE_HEARTBEAT`  
`SUCCESS_NE_NOTIFICATION_REQUIRED`  
`READY_NE_PREPARED`  
`SENT_NE_DELIVERED`  
`DELIVERY_NE_PICKUP`  
`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`  
`MASSIVE_PARALLELITY_NE_MASSIVE_SIMULTANEOUS_MATERIALIZATION`  
`WORKER_COUNT_NE_PROGRESS`  
`FLOW_HEALTH_NE_ACTIVITY_COUNT`  
`OUTBOUND_MOMENTUM_NE_AUDIENCE_PICKUP`  
`RICKBAR_FIRST__RECEIPTS_BEHIND`  
`VALIDATION_IS_NOT_ACCEPTANCE`

## NextSafeAction

The next proof should bind one real CoBar/CoFleet receiver to this projection and demonstrate:

```text
many hidden logical sessions
+ one visible user workplane
+ automatic stall detection
+ no routine human heartbeat
+ evidence drill-down on demand
```

without claiming a global fleet census.
