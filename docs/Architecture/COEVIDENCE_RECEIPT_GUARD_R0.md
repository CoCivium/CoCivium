# CoEvidenceReceiptGuard+ R0

**State:** `CANDIDATE__DESIGN_ONLY__NO_RUNTIME_ADOPTION_NO_CANON`

## Trigger

A bounded Co1 discovery run exposed a general receipt-integrity failure class: the intended output artifact was absent, verification commands reported that absence, yet later display logic emitted `VERIFIED_LOCAL` together with hash/byte values retained from an earlier artifact.

This architecture treats that as a control-plane defect, not a cosmetic logging problem.

## Invariant

A success receipt MUST be constructed only from evidence freshly derived from the exact output artifact named by that receipt.

`PRINTED_RECEIPT_NE_VERIFIED_ARTIFACT`  
`STALE_VARIABLE_NE_CURRENT_RECEIPT`  
`OUTPUT_MISSING_OVERRIDES_SUCCESS_LABEL`

## State machine

```text
INTENT
 -> WRITE_ATTEMPT
 -> OUTPUT_EXISTS
 -> FRESH_HASH
 -> FRESH_SIZE
 -> OPTIONAL_PARSE
 -> OPTIONAL_SCHEMA_CHECK
 -> READBACK
 -> RECEIPT_BUILD
 -> PASS_EMIT
```

Any failed required edge routes to `HOLD` / `FAIL`; it MUST NOT fall through to `PASS_EMIT`.

## Fresh-evidence discipline

Before a run:

- initialize receipt fields to null/unset inside a fresh scope;
- bind a unique run ID and exact output locator;
- do not inherit hash, byte count, PASS state, or readback values from caller/session scope.

After write:

1. assert exact output exists;
2. assert it is a regular file where applicable;
3. derive hash from that exact locator;
4. derive byte count from that exact locator;
5. perform required parse/schema/readback checks;
6. build the receipt from those fresh observations;
7. emit PASS only after all required checks succeed.

`RECEIPT_FIELD_MUST_BIND_CURRENT_RUN`

## Error handling

Catch-and-continue wrappers are appropriate for optional discovery observations, not for required receipt edges.

Required output verification SHOULD use terminating errors and a single fail-closed boundary.

A failed write/hash/readback MUST invalidate any provisional success state.

`OPTIONAL_DISCOVERY_ERROR_NE_REQUIRED_RECEIPT_ERROR`  
`VERIFICATION_FAILURE_INVALIDATES_PROVISIONAL_PASS`

## Receipt shape

Candidate fields:

`receipt_schema | run_id | producer | session | operation | output_locator | output_kind | write_completed | exists_verified | hash_algorithm | hash | bytes | parse_verified | schema_verified | readback_verified | observed_at | source_inputs | authority_ceiling | mutations | errors | state | nonclaims`

For non-applicable checks use explicit `NOT_APPLICABLE`, not an implied success.

## Atomic publication

Where practical:

```text
write temp
 -> verify temp
 -> atomic rename/move into final locator
 -> verify final locator
 -> emit receipt
```

This reduces partial-output ambiguity.

`PATH_NAMED_NE_OUTPUT_COMMITTED`

## Receipt/readproof separation

A producer receipt is evidence about producer-side verification. A distinct receiver readproof remains stronger evidence for pickup/reconstruction.

`PRODUCER_RECEIPT_NE_RECEIVER_PICKUP`  
`HASH_MATCH_NE_SEMANTIC_INGESTION`

## Self-test fixtures

At minimum:

1. successful write/hash/readback -> PASS;
2. write suppressed -> HOLD, no stale hash;
3. output deleted before hash -> HOLD;
4. hash command fails -> HOLD;
5. malformed JSON -> HOLD when parse required;
6. wrong schema -> HOLD when schema required;
7. previous run populated hash/bytes, current run fails -> HOLD with null current hash/bytes;
8. output path points to prior artifact -> HOLD on run-ID/path binding mismatch;
9. final atomic move fails -> HOLD;
10. receipt itself can be parsed and binds exact run/output.

## R0F classification example

The motivating run is classified:

`HOLD_FALSE_RECEIPT__OUTPUT_MISSING__STALE_VARIABLE_LEAK`

Useful pre-output observations may remain bounded observations, but they are not promoted as a verified artifact or completed topology.

## Integration targets

- CoEvidence+;
- CoOps+ / CoAutoEvo+;
- CoSourceGraph+;
- CoLineageCompactor+;
- CoSessionAutocycle+;
- PS7 one-paste runners;
- local/Ollama workers;
- CI;
- RickBar evidence projection.

AutoEvo SHOULD prefer no progress claim over a fabricated success receipt.

`NO_RECEIPT_IS_BETTER_THAN_FALSE_RECEIPT`

## Rails

`PRINTED_RECEIPT_NE_VERIFIED_ARTIFACT`  
`STALE_VARIABLE_NE_CURRENT_RECEIPT`  
`OUTPUT_MISSING_OVERRIDES_SUCCESS_LABEL`  
`RECEIPT_FIELD_MUST_BIND_CURRENT_RUN`  
`OPTIONAL_DISCOVERY_ERROR_NE_REQUIRED_RECEIPT_ERROR`  
`VERIFICATION_FAILURE_INVALIDATES_PROVISIONAL_PASS`  
`PATH_NAMED_NE_OUTPUT_COMMITTED`  
`PRODUCER_RECEIPT_NE_RECEIVER_PICKUP`  
`HASH_MATCH_NE_SEMANTIC_INGESTION`  
`NO_RECEIPT_IS_BETTER_THAN_FALSE_RECEIPT`
