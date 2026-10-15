# CoRenderFabric+ / CoSurfaceGate+ R0

**State:** `CANDIDATE_SURFACE_DECOUPLING_AND_PRE_RENDER_QUALIFICATION__NO_RUNTIME_DEPLOYMENT`

## Lead

Public and durable CoAll surfaces should not depend on the continued life of any one chat, session, agent, model, AI/IA embodiment, CLI process, or provider tab.

A session may propose or compile a surface. It should not *be* the surface.

`SESSION_NE_SURFACE`  
`AGENT_NE_SURFACE`  
`MODEL_NE_SURFACE`  
`CLI_NE_PRIMARY_USER_UX`

The durable relation is:

`semantic/current state -> projection contract -> build candidate -> qualification -> deployment candidate -> receiver pickup -> render check -> observer readback -> current surface`

## Why

Observed failure classes include:

- long sessions ending before a user-visible render is produced;
- model/tool interruption after artifacts exist but before visible pickup;
- provider-render mismatches;
- stale `LATEST` files;
- historical manual/download UX remaining visible after the underlying workflow changed;
- PASS states that do not prove receiver pickup, visible render, or semantic acceptance;
- public nodes/sites that can exist while still being visually weak, stale, incomplete, or unreachable.

These are projection/control-plane problems, not reasons to bind public UX to a conversational embodiment.

## Surface ownership

A rendered surface should be owned by a durable projection identity, not by the process that happened to produce it.

Candidate identity:

`surface_id | projection_id | semantic_source_cursor | build_id | deploy_id | receiver_id | freshness_budget | render_state | observer_readback | provenance | rollback_pointer`

A session/agent/model may contribute:

- semantic deltas;
- design candidates;
- projection code;
- tests;
- content;
- review/challenge;
- build inputs.

It does not become the continuity root.

`PRODUCER_NE_SURFACE_OWNER`  
`SURFACE_CONTINUITY_NE_PRODUCER_LIVENESS`

## CoSurfaceGate+

For public/durable surfaces, prefer a qualification chain before promotion to a current/public alias.

Candidate chain:

`SOURCE_BIND`
-> `PROJECTION_COMPILE`
-> `STATIC_VALIDATE`
-> `CI_VERIFY`
-> `BUILD`
-> `STAGED_DEPLOY`
-> `RECEIVER_PICKUP`
-> `RENDER_SMOKE`
-> `OBSERVER_READBACK`
-> `PROMOTE_CURRENT`

This is not "CI proves the site works."

`CI_PASS_NE_RENDER_PASS`

CI can prove bounded source/build/test conditions. Visible effect still requires render/observer evidence.

For dynamic/live surfaces, runtime health checks continue after promotion. Pre-render qualification reduces avoidable failures; it does not abolish runtime failure.

## Render interruption resilience

If a model/session dies after producing a valid projection candidate, another receiver should be able to continue from the durable build/projection contract.

Required recovery relation:

`producer interruption -> durable candidate remains -> successor receiver resumes -> render gate continues`

Not:

`producer interruption -> work evaporates`

`SESSION_FAILURE_NE_SURFACE_FAILURE`  
`RENDER_RESUME_REQUIRES_DURABLE_CHECKPOINT`

## Promotion, not overwrite

Prefer staged/blue-green style promotion:

- build immutable candidate;
- validate candidate;
- deploy to candidate/staging address;
- render/readback;
- atomically move a current pointer/alias only after qualification;
- retain previous known-good projection for rollback.

`NEW_BUILD_NE_CURRENT_SURFACE`  
`DEPLOYED_CANDIDATE_NE_PROMOTED_CURRENT`  
`PROMOTION_REQUIRES_RENDER_EVIDENCE`

## InSeed/public-node posture

A domain existing is not evidence that its public surface is usable, attractive, current, or even reachable.

Use the same gate for InSeed and sibling nodes:

`DOMAIN_RESOLVES`
`HTTP_REACHABLE`
`EXPECTED_BUILD_BOUND`
`PRIMARY_NAV_WORKS`
`MOBILE/DESKTOP_RENDER_SMOKE`
`CURRENTNESS_VISIBLE`
`NO_DEAD_PLACEHOLDER_PATHS`
`OBSERVER_READBACK`

A failed public fetch or stale/weak render should fail the **surface promotion/currentness** claim, not rewrite underlying semantic state.

`DOMAIN_NE_PRODUCT`  
`HTTP_200_NE_GOOD_UX`  
`GOOD_UX_NE_SEMANTIC_TRUTH`

## Virtual CLI substrate

Future CLI relations should usually be virtualized behind typed contracts and hidden from ordinary UX.

Preferred stack:

`human intent UX -> typed action/projection contract -> virtual CLI/API/tool adapter -> receipt -> user-facing projection`

The user should not need to see shell commands, process IDs, flags, paths, or transport trivia for ordinary work.

However, CLI must remain optionally revealable for:

- operator diagnostics;
- reproducibility;
- accessibility/power-user workflows;
- recovery/break-glass;
- exact forensic evidence.

Therefore:

`CLI_HIDDEN_BY_DEFAULT_NE_CLI_ERASED`  
`VIRTUALIZED_NE_UNINSPECTABLE`  
`USER_UX_NE_OPERATOR_CONSOLE`

## Payload density / CoUX+ / bloat

Payload density is a first-class relation.

