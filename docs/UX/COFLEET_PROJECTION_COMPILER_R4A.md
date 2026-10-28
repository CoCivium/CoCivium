# CoFleetProjectionCompiler R4A

**State:** `DETERMINISTIC_COMPILER_READY__RICKBAR_RECEIVER_UNPROVEN`

R4A turns already-bounded control-plane objects into a quiet CoFleetProjection+ suitable for RickBar/CoDesktop or another observer surface.

Inputs may include:

- R1 shadow lifecycle ledger;
- R2 logical spawn plan;
- public front registry;
- separately proven runtime facts.

Missing runtime facts remain null/unknown. They are never synthesized from architecture.

## Important distinctions

- bounded ledger session count != global fleet census;
- logical CoSpawn contract != live worker;
- blocked work != human blocker;
- provider-session count requires explicit runtime evidence;
- front registry count != active front embodiments;
- exception != request for Rick.

## Temperature mapping

- HOT: ACTIVE, WORKING, CHALLENGING, REAWAKENED, RECOVERY, DEGRADED
- WARM: BOOTSTRAPPING, WAITING, COTWILIGHT, EXTERNALIZING, SUCCESSOR_READY
- DORMANT: QUIESCENT, DORMANT
- ARCHIVE: CLOSE_SAFE
- COMPOST: SUPERSEDED
- COOL: otherwise

The mapping is a UX projection and remains revisable.

## Pressure

R4A retains dimensions. The compact headline is only a projection:

- DEGRADED if bounded session evidence includes degraded/recovery state;
- HIGH if blocked contracts or explicit human blockers exist;
- MODERATE if logical work exists;
- LOW if bounded inputs are quiet;
- UNKNOWN without useful inputs.

## Human blockers

R4A refuses to infer human blockers from generic blocked contracts. A blocker appears only from a runtime/control-plane object that explicitly binds a human authority or information requirement.

`EXCEPTION_NE_HUMAN_BLOCKER`

## Self-test

The embedded self-test checks:

- bounded temperature counts;
- blocked logical contract does not become human blocker;
- provider count remains unknown without runtime facts;
- global fleet census remains unproven.

## Next

R4B is receiver binding into the native RickBar/CoDesktop host once a proven runtime adapter can supply the projection object or an equivalent readproof.

`COUNT_NE_GLOBAL_CENSUS`  
`LOGICAL_CONTRACT_NE_LIVE_WORKER`  
`RICK_NE_HEARTBEAT`


## R4A1 waitless shadow visibility

CoFleetProjection now counts `SHADOW` logical contracts separately from
`LOGICAL_ONLY` and `BLOCKED` contracts. A shadow verifier is useful bounded
work with no effect lease; it is not inferred to be a live worker or a human
blocker.

`SHADOW_CONTRACT_NE_HUMAN_BLOCKER`  
`SHADOW_CONTRACT_NE_LIVE_WORKER`  
`EFFECT_GATED_NE_GLOBAL_BLOCKER`

## R4B fail-closed observer currentness (2026-10-28 research candidate)

This is a **behavioral repair to the existing CoFleet R4A compiler**, not a new controller, X2 diagnosis, native CoBar deployment, or global census.

Previous R4A code set the pressure headline to `UNKNOWN` whenever both bounded session and logical-contract inputs were empty. As a result, a separately supplied `runtime.currentness.state=STALE` or `DEGRADED` could disappear from the headline. Boolean runtime counts also passed the Python integer check, so `materialized_workers=true` could be reported as one worker.

R4B test contract:
- explicit bounded observer `STALE`/`DEGRADED` produces a `DEGRADED` pressure headline and a source-scoped exception; **not a claim about whether the actual device is powered on or healthy**;
- `AGING` produces `MODERATE`; `HEALTHY` without a runtime census remains `UNKNOWN`;
- independently supplied human blockers or blocked logical contracts remain visible even when there are no sessions;
- `true`/`false` and negative values never count as proven runtime workers, sessions, or leases; real nonnegative integers remain valid;
- stale observer data does **not** create a human blocker, receiver acknowledgment, active agent, or permission to restart a process.

Run `python scripts/CoFleetProjectionCompilerR4A.py --selftest` and `python -m unittest discover -s tests -p 'test_cofleet_currentness_r4b.py' -v`. CI checks Python 3.11 and 3.13.

**Specific X2 boundary:** Desktop Commander reported its X2 **observer route** offline in the October 28 audit (last seen about 99 hours earlier). That is a currentness limitation of this particular remote observer, **not proof X2 is dead or off**. The existing X2 Reconnect Watch and CoAll Device Continuity already cover discovery; do not install a duplicate watcher. Before any native CoOrb placement, require fresh X2 foreground-input/latency health, existing CoBar/RickBar process identity, and a single controlled read-only census.

`OBSERVER_PATH_OFFLINE_NE_DEVICE_DEAD | UNKNOWN_NE_HEALTHY | BOOLEAN_NE_COUNT | LOW_WORKLOAD_NE_HEALTH | PROJECTION_NE_RUNTIME`
