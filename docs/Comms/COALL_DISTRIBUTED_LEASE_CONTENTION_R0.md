# CoAll Distributed Lease Contention R0

**State:** `CANDIDATE__SYNTHETIC_CONTENTION_CANARY__NO_REAL_RESOURCE_EXECUTION`

## Purpose

Once multiple schedulers can see the same eligible resource, eligibility alone is insufficient. Two schedulers may independently conclude that the same capacity is available and both attempt to reserve it.

R0 adds a bounded contention rule:

`ELIGIBLE -> RESERVE -> FENCE -> EXECUTE`

rather than:

`ELIGIBLE -> EVERY_OBSERVER_MAY_EXECUTE`

## Core distinction

A grant may authorize a resource for a class of work. A lease reserves a bounded portion of that resource for one task. A fencing token distinguishes the currently accepted reservation epoch from stale holders.

`ELIGIBILITY_NE_RESERVATION`

`LEASE_ID_NE_CURRENT_FENCE`

`STALE_FENCE_NE_MUTATION_AUTHORITY`

## Exclusive resources

Some resources are exclusive for a task window.

If scheduler A acquires the active lease first, scheduler B MUST receive a contention result rather than a second concurrent lease.

`ONE_EXCLUSIVE_RESOURCE_NE_TWO_ACTIVE_LEASES`

The losing scheduler may wait, choose another eligible resource, or retry only after expiry/release/currentness change.

## Shareable capacity

Shareable resources MAY have multiple active leases only when the sum of reserved capacity remains within the grant ceiling.

`SUM_ACTIVE_RESERVATIONS_LTE_GRANT_CAPACITY`

A scheduler seeing 600 available units while 400 are already leased may reserve at most the remaining 200.

## Fencing

Each accepted reservation receives a monotonically increasing fencing token within the bounded resource-allocation domain.

A later valid lease may supersede an expired/stale holder. Any downstream adapter that supports fenced mutation MUST reject effects carrying an older token than the latest accepted fence.

`NEWER_FENCE_NE_TRUTH`

The fence only orders lease authority for that resource domain. It does not establish semantic truth, governance rank, or universal time.

## Replay and idempotency

A retried reservation request with the same idempotency key MUST return the prior reservation result rather than consume capacity twice.

`IDEMPOTENT_REPLAY_NE_SECOND_ALLOCATION`

## Partition boundary

If two schedulers cannot reach the same authoritative reservation state, R0 does not permit both to self-elect authority.

`NETWORK_PARTITION_NE_DUAL_LEASE_AUTHORITY`

A future distributed implementation would need a proven coordinator/consensus/lease authority or a deliberately partitionable resource model. R0 does not select a consensus algorithm.

## Revocation and expiry

Revoked or expired leases release future eligibility according to the separate revocation policy, while historical receipts remain.

A stale holder with an obsolete fencing token MUST NOT regain authority merely because it becomes reachable again.

`RECONNECTION_NE_LEASE_REVIVAL`

## First safe canary

The synthetic canary proves:

1. an exclusive resource cannot have two active leases;
2. shareable reservations cannot exceed total granted capacity;
3. stale fencing tokens are rejected;
4. idempotent replay does not allocate twice;
5. revocation/expiry releases future capacity without resurrecting stale authority;
6. partitioned schedulers do not both self-elect active authority.

No real compute, storage, network, messaging, device, financial, or public effect is executed.
