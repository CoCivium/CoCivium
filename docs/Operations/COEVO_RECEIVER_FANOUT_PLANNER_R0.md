# CoEvoReceiverFanoutPlanner R0

**State:** `PUBLIC_CANDIDATE__RECEIVER_RELATIVE_ROUTE_PLAN__ZERO_TARGET_EFFECTS`

## Purpose

Turn bounded CoEvoDelta+ objects into two coordinated candidate projections:

1. **repository receiver routes** from the shared evolution-domain lanes and repo-role map;
2. **session-profile subscription proposals** from CoSessionSubscription+ HOT/WARM/DIGEST relations.

This is the missing fan-out planning rung after CoSession projection -> CoEvoDelta compilation.

It does not write target repositories, push provider sessions, claim receiver pickup, or bind RickBar runtime.

`ROUTE_PLAN_NE_TARGET_MUTATION`  
`PROFILE_DELIVERY_NE_SESSION_PICKUP`

## Inputs

Reference implementation:

`scripts/CoEvoReceiverFanoutPlanner.py`

Machine output contract:

`schemas/coevo-fanout-plan-v0.1.schema.json`

Normal inputs:

- compiled CoEvoDelta v0.1/v0.2 compatible objects;
- `ai/evolution-lanes.json`;
- `ai/repo-role-map.json`;
- `ai/session-subscription-profiles.json`;
- optional exact receiver-head map;
- optional bound source-current head.

The planner reads those registries as bounded policy inputs. It does not treat repository names as ontology or subscription as authority.

## Repository receiver planning

For each CoEvoDelta, R0:

- normalizes known domain aliases;
- gathers candidate receivers from the domain registry;
- deduplicates cross-domain receiver overlap;
- binds receiver visibility and roles;
- holds public targets when confidentiality is not `PUBLIC`;
- holds public targets unless `public_safety=PUBLIC_SAFE`;
- preserves `EFFECT_GATED` as a downstream effect gate without pretending route planning itself needs human authority;
- requires target-head currentness before any later write;
- surfaces unmapped domains as evolution-lane debt rather than inventing a repository.

A receiver-head map can prove target currentness for the plan. It still does not authorize the write.

## Session-profile planning

For each CoEvoDelta and subscription profile:

- HOT -> `CURRENT_DELTA_PACKET`
- WARM -> `DEPENDENCY_OR_RELEVANCE_PACKET`
- DIGEST -> `COMPACT_DIGEST_ONLY`
- SLEEP -> counted only; no bulky per-delta sleep object is emitted.

Profile proposals are **interest/currentness relations only**.

They carry:

`PROFILE_INTEREST_ONLY__INSTANCE_UNBOUND`

An actual session delivery still requires a bound receiver instance and currentness cursor. Non-public material additionally requires a proven confidentiality capability.

`PROFILE_NE_SESSION_INSTANCE`  
`SUBSCRIPTION_NE_AUTHORITY`  
`CURRENTNESS_FOR_ALL_NE_CONTENT_FOR_ALL`

No provider-session push occurs in R0.

## RickBar / CoFleet R4 relation

R0 follows the current exception-first RickBar contract.

Routine candidate routes and subscription matches remain hidden.

Foreground triggers are limited to material conditions already recognized by the R4 attention contract, including:

- confidentiality collision;
- material contradiction;
- currentness failure;
- invalid input requiring recovery.

A future effect being `EFFECT_GATED` does **not** by itself become a human blocker during planning. Human authority becomes a blocker only when a currently material transition actually requests the gated effect.

`RICK_NE_HEARTBEAT`  
`EXCEPTION_NE_HUMAN_BLOCKER`

Unmapped-domain debt remains background evolution debt unless it becomes materially blocking.

## Embedded self-test

Run:

`python3 scripts/CoEvoReceiverFanoutPlanner.py --selftest`

The embedded bounded canary verifies:

- 4 input CoEvo deltas;
- 9 repository route proposals;
- 7 HOT/WARM/DIGEST subscription proposals across 5 profiles;
- 1 unmapped-domain debt item;
- 3 RickBar foreground confidentiality routes;
- 0 human blockers;
- zero target mutations, profile deliveries, provider pushes, PRs, publications, pickup claims, or canon changes.

Observed self-test result before landing:

`SELFTEST=PASS_ROUTES_9__SUBSCRIPTIONS_7__FOREGROUND_3__HUMAN_BLOCKERS_0__ZERO_EFFECTS`

Self-test plan SHA-256:

`221E537C5AA430AE54FA939DDFFE19579BE91FEF9EDA0C7C6407BC5A841DABD5`

A separate path-independence canary produced byte-identical output from identical input bytes under different file names, and the resulting plan validated against `coevo-fanout-plan-v0.1.schema.json`.

## Effects

R0 always declares zero:

- target repository mutations;
- profile deliveries executed;
- provider-session pushes;
- branch creation;
- PR creation;
- publication;
- receiver pickup claims;
- canon changes.

## Next gate

`BIND_TARGET_HEADS + BIND_RECEIVER_INSTANCES + REVIEW_HOLDS -> COMPILE_BOUNDED_RECEIVER_PACKETS`

That rung is now implemented by [CoEvoReceiverPacketCompiler R0](COEVO_RECEIVER_PACKET_COMPILER_R0.md), with [receiver-binding schema](../../schemas/coevo-receiver-bindings-v0.1.schema.json), [packet-bundle schema](../../schemas/coevo-receiver-packets-v0.1.schema.json), and [reference compiler](../../scripts/CoEvoReceiverPacketCompiler.py).

The next gate after packet compilation is a proven receiver adapter plus delivery receipt and exact packet readproof. Packet compilation itself still proves no delivery or uptake.

## Rails

`ALL_SESSIONS_CAN_CONTRIBUTE_NE_ALL_SESSIONS_MUTATE_ALL_SURFACES`  
`CURRENTNESS_FOR_ALL_NE_CONTENT_FOR_ALL`  
`SUBSCRIPTION_NE_AUTHORITY`  
`PROFILE_NE_SESSION_INSTANCE`  
`ROUTE_PLAN_NE_TARGET_MUTATION`  
`CANDIDATE_ROUTE_NE_INTEGRATION`  
`DELIVERY_NE_PICKUP`  
`COUNT_NE_GLOBAL_CENSUS`  
`MERGED_NE_CANON`

## Forward reconciliation with CoAllPulseField+

Current main now provides [CoAllPulseField+ R0](../Architecture/COALL_PULSEFIELD_COTIME_R0.md) and [CoPulseSubscriptionRouter R0A](COPULSE_SUBSCRIPTION_ROUTER_R0A.md).

Therefore the `subscription_proposals` emitted by this R0 planner are retained as historical canary/compatibility evidence only. They are no longer the preferred forward session-currentness transport.

Forward route:

`CoEvoDelta+ -> CoEvoToPublicCoPulseProjector R0 -> CoPulseSubscriptionRouter R0A -> receiver packet -> exact receiver readproof -> ACK cursor advance`

The repository-route proposals in this planner remain useful for repository/surface fanout.

`COPULSE_ROUTER_SUPERSEDES_DIRECT_COEVO_SESSION_SUBSCRIPTION_DELIVERY`  
`HISTORICAL_CANARY_NE_ACTIVE_TRANSPORT`
