# Downloads Orphan-Exposure Census Automation R0

**State:** `PUBLIC_SCRIPT__LOCAL_READONLY_SOURCE__APPEND_ONLY_PRIVATE_OUTPUT`

This script is the bounded fallback while direct X2 machine routing is unavailable.

## What it does

- recursively inventories recent/project-like files in Downloads;
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
