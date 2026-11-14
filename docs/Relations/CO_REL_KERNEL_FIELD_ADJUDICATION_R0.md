# CoRelKernel x CoRelationField collision adjudication R0

**State:** `CANDIDATE_COLLISION_ADJUDICATION__NO_CANON_NO_RUNTIME_NO_MERGE_AUTHORITY`

## Purpose

The exact collision canary between PR128 and frozen PR127 left two ownership decisions unresolved:

1. causal-status vocabulary;
2. absence / negative-space representation.

This R0 adjudication resolves **layer ownership**, not semantic equivalence and not schema promotion.

## D01: causal status is layered

CoRelKernel keeps a deliberately coarse source-facing causal status:

- `causal`
- `possibly_causal`
- `non_causal`
- `unknown`
- `mixed`

CoRelationField keeps the richer profile interpretation:

- `CAUSAL_SUPPORTED`
- `CAUSAL_CANDIDATE`
- `NONCAUSAL`
- `COMMON_CAUSE_CANDIDATE`
- `COUNTERFACTUAL_DEPENDENCE`
- `CONSTRAINT_RELATION`
- `UNKNOWN_CAUSAL_STATUS`
- `CAUSALITY_NOT_APPLICABLE`

The translation adapter owns the partial mapping.

Most important safety rule:

```text
kernel causal
  -> field CAUSAL_CANDIDATE by default

field CAUSAL_SUPPORTED
  requires field-side supported-causal criteria
  and MUST NOT be inferred from the kernel word "causal" alone
```

Likewise:

- kernel `unknown` maps by default to `UNKNOWN_CAUSAL_STATUS`, not `CAUSALITY_NOT_APPLICABLE`;
- kernel `mixed` has no lossless single field value;
- kernel `non_causal` may map to `NONCAUSAL` as the preserved source claim, with source provenance and epistemic qualification intact.

`KERNEL_CAUSAL_STATUS_NE_FIELD_CAUSAL_STATUS`  
`CAUSAL_NE_CAUSAL_SUPPORTED_BY_TRANSLATION`  
`UNKNOWN_NE_CAUSALITY_NOT_APPLICABLE`  
`MIXED_NE_FORCED_SINGLE_FIELD_VALUE`

## D02: absence uses dual layering

The two candidates encode useful but different things.

### Kernel role

A kernel predicate such as:

`EXPECTED_BUT_MISSING`

expresses an absence **claim / observation relation**.

### Field role

A typed `ABSENCE` relatum is useful when the absence itself must participate in additional relations, for example:

- blocks an action because permission is absent;
- is supported/challenged by evidence;
- changes across observer/time/scope;
- is projected into another semantic view.

R0 therefore does **not** reify every absence predicate automatically.

When translation genuinely needs a field-level absence participant, the adapter may create a projection-scoped `ABSENCE` relatum bound to exact source provenance and explicit scope.

That projection identity is not proof that an independent metaphysical entity called “the absence” exists.

`ABSENCE_PREDICATE_NE_ABSENCE_RELATUM`  
`ABSENCE_RELATUM_NE_INDEPENDENT_ENTITY_CLAIM`  
`DUAL_REPRESENTATION_NE_DUPLICATE_TRUTH`  
`ABSENCE_NE_NONEXISTENCE`  
`NO_EVIDENCE_NE_EVIDENCE_OF_ABSENCE`

## Result

The prior collision matrix had two unresolved ownership decisions.

R0 candidate result:

```text
ownership_unresolved_before = 2
ownership_unresolved_after  = 0

semantic_non_equivalence_remaining = true
schema_mutation_required_now       = false
```

Candidate division:

```text
CoRelKernel
  minimal relation atom
  observer/time
  revision/conflict/resolution

CoRelationField
  richer field typing
  negative-space participants
  projection/transform loss
  domain adapters

Translation adapter
  explicit partial mapping
  declared loss
  no semantic upgrades by convenience
```

This is contraction rather than another schema-growth wave.

## Next gate

Do not mutate either schema merely to make their vocabularies look alike.

Next useful proof is a **translation canary** implementing these two policies on synthetic exact cases and proving:

- no `causal -> CAUSAL_SUPPORTED` automatic promotion;
- `unknown` does not become `CAUSALITY_NOT_APPLICABLE` automatically;
- `mixed` fails closed without an explicit composite strategy;
- absence reification occurs only when the destination relation needs an absence participant;
- every generated absence relatum retains exact source provenance and nonexistence nonclaims.

## Rails

`ADJUDICATION_NE_CANON`  
`OWNERSHIP_POLICY_RESOLVED_NE_SEMANTIC_EQUIVALENCE`  
`TRANSLATION_RULE_NE_TRUTH`  
`COLLISION_RESOLUTION_NE_MERGE_AUTHORITY`  
`SCHEMA_SIMILARITY_NE_CONVERGENCE`
