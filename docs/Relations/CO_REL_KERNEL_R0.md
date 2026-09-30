# CoRelKernel R0

**State:** `CANDIDATE__PUBLIC_RND__NOT_CANON__NOT_RUNTIME_AUTHORITY`

## Purpose

CoRelKernel R0 is a minimal relational substrate for representing causal, non-causal, meta, null/absence, boundary-crossing, observer-relative, time-qualified, conflicting concurrent relation revisions, and explicit conflict resolutions without erasing provenance or uncertainty.

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

## Concurrent revision conflicts

Sibling revisions that supersede the same prior relation MUST expose one shared `conflict_set_id` and a `conflict_status`.

Allowed states:
- `unresolved`
- `resolved`
- `superseded`
- `not_applicable`

R0 preserves conflicting siblings rather than selecting a winner implicitly.

## Conflict resolution as a relation

A resolution is represented as a new relation, not by deleting or silently rewriting the conflicting siblings.

A resolution relation MUST:
- use predicate `RESOLVES_CONFLICT`;
- name the target set in `resolves_conflict_set_id`;
- point via its object `rel_ref` to a member of that conflict set;
- carry provenance;
- carry a non-empty `resolution_note`.

This makes adjudication itself queryable and revisable.

## Other invariants

`RELATION_MUST_HAVE_PROVENANCE`  
`CAUSAL_STATUS_MUST_BE_EXPLICIT`  
`UNKNOWN_NE_FALSE`  
`ABSENCE_NE_NO_INFORMATION`  
`RELATION_ON_RELATION_MUST_REFERENCE_EXISTING_REL_IDS`  
`TRANSFORMATION_MUST_PRESERVE_LINEAGE`  
`SIBLING_REVISIONS_MUST_EXPOSE_CONFLICT`  
`CONFLICT_RESOLUTION_MUST_REFERENCE_EXISTING_CONFLICT_MEMBER`  
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

Exercise observer-relative disagreement and time-qualified contradiction, then consider extracting stable validator semantics into a reusable relation library before any runtime promotion.
