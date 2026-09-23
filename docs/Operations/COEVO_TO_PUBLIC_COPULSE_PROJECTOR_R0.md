# CoEvo -> Public CoPulse Projector R0

**State:** `PUBLIC_CANDIDATE__LOSSLESS_EPISTEMIC_CURRENTNESS_PROJECTION__NO_DELIVERY_NO_ACK`

## Purpose

Project one PUBLIC-safe `CoEvoDelta+` object into one `CoAllPulse+` candidate so the existing CoPulseSubscriptionRouter R0A can handle receiver-specific HOT/WARM/DIGEST currentness.

Forward relation:

`CoEvoDelta+ -> CoPulse projection -> CoPulseSubscriptionRouter R0A -> receiver packet -> exact receiver readproof -> ACK cursor advance`

The projector does not perform receiver selection, delivery, pickup, or ACK advancement.

## Epistemic reconciliation

Current CoPulse v0.1 now exposes the same epistemic classes used by CoEvoDelta+:

`OBSERVED | INFERRED | HYPOTHESIS | PREDICTED | PLANNED | PREFERRED | METAPHORICAL | MYTHIC | HUMOROUS | COUNTERFACTUAL | UNKNOWN`

The projector therefore preserves the source epistemic class exactly.

No `HUMOROUS -> UNKNOWN`, `HYPOTHESIS -> UNKNOWN`, or other lossy coercion is required.

`EPISTEMIC_CLASS_PRESERVED`  
`HUMOUR_NE_EVIDENCE`  
`MYTHIC_PROJECTION_NE_FACTUAL_CLAIM`

## Fail-closed rules

The public projector rejects:

- non-PUBLIC CoEvo objects;
- objects lacking `public_safety=PUBLIC_SAFE`;
- unknown epistemic classes;
- negative cursors;
- multiple source deltas in one R0 invocation.

Private/restricted currentness belongs on private custody paths, not this GitHub-hosted public projection.

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

After the CoPulse epistemic-schema repair, the revised candidate passed:

`SELFTEST=PASS_DETERMINISTIC__EPISTEMIC_CLASS_PRESERVED__NONPUBLIC_AND_UNSAFE_FAIL_CLOSED`

Observed HUMOROUS fixture pulse:

`copulse:coevo:CB1A1AD1E7893A9EE591A937`

Canonical pulse SHA-256:

`98F930B8BF86535100FB3C4F85C141E3FB2617CD63A181A543BD27E973229C64`

Revised candidate script SHA-256:

`74E727F4F6E30B16A5D4DD1EEBCABE6762984EFA131F61C3D9DBDED3C800263C`

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
