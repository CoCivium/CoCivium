# CoMeasureFabric+ / CoPriMath+ | Typed Relational Measure Fabric R0

**2026-11-08 | PUBLIC REVIEW CANDIDATE | SOURCE-ONLY | NOT A NEW SI, MATHEMATICAL THEOREM, GOVERNING ONTOLOGY, RUNNING ENGINE, OR RECEIVER ACK**

**Intended integration:** [CoMeasureFabric issue #367](https://github.com/CoCivium/CoCivium/issues/367) owns the measure-registry proposal; [CoEvoRate comparison R0](COEVORATE_COMPARATIVE_FITNESS_R0_20261108.md) consumes its qualified measures. This is a bridge, not an independent unit authority. Also reuse [CoNull+](../../examples/conotspace/README.md), [CoBaseline](../Architecture/COBASELINE_FRONTIER_REGISTRY_R0_20261027.md), [CoOrb boundary/CoTime](../Architecture/COORB_BOUNDARY_TEMPORAL_FIELD_R0_20261108.md), [G_dSide/CoPriMath](../Evolution/GDSIDE_COPRIMATH_GSLOOP_PUBLIC_R0.md) and [CoStageReview](../Architecture/COREVIEW_PANEL_LIFECYCLE_R0.md).

## Thesis: shared typing, not one universal numerical measure

We can **connect descriptions and equations in a common typed, versioned relational fabric**. We cannot infer that every entity has a meaningful numerical unit, every pair is causally connected, all units are convertible, or a comprehensive graph has already been discovered.

CoPriMath should treat a measure as one *interface* on a much broader relational object. Dimensional analysis catches physical impossibilities, while meaning, context, causal assumptions, rights and evidence determine whether a permissible computation is also a valid conclusion.

Not only G_d and CoNull anchor the work. Independent foundations include identity/reference, logic and mathematics, types/units, evidence/provenance, space/reference frames, CoTime/ordering, causal model, observer, uncertainty, consent/authority, scope/boundaries and reversibility. None should silently inherit authority from another. G_d remains an optional philosophical/counterfactual benevolence orientation, not a physical base unit, experimentally observed source, cosmic instruction, or truth oracle. CoNull is typed missingness/negative epistemic state, not numeric 0 or a universal origin.

## The core grammar: CoClaim, CoMetric, CoRelation, CoProof

**CoClaim:** subject, predicate, object, quantification scope, domain, model assumptions, frame, validity interval, provenance, evidence for/against, version, authority.

**CoMetricDefinition:** stable ID + definition version; measurand; semantic quantity kind; value domain (ratio / interval / ordinal / nominal / boolean / probability / distribution / symbolic / vector / tensor / event); **physical dimension** (where applicable); standard unit; scale and zero reference; denominator / cohort; measurement method; calibration; observable versus anticipated; reference frame; independent replicability; uncertainty/error model; privacy, consent and allowed uses; source time and supersession.

**CoObservation:** reference to a specific metric-definition version, subject and eligible scope, **measured value or typed CoNull**, observation method and instrument version, event/observed/recorded/valid time and clock, evidence/custody identity, uncertainty, independence, authorization and exact source. Prediction is a different claim type with horizon, distribution, falsifier and future reconciliation.

**CoRelation:** stable ID, typed source and target, link kind, preconditions, evidence class, causality status, reference-frame mapping, admissible transformations, dimensional and semantic guards, uncertainty propagation, time/lag assumptions, reversibility or inverse, budget and falsifiers. Relations may connect other relations (hyperedges), but materialization must be bounded. Unknown links are **questions**, not traversable proof edges.

**CoProof:** reproducible computation or observation, source identity, independent witness/receiver when claimed, negative controls, counterevidence, version, expiry and scope. A hash proves byte identity only.

## Relational typing for all CoPriMath operators

The preferred reusable operator contract is:

`T : TypedClaims[inputs] -> TypedClaims[outputs] | CoNull[typed_reason]`

with declared input/output semantic kinds, dimensional and scale rules, mathematical domain, reference frames, assumptions, provenance transfer, uncertainty/interval propagation, temporal order, effect authority (normally none), inverse/round-trip loss, test data and falsifier.

Some valid instances:
- **Physical dimensional composition:** `P = E / duration` derives watts from joules and seconds when values denote compatible energy and elapsed duration. Length, mass, time, electric current, temperature, amount and luminous intensity use existing SI definitions (BIPM), with UCUM/QUDT where useful. A temperature reading in degrees Celsius needs an *affine* transform, not arbitrary multiplication.
- **Semantic distinction despite identical SI dimensions:** 1 hour of CPU core usage is not 1 hour of human attention. Both carry a time dimension, but the measurand is distinct. Commits/hour and independently accepted user tasks/hour both have physical inverse-time dimensions, but are **not the same kind of rate**.
- **Nonphysical exact mathematics:** proofs, logical implication, graph reachability, category/identity composition and set membership need typed mathematical objects and validity rules, not necessarily empirical units.
- **Contextual/qualitative comparison:** ordinal satisfaction, accessibility judgments, consent, legal authorization and personal dignity cannot be legitimately aggregated into watts or currency. Some can use **defined instruments** for limited tasks, but values and rights remain constraints, not natural constants.
- **Prediction/calibration:** a probability is dimensionless but not a synonym for a ratio, score, confidence label, or Bayesian posterior; it needs a model, event definition and calibration scope.
- **Information gain:** bits require a probability model and an information measure; storage bits are not information gain by renaming.

`COMPATIBLE_DIMENSION != SAME_SEMANTIC_KIND != CAUSAL_RELATION != AUTHORITY`.

## Link kinds and permitted inferences

| Link kind | Meaning | Admissible inference |
|---|---|---|
| EXACT_CONVERSION | Same defined quantity, compatible units, scale and frame | Numeric conversion under a verified map |
| DERIVES | Reproducible typed formula with qualified inputs | Derived value + propagated uncertainty |
| MAPS_TO | Explicit potentially lossy semantic/projection map | Proposed equivalent with loss ledger, not automatic equality |
| CORRELATES | Observed statistical association in named population/window | Association only, not causal effect |
| CAUSAL_HYPOTHESIS | Proposed directed effect in a model | Falsifiable prediction; not established causation |
| CAUSALLY_IDENTIFIED | Bounded identification supported by valid design and assumptions | Context-specific effect estimate; no universal transitivity |
| CONSTRAINS | Formal theorem, hard safety bound or policy rule | Scoped obligation; no automatic real-world proof |
| ANALOGOUS | Similar structure, metaphor, cross-domain transfer proposal | Hypothesis generation only |
| CONTRADICTS | Incompatible qualified observations/claims | Preserve competing witnesses; investigate |
| UNKNOWN_RELATION | Link may exist, unknown type/direction or missing evidence | Discovery request, **no numerical propagation** |
| OBSERVED_NO_LINK | Qualified negative finding within closed scope/test sensitivity | Scoped absence only, not universal disconnection |
| NORMATIVE_PREFERENCE | Human/organizational value, ethical lens, contestable weight | Decision explanation within consent/rights rules |

Multi-hop pathways must keep a complete provenance chain and may **downgrade**, but never silently upgrade, evidence class. Correlation + correlation does not produce causation. A path of independently supported causal edges is still not automatically an identified combined effect: feedback, confounding, interference and scope shift require checking the *whole* causal model.

## CoNull and anticipated metrics are first-class

Knowledge states may include: OBSERVED_VALUE, OBSERVED_ZERO, NOT_OBSERVED, NOT_TESTED, BELOW_DETECTION, CENSORED, WITHHELD, NOT_APPLICABLE, CONTRADICTED, EXPIRED, DEFINED_NOT_MEASURED, ANTICIPATED, and OBSERVED_ABSENT_IN_SCOPED_DOMAIN. These are **typed dimensions of epistemic/deontic/temporal state**; this list is an explanatory projection, not a final mutually exclusive enum.

An anticipated metric can be defined before any observation:
- anticipated definition ID, version and quantity kind;
- hypothetical method, instrument, input/output signature and unit;
- purpose/decision, necessary permissions and eligible population;
- falsifiable forecast and planned observation time, sensitivity and null behaviors;
- calibration requirements, estimated resource cost and review/retirement triggers;
- **no invented value, observer or independent proof**.

If no instrument yet exists, preserve it as ANTICIPATED/UNTESTED, not a numerical zero. Reserve definition identity so later measurements do not accidentally redefine historical terms.

## What 'all relates to all' means operationally

A **potential** relation between any two entities can be posed as a question. That does not imply that the world contains an empirically identifiable, useful or causal edge between them. The graph should be sparse and lazy, with explicit unresolved frontiers, not automatically fully connected.

Build versioned entity/metric/claim/edge objects and include *relation-of-relations*, multiway constraints, scale, locality and time. Discovery traverses:
`source -> type check -> candidate relation -> counterexample -> discriminating observation -> qualified edge -> compositional path or scoped HOLD`.

Choose candidates by expected information gain, risk, marginal value, falsifiability, dependency relevance and budget. Preserve cycles without infinite recursive expansion. Derive a full causal path only under a named causal model with temporal direction, alternative explanations, interventions or identification assumptions and counterfactual tests.

Example unproven chain:
`new RickBar HTTP safeguard -> fewer exploitable unsafe requests -> higher reliability/trust -> more completed user tasks`.
Only source-level HTTP tests might initially be established. The other arrows remain hypotheses requiring real security and user-outcome measurements. This is exactly why CoEvoRate cannot be 'commits/hour'.

## Comparative-evolution use

Use existing CoBaseline comparability keys. For each alternative/fork/version track a **vector of qualified metrics**: correct task completion, consent/safety, p95 latency, independent recovery, human effort, resource costs, accessibility, provenance, option value and effect uncertainty. A successor can improve some axes and regress others. Preserve Pareto alternatives. No unconsented global ranking of people, and model capability never becomes action authority.

Users of the same fabric:
- **CoEvoRate:** outcome rates, per-window improvement/regression and open proof debt.
- **CoPriMath:** valid type-checked relations, transformations, logical nonnumeric objects, conjectures and counterexamples.
- **CoTime/CoPredict:** forecast versus observed residuals with explicit horizons and clocks.
- **CoOrb/CoMap:** accessible, multi-scale projections, provenance drilldowns and visible unknowns.
- **CoPetitor / competitor contributions:** source/rights/attribution and independent comparable baselines, with inherited advances recognized without creating false novelty.
- **CI+/iOS:** validation contracts and platform-specific observation environments, not claims of app deployment.

## Acceptance ladder and minimal negative controls

1. Reuse source-bound metric definitions from issue #367 without minting competing global IDs.
2. Type-check valid seconds-to-hours and joules-per-second derivation, plus uncertainty and source.
3. Reject CPU-hours == human-hours and commits/hour == receiver-closures/hour despite matching physical dimensions.
4. Preserve numeric zero separately from missing, withheld, contradictory and anticipated readings.
5. Reject unknown/analogy/correlation edges as causal conversions.
6. Reject arbitrary sums of ordinal ranks, uncalibrated probabilities, and affine temperatures handled as ratios.
7. Reject forecast as observation, an expired observation as current, and self-reported ACK as verified pickup.
8. Preserve both non-dominated forks, predecessor, rollback, challenge and context-specific best.
9. A proposed G_d-influenced objective is explicitly labeled normative/counterfactual, with plural affected parties and no privileged measurement or instruction.
10. Demonstrate simple-text/JSON output before UI projection and show whether the richer fabric increases real comprehension and task usefulness relative to that simpler baseline.

**Next executable seam:** implement a **read-only, bounded CoMeasure/CoPriMath type-checking adapter** and test against #367's invariants. It may produce derived claims but must never rewrite past records, fabricate causal proofs, grant permission, or promote itself to runtime. Link its test results to the existing CoEvoRate review PR; independent adoption and CI are separately required.

**Rails:** `UNIT_NE_MEANING | RELATED_NE_CAUSED | UNKNOWN_NE_ZERO | G_D_NE_UNIT_OR_AUTHORITY | MODEL_NE_WORLD | FORECAST_NE_OBSERVATION | PROVENANCE_NE_TRUTH | VALIDATION_NE_ADOPTION | LINK_NE_PROOF | ALL_POTENTIAL_NE_ALL_MATERIALIZED | CHANGE_NE_IMPROVEMENT | COCLAIM_NE_RUNTIME`.
