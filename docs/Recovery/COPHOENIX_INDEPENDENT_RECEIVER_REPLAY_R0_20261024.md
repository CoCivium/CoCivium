# CoPhoenix R0 — Independent Receiver Replay Contract

**State:** PUBLIC_REPLAY_CONTRACT__INDEPENDENT_RECEIVER_EXECUTION_HELD  
**Observed:** 2026-10-24

## Exact source

- archive: `CoPhoenix_R0_Offline_ColdStart.zip`
- expected SHA-256: `868a2f8f9ca9276e359917b526c24cc178639b19a600e2c358b514e8f82f0d9f`
- prior scoped cold-start receipt: **26/26 PASS**
- fresh qualification delta: archive checksum matched sidecar; 15 archive members; no path traversal; no symlinks; embedded manifest matched; **13 pinned payload members verified**
- prior 26/26 suite was **not rerun** during that later qualification wave

## Purpose

Close the remaining CoPhoenix recovery cut set with one exact replay on a **separately powered, authorized receiver**.

This contract does not claim that such a receiver has already executed the replay.

## Receiver acceptance sequence

```
obtain exact archive
-> compute SHA-256
-> require exact expected hash
-> extract into fresh empty directory
-> reject absolute / parent-traversal / symlink members
-> verify embedded manifest and all pinned members
-> start bootstrap with network unavailable
-> exercise the bounded offline user actions
-> capture source-bound readback
-> write append-only receiver receipt
```

## Minimum receiver receipt

The receiver must record:

- receiver identity or pseudonymous device identity appropriate to scope;
- observation UTC;
- receiver power/failure-domain relation to source machine;
- archive SHA-256 seen;
- exact-hash match boolean;
- extraction result;
- manifest verification result;
- pinned-member count;
- cold-start result;
- offline/network-isolation statement;
- user-action/readback result;
- any failure or warning;
- exact source reference;
- receipt SHA-256.

## PASS condition

`INDEPENDENT_RECEIVER_RECOVERY_PASS` requires all of:

1. separately powered authorized receiver;
2. exact archive SHA-256 match;
3. safe extraction;
4. embedded manifest verification;
5. all 13 pinned payload members verified;
6. cold-start succeeds without relying on source machine;
7. at least one source-bound readback confirms the intended local content;
8. append-only receiver receipt exists.

## FAIL condition

Any of:

- archive hash mismatch;
- unsafe path/symlink member;
- manifest mismatch;
- missing/changed pinned payload;
- cold-start failure;
- source-bound readback failure;
- receiver depends on the same failed power/control domain being tested.

FAIL is evidence and must be retained.

## HELD condition

Use HELD when:

- no separately powered authorized receiver is available;
- exact archive bytes are unavailable;
- receiver authority is unclear;
- receiver cannot provide exact readback;
- the test would require widening privacy or external-effect authority.

## Lifecycle interpretation

Current evidence supports:

- Library source objects: `LANDED`
- materialized archive copy: `VERIFIED_LOCAL`
- independent receiver pickup: `UNKNOWN / HELD`
- CoStead custody: `UNKNOWN`
- independent offsite recovery: `UNKNOWN`

Do not promote later states from local validation.

## Nonclaims

`LOCAL_IS_NOT_LANDED`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`  
`HASHING_IS_NOT_SEMANTIC_INGESTION`  
`DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY`  
`PORTABLE_ARCHIVE_NE_INDEPENDENT_FAILURE_DOMAIN`  
`OFFLINE_COLD_START_NE_DISASTER_RECOVERY`  
`LIBRARY_SIDECAR_NE_INDEPENDENT_AUTHENTICITY_ANCHOR`

## Next wake

A separately powered authorized receiver becomes reachable with the exact archive and can produce the required readback receipt.
