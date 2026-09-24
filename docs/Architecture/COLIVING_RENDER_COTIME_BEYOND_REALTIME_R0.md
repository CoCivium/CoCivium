# CoLivingRender+ / CoRenderSession+ / CoBeyondRealtime+ R0

**Date:** 2026-09-24  
**State:** `CANDIDATE__BRANCH_ONLY__NO_RUNTIME_CANON_PUBLIC_RELEASE_OR_PROVIDER_SESSION_CONTROL`

## Lead

A CoAll surface does not need to be frozen, and it does not need to be owned by one continuously live model/provider session.

Distinguish:

- **Rendered+**: a bounded projection observed at a specific currentness/time point.
- **Rendering+**: a receiver-relative projection process that may recompile as authorized source relations change.
- **CoRenderSession+**: the continuity envelope that keeps a surface addressable while renderers, workers, models and provider sessions appear, disappear, hand off or sleep.
- **CoBeyondRealtime+**: candidate UX/temporal class in which usefulness comes from combining present state with provenance, replay, prediction, branching, precomputation and later calibration rather than optimizing only for lowest latency.

`RENDER_SESSION_NE_PROVIDER_SESSION`  
`RENDERING_NE_CONTINUOUS_MODEL_EXECUTION`  
`BETTER_THAN_REALTIME_NE_FASTER_THAN_REALTIME`

## Why "beyond realtime" can be better

Realtime answers one question:

> what is happening now?

CoTime+ can answer a richer set:

- what happened before;
- what changed;
- what was believed then;
- what is current now;
- what is predicted next;
- what assumptions produce each future;
- what can be prefetched before the receiver asks;
- what alternative branch should remain available;
- what later happened;
- how prior predictions calibrated;
- what this receiver should see versus another receiver.

For many knowledge-work and coordination tasks, this can outperform a purely realtime surface because the system can be **temporally richer**, not merely lower-latency.

`NOW_NE_WHOLE_TEMPORAL_CONTEXT`

## Important boundary

CoBeyondRealtime+ does not mean realtime is obsolete.

Hard realtime or very low latency remains important for classes such as:

- safety control;
- physical actuation;
- live communications;
- certain market-data or operational monitoring;
- interactive media;
- emergency response;
- synchronous collaboration.

The claim is narrower:

> where a task benefits from prediction, provenance, replay, branching, asynchronous preparation, receiver-relative currentness or calibration, a CoTime+ surface may be more useful than a realtime-only surface.

`TEMPORAL_RICHNESS_NE_LATENCY_IRRELEVANCE`

## Existing architecture this composes

Current CoLivingHighlightAsset+ already permits a living asset to evolve while being read through:

1. snapshot pinning;
2. visible live evolution with explicit delta/currentness;
3. receiver-relative refresh.

Current CoVirtualSession+ already separates durable logical-session identity from live process/provider embodiment.

Current CoAllPulseField+/CoTime+ already separates durable event/currentness state from provider-session delivery and distinguishes observation from prediction.

CoRenderSession+ composes these into a participant-facing continuity layer.

## Reference architecture

```text
sources / receipts / relation graph / forecasts
                    |
              CoPulseField+
                    |
          subscription + CoTime+
                    |
      bounded reconcile / fan-in
          /        |        \
   replay     currentness    futures
      \          |          /
        projection compiler
                 |
          CoRenderSession+
       /           |           \
 snapshot      live-delta    receiver-refresh
       \           |           /
          participant surface
                 ^
                 |
     temporary worker/model/provider
             embodiments
```

The surface is not owned by any one worker.

`WORK_SURVIVES_WORKER`  
`SURFACE_NE_WORKER`

## Complete rerender

A refresh may legitimately change nearly every visible element while preserving one semantic lineage.

Examples:

- text becomes a graph;
- a graph becomes a temporal map;
- terse controls become an explanatory narrative;
- accessibility requirements produce a substantially different projection;
- a participant changes role;
- a newer compiler reorganizes the same underlying relations;
- new evidence changes salience and layout;
- one receiver sees operations while another sees explanation.

A same-lineage rerender requires enough preserved invariants to prove continuity.

Candidate equivalence:

```text
stable asset identity
+ admissible source lineage
+ mandatory relation preservation
+ explicit projection loss
+ recoverable prior observed projection
+ receiver/currentness binding
= candidate same-lineage rerender
```

`RENDER_EQUIVALENCE_NE_PIXEL_EQUIVALENCE`  
`FULL_RERENDER_NE_HISTORY_ERASURE`

## Better-than-realtime temporal classes

Candidate render features:

### 1. Pre-time
Prepare likely useful work before the receiver asks.

Examples:

- prefetch likely next evidence;
- run bounded challengers;
- stage likely next render;
- warm a local model;
- compile possible next views.

`PREFETCH_NE_AUTHORITY`

### 2. Now-time
Represent current observed state with explicit freshness.

### 3. Replay-time
Reconstruct a prior observed projection exactly enough to answer:

> what did I actually see or know then?

