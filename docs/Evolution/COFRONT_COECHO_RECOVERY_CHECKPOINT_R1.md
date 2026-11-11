# CoFront+ / CoEcho+ recovery checkpoint R1

Status: **LOCAL SYNTHETIC TESTS PASSED; PUBLIC RUNTIME NOT ESTABLISHED**.

## Executed on 2026-11-09

A new local, independently rerun-able Python prototype was constructed and tested, distinct from the earlier unpublished 93-line prototype. The local command `python -m unittest -v test_cofront_echo.py` reported **9 tests run, 9 passed, 0 failures**. Local files:

- `cofront_echo.py`: SHA-256 `83128388ff363274aed955a0d0a00ea8f098745808d4a3a1d57fc92e8f557631`
- `test_cofront_echo.py`: SHA-256 `0125d88a3e9839b48bd667652dea0b249f5aa9fda9a7024c4f9b0343052c03b0`

Coverage: duplicate replay, changed digest preservation, event time separation, private record exclusion, deterministic replay, missing dependency detection, retraction history, unsupported verified-effect rejection, and public projection checksum.

**Limits:** synthetic records; in-memory only; no durable disk write; no real crash simulation; no authorized historical ingestion; no independently operated receiver; no cross-session synchronization; no 24-hour persistence; no live X2 integration. A checksum alone is not authenticity proof. The current prototype accepts a caller-supplied independent_receipt flag and does not authenticate its provenance. It does not prove no private content is leaked through unrestricted user-supplied public fields. Do not treat it as production-safe.

## Recovery rails

1. CoFront: discover source and custody, preserve source digest, avoid duplicate work.
2. CoEcho: chronological, dependency-first, risk-first, inverse, and predictive-retro passes. Predictions nominate searches, not past facts.
3. CoTime: keep source event time distinct from discovery time, receipt time, and publication time.
4. CoSilo: explicitly register missing dependencies as HELD, not silently dropped.
5. CoTru: label source observation, inference, proposal, test result, verified effect distinctly.
6. CoPublic: publish only explicitly authorized, independently readable redacted projections.
7. CoBreakGlass: freeze conflicting writes and preserve prior versions rather than clobber.
8. CoReGroup: reconcile divergent session claims through source lineage, never by majority vote alone.
9. CoBoogie: vary search strategies while preserving repeatable controls and regression tests.

## Next gates

- Commit runnable prototype and tests to repository and verify GitHub Actions.
- Replace flag-based trust with cryptographically/verifiably bound evidence.
- Add durable append-only ledger, crash recovery, fenced writer, schema and URL validation, and strict public allowlist.
- Perform bounded backfill of already public repository sources, then independent readback and restoration.
- Only then claim operational CoFront+/CoEcho+ recovery; cross-session and X2 claims remain separately held.

References: `docs/Evolution/COFRONT_COECHO_RETRO_RECOVERY_R0.json`, `docs/Evolution/COFRONT_COECHO_LOCAL_TEST_RECEIPT_R0.json`.
