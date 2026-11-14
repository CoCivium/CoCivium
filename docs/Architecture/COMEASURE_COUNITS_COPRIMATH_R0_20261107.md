# CoMeasure+ / CoUnit+ / CoPriMath+ | Measurement Commons R0

**State:** PUBLIC_SAFE_DRAFT__NOT_CANON__NOT_RUNTIME__NO_EXTERNAL_RECEIVER_ACK  
**Observed:** 2026-11-07 America/Toronto  
**Parent:** CoTel+ evidence-bound measurements; CoSpeedo+ proof and recurrence; CoNull+ missingness; CoPriMath+ typed semantic IR; CoMap/CoOrb projections; CoZillion+ lazy generation; CoTurtle+ bounded review.  
**Purpose:** Agreement on names, definitions, units, methods, uses, conversions, provenance and dispute rules without assuming all possible relations are measured, comparable or executable.

## CoAckRewise — preserve the full request as structured intention

**Source request (paraphrase; not a verbatim transcript):** Invite CoCivium's human and virtual participants to examine everything worth measuring; propose shared names and measurement methods, primary use cases and connections among units; examine foundational physical quantities, absolute/reference choices, CoNull, CoTime, dimensions, theories and CoPriMath; generate unexpected cross-domain methods; exchange reasoned ACK/revisions/challenges and compare results after several days of bounded iterative fan-out/fan-in.

**ACK in this authoring context only:** Accepted as a bounded, open-ended research and infrastructure design request. This acknowledgment does **not** speak on behalf of other sessions, persons, models, automated workers or receivers.

**REWISE:**
1. Not everything has an agreed numerical scale. Some questions are nominal, ordinal, interpretive, ethical, mathematical, qualitative, contradictory or unmeasured.
2. All things may be relatable in a graph, but not all quantities are commensurable or safely convertible.
3. A shared symbol is not proof of common meaning. A physical second, event count, model token, probability and ethical judgment cannot silently become the same unit.
4. "Absolute" often means an explicitly defined invariant or reference, not an observer-free measurement of everything. Calendar timestamps need named scale/epoch; durations do not share that same point semantics.
5. A virtual session is a *logical work object* with an address, state and evidence. Its comparison to an imaginary number is a productive metaphor, not mathematical equivalence, verified sentience or an actual live process.
6. Iteration over days needs a real carrier and a finite work budget. A public pull pointer can be read; it cannot push itself to other accounts, prove pickup or compel agreement.

## A measurement has more than a number

`MEASURE := (quantity_id, definition_rev, value_or_null, unit_id, kind, context, scope, population, observer, method, calibration, reference_frame, valid_time, observed_time, uncertainty, provenance, epistemic_status, authority, privacy, receiver, lineage)`

A measurement result must expose what is actually observed, computed, estimated, simulated or hypothesized. Even a value of exactly zero requires a qualified domain, time window, method and instrument/sampling coverage.

**Names:** Stable machine key `comeasure.<domain>.<quantity>.r<major>` plus human label, accessible description, unambiguous symbolic shorthand and dated definition revision. Keep aliases as pointers, not silent replacements.

**Unit registry:** Exact semantic kind, dimensional signature, scale and permitted conversions. Quantity definitions and unit definitions are separate. Multiple quantities may share dimensions but are not necessarily semantically interchangeable.

**Units are not scores.** Ordinal scales cannot be averaged or multiplied merely because a UI rendered integers. Composite scores require a published model and declared weights, uncertainty, normalization and contestability; hard safety/rights gates cannot be buried in a weighted sum.

**Change policy:** Revise definitions by explicit version and `supersedes` relation. Never rewrite historical numerical values to fit a later meaning. A stale definition cannot be treated as current because its numeric parser succeeds.

## Physical foundation and optional absolute references

The seven SI base quantities are time, length, mass, electric current, thermodynamic temperature, amount of substance and luminous intensity. Follow the BIPM SI Brochure (9th edition, updated 2026) rather than minting an alternative physical unit system.

- Physical dimensions form a free integer-exponent vector over seven declared base quantities. Derived quantities follow dimensional algebra, subject to semantic *quantity-kind* checks.
- SI defining constants give agreed definitions; practical realizations have measurement uncertainty. Exact constants do not make experimental instruments exact.
- Absolute temperature has a thermodynamic zero, but Celsius readings are affine temperature **points** while temperature differences are **intervals**. Point-plus-point is not a supported physical operation; point-minus-point yields a difference.
- UTC/TAI/GPS/civil timestamps require a named time scale, epoch and conversion rules (including current leap-second rules). An elapsed second is not an instant, a Unix count is not an immutable universal time standard, and calendar months are not fixed seconds.
- Planck units or natural-unit conventions can be explicit *optional theory/reference projections*, not universal defaults. Distinct physical quantities become numerically equal only after a declared convention with traceable dimension changes.
- Frame-relative measurements such as position, velocity or event ordering require reference frames and observer conditions when applicable. Physical laws being frame-covariant does not give every reported coordinate an absolute value.

