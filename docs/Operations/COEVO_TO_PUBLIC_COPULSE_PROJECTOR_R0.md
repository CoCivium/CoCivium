# CoEvo -> Public CoPulse Projector R0

**State:** `PUBLIC_CANDIDATE__EXPLICIT_CURRENTNESS_PROJECTION__NO_DELIVERY_NO_ACK`

## Purpose

Project one PUBLIC-safe `CoEvoDelta+` object into one `CoAllPulse+` candidate so the existing CoPulseSubscriptionRouter R0A can handle receiver-specific HOT/WARM/DIGEST currentness.

This reconciles the earlier CoEvo fanout prototype with the current CoAllPulseField+ architecture:

`CoEvoDelta+ -> CoPulse projection -> CoPulseSubscriptionRouter R0A -> receiver packet -> exact receiver readproof -> ACK cursor advance`

The projector does not perform receiver selection, delivery, pickup, or ACK advancement.

## Fail-closed rules

The public projector rejects:

- non-PUBLIC CoEvo objects;
- objects lacking `public_safety=PUBLIC_SAFE`;
- negative cursors;
- multiple source deltas in one R0 invocation;
- lossy epistemic mapping unless an explicit CoPulse class and projection-loss note are supplied.

CoPulse v0.1 has a smaller epistemic vocabulary than CoEvoDelta+. Therefore:

`INFERRED | HYPOTHESIS | METAPHORICAL | MYTHIC | HUMOROUS`

are never silently flattened into `UNKNOWN` or another class.

The source epistemic class and projection-loss note are preserved in the pulse payload.

`PROJECTION_NE_EQUIVALENCE`  
`HUMOUR_NE_EVIDENCE`

## Explicit temporal bindings

R0 requires the caller to supply:

- `cursor`;
- `recorded_at`;
- `valid_from`.

It does not invent a validity start from observation time.

## Reference implementation

`scripts/CoEvoToPublicCoPulseProjectorR0.py`

Downstream machine schema:

`schemas/coall-pulse-v0.1.schema.json`

Downstream router:

`scripts/CoPulseSubscriptionRouterR0A.py`

## Bounded self-test

Before landing, the exact candidate script passed:

`SELFTEST=PASS_DETERMINISTIC__LOSSY_EPISTEMIC_REQUIRES_EXPLICIT_MAPPING__NONPUBLIC_FAILS_CLOSED`

Observed fixture pulse:

`copulse:coevo:C2AC3875FCBB5DF29030F077`

Canonical pulse SHA-256:

`43D85657910E0707DC08B1F874C4E94173D1B121A52EF7FC5581AEBD49C3ABB4`

Pre-commit candidate script SHA-256:

`9D30663C6FA669BAF2C24722842726140C4771D0A624EA6EF365BDD9B263AF6E`

## Supersession relation

The session-subscription proposals emitted by `CoEvoReceiverFanoutPlanner R0` remain historical canary evidence, but they are no longer the preferred session-currentness transport.

Forward path:

- CoEvo fanout retains repository-route planning;
- CoEvo currentness becomes CoPulse;
- CoPulseSubscriptionRouter R0A performs profile/cursor filtering;
- receiver readproof controls ACK advancement.

`COPULSE_ROUTER_SUPERSEDES_DIRECT_COEVO_SESSION_SUBSCRIPTION_DELIVERY`

## Rails

`PROJECTION_NE_DELIVERY`  
`DELIVERY_NE_PICKUP`  
`CANDIDATE_DELIVERED_CURSOR_NE_ACK_CURSOR`  
`PUBLIC_ROUTER_NE_PRIVATE_BUS`  
`SUBSCRIPTION_NE_AUTHORITY`