### 4. Branch-time
Maintain several possible futures or interpretations without newest-wins collapse.

### 5. Forecast-time
Present predictions separately from observations.

### 6. Calibration-time
Bind prior forecasts to later outcomes.

### 7. Counterfactual-time
Explore what would differ under alternate assumptions.

### 8. Receiver-time
Allow different participants to advance through currentness at different rates while preserving shared lineage.

## Apparent continuity without continuous model execution

A participant may experience a continuously useful surface while worker execution is discontinuous.

```text
durable surface
+ event-driven currentness
+ prepared projections
+ bounded worker materialization
+ fast handoff
+ replay/reconstruction
= continuous participant experience
```

This does not imply one model continuously reasons in the background.

`CONTINUOUS_SURFACE_NE_CONTINUOUS_MODEL`  
`REALTIME_UX_NE_UNINTERRUPTED_REASONING`

## Provider-cycle interruption absorption

Provider interruption becomes one failure domain rather than the lifecycle boundary.

```text
provider A contributes
-> durable pulse/checkpoint
-> provider A ends
-> surface remains usable
-> local worker/provider B receives bounded currentness
-> B contributes successor delta
-> projection compiler rerenders
-> participant sees continuity + provenance
```

The goal is not an immortal tab.

The goal is:

> work continuity survives embodiment interruption.

`PROVIDER_INTERRUPTION_NE_WORK_INTERRUPTION`

## CoTime+ opportunity

One object may expose:

```text
past observed state
current state
newer available state
predicted next state
alternative future branches
counterfactual branch
later outcome
prediction calibration
receiver-specific projection
```

A user can therefore move through time relationally instead of treating the latest screen as reality itself.

## Massive parallelity behind the surface

Parallelism should normally be invisible unless material.

Candidate pattern:

```text
one participant-visible CoRenderSession
        |
        +-- challenger workers
        +-- evidence collectors
        +-- local/open models
        +-- provider models
        +-- CI canaries
        +-- forecast workers
        +-- render compilers
        |
      bounded fan-in
        |
  one coherent receiver projection
```

This allows large internal parallelism without recreating a wall of provider tabs.

`PARALLEL_WORKERS_NE_PARALLEL_USER_BURDEN`

## Render-session state

Candidate minimum envelope:

`render_session_id | asset_id | receiver_scope | read_mode | observed_projection_ref | prior_projection_ref | source_bindings | source_cursor | rendered_cursor | projection_compiler | renderer_binding | worker_bindings | event_time | observation_time | projection_time | currentness_state | visible_delta | projection_loss | authority_ceiling | confidentiality | recovery_ref | successor_ref | nonclaims`

Candidate currentness states:

- `CURRENT_FOR_BOUND_SCOPE`
- `NEWER_AVAILABLE`
- `RENDERING`
- `STALE_HOLD`
- `SOURCE_CONFLICT_HOLD`
- `WORKER_UNAVAILABLE_RENDER_STABLE`
- `RECONSTRUCTING`

## Product implications

RickBar / CoDesktop can become a stable participant surface over changing embodiments.

A participant might see:

```text
CoHereNow
  current through 17:16
  3 newer relations available
  1 forecast prepared
  2 background challenges complete
  provider A sleeping
  local worker available
  prior view recoverable
```

The visible interaction can therefore be more coherent than any one realtime provider session.

## Immediate canary

First bounded proof should use synthetic/public-safe data only.

1. materialize one render session from a stable asset;
2. render snapshot A;
3. advance source cursor;
4. execute several parallel synthetic workers;
5. fan-in one materially different projection B;
6. prove A remains recoverable;
7. prove B retains source/provenance bindings;
8. prove prediction remains distinct from observation;
9. simulate worker/provider disappearance;
10. prove surface continuity and reconstruction from durable inputs.

## Nonclaims

This R0 does not prove:

- continuous background reasoning;
- provider-native idle-session mutation;
- zero-latency updates;
- hard realtime guarantees;
- lossless semantic equivalence across arbitrary renders;
- runtime adoption;
- canon;
- authority transfer.

## Rails

`BETTER_THAN_REALTIME_NE_FASTER_THAN_REALTIME`  
`NOW_NE_WHOLE_TEMPORAL_CONTEXT`  
`TEMPORAL_RICHNESS_NE_LATENCY_IRRELEVANCE`  
`RENDER_SESSION_NE_PROVIDER_SESSION`  
`RENDERING_NE_CONTINUOUS_MODEL_EXECUTION`  
`WORK_SURVIVES_WORKER`  
`SURFACE_NE_WORKER`  
`RENDER_EQUIVALENCE_NE_PIXEL_EQUIVALENCE`  
`FULL_RERENDER_NE_HISTORY_ERASURE`  
`CONTINUOUS_SURFACE_NE_CONTINUOUS_MODEL`  
`REALTIME_UX_NE_UNINTERRUPTED_REASONING`  
`PROVIDER_INTERRUPTION_NE_WORK_INTERRUPTION`  
`PARALLEL_WORKERS_NE_PARALLEL_USER_BURDEN`
