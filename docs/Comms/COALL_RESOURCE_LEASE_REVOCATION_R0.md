# CoAll Resource Lease + Revocation R0

**State:** `SYNTHETIC_LEASE_AND_REVOCATION_CANARY__NO_REAL_RESOURCE_USE_NO_RUNTIME_AUTHORITY`

## Purpose

The resource field can identify resources that are currently eligible for a task. That is still not permission to use them.

R0 adds an explicit lease boundary:

```text
ACTIVE explicit grant
-> task eligibility
-> candidate selection
-> bounded resource lease
-> pre-execution currentness recheck
-> execution authority
-> receipt
```

This canary stops before execution.

`ELIGIBLE_NE_LEASED`

`LEASED_NE_EXECUTED`

## Why a lease exists

A contribution grant may last longer than any one task.

A task lease narrows the grant to one bounded use:

- grant ID and exact grant version;
- task ID;
- resource class and purpose;
- capacity ceiling;
- privacy scope;
- effect ceiling;
- expiry;
- receipt requirement.

The lease is not an ownership transfer.

`LEASE_NE_AUTHORITY_TRANSFER`

## Currentness at execution time

Issuing a lease is not enough.

Immediately before execution, the runtime must re-check that the underlying grant is still current and compatible.

R0 requires:

`CURRENT_GRANT_REQUIRED_AT_EXECUTION`

If the participant revokes the grant after lease issuance but before execution, the old lease becomes invalid for future execution.

`REVOKED_GRANT_INVALIDATES_FUTURE_EXECUTION`

This is the central proof in R0.

## Synthetic sequence

The canary performs only state transitions:

```text
ACTIVE grant
-> eligible
-> lease issued
-> pre-execution check would pass
-> participant revokes grant
-> lease invalidated
-> execution denied
-> new lease denied
```

Real execution count remains exactly zero.

## Negative cases

R0 additionally proves that no lease may become usable when:

- the grant is merely offered;
- the grant is paused;
- the grant is expired;
- the task purpose does not match;
- the requested capacity exceeds the grant;
- the lease references a stale grant version.

## Relation to recommended defaults

A one-click recommended-default acceptance may activate several individually visible grants.

That convenience does not weaken the lease rule.

Every later task still needs to match a current explicit grant.

So the flow is:

```text
recommended defaults preview
-> explicit acceptance
-> individual ACTIVE grants
-> resource-field eligibility
-> task lease
-> currentness recheck
-> bounded execution
```

not:

```text
clicked recommended defaults once
-> indefinite background permission
```

## Revocation semantics

Revocation stops future use for the revoked scope.

It does not pretend that prior legitimate use never occurred.

`REVOKED_NE_HISTORY_ERASURE`

A later implementation should preserve prior receipts while blocking new work.

## Current boundary

R0 creates no real resource lease against a participant or device.

It executes no compute, model, storage, network, sensor, financial, private-data, or public-posting effect.

It changes no governance authority.

It proves only the synthetic lease/currentness control law.

## Rails

`ELIGIBLE_NE_LEASED`  
`LEASED_NE_EXECUTED`  
`LEASE_NE_AUTHORITY_TRANSFER`  
`LEASE_REQUIRES_CURRENT_GRANT`  
`CURRENT_GRANT_REQUIRED_AT_EXECUTION`  
`REVOKED_GRANT_INVALIDATES_FUTURE_EXECUTION`  
`REVOKED_NE_HISTORY_ERASURE`  
`STALE_GRANT_VERSION_NE_CURRENT_AUTHORITY`  
`CAPACITY_NE_PERMISSION`  
`RESOURCE_USE_REQUIRES_RECEIPT`  
`VALIDATION_IS_NOT_ACCEPTANCE`
