# CoAll+ Coordination Fan-Out + Recovery R0

**State:** BOUNDED_SYNTHETIC_COORDINATION_PROOF__NO_EXTERNAL_BROADCAST__NO_GLOBAL_SYNC  
**Observed:** 2026-10-27  
**Tracker:** GitHub issue #317

## Purpose

Close the first executable coordination gap in issue #317:

- inventory test destinations;
- define one canonical task packet;
- route one synthetic input to two destinations;
- record per-destination attempt/ack receipts;
- simulate one destination failure;
- recover without duplicating completed work;
- reconcile one status view;
- reconstruct and continue from a fresh process using the task packet plus durable receipts.

This is deliberately smaller than the surrounding CoAll architecture.

`ONE_BOUNDED_PROOF_BEFORE_SCALE`

## Canonical inputs

- Receiver inventory: `ai/coordination/coall-fanout-r0/receiver-inventory.json`
- Task packet: `ai/coordination/coall-fanout-r0/task-packet.json`
- Runner: `scripts/CoAllFanoutR0.py`

The task packet binds:

- stable task ID;
- source pointer and source version;
- intent;
- scope / permissions;
- forbidden effects;
- owner;
- next action;
- acceptance criteria;
- timestamp;
- state;
- exact two-destination list;
- receiver inventory pointer;
- deterministic runtime path;
- Golden-Learning distinctions.

## Test destinations

### synthetic-local-a

Behavior: `ACK_ALWAYS`

Mechanism: deterministic local JSON projection plus exact receipt.

### synthetic-local-b

Behavior: `FAIL_FIRST_THEN_ACK`

First attempt intentionally emits a `SIMULATED_FAILURE` receipt and leaves the destination recoverable.

A fresh recovery process must retry B and must not redispatch A.

## Other observed routes

The inventory keeps non-canary routes explicit:

- GitHub issue #317 is the evidence tracker, not a dispatch target.
- X2 Remote Desktop Commander is currently unavailable/offline and excluded.
- External mail is excluded from this synthetic-first proof.

This prevents a synthetic coordination pass from becoming an accidental external broadcast.

## Receipt grammar

Each ledger event carries:

- task ID;
- canonical packet SHA-256;
- source pointer/version;
- logical sequence;
- event kind;
- destination;
- attempt number where applicable;
- result;
- detail;
- explicit zero-effect envelope;
- receipt ID derived from the canonical receipt body.

Receipt kinds:

- `QUEUE_CREATED`
- `DISPATCH_ATTEMPT`
- `DISPATCH_FAILURE`
- `DESTINATION_ACK`
- `RECOVERY_START`
- `RECOVERY_SKIP_ALREADY_ACKED`
- `RECOVERY_COMPLETE`

`ATTEMPT_NE_ACK`  
`ACK_NE_RECEIVER_EFFECT`

## Phase 1

Fresh runtime:

```
init
-> dispatch
-> reconcile
```

Expected:

- A: `ACKED`
- B: `RETRY_QUEUED`
- overall: `PARTIAL_RECOVERABLE`

## Phase 2 fresh-process recovery

A separate Python process runs:

```
recover --packet <canonical packet>
```

The packet provides the deterministic runtime location and receiver-inventory pointer.

The recovery process reconstructs destination states from the durable receipt ledger rather than from in-memory state.

Expected:

- A: skip because exact ACK already exists;
- B: second attempt succeeds;
- final overall: `COMPLETE_ACKED_LOCAL`.

## Acceptance proof

PASS requires:

- both destinations ACKED;
- A has exactly one dispatch attempt and one ACK;
- recovery records exactly one skip for A;
- B has exactly two attempts, one simulated failure and one ACK;
- every receipt keeps the same task ID and packet digest;
- recovery start is explicitly receipted as reconstructed from packet + receipts;
- all external-effect counters remain zero;
- final reconciled state is complete.

## Golden-Learning relation

This test carries the cross-cutting requirement recorded on issue #317:

```
SOURCE
-> TASK PACKET
-> ATTEMPT
-> ACK / FAILURE
-> RECOVERY
-> RECONCILIATION
-> ACCEPTANCE
-> NEXT LEARNING
```

Distinctions are preserved:

`ATTEMPT_NE_ACK`  
`ACK_NE_EFFECT`  
`SIMULATED_FAILURE_NE_EXTERNAL_FAILURE`  
`RECOVERY_NE_GLOBAL_SYNC`

## Nonclaims

A PASS does **not** prove:

- external delivery;
- human receiver use;
- cross-device synchronization;
- X2 integration;
- Gmail fan-out;
- background execution;
- production scheduling;
- global CoAll mesh operation;
- CoEx;
- adoption.

It proves the bounded coordination semantics only.

## Lifecycle interpretation

The runtime output is test evidence. It is not automatically a durable receiver landing.

`LOCAL_IS_NOT_LANDED`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`  
`HASHING_IS_NOT_SEMANTIC_INGESTION`  
`DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY`

## Next gate after PASS

Attach the reproducible CI evidence to issue #317 and mark only the criteria actually covered.

Then elect the next smallest missing criterion, rather than expanding architecture by default.
