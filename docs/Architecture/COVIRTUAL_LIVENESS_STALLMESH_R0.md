# CoVirtualLiveness+ / CoStallMesh+ R0

**State:** `CANDIDATE_VIRTUAL_LIVENESS_AND_RECOVERY_QUORUM__NO_RUNTIME_ADOPTION`

## Lead

Provider tabs, visible sessions, running processes and heartbeat signals are not reliable definitions of liveness.

CoAll should compute liveness from evidence.

`VISIBLE_NE_LIVE`
`HEARTBEAT_NE_PROGRESS`
`TAB_NE_WORKER`
`SESSION_NE_WORK`

A session may be visible but dead, invisible but recoverable, or stopped while its work continues elsewhere.

## Virtual liveness source

Candidate states:

- `VISIBLE`
- `RESPONSIVE`
- `PROGRESSING`
- `SLOW`
- `STALLED`
- `DORMANT`
- `RECOVERING`
- `SUPERSEDED`
- `STOPPED`
- `UNKNOWN`

A classification should derive from a relation vector such as:

`visibility | responsiveness | last_heartbeat_at | last_progress_at | durable_receipt | checkpoint | expected_next | lease | successor | recoverability | worker/process evidence | currentness`

No single signal is sufficient by default.

## Progress evidence

Heartbeats keep a route observable. They do not prove productive work.

Prefer at least one progress-bearing signal:

- durable receipt/checkpoint changed;
- elected output advanced;
- receiver pickup advanced;
- proof state advanced;
- backlog decreased for the bound deed;
- expected-next relation changed materially.

`NO_SIGNAL_NE_DEAD`
`RECOVERABLE_NE_RUNNING`
`RESTART_NE_RECOVERY_PROOF`

## CoStallMesh+

Many observers may watch the same work, but only one actuator should attempt recovery for a given lease/effect scope.

`MANY_WATCHERS_ONE_ELECTED_ACTUATOR`

Candidate recovery ladder:

`OBSERVE -> CLASSIFY -> ELECT_ACTUATOR -> ONE_IDEMPOTENT_NUDGE -> BACKOFF -> RECHECK -> SUCCESSOR_FROM_CHECKPOINT -> QUARANTINE -> HUMAN_GATE_IF_MATERIAL`

Recovery must be:

- bounded;
- idempotent where possible;
- lease-aware;
- evidence-producing;
- backoff-controlled;
- circuit-broken after repeated failure.

Do not create recovery storms.

## Acceleration / anti-jam posture

The target is not maximal parallelism.

The target is maximum useful verified throughput under receiver, proof, authority and resource constraints.

Watch at least:

`discovery_rate`
`execution_rate`
`proof_rate`
`receiver_pickup_rate`
`fanin_rate`
`retirement_rate`
`queue_growth`
`human_attention_debt`

If discovery or execution outruns pickup/fanin, bias toward compaction and receiver work rather than spawning more workers.

`MORE_PARALLEL_NE_MORE_PROGRESS`
`ACCELERATION_NE_UNBOUNDED_CONCURRENCY`
`QUEUE_GROWTH_CAN_SIGNAL_RECEIVER_STARVATION`
`MOMENTUM_NE_AUDIENCE_PICKUP`

## Delivery / audience truth

For outreach, sites, nodes, modules and other receiver-facing work, distinguish:

`READY -> SENT -> DELIVERED -> PICKED_UP -> UNDERSTOOD -> RESPONDED -> INTEGRATED`

A state called `READY` must not imply `SENT`.

A state called `SENT` must not imply `DELIVERED`.

A state called `DELIVERED` must not imply `PICKED_UP`.

`READY_NE_SENT`
`SENT_NE_DELIVERED`
`DELIVERY_NE_PICKUP`
`PICKUP_NE_UNDERSTOOD`
`UNDERSTOOD_NE_INTEGRATED`

## User UX

Ordinary users should not manage provider sessions, CLIs, worker tabs, leases, queues or recovery ladders.

Preferred UX:

`CoHereNow`
- material workspaces;
- currentness;
- meaningful progress;
- only material exceptions;
- genuine human blockers;
- receiver/outreach status when relevant.

Backend session/process detail should normally remain virtual, hidden or drill-down only.

`USER_WORKSPACE_NE_PROVIDER_SESSION`
`CLI_NE_PRIMARY_USER_UX`
`BACKEND_COMPLEXITY_NE_USER_OBLIGATION`

## Rails

`VISIBLE_NE_LIVE`
`HEARTBEAT_NE_PROGRESS`
`TAB_NE_WORKER`
`SESSION_NE_WORK`
`NO_SIGNAL_NE_DEAD`
`RECOVERABLE_NE_RUNNING`
`RESTART_NE_RECOVERY_PROOF`
`MANY_WATCHERS_ONE_ELECTED_ACTUATOR`
`MORE_PARALLEL_NE_MORE_PROGRESS`
`ACCELERATION_NE_UNBOUNDED_CONCURRENCY`
`READY_NE_SENT`
`SENT_NE_DELIVERED`
`DELIVERY_NE_PICKUP`
`USER_WORKSPACE_NE_PROVIDER_SESSION`
`CLI_NE_PRIMARY_USER_UX`
`VALIDATION_IS_NOT_ACCEPTANCE`
