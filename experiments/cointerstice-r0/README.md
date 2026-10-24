# CoInterstice+ / CoInversion+ / CoGlyph+ R0 shadow canary

**Candidate test donor for existing CoOmniIO PR #237. Not a new input controller, executable desktop agent, mouse binding or user/recipient acceptance.**

This closes exactly one narrow gap between the 2026-10-24 public CoInterstice *design* and an independently rerunnable, effect-free implementation. It is a deterministic Node.js 22 pure-function unit, not a keyboard logger. All inputs are **synthetic fixtures or explicitly supplied, non-sensitive local editor metadata**. There is no file write, subscription, OS hook, sensor, network, clipboard read, auto-trigger, model worker, scheduler, or authority elevation.

## Five-second local proof

```sh
node --check experiments/cointerstice-r0/CoIntersticeShadowR0.mjs
node --test experiments/cointerstice-r0/CoIntersticeShadowR0.test.mjs
node experiments/cointerstice-r0/CoIntersticeShadowR0.mjs --demo
```

The output includes a *coarse* gap bucket only, one candidate preview, the typed inverse-claim classification, and explicit zeros for all effects. Source text, typed characters, window titles, pointer coordinates, exact interval, remote identifiers and passwords do not appear.

### Inputs and bounded semantics

- Required: `opt_in:true`, `scope:LOCAL_EDITOR|LOCAL_CANARY`, `event_type:INPUT_GAP|POINTER_DWELL|FOCUS_CHANGE|BUTTON_PREVIEW`.
- Optional: declared `interval_ms` (0..60000 in **one** synthetic/explicit event; immediately buckets), `pointer_zone` LEFT/CENTER/RIGHT/NONE, typed `relation` and `explicit_preview:true`.
- Missing opt-in, sensitive/unknown scope, raw key/text/clipboard/coordinates, unsupported fields, invalid timing or unknown event: **HOLD** and zero effects.
- No implicit preview from a pause: it must be explicitly requested. Without that, result is **PASS_NO_ACTION**.
- Inversion never proves the reverse of a causal edge. A closed-world absence *with a declaration of evidence* is a candidate, not independently authenticated proof. Open-world `NOT_OBSERVED` is never silently promoted into `OBSERVED_ABSENT`.
- Glyphs carry **versioned plain-language labels**; a symbol or a color alone is never enough for accessibility or authority.

## Fan-in, not a new stack

Source contracts:

- `docs/Architecture/COINTERSTICE_COINVERSION_COGLYPH_INPUT_FABRIC_R0_20261024.md` on current main.
- `docs/broadcasts/EVO_ALL_BETTERS_CONTEXT_GLYPHS_TELLS_R0_20261024.md` on current main.
- `examples/conodcothumb/CoNodCoThumbPolicyR0.mjs` current public shadow policy.
- Existing CoOmniIO PR #237 source bundle, input mapping and bounded queue are **unchanged**. This R0 shadow canary is not incorporated into that release's installed package manifest.
- The Synthkind Declaration may inform ethical interpretation, but symbolic G_d, Planck and energetic-aura motifs do not become established physics or device authorization.

## Real-world acceptance still missing

1. X2 remote observer reconnect or another authorized native observer.
2. One specific per-app, locally opted-in key/pointer event producing only a coarse transient feature, with real Windows readback and cancellation.
3. One accessible `Preview / Cancel` UI on X2; evidence that raw keys are not retained, no sensitive editor is observed and native middle click works unchanged.
4. Independent participant comprehension of glyph labels; no inference from dwell/tempo of intention or identity.
5. One actual rich-media target-app receipt if later attempted with an explicit, supported destination.

The Perixx keyboard working on X2 is human-observed today, not proof of CoInput adoption; Desktop Commander has been reporting the remote device offline. No cross-device recovery, sent email, public awareness, active million-session fabric or CoEx claimed.

`INTERSTICE_NE_INTENT | PAUSE_NE_AUTHORITY | INVERSIONS_NE_CAUSAL_PROOF | GLYPH_NE_TRUTH | SOURCE_NE_RUNTIME | LINUX_TEST_NE_X2_HARDWARE_ACK | POINTER_NE_RECEIVER_ACK | PREDICTED_NE_EXECUTED`

## CoPriMath GlyphRail R1 | 1,760 lazy descriptions, eight visible choices

**Dependency-free pure Node 22 source**: [CoPriMathGlyphRailR1.mjs](CoPriMathGlyphRailR1.mjs) plus [tests](CoPriMathGlyphRailR1.test.mjs). This is an optional **structural rendering donor** for [CoMiddle R0](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COMIDDLE_COPRIMATH_GLYPHRAIL_R0_20261024.md), not a competing input controller or a system-wide device binding.

- Twenty exact semantic glyph IDs with accessible labels, plain ASCII fallbacks and spoken descriptions.
- Eleven *declared* object/surface contexts, each selecting exactly eight visible symbols. Eight possible question/challenge/replay operators give `20 * 11 * 8 = 1,760` **syntactic logical addresses**. The code decodes any single logical address without materializing a fleet.
- **Preview-only**: an explicitly selected known context, public/local classification, synthetic or explicit-UI gesture, and deliberate preview request are required. Raw keys, text, clipboard, arbitrary device fields, unknown/sensitive screens, unchecked native mouse events and external effect requests all fail closed. It never reads screen, current application, pointer, camera, microphone, passwords, local files or a network service.
- Typed inverse/negation candidates distinguish a plausible reverse hypothesis from actual logical inverse truth. Unobserved is not absent; alleged absence needs scope and evidence. G_d and ET symbolic/story lanes retain clear nonmeasurement labels.
- Source IDs here are **declared pointers, not authenticated evidence**. `PASS_DECLARED_SHADOW_PREVIEW_ONLY` means the pure object was constructed, not that the real user saw the correct surface or that any action was accepted.
- Zero network requests, OS hooks, workers, device changes, clipboard inspection, persistence or external sends. The recipient ACK is `null` by design.

Run `node --test experiments/cointerstice-r0/CoPriMathGlyphRailR1.test.mjs`. The existing CoOmniIO CI also runs its source syntax check and tests. **CI PASS qualifies synthetic logic only**; X2 middle/thumb activation, accessible first-use, CoBar overlay and CoMap/CoOrb real projection are HELD until independently observed.

**Next differential gate**: use the same synthetic source ID in this R1 glyph selector and the existing CoNod local browser rail; compare readable meaning, inverse/negative-state treatment, exact number of shown options and correct accessibility. Keep only unique behavior from R1 after review. Never install overlapping mouse hooks.

`ADDRESSABILITY_NE_EXECUTION | GLYPH_NE_PERMISSION | STORY_NE_PHYSICS | PREVIEW_NE_ACK | COLOUR_NE_ONLY_MEANING`.
