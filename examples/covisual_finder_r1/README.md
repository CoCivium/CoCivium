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
