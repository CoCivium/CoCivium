# CoSession Relational Fan-In R0

**State:** `PUBLIC_CANDIDATE__DETERMINISTIC_SESSION_PROJECTION_FANIN__NO_AUTOMATIC_FANOUT`

## Purpose

This compiler fans in the **session projection of CoEvoDelta+** before target surfaces are mutated.

It is not the canonical semantic evolution format. The canonical shared object remains CoEvoDelta+ under `docs/Evolution/COALL_GITHUB_EVOLUTION_FABRIC_R0.md`.

`COSESSION_RELATIONAL_DELTA_IS_COEVO_PROJECTION_NE_PARALLEL_SEMANTIC_STANDARD`

## Reference implementation

- `scripts/CoSessionRelationalFanIn.py`
- session projection schema: `schemas/cosession-relational-delta-v0.1.schema.json`
- canonical CoEvoDelta schema: `schemas/coevo-delta-v0.1.schema.json`
- bounded fixture: `docs/Operations/fixtures/cosession-relational-fanin-r0-input.json`

The implementation uses only the Python standard library.

## Current R0 boundary

R0 mechanically:

- binds exact input SHA-256 identities;
- accepts bounded session-projection records;
- deduplicates exact normalized operations;
- surfaces subject/relation collision candidates without declaring contradiction;
- indexes target domains and candidate surfaces;
- separates highlight candidates;
- holds non-`PUBLIC_SAFE` records from public fanout;
- performs zero automatic shared-target mutation, fanout, canon change, or receiver-pickup claim.

**R0 does not yet compile the projection into canonical CoEvoDelta+ records.** That is the next rung. Until then, this output is a review/compaction surface only.

`FANIN_NE_COEVO_INTEGRATION`

## Bounded executable canary

The repaired fixture explicitly declares `projection_of: CoEvoDelta+`, an observed base ref, intended receiver, and exact-readproof gate.

Observed local result:

- accepted deltas: 2
- unique operations: 3
- exact duplicate-operation groups: 1
- collision candidates: 1
- highlight candidates: 1
- public-fanout holds: 1
- compiled canonical SHA-256: `DDE7DC4CC29DFA6AE49F2123CEFC3EAAC0D04D07DAD76D3784B93AF64B0DF81B`

This proves bounded mechanical behavior for the fixture only.

## Next gate

`COMPILE_REVIEWED_SESSION_PROJECTIONS_TO_COEVO_DELTA_THEN_ELECT_TARGETED_FANOUT`

A later compiler should map each reviewed operation to one or more CoEvoDelta+ objects while preserving provenance, epistemic class, authority ceiling, current-base binding, public/private state, collision relations, intended receiver, and pickup/readproof requirements.

## Rails

`FANIN_NE_FANOUT`  
`FANIN_NE_COEVO_INTEGRATION`  
`COLLISION_CANDIDATE_NE_CONTRADICTION`  
`VALIDATION_NE_ACCEPTANCE`  
`DELIVERY_NE_PICKUP`  
`MERGED_NE_CANON`  
`ALL_SESSIONS_NE_ALL_STATE`
