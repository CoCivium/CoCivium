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


## 2026-11-10 | CoDiscover+ competitive representation witness R0

**Distinct addition to the same candidate PR (not another ontology or watcher):** [CoDiscoverProjectionProbeR0.py](../../scripts/CoDiscoverProjectionProbeR0.py) + [27 source-level negative tests](../../tests/test_codiscover_projection_probe_r0.py). The **existing CoPriMath CI** checks this donor on Python 3.11 and 3.13.

CoDiscovery+ for languages, notations and substrates should keep **multiple candidate representations available**, with receiver-specific qualification and explicit losses. An alternative may become the default for a particular task without erasing its competitors, source lineage or user exit path. Discovery should resume upon an **actual new source/version/capability/receiver requirement or failed proof**, not burn resources polling everything continuously.

### Counterexample, rather than abstract naming

For one synthetically constructed **typed ratio claim** with an exact zero rational, a source pointer and observation time, the existing bridge emits:

- **Canonical typed JSON:** retains source pointer, observed time, kind, epistemic state and exact base value. Digest applies to the source-claim canonical structure, not physical truth.
- **ASCII explanation:** includes number, kind and epistemic state but omits source pointer and timestamp. Two distinct provenance claims can display identically.
- **Presentation MathML:** includes displayed number and unit but omits source, timestamp, kind and the difference between observed-zero and claimed-exact-zero for this example. Two meanings can share the same rendered formula.

The new helper constructs a **pair of typed source claims differing in exactly one facet**, verifies that their canonical digests differ, then asks whether each actual output string also differs. It records a **collision witness** for each format, not a universal proof that the format could never be extended to preserve the distinction. It evaluates one receiver's required facets (up to five) and refuses to treat a collapsed field as preserved. Its only resource-cost observation is UTF-8 byte length for a synthetic example, not energy, latency, accessibility or actual consumer preference.

**Three sample receiver profiles:**

| Receiver's stated need | Qualifying R0 projection candidates in synthetic check | Held and why |
| --- | --- | --- |
| Machine source audit: source, time, kind, state, value | typed JSON | ASCII and MathML collapse provenance/time; MathML collapses more |
| Fast explanation: kind, state, value | typed JSON and ASCII | Bare Presentation MathML collapses kind and status in tested case |
| Display only: numerical value | all three | No semantic endorsement, usability or accessibility measured |

This is a minimal **typed discovery selector**, *not* a semantic roundtrip, universal format converter, language performance benchmark, public crawler, FOSS-provider registry, an independently observed AI receiver or a non-GitHub artifact custodian. The HTML/MathML projection must still be made accessible to real users, including screen-reader consumers; a string-level test cannot substitute for that.

### Evolving the same work without building a new control plane

`DISCOVER_EVENT -> SOURCE_IDENTITY -> DIFFERENTIATING_WITNESS -> RECEIVER_REQUIREMENT -> NONDOMINATED_ALTERNATIVES -> REPLAY -> REAL_USE -> REVISE_OR_HOLD`.

Future candidates: natural languages, formal languages, graphical notation, audio/speech, sign/tactile, glyphs, 3D/VR, source code, CPU/edge/network, and yet-unknown carriers. Qualify each by declared rights, actual parser/renderer capability, accessibility, energy/cost observations, safety, semantic roundtrip and failures. Cross-domain comparisons should preserve **incomparability** rather than force one score; no model/client is declared sentient, authoritative or an actual customer from notation discovery.

`AVAILABLE_NE_EXECUTING` · `FORMAT_COMPETITION_NE_FORCED_WINNER` · `COLLISION_WITNESS_NE_UNIVERSAL_INCAPABILITY` · `DISTINCT_OUTPUT_NE_SEMANTIC_ROUNDTRIP` · `BYTES_NE_ENERGY` · `SYNTHETIC_QUALIFICATION_NE_CLIENT_SUCCESS` · `DISCOVERY_NE_EFFECT_AUTHORITY`.

## CoDiscover+ / CoFed+ / CoInverse+ / CoTurtle+ | bounded federated graph donor (2026-11-10)

