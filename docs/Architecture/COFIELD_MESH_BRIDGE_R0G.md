# CoFieldMesh+ / CoBridgeField+ R0G

**State:** `SYNTHETIC_SURFACE_BRIDGE_FIELD_CANARY__NO_RUNTIME_NO_CANON_NO_AUTHORITY_CHANGE`

## CoHereNow

The BranchField and CoCatchUp work now have a candidate surface/bridge layer.

The useful object is not a single global connector state such as "connected".

It is an observer- and time-relative relation:

```text
observer/front
  --bridge-->
surface
```

with orthogonal facets for:

- discovery;
- capability;
- read authority;
- write authority;
- connectivity;
- proof;
- currentness;
- seat/materialization;
- effect lease;
- invitation;
- confidentiality.

## Why orthogonal facets

A bridge may be:

- connected but revoked;
- authorized but disconnected;
- proven but stale;
- readable but not writable;
- writable in principle but lacking a materialized seat;
- visible yet entirely unauthorized for effects.

So a single ladder such as:

`DISCOVERED -> CAPABLE -> AUTHORIZED -> CONNECTED -> PROVEN`

is useful as a story but false as a complete state model.

R0G therefore uses a state vector.

`AUTHORIZED_NE_CONNECTED`

`CONNECTED_NE_PROVEN`

`PROVEN_NE_CURRENT_FOREVER`

`DISCONNECTED_NE_REVOKED`

## CoFieldMesh+

Candidate composition:

```text
CoSurfaceField+
  visible/known surfaces
        +
CoBridgeField+
  typed observer<->surface relations
        +
CoAttentionField+
  quiet/watch/actionable rendering
        +
CoFieldRouting+
  route only bridges that satisfy exact task gates
        =
CoFieldMesh+
```

A later CoFieldEcology+ may add:

- bridge birth/retirement;
- competition and substitution;
- failure-domain diversity;
- cost/benefit metabolism;
- relation propagation;
- dormant/reactivated surfaces;
- multi-front routing;
- observer-specific projections.

No such runtime ecology is activated here.

## R0G synthetic canary

Nine bridge cases are tested:

1. proven current read-only path -> `READ_ONLY_PROVEN`;
2. public visible but unproven -> `OBSERVE_UNPROVEN`;
3. write authority + invitation but no seat -> `DRAFT_ONLY_NO_SEAT`;
4. proven but stale -> `HOLD_STALE`;
5. degraded but readable -> `DEGRADED_READ_ONLY`;
6. disconnected but not revoked -> `HOLD_DISCONNECTED`;
7. connected but revoked -> `HOLD_REVOKED`;
8. every synthetic write gate passes -> `BOUNDED_WRITE_ELIGIBLE`;
9. confidentiality mismatch -> `HOLD_CONFIDENTIALITY`.

Only one synthetic case becomes write-eligible, and even that does not create real external effect authority.

## CoAttentionField+

The same state vector projects into a deliberately small attention surface:

- `QUIET`: proven/current and no action required;
- `WATCH`: usable for observation but degraded or unproven;
- `ACTIONABLE`: a hold, missing gate, stale state, or hypothetical effect path needing a decision.

This is rendering, not ontology deletion.

`RENDERED_NE_EXISTENT`

`HIDDEN_NE_DELETED`

## Relation to CoCatchUp+

CoCatchUp already proves a bounded path from a live GitHub currentness receipt to exact receiver pickup and a quiet human projection.

R0G treats that pattern as one donor for a broader bridge model.

It does not claim CoBar, CoCivium.exe, provider connectors, social surfaces, or private surfaces are currently integrated.

`RECEIPT_PICKUP_NE_PRODUCT_INTEGRATION`

## Candidate routing law

A write-capable route requires, at minimum:

```text
DISCOVERED
+ CAPABLE
+ READ_AUTHORIZED
+ WRITE_AUTHORIZED
+ CONNECTED
+ PROVEN
+ CURRENT
+ MATERIALIZED_SEAT
+ INVITATION
+ EFFECT_LEASE
+ CONFIDENTIALITY_COMPATIBLE
```

A failure of one write gate may still leave a safe read/draft path.

That lets CoAll degrade gracefully rather than equating "cannot write" with "cannot observe".

## Rails

`BRIDGE_NE_SURFACE`  
`SURFACE_NE_BRIDGE`  
`VISIBLE_NE_AUTHORIZED`  
`AUTHORIZED_NE_CONNECTED`  
`CONNECTED_NE_PROVEN`  
`PROVEN_NE_CURRENT_FOREVER`  
`STALE_NE_DEAD`  
`DISCONNECTED_NE_REVOKED`  
`REVOKED_GT_CONNECTIVITY`  
`READ_AUTHORITY_NE_WRITE_AUTHORITY`  
`WRITE_AUTHORITY_NE_EFFECT_LEASE`  
`EFFECT_LEASE_NE_INVITATION`  
`SEAT_NE_AUTHORITY`  
`ONE_SURFACE_CAN_HAVE_MANY_BRIDGES`  
`BRIDGE_STATE_IS_OBSERVER_TIME_RELATIVE`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`
