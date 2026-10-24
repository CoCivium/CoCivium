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
