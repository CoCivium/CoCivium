# CoLens legacy highlight-registry bridge R0

**Purpose:** A real, bounded compatibility demonstration: take the existing **public source-controlled** flat `ai/highlight-assets.json` and project its metadata into **CoMap + CoOrb + Text**, without changing the JSON, pretending applications are interoperable, or creating another control plane. This is an additive donor to [CoLens R0](../README.md) and [CoLivingHighlight+](../../../docs/Architecture/COLIVING_HIGHLIGHT_ASSETS_R0.md).

## Why this is different from a proposal

This adapter reads **one real existing registry** containing ten highlights, with an explicit pinned Git blob identity (not a fabricated source fixture). It rejects changed source bytes until reviewed. It creates a standalone HTML file without JavaScript, network, clipboard access, provider calls, user/device metadata, OS hooks or outbound communication.

A pre-existing application can continue using the untouched original JSON. Removing only the generated `preview.html` restores the original experience. The overlay neither changes format ownership nor assumes new authority.

## Reproduction

From the **repository root**, using Python 3.9+ standard library only:

```sh
python3 -m unittest discover -s examples/colensmedia/highlight_registry_bridge_r0 -p 'test_*.py' -v
python3 examples/colensmedia/highlight_registry_bridge_r0/bridge.py --build
python3 examples/colensmedia/highlight_registry_bridge_r0/bridge.py --check
```

Then open `examples/colensmedia/highlight_registry_bridge_r0/preview.html` in a local browser. The HTML is **deliberately not committed**: CI publishes a generated artifact for reviewers; the repository keeps just the deterministic builder and source.

### Three compatible presentations of exactly one source

- **Text:** all original ID, name, status and readiness columns, one row per entry.
- **CoMap:** the only justified edge is `REGISTRY --LISTS_ENTRY--> ASSET`. It does not invent interasset dependencies, causal relationships, funding, rights or scientific proof.
- **CoOrb:** summary of declared candidate/public status counts and an accessible enumeration, never a live health, device, release or popularity counter.

All three sections carry the exact source SHA-256. The source declares an update timestamp from September 2026, so **currentness remains NOT_VERIFIED_CURRENT** until separately probed. A fresh page render is not proof the source refreshed.

### Legacy loss and authority

The source supplies **no** per-asset evidence links, timestamps, rights proof, current execution status or verified receiver acknowledgments. Those are listed as translation losses, not supplied by guesswork. `PUBLIC_HIGHLIGHT` is the source's own status token, not permission to republish a third-party asset. The bridge does not accept private/user-selected files, even if its HTML happens to look polished.

Stop/rollback: delete generated `preview.html`. The original registry remains intact.

### What the test proves and what it does not

The pure 30-case test set checks pinned source identity, escape/XSS text treatment, duplicate/unknown JSON fields, unsupported statuses, one-source/three-view parity, readiness and currentness non-promotion, unknown rights, and zero effects. The CI runner builds a deterministic offline HTML artifact and checks exact parity. These are **source and generated-output tests**, not independent browser accessibility acceptance, user-value measurement, X2 integration, CoStead custody or a deployed web service.

The [Great ReFact+ first-proof](../../../docs/Architecture/COGREAT_REFACT_R0_20261025.md) still requires a human task comparison and removal/fallback observed in the original product. The full promised human-time improvement remains **HELD**, pending an independent first-use trial.

`READ_ONLY_BRIDGE_NE_NATIVE_APP_REPLACEMENT | SOURCE_DECLARATION_NE_VERIFIED_TRUTH | MAP_LINE_NE_CAUSAL_LINK | RENDER_DATE_NE_SOURCE_CURRENTNESS | ARTIFACT_NE_RECEIVER_ACK | ADAPTER_REMOVABLE_NE_VENDOR_PARTNERSHIP`.
