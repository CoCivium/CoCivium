# CoOrb+ / CoOrbWare+ / CoAll+ Compatibility and Evolution Contract R0

**State:** PROPOSED_CONTRACT__BRANCH_ONLY__NOT_RUNTIME_IMPLEMENTATION  
**Date:** 2026-10-26  
**Related existing work:** `docs/Architecture/CORELATION_CLOUD_CLUSTER_ORG_BRAID_R0_20261026.md`; repository issue #225, “EVO ALL BETTERS +”.  
**Purpose:** preserve richer relationship meaning while allowing legacy and future environments to participate at their actual capabilities.

## Prime invariant

`PRESERVE_MEANING__ADAPT_PROJECTIONS__REPORT_LOSS__NEVER_FAKE_COMPATIBILITY`

CoOrb+ views, CoOrbWare+ capabilities, and CoAll+ relationship semantics must not be constrained to the least expressive legacy schema. Conversely, richer semantics must not be silently invented, injected into unauthorized destinations, or represented as successfully supported when the target cannot carry them.

## Layer responsibilities

- **CoAll+ RELS / canonical relationship fabric:** stable identities, typed relationships, temporal history, provenance, uncertainty, permissions, version lineage, and explicit distinctions between observed facts, hypotheses, proposals, actions, and verified outcomes.
- **CoOrb+:** user-facing and machine-facing projections of the canonical fabric. A projection is a view, not the source of truth.
- **CoOrbWare+:** reusable capabilities and substrate-specific implementations: adapters, connectors, renderers, storage/event interfaces, validation, execution boundaries, and receipts.
- **Compatibility/evolution services (cross-cutting responsibility; not yet a claim of a separate implemented product):** schema negotiation, mapping, capability discovery, migration planning, loss reporting, conflict handling, conformance testing, and rollback.

Reuse existing CoRel, CoTerms, CoModule, CoMap, CoSurfaceOS, CoOrb, CoOrbWare, and related assets before adding a new subsystem. Names in this document describe responsibilities, not proof that a runtime implementation exists.

## Compatibility outcomes

Every source-to-target mapping must resolve to one explicit outcome:

1. **NATIVE** — target represents the required semantics directly.
2. **ADAPTED_WITH_RECEIPT** — mapping is understood and preserves declared invariants; mapping and version are recorded.
3. **REDUCED_PROJECTION** — target receives a safe subset; omitted or approximated semantics are enumerated and remain available in the authorized canonical store.
4. **READ_ONLY_VIEW** — target may inspect but not mutate the canonical object.
5. **QUEUED_HANDOFF** — target cannot perform the operation now; work remains durable with blocker and retry/next-wake condition.
6. **UNSUPPORTED** — no safe mapping exists; do not pretend success.
7. **CONFLICT** — incompatible concurrent edits or identity mappings require reconciliation before write-back.

A route or adapter must never upgrade its own status from planned to executed, sent to delivered, delivered to read, read to understood, or understood to adopted without corresponding evidence.

## Required compatibility envelope

Each adapter or projection declares:

- source and target identifiers, versions, and capability profiles;
- mapping rules and directionality;
- stable IDs and alias/identity policy;
- preserved, transformed, omitted, and approximated fields/relations;
- provenance and evidence pointers;
- privacy class, authorization scope, and permitted operations;
- temporal/version behavior and conflict strategy;
- error, retry, idempotency, and recovery behavior;
- conformance tests, observed results, known gaps, and rollback path.

Unknown capability is not capability. Missing metadata is not permission. A successful serialization is not proof that the target preserved meaning.

## Relationship semantics that must survive

Where relevant to the source contract, preserve:

- entity identity and relationship direction/type;
- source provenance and event chronology;
- uncertainty and evidence ceiling;
- proposed versus actual roles or memberships;
- consent, permissions, privacy classifications, and revocation;
- current state versus future possibility;
- lineage, supersession, merges, and reversibility;
- unresolved questions and explicit unsupported/loss states.

Examples of forbidden silent coercions: candidate to member; invitation to appointment; visible contact to active relationship; contact route to authority; planned action to completed action; list membership to canonical identity.

## Schema evolution and legacy boundaries

- Version schemas explicitly; do not infer compatibility from similar names alone.
- Use versioned migrations with preflight checks, dry-run diffs, backups or recoverable snapshots where appropriate, and rollback instructions.
- Keep source data unchanged until the target mapping passes validation and authorization.
- Preserve unknown extension fields when safe; otherwise report their disposition explicitly.
- Detect non-invertible mappings. Do not promise round-trip fidelity where the target model is lossy.
- Record each migration as an append-only receipt linked to source and target versions.
- Keep legacy adapters replaceable; no adapter becomes the canonical semantic authority merely because it is widely deployed.
- Prefer a capability-based interface over branching core logic for every legacy environment.

## Minimum conformance tests

1. **Identity stability:** round-trip preserves stable IDs or produces a documented, reversible alias map.
2. **Semantic loss:** unsupported relationship types are reported, never silently dropped.
3. **Evidence ceiling:** no state is upgraded without source evidence.
4. **Permission boundary:** unauthorized reads/writes fail closed and are recorded.
5. **Conflict handling:** divergent edits surface a conflict rather than silently overwriting.
6. **Version migration:** old versions migrate through a declared path with a reviewable diff.
7. **Rollback:** failed migration can restore the previous valid state or clearly state why rollback is unavailable.
8. **Idempotency:** replaying an event does not duplicate relationships or actions.
9. **Projection truthfulness:** UI labels distinguish canonical state, cached view, stale data, and unknown state.
10. **Accessibility and alternative substrates:** required meaning remains available in supported text/assistive interfaces when a richer visual rendering is unavailable.

Each test receipt must state exact scope, inputs, expected result, observed result, timestamp, software/version, and PASS/FAIL/BLOCKED. A proposed test is not a test run.

## First bounded experiment

Select one existing CoOrb-style view and one representative legacy schema only after inspecting current assets. Use synthetic or explicitly privacy-safe fixtures; do not publish private contact data.

For each fixture, record:
- canonical source and stable relation ID;
- source version and target capability profile;
- expected mapping and any known loss;
- authorization and allowed operation;
- observed adapter result;
- conformance test receipts;
- rollback/recovery result.

Compare the rendered projection against the canonical object and verify that omitted semantics remain visible as omissions. Do not claim the experiment passed until it is actually run and its receipts are recorded.

## Acceptance criteria

- No duplicate core subsystem is created before the existing resource reconciliation.
- Every mapping has a declared outcome and version.
- Every lossy projection reports its loss.
- No authorization or relationship-state upgrade is inferred from compatibility.
- Required conformance tests are runnable and produce reproducible receipts.
- CoOrb+ makes uncertainty, stale state, unsupported semantics, and next action legible.
- Unfinished work remains queued, blocked with reason, cancelled with reason, or verified complete.

## Status and next step

This document is a proposed contract on a working branch. It does **not** establish that an adapter, runtime, migration, test harness, or benchmark currently exists or has passed. Next: reconcile this contract against existing CoOrb/CoOrbWare, CoRel, CoTerms, CoModule, CoMap, and CoSurfaceOS artifacts; revise overlaps; then implement one smallest reversible vertical slice and record its actual test receipts.
