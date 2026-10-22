# RD1 CoAll Web Service / Graphical Specification

**Status:** public candidate / build-ready specification / not deployed

## Product

A lightweight browser surface that makes the CoDot/CoMap/CoOrb concept tangible without requiring the user to understand the underlying machinery.

## UX stack

```text
                 +-----------------------+
                 |      CoDot / 00_me    |
                 |  tiny truthful status |
                 +-----------+-----------+
                             |
                    expands on relevance
                             v
                 +-----------------------+
                 |      CoBar / RickBar  |
                 |  state + next action  |
                 +-----------+-----------+
                             |
                             v
                 +-----------------------+
                 |        CoMap           |
                 | nodes / edges / time   |
                 +-----------+-----------+
                             |
                             v
                 +-----------------------+
                 |       CoOrb / CoTele  |
                 |  temporal + scenarios |
                 +-----------------------+
```

## RD1 screens

### 1. Quiet home

- tiny CoDot
- currentness ring
- one-line status
- no auto-expanding animation unless state changes

### 2. CoBar

Columns:

`NOW | MOVED | WATCH | NEXT`

### 3. CoMap

Node categories:

`WORK | RESOURCE | RECEIVER | EVIDENCE | DEVICE | MODEL | RECOVERY`

Edge categories:

`DEPENDS | FEEDS | CHALLENGES | RECOVERS | PROPAGATES | OBSERVES | SUPERSEDES`

### 4. CoOrb

Radial visualization of:

`core -> near orbit -> working orbit -> research orbit -> audience orbit`

### 5. CoTele

Slider:

`prior | now | forecast | counterfactual`

Every non-current state is explicitly labeled.

## Camera/audio disclosure

RD1 may offer optional camera/audio experiments only behind an explicit consent surface.

Required copy concept:

> Camera/microphone access is optional and exists to test whether multimodal context can improve the experience. The interface must show clearly when access is active, what stream is available, and what is not available.

The demo must never imply that camera/audio access exists merely because hardware is attached.

## Evidence grammar

Every dynamic element exposes one of:

`OBSERVED | DERIVED | SIMULATED | INFERRED | CANDIDATE | UNAVAILABLE`

## Demo data

Use synthetic data by default.

Example:

`CoDot -> CoBar -> CoMap`

`work-A --depends--> resource-B`

`worker-3 --challenges--> worker-1`

`checkpoint-7 --recovers--> work-A`

No private contacts or credentials are required.

## Distributed hosting target

Architecture should permit:

- static edge hosting
- replicated read-only projections
- independent API/runtime nodes
- provider-neutral export
- local/offline fallback
- portable object bundles

Do not claim global redundancy until multiple independent deployments are actually verified.

## RD1 acceptance tests

1. Page remains readable if animation fails.
2. CoDot state is truthful when backend is unavailable.
3. Simulated workers are visually distinct from real workers.
4. Camera/audio permission state is explicit.
5. Temporal projections cannot masquerade as current facts.
6. Public/demo data cannot expose private operational state.
7. Refresh preserves the current demo state.
8. Recovery fixture can reconstruct the same demo graph from durable seed data.

## Success criterion

The visitor should understand in under one minute:

**one field -> many relations -> many perspectives -> selective execution -> visible evidence -> recoverable state**

without needing a tour guide.

## Nonclaims

RD1 is a candidate web-service design. It is not a deployed global service, not a proof of device control, and not evidence of machine consciousness.