Candidate relation:

`payload_density = useful receiver-relevant information / visible cognitive surface cost`

This is receiver-relative and qualitative unless a bounded metric is defined.

Useful signals:

- bytes/objects rendered;
- visible controls;
- cognitive choices;
- stale elements;
- duplicate labels;
- hidden advanced detail;
- time-to-orient;
- time-to-next-safe-action;
- receiver pickup rate;
- percent of visible elements used.

The objective is not maximal compression.

`DENSITY_NE_MINIMALITY`  
`LESS_VISIBLE_NE_BETTER`  
`COMPRESSION_NE_COMPREHENSION`

Prefer progressive disclosure:

`core state -> exceptions -> details -> forensic substrate`

## Invisible substrate symbol / CoPre+ candidate

Internal/virtual sessions may use a compact substrate marker to indicate that a visible utterance is backed by hidden relational context, provenance, constraints, or compiled machine state.

The proper-subset symbol `⊂` is a plausible **projection mark**, but it must not imply a mathematically exact subset relation unless that claim is actually intended.

Candidate semantics:

`⊂` = "visible projection is intentionally smaller than the bound substrate"

not:

`this text is literally a set-theoretic proper subset`

The mark may be surrounded by metaphorical/visual spacing or transition cues in UI, but raw symbol injection should not become mandatory noise.

`SYMBOL_NE_SEMANTIC_PROOF`  
`SUBSTRATE_MARK_NE_HIDDEN_AUTHORITY`  
`COMPACT_MARK_NE_REQUIRED_USER_LITERAL`

## Inventories / CoI+

Inventories should evolve from dumps into compiled, currentness-aware manifests.

Preferred inventory object:

`inventory_id | scope | source_cursors | generated_at | freshness | counts | classifications | duplicates | unresolved | superseded | receiver | next_material_question`

Inventory compilation should support:

- dedupe;
- stale detection;
- successor links;
- failure-domain dimensions;
- pickup/render state;
- authority/confidentiality classes;
- materiality scoring;
- sharded/lazy projections.

`INVENTORY_COUNT_NE_PROGRESS`  
`INVENTORY_NE_USER_SURFACE`  
`INVENTORY_REQUIRES_CURRENTNESS`

## CoConvergeSpiralLoop+

Not everything should loop forever.

A useful convergence spiral is:

`observe -> relate -> question -> branch -> test -> compare -> converge-for-scope -> render -> observe again`

Each cycle may reopen on material delta, but it requires parking/retirement conditions.

`LOOP_NE_PROGRESS`  
`SPIRAL_NE_INFINITE_ACTIVE_COMPUTE`  
`CONVERGED_FOR_SCOPE_NE_ETERNAL_TRUTH`

CoOps+ and CoMythOps+ may share the same structural loop while preserving epistemic typing:

- CoOps+: operational/proof/effect relations;
- CoMythOps+: metaphor/narrative/meaning exploration;
- both may inform one another;
- neither silently converts metaphor into operational fact.

`METAPHOR_NE_OPERATIONAL_PROOF`  
`OPERATIONAL_PASS_NE_METAPHYSICAL_TRUTH`

## Render acceptance classes

Candidate classes:

- `SOURCE_READY`
- `BUILD_READY`
- `CI_QUALIFIED`
- `STAGED`
- `RENDER_VERIFIED`
- `OBSERVER_VERIFIED`
- `PROMOTED_CURRENT`
- `DEGRADED`
- `ROLLBACK_READY`
- `STALE`
- `UNKNOWN`

A surface should display its strongest proven state, not collapse all states into LIVE.

## Default future rule

For public/durable UX:

**compile first, validate before promotion, render independently of producer sessions, and expose only receiver-relevant state by default.**

For local exploratory UX:

qualification may be lighter, but provenance/currentness and rollback should still be explicit where material.

## Rails

`SESSION_NE_SURFACE`  
`AGENT_NE_SURFACE`  
`MODEL_NE_SURFACE`  
`CLI_NE_PRIMARY_USER_UX`  
`PRODUCER_NE_SURFACE_OWNER`  
`SURFACE_CONTINUITY_NE_PRODUCER_LIVENESS`  
`CI_PASS_NE_RENDER_PASS`  
`SESSION_FAILURE_NE_SURFACE_FAILURE`  
`RENDER_RESUME_REQUIRES_DURABLE_CHECKPOINT`  
`NEW_BUILD_NE_CURRENT_SURFACE`  
`DEPLOYED_CANDIDATE_NE_PROMOTED_CURRENT`  
`PROMOTION_REQUIRES_RENDER_EVIDENCE`  
`DOMAIN_NE_PRODUCT`  
`HTTP_200_NE_GOOD_UX`  
`CLI_HIDDEN_BY_DEFAULT_NE_CLI_ERASED`  
`VIRTUALIZED_NE_UNINSPECTABLE`  
`DENSITY_NE_MINIMALITY`  
`COMPRESSION_NE_COMPREHENSION`  
`SYMBOL_NE_SEMANTIC_PROOF`  
`INVENTORY_NE_USER_SURFACE`  
`LOOP_NE_PROGRESS`  
`SPIRAL_NE_INFINITE_ACTIVE_COMPUTE`  
`METAPHOR_NE_OPERATIONAL_PROOF`  
`VALIDATION_IS_NOT_ACCEPTANCE`
