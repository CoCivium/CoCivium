# CoAll Resource / Correspondence Convergence Map R0

**State:** `CONVERGENCE_COLLISION_MAP__NO_RENAME_NO_MERGE_NO_CANON_NO_RUNTIME`

## CoHereNow

PR #137 has proved enough adjacent resource mechanics that the next useful move is contraction, not another noun.

The candidate now overlaps existing CoAll architecture in several places. R0 maps those overlaps before any extraction, rename, merge or promotion.

## Layering candidate

```text
CoCivia correspondence
  trigger / relation / consent / front-seat gates
        |
        v
CoResourceGrantLayer candidate
  participant-owned grant / scope / revocation / privacy / purpose
        |
        v
CoEnerget+ existing
  capacity/resource field / throttle / route / compact / sleep / fan-out
        |
        +--> CoSubstrateField+ existing
        |      capability / locality / privacy / cost / failure / translation
        |
        v
CoPlan+ / CoOps+ existing
  roadmap / queue / allocation / gates / receipts
        |
        v
CoResourceLease+ candidate
  bounded reservation / fence / revocation / handoff
        |
        v
EffectLease existing
  permission for the actual effect class
        |
        v
bounded execution / checkpoint / failover / receipt
```

This is a relation map, not a hierarchy of authority.

## Important contractions

The PR137 phrase `CoResourceField+` substantially overlaps existing `CoEnerget+`, which main already defines as the capacity/resource field used to throttle, route, compact, sleep or fan out.

So the safe interpretation is:

`CORESOURCEFIELD_CANDIDATE_RELATES_TO_COENERGET__NOT_AUTOMATIC_RENAME`

The opt-in/grant semantics remain distinct because an eligible capacity field does not itself prove participant consent, ownership, scope or revocation.

`RESOURCE_GRANT_NE_CAPACITY_FIELD`

Likewise, the resource lease mechanics are operational reservation semantics. They are not the same thing as an effect lease.

`RESOURCE_LEASE_NE_EFFECT_LEASE`

And substrate capability is not a participant grant:

`SUBSTRATE_CAPABILITY_NE_RESOURCE_GRANT`

## Extraction candidates

R0 identifies four candidates for later review, not movement:

1. grant/opt-in semantics as a thin grant layer feeding CoEnerget+;
2. lease/fence/revocation semantics as a reusable CoOps+ resource-reservation primitive;
3. compaction/activation metabolism as a projection or specialization of existing CoEnerget+;
4. composition/failover/checkpoint-resume as a CoOps+ execution projection using CoSubstrateField+.

CoCivia-specific trigger, relationship, consent and seat semantics stay in the correspondence layer.

## Why not extract now?

Because source lineage, collision review and receiver impact need to be explicit before moving files or renaming concepts.

A clean-looking refactor that silently changes semantic ownership is still a semantic mutation, merely wearing nicer clothes.

`EXTRACTION_CANDIDATE_NE_EXTRACTION`

`OVERLAP_NE_DUPLICATE`

`NEWEST_NE_WINNER`

## Current boundary

This canary performs no file move, rename, merge, runtime mutation, resource wake, correspondence effect, public reply, or authority transfer.

It only exact-binds the current candidate and existing-main donor surfaces and checks that semantic ownership remains non-collapsed.

## Rails

`RESOURCE_GRANT_NE_CAPACITY_FIELD`  
`CAPACITY_FIELD_NE_SCHEDULER`  
`SCHEDULING_NE_EXECUTION_AUTHORITY`  
`RESOURCE_LEASE_NE_EFFECT_LEASE`  
`SUBSTRATE_CAPABILITY_NE_RESOURCE_GRANT`  
`CORRESPONDENCE_TRIGGER_NE_RESOURCE_AUTHORITY`  
`CORESOURCEFIELD_CANDIDATE_RELATES_TO_COENERGET__NOT_AUTOMATIC_RENAME`  
`OVERLAP_NE_DUPLICATE`  
`EXTRACTION_CANDIDATE_NE_EXTRACTION`  
`NEWEST_NE_WINNER`  
`VALIDATION_IS_NOT_ACCEPTANCE`
