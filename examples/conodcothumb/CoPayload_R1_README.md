# CoThumb / CoPayload / CoEvoCycle: bounded high-bandwidth canary R1

**Status:** bounded local R1 code and independent 2026-10-24 isolated-container regressions, **not** installed on X2, mapped to a physical mouse, granted credential access, or promoted into a production device controller.

## User-facing intent
One touch eventually opens a local preview of the selected object, then offers an optional explicit file-backed transfer. A rich file is never pasted as megabytes of text: it gets a SHA-256 identity, an exact chunk manifest and a verified, private local buffer. Actual application attachment, upload, send, mouse binding, monitoring and account/device actions are separate, permission-scoped adapters not included here.

## Code and tests
- `CoPayloadCapsuleR0.mjs` + `.test.mjs`: previous <=512 MiB explicit local staging baseline, 10 regression cases.
- `CoPayloadLargeR1.mjs` + `.test.mjs`: new 1..16 MiB chunk streaming, 16 GiB default bounded per-file budget and 64 GiB hard limit with explicit module API budget. Existing chunks reused after an injected interruption; manifests are never overwritten; exact-byte readback detects tampering. 12 regression cases, including a separately enabled 600 MiB sparse-file read.
- `CoRouteSelectorR0.mjs` + `.test.mjs`: selects inline, R0, R1 or HELD based on size and consent/budget; 11 regression cases. A recommendation gives no permission.
- `CoEvoCycleR0.mjs`: finite regression executor, run-output SHA/size and structured JSONL, review-only lane election. No auto-code promotion, secrets, network, send, clipboard or hardware mutation.

## Commands
```
node --test CoPayloadCapsuleR0.test.mjs
CO_THUMB_LARGE_TEST=1 node --test CoPayloadLargeR1.test.mjs
node --test CoRouteSelectorR0.test.mjs
node CoPayloadLargeR1.mjs --preview /path/to/non-sensitive-file
node CoPayloadLargeR1.mjs --stage /path/to/file --buffer-dir /path/to/owned-private-folder --accept-local-copy
node CoPayloadLargeR1.mjs --verify sha256-<filehash>-chunks-8388608.json --buffer-dir /path/to/owned-private-folder
```
The optional automated cycle expects a matching GitHub repository layout, including existing CoNod shadow policy and CoStretch benchmark fixtures. `--allow-partial-sandbox` preserves missing fixture status as HELD instead of inventing PASS; a real CI run must not use that switch.

## Boundaries
- 600 MiB test uses a sparse input. It reads/hash-verifies all logical bytes but stages none of that test to persistent disk. This is not proof of 16 GiB/64 GiB production throughput or multi-device portability.
- File-backed storage is local, not durable/offsite custody. Integrity hashes do not establish trusted authorship or privacy review. Path traversal defenses are best-effort, not a hostile local-user security boundary.
- Chunk writes and manifest publication are serial and exclusive; retry is idempotent on verified immutable chunks, except completed temporary files may be left after process death. No network, provider or external effects are implemented.
- Access to X2 and its actual mouse button is offline from the available connector, so physical mapping is unverified.
- `CO_THUMB_LARGE_TEST=1` causes a bounded ~600 MiB full-read experiment; omit on resource-constrained devices.
- Continuous improvement requires an actual runner such as a scoped GitHub Actions schedule. Source code by itself is not a running unattended service. Reviews can propose changes; source integrations require normal authorization and CI.

`PREVIEW_NE_SEND | STAGED_NE_CUSTODY | NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF | LOGICAL_SCALE_NE_ACTIVE_WORKERS | RICH_FILE_NE_TOKEN_INFINITY`

## Additional bounded composition observation (2026-10-24)

The separately private CoPhoenix R3 ZIP (49,489 bytes; public R3 SHA-256 0f40f2f2f6d6b5494574351ca685d498c41f1738a3eed76d1e0f2f5e3290b4f2) was loaded through the R1 explicit chunk buffer, verified, reconstructed using only that buffer, re-verified as an exact ZIP, extracted via CoPhoenix RESTORE_ZIP.py, and served on a loopback-only HTTP test. Fresh tests: **26 PASS / 0 FAIL / 5 HELD**. Another **33/33 Node regressions PASS**, including an opt-in 600 MiB sparse-file preview. No private payload bytes are published with this module. These counts do not imply an off-provider independent custodian, remote receiver ACK, a 16/64 GiB full transfer, native mouse mapping, or human first-use acceptance.

For public code, see the [coordinating policy and limits](../../docs/Architecture/COTHUMB_COPHOENIX_LARGE_PAYLOAD_R1_20261024.md). Reuse the existing CoNod shadow policy rather than overriding it.
