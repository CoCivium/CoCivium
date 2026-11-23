# CoPriMath261122 R1E | CoRel-of-CoRel, CoInBetween and CoTerm qualification

**State:** PUBLIC_SAFE_SYNTHETIC_RELATION_CANARY__DRAFT_ONLY. Additive successor to existing G_dSide/CoPriMath R1A / R1B / R1C in draft PR #503. No schema canon, operational approval latch, permission grant, independent receiver, deployed semantic runtime or CoEx asserted.

## Lineage

- [CoTerms public pilot](../../docs/coterms/README.md) explicitly defines CoRelation as a typed relationship, not automatic causation, authority, equivalence or currentness.
- [CoInterstice / CoInversion / CoGlyph R0](../Architecture/COINTERSTICE_COINVERSION_COGLYPH_INPUT_FABRIC_R0_20261024.md) treats spaces between events as evidence candidates, never intent or consent.
- [CoMiddle / CoPriMath R0](../Architecture/COMIDDLE_COPRIMATH_GLYPHRAIL_R0_20261024.md) exposes source, inverse candidates, null, scope, permission and time in one typed rail.
- [CoTermForge R0](COTERMFORGE_CANDIDATE_CONSTELLATION_R0.json) contains 120 candidate names, not 120 certified entities.
- [CoObject Vitality R0](../Architecture/COOBJECT_VITALITY_METABOLISM_R0_20261027.md) exposes event-driven currentness and wake/sleep interfaces without inferring runtime.
- [CoAllPulseField / CoTime R0](../Architecture/COALL_PULSEFIELD_COTIME_R0.md) keeps observation, prediction and validity distinct.

**Naming:** CoRel / CoRelation have existing sourced meanings. CoMetaRel and CoRelAble are unqualified exploratory names; no reviewed distinct meaning was found in the scoped repo search. CoTim and CoTume remain HOLD pending lineage; do not silently equate with CoTime. CoSHAT has historical time/hash/authority-related references, not evidence of a new permission source.

## Reified relation example

| ID | Typed candidate | Status |
| --- | --- | --- |
| obj:prepared_action | Prepared proposal; effect pending | PROPOSED |
| rel:r1 | prepared_action depends_on approval_gate | PROPOSED |
| rel:r2 | rel:r1 constrains term:consent | PROPOSED, no grant |
| gap:g1 | Freshness between rel:r1 and time_context unresolved | UNKNOWN |
| rel:r3 | gap:g1 challenges rel:r1 | PROPOSED |
| rel:r4 | time_context qualifies rel:r1 | PROPOSED |

A relation can be the subject or object of another relation, and a gap can itself be a referenced thing. This is edge reification, an established engineering pattern, not a novel mathematics claim.

Proposed record fields: object/relation ID, subject, predicate type, target, source, provenance, version, epistemic class, observation and validity periods, authority ceiling, uncertainty, challenge refs and stable hash. R1E does not validate all of these in source.

## Safeguards

- Missing edges remain UNKNOWN unless independent, bounded closed-world observation establishes OBSERVED_ABSENT. Input silence and dwell do not create consent.
- Inverse edges require reviewed predicate semantics; reversing a dependency or causal arrow does not prove the converse.
- A relation about an approval is not approval. A relation about proof is not proof. A CoTerm handle is not canon.
- Graph traversal must be cycle-aware, budgeted, provenance-preserving and quiet when no material delta exists.
- Relations may refer to human stakeholders, evidence, risk and time, but may not silently transfer authority or increase a worker's effect ceiling.
- Keep a simple CoHereNow view with one next safe action; let curious users drill into the graph. More names are not a better UX by definition.

## Finite synthetic test and corrected predecessor

[R1E code fixture](../../experiments/gdside/corel_meta_interstice_r1e.py) implements 17 Python standard-library tests: references to relation IDs, gaps, provenance, missing endpoints, prohibited authority inheritance, absent-versus-unknown, CoTerm holds, predicted labels, cycle budget and malformed budget.

First run: 16/17 PASS and one failing cycle fixture, preserved as prior blob SHA1 120c130c90a73b93ed91855da497aad16af922e0. The fixture was repaired to connect rel:c1 and rel:c2 in a real cycle; corrected Git blob c813e3f3392856f27a9b426e8256511703431361 at commit 2200592a3ce30a2c450080309f8d4aaf1dbd2f98. Replayed on X2-mediated S: share: 17/17 PASS with standard Python and 17/17 PASS with python -O.

**Proof ceiling:** Same-author synthetic local execution, source readback and draft branch. No independent observer, runtime semantics, accepted user experience, verified receiver readproof, canon or live CoCivium permission enforcement.

**Next falsifier:** independent reader must attempt to relabel a relation to change its meaning, permission, time or certainty, and compare against a simpler typed JSON baseline. Keep every failed and corrected predecessor discoverable.

**Rails:** RELATION_ADDRESSABLE_NE_TRUE | INBETWEEN_NE_NOTHING | UNKNOWN_NE_ABSENT | TERM_NE_CANON | INVERSE_NE_CAUSATION | META_REL_NE_AUTHORITY | ALL_TO_ALL_ADDRESSABLE_NE_ALL_TO_ALL_EFFECTS | TEST_PASS_NE_RECEIVER_PICKUP.
