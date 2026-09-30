# CoRelKernel R0

**State:** `CANDIDATE__PUBLIC_RND__NOT_CANON__NOT_RUNTIME_AUTHORITY`

## Purpose

CoRelKernel R0 is a minimal relational substrate for representing causal, non-causal, meta, null/absence, boundary-crossing, observer-relative, time-qualified, and conflicting concurrent relation revisions without erasing provenance or uncertainty.

The kernel is deliberately small. New vocabulary should be composed from typed relations and metadata before inventing new primitives.

## Minimal relation object

A relation contains:
- `rel_id`
- `subject`
- `predicate`
- `object`
- `scope`
- `observer`
- `time`
- `evidence`
- `confidence`
- `causal_status`
- `provenance`

The subject or object MAY reference another relation ID, allowing relation-of-relations.

## Causal status

Allowed baseline states:
- `causal`
- `non_causal`
- `possibly_causal`
- `mixed`
- `unknown`

`RELATION_NE_CAUSATION`
`UNKNOWN_CAUSE_NE_NO_RELATION`

## Null / absence relations

Absence is represented explicitly rather than by silently omitting an edge.

Baseline null predicates:
- `EXPECTED_BUT_MISSING`
- `IMPOSSIBLE`
- `FORBIDDEN`
- `UNKNOWN_RELATION`
- `NOT_YET_OBSERVED`
- `ONCE_EXISTED`
- `COUNTERFACTUALLY_PRESENT`

`NO_EDGE_NE_NO_INFORMATION`

## Relation transformation

A relation revision MUST preserve lineage rather than overwrite historical meaning.

A transformed relation SHOULD include:
- `supersedes_rel_id`
- `change_reason`
- `evidence_delta`
- `changed_by`
- `changed_at`

Supersession lineage MUST be acyclic.

`EVOLVING_RELATION_NE_HISTORY_ERASURE`
`SUPERSESSION_CYCLE_IS_INVALID`

## Concurrent revision conflicts

Multiple valid revisions MAY supersede the same prior relation. R0 preserves these as explicit sibling branches rather than silently selecting a winner.

When two or more revisions supersede the same relation, every sibling MUST include:
- `conflict_set_id`
- `conflict_status`

All siblings MUST share the same `conflict_set_id`.

Allowed baseline conflict states:
- `unresolved`
- `resolved`
- `superseded`
- `not_applicable`

An optional `resolution_note` MAY explain later adjudication.

`CONCURRENT_REVISION_NE_AUTOMATIC_WINNER`
`CONFLICT_NE_INVALIDITY`
`LATEST_TIMESTAMP_NE_TRUTH`
`MERGE_NE_ERASE_DISAGREEMENT`

## Boundary qualification

A relation or endpoint MAY be marked:
- `internal`
- `external`
- `boundary`
- `unknown_domain`

`COALL_NE_ALL_THAT_EXISTS`
`MODELLED_EXTERNALLY_NE_OWNED_BY_COALL`

## Query obligations

A useful relational substrate should support:
- what supports this?
- what contradicts this?
- what depends on this?
- what changed?
- what is stale?
- what is inferred only?
- what is unknown?
- what would break if this relation disappeared?
- what relation-of-relation claims modify this relation?
- what sibling revisions disagree?
- is a conflict unresolved, resolved, or superseded?

## R0 invariants

`RELATION_MUST_HAVE_PROVENANCE`
`CAUSAL_STATUS_MUST_BE_EXPLICIT`
`UNKNOWN_NE_FALSE`
`ABSENCE_NE_NO_INFORMATION`
`RELATION_ON_RELATION_MUST_REFERENCE_EXISTING_REL_IDS`
`TRANSFORMATION_MUST_PRESERVE_LINEAGE`
`RELATION_MODEL_MUST_SUPPORT_REVISION_WITHOUT_HISTORY_ERASURE`
`SIBLING_REVISIONS_MUST_EXPOSE_CONFLICT`
`EVERYTHING_MAY_RELATE_NE_EVERY_RELATION_IS_USEFUL`

## Anti-explosion rail

Potential relations may be combinatorially large. Active expansion SHOULD be selective and biased toward information gain, decision relevance, evidence gain, failure detection, or compression benefit.

`RELATION_DENSITY_NE_UNDERSTANDING`

## Non-goals

R0 does not:
- assert that all entities are reducible to relations;
- assert causal truth from sequence or correlation;
- claim CoAll contains all reality;
- define a complete ontology;
- define a universal graph engine;
- automatically resolve competing sibling revisions;
- grant authority merely because a relation is represented.

## Next

Exercise conflict resolution transitions, observer-relative disagreements, and time-qualified contradictions before any runtime promotion.
