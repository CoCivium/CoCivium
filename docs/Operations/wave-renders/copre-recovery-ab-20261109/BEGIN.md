# CoPre recovery A/B | Wave render BEGIN

**WorkID:** `CoPre.Offshore.20261109` · **Wave:** `CoPreRecoveryAB.R0` · **Phase:** `BEGIN`  
**UTC date:** 2026-11-09 · **Authority:** public draft-branch source and read-only CI  
**Observed starting head:** `a2442ba5fd442a0bfb6a5a45cca185268acc3bc0` · **State:** `INTENT_ONLY`

## Why this wave

[CoPre/CoStatusOffload PR #401](https://github.com/CoCivium/CoCivium/pull/401) just passed 9/9 isolated CoUptake bridge checks. The receiver pin was self-generated in a synthetic fixture, and no separately authorized receiver or independent durable storage was present. It would be false to call that external recovery or adoption.

The remaining useful read-only experiment compares **two packet strategies** under the same synthetic work state and failure assumptions:

- **A: compact WorkID + source revision + exact expected digest**, requiring a separately accessible source resolver.
- **B: complete portable CoUptake packet**, requiring an independently trusted receiver pin to assert trust; the packet can retain bytes when the source resolver disappears.

## Elected bounded experiment

1. Reuse the existing CoStatusOffload checkpoint compiler and CoUptake standalone receiver at exact pinned donor commit; do not implement another packet codec or trust service.
2. Test A and B against the same public-safe synthetic checkpoint for healthy source, missing source, changed bytes, malicious WorkID/authority, stale policy and incomplete pins.
3. Measure actual JSON transport sizes, byte match, recovery outcome and which explicit dependencies remain. Never infer latency, costs, usability or security from payload size alone.
4. Save a separate END render recording the result and exact CI evidence, including negative outcomes. END authoring is before CI completion and must not preclaim PASS.

## Inversions

A tiny pointer may outperform a complete packet where a qualifying source is reachable. A complete packet may restore offline bytes but cannot prove currentness or publisher authority. Two replicas sharing credentials do not have independent availability.

**STOP:** no authorized source, no independent receiver trust, or no material change.  
**Human relay:** none for this draft-source wave.

**Nonclaims:** `BEGIN_NE_PASS | SYNTHETIC_PIN_NE_INDEPENDENT_TRUST | LOCAL_OFFLINE_NE_CROSS_PROVIDER | SIZE_NE_USEFULNESS | BYTE_RESTORE_NE_CURRENT_HEAD | SOURCE_LANDING_NE_COEX`.
