# CoMap+ / CoNav+ Public Megascroller R0

**Status:** public-source-only static edition candidate, not a verified hosted website, independent mirror, live CoOrb on X2, independent receiver uptake, canon or CoEx.

This is a **reader view** of existing CoMap / CoNav evidence, not an alternate registry or source of truth.

## Open the edition

- [Offline HTML megascroller](index.html). GitHub's file viewer may display the markup instead of executing it; a normal browser can open the exact HTML bytes locally with no network calls. No private chat, inbox data or external media are embedded.
- [Machine-readable release manifest](release-manifest.json). Includes stable IDs for each public fragment, sources, relation references, rights uncertainty, fallback source URIs and exact SHA-256 digests.
- [Primary nested CoNav atlas](../diagram-of-diagrams-r0.md) and [original CoMap source graph](../../../ai/comap-source-projection-r0.json). No governing duplicate is created.
- [CoPublic Constellation design contract](../../../docs/Evolution/COPUBLIC_CONSTELLATION_MEGASCROLLER_R0.json).

The page has a readable chapter rail, accessible text, a static SVG overview, nested expandable object maps, optional client-side search, stable fragment links, source evidence, and mirror/recovery gates. Its text and navigation remain usable with JavaScript disabled. External source links are optional; they do require connectivity.

## Reproduce and verify

Run from the repository root:

```sh
node scripts/build_public_megascroller_r0.cjs --check
node --test scripts/test_public_megascroller_r0.cjs
```

The build generator uses only Node.js standard libraries and three existing public sources. The exact source graph and all five curated prior-media Git blobs must match. The checked-in HTML and manifest must be **byte-for-byte reproducible**. CI runs negative controls for private-media rejection, source-tamper rejection, fragment identity, no external network dependencies, old-version recovery and no invented independent replica.

The offline restore control copies edition and required source bytes into a temporary directory, then rebuilds and verifies exact content. That is **one-provider/local simulated recovery only**, not a second administrator, independent web host, domain or demonstrated outage failover.

## Constallation and resilience gates

| Surface | Provisional role | Proof status |
| --- | --- | --- |
| CoCivium Git repository | Public files, version history, build and CI | Verify merge, exact source and mainline CI |
| Public custom-domain megascroller | Human first-use surface | NOT DEPLOYED |
| Independent static mirror | Different provider, admin and hosting failure domain | NOT CONFIGURED |
| Offline archive | Export, versioned recovery and cold restore | PORTABILITY TEST ONLY |
| Headless clients | JSON manifest, fragment identifiers, SHA-256 | SPECIFIED; uptake not verified |
| X2 / CoOrb | Local native app or browser display | NOT OBSERVED |

No copy counts as a verified replica until it independently retrieves the exact edition, checks the manifest and source hashes, reports its distinct failure domain and survives an injected primary outage. A successful upload is not a tested backup. A copied page is not independent epistemic verification.

## Successor and navigation discipline

A public fragment has a stable identifier, release ID, SHA-256 over its source object, typed relation references, custody/rights status and fallback source URI. This R0 edition has no demonstrated successor, license clearance or independent hosted origin; the release manifest leaves those fields explicit rather than guessing. Future editions must preserve predecessors and correction paths, not silently redirect old meaning.

The renderer shows exactly published public metadata. Do not include private chats, mail bodies, contacts, screenshot contents or private donor media; do not infer consent or license from the ability to view a GitHub path. CoLUE draft evolution can link a verified public fragment only under its separate consent and send authority gates.

**Next acceptance:** independently serve the exact static edition from a controlled website and a distinct mirror, read back both digests, unplug one host, recover the same fragment and source while navigating via keyboard/mobile, and record actual reader comprehension. Until then: **PUBLIC_SOURCE_ONLY; MIRRORS_HELD; X2_HELD.**
