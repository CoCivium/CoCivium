# CoSession Shadow Ledger R1

**State:** `DETERMINISTIC_SHADOW_COMPILER__NO_PROVIDER_SESSION_MUTATION`

This is the first executable rung beneath CoSessionAutocycle+.

It compiles bounded observation objects into:

- conservative lifecycle projections;
- candidate machine labels;
- append-only CoLabelSignal+ objects;
- explicit nonclaims and provider-effect zeros.

It does **not** create, rename, close, wake, or otherwise mutate provider sessions.

## Input

JSON array, or:

```json
{"observations":[ ... ]}
```

Required observation fields:

`session_id | observed_at | observer | work_state | evidence_state | authority_ceiling | currentness`

Optional explicit relations such as `tab_close_safe`, `successor_ready`, `cotwilight`, `waiting`, `quiescent`, and `source_refs` may strengthen the projection.

The compiler never claims a global session census from a bounded input set.

## Output

One JSON shadow ledger containing:

`coverage | sessions | label_signals | effects | next | nonclaims`

Visible-provider mutation remains zero.

## Projection priority

Explicit source projection, then:

`SUPERSEDED -> RECOVERY -> DEGRADED -> CLOSE_SAFE -> SUCCESSOR_READY -> EXTERNALIZING -> COTWILIGHT -> QUIESCENT -> WAITING -> CHALLENGING -> WORKING/ACTIVE/DORMANT -> UNORIENTED`

That order is intentionally conservative and revisable.

## Next

R2 should consume the ledger to generate **logical** CoSpawn contracts, dedupe equivalent work, and exercise collision-domain fixtures without needing a live provider session.

## Rails

`LIFECYCLE_LABEL_NE_LIFECYCLE_TRUTH`  
`AUTO_LABEL_SIGNAL_NE_PROVIDER_UI_MUTATION`  
`SESSION_STATE_NE_WORK_STATE_NE_EVIDENCE_STATE`  
`DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY`
