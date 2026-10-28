# CoMapOmni+ R1 | Five-minute independent reproduction

This is **an offline, public-safe browser experiment**, not an installed operating-system layer or a connected network of AI workers.

## Run without an AI account

1. Unpack the ZIP somewhere you control.
2. Open `CoMapPulse_ONEFILE_R1.html` locally in a modern browser. It embeds all code and its nine-node base graph plus nine *non-established* candidate relations. Browser restrictions may affect direct `file://` navigation; do not disable security policies merely to run the demo.
3. Inspect the CoMap trails. In **What isn't connected (yet), and why?**, compare "Missing & safety gates" with "Unknown & hypothesis." The latter are **not** verified edges.
4. Opt into local cursor suggestions. Type `CoNot`, then accept `CoNotSpace+` with the visible button or F2. Do not expect automatic routing or sending.
5. Close the page and reopen. The demo has no persistent or external state, sessions, subscriptions, or sender/receiver acknowledgments.

## Verify via Python and Node.js

From the unpacked `CoMapOmni_R1` directory:

```sh
node tests/test_core.cjs
node tests/test_omni.cjs
node tests/test_receipt.cjs
python3 verify_benchmark.py
python3 -c "from pathlib import Path; from verify_benchmark import verify; print(verify(Path('benchmark_evo_R1.jsonl'), Path('HEAD_R1.sha256')))"
node verify_benchmark_r1.cjs
python3 verify_package_R1.py
```

Rebuild the browser artifacts from their source with `python3 build.py` and inspect the resulting output changes. The browser canary source `browser_canary_r1.py` is optional and depends on Playwright plus an available Chromium executable; it is **not** a dependency for the demo itself.

## What this tests

- The original map remains **nine nodes / twelve existing trails**.
- The new CoOmniIO/CoNotSpace layer displays **nine separate candidate, missing, intentionally blocked, or hypothetical relations**, without drawing them as validated graph connections.
- All candidate effects remain `NONE`, every receiver ACK remains `NOT_OBSERVED`, and private URLs fail validation.
- A recorded historical R0 defect accepted a stale completion. R1 rejects that completion.
- Node tests bind the underlying graph **exact bytes** (SHA-256), while the browser itself checks the public schema and snapshot, not cryptographic custody.

## CoAndrew / model choices

Claude, PI.dev, Ollama and other open models can evaluate the design, but **none is called by this package**. Before describing any adapter as integrated, run an authorized real task and compare it with the no-model baseline. The old `.md` instructions by themselves are not a running agent or tool.

## Source provenance and no-claims

This version extends the CoMapPulse R0 branch, and links to CoCivium [issue #214](https://github.com/CoCivium/CoCivium/issues/214) and [issue #178](https://github.com/CoCivium/CoCivium/issues/178). The original `CoMapPulse_ONEFILE_R0.html` is retained as a historical artifact. `HISTORICAL_R0_PACKAGE_MANIFEST.json` is explicitly *not* the current package manifest.

No WhatsApp screenshots, contact details, source secrets, real credential probes, CoStead access, site/node fan-out, emailed outreach or device control were included. CoSpirit/CoET/G_d labels are questions or symbolic hypotheses, **not evidence of a supernatural, extraterrestrial or physical channel**.

**Promotion gate:** independent Mac/X2 user comprehension and task completion, verified device/receiver pickup, an alternative provider run, and actual time/cost/resource metrics remain **NOT RUN**.

`LOCAL_CHECK_NE_INDEPENDENT_ACCEPTANCE | DISPLAY_NE_AUTHORITY | MISSING_EDGE_NE_PERMISSION | POINTER_NE_ACK`
