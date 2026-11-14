# CoRelKernel R0 x CoRelationField PR127 convergence crosswalk R0

**State:** `CANDIDATE_COLLISION_RECONCILIATION__NO_CANON_NO_RUNTIME_NO_MERGE_AUTHORITY`

## Why this exists

Two live candidates now overlap materially:

- PR #128: `CoRelKernel R0: minimal causal + non-causal relational substrate`
- PR #127 frozen review snapshot: `95db06101b16954a90468c5ef4f1b4e78a3195a5`
  via `review/corelation-field-pr127-95db0610`

They should not silently harden into two competing generic relation ontologies.

`PARALLEL_SCHEMA_NE_DESIRED_ENDSTATE`

## Proposed division of responsibility

### CoRelKernel R0

Candidate role:

**minimal relation atom + relation-history/conflict semantics**

Owns, or is the preferred donor for:

- `subject / predicate / object` relation atom;
- relation references as endpoints;
- provenance requirement;
- observer qualification;
- validity / observation time;
- explicit contradiction basis;
- supersession lineage;
- concurrent sibling revision conflicts;
- conflict sets;
- conflict resolution as a new relation;
- boundary qualification;
- anti-explosion rails.

### CoRelationField PR127

Candidate role:

**field-level typing + projection/transform/adapter semantics**

Owns, or is the preferred donor for:

- `relation_family`;
- more explicit causal-status distinctions;
- typed negative-space relata such as absence, non-event, boundary, unknown and counterfactual;
- relation-as-relatum depth accounting;
- projection selected/omitted relation accounting;
- declared projection loss;
- transform source/output lineage;
- declared transform loss;
- pointer-only adapters into CoOpenRelation, CoEncounter, CoResearchEvidence, CoTime, CoEvoDelta and CoSubstrateField;
- receiver pickup/integration/portability proof patterns;
- RDF / PROV / SHACL interoperability posture.

## Candidate layered shape

```text
CoRelKernel relation atom
        |
        v
CoRelationField field envelope
        |
        +--> projections / transforms
        +--> domain-carrier adapters
        +--> evidence / time / observer views
        +--> external RDF / PROV / SHACL projections
```

This is a candidate contraction, not an elected architecture.

`KERNEL_NE_FIELD`  
`FIELD_NE_KERNEL`  
`LAYERING_CANDIDATE_NE_CANON`

## Causal-status mapping is not one-to-one

PR128 currently uses:

- `causal`
- `non_causal`
- `possibly_causal`
- `mixed`
- `unknown`

PR127 currently uses:

- `CAUSAL_SUPPORTED`
- `CAUSAL_CANDIDATE`
- `NONCAUSAL`
- `COMMON_CAUSE_CANDIDATE`
- `COUNTERFACTUAL_DEPENDENCE`
- `CONSTRAINT_RELATION`
- `UNKNOWN_CAUSAL_STATUS`
- `CAUSALITY_NOT_APPLICABLE`

Candidate safe projection:

| CoRelKernel | CoRelationField | Notes |
| --- | --- | --- |
| `causal` | `CAUSAL_SUPPORTED` or `CAUSAL_CANDIDATE` | requires evidence/mechanism distinction |
| `possibly_causal` | `CAUSAL_CANDIDATE` | closest bounded mapping |
| `non_causal` | `NONCAUSAL` | only when non-causality is actually supported |
| `mixed` | no lossless single value | preserve source + declare loss |
| `unknown` | `UNKNOWN_CAUSAL_STATUS` or `CAUSALITY_NOT_APPLICABLE` | depends on relation family/context |

`MAPPING_NE_EQUIVALENCE`  
`UNKNOWN_NE_CAUSALITY_NOT_APPLICABLE`  
`NONCAUSAL_NE_UNKNOWN_CAUSE`

## Important collision findings

### 1. Revision/conflict semantics are materially stronger in PR128

PR128 carries explicit:

- `supersedes_rel_id`;
- change reason / actor / time;
- sibling conflict sets;
- conflict status;
- resolution relations;
- observer/time-qualified contradiction.

PR127 should not independently reinvent these if PR128 survives review.

Candidate disposition:

