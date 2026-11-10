# CoRelKernel R0

**State:** `CANDIDATE__PUBLIC_RND__NOT_CANON__NOT_RUNTIME_AUTHORITY`

## Purpose

CoRelKernel R0 is a minimal relational substrate for causal, non-causal, meta, null/absence, boundary-crossing, observer-relative, time-qualified, conflicting, and revisable relations without erasing provenance or uncertainty.

## Minimal relation object

A relation carries `rel_id`, `subject`, `predicate`, `object`, `scope`, `observer`, `time`, `evidence`, `confidence`, `causal_status`, and `provenance`. Subject or object MAY reference another relation ID.

## Core rails

`RELATION_NE_CAUSATION`  
`UNKNOWN_CAUSE_NE_NO_RELATION`  
`NO_EDGE_NE_NO_INFORMATION`  
`EVOLVING_RELATION_NE_HISTORY_ERASURE`  
`SUPERSESSION_CYCLE_IS_INVALID`  
`CONCURRENT_REVISION_NE_AUTOMATIC_WINNER`  
`CONFLICT_NE_INVALIDITY`  
`LATEST_TIMESTAMP_NE_TRUTH`  
`MERGE_NE_ERASE_DISAGREEMENT`  
`RESOLUTION_NE_HISTORY_ERASURE`  
`RESOLUTION_NE_TRUTH_BY_AUTHORITY`  
`DIFFERENT_OBSERVER_NE_FALSEHOOD`  
`DIFFERENT_TIME_NE_CONTRADICTION`

## Observer-relative and time-qualified contradiction

`CONTRADICTS` is not an unqualified magic edge. It MUST include `contradiction_basis`.

Baseline bases:
- `observer_relative`
- `temporal_overlap`
- `scope_relative`
- `evidence_conflict`
- `logical_conflict`

For `observer_relative`, both endpoints must be relation references with distinct non-empty observers.

For `temporal_overlap`, both endpoints must be relation references whose `valid_from` / `valid_to` intervals overlap. Non-overlapping states are not contradictory merely because their values differ.

Time objects may carry:
- `valid_from`
- `valid_to`
- `observed_at`

When both validity bounds are present, `valid_from <= valid_to` is required.

## Concurrent revision conflicts

Sibling revisions that supersede the same prior relation MUST expose one shared `conflict_set_id` and a `conflict_status`. R0 preserves conflicting siblings rather than selecting a winner implicitly.

Allowed states:
- `unresolved`
- `resolved`
- `superseded`
- `not_applicable`

## Conflict resolution as a relation

A resolution is represented as a new relation, not by deleting or silently rewriting the conflicting siblings.

A resolution relation MUST use `RESOLVES_CONFLICT`, name the target set in `resolves_conflict_set_id`, point to a member of that set, carry provenance, and carry a non-empty `resolution_note`.

## Other invariants

`RELATION_MUST_HAVE_PROVENANCE`  
`CAUSAL_STATUS_MUST_BE_EXPLICIT`  
`UNKNOWN_NE_FALSE`  
`ABSENCE_NE_NO_INFORMATION`  
`RELATION_ON_RELATION_MUST_REFERENCE_EXISTING_REL_IDS`  
`TRANSFORMATION_MUST_PRESERVE_LINEAGE`  
`SIBLING_REVISIONS_MUST_EXPOSE_CONFLICT`  
`CONFLICT_RESOLUTION_MUST_REFERENCE_EXISTING_CONFLICT_MEMBER`  
`CONTRADICTION_MUST_BE_QUALIFIED`  
`EVERYTHING_MAY_RELATE_NE_EVERY_RELATION_IS_USEFUL`

## Boundary qualification

A relation or endpoint MAY be marked `internal`, `external`, `boundary`, or `unknown_domain`.

`COALL_NE_ALL_THAT_EXISTS`  
`MODELLED_EXTERNALLY_NE_OWNED_BY_COALL`

## Anti-explosion rail

Potential relations may be combinatorially large. Expansion SHOULD be selective and biased toward information gain, decision relevance, evidence gain, failure detection, or compression benefit.

`RELATION_DENSITY_NE_UNDERSTANDING`

## Non-goals

R0 does not claim all entities are reducible to relations, infer causation from correlation, claim CoAll contains all reality, define a universal graph engine, or grant authority because a relation is represented.

## Next

