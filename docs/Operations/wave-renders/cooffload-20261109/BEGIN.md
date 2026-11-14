# CoStatusOffload+ | Wave Render BEGIN

**WorkID:** `CoPre.Offshore.20261109` · **Wave:** R0 · **Phase:** BEGIN
**UTC date:** 2026-11-09 · **Landing:** public review branch PR #401
**Pre-wave verified head:** `004ecb9b01c0deb07d283c6fa5183d559713360e`
**Status:** `INTENT_RECORDED_NOT_RESULT` · **Authority:** draft source and read-only/isolated synthetic CI.

## CoHereNow

Session-local memory is a disposable working cache. Durable shared work state should exist in authorized custody independently of the chat that produces it. Prior source explicitly supports CoVirtualSession, CoSessionAutocycle, CoSessionShadowLedger, RickBar SQLite/WAL continuity and CoLocalModelWorker/Ollama. Their coexistence is **not** evidence of one deployed common-state mesh. X2/CoStead private runtime and other-provider access are unverified in this wave.

An attempted earlier BEGIN write did not appear on GitHub readback. This document is the first verified target of the resumed wave. Treat a tool-attempt as distinct from a source landing.

## Elected bounded change

1. Reuse existing contracts; do not invent a competing session-memory store. Add a portable **public-safe immutable CoPre/WorkID status checkpoint** and no-clobber staging with cold recovery.
2. Allow multiple workers to stage independently. Compare sibling changes against an exact parent; disjoint changes can be considered for merge, overlapping writes HOLD. Actual election remains an authorized writer's responsibility.
3. Test corruption detection, privacy/authority envelope, a new process reading the checkpoint, stale head, concurrent sibling conflict and missing source state.
4. Preserve local cache vs remote mirror availability, latency, security and custody as different axes; offshore storage is not automatically accessible, safer or larger.
5. Save an END render with source/tests/holds and exact CI proof. No private status in this public branch, provider chat mutation, hosted automation change, local-model call or actual remote mount.

## Inversion and next test

A compact WorkID manifest may recover better than full transcripts. A private local mirror may be safer than unreachable cloud storage. More staged branches are not more authoritative heads.

**STOP:** missing current head, permission, currentness or receiver.
**WAKE:** exact material source delta or independent readproof.
**Nonclaims:** `BEGIN_NE_DONE | PUBLIC_FILE_NE_REMOTE_PRIVATE_STORAGE | STAGE_NE_PICKUP | GITHUB_NE_PRIVATE_VAULT | WAL_NE_DISTRIBUTED_LOCK | OLLAMA_SOURCE_NE_LIVE_MODEL | SOURCE_COMMIT_NE_COEX`.
