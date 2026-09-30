# CoRelKernel R0

**State:** `CANDIDATE__PUBLIC_RND__NOT_CANON__NOT_RUNTIME_AUTHORITY`

## Purpose

CoRelKernel R0 is a minimal relational substrate for representing causal, non-causal, meta, null/absence, boundary-crossing, observer-relative, and time-qualified relations without erasing provenance or uncertainty.

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

`EVOLVING_RELATION_NE_HISTORY_ERASURE`

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

## R0 invariants

`RELATION_MUST_HAVE_PROVENANCE`
`CAUSAL_STATUS_MUST_BE_EXPLICIT`
`UNKNOWN_NE_FALSE`
`ABSENCE_NE_NO_INFORMATION`
`RELATION_ON_RELATION_MUST_REFERENCE_EXISTING_REL_IDS`
`TRANSFORMATION_MUST_PRESERVE_LINEAGE`
`RELATION_MODEL_MUST_SUPPORT_REVISION_WITHOUT_HISTORY_ERASURE`
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
- grant authority merely because a relation is represented.

## Next

Validate the schema and fixtures, then add deterministic checks for lineage, causal-status explicitness, null-relation typing, and relation-on-relation referential integrity before any runtime promotion.