`REVISION_AND_CONFLICT_SEMANTICS_PREFER_CORELKERNEL_DONOR`

### 2. Projection/transform loss semantics are materially stronger in PR127

PR127 carries:

- selected + omitted relation IDs;
- explicit projection loss;
- transform source/output IDs;
- source mutation false by default;
- transform loss/provenance;
- projection/source separation rails.

PR128 should not independently grow parallel projection machinery if PR127 survives review.

Candidate disposition:

`PROJECTION_AND_TRANSFORM_LOSS_PREFER_CORELATIONFIELD_DONOR`

### 3. Negative-space treatment differs

PR128 expresses null/absence primarily through predicates such as:

- `EXPECTED_BUT_MISSING`
- `IMPOSSIBLE`
- `FORBIDDEN`
- `UNKNOWN_RELATION`
- `NOT_YET_OBSERVED`
- `ONCE_EXISTED`
- `COUNTERFACTUALLY_PRESENT`

PR127 additionally types negative-space relata:

- `ABSENCE`
- `NON_EVENT`
- `MISSING_EVIDENCE`
- `BOUNDARY`
- `UNKNOWN`
- `COUNTERFACTUAL`

Neither encoding should silently replace the other until a fixture proves whether predicate-only, typed-relatum, or dual representation preserves more semantics with less complexity.

`ABSENCE_PREDICATE_NE_ABSENCE_RELATUM`  
`DUAL_ENCODING_REQUIRES_COLLISION_TEST`

### 4. Meta-relation cycle rules differ in emphasis

PR127 R0 currently holds the **relation-as-relatum dependency graph** acyclic so `meta_depth` is finite and mechanically provable, while ordinary relation-field cycles remain allowed.

PR128 allows relation references but does not currently impose that same explicit meta-depth model.

Candidate convergence test should distinguish:

- ordinary graph cycles;
- supersession cycles;
- relation-reference cycles;
- recursive nesting depth;
- stable-ID cyclic references.

`FIELD_CYCLE_NE_META_REFERENCE_CYCLE`  
`SUPERSESSION_CYCLE_NE_RELATION_CYCLE`

### 5. Schema philosophy differs

PR128 is deliberately minimal and permissive, with `additionalProperties: true`.

PR127 is deliberately more typed and closed in several envelopes.

That tension is useful and should be tested, not resolved by taste.

Candidate question:

**Can CoRelKernel remain a small stable atom while CoRelationField carries stricter field/profile constraints?**

`MINIMAL_KERNEL_NE_PERMISSIVE_EVERYWHERE`  
`FIELD_PROFILE_NE_KERNEL_REWRITE`

## Merge / promotion posture

Neither PR should be merged merely because both are green.

Until convergence is adjudicated:

- PR127 remains frozen for distinct semantic review;
- PR128 remains draft;
- neither candidate should claim generic-relation canon;
- no newest-wins rule applies;
- closing either PR before harvesting unique semantics would discard useful work.

`GREEN_CI_NE_COLLISION_RESOLUTION`  
`NEWEST_NE_WINNER`  
`DUPLICATE_LANE_NE_DUPLICATE_VALUE`

## Next bounded proof

Build one **translation/collision fixture** that instantiates the same semantic cases in both candidates:

1. direct causal relation;
2. possible/unknown causal relation;
3. typed absence;
4. relation-about-relation;
5. observer disagreement;
6. time-qualified contradiction;
7. sibling revisions;
8. conflict resolution;
9. projection loss;
10. transform lineage.

The canary should report:

- lossless mappings;
- lossy mappings;
- unmappable fields;
- semantic collisions;
- duplicate responsibilities;
- candidate ownership by layer.

No automatic merge or schema replacement should follow from that canary.

## Rails

`PARALLEL_SCHEMA_NE_DESIRED_ENDSTATE`  
`KERNEL_NE_FIELD`  
`FIELD_NE_KERNEL`  
`MAPPING_NE_EQUIVALENCE`  
`NEWEST_NE_WINNER`  
`GREEN_CI_NE_COLLISION_RESOLUTION`  
`COLLISION_REVIEW_NE_MERGE_AUTHORITY`  
`CROSSWALK_NE_CANON`  
`CROSSWALK_NE_RUNTIME`
