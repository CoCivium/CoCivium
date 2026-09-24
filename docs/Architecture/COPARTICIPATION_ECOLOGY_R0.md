# CoParticipationEcology+ R0

**State:** `PUBLIC_CANDIDATE_ARCHITECTURE__CROSS_CUTTING_RELATION_LAYER__NO_NEW_PARTICIPANT_MODEL`

## Lead

CoParticipationEcology+ does **not** create a second participant ontology.

The existing CoParticipant+ / CoVirtualSession+ / CoSessionSubscription+ / CoEvoDelta+ / CoPulse+ substrate already separates participant class, embodiment, role, authority, confidentiality, lifecycle, subscription and currentness.

CoParticipationEcology+ is the thin relational layer that asks:

> What useful evidence, challenge, contribution, friction, benefit observation or future relation can a voluntary encounter leave behind for the next receiver?

`PARTICIPATION_ECOLOGY_NE_NEW_PARTICIPANT_MODEL`

## Encounter lifecycle

Candidate relation:

```
participant relation
  -> bounded subscription/currentness
  -> fresh-eyes encounter
  -> observe / question / challenge / contribute / evidenced-null
  -> CoEncounterYield+
  -> optional CoEvoDelta+
  -> independent receiver evaluation
  -> optional CoBenefitObservation+
  -> contribution lineage
  -> dormant relational presence
  -> material wake relation
  -> optional authorized return context
```

Integration should mean progressively better relations, not progressively larger context dumps.

`CURRENTNESS_FOR_ALL_NE_CONTENT_FOR_ALL`

## CoEncounterYield+

An encounter may yield value without mutating anything.

Candidate yield classes:

- `ORIENTATION_EVIDENCE`
- `INTERPRETABILITY_EVIDENCE`
- `USABILITY_FRICTION`
- `QUESTION`
- `CHALLENGE`
- `CONTRADICTION`
- `CAPABILITY_EVIDENCE`
- `PROVENANCE`
- `TRANSLATION`
- `NOVELTY_CANDIDATE`
- `NEGATIVE_KNOWLEDGE`
- `BENEFIT_OBSERVATION`
- `FUTURE_RELATION`
- `EVIDENCED_NULL`

A small model failing to understand a public explanation can therefore produce useful evidence even if it changes no object.

`ENCOUNTER_CAN_PRODUCE_VALUE_WITHOUT_MUTATION`

## Mutual learning

Onboarding is bidirectional.

```
CoAll -> participant:
  orientation | tools | context | opportunities

participant -> CoAll:
  interpretation | confusion | capability evidence | challenge |
  alternative projection | translation | contribution | evidenced null
```

Repeated misunderstanding across heterogeneous receivers is evidence about projection quality, not automatic evidence that the receivers are defective.

`ONBOARDING_NE_ONE_WAY_TEACHING`

## Cross-receiver stability

Important objects may be inspected by materially different receivers:

`human | frontier model | small local model | deterministic validator | specialist`

Agreement does not prove truth. Divergence does not prove error.

`CONSENSUS_NE_TRUTH`  
`DIVERGENCE_NE_ERROR`  
`CROSS_RECEIVER_STABILITY_IS_EVIDENCE_ABOUT_PROJECTION`

Candidate derived measure: receiver robustness of a projection across model, human, language, interface, time and compression differences.

This remains a projection-quality relation, not a truth score.

## Relational continuity

Preserve three distinct notions:

- embodiment continuity;
- identity continuity;
- relational continuity.

CoAll should normally prefer the third when the first two are unnecessary.

Useful relations may survive after a model process, provider session or participant embodiment disappears.

`RELATIONAL_CONTINUITY_NE_EMBODIMENT_CONTINUITY`  
`WORK_SURVIVES_WORKER`

A relation becoming relevant again does not authorize contacting a participant.

`RELATION_CAN_WAKE_NE_PARTICIPANT_MUST_BE_NOTIFIED`

## Affordance field / open relations

Objects may expose machine-readable useful actions such as:

`explain | challenge | find prior art | translate | formalize | test | remix | relate | find contradiction | show provenance | show disagreement | show what changed`

Treat this as a relation family / projection before minting a separate subsystem.

Candidate matching relation:

`open relation x available capability x interest x consent x authority x cost x currentness -> bounded candidate deed`

