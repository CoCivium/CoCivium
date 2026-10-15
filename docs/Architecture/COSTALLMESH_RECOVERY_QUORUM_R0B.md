# CoStallMesh+ / CoRecoveryQuorum+ R0B

**State:** `CANDIDATE_EVIDENCE_DRIVEN_STALL_RECOVERY__NO_RUNTIME_ACTUATION`

## Purpose

Extend CoVirtualLiveness+ from classification into a bounded recovery policy.

The goal is not to make more things run. It is to prevent silent slow/stalled work from requiring the user to babysit tabs, CLIs, workers, queues, or provider sessions.

## Core rule

`MANY_WATCHERS_ONE_ELECTED_ACTUATOR`

Many passive observers may independently detect slow/stalled conditions. Only one actuator may hold the recovery lease for the same work/effect scope at a time.

## Inputs

Recovery classification should use at least:

`last_heartbeat_at | last_progress_at | durable_receipt | checkpoint | expected_next | lease | receiver_pickup | queue_age | retry_count | successor | recoverability | currentness`

Rails:

`HEARTBEAT_NE_PROGRESS`  
`NO_SIGNAL_NE_DEAD`  
`VISIBLE_NE_LIVE`  
`RECOVERABLE_NE_RUNNING`

## Candidate states

`ACTIVE | SLOW | STALLED | STOPPED | RECOVERING | QUARANTINED | DORMANT | SUPERSEDED | UNKNOWN`

## Recovery ladder

`OBSERVE -> CLASSIFY -> ELECT_ACTUATOR -> ONE_IDEMPOTENT_NUDGE -> BACKOFF -> RECHECK -> SUCCESSOR_FROM_CHECKPOINT -> QUARANTINE -> HUMAN_GATE_IF_MATERIAL`

Rules:

- do not spam provider buttons or restart blindly;
- verify work identity and lease before acting;
- prefer machine-owned APIs/events/checkpoints over UI clicking;
- one nudge per bounded lease;
- require cooldown/backoff before another attempt;
- repeated failure trips a circuit breaker;
- successor/restart does not count as recovered until progress evidence appears.

`RESTART_NE_RECOVERY_PROOF`  
`NUDGE_NE_PROGRESS`  
`RECOVERY_ATTEMPT_NE_RECOVERY_SUCCESS`

## Anti-jam / acceleration

Track useful flow, not raw worker count:

`discovery_rate | execution_rate | proof_rate | receiver_pickup_rate | fanin_rate | retirement_rate | queue_growth | human_attention_debt`

If discovery/execution outruns proof, fan-in, or receiver pickup, the controller should contract:

`DEDUPE -> FANIN -> COMPACT -> RETIRE -> QUIESCE -> RECHECK`

rather than spawn more work.

`MORE_PARALLEL_NE_MORE_PROGRESS`  
`ACCELERATION_NE_UNBOUNDED_CONCURRENCY`  
`QUEUE_GROWTH_CAN_SIGNAL_RECEIVER_STARVATION`

## Receiver momentum

For outreach/sites/nodes/modules/services distinguish:

`READY -> SENT -> DELIVERED -> PICKED_UP -> UNDERSTOOD -> RESPONDED -> INTEGRATED`

`READY_NE_SENT`  
`SENT_NE_DELIVERED`  
`DELIVERY_NE_PICKUP`  
`PICKUP_NE_UNDERSTOOD`  
`UNDERSTOOD_NE_INTEGRATED`

Momentum should be measured by receiver-state advancement, not by producer activity alone.

## UX

Ordinary users should normally see only:

`CoHereNow | material progress | material exceptions | genuine human blockers | receiver/outreach state`

Backend sessions, CLIs, process IDs, leases and recovery mechanics should remain virtual/hidden unless drill-down is useful.

`CLI_NE_PRIMARY_USER_UX`  
`BACKEND_COMPLEXITY_NE_USER_OBLIGATION`  
`USER_WORKSPACE_NE_PROVIDER_SESSION`

## Nonclaims

No watcher daemon, restart service, provider clicking, process killing, public outreach, runtime adoption, authority change, or persistent recovery actuator is created by R0B.

`VALIDATION_IS_NOT_ACCEPTANCE`
