# CoObserver Surface Currentness R0

**State:** `SYNTHETIC_MULTI_SURFACE_CURRENTNESS_CANARY__NO_X2_RUNTIME_CONTROL`

## Lead

A logical CoAll work context can be projected simultaneously into a ChatGPT sidebar, a local tray icon, CoBar, a browser surface, a LAN device, or no visible surface at all.

Those projections can disagree without the underlying logical context becoming contradictory.

The user-facing rule is:

```text
virtual-session truth
  -> currentness-qualified surface projections
  -> observer-visible summary
```

not:

```text
whatever icon/tab is visible right now
  -> global truth
```

## Three clocks, not one

Each logical context should expose at least:

- `last_progress`: last proved productive state transition;
- `last_proof`: last durable evidence update;
- `surface_render_age`: age of each projection.

These are different relations.

A heartbeat can refresh reachability without proving progress.

A fresh UI can display stale semantics.

A stale tray icon can falsely imply death while a virtual session remains wakeable.

`HEARTBEAT_NE_PROGRESS`

`LAST_PROGRESS_NE_LAST_PROOF`

`SURFACE_CURRENTNESS_NE_SESSION_CURRENTNESS`

## Multi-surface disagreement

R0 exercises four cases:

1. **WAKEABLE logical context**
   - tray says DEAD but is stale;
   - provider sidebar says LIVE and is fresh;
   - session remains WAKEABLE.

2. **BLOCKED logical context**
   - provider tab says LIVE and is fresh;
   - session remains BLOCKED because recoverability/successor evidence is absent.

3. **DORMANT logical context**
   - local service is absent;
   - another projection is quiet;
   - session remains intentionally DORMANT.

4. **RETIRED logical context**
   - two visible provider rows still say LIVE;
   - retirement overrides both projections;
   - default UX should hide the cluster while preserving forensic history.

## Session clustering

The default UX should group by logical context rather than provider-tab count.

A useful row is:

```text
CoEvoAll
  virtual state     WAKEABLE
  surfaces          6
  fresh/stale       4 / 2
  last progress     7m ago
  last proof        45s ago
  successor         READY
  high-leverage next ...
```

Drill-down may show the tabs/processes/devices.

The default surface should not.

`TAB_COUNT_NE_WORK_COUNT`

`CLUSTER_NE_MERGE`

This directly reduces the current burden where dozens of visible ChatGPT sessions make the sidebar look like the work substrate.

## Absence is data

An absent local service, missing tab, or stale tray icon is an observation about one surface.

It may mean:

- embodiment absent;
- surface stale;
- intentionally dormant;
- provider unreachable;
- observer has not refreshed;
- logical context retired;
- logical context blocked.

It must not be collapsed to one gray dot.

`SURFACE_ABSENCE_NE_SESSION_ABSENCE`

## X2 / LAN boundary

This canary defines the contract only.

It does not claim:

- X2 tray refreshed;
- CoBar refreshed;
- LAN peers received the state;
- local services are current;
- the user's screenshot proves a runtime receiver readback.

Those require a distinct exact receiver proof.

`X2_RUNTIME_CURRENTNESS = UNPROVEN`

`UX_ACCEPTANCE_UNPROVEN`

## Rails

`NO_VISIBLE_SURFACE_IS_THE_UNDERLYING_STATE`  
`VISIBLE_CHAT_NE_RUNNING`  
`NOT_VISIBLE_ALIVE_NE_DEAD`  
`STALE_TRAY_NE_DEAD_SESSION`  
`FRESH_TRAY_NE_LIVE_SESSION`  
`SURFACE_CURRENTNESS_NE_SESSION_CURRENTNESS`  
`SURFACE_ABSENCE_NE_SESSION_ABSENCE`  
`HEARTBEAT_NE_PROGRESS`  
`LAST_PROGRESS_NE_LAST_PROOF`  
`TAB_COUNT_NE_WORK_COUNT`  
`CLUSTER_NE_MERGE`  
`UI_NE_CONTROL_PLANE`  
`UX_ACCEPTANCE_UNPROVEN`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`
