# CoLineageCompactor+ R0

**State:** `CANDIDATE__DESIGN_ONLY__NO_LOCAL_MUTATION_NO_DELETION_NO_RUNTIME_ELECTION`

## Purpose

Convert high-volume historical artifact estates into bounded semantic lineage candidates without treating artifact count as concept importance or deleting reconstructive evidence.

This design is motivated by the bounded R0H filename census, where one generated family can dominate raw observations by orders of magnitude.

`ARTIFACT_COUNT_NE_SEMANTIC_DELTA_COUNT`
`COMPACTION_NE_DELETION`

## Input

A compaction run MAY consume bounded observations such as:

- source/custody identity;
- path or ZIP-member name;
- filename;
- bytes;
- modified/observed time;
- content hash when already available or safely elected;
- schema/version hints;
- stable identity hints;
- predecessor/successor hints;
- currentness/latest-pointer hints;
- source provenance;
- receiver scope.

Filename-only evidence remains filename-only evidence.

`FILENAME_MATCH_NE_SEMANTIC_EQUIVALENCE`

## Pipeline

```text
OBSERVE
 -> NORMALIZE
 -> FAMILY_CLUSTER
 -> GENERATION_CLUSTER
 -> REPRESENTATIVE_SAMPLE
 -> SEMANTIC_COMPARE
 -> LINEAGE_PROPOSE
 -> CHALLENGE
 -> FAN_IN
 -> RECEIVER_PROJECTION
```

### NORMALIZE

Normalize path separators, case only where source semantics permit, timestamp/run suffixes as candidate metadata rather than identity, and known generated-directory patterns.

Normalization MUST retain the original locator.

### FAMILY_CLUSTER

Group candidates by bounded evidence such as normalized path family, explicit stable ID, schema family, term/alias lineage, or known generator.

`CLUSTER_NE_IDENTITY`

### GENERATION_CLUSTER

Within a family, identify likely repeated generations while preserving temporal/provenance ordering.

Candidate states:

- `EQUIVALENT_GENERATION_CANDIDATE`
- `PROJECTION_ONLY_DELTA_CANDIDATE`
- `PROVENANCE_ONLY_DELTA_CANDIDATE`
- `SEMANTIC_TRANSITION_CANDIDATE`
- `DIVERGENCE_CANDIDATE`
- `CURRENT_DESCENDANT_CANDIDATE`

### REPRESENTATIVE_SAMPLE

Prefer bounded representatives:

- earliest observed ancestor;
- latest observed candidate;
- first/last per schema/version;
- points around large size/hash/path changes;
- explicit predecessor/successor boundaries;
- contradictions/divergences;
- deterministic interval samples when a family remains huge.

Sampling policy is provenance.

`SAMPLE_NE_INVENTORY`
`SAMPLING_POLICY_IS_PROVENANCE`

### SEMANTIC_COMPARE

Only this stage may propose semantic equivalence/delta, and only with content sufficient for the claim.

Local/open models MAY assist classification and summarization, but model output remains proposal/review evidence.

`MODEL_CLASSIFICATION_NE_SEMANTIC_TRUTH`
`LOCAL_NE_TRUSTED`

### LINEAGE_PROPOSE

Proposed relations MAY include:

- predecessor_of;
- successor_of;
- equivalent_generation_of;
- projection_of;
- derived_from;
- supersedes;
- contradicts;
- diverges_from;
- reconstructs_from;
- current_candidate_for;
- historical_donor_for.

`LATEST_TIMESTAMP_NE_ELECTED_SUCCESSOR`

### CHALLENGE + FAN_IN

A separate challenger/verifier SHOULD inspect high-impact merges, unresolved divergence, current-successor claims, and any compaction that would affect receiver-visible currentness.

## Output

A compactor SHOULD emit:

1. immutable run manifest;
2. source/scope/method metadata;
3. family clusters;
4. representative set;
5. proposed lineage edges;
6. unresolved ambiguities;
7. negative knowledge;
8. reconstruction pointers;
9. omitted-count summary;
10. receiver projection candidates;
11. exact nonclaims.

## Retention

R0 is **non-destructive**.

No source artifact is deleted, moved, rewritten, or demoted merely because it is classified as repetitive.

Future retention policy MAY migrate repetitive generations to colder custody only after:

- exact custody is known;
- reconstruction path is tested;
- retention/authority policy permits it;
- successor/currentness is separately proven;
- rollback is possible.

`COLD_NE_DELETED`
`COMPACTED_NE_UNRECOVERABLE`
`RETENTION_NE_CURRENTNESS`

## Parallelism

Compaction is naturally shardable by family/source/time window.

Workers MAY run in parallel where collision domains do not overlap. Fan-in MUST preserve deterministic cluster IDs and unresolved conflicts.

`MASSIVE_PARALLELISM_NE_MASSIVE_SIMULTANEOUS_MATERIALIZATION`
`PARALLEL_CLASSIFICATION_REQUIRES_DETERMINISTIC_FANIN`

## Local-model role

Qwen/Ollama or successor local workers are candidate low-authority classifiers for:

- family naming;
- semantic-delta proposal;
- duplicate/equivalent-generation proposal;
- representative rationale;
- contradiction flagging;
- summary generation.

They MUST NOT independently delete, publish, elect canon, broaden authority, or decide privacy.

## First canary

Use one bounded high-volume family, preferably CoPulse, but only a deterministic slice.

Candidate canary:

- source: R0H observations;
- select one path family with >= 100 generations;
- retain first, last, schema/version boundaries, large-change boundaries, and deterministic interval samples;
- content-read only those representatives if authority/scope permits;
- ask local worker for semantic-delta proposals;
- independently verify;
- emit lineage candidate + reconstruction pointers;
- mutate nothing.

## Integration

Candidate consumers:

- CoLivingHighlight+;
- CoSubscriptionEcology+;
- CoAllPulseField+;
- CoIndex / GIBindex;
- CoLex / CoMeaning;
- CoSourceGraph+;
- CoMemoryEcology+;
- CoConfluence+;
- CoDrift+;
- RickBar / CoFleet.

## Rails

`ARTIFACT_COUNT_NE_SEMANTIC_DELTA_COUNT`  
`COMPACTION_NE_DELETION`  
`FILENAME_MATCH_NE_SEMANTIC_EQUIVALENCE`  
`CLUSTER_NE_IDENTITY`  
`SAMPLE_NE_INVENTORY`  
`SAMPLING_POLICY_IS_PROVENANCE`  
`MODEL_CLASSIFICATION_NE_SEMANTIC_TRUTH`  
`LATEST_TIMESTAMP_NE_ELECTED_SUCCESSOR`  
`COLD_NE_DELETED`  
`COMPACTED_NE_UNRECOVERABLE`  
`PARALLEL_CLASSIFICATION_REQUIRES_DETERMINISTIC_FANIN`
