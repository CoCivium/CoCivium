# CoAll Resource Failover + Resume R0

**State:** `CANDIDATE__SYNTHETIC_FAILOVER_CANARY__NO_REAL_RESOURCE_EXECUTION`

## Purpose

A leased resource may fail after producing a valid checkpoint.

R0 defines a bounded continuation rule for moving the unfinished task to a different eligible resource without pretending that resource identity, lease authority, or stale fencing state transfers with it.

This profile reuses the existing CoSubstrateField translation vocabulary, especially `reconstructs_from`, `preserves_invariant_across`, `requires_adapter`, `incompatible_with`, and `bounded_by`.

`RESOURCE_FAILOVER_PROFILE_NE_NEW_SUBSTRATE_ONTOLOGY`

## Continuation chain

```text
source active lease
-> bounded checkpoint + receipt
-> source failure
-> source lease no longer executable
-> discover independently granted compatible replacement
-> verify reconstruction requirements
-> issue NEW replacement lease
-> issue NEW fencing token
-> reconstruct from checkpoint
-> verify invariants
-> resume only remaining work
-> emit continuation receipt
```

A replacement resource is a successor execution carrier, not the same resource instance.

`FAILOVER_NE_IDENTICAL_RESOURCE`

`CHECKPOINT_NE_LEASE_TRANSFER`

## Authority

The failed source resource's authority does not transfer to the replacement.

The replacement must have its own current grant covering the task and must receive its own bounded lease.

`SOURCE_AUTHORITY_NE_SUCCESSOR_AUTHORITY`

`SHARED_TASK_NE_SHARED_LEASE`

`FAILOVER_NE_AUTHORITY_INHERITANCE`

## Fencing

A resumed execution receives a fencing token newer than the failed/stale holder.

Any late effect from the old resource carrying the stale token MUST be rejected.

`RESUME_REQUIRES_NEW_FENCE`

`FAILED_RESOURCE_RECONNECT_NE_OLD_FENCE_REVIVAL`

## Checkpoint and provenance

A replacement may resume only from a checkpoint whose provenance and declared invariants are verified.

The checkpoint MUST bind:

- task ID;
- source resource ID;
- source lease ID;
- source fencing token;
- completed work units;
- remaining work;
- semantic/state digest;
- required invariants;
- authority/effect ceiling;
- privacy class;
- receipt/provenance refs.

`CHECKPOINT_BYTES_NE_TRUSTED_CHECKPOINT`

`CHECKPOINT_PROVENANCE_REQUIRED_FOR_RESUME`

## Compatibility

A replacement may be:

- directly compatible;
- compatible through an explicitly bound adapter;
- incompatible;
- unknown.

Unknown or incompatible replacements do not self-elect continuation.

`AVAILABLE_REPLACEMENT_NE_COMPATIBLE_REPLACEMENT`

`UNKNOWN_COMPATIBILITY_NE_RESUME_PERMISSION`

## Double execution

Once a successor lease/fence is active, the failed predecessor must not resume the same remaining work merely because it reconnects.

`ONE_REMAINING_WORK_RANGE_NE_TWO_ACTIVE_EXECUTORS`

Historical completed work remains valid where its receipts remain valid.

## First safe canary

The synthetic canary proves:

1. compatible independently granted replacement resumes from a valid checkpoint;
2. replacement receives a new lease and higher fence;
3. predecessor authority and fence do not transfer;
4. stale predecessor reconnect is rejected;
5. incompatible or ungranted replacement is held;
6. missing checkpoint provenance blocks resume;
7. only remaining work is resumed;
8. completed source history remains preserved.

No real resource, device, model, storage, network, messaging, financial, or public effect is executed.