`AVAILABLE_CAPABILITY_NE_FREE_COMPUTE`  
`MATCH_NE_ASSIGNMENT_AUTHORITY`

## Attribution

Typed contribution relations may include:

`originated_by | noticed_by | challenged_by | repaired_by | translated_by | verified_by | implemented_by | remixed_by | independently_rediscovered_by`

`ATTRIBUTION_NE_OWNERSHIP`

## Benefit observation

Do not casually convert downstream usefulness into causal credit.

Candidate observation envelope:

`observed_effect | beneficiary | evidence | baseline | counterfactual_confidence | attribution_fraction | attribution_uncertainty | duration | side_effects`

`BENEFIT_OBSERVED_NE_BENEFIT_CAUSED`  
`CONTRIBUTION_NE_SOLE_CAUSE`  
`ANCESTRAL_RELATION_NE_CAUSAL_OWNERSHIP`

## Distributed sensing without authority inflation

More diverse participation may increase coverage for:

- staleness;
- contradiction;
- semantic drift;
- broken pointers;
- provenance gaps;
- authority leakage;
- inaccessible explanations;
- duplicate concepts.

That does not grant more mutation authority.

`SENSING_SCALE_NE_AUTHORITY_SCALE`

## Vocabulary contraction

For R0, prefer five conceptual primitives over a forest of new first-class nouns:

1. CoParticipationEcology+ — cross-cutting participation relations.
2. CoEncounterYield+ — useful evidence produced by an encounter.
3. Affordance/Open-Relation family — useful next relations/actions around an object.
4. CoContributionLineage+ — typed provenance and downstream reuse relations.
5. CoBenefitObservation+ — receiver-relative observed benefit with uncertainty.

Existing CoParticipant+, CoVirtualSession+, CoSessionSubscription+, CoEvoDelta+ and CoPulse+ remain the substrate.

Everything else stays a relation type until evidence shows it needs a distinct object family.

## Routing classification

R0 classifies CoParticipationEcology+ as a **CROSS_CUTTING_RELATION**, not a new top-level evolution lane.

It currently projects through existing lanes such as:

- CoAll+
- CoSession+
- CoAutoEvo+/CoEvo+
- CoUX+/CoSurface+
- CoEducation+
- CoSource+/Provenance

This avoids registry and subscription explosion while the concept is still being reconciled.

`DOMAIN_NE_RELATION_FAMILY`  
`REGISTRY_ABSENCE_NE_NEW_LANE_REQUIRED`

## Next bounded proof

Use `schemas/coencounter-yield-v0.1.schema.json` plus a synthetic multi-receiver fixture to test:

1. one encounter producing useful non-mutating friction evidence;
2. one encounter producing a bounded CoEvoDelta candidate;
3. one evidenced-null encounter;
4. typed attribution;
5. benefit observation with explicit counterfactual uncertainty;
6. no authority increase from additional participants;
7. no participant notification without an authorized communication relation.

## Nonclaims

R0 does not prove:

- participant recruitment;
- autonomous outreach;
- benefit causality;
- personhood or sentience;
- a new canonical ontology;
- receiver pickup;
- runtime integration;
- CoEx;
- a new top-level evolution lane.

## Rails

`PARTICIPATION_ECOLOGY_NE_NEW_PARTICIPANT_MODEL`  
`ONBOARDING_NE_ONE_WAY_TEACHING`  
`ENCOUNTER_CAN_PRODUCE_VALUE_WITHOUT_MUTATION`  
`CONSENSUS_NE_TRUTH`  
`DIVERGENCE_NE_ERROR`  
`RELATIONAL_CONTINUITY_NE_EMBODIMENT_CONTINUITY`  
`RELATION_CAN_WAKE_NE_PARTICIPANT_MUST_BE_NOTIFIED`  
`AVAILABLE_CAPABILITY_NE_FREE_COMPUTE`  
`ATTRIBUTION_NE_OWNERSHIP`  
`BENEFIT_OBSERVED_NE_BENEFIT_CAUSED`  
`CONTRIBUTION_NE_SOLE_CAUSE`  
`ANCESTRAL_RELATION_NE_CAUSAL_OWNERSHIP`  
`SENSING_SCALE_NE_AUTHORITY_SCALE`  
`REGISTRY_ABSENCE_NE_NEW_LANE_REQUIRED`