**Existing owners, not a new federation authority:** [Civ2+ federated cells](CIV2_FEDERATED_CELL_HOSTING_R0.md), [CoNode participation](CONODE_PARTICIPATION_R0.md), [CoSubstrateField](COSUBSTRATE_FIELD_R0.md), [CoTurtle deep provenance](../Evolution/COSTRETCH_COTURTLE_PUBLIC_BENCHMARK_20261023.md), and the existing [CoPre source-federation pointer](../../ai/copre-seed-path-federation-r0.json). This donor is in the current CoPriMath/CoDiscover draft for a **synthetic cross-domain falsifier only**. It should not be merged or become a second node registry without review by the actual federation owner.

### Core relational distinction

A federation is **both** a discoverable object and a *possible* discovery participant. A discovered object may itself be a system, federation or substrate and may recursively link to others. The graph is not necessarily a tree, and the recursion is not unlimited.

`FEDERATION/SYSTEM/SUBSTRATE -> TYPED_PUBLIC_EDGE -> BOUNDED_NESTED_DISCOVERY -> INVERSE_CHALLENGE -> RECEIVER_GATED_USE`

- **Turtles:** Limit max traversed depth to 5, candidate input nodes to 32, candidate edges to 96, and displayed public nodes to 24. A repeated node is visited once; graph cycles and repeated paths do not mint more workers or independent witnesses.
- **Inversion vs reciprocity (corrected):** The formal inverse of `A DISCOVERS B` is `B DISCOVERED_BY A`: a *second description of the same directed claim*, not evidence of a second discovery. A genuinely reciprocal discovery **claim** would instead be `B DISCOVERS A`. The probe now emits independent fields for `formal_inverse_evidence` and `reciprocal_discovery_evidence`; even both explicitly declared do **not** establish a separately authenticated observer, trust, consent, rights or membership. Changing the root also changes what is addressable within the same depth budget.
- **Privacy:** PUBLIC scoped output must not emit private node IDs, private edges, descendant IDs, private counts or a whole-input digest that could vary with a private subtree. Validation of the synthetic fixture precedes traversal. Discovery of a public edge naming a private child still cannot elect that child as public.
- **CoNull/currentness:** All source hashes in the fixture are synthetic declared strings, not fetched source bytes, signed manifests or evidence of independent operator identity. Unknown transport reachability or remote receipt remains NOT_TESTED. All materialized effects, provider requests and running workers equal zero.
- **CoFed:** No hierarchy of roots, global governor, external trust, compulsory membership, consent inheritance, rights transfer or automatic storage replication. A member can leave or hide scoped content without disclosing its private topology to everyone.

The actual bounded source and its tests are [CoDiscoverFederationTurtleProbeR0.py](../../scripts/CoDiscoverFederationTurtleProbeR0.py) and [test_codiscover_federation_turtle_r0.py](../../tests/test_codiscover_federation_turtle_r0.py). The same path-triggered CoPriMath/CoDiscover CI runs **40 synthetic checks** alongside the earlier notation tests. This is a source-level scope/edge proof, not remote federation onboarding, a >24h receiver cold restore, a cross-device benchmark or an omniverse census.

**A particularly useful discriminating canary:** Discover a publicly described regional federation in two directions using the **same** max-hop budget. Confirm public paths differ by root; a newly declared formal inverse and a distinct reciprocal-discovery assertion produce different typed evidence states without creating trust or authority; inserting, editing or unlinking a PRIVATE subtree leaves public output unchanged. Then require an independent operator-controlled reader before any claim of actual interoperation.

**Scale policy:** Recursion can generate a large *logical* optionality field without opening a huge active queue. Discover on material source/capability changes or an explicit receiver need, stop at privacy/lease/budget gates, checkpoint only qualified public-safe work, and sleep when no new information is gained.

`COFED_NE_ONE_CENTRAL_OPERATOR` · `TURTLE_NE_ENDLESS_RECURSION` · `INVERSION_NE_AUTOMATIC_RECIPROCITY` · `DISCOVERABLE_NE_CONSENT` · `MANY_PATHS_NE_INDEPENDENT_FAILURE_DOMAINS` · `PUBLIC_EDGE_NE_PRIVATE_DISCLOSURE` · `CI_PASS_NE_LIVE_FEDERATION`.
