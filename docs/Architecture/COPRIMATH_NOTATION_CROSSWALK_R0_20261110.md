# CoPriMath+ | Historical Notation, Typed Measurement and Semantic Bridge R0

**Date:** 2026-11-10. **Status:** `PUBLIC_SAFE_SOURCE_CANDIDATE__SYNTHETIC_TESTS_ONLY__NOT_A_NEW_MATHEMATICS_OR_RUNTIME`.  
**Owner spine:** [CoMeasureFabric #367](https://github.com/CoCivium/CoCivium/issues/367); [CoPriMath + GS-Loop public contract](../Evolution/GDSIDE_COPRIMATH_GSLOOP_PUBLIC_R0.md); [CoMiddle glyph rail](COMIDDLE_COPRIMATH_GLYPHRAIL_R0_20261024.md); [CoZillion lazy relation grammar](COZILLION_GENERATIVE_RELATION_GRAMMAR_R0_20261026.md). This is an interoperable donor, not a second metric registry.

## Thesis: a mathematical inheritance, not a new empire of symbols

The history of mathematics offers many notations, logical systems, and semantic structures. A glyph is not a meaning, a meaning is not a measured fact, and a measured fact is not legitimate permission to act. CoPriMath can reuse existing formal tools by separating **meaning**, **rendering**, **typed quantity**, **epistemic state**, **authority**, and **evidence**.

`EXACT_SOURCE -> TYPED_SEMANTICS -> VALIDATED_OPERATORS -> HUMAN / AI / SPATIAL PROJECTIONS -> CHALLENGE -> OBSERVED_OUTCOME`

| Historical/formal family | Established donor ideas | Candidate CoPriMath reuse | Why not automatically equivalent |
| --- | --- | --- | --- |
| Positional and symbolic arithmetic | decimal, sexagesimal, exact fractions, integer/rational domains | representation + exact conversion | same digits can represent different bases or precision |
| Algebra and equational reasoning | symbolic variables, rewriting, substitution, polynomials | typed transformations and simplifiers | identical-looking symbols can refer to incompatible quantities |
| Geometry and Cartesian coordinates | points, transformations, reference frames, projective spaces | CoMap/CoOrb and multi-view state | axes/coordinates require a frame and unit |
| Calculus and dynamical systems | derivatives, integrals, vector fields, differential equations | time-evolution hypotheses, CoSpeedo | instantaneous rates differ from averages and event counts |
| Logic and Boolean/predicate formalisms | propositions, quantifiers, implication, three-valued logics | rights/evidence/consent gates and explicit UNKNOWN | false, unknown, withheld and absent differ |
| Set theory and order theory | membership, lattices, partial orders, Pareto fronts | CoRel/CoBraid typed inclusion and incomparable alternatives | a partial order is not a ranked popularity contest |
| Linear algebra and tensors | vectors, matrices, tensor/index notation | typed multivariate measurements, projections | axes, basis and observer frame cannot disappear |
| Probability and statistics | conditioning, likelihood, Bayesian updates, confidence intervals | uncertain predictions and calibration | a probability is not a vote, a right, or a guaranteed outcome |
| Graphs and networks | paths, cycles, hyperedges, flow, cut sets | causal/dependency graphs and CoNode routing | an edge labelled causal is not proof of causation |
| Category theory | objects, morphisms, functors, composition, natural transformations | relation-preserving translation across substrates | a metaphorical functor is not a mathematically proven functor |
| Type theory and Curry–Howard | type judgements, proof-carrying terms, dependent types | safe operator signatures and proof obligations | a type checker does not check real-world truth |
| Computability and lambda calculus | functions, substitution, reduction, operational semantics | lazy generative relations, bounded evaluators | computable description does not imply feasible execution |
| Information and coding theory | entropy, compression, channel capacity, error correction | CoAmp/CoContext and provenance-preserving compression | byte reduction does not prove semantic preservation |
| Optimization and control theory | constrained optimization, robustness, stability, feedback | CoEvo adaptation under resource/rights constraints | more reward or higher throughput is not universal wellbeing |
| Formal verification and proof assistants | Lean, Isabelle/HOL, Coq, SMT and model checking | mechanized property proof and falsifiers | verified code may encode the wrong real-world question |
| Dimensional metrology and ontology | BIPM SI, UCUM, QUDT | units, dimensions, kinds, conversions, calibration | compatible dimensions do not guarantee compatible semantics |
| Mathematical communication and accessibility | TeX, LaTeX, MathML, OpenMath, speech, tactile and spatial forms | human/AI view parity from common semantics | a rendered equation is not necessarily machine-interpretable |

The table is a **selective map of reusable families**, not a historical priority claim, complete mathematical taxonomy, proof of a new theorem, or license to import arbitrary external datasets.

## Standards and source pointers

- [W3C MathML 4, working draft 2026-11-05](https://www.w3.org/TR/mathml4/): presentation structure and mathematical meaning are different representational problems. The W3C spec was a working draft on the date of this proposal.
- [W3C MathML Core](https://www.w3.org/TR/mathml-core/): browser-oriented subset, currently at Candidate Recommendation stage in the retrieved specification.
- [OpenMath normative standard 2.0 revision 2](https://openmath.org/standard/): mathematical objects and explicit symbol semantics in content dictionaries.
- [BIPM SI Brochure, 9th edition updated 2026](https://www.bipm.org/en/publications/si-brochure): traceable physical units and definitions.
- [QUDT Ontologies](https://qudt.org/): machine identifiers for quantities, units, dimension vectors and related vocabularies.
- Standards are cited as **candidate interoperability donors**. Their full standards, converters, validators, ontologies, content dictionaries, licences and normative conformance are NOT bundled or implemented in this R0. Before adopting exact semantics, independently inspect their current definitions and licensing.

## Bounded executable source: CoPriMathNotationBridgeR0

[Source](../../scripts/CoPriMathNotationBridgeR0.py) + [adversarial tests](../../tests/test_coprimath_notation_bridge_r0.py).

One illustrative typed measurement record has: `schema, quantity_kind, unit, value {n,d}, epistemic_state, source_ref, observed_at_utc`. It carries synthetic source claims, not independently observed/calibrated readings.

- **Exact rational and dimensional sublanguage only:** length (m, km); duration (s, min); speed (m/s, km/h); ratio (1, %); probability (1, %). Conversion uses exact rational multipliers and keeps quantity kind distinct even if physical dimensions match.
- **CoNull+:** `UNKNOWN`, `NOT_TESTED`, `NOT_APPLICABLE`, `BELOW_DETECTION`, `WITHHELD`, `CENSORED`, `UNDEFINED` require *null numeric content*; `EXACT_ZERO_CLAIM` requires an explicit zero rational. Null data are not silently converted to zero. `OBSERVED_CLAIM` signals claimed observation, not instrument proof.
- **Operator signatures:** same-kind addition and speed × duration → length; everything else held until typed. Explicit refusal of physical+subjective/category mixing, and unsupported Celsius affine transforms. A 2-minute illustrative duration at 18 km/h yields **600 m** in exact units, explicitly `DERIVED_FROM_UNVERIFIED_SOURCE_CLAIMS`, no real-world effect.
- **Representational projections:** ASCII plus *Presentation MathML only*. The semantic digest comes from typed canonical JSON, **not** from parsing/scraping MathML or LaTeX. Full OpenMath/Content MathML translation remains unimplemented. A scalar may render differently while retaining an exact typed meaning and source identity.
- **Digest:** SHA-256 over a canonicalized JSON projection containing base unit, exact value, quantity kind, source reference, status and observation time. Equal source/time claims expressed as 1 min or 60 s produce the same digest; different sources/times/statuses do not. This digest is a deterministic **source-claim fingerprint**, not a scientific proof or authentication.

Run using Python 3.11+ standard library (review source first):

```sh
python -B -m unittest discover -s tests -p 'test_coprimath_notation_bridge_r0.py' -v
python -B scripts/CoPriMathNotationBridgeR0.py
```

Path-triggered [CoPriMath test CI](../../.github/workflows/coprimath-notation-bridge-r0.yml) uses Python 3.11/3.13 without any cron, provider calls, credential or device access.

## One unifying CoRel+ / CoBraid+ relation

A future math/measurement edge must name:
`source_expression | symbol_dictionary | quantity_kind | dimension_vector | unit_id | numeric_domain | reference_frame | observation_time | null_state | uncertainty | transformation | proof_obligation | context | observer | evidence | authority | loss_ledger`.

**Translation state transitions:**
`UNPARSED -> PARSED -> TYPE_CHECKED -> SEMANTICS_BOUND -> PROJECTION_EMITTED -> RECHECKED -> RECEIVER_VALIDATED`.
The R0 code proves only parts of type checking, exact arithmetic and output structure. It does not establish proof assistant correctness, cross-system roundtrips, live sensor truth, uncertainty propagation, SI certification, public uptake, CoStead/X2 integration or receiver ACK.

**Civ2+ critical guard:** Avoid making *evidence quality*, *first-person testimony*, *rights scope* and *consent* additive numeric votes merely because each can be given a number. Those are distinct kinds of evidence and authority; applicable rights are hard constraints rather than optimization units. CoNull and unexpressed interests retain their own state.

## Evolving without combinatorial waste

A powerful next progression would be:
1. **Source-kind parity:** benchmark exact round-trip of selected content-aware MathML/OpenMath expressions with an independent semantic checker. Record refusals and losses.
2. **Uncertainty:** distinguish exact quantities from calibrated measured estimates, intervals, confidence and covariance. No default false precision.
3. **Typed causal/graph relations:** link CoRel/CoBraid operators to observable counterexamples and independent validators.
4. **CoMeasure receipt:** qualify one actual sensor or domain-specific computation with instrument/method metadata, independent reader and a current source; test a deliberate mismatch.
5. **Human and AI uptake:** one newcomer can read an accessible math explanation and one independently authorized client can recover the same typed semantics, with no self-awarded ACK.

**No new named ontological universe is required.** Keep optionalities lazily addressable; prefer fewer verified transformations to millions of untested symbols.

`NOTATION_NE_SEMANTICS` · `TYPECHECK_NE_TRUTH` · `DIMENSION_MATCH_NE_QUANTITY_KIND_MATCH` · `ZERO_NE_UNKNOWN` · `SOURCE_HASH_NE_CALIBRATION` · `MATHEMATICAL_ELEGANCE_NE_GOVERNANCE_LEGITIMACY` · `CI_PASS_NE_RECEIVER_ACCEPTANCE`.
