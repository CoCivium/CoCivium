# CoUXCurrentness+ / Self-Refreshing Observer Surface R0

**State:** `CANDIDATE_UX_CURRENTNESS_CONTRACT__NO_LIVE_RICKBAR_REPAIR_YET`

## Lead

The current local UX is materially behind the current CoAll frontier.

Fresh X2 readback on 2026-10-02 found RickBar/CoBar visible-state artifacts whose embedded timestamps are mostly from April and June 2026, while active CoAll work is in October 2026.

Examples observed on X2:

- `D:\CoCivium\CoStacks\RickBar\COBAR_CONTROL_VIEW__LATEST.json` -> `2026-04-07T23:36:35Z`
- `D:\CoCivium\CoStacks\RickBar\COBAR_HEARTBEAT_ENFORCEMENT_TICKER__LATEST.json` -> `2026-04-07T06:01:15Z`
- `D:\CoCivium\CoStacks\RickBar\UI\RICKBAR_COMPACT_CONFIG__LATEST.json` -> `2026-04-03T20:05:18Z`
- local RickBar launch-surface pointer -> `2026-06-14T21:43:25Z`
- local session-health lag pointer -> `2026-06-15T14:35:25Z`

The local `status.json` currently reports `DEGRADED_PASS`.

This is evidence of visible UX staleness, not evidence that the underlying semantic/project state is equally stale.

`VISIBLE_STALENESS_NE_SEMANTIC_STALENESS`

## Target

RickBar / CoBar / CoDesktop should become observer projections over a currentness fabric rather than collections of manually refreshed "LATEST" files.

Preferred relation:

```text
durable currentness sources
-> receiver-specific subscription
-> freshness/currentness gate
-> compact CoHereNow projection
-> local visible surface
-> observer readback
-> ACK/currentness cursor
```

The surface should refresh itself when a material subscribed relation changes, with a bounded heartbeat fallback when event delivery is unavailable.

`CURRENTNESS_EVENT_NE_GLOBAL_REFRESH`

`REFRESH_NE_GLOBAL_STATE_DUMP`

## Minimum projection

Default visible content should remain small:

- CoHereNow;
- Meaning;
- material exceptions;
- human blockers only when real;
- currentness age;
- source coverage;
- active effect leases;
- next safe action only when needed.

Detailed receipts, session archaeology, raw hashes and backend inventories remain drill-down.

## Freshness contract

Each visible projection SHOULD bind:

`projection_id | built_at | source_cursors | source_times | freshness_budget | coverage | stale_after | currentness_state | receiver | evidence_refs`

Candidate states:

- `CURRENT`
- `AGING`
- `STALE`
- `SOURCE_UNREACHABLE`
- `COVERAGE_PARTIAL`
- `UNKNOWN`

A surface that cannot refresh should visibly declare staleness instead of continuing to render old state as though it were current.

`STALE_VISIBLE_STATE_MUST_SELF_DISCLOSE`

## Source ecology

Candidate source order:

1. authorized local/private CoPulse or CoStead currentness;
2. current local execution/receipt state;
3. public-safe GitHub currentness;
4. bounded provider/session state where available;
5. explicit UNKNOWN when a source is unavailable.

No one source is the control plane.

`COBAR_NE_CONTINUITY_ROOT`
`GITHUB_NE_UI_CURRENTNESS_ROOT`
`PROVIDER_SESSION_NE_UI_CURRENTNESS_ROOT`

## Automatic refresh

Preferred:

`EVENT_DRIVEN_WHERE_PROVEN + BOUNDED_HEARTBEAT_FALLBACK`

Not:

`USER_MANUAL_REFRESH_AS_CONTROL_PLANE`

The exact heartbeat interval is a receiver/runtime parameter, not a universal architectural constant.

## Acceptance ladder

`SOURCE_CURRENTNESS_BOUND`
-> `PROJECTION_COMPILED`
-> `LOCAL_SURFACE_PICKUP`
-> `AUTOMATIC_REFRESH_TRIGGERED`
-> `VISIBLE_RENDER_UPDATED`
-> `OBSERVER_READBACK`
-> `STALE_SOURCE_SELF_DISCLOSED`

No lower rung implies the higher one.

## Rails

`VISIBLE_STALENESS_NE_SEMANTIC_STALENESS`
`STORED_STATE_NE_VISIBLE_STATE`
`PROJECTION_ARTIFACT_NE_VISIBLE_PICKUP`
`CURRENTNESS_EVENT_NE_GLOBAL_REFRESH`
`REFRESH_NE_GLOBAL_STATE_DUMP`
`STALE_VISIBLE_STATE_MUST_SELF_DISCLOSE`
`COBAR_NE_CONTINUITY_ROOT`
`USER_MANUAL_REFRESH_NE_CONTROL_PLANE`
`VALIDATION_IS_NOT_ACCEPTANCE`