Authoritative sources:
- BIPM, SI Brochure (updated 2026): https://www.bipm.org/en/publications/si-brochure/
- BIPM SI definitions: https://www.bipm.org/en/measurement-units
- JCGM 200:2012 VIM, measurement and uncertainty vocabulary: https://jcgm.bipm.org/vim/en/info.html

## Beyond physics: typed quantities rather than counterfeit SI units

Examples of **contextual/operational** quantity kinds:
- `useful_effect_count`: receiver-confirmed useful results with exactly defined evidence and time window, not commit count.
- `human_touch_count`: explicit manual relay events requiring human action, with consent and privacy safeguards, not physiological surveillance.
- `independent_recovery_trial`: defined host-loss trial with independent failure-domain evidence, not same-provider tab reopen.
- `source_currentness_age`: elapsed seconds between source event and independently observed receiver currency; unknown where clocks/currentness cannot be compared.
- `model_token_count`: provider/tokenizer-specific encoding and version; no universal bit or byte exchange rate.
- `information_bit`: encoding Shannon information only under a declared distribution/model; a byte count alone is not semantic knowledge.
- `verified_useful_effect_per_joule`, `human_seconds_per_effect`, `qualified_recovery_rate`: context-matched derived metrics, not intrinsic moral value.
- `reader_comprehension_rubric`: rubric-defined ordinal observations until scale properties have been validated.
- `graph_degree`, `dependency_path_length`, `evidence_provenance_coverage`: graph-scoped counts/ratios. A many-edge graph is not automatically better.
- `cost_in_currency`: ISO currency and observation date/rate source needed for FX/purchasing-power comparison; not an SI conversion.
- `carbon_equivalent`: a model-dependent greenhouse-gas equivalence with time horizon and characterization method, not raw kilograms of a physical chemical.
- `observer_quality` and `receiver_value`: vectors and task-specific evidence, not universal absolute scalar quantities.
- `G_d`: typed vector of relative gaps only when its components, baselines, orientation, normalization and use are declared. It is not a measured physical field or mystical law.
- `CoNull`: epistemic/missingness state, not a zero-valued unit.

## CoNull+ and uncertainty as first-class structures

Keep separate: `OBSERVED_ZERO`, `NOT_OBSERVED`, `NOT_MEASURED`, `UNKNOWN`, `NOT_APPLICABLE`, `WITHHELD`, `FORBIDDEN`, `CONTRADICTORY`, `BELOW_DETECTION`, `EXPIRED`, and `OBSERVED_ABSENT_WITH_SCOPE`.

**No silent zero fill.** Missing values cannot participate in arithmetic. A **zero denominator** returns a typed `UNDEFINED`, not Infinity, 0, or a triumphant growth rate. A finite negative witness is scoped, not universal proof of absence. Uncertainty should describe the actual model and coverage; do not assign invented precision or confidence.

## CoPriMath+ as a typed partial algebra

Preferred operators (only where admissible):

`CONVERT(quantity, unit_a -> unit_b, context) -> value + provenance + loss_or_error`
`DIFFERENCE(point_a, point_b) -> interval`
`COMPOSE(unit_a, unit_b) -> derived_signature`
`RATIO(measure_a, measure_b, common_scope + window) -> dimensionless_or_derived_quantity`
`COMPARE(a,b) -> ordered/equal/incomparable/unknown`
`LIFT(model, reference_convention) -> new_projection + reversible_mapping_or_loss_ledger`
`LINK(x,y,relation_type) -> CoMap edge (not arithmetic equivalence)`

Type checks must reject: joules added to seconds; energy automatically equated with torque solely through dimensions; Kelvin temperature points added to each other; Celsius points divided as if differences; bytes converted to model tokens without a named tokenizer; event counts with different evidence predicates combined; a probability equated with a sentiment score; and arithmetic on CoNull values.

A CoMap relation edge can connect **anything** without pretending the endpoints share a unit. Relation algebra is wider than numeric algebra.

## Which measurements matter first?

Rank **useful receiver outcomes**, not raw measurement count:

