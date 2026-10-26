# CoAllBloom+ Operating Braid R0 — EVO ALL BETTERS+

**State:** `PROPOSED_OPERATING_CONTRACT__BRANCH_ONLY__NOT_LIVE_ORCHESTRATION`  
**Branch:** `evo/coallbloom-operating-braid-r0`  
**Intent:** turn the broad CoAllBloom+ optionality field into a practical, evidence-led workflow that can discover and reconcile existing CoCivium work without pretending every possibility is implemented.

## 1. Decision

Use **CoAllBloom+** as the possibility/meaning/alternative field and **CoAllBloom+ relations** as the canonical records connecting candidate concepts, evidence, resources, experiments, software surfaces, agents, people, time, and outcomes. **CoAllBloom+ betters** are versioned improvements to those relations, their grammars, projections, workflows, or implementations, each with a stated reason and evidence.

Do not create a separate service for every suffix. Prefer relation families and schemas first; split into components only when a tested need, ownership boundary, or deployment constraint justifies it.

## 2. Relation families — open taxonomy, not an exhaustive universe

Each family is a typed view over the shared relation envelope. Families may overlap, nest, invert, combine, or be unknown.

- **Origin / seed / lineage:** sources, parent ideas, provenance, prerequisites, forks, descendants, supersession, recovery.
- **Combination / permutation / inversion:** compositions, orderings, reversals, duals, complements, negations, symmetry, asymmetry, transformations.
- **Alternatives / optionality basins:** candidates, counterfactuals, branching paths, possibility regions, trade-offs, excluded paths, retirement reasons.
- **Meta-relations / logic / symbols:** relations between relations, formal rules, mappings, types, definitions, contradictions, proofs within a stated system.
- **Domain / modality:** physical, material, computational, social, linguistic, mathematical, subjective, experiential, cultural, spiritual, non-spiritual, mystical, hypothetical, simulated, metaphorical, unknown, and mixed-domain.
- **Space / boundary / dimension:** location, scale, inside/outside, between, adjacency, topology, dimensional model, non-spatial representation, frame changes.
- **Time / evolution:** event time, observation time, valid interval, sequence, recurrence, freshness, drift, chaos, adaptation, evolution, emergence, stabilization, decay, and recovery.
- **Agent / relationship / organization:** people, AI/IA identities, sessions, capability, role candidates, contacts, groups, organizations, consent, authority, handoffs, acknowledgements.
- **Software / surface / device:** OS, native stack, legacy applications, runtimes, dependencies, desktop, wallpaper, screensaver, UX, accessibility, devices, LAN/local/regional/cloud resources, clusters, projections.
- **Resource / production / evidence:** discovery, qualification, allocation, experiment, product, production, verification, receipt, preservation, extension, recombination.
- **Not-those / boundary / risk:** incompatible candidates, unsupported mappings, stale or missing sources, disallowed actions, privacy limits, unresolved contradictions, retired paths, rollback.

Terms such as G_d, angel-related, ET-related, spiritual, mystical, or non-space may be represented with their source, intended frame, and epistemic type. A relation record does not independently validate the reality of its subject.

## 3. Canonical relation envelope

Required core fields:

- `relation_id`, `subject_ref`, `predicate`, `object_ref_or_value`
- `family`, `domain`, `modality`, `epistemic_type`
- `source_refs[]`, `observed_at`, `valid_time`, `version`, `lineage_refs[]`
- `status`, `confidence_or_unknown`, `assumptions[]`, `alternatives[]`, `contradictions[]`
- `permission_scope`, `privacy_class`, `effect_authority`, `expiry_or_recheck`
- `next_test_or_wake`, `owner_or_worker`, `receipt_ref`, `supersedes_or_retired_by`

Projection-specific fields: `projection_id`, `surface`, `rendered_at`, `currentness`, `loss_ledger[]`. Do not fill unknown fields with guesses. Use explicit unknown/not-observed values.

## 4. Core operating loop

`DISCOVER → QUALIFY → RELATE → RESOURCE → EXPERIMENT → PRODUCE → VERIFY → PRESERVE → EXTEND → RECOMBINE`

1. **Discover:** search existing repository artifacts, source systems, resources, versions, and known prior decisions before rebuilding.
2. **Qualify:** distinguish observation, report, inference, hypothesis, simulation, proposal, and verified outcome; check freshness, access, cost, privacy, and authority.
3. **Relate:** connect sources, candidates, alternatives, constraints, dependencies, and contradictions with stable IDs and provenance.
4. **Resource:** route only to available and authorized workers/tools; preserve capability and access uncertainty.
5. **Experiment:** choose the smallest reversible test with measurable acceptance criteria and rollback.
6. **Produce:** create a versioned artifact or bounded result; do not label an idea a running implementation.
7. **Verify:** inspect the artifact/result and run relevant checks; report checks actually performed.
8. **Preserve:** commit source pointers, receipts, loss ledger, unresolved questions, and next wake.
9. **Extend:** add a better only when it contributes measured value, a clarified distinction, or a useful alternative.
10. **Recombine:** reuse compatible relations and artifacts while preserving their independent lineage and semantics.

