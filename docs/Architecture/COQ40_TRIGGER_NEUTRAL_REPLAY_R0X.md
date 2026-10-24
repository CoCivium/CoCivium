# Q40 Trigger-Neutral Lease / Receipt Replay R0X

**State:** `PASS_BOUNDED_SYNTHETIC_LEASE_RECEIPT_REPLAY__NO_PERSISTENT_TRIGGER`

## Purpose

R0W defined a trigger-neutral local work protocol:

`INBOX -> LEASE -> CONSUMER -> RECEIPT -> DISPOSITION`

R0X executes the next earned proof as a deterministic synthetic replay of the five protocol cases, without installing a scheduler, daemon, service, startup hook, filesystem watcher, or other persistent trigger.

The replay proves protocol state transitions only.

## Cases

1. **Clean claim**
   - valid task
   - no active lease
   - no completion receipt
   - exact task hash matches
   - result: `LEASE_CLAIMED`

2. **Concurrent claim collision**
   - non-expired lease already exists for same idempotency key
   - result: `HOLD_ACTIVE_LEASE`
   - executions: `0`

3. **Stale lease takeover**
   - old lease expired
   - no completion receipt
   - task hash unchanged
   - authority/effect/confidentiality gates revalidated
   - result: `LEASE_TAKEOVER_ELECTED`

4. **Already receipted duplicate wake**
   - matching completion receipt exists for same idempotency key
   - result: `ALREADY_RECEIPTED_NO_EXECUTION`
   - executions: `0`

5. **Identity collision**
   - same task id with changed bytes/hash
   - result: `FAIL_CLOSED_IDENTITY_COLLISION`
   - executions: `0`

## Result

The replay validates:

- one clean lease claim;
- one concurrent-claim HOLD;
- one stale-lease takeover after full revalidation;
- one duplicate wake suppressed by prior receipt;
- one changed-bytes identity collision rejected.

No case permits duplicate deed execution.

No trigger class receives authority from the trigger mechanism itself.

## What this proves

`TRIGGER_NEUTRAL_STATE_MACHINE = PROVEN_SYNTHETIC`

`ONE_ACTIVE_LEASE_PER_IDEMPOTENCY_KEY = PROVEN_SYNTHETIC`

`STALE_LEASE_TAKEOVER_GATES = PROVEN_SYNTHETIC`

`ALREADY_RECEIPTED_DUPLICATE_SUPPRESSION = PROVEN_SYNTHETIC`

`TASK_IDENTITY_COLLISION_FAIL_CLOSED = PROVEN_SYNTHETIC`

## What this does not prove

- autonomous trigger execution;
- persistent local runtime;
- task authenticity/signature;
- receiver semantic acceptance;
- cross-host/site/provider independence;
- provider exit completeness;
- production scheduler/service suitability.

## Next earned rung

The protocol no longer needs another abstract replay.

The next materially stronger proof is **receiver disposition over the emitted receipt contract**, or a one-shot use of the same protocol with an already-authorized nonpersistent trigger surface if one independently exists.

Do not install persistence merely to improve an autonomy score.

## Rails

`TRIGGER_NE_AUTHORITY`  
`LEASE_NE_AUTHORITY`  
`ACTIVE_LEASE_NE_COMPLETED_DEED`  
`STALE_LEASE_NE_FAILED_DEED`  
`DUPLICATE_WAKE_NE_DUPLICATE_EFFECT`  
`RECEIPT_NE_SEMANTIC_ACCEPTANCE`  
`TASK_HASH_NE_SIGNATURE`  
`SYNTHETIC_REPLAY_NE_LIVE_TRIGGER`  
`ONE_SHOT_PROTOCOL_PROOF_NE_PERSISTENT_WORKER`  
`VALIDATION_IS_NOT_ACCEPTANCE`
