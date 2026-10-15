# CoTriPie+ / Dynamic Cadence R0

**State:** `CANDIDATE_PUBLIC_ARCHITECTURE__NO_INDEPENDENT_RUNTIME_PROOF`

## CoTriPie+

Critical work should not be protected by blindly duplicating every process.

Use three **roles**:

### Active Pie
The elected active work identity: current lease, authority snapshot,
dependency/collision state and at most one effect actuator per collision domain.

### Shadow Pie
Durable current pointer, checkpoints, receipts/readproof, passive verification
and warm-standby preparation. Shadow has no effect lease by default.

### Recovery Pie
Independently restorable state, exact source/object identities, reconstruction
instructions, authority boundaries, wake/failover predicates and restore proof.

`TRIPIE_NE_THREE_ALWAYS_RUNNING_PROCESSES`

## Protection tiers

- T0 disposable: recreate when cheaper than protecting.
- T1 recoverable: durable checkpoint.
- T2 important: Active + Shadow.
- T3 continuity-critical: full TriPie.
- T4 identity/authority/safety-critical: TriPie + independent verifier + drills.

## Dynamic cadence

The preferred control rule is:

`EVENT_DRIVEN_PRIMARY__HOURLY_RECONCILIATION_FALLBACK`

A material event may include:

- new exact evidence;
- receiver pickup/effect;
- route loss/return;
- authority change;
- lease expiry;
- dependency resolution;
- contradiction;
- new durable Need;
- recovery event.

The hourly sweep catches missed events, stale currentness, due leases,
proof/receiver debt and runnable safe work. Hourly is a wake opportunity, not a
fixed checklist and not a requirement to burn compute when no useful delta
exists.

## Wake cycle

```text
bind durable current state
 -> qualify currentness/evidence/authority/confidentiality
 -> qualify capabilities/routes/failure domains
 -> dedupe fresh receipts
 -> evaluate leases/collisions/backpressure
 -> generate bounded options
 -> elect highest-value safe frontier
 -> fan out independent shadow work
 -> elect few actuators
 -> verify effect/receiver
 -> fan in disagreement + negative knowledge + learning
 -> checkpoint + update wake predicates
```

`NO_DELTA` is a valid output.

## Provider-neutrality

Schedule semantics, work graph, leases, authority snapshots, currentness,
capability registry, TriPie roles, receipts, watermarks, wake predicates and
recovery instructions should not depend on one provider.

A provider task, CI runner, local scheduler, LAN worker or other route is an
adapter/implementation, not the control-plane ontology.

## Rails

`REPLICA_NE_AUTHORITY`  
`COPY_COUNT_NE_FAILURE_DOMAIN_COUNT`  
`BACKUP_NE_REAL_UNTIL_RESTORE_PROOF`  
`MANY_WATCHERS_ONE_ELECTED_ACTUATOR`  
`SHADOW_WORK_NE_EFFECT_AUTHORITY`  
`HOT_SHADOW_NE_SECOND_ACTUATOR`  
`HOURLY_NE_ALWAYS_BUSY`  
`DYNAMIC_NE_RANDOM`  
`AGENTIC_NE_UNBOUNDED_AUTHORITY`  
`ALWAYS_EVO_NE_ALWAYS_MUTATE`  
`SCHEDULE_NE_PROVIDER`  
`PROVIDER_TASK_NE_CONTROL_PLANE`
