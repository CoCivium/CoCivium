# CoAll CoMeasure+ R0 | typed quantities, units, evidence and relations

Status: PUBLIC-SAFE DRAFT PROPOSAL / tested local subset / NOT CANON.
Origin: cross-session user mandate, 2026-11-07. Candidate for CoLex / CoPriMath review.
Companion objects: `registry_r0_1.json`, `verify_registry_r0_1.py`.
Do not use this candidate as an unreviewed safety-critical converter.

## Design aim

A quantity, a unit, and a measurement are different objects.
A mathematical relation does not imply conversion or physical causation.
Every measurable claim should be comparable only inside its declared semantic,
temporal, procedural, evidentiary and authority envelope.

The intended public/CoAll contract is:
`QuantityKind + Unit + DimensionVector + ValueState + MeasurementProcedure +
 ObservationTime/Window + Uncertainty + Provenance + RelationEdges + Authority`.

## 1. Interoperate before inventing

* Physical SI base dimensions: L, M, T, I, Theta, N, J, in that order in R0.
* Physical-unit anchor: SI Brochure, BIPM; SI is defined via seven exact defining constant values.
* Machine-exchange unit-code reference: UCUM, where applicable.
* Semantic ontology reference: QUDT QuantityKind / Unit / DimensionVector.
* Uncertainty reference: GUM / NIST. Uncertainty and confidence are not interchangeable.
* Calendar dates, timestamps, currencies, digital information, social outcomes and
  governance state require type-specific semantics; don't force them into SI vectors.
* CoPriMath / CoNull / natural-units / complex-number systems are *candidate relation
  systems*, not newly established SI dimensions or physical laws.

References:
https://www.bipm.org/en/publications/si-brochure/
https://www.bipm.org/en/measurement-units
https://ucum.org/ucum
https://qudt.org/
https://www.nist.gov/itl/sed/topic-areas/measurement-uncertainty

## 2. Typed observation envelope

Required by proposed API (not all fields yet enforced by R0 code):
```json
{
  "schema": "CoAll.MeasurementObservation.R0_CANDIDATE",
  "quantity_kind": "fraction_of_whole",
  "unit_id": "ratio",
  "value_state": "MEASURED",
  "value": "0.625",
  "uncertainty_kind": "NOT_ASSESSED",
  "uncertainty_value_or_null": null,
  "observed_at_utc": "2026-11-07T00:00:00Z",
  "interval_or_window": "SYNTHETIC_ONLY",
  "observer_id": "synthetic-exemplar",
  "source_id": "synthetic-sample",
  "source_sha256": "NOT_REAL_PROOF",
  "method_or_null": "5 accepted / 8 qualified deliveries",
  "authority_scope": "NONE",
  "comparison_baseline_or_null": null
}
```
Example is **synthetic**, not actual CoAll performance.
For production: exact numerator/denominator, sampling, calibration, censoring,
rights, version, confidence and observer identity must be proven.

## 3. CoNull value states

Numerical 0 is an observed or specified value, never a synonym for no data.
`MISSING`, `UNKNOWN`, `NOT_APPLICABLE`, `BELOW_DETECTION_LIMIT`,
`REDACTED`, `INVALID`, `UNDEFINED`, and symbolic `INFINITE` mean
different things. A below-detection observation needs an instrument threshold;
a redaction must not leak the hidden value through a derived metric.
An empty denominator is not a zero rate; it produces an undefined or not-applicable
result, subject to explicitly declared statistical policy.
CoNull is a candidate symbolic layer over these distinctions, not a license
to equate them or to define a physical absolute zero.

## 4. Relation algebra: all may relate, but not all may convert

Proposed edge predicates:
`SAME_QUANTITY_KIND`, `CONVERTIBLE`, `DERIVED_FROM`, `NORMALIZED_BY`,
`CORRELATED_WITH`, `CAUSAL_HYPOTHESIS`, `CONSTRAINED_BY`, `REFERENCES`,
`ORTHOGONAL`, `INCOMPARABLE`.

`CONVERTIBLE` requires matching dimension vectors **and quantity kinds**,
including affine-unit handling where applicable. Hertz and event-per-second
can share dimension T^-1 yet have different meanings. A count and a fraction
can both be dimensionless yet cannot be exchanged without a model.
Timestamp is not a duration. A statistical link is not causal proof.
Conversion of a value does not certify the instrument or observation.

R0 exact affine transform: `anchor = source_value * source_scale + source_offset`;
`dest_value = (anchor - dest_offset) / dest_scale`.
This is a narrow scalar registry, not universal unit calculus.

### Temperature points versus intervals

An absolute thermodynamic-temperature point and a temperature difference
can share the same physical dimension but have **different quantity kinds**.
`0 Cel` as a point converts to `273.15 K`. A difference of `1 delta_Cel`
converts to `1 delta_K`, **not** `274.15 K`.
R0.1.2 registers `delta_K` and `delta_Cel` as zero-offset
`temperature_difference` units. Neither may silently convert to absolute
`Cel`/`K`. A quantity kind is not inferred from a unit's printed symbol.

### Observed numeric value versus prediction or null