If this candidate remains green, the next useful step is contraction: extract stable validation semantics into a reusable relation library and stop growing the R0 surface unless a failing fixture earns a new field.

## CoRel+ / CoBraid+ bounded logical review braid | November 2026

**Public-source experiment only:** [CoRel+ / CoBraid+ logical wave planner](../../tools/corel_braid_logical_wave_r0.py), [synthetic eight-work-item fixture](../../fixtures/relations/corel_braid_logical_wave_r0.json), and [adversarial source tests](../../tools/test_corel_braid_logical_wave_r0.py). This is a **read-only next-review projection**, not a session orchestrator, cross-provider scheduler, runtime installer, or conversion of CoRelKernel into governing canon.

### Recover a talked-out causal chain without treating every relation as a command

- CoRelKernel's `CAUSES`, `POSSIBLY_CAUSES`, `INVERTS`, `CHALLENGES`, `RELATED_TO` and `PRECEDES` remain **descriptive**. Their declared `causal_status` is a **source claim**, not permission to execute, an independently supported causal mechanism, or even a work-order prerequisite.
- **Only** an explicit, provenance-bearing `REVIEW_DEPENDS_ON` relation is interpreted as a *logical prerequisite for source review*. It does not change either candidate ontology's schema or create execution authority. In this preview, `subject` is the downstream review and `object` is the prerequisite. A claimed source receipt fulfills a *preview* dependency; the actual bytes were not refetched here, so acceptance remains unproven.
- Run the currently ready, distinct-collision-domain **logical reviews side by side** within a small fan-out cap. Hold unfinished downstream reviews until their declared source receipts; carry stop/HOLD branches as explicit unresolved dependencies rather than freezing independent branches.
- A fan-in review needs each of its explicitly named upstream source proofs; a successful test from one side does not count as proof from the other. Cycles quarantine their members and descendants without erasing unaffected paths.
- An `EFFECT_GATED` item can be **shadow-reviewed** when its source prerequisites are presented, but receives no effect lease, host process, publisher permission or human-gate bypass. One elected actuator and a genuine receiver readproof remain separate runtime acceptance gates.

### Synthetic eight-object proof
The synthetic fixture models one completed public source orientation, three **independent eligible reviews** (CoRel inversion, CoSpeedo comprehension and X2 launcher triage), downstream local quiet-boot remediation, a three-way CoBraid fan-in review, and an unrelated historical HELD branch with one descendant. It deliberately includes a narrative `CAUSES` relation that **does not** schedule work. The planner should elect three bounded preview candidates, keep quiet-boot remediation and braid fan-in waiting, and preserve the historic HELD branch. No OS windows, PowerShell, hosted workers or new schedules are started. The user does not supply another CoPre rant to move the source-bound review graph.

### Source qualification and limits
- The schema surface is intentionally narrow: at most 32 synthetic work objects, 96 relations, and four parallel *logical* candidates. Unrecognized fields, dangling endpoints, duplicate identities, missing source/receipt digest claims, unqualified privacy scope, self-dependency and malformed provenance fail closed.
- `VERIFIED_SOURCE` is explicitly an **untrusted input declaration** here; no independent source bytes, device readiness, receiver ACK, donor schema equivalence, or causal status support can be inferred. Currentness, consent and real collision leases must be checked by an actual adopted runtime.
- This is **not** a replacement for the [CoLogicalSpawnPlanner R2](../Operations/COLOGICAL_SPAWN_PLANNER_R2.md) or [CoWaitlessExecution R0](../Architecture/COWAITLESS_EXECUTION_R0.md): it is a bounded review of why some logical DAG branches can proceed and others must HOLD. The existing PR127 richer CoRelationField remains a separate frozen candidate; this proof does not promote or merge either ontology.

**Stop / acceptance condition:** A separate, authorized receiver can reconstruct the same source-bound review state, challenge an intentionally false upstream receipt, retain one unaffected ready branch and show one real progress event without a human keepalive. Until this is observed: `LOGICAL_PLAN_NE_EXECUTION`, `CAUSAL_LINK_NE_REVIEW_DEPENDENCY`, `FANOUT_NE_RUNNING_AGENTS`, `NO_INPUT_NE_ALWAYS_ON`, `SOURCE_HASH_STRING_NE_RECEIVER_READPROOF`, `PUBLIC_BRANCH_NE_DEPLOYED`.
