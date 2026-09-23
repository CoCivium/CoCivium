# Downloads Orphan-Exposure Census Automation R0

**State:** `PUBLIC_SCRIPT__LOCAL_READONLY_SOURCE__APPEND_ONLY_PRIVATE_OUTPUT`

This script is the bounded fallback while direct X2 machine routing is unavailable.

## What it does

- inventories **top-level** recent/project-like files in Downloads by default;
- hashes files up to the configured bound;
- groups exact duplicate content;
- classifies broad content classes;
- performs a heuristic secret-pattern scan on small text-like files **without recording matched secret values**;
- writes a reconciliation report and receipt into a unique CoFarm run directory.

## What it does not do

- delete;
- move;
- rename;
- upload;
- publish;
- write into Downloads;
- contact GitHub or any other network service;
- declare files orphaned merely because they are staged;
- infer landing, pickup, integration, CoEx, canon, or public safety.

## Default boundary

- Downloads root: current user's `Downloads`
- Since: `2026-09-22T00:00:00`
- Scan mode: `TopLevel` by default; optional `Depth1` only after the top-level census is understood
- Max candidates: 10,000
- Per-file hash ceiling: 1 GiB
- Output: `D:\CoCivium\CoFarm\CoDownloadsOrphanExposureCensus\<UTC stamp>`

## CoLUE+ launch

Use the exact commit-pinned launcher printed by the coordinating session. The mature route should be machine-owned MCP/CoGateway or successor; PS7 is break-glass/bootstrap only.

## Next

R1 should compare exact hashes against CoFarm, CoStead, GitHub/public projections, and any elected private replica indexes without requiring Rick to ferry the payloads.

`RICK_NE_FILE_FERRY`  
`STAGED_NE_ORPHANED`  
`UNKNOWN_NE_PUBLIC`  
`PS7_NE_DEFAULT_RUNTIME`


## R0A bounded-scope repair

The original R0 default recursed through the full Downloads subtree and correctly fail-closed when the candidate set reached 189,753 files, far above the 10,000-file ceiling.

R0A changes the default to `TopLevel`. This is the intended first pass because the visible orphan-exposure problem is the top-level Downloads staging surface. Nested directories are not silently inferred safe; they are deferred for separately bounded follow-up.

`FAIL_CLOSED_NE_FAILURE`  
`BROAD_DISCOVERY_NE_BETTER_DISCOVERY`  
`TOP_LEVEL_FIRST__THEN_ELECT_BOUNDED_DESCENTS`
