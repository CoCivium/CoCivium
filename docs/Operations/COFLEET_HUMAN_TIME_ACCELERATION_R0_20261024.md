# CoFleet+ Human-Time Acceleration R0

**State:** PUBLIC_OPERATING_CANDIDATE__NOT_DEVICE_DEPLOYMENT_PROOF  
**Observed:** 2026-10-24

## Why

CoCivium has accumulated substantial architecture, proof rails and local prototypes, but too many authorized local device classes remain unqualified or unadopted in human time.

The optimization target is therefore:

`MINIMIZE_CALENDAR_TIME_TO_USEFUL_TRUSTWORTHY_DEVICE_PRESENCE`

not:

`MAXIMIZE_NUMBER_OF_DEVICE_FEATURES`.

## Minimum viable CoCivium presence

A device counts as **MVC_PRESENT** only when it has all of:

1. exact device identity;
2. one visible, user-owned ingress/observer surface;
3. currentness state;
4. local/native stop or disable path;
5. one bounded useful action;
6. one restart/recovery proof appropriate to the device;
7. privacy/authority boundary;
8. append-only receipt;
9. no provider tab required as the sole continuity anchor.

A richer device may add CoBar, CoOrb, CoEyes, CoThumb, CoPayload, local AI, sensors or spatial views later.

## Shared kernel

Every device class should reuse the same contract where possible:

```
identity
+ current work pointer
+ currentness
+ ingress
+ capability registry
+ authority
+ privacy
+ heartbeat / wake
+ receipt
+ recovery
```

Device-specific rendering and input are adapters, not separate truth systems.

## Parallel qualification lanes

Run device lanes in parallel when independent and safe:

- X2 desktop
- secondary Windows laptop/desktop
- Android/Samsung phone
- iPad/tablet
- Quest/VR
- headless/local service nodes
- future devices

Each lane produces PASS / FAIL / HELD and may not borrow proof from another lane.

## Human-time urgency score

Prioritize by:

```
Urgency =
  expected_daily_human_minutes_saved
+ failure-domain value
+ continuity value
+ receiver value
+ cross-device reuse
- setup burden
- privacy/security risk
- irreversible coupling
```

Calendar delay is a real cost.

## X2 priority

X2 remains the reference exemplar, but **X2 completion must not block independent device lanes**.

Current next X2 proof:

- re-establish machine-observable route;
- identify current RickBar/CoBar generation or exact absence;
- restore one visible ingress if safely recoverable;
- qualify CoInput/CoThumb only after exact physical event proof;
- verify restart/currentness/recovery;
- keep native rollback.

## Device-wave contract

For each device:

```
DISCOVER
-> IDENTIFY
-> QUALIFY CAPABILITIES
-> INSTALL/OPEN MINIMUM SAFE SURFACE
-> ONE USEFUL ACTION
-> RESTART/RECOVERY TEST
-> RECEIPT
-> USER ACCEPTANCE
-> EVOLVE
```

Do not wait for perfect feature parity.

## Review cadence

Use **human-time gates**:

- T+0: device identified / blocker explicit;
- T+1 bounded wave: minimum surface candidate;
- T+2: one useful action;
- T+3: restart/recovery;
- then enrich only after baseline passes.

A lane that remains blocked must expose the blocker and let other lanes continue.

## Parallelism rails

`PARALLEL_LANES_NE_SHARED_AUTHORITY`  
`DEVICE_A_PASS_NE_DEVICE_B_PASS`  
`X2_BLOCKED_NE_FLEET_BLOCKED`  
`MORE_FEATURES_NE_MORE_MATURITY`  
`CALENDAR_DELAY_IS_A_COST`  
`HUMAN_OPTIONAL_OPERATION_NE_HUMAN_IRRELEVANT`

## Current evidence boundary

- X2 has historical RickBar restore/interaction evidence, but current liveness/adoption is not established.
- Phone/tablet/Quest projections exist as candidate modes but are unverified device adoption.
- Current Desktop Commander route reports X2 offline.
- No claim is made here that other local devices are currently reachable, installed, integrated or CoEx.

## Highest-value next motion

Qualify **two lanes in parallel** when reachable:

1. X2: restore/verify one visible current ingress.
2. one independently powered secondary device: establish MVC_PRESENT and use it as the first real cross-device receiver/recovery exemplar.

This closes both usability and failure-domain debt faster than polishing X2 alone.