## 5. Evergreen AI/IA onramp

The onramp is evergreen by contract, but live freshness requires a real trigger and receiver.

- Discover current bootstrap, relevant files, branches, issues, commits, and task ledger.
- Qualify provider/model/tool capability, access, constraints, provenance, and recency.
- Bind a compact currentness packet: task, source refs, versions, scope, permissions, acceptance criteria, and known contradictions.
- Return a bounded `CoEvoDelta+`: what changed, evidence, files/refs, tests, uncertainties, conflicts, and next action.
- Review and merge only after deduplication, compatibility checks, and permission checks.
- If a worker is unavailable, leave the task queued or blocked with reason; do not silently drop it.
- Refresh stale source pointers and revalidate access before consequential action.

A GitHub artifact alone does not awaken idle sessions, continuously synchronize every AI, or confer authority.

## 6. CoSoftware+ / CoSmoosh+ / CoOrbWare+ and X2

Reuse the companion proposal `docs/Architecture/COSOFTWARE_COSMOOSH_COORB_SURFACE_BRAID_R0_20261026.md` as the software/surface branch of this operating braid.

X2 is a candidate exemplar, not a verified representative of all surfaces. Start with permissioned read-only discovery of OS/software versions, dependencies, desktop configuration, wallpaper/screensaver, UX/accessibility, device context, and currentness. Build a CoOrb+ projection with source pointers, missing-data notices, stale markers, and semantic-loss notes. Then test one reversible workflow. No machine mutation, secret collection, or cross-system outreach is implied.

## 7. Compatibility, authority, and receipts

Preserve mappings as `NATIVE`, `ADAPTED_WITH_RECEIPT`, `REDUCED_PROJECTION`, `READ_ONLY_VIEW`, `QUEUED_HANDOFF`, `UNSUPPORTED`, or `CONFLICT`.

Keep these distinctions explicit:

- identity ≠ authentication ≠ authorization;
- visible tag ≠ authority;
- discovered route ≠ consent;
- SENT ≠ DELIVERED ≠ READ ≠ UNDERSTOOD ≠ ADOPTED;
- candidate ≠ tested result;
- rendered state ≠ source truth;
- unexplained pattern ≠ proof;
- file exists ≠ runtime operates;
- commit exists ≠ tests passed;
- proposal ≠ implementation;
- implementation ≠ verified benefit.

Each consequential action needs an authorized principal, specific scope, basis, time window, and revocation/rollback path. Each completion claim needs an observable receipt.

## 8. First conformance fixture

Use synthetic data first. Include OS/software versions, legacy dependency, desktop projection, stale/missing source, contradictory relation, inversion/permutation, alternative candidate, mixed epistemic domains, an unauthorized tag, an acknowledgement with unknown delivery, and a time-order ambiguity.

Pass criteria:
1. Source and epistemic status are visible for every claim.
2. Alternatives, contradictions, and retired paths survive recomputation.
3. Forbidden effects are rejected before execution.
4. Projection loss and stale data are explicit.
5. Legacy source semantics and lineage remain recoverable.
6. Receipts describe only performed and observed actions.
7. Unfinished work stays queued, blocked, or retired with reason.
8. A fresh session can reproduce the fixture from source pointers.

This document's creation is not a test run. No live X2 inventory or universal AI synchronization is claimed.

## 9. Promote betters by evidence

A proposed better records: `better_id`, prior version, changed relation/rule, reason, predicted benefit, acceptance test, observed outcome, regressions, uncertainty, rollback, and decision (`KEEP`, `REVISE`, `REJECT`, `DEFER`). Do not promote a better merely because it is newer, more elaborate, or more expansive.

## 10. Work-conservation invariant

Every useful unfinished item must be one of: `QUEUED`, `BLOCKED_WITH_REASON`, `DEFERRED_WITH_WAKE`, `RETIRED_WITH_REASON`, or `VERIFIED_COMPLETE`. Preserve owner/worker, next wake, source refs, and authority needs. User presence should be optional where safe automation exists, but never fabricated where no authorized trigger, worker, or receiver exists.

**LATCHED EVERMORE** = durable versioned continuity, recoverable lineage, refreshable pointers, and permissioned renewal—not perpetual execution, infinite compute, universal synchronization, or irreversible lock-in.
