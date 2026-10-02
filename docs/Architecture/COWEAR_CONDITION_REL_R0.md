# CoWear+ / CoConditionRel+ R0

**State:** `CANDIDATE_CROSS_DOMAIN_CONDITION_TRAJECTORY__NO_CANON_NO_RUNTIME_NO_AUTHORITY_CHANGE`

## Lead

Yes: shoes wear down.

The useful generalization is not that everything is literally a shoe. It is that many CoAll objects have **condition trajectories** whose changes can be observed, estimated, maintained, repaired, reframed, replaced, retired, or predicted.

~~~text
object
  + time
  + use
  + load/stress
  + environment
  + maintenance
  + upstream relations
        ↓
time-indexed condition field
        ↓
observe / maintain / repair / replace / retire / predict
~~~

## Shoes first, because reality occasionally provides a decent metaphor

A shoe can lose tread through abrasion, cushioning through compression set, flexibility through material aging, adhesive integrity through chemistry/environment, and upper integrity through flex/fatigue.

An unused shoe can age without accumulating use-wear.

A cleaned shoe can improve in cleanliness without regrowing tread.

A resoled shoe can improve materially while still preserving the same system identity for a bounded purpose.

`AGE_NE_WEAR`

`USE_NE_DAMAGE`

`WEAR_NE_FAILURE`

`MAINTENANCE_NE_RESTORE_ORIGINAL`

## CoWear+ is typed, not one magic decay number

Candidate cause families include abrasion, fatigue, compression set, chemical aging, environmental degradation, dependency drift, data staleness, semantic overuse, and attention fatigue.

The mechanism matters. A software API does not have rubber tread. A metaphor does not oxidize. Cross-domain relation does not mean causal equivalence.

`METAPHOR_NE_MECHANISM`

`CROSS_DOMAIN_ANALOGY_NE_CAUSAL_EQUIVALENCE`

## CoConditionRel+

A condition relation should be time-indexed and dimensioned:

~~~text
(object, dimension, observation-time)
  -> observed value
  -> evidence/provenance
  -> uncertainty
  -> cause candidates
  -> maintenance history
  -> predicted trajectory
~~~

Physical dimensions may include abrasion, fatigue, structural integrity, chemical integrity, and compression.

Software dimensions may include compatibility, dependency currentness, test health, security posture, and interface stability.

Information dimensions may include currentness, coverage, proof freshness, and semantic precision.

Operational dimensions may include receiver health, proof debt, collision rate, recovery time, and attention cost.

No single condition score should pretend to be total value.

`CONDITION_NE_VALUE`

## Semantic wear

Words, metaphors, interfaces, labels, and CoTerms can become less useful through repeated loading across too many contexts.

~~~text
novel / sharp
-> useful
-> heavily reused
-> overloaded
-> ambiguous
-> distorting
~~~

Possible interventions include reframe, alias, split meanings, scope, version, retire for a context, and preserve lineage.

`SEMANTIC_OVERUSE_NE_FALSEHOOD`

A worn metaphor may still contain useful history.

## Maintenance and repair

Maintenance can alter future condition without erasing prior wear.

Repair can restore one dimension while leaving others unchanged.

Replacement can improve local condition while creating migration, proof, compatibility, cost, or identity risks.

`REPAIR_NE_HISTORY_ERASURE`

`REPLACEMENT_NE_PROGRESS`

`MAINTENANCE_NE_FOREVER`

Sometimes the correct deed is repair. Sometimes replace. Sometimes leave alone. Sometimes gracefully retire.

## CoTime+ prediction

Condition history can feed bounded predictive models:

~~~text
observations over time
-> rate / hazard candidates
-> confidence bounds
-> repair or replacement window
-> next observation
-> prediction revision
~~~

The output should usually be a window with assumptions, not a prophecy.

`PREDICTED_EOL_NE_CERTAINTY`

For shoes, tread might support a replacement window. For software, dependency/currentness trajectories might support a maintenance window. For evidence, proof freshness might support revalidation timing. For metaphors, semantic drift might support reframe or retire suggestions.

## Cross-CoAll implication

Condition should become a relation available to many object classes rather than a hardware-only field.

Possible later extensions include `CoDecayBudget+`, `CoMaintenanceWindow+`, `CoGracefulAging+`, `CoRepairability+`, `CoReplaceability+`, `CoEphemerality+`, `CoConditionForecast+`, `CoWearMap+`, `CoFreshnessHalfLife+`, and `CoSemanticPatina+`.

That last one matters: wear is not always bad. A shoe can mold to a foot; a tool handle can gain familiarity; a term may accumulate useful history. Condition evolution can improve one dimension while degrading another.

## R0 canary

Seven deterministic scenarios test active footwear abrasion/compression, stored footwear aging without use, maintenance improving one dimension without rewinding another, software dependency drift, semantic overuse, replacement without automatic progress, and an uncertainty-bounded predictive end-of-life window.

## Current boundary

This candidate mutates no hardware, schedules no maintenance, makes no medical claim, predicts no real shoe failure, and changes no runtime policy.

It is an architectural donor only.

## Rails

`AGE_NE_WEAR`  
`USE_NE_DAMAGE`  
`WEAR_NE_FAILURE`  
`OLD_NE_OBSOLETE`  
`MAINTENANCE_NE_FOREVER`  
`MAINTENANCE_NE_RESTORE_ORIGINAL`  
`REPAIR_NE_HISTORY_ERASURE`  
`REPLACEMENT_NE_PROGRESS`  
`CONDITION_NE_VALUE`  
`VISIBLE_WEAR_NE_TOTAL_CONDITION`  
`SEMANTIC_OVERUSE_NE_FALSEHOOD`  
`PREDICTED_EOL_NE_CERTAINTY`  
`METAPHOR_NE_MECHANISM`  
`CONDITION_MODEL_NE_REALITY_TOTALITY`  
`VALIDATION_IS_NOT_ACCEPTANCE`


## R0A semantic compaction into CoRelIR

The cross-domain terms in this candidate should not automatically become new ontology primitives merely because they are memorable.

R0A projects them onto a compact candidate semantic nucleus:

`ENTITY | RELATION | EVENT | STATE | TIME | OBSERVER | CONTEXT | EVIDENCE | PROVENANCE | AUTHORITY | UNCERTAINTY | POSSIBILITY | TRANSFORMATION | PROJECTION`

Classification:

- `CoWear+` -> relation family over time/context/evidence/uncertainty;
- `CoConditionRel+` -> condition relation envelope, not a new object kind;
- `CoMaintenance+` -> event/transformation pattern;
- `CoRetirement+` -> scoped state-transition policy pattern;
- `CoConditionForecast+` -> projection/possibility pattern with uncertainty;
- `CoSemanticPatina+` -> optional metaphor/alias over accumulated semantic history.

None is elected as a new primitive in R0A.

This is deliberate ontology pressure relief:

```text
new useful phrase
   !=
new primitive

prefer:
  existing primitive roots
  + typed relation
  + qualifier
  + operator/pattern
  + projection
  + provenance
```

The seven existing CoWear scenarios are all projected through this nucleus. The projection preserves their distinctions while blocking several category errors:

`FORECAST_NE_STATE`

`POSSIBILITY_NE_FACT`

`TRANSFORMATION_NE_IMPROVEMENT`

`CONDITION_TRAJECTORY_NE_OBJECT_IDENTITY`

`COTERM_NE_PRIMITIVE_BY_DEFAULT`

`COMPACTION_NE_INFORMATION_ERASURE`

This is a candidate compaction projection only. It does not establish CoRelIR as canon, runtime schema, or universal ontology.
