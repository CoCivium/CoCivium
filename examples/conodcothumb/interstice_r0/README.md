# CoInput+ / CoInterstice+ / CoGlyph+ browser canary R0

**State:** public-safe browser-local R&D. Not an X2 installation, OS input driver, CoBar/CoOrbWare native runtime, hardware receiver, sent message or reviewer acceptance.

**What the participant can do now:** Open `index.html` in a browser where local HTML is permitted. Click a demo context, then a glyph, and select **Preview one safe next step**. Optionally enable *15-second local interval counting*, type non-private sample characters in the single demo field, and preview again. A bounded pause can offer a clearly marked prior-review hint. Click **Prepare local JSON** and, if desired, **Download this JSON**. The resulting JSON is a proposal, never an authorization or effect receipt. **Clear everything** resets local text, counters, selected context and the optional capsule.

No network connection, provider call, screen scraping, general clipboard inspection, global keyboard listener, mouse remapping, external file selection, background worker or automatic app submission occurs. The page does not inspect the sample text or key identities. While the field itself holds manually typed text in its visible DOM, the script uses only keydown timing in that explicitly enabled field; the coarse counts stay in page memory unless the participant separately checks an option to include them in an explicitly requested JSON download. Avoid typing secrets in the demo.

The interactive demo is intentionally *not* the real MX Master/Perixx physical event receiver. It maps six clearly marked page contexts and eight glyphs into a **single reversible shadow proposal**. Real Windows foreground/selected-object evidence and explicit consent remain future requirements.

## Inherited prior contracts, no competing controller

- [CoInterstice/CoInversion/CoGlyph architecture](../../../docs/Architecture/COINTERSTICE_COINVERSION_COGLYPH_INPUT_FABRIC_R0_20261024.md) is the source of the candidate relation semantics.
- [CoOrbMouse/CoGlyph public explanation](../../../docs/broadcasts/EVO_ALL_BETTERS_CONTEXT_GLYPHS_TELLS_R0_20261024.md) supplies accessible symbols and the same zero-authority boundary.
- [CoNod/CoThumb shadow policy](../CoNodCoThumbPolicyR0.mjs) supplies one safe preview instead of a worker explosion.
- [CoRelationalUX / CoPredictiveInput](../../../docs/Architecture/CORELATIONAL_UX_PREDICTIVE_INPUT_R0.md) supplies one source object rendered differently and the RAW/preview separation.

The exact Git blob identities were recorded in `manifest.json` when the canary was authored. They are source pointers, not guarantees that the donors will never change. The script does not implement an infinite work or model context. CoThumb/CoPayload R1 remains the proper separate route for actual selected large media bytes and their integrity receipts.

## Actual tests and honest limits

Run locally with Node 22+ standard library:

```sh
node smoke.cjs
node smoke.cjs --output /path/to/new_receipt.json
```

Source/safety logic: **69/69 PASS** in an isolated local Node 22 runtime.

Optional isolated browser QA with Python Playwright/Chromium:

```sh
python3 browser_qa.py
```

Interactive desktop/mobile extracted-HTML QA: **22/22 PASS**. The check exercised context switching, glyph meaning, zero-effect capsule generation, sensitive-context refusal, opt-in coarse intervals, clearing text and counters, keyboard focus, no horizontal overflow, no network requests, and zero browser JavaScript errors. **Direct `file://` navigation was blocked by the browser sandbox**, so it was not measured and no physical X2, local installation, or first-time human acceptance is inferred.

Historical QA correction: The first browser QA draft reported **18 PASS / 4 FAIL** because it compared CSS-transformed uppercase `innerText` to raw mixed-case source and used programmatic focus instead of a keyboard Tab for `:focus-visible`. This failure is preserved in `history/browser_R0A_18_PASS_4_FAIL.json`, followed by source-identical **22/22** corrected QA in the receipts. The subsequent canary adds a voluntary pause-to-priors preview, with all latest source and browser checks rerun.

## Promotion gates (HELD)

1. Fresh, explicitly authorized X2 physical Perixx key and MX Master gesture observation, preserving ordinary controls and a visible stop.
2. A selected, harmless file object and source-bound CoCopy proposal through the existing Windows adapter, not this browser test.
3. Same object on CoMap/CoOrb/accessible text with identical source identity, privacy, currentness and recovery, plus reviewer-origin readproof.
4. Independent first-use, screenreader accessibility, native Windows performance and second-device restore.
5. GitHub Actions completion after the test source is included in the existing bounded CoThumb CI. A workflow file or local PASS is not CI PASS.

**Never claim:** `INTERSTICE_NE_INTENT`, `GESTURE_NE_AUTHORITY`, `GLYPH_NE_TRUTH`, `LOGICAL_OPTIONALITY_NE_ACTIVE_WORKER`, `LOCAL_IS_NOT_LANDED`, `VALIDATION_IS_NOT_ACCEPTANCE`, `NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`, `NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`, `HASHING_IS_NOT_SEMANTIC_INGESTION`, `DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY`.

FOSS Forever | CoGoAll | Working Together Respectfully | privacy by design | display required where effects are possible, wearables optional.
