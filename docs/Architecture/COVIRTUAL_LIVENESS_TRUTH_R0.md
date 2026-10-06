# CoVirtual Liveness Truth R0

**State:** `PUBLIC_CANDIDATE_ARCHITECTURE__SYNTHETIC_CANARY__NO_RUNTIME_CONTROL`

## Lead

Liveness belongs to the **virtual session**, not to any one provider tab, browser window, model process, local worker, or device.

The durable source of truth is therefore not:

```text
is this tab/process alive?
```

It is:

```text
can this logical work context still be recovered, understood, and safely awakened?
```

## Two different truths

### Embodiment liveness

Temporary fact about one projection:

`LIVE | STALE | UNREACHABLE | ABSENT | UNKNOWN`

Examples:

- ChatGPT tab responds;
- local process answers a challenge;
- provider session exists;
- X2 worker is reachable.

This expires quickly.

### Virtual-session liveness

Durable relation over the logical work context:

`RECOVERABLE | WAKEABLE | MATERIALIZED | BLOCKED | DORMANT | RETIRED`

Derived from:

- checkpoint/frontier;
- currentness cursor;
- provenance;
- authority envelope;
- wake conditions;
- successor/reconstruction recipe;
- relevant pulses;
- retirement state;
- optional embodiment evidence.

A virtual session can therefore be alive while having **zero live embodiments**.

`DEMATERIALIZED_NE_DEAD`

## Proposed source-of-truth rule

```text
VirtualAlive(session,t)
  := recoverable(session,t)
     AND not_retired(session,t)
     AND (
       wakeable(session,t)
       OR materially_active(session,t)
       OR intentionally_dormant(session,t)
     )
```

A live embodiment may make a session materially active, but embodiment liveness is not the identity root.

## Why some current sessions do not “come back alive”

Possible classes include:

1. **Embodiment dead, virtual session healthy**
   - provider tab vanished;
   - durable checkpoint + cursor + wake condition remain;
   - state should be `WAKEABLE` or `DORMANT`.

2. **Embodiment live, virtual recovery weak**
   - process responds now;
   - no durable checkpoint or reconstruction contract;
   - state may be `MATERIALIZED` but fragile.

3. **Virtual session blocked**
   - no live embodiment;
   - no sufficient durable frontier;
   - no wake condition;
   - state `BLOCKED`.

4. **Explicitly retired**
   - durable history may remain;
   - liveness false by policy;
   - state `RETIRED`.

The UI should distinguish these instead of one misleading green/gray dot.

## CoUX projection

A user-facing surface should prefer:

```text
CoHereNow
  CoLanguage       WAKEABLE
  CoVids           DORMANT
  CoPublic         MATERIALIZED
  CoOldTab17       BLOCKED
```

Optional evidence drill-down:

```text
WAKEABLE because:
  checkpoint        PASS
  currentness cursor PASS
  wake condition    PASS
  live embodiment   NONE
```

Thus a quiet session can still be truthfully shown as alive in the virtual sense.

## Heartbeat semantics

A heartbeat should prove only what produced it.

Possible heartbeat classes:

- `EMBODIMENT_HEARTBEAT`
- `VIRTUAL_SESSION_CURRENTNESS_PULSE`
- `RECEIVER_READPROOF`
- `WAKEABILITY_SELFTEST`
- `RECONSTRUCTION_CANARY`

Do not collapse them into one bit.

`HEARTBEAT_NE_SESSION_IDENTITY`

## Recovery preference

When a visible provider session fails to return:

```text
do not resurrect the tab first

read virtual-session truth
  -> reconstruct minimal working context
  -> elect best current embodiment
  -> bind provenance/currentness
  -> continue work
```

The replacement embodiment may be another provider, local model, CI worker, deterministic worker, or no live embodiment at all.

## Liveness source hierarchy

Candidate order:

1. explicit retirement / authority state;
2. durable checkpoint + frontier;
3. currentness cursor;
4. wake conditions / reconstruction recipe;
5. receiver readproof;
6. live embodiment evidence;
7. visible UI/provider status.

The last item is useful UX evidence, not the truth root.

`VISIBLE_STATUS_NE_RECEIVER_ROUTE`

## Relationship to custody

Virtual-session liveness is not lifecycle promotion.

A session being WAKEABLE does not imply its artifacts are:

`LANDED`, `PICKED_UP`, `INTEGRATED`, or `COEX`.

Those transitions still require their own exact evidence.

`RECOVERABLE_NE_INTEGRATED`

## Rails

`VIRTUAL_SESSION_NE_PROVIDER_TAB`  
`SESSION_IDENTITY_NE_LIVE_PROCESS`  
`EMBODIMENT_NE_IDENTITY`  
`DEMATERIALIZED_NE_DEAD`  
`QUIET_NE_DEAD`  
`LIVE_EMBODIMENT_NE_RECOVERABLE_SESSION`  
`UNREACHABLE_EMBODIMENT_NE_DEAD_SESSION`  
`VISIBLE_STATUS_NE_RECEIVER_ROUTE`  
`LIVENESS_NE_PERSISTENCE`  
`LIVENESS_NE_AUTHORITY`  
`WAKEABLE_NE_MATERIALIZED`  
`RECOVERABLE_NE_INTEGRATED`  
`VALIDATION_IS_NOT_ACCEPTANCE`
