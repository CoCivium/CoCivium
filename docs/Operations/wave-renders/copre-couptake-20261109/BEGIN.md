# CoPre+ ↔ CoUptake+ | Wave render BEGIN

**WorkID:** `CoPre.Offshore.20261109`  **Wave:** `CoPreUptakeBridge.R0`  **Phase:** `BEGIN`
**Date:** 2026-11-09 UTC  **State:** `INTENT_RECORDED_NOT_EFFECT`
**Destination:** CoCivium/CoCivium public draft PR #401 branch only.
**Observed starting head:** `99f5f1e90afc9be6f32a3087678430a0fd2d71e1`.
**Privacy:** synthetic public-safe fixture only  **Authority:** read-only CI + authorized draft-branch source writes.

## CoHereNow

The originating session is not custody. CoStatusOffload R0 has 23/23 synthetic tests and a hash-linked public-safe WorkID checkpoint; CoUptake PR #360 already has a standalone cold verifier and receiver-pin checks. Neither alone proves a separate provider or independent receiver accepts CoPre.

The primary continuity gap is the **typed binding between exact source bytes and the intended next deed/stop/authority**. CoUptake verifies an approved, pinned packet of bytes; CoStatusOffload validates work-specific structure and candidate-only semantics.

## Elected proof

1. Pin and reuse CoUptake's existing standalone receiver at `248d3f3bc4836bb2b42378152f087221494cf0bc`, script Git blob `a3bbf5bf6b8ed9c1b54858346f67e8460ee958a5`. Do not fork a new receiver.
2. Build a public-safe synthetic WorkID checkpoint from CoStatusOffload, pack its exact bytes into the **existing CoUptake packet format**, and run the standalone verifier in an isolated Python interpreter against a synthetic receiver-held policy.
3. After exact source-pin verification, cold-check the inner checkpoint's WorkID, authority, STOP and NEXT with the existing CoStatusOffload code in a separately spawned Python interpreter.
4. Adversarially test stale generations, maliciously substituted source bytes, source/inner-checkpoint rehashing, forged/self-generated pins and stale work heads. Distinguish what the two adapters can and cannot establish.
5. Save this BEGIN and a distinct END human-readable render; require CI results and exact branch readback before claiming a successful source test.

## Explicit inversions

- A compact WorkID/pin may be more reliable than a large injected chat prompt.
- Two verifiers on one runner are not two independently governed receivers.
- Valid packet bytes can contain an invalid WorkID or unauthorized effect.
- A self-generated receiver pin can appear valid yet provide no independent authenticity.

**Stop:** missing exact source, conflicting prior heads, non-public data, false receiver claims or unavailable permissions.
**Next wake:** a material public source change or actual receiver-produced readproof.
**Nonclaims:** `BEGIN_NE_PASS | COLD_PROCESS_NE_REMOTE_HOST | PACKET_PIN_NE_AUTHORITY | SOURCE_MATCH_NE_SEMANTIC_VALIDITY | DRAFT_NE_MAIN | NO_RETRY_OF_DENIED_STORAGE_WRITE`.
