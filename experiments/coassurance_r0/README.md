# CoAssurance+ lifecycle R0

**State:** BOUNDED_SYNTHETIC_REVIEW_CONTRACT; not a live governance board, identity verification, independent panel, deployment, or release approval.

The existing CoRoleSpace seven-seat advisory panel, CoResearch extraordinary gate, CoFitness multidimensional criteria, CoEvidenceReceiptGuard and custody transitions remain primary donors. This overlay does not replace or loosen them.

## Scope

Each candidate in DISCOVER / DESIGN / BUILD / REVIEW / PUBLIC_PREVIEW / OPERATE / RECOVER / RETIRE carries a named source, prior/historical baseline, falsifier, role-labelled review contribution, test state, bounded recursive Turtle budget and effect authority. The burden scales with the declared risk and stage. External publication, custody and legal/financial effects retain their *separate* real-world gates.

- LOW: small review with proposer and challenger; declared source/prior/falsifier.
- MEDIUM: also provenance check, test and rollback appropriate to stage.
- HIGH: human domain review, diversity, separate independent acceptance, risk-specific controls. No claim that a string in a manifest authenticates a real reviewer.
- Before public preview: security/privacy assessment and rollback plan.
- Before live operation/restore/retirement: exact receiver readproof and useful recipient outcome.
- CoTurtle review: max depth 2, max rounds 2, max 8 active workers, total 128 evaluations, and never inherited authority.

The example uses a deliberately synthetic all-a source SHA-256 to exercise format validation, **not** an authenticated GitHub source digest. Real promotion must bind and independently verify the true source bytes.

This is **not** a rule that every typo needs a seven-seat tribunal. A minimal automatic check may suffice for harmless experiments. Review coverage should exist across stages without running all reviewers or models continuously. Budget, marginal value, risk, and actual independence govern invocation.

## Reproduce

`python3 test_gate.py` (30 synthetic tests)

`python3 gate.py candidate.json` (returns 0 when the declared structure is consistent, 1 for evidence HOLD, 2 for malformed/false attestation; all PASS results explicitly carry DECLARED_STRUCTURE_ONLY).

## Nonclaims

`LOCAL_IS_NOT_LANDED` | `VALIDATION_IS_NOT_ACCEPTANCE` | `NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF` | `NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE` | `HASHING_IS_NOT_SEMANTIC_INGESTION` | `DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY` | `PANEL_VOTES_NE_INDEPENDENT_EVIDENCE` | `SELF_ATTESTED_PASS_NE_EXTERNAL_APPROVAL`.