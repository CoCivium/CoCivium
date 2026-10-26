# CoVisualFinder+ R1 | source-linked inspiration, not a media firehose

**2026-10-25 | PUBLIC-SAFE BOUNDED REFERENCE | NO_BULK_SCRAPE | NO_IMAGE_BYTES | NO_EXTERNAL_SEND | NO_DEVICE_RUNTIME**

[Existing visual-priors source-to-spec contract](../../docs/Architecture/COVISUAL_PRIORS_TO_SPECS_R0_20261025.md) | [Existing CoMedia Inspiration Corpus](../../docs/Architecture/COMEDIA_INSPIRATION_CORPUS_R0_20261025.md) | [CoLens living media](../colensmedia/README.md) | [CoContextRail](../conodcothumb/context_rail_r1/README.md)

## One small outcome

Four externally grounded, source-page-linked inspiration candidates were reviewed as a finite sample. `sources.json` preserves original source URLs, credited owners/institutions, explicit rights uncertainty, accessible motif descriptions, inverse challenges, one narrow test, and at most three **proposed internal role labels** each. `finder.py` refuses unsafe URL hosts, unqualified media copy, unknown role routes, accidental external effects and candidate over-budget. The deterministic `index.html` displays only text and links. **No source image was downloaded, embedded, republished, or transmitted.**

The project is a missing **external-source qualification donor** for the existing CoVisualPriors/CoMedia/CoOmni contracts, not a new global CoOrbWare controller or an attempt to replace the four-image private atlas. The prior private atlas, user's X2 screenshot and WhatsApp/Gmail details were NOT copied into this repo. Their rights/consent remain separate.

## Four real public references, distinct reuse gates

| Source | Source-page evidence | Credit / rights decision | Candidate use |
|---|---|---|---|
| [Wikimedia Commons proposed interwiki graph](https://commons.wikimedia.org/wiki/File:Commons_Interwiki_links_with_wikidata_3.svg) | Description and specific file licence on source page | CC BY-SA 3.0; Jarekt source plus derivative contributor Visite fortuitement prolongee. Licence/attribution/share-alike remain in force for derivatives; **no original bytes copied here** | Directional typed CoMap relations, inverse/edge check |
| [NASA Gas Planet Orbits PIA17304](https://science.nasa.gov/photojournal/gas-planet-orbits/) | NASA page gives title, description and NASA/Lunar and Planetary Institute credit | [NASA imagery guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/) generally allows informational uses but restricts endorsement/third-party materials; item reuse clearance is **not** claimed here | CoOrb scales with units and fidelity warnings |
| [W3C RDF 1.2 Primer](https://www.w3.org/TR/rdf12-primer/) | Multiple/named graph examples; source expressly says **Group Note Draft, not normative** | Individual example-figure reuse rights not independently qualified; link-only | Named graph scope, source and inverse evidence |
| [Creative Commons Linked Commons graph project](https://opensource.creativecommons.org/blog/entries/linked-commons-gsoc-wrap-up/) | Creator-maintained historical graph filter screenshot and description | Image-specific licence not verified; link-only | CoOrb focus+neighbors, filtered discovery and text parity |

For future large-scale discovery, [Openverse's API](https://api.openverse.org/v1/) offers filters for source and license and explicitly imposes query/rate limits. [Openverse's own reuse warning](https://docs.openverse.org/api/reference/made_with_ov.html) says licence metadata is not guaranteed accurate. Thus discovery **does not clear rights**. Wikimedia Commons also requires checking item-specific terms, credits and other applicable privacy/trademark/personality rights. No Openverse API call, scraping, scheduled crawl or bulk media download occurred in this reference wave.

## Run / inspect

```sh
python3 finder.py
python3 finder.py --check
python3 -m unittest discover -s tests -p 'test_*.py'
# Optional GUI proof, needs installed Playwright and local Chromium:
python3 tests/browser_qa.py
```

The generated HTML is offline/self-contained. No JavaScript packages or third-party image bytes. Its CSP blocks image loads, scripted network calls and forms. Four `Open original source page` links are user-initiated navigation only.

Local proof: **50/50 Python source/policy assertions PASS** and **30/30 isolated Chromium desktop/mobile interaction checks PASS** using exact HTML through `page.set_content`. Chromium administration blocked direct `file://` navigation, so that route remains HELD (not a bug silently called PASS). The first 49/50 run was a bad negative-test fixture mutating a copied list slice rather than the source list; preserved in original log and fixed in the test, not the product. Generated source bytes replayed deterministically. No third-party human first-use or actual receiver ACK is claimed.

## Find / Fan / Spray, reframed as evidence-safe distribution

```
FIND public source pointer
  -> QUALIFY source / purpose / licence / privacy / recency
  -> DEDUPLICATE exact canonical URL and source identity
  -> TAG motif + accessible description + challenge
  -> FAN into at most three internal, inactive role proposals
  -> FAN-IN source-linked alternatives and anti-patterns
  -> ELECT one user/use-case first-render experiment
  -> TEST semantic loss and usability against simple text baseline
  -> REQUIRE actual receiver acceptance before release / onward propagation
  -> RETAIN prior source and its revision / stop / wake condition
```

- **Fan** means typed links to roles (`CoMap`, `CoOrb`, `CoTurtle`, `CoA11y`, etc.). It does **not** duplicate messages, generate model tokens, activate agents or deliver to external accounts.
- **Spray** is permitted only for independently authorized, opt-in subscriptions or public pull indexes with the required rights/quality gates, not unsolicited recipient fanout or wholesale image mirroring. This reference has **zero** active receivers.
- **CoOmni+** means virtually large addressability and on-demand rehydration, not limitless context windows, compute or time. Only four metadata records and twelve candidate route labels are materialized here.
- **CoTurtle+** challenges what a visually impressive diagram omits: wrong scale, false causality, false liveness, unsupported licenses, inaccessible text, missing provenance or unearned authority.
- **CoEvergreen+** should wake only when a materially changed source, rights record, receiver need or test result justifies it. This sample is **not** a continuously running monitor or a live web discovery service.

## Acceptance truth

**PASS:** four bounded publicly linked source-page candidates; exact deterministic source/data/UI outputs; policy negative tests; local desktop/mobile UI tests; zero scripted external requests.

**HELD:** source-image publication and derivatives except after item-specific rights clearance; complete historical/session corpus; independent new-user task comprehension; actual CoOrbWare/CoMap receiver pickup; X2 native input; source-change monitor; model token-extension claims; massive parallel workers; public broadcast or subscription ACK.

`SOURCE_PAGE_NE_LICENSE_CLEARANCE | SOURCE_LINK_NE_IMAGE_BYTES | PROPOSED_ROUTES_NE_SENT | BEAUTIFUL_NE_TRUE | GLYPH_NE_AUTHORITY | LOGICAL_INFINITY_NE_UNLIMITED_COMPUTE | LOCAL_IS_NOT_LANDED | NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`.

Code follows this repository's GPL-3.0 license. Third-party works remain under their own rights and are NOT included.

## CoLens source-to-view bridge R0 | executable comparative donor

A bounded [`lens_bridge.py`](lens_bridge.py) converts the **same four validated public-source metadata records** into three **specification payloads** per source: `Text`, `Map`, and `Orb`. All twelve carry identical work ID, source URL, source digest, rights state and epistemic classification. The Map records exactly two advisory relation edges plus one inverse-question node; the Orb records up to three candidate internal role labels and a plain-text alternative. No external images, private screen/media, provider credentials or source image bytes are imported.

It reads [CoLens's existing three-view manifest](../colensmedia/manifest.json) solely to verify a compatible, no-authority view grammar. It **does not re-use** the unrelated Synthkind-theme content, modify CoLens's running renderer or introduce a second image viewer. The output is a typed **view-spec JSON**, not a visual render accepted by a participant.

Reproduce offline from the repository root:

```sh
python3 examples/covisual_finder_r1/lens_bridge.py --check
python3 examples/covisual_finder_r1/lens_bridge.py > visual_lens_bridge.json
python3 -m unittest discover -s examples/covisual_finder_r1/tests -p 'test_*.py' -v
```

Thirty-five new negative/parity assertions verify stable source identities across all three view specifications, no source image bytes, no rights promotion, no authority, typed noncausal inverse questions, strict rejection of undeclared private source metadata, and tampering with graph edges, URLs, source rights or unqualified fanout. Source/registry changes affect the exact structural digest. The existing CoVisualFinder CI workflow now runs the bridge check alongside the original policy/browser-source tests.

**Proof boundary:** This candidate builds **three linked view payloads**, *not* three independent renderers. A real CoMap/CoOrb/accessible first-use, currentness propagation, image-source rights review, media reproduction and a human receiver-origin comprehension ACK remain HELD. A good successor would integrate the resulting work objects into the existing CoLens renderer without starting another frontend.

`ONE_SOURCE_THREE_SPECIFICATIONS_NE_THREE_RENDERERS | INSPIRED_BY_NE_LICENSE_TO_COPY | SOURCE_HASH_NE_TRUTH | MACHINE_PARITY_NE_HUMAN_COMPREHENSION | OMNI_ADDRESSABLE_NE_OMNI_LOADED`.

## CoLens static SVG preview R0 | a visible reference, not another control plane

The [source-to-view bridge](lens_bridge.py) already creates three typed view *specifications* for each of four vetted **public source-page descriptions**. The [offline renderer](lens_preview_r0.py) now turns those specifications into a single **standalone, script-free HTML file** containing 12 actual Text/Map/Orb panels with eight inline SVG drawings and visible accessible alternatives.

**Default has zero network or writes**:

```sh
python3 examples/covisual_finder_r1/lens_preview_r0.py --check
python3 -m unittest discover -s examples/covisual_finder_r1/tests -p 'test_*.py' -v
```

To create a local, public-safe preview explicitly:

```sh
python3 examples/covisual_finder_r1/lens_preview_r0.py --output colens-public-inspirations-r0.html
```

Open that generated file in a browser. It displays **four public metadata references**, each with the same work ID, source SHA-256 identity, rights status and epistemic class across Text, Map and Orb. Map shows **PROPOSED** rather than causal lines; Orb shows *illustrative roles*, never live workers; Text and captions provide readable alternatives. No original images, third-party artwork, personal screenshots, audio/video, external scripts, private data, analytics, clipboard, network fetching or provider credentials are embedded. Clicking an original-source link is a deliberate browser navigation; source rights do not automatically permit republishing its media.

The **existing CoVisualFinder GitHub Actions workflow** creates an unhosted public-safe HTML artifact for independent review. This renderer is a **bounded integration acceptance donor** to the elected [CoLens living-media UX](../colensmedia/README.md), not a competing deployed frontend, production site, working native CoOrbWare or permission to bypass release review. The markup is structurally renderable in ordinary browsers; actual browser visual QA, screen-reader comprehension, a new user's first-use and receiver-origin ACK remain independently **HELD**.

**Acceptance scope:** new 32-case Python suite checks 4 sources, 12 views, eight SVGs, source/hash/rights parity, safe escaping, no external effects, negative cases and deterministic explicit export. Preserve every earlier failure and retention receipt. Do not silently upgrade "specification" to "independent visual user success."

`INSPIRATION_NE_SOURCE_REUSE_RIGHTS | HTML_SOURCE_NE_HUMAN_ACCEPTANCE | RENDERED_MARKUP_NE_OFF_PROVIDER_PICKUP | MAP_EDGE_NE_CAUSE | ORB_CIRCLE_NE_AGENT | CI_ARTIFACT_NE_PUBLIC_SITE`.