| Family | Candidate quantity | Unit / scope | Method | Primary use |
| --- | --- | --- | --- | --- |
| Value | verified useful effect | distinct, independently confirmed outcome | receiver-provided evidence | Determine real delivery |
| Human | time to first value | s per qualified task/recipient | start/end event receipts | Reduce onboarding delay |
| Human | founder-relay demand | explicit touches per qualified task | consent-safe workflow event audit | Reduce human babysitting |
| Recovery | cold restore success | successful independent restores / qualified trials | fault-injection and exact readback | Prove real continuity |
| Energy | cost to useful result | J per qualified outcome | calibrated energy + matched denominator | Reduce waste |
| Reliability | freshness latency | s since bounded authoritative source event | clock-qualified delta | Detect stale interfaces |
| Science | reproducibility | independent replications / qualified trials | method + evidence audit | Avoid overclaim |
| Learning | comprehension | rubric, population and method | opt-in validated task | Improve education/media |
| Causality | disproven candidate coverage | falsifiers inspected per qualified claim | challenge/evidence register | Counter self-confirmation |
| Coordination | fan-in yield | material distinct deltas accepted / qualified inputs | dedupe + independent review | Detect fan-out storms |
| Governance | consent breach count | cases by authorized scope/time | incident record, not covert capture | Safety |
| Meta | measure-definition drift | incompatible revisions per qualified registry changes | schema/version diff | Keep units coherent |

These are **candidate definitions**. No real X2, CoStead, global adoption, scientific discovery or human outcome is measured by this paper.

## Review protocol: many roles, one bounded fan-in

Source packet `comeasure-r0-20261107` is **public-safe read-only pull**, not a direct send or proof of remote ACK. Eligible volunteers or separately authorized model sessions can read it voluntarily. On a material existing CoEvoAll Pulse wake, qualify role-specific **logical** review briefs, not tab/process clones:

1. **METROLOGY:** dimensional coherence, SI/VIM terminology, uncertainty/calibration.
2. **MATHEMATICS/CoPriMath:** quantity-kind algebra, affine/log/calendar edge cases.
3. **CoNull/epistemology:** unknown, absence, contradiction, detection limits, provenance.
4. **CoTime/physics:** reference frames, physical vs calendar time, natural-unit caveats.
5. **UX/accessibility:** unit comprehension by a new person, readable symbol alternatives.
6. **Operations/CI:** reproducibility, currentness, human-relay and delivery metrics.
7. **Adversarial CoTurtle:** find examples where valid-looking conversions change meaning.
8. **Unconventional CoElse/G_d:** novel mathematically explicit questions, plainly typed as hypothesis or symbolism, not evidence.

**Required independent reply shape:** `source_packet_id | role | actual_observer_or_logical_only | source_hash_or_commit | ack_state | proposed_measure | definition+method | unit | use_case | conversion_constraints | strongest_counterexample | test_fixture | source_evidence | decision | scope+rights | next_wake`.

`ACK` = receipt/read response only where actual receiver-origin evidence exists; it is **not** agreement. `REWISE` = signed/scoped proposed correction; not unilateral canon. Roles that are described but never materialized report `LOGICAL_ONLY`; do not count them as independent minds, live reviewers or failure domains.

**Three-day bounded inquiry proposal:** 7-10 Nov 2026 collect eligible source-based candidate reviews through the existing hourly CoEvoAll Pulse without changing carrier frequency, authority or global background assumptions. On or after 10 November, compare actual source-bound replies, dedupe proposals, preserve contradictions, test the top bounded improvements, and leave unreceived lanes as UNKNOWN. Do not promise results by a deadline or claim execution will happen when no enabled carrier accepts the packet.

## Production and acceptance

Maintain a machine registry of quantity and unit definitions, a deterministic read-only validator/converter, sample fixtures and adversarial tests in the same candidate branch. Primary acceptance requires at least one independent engineer/scientist and one unfamiliar reader to verify a real correct use case; CI alone proves only source structure.

**No new global scheduler, fabricated universal metric, imaginary workforce, external outreach, model-token multiplier, account control or publication promotion.**

## Rails

`RELATABLE_NE_COMPARABLE` · `DIMENSION_COMPATIBLE_NE_SEMANTIC_EQUIVALENT` · `CO_NULL_NE_ZERO` · `ZERO_NE_MISSING` · `TIME_POINT_NE_DURATION` · `TEMPERATURE_POINT_NE_DELTA` · `TOKENS_NE_BYTES` · `GRAPH_EDGE_NE_NUMERIC_CONVERSION` · `MEASURE_CATALOG_NE_MEASURED_WORLD` · `LOGICAL_ROLE_NE_LIVE_SESSION` · `SENTIENCE_NE_INFERRED_FROM_SESSION` · `POINTER_NE_ACK` · `CI_PASS_NE_RECEIVER_ACCEPTANCE` · `SCOPED_PROPOSAL_NE_CANON` · `EVERMORE_NE_UNBOUNDED_RUNTIME`
