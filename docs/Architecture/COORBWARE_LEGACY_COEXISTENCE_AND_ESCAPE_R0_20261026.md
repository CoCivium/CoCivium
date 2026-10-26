# CoOrbWare+ Legacy Coexistence + Escape R0

**State:** CANDIDATE_ARCHITECTURE__NOT_RUNTIME__NOT_VENDOR_CLAIM
**Observed:** 2026-10-26

## Thesis

CoOrb+ and CoOrbWare+ should not assume they fit naturally inside legacy environments.

Legacy operating systems, applications, accounts, file formats, identity systems, permission models, workflows, UI conventions, and organizational structures may remain useful while still being structurally mismatched with CoOrbWare.

The objective is therefore not forced replacement and not forced conformity.

`COEXIST -> WRAP -> TRANSLATE -> PROJECT -> ESCAPE_WHEN_NEEDED`

## Core rule

`LEGACY_CONTAINER_NE_CANONICAL_MODEL`

A legacy surface may host or project a CoOrbWare capability without becoming the authority for:
- identity;
- provenance;
- permission;
- evidence;
- currentness;
- recovery;
- work-object continuity;
- semantic meaning.

## Four coexistence modes

### 1. Native legacy projection
Use the existing UI/process where it remains the lowest-friction, safest surface.

### 2. Compatibility wrapper
Expose legacy capability through a typed adapter with explicit inputs, outputs, permissions, failure states, and receipts.

### 3. Parallel CoOrb surface
Keep the legacy tool intact while CoOrb provides context, currentness, relation, challenge, recovery, and cross-tool continuity beside it.

### 4. Escape / substitution
When a legacy environment prevents portability, proof, recovery, scoped authority, or acceptable UX, route to another provider, local implementation, open format, or native CoOrbWare surface.

## Compatibility contract

Every adapter should declare:
- source system;
- capability exposed;
- identity mapping;
- permission mapping;
- read/write/delete scope;
- state portability;
- provenance preservation;
- receipt quality;
- currentness semantics;
- failure modes;
- rollback / recovery;
- export / exit;
- privacy boundary;
- vendor dependency;
- replacement/substitution path.

## Anti-fit principle

Do not distort CoOrbWare simply to mimic inherited product assumptions.

Examples of legacy assumptions that may be treated as optional:
- one app owns one workflow;
- one screen is the product boundary;
- one account equals one identity;
- one vendor owns state;
- GUI navigation is the primary interface;
- session continuity equals work continuity;
- local storage location equals custody;
- visible success equals verified effect;
- permissions are account-wide rather than task-scoped.

`FAMILIAR_NE_REQUIRED`

## UX relation

CoOrb should be able to appear as:
- bottom CoBar;
- context lens;
- overlay;
- tray surface;
- browser projection;
- mobile companion;
- voice projection;
- headless API/JSON;
- CoMap relation view;
- ambient/wallpaper/idle view;
- native spatial/immersive surface where appropriate.

The same work object may project differently in each environment.

`MANY_PROJECTIONS_NE_MANY_TRUTH_STORES`

## CoSmoosh relation

Reuse CoSmoosh for reversible composition without forced homogenization.

Legacy products remain qualified contributors to a journey rather than compulsory owners of the whole journey.

`WRAPPED_NE_REFACTORED`
`INTEROPERABLE_NE_IDENTICAL`
`COMPOSE_NE_OWN`

## Escape hatches

Every important legacy integration should preserve at least one of:
- export;
- alternate provider;
- local fallback;
- open-format representation;
- human-readable receipt;
- replayable source packet;
- independent recovery path.

`NO_EXIT = DEPENDENCY_RISK`

## Degradation behavior

When a legacy surface blocks a desired capability:
1. expose the constraint;
2. degrade gracefully;
3. preserve source state;
4. offer a compatible alternate route;
5. avoid pretending partial success is full success;
6. record the loss ledger.

## Migration posture

Prefer gradual migration:

`LEGACY_ONLY -> WRAPPED -> PARALLEL_COORB -> PORTABLE_STATE -> MULTI_PROVIDER -> NATIVE_COORB_OPTION`

Not every system needs to reach the final stage.

## Selection rule

Choose the surface that maximizes:
`receiver_fit + safety + proof + portability + recovery + accessibility + optionality - friction - lockin - hidden_state - maintenance_debt`

## Rails

`LEGACY_CONTAINER_NE_CANONICAL_MODEL`
`COEXIST_NE_CONFORM`
`WRAPPED_NE_REFACTORED`
`INTEROPERABLE_NE_IDENTICAL`
`FAMILIAR_NE_REQUIRED`
`MANY_PROJECTIONS_NE_MANY_TRUTH_STORES`
`NO_EXIT = DEPENDENCY_RISK`
`ADAPTER_NE_AUTHORITY`
`VISIBLE_NE_TRUSTED`
`CONNECTED_NE_SAFE`

## First bounded proof

Pick one mature legacy workflow on X2 and render the same work object through:
1. its native legacy surface;
2. a CoOrb wrapper/overlay;
3. a headless typed representation.

Verify that identity, provenance, authority, currentness, and recovery remain consistent while the projections differ.

Pass only if the user can exit one projection without losing the work object or its receipt lineage.