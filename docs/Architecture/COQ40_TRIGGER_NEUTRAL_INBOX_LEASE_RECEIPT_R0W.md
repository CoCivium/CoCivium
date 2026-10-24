# Q40 Trigger-Neutral Inbox / Lease / Receipt Protocol R0W

**State:** `CANDIDATE_TRIGGER_NEUTRAL_LOCAL_WORK_PROTOCOL__NO_PERSISTENT_TRIGGER_INSTALLED`

## Purpose

R0V proved that X2 can consume a pre-existing machine-readable task, execute one bounded read-only deed, emit a hashed receipt, and exit.

The remaining gap is **how such a task may later be awakened without changing deed semantics or turning the wake mechanism into authority**.

R0W defines a trigger-neutral protocol:

`INBOX -> LEASE -> CONSUMER -> RECEIPT -> DISPOSITION`

The protocol may later be driven by an authorized local scheduler, file event, node message, manual launch, or other trigger surface. None is installed or elected here.

`TRIGGER_MECHANISM_NE_DEED_SEMANTICS`

`TRIGGER_NE_AUTHORITY`

## Objects

### Task envelope

A task carries:

- `task_id`
- `task_sha256`
- `deed_class`
- `authority_ceiling`
- `effect_class`
- `confidentiality`
- `receiver_id`
- `created_at`
- `expires_at`
- `idempotency_key`
- `input_refs`
- `stop_condition`

Inbox presence alone does not authorize execution.

`INBOX_PRESENCE_NE_EXECUTION_PERMISSION`

### Lease

A consumer may claim a bounded lease only after validating the task envelope.

A lease binds:

- `lease_id`
- `task_id`
- `task_sha256`
- `consumer_id`
- `claimed_at`
- `expires_at`
- `authority_ceiling`
- `idempotency_key`

The lease is coordination, not permission inflation.

`LEASE_NE_AUTHORITY`

`LEASE_HELD_NE_DEED_COMPLETED`

### Receipt

A completed bounded deed emits a receipt binding:

- `receipt_id`
- `task_id`
- `task_sha256`
- `lease_id`
- `consumer_id`
- `output_sha256`
- `completed_at`
- `disposition`
- `effect_counts`
- `nonclaims`

A receipt proves the stated bounded transition only.

`RECEIPT_NE_SEMANTIC_ACCEPTANCE`

`HASHED_RECEIPT_NE_SIGNATURE`

## State machine

`TASK_AVAILABLE`

-> validate identity / authority / expiry / effect class

-> `LEASE_CLAIMED`

-> exact task hash re-read

-> `DEED_EXECUTED | HOLD_FAIL_CLOSED`

-> `RECEIPT_EMITTED`

-> receiver disposition

-> `LEASE_RELEASED_OR_EXPIRED`

No state silently skips the exact task hash re-read.

## Concurrency / anti-storm

The protocol follows:

`MANY_WATCHERS_ONE_ELECTED_ACTUATOR`

Only one non-expired lease may exist for the same idempotency key.

A second consumer encountering a current lease must HOLD rather than execute.

A stale lease may be taken over only when:

- the old lease is expired;
- no completion receipt exists for the same idempotency key;
- the task hash still matches;
- the new consumer revalidates authority/effect/confidentiality/currentness gates.

`STALE_LEASE_NE_FAILED_DEED`

`LEASE_EXPIRY_NE_COMPLETION`

`DUPLICATE_TRIGGER_NE_DUPLICATE_EFFECT`

## Idempotency

The deed-level idempotency key binds the semantic work unit, not merely the trigger event.

Repeated wake signals for the same work unit must converge on the same key.

If a completed receipt exists for that key, a later trigger should normally classify:

`ALREADY_RECEIPTED -> NO_EXECUTION`

unless the task explicitly carries a new version/currentness identity.

`NEW_TRIGGER_NE_NEW_WORK`

`SAME_TASK_ID_WITH_CHANGED_BYTES -> FAIL_CLOSED_IDENTITY_COLLISION`

## Trigger neutrality

Allowed future trigger classes may include:

- explicit manual launch;
- authorized local scheduler;
- filesystem/event watcher;
- local node/queue event;
- recovery replay after stale lease expiry.

R0W does not prefer one.

The deed contract, task identity, lease rules and receipt format remain the same across trigger classes.

`MANUAL_TRIGGER_NE_HUMAN_TRANSPORT_REQUIREMENT`

`SCHEDULER_NE_AUTHORITY_ROOT`

`WATCHER_NE_ACTUATOR`

## Bounded protocol cases

R0W validates five cases:

1. **Clean claim**  
   Valid task, no existing lease/receipt -> one lease may be claimed.

2. **Concurrent claim collision**  
   Valid non-expired lease already exists -> second consumer HOLDs.

3. **Stale lease takeover**  
   Expired lease, no receipt, exact task hash unchanged -> takeover may be elected after full revalidation.

4. **Already receipted duplicate wake**  
   Matching completion receipt exists -> no second execution.

5. **Identity collision**  
   Same task id but changed bytes/hash -> FAIL CLOSED.

These cases prove protocol logic only, not a persistent runtime.

## What this advances

R0W makes the wake mechanism substitutable.

That matters for provider exit because a later local scheduler or CoNode trigger can awaken the same consumer without changing the deed contract.

It does **not** yet prove:

- an autonomous trigger actually fired;
- a daemon/service/scheduled task is installed;
- signed task authenticity;
- receiver semantic acceptance;
- cross-host/site/provider independence;
- provider exit completion.

## Next earned rung

The next safe proof is a **one-shot synthetic lease/receipt replay** that exercises the five protocol cases without installing persistence.

Only after that passes should any real trigger surface be considered, and any persistent scheduler/service/startup mutation still requires separate authority and evidence.

## Rails

`TRIGGER_MECHANISM_NE_DEED_SEMANTICS`  
`TRIGGER_NE_AUTHORITY`  
`INBOX_PRESENCE_NE_EXECUTION_PERMISSION`  
`LEASE_NE_AUTHORITY`  
`LEASE_HELD_NE_DEED_COMPLETED`  
`STALE_LEASE_NE_FAILED_DEED`  
`LEASE_EXPIRY_NE_COMPLETION`  
`DUPLICATE_TRIGGER_NE_DUPLICATE_EFFECT`  
`NEW_TRIGGER_NE_NEW_WORK`  
`WATCHER_NE_ACTUATOR`  
`HASHED_RECEIPT_NE_SIGNATURE`  
`RECEIPT_NE_SEMANTIC_ACCEPTANCE`  
`ONE_SHOT_PROTOCOL_PROOF_NE_PERSISTENT_WORKER`  
`VALIDATION_IS_NOT_ACCEPTANCE`