`MEASURED` is permitted only with an exact numeric string under the
R0 evaluator; `OBSERVED_ZERO` is a separate zero-specific state.
`PREDICTED` is **not accepted** by this simple value validator because
a prediction needs its own model version, target time, probability/interval
and calibration. A numeric validation pass by itself does **not** authenticate
the source, measurement method, uncertainty, clock or independent receiver.
The private CoNeedleEvo challenger separately tests time, phase, metric
version, population and denominator comparisons.

## 5. Measurement families worth agreeing upon

* Physical: time, distance, temperature, mass, energy, power, information,
  frequency, rate, efficiency and dimensions/derived ratios.
* Operating: source age, queue age, cold-start duration, fan-in latency,
  receiver pickup fraction, proof-debt growth, recurrence, crash loops.
* Reliability: availability under a declared window, restart budget, lost-work
  incidence, failure-domain independence, backup restore, mean time to restore.
* Quality: task completion, useful accepted deltas, contradictory claims,
  calibration error, false-green rate, reproducibility, uncertainty.
* Human: intervention count, comprehension, cognitive load, discoverability,
  accessibility, consent reversibility, agency and retention.
* Resource: joules, compute cost, money and dated exchange rates, carbon-boundary
  estimates, network bytes, energy per verified benefit.
* Epistemic/social: competing hypotheses, diversity of independent evidence,
  falsifiable predictions, source trust and explanatory scope.
* Math/theory: dimensional invariants, natural-unit projections, complex-valued
  representations, symmetry, limits, singularities, CoNull and CoPriMath mappings.
  These must carry stated assumptions and experimental discriminators.

Some outcomes are inherently vector-valued, ordinal, categorical or normative.
Do not replace fairness, trust, safety, accessibility and cost with one hidden
all-purpose scalar. Trade-offs require declared value choices.

## 6. Consensus, source governance and cross-session flow

Propose -> dedupe existing CoLex and CoPriMath meanings -> bind named
quantity-kind / aliases / unit / dimensions / procedure / uncertainty ->
independent challenge -> execute scoped tests -> record versioned receipt ->
elect candidate or HOLD -> publish only within authority -> monitor drift.
Session agreement in chat alone does not create standard adoption.

Each candidate proposal should record:
`object_id, kind, aliases, external_standard_ref, dimension_vector,
 semantic_scope, algorithm, test_vectors, uncertainty_policy, source_hash,
 proposer, independent_challenger, reviewed_status, version, supersedes,
 privacy, rights, recipient, receiver_readproof, wake_predicate`.

Parallel workers may suggest names, build conversion tests, critique null
semantics, explore theory relations, model UX, and test performance separately.
Shared registry writes need one elected actuator and collision control.
Use existing CoAll/CoSteward Seed and Pulse. No mass prompts, no duplicate task
runner, no claim that other provider sessions read the candidate automatically.

## 7. R0 proof and gaps

**Historical R0.1.1 checkpoint:** the registry contained 19 unit/semantic
variants and 7 operating metric families. Its Python verifier passed 24/24
scoped checks on X2 on 2026-11-07, with exact source SHA-256
`30d8e27168bf9f9b3ccefa1fda267d872521127fb09c54f8458db0be0ad2b744`.
The preceding `registry_r0.json` had failed two unbound metric-unit references
and was preserved rather than silently overwritten.

**R0.1.2 scoped challenger integration (new branch source):** 21 registered
unit/semantic variants, 7 operating metric families and 35 deterministic
verification assertions: 11 exact conversions, 7 invalid conversions
rejected, 6 valid null states, 3 exact measured-value examples and 8
invalid null/value representations rejected. The existing 24-case X2
result does **not** attest this changed registry. The first [exact-source GitHub CI](https://github.com/CoCivium/CoCivium/actions/runs/42410266679)
completed SUCCESS at commit `248c09f8fab66fc015773d123aa03719aa07970e`:
35/35 assertions, idempotent second execution, no external test effects.
The tested registry SHA-256 was
`14544bf12c8498c3fa664c7a11d01b8706d5d1f4704a7cc99f7040f159a033e7`.
These are hosted CI claims only, not X2 reinstallation, independent
semantic reviewer adoption, CoEx or canon.

**No false consensus:** The private CoNeedleEvo 28-test candidate in
[CoSteward draft PR #265](https://github.com/CoCivium/CoSteward/pull/265)
is retained as a time/metric-version/freshness *challenger*, **not** a
second elected registry or an independent receiver ACK. The user requested
cross-session fan-out/fan-in, but no system-wide delivery, voting or
multi-provider adoption is established.

Not implemented: uncertainty propagation, complex quantities, dimensional
multiplication/inversion engine, SI traceability chain, calibration registry,
statistical comparison, actor/receiver consensus, actual multi-session uptake,
machine-to-machine fan-out, or 24h independent recovery.

## 8. Next falsification challenge

Have a separate executor fetch the exact candidate hash, run an independent
implementation (not this script), reject 0-vs-null and fraction-vs-count swaps,
challenge temperature offsets and non-affine units, and perform one meaningful
receiver-origin task. Compare outcomes on at least two distinct execution
domains. Preserve each failure and contested naming choice without clobber.
