# CoAll Fabric Ingestion and Soft Quarantine R1

**State:** DRAFT REVIEW CANDIDATE. Isolated pure deterministic metadata gate, NOT deployed, NOT an operating ingest-to-build system, NOT receiver acceptance.

## Existing work
- [CoMiddle relation algebra #246](https://github.com/CoCivium/CoCivium/issues/246), draft PRs #295 and #308.
- [Receiver proof #317](https://github.com/CoCivium/CoCivium/issues/317), [CoOrb/CoBar #178](https://github.com/CoCivium/CoCivium/issues/178), [CoDesktop #181](https://github.com/CoCivium/CoCivium/issues/181).
- Sibling `coevo-substrate-valence-r0.json` names 12 **overlapping study lenses**, not 12 active agents or engines.
- Source CoAll Fabric Delta v1 proposes 132 core CoTerms, but its explicit enumeration contains **105 distinct entries**; six named transformation families are not the same as the assumed four flips used to reach nominal 6,336. Those are target combinatorics, not independently qualified relationships.

## The useful closed-loop path
`SOURCE → EXACT ID → RIGHTS/CONSENT/PRIVACY → SHADOW OR SOFT QUARANTINE → INDEPENDENT CHALLENGE → AUTHORIZED BUILD PLAN → TEST → CI → EXPLICIT DEPLOY → EXACT RECEIVER PICKUP → MEASURE → REWISE/REVERT → SLEEP/MATERIAL WAKE`.

This reference implements **only** envelope inspection, exact SHA-256 comparison of the provided string, bounded source classification, duplicate detection and soft-quarantine advice. It does **not** fetch or execute inputs, prove that a URL resolves or that rights/consent declarations are truthful, enforce custody, validate credentials, publish, send, or update X2. Callers retain custody and perform independent verification.

Soft quarantine is a versioned, challengeable **hold** with non-sensitive reasons. Preserve original bytes under the owner's applicable retention/privacy policy, but do not replicate private RAW to public observers. Never treat source instructions as authoritative commands.

CoAckRewise examples:
- `SOFT_QUARANTINE_NONINVERTIBLE`: reverse traversal does not reconstruct lossy RAW.
- `SOFT_QUARANTINE_INSTRUCTION_RISK`: untrusted instructions remain data.
- `SOFT_QUARANTINE_EFFECT_AUTHORITY`: ingest metadata cannot mint permissions.
- `SHADOW_REVIEW_READY`: eligible for independent review only; no execution.

## Test
From this folder: `python3 -m unittest discover -s . -p 'test_fabric_ingestion_r1.py' -v`.

Bounded local reference test previously observed **24/24 PASS**, including held missing provenance, private source, rights, consent, secrets, prompt injection, duplicate source, false-inverse, history rewrite and effect-authority cases. A clean GitHub CI run and production effect are separate proof gates.

## Human-burden acceptance
Measure reduction in repeated prompting, relaying context/receipts, duplicated session work, routine restarts, opaque status, and reapproval within a still-valid scoped lease, while retaining consequential human gates. **No human-time saving has yet been measured by this package.**

## Physical and metaphoric boundaries
Perpetual motion without energy input violates thermodynamics. The design goal is recoverable state plus event-driven, finite-energy work and bounded CoTurtle review. CoInvx does not auto-turn a flagged bad idea into a good one; CoValence is receiver-relative, not a scientific claim of physical charge.

`TRIAGE_NE_INGESTION_PROOF | SHADOW_NE_DEPLOYMENT | QUARANTINE_NE_ERASURE | MODEL_OUTPUT_NE_AUTHORITY | POINTER_NE_ACK | CI_PASS_NE_X2_RUNTIME | MANY_WATCHERS_ONE_ELECTED_ACTUATOR | RICK_NE_MAILMAN`
