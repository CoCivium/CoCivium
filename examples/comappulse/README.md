# CoMapPulse+ / CoQuanta+ / CoAckRAW / CoReWis R0

**State: OFFLINE_PUBLIC_CANDIDATE. This is NOT the production CoMap, CoOrbWare, RickBar, MX mouse mapping, global event bus, autonomous agent, or live receiver network.**

CoMapPulse R0 is a deliberately bounded projection onto the existing CoCivium architectural proposals. It demonstrates nine public-safe resources, twelve typed relations, five receiver dispositions, a quiet CoOrb-style surface, and an **opt-in, local static completion displayed after the input caret**.

## Try it

Simplest: open **`CoMapPulse_ONEFILE_R0.html`** with a browser that permits local files. It embeds the exact public graph and both small JavaScript files, with no remote dependency. On managed browsers that block `file://`, use a loopback server instead.

From the `examples/comappulse` directory on a machine with Python 3:

```sh
python3 build.py
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/index.html` in your browser. Stop the server with Ctrl+C. The page makes no outgoing requests; the local server only provides static files. Many browsers also allow opening `index.html` directly, but managed browsers may block `file://` access. Browser testing in the isolated build environment therefore used `page.set_content` with the **same source files inlined**; it does not establish that direct file navigation works there.

Select any graph node, inspect its typed trails, and switch among CoMap, Trails + Time, and Quiet CoOrb modes. Expand the alternative list of all nodes for keyboard navigation or small screens.

Enable *local suggestions*, type `CoM` with the cursor at its end, and observe `ap+` appear as ghost text after the caret. Explicitly press F2 or click **Accept hint** to insert it. Suggestions are off by default, and nothing is submitted. A generic private phrase receives no completion; the small static dictionary is inspectable in `core.js`.

Select CoVIA & nodes, click **Record local inspection**, and note that receiver ACK remains **NOT_OBSERVED**. There is no route to elevate the static data into a verified ACK in R0.

## Verify

```sh
node tests/test_core.cjs
python3 build.py
```

The Node test has 28 deterministic assertions, including forged-ACK rejection, held receiver behavior, privacy allowlists, explicit prediction, local-only effects, malformed inputs, and parity between the human HTML and machine `graph.json`.

A separate Playwright/Chromium interaction canary was run in an isolated sandbox with scripts inlined, testing the real visual map, 9 nodes/12 edges, three views, local ghost input, F2, five receiver rows, no outgoing requests, local-inspection semantics, and mobile list navigation. The canary script and its report accompany the separate downloadable bundle, not this public default package.

## Relation vocabulary

- **Identity**: `node.id`, `edge.id`, `source`.
- **Epistemic**: `DOCUMENTED` means the linked public source describes a concept, NOT that a future implementation is working; `PROPOSED` has no proof yet; `HELD` cannot be treated as delivered.
- **Time**: `edge.time` is qualitative, not a live clock or forecast.
- **Acknowledgment**: all R0 `ACK_VERIFIED` inputs are rejected; actual receiver readproof requires a future authorized adapter and exact-object check.
- **CoQuanta+**: separate budget/evidence/attention units here; NOT physical quantum sensing.
- **CoReWis+**: rebuilding a view from the same graph and schema, not inferring hidden conversation memory.
- **CoMap+/CoOrbWare+**: multiple UI projections over one relation source, not a deployed Windows/macOS surface.

## Broadcasting and privacy

The receiver table is a **routing plan**. GitHub is a public **pull/discovery** surface; Gmail is suppressed as a recent duplicate; dedicated CoVIA, `.nodes`, `nodes`, `.sites`, and `sites` are **HELD_NO_RECEIVER**. Nothing sends automatically.

No account credentials, inbox content, private machine paths, clipboard reads, live device state, model calls, native hotkeys, tracking, persistence, or third-party remote sessions exist in this prototype. Private local custody inventories are NOT included in the public package.

A renderer cannot conjure data, authorization, model inference, subscriptions, or a verified receiver. A logical session can help replace provider-specific *interfaces*, but eliminating provider costs requires separately tested inference and recovery alternatives.

## Key sources and existing work

- [CoVirtualSession+](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COVIRTUAL_SESSION_MORPHOLOGY_R0.md)
- [CoSubscriptionEcology+](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COSUBSCRIPTION_ECOLOGY_R0.md)
- [CoAll public pulse](https://github.com/CoCivium/CoCivium/blob/main/docs/Updates/COALL_PUBLIC_PULSE_20261023_R0.md)
- [CoAttractorPull+ / CoCopy+](https://github.com/CoCivium/CoCivium/tree/main/examples/coattractorpull)
- [CoCopy+ middle-click review](https://github.com/CoCivium/CoCivium/pull/213), a separate browser-scoped input prototype; NO OS button remapping.

## Next high-bar discriminator

Bring **one** opted-in, independent receiver and a nonsecret example. Have it fetch exact bytes, independently hash and acknowledge them, and confirm that CoMapPulse differentiates its receipt from the existing GitHub pointer. Then test the same projection on Andrew's Mac with his preferred Pi/Claude/Ollama route, with matched baseline and measured attention, cost, latency and recoverability.

**Nonclaims:** `DISCOVERED_NE_USABLE` · `VIRTUAL_NE_RUNNING` · `POINTER_NE_ACK` · `LOCAL_INSPECTION_NE_REMOTE_PICKUP` · `FORECAST_NE_FACT` · `PROJECTED_NE_INSTALLED` · `NO_ALL_TO_ALL_BROADCAST` · `NOT_ON_ANDREW_MAC`.

Inherits the repository GPL-3.0 license. FOSS, privacy-by-design, inclusive opt-in, no crowns, no coercion, no corruption.
