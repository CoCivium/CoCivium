# CoVisual Relations R0 | CoTurtle∞ ⇄ CoOrbWare

**Status:** source-link research and bounded offline intake prototype. No image download, open-source import, deployment, crawler, recurring watcher, outbound broadcast, user/device scan, image inference, or provider-infinite-context claim.

## Why

An image is a possible evidence, design, accessibility, historical, mathematical, scientific, visual metaphor, training-reference, or counterexample *relation*. An index of every vaguely interesting picture would swamp attention and reproducibility. The correct default is cheap metadata and links, not raw duplication.

## Loop

`SOURCE_LINK -> RIGHTS/PRIVACY_CLASS -> OBJECT/IMAGE_ID -> DESIGN_HYPOTHESIS -> CHEAP CHALLENGE -> REPRODUCIBLE TEST -> EVIDENCE FAN-IN -> OPTIONAL LICENSED REUSE -> SUBSCRIBER DELIVERY -> RECEIVER READPROOF`

Fan out at most three cheap, independent review lanes per elected candidate: (1) rights/privacy, (2) technical/test-fit, (3) accessibility/alternative. Fan in to one coherent decision per bounded wave. Queries may roam widely but must obey site terms, robots/rate limits, and privacy limits. Prohibit background copy of people's images or private screenshots and mass dissemination.

## Existing CoCivium reuse

- CoThumb/CoCopy R1 already classifies IMAGE and proposes dimensions, alt text, thumbnail and rights review. This prototype is **metadata upstream**, not a second clipboard handler.
- CoOrbWare R0 is a *projection contract*, not a deployed OS or infinite renderer.
- Existing enabled CoEvoAll Pulse owns general external-donor scouting. No duplicate automation is created by this package.

## Six external donor classes + one existing baseline

1. **React Flow:** editable graph layouts, keyboard controls (MIT core software, site/demo screenshots require separate rights review).
2. **Cytoscape.js:** query/analysis of graph edges (MIT core, screenshot rights unqualified).
3. **Sigma.js:** potential WebGL dense view, version-specific license/performance review before reuse.
4. **Openverse:** source discovery, **not** a guarantee of each image's license.
5. **Wikimedia Commons:** individually documented media licenses; preserve creator, credit, license version and source URL.
6. **Smithsonian Open Access:** explicitly marked CC0 items can be reused; the entire site is not assumed CC0.
7. **CoOrbWare existing first-look:** local CoCivium baseline for independent usability comparison.

All source URLs and proposed comparisons are in `sources.json`. No screenshots are bundled or relabeled as new creations.

## Review metrics and brakes

- `% image URLs with exact item license & attribution`, `duplicate discovery prevented`, `novel testable relation per hour`, `person-time to first valuable interface improvement`, `proof debt`, `misattributed or overclaimed image rate`, `accessibility defects`, `independently replicated useful changes`.
- When predicted gains fail against basic designs, **record a FAIL and retain the simpler baseline**. Never optimize only aesthetics or source count.
- If rights, consent, source provenance, licensor identity, accessibility, site terms or the target receiver are unknown: link-only, HOLD for public reuse.
- No publication to mailing lists, websites, third-party accounts, `.nodes` or `.sites` without current exact channel, rights and approved audience. *Fan-out of research is not public spray.*
- Use checksum/source identity if an exact individual image is admitted, not just a thumbnail URL.
- Token context is finite: use checkpoints, summaries with citations, retrieval, dedupe, per-job budgets and recoverable references. A larger logical graph is not unlimited compute.

## Run

`python3 -m unittest discover -s tests -v`

`python3 scout.py`

Python stdlib only. This does not access networks or execute external resources. The auto-generated `REPORT.json`, `benchmark_evo.jsonl`, and `HEAD.sha256` are synthetic source-intake receipts, **not real image ingestion**.

## Promotion gates

1. An independent reviewer selects **one exact third-party image**, verifies file-level rights and attribution, records source and license evidence, then one bounded test renders it.
2. An unfamiliar person completes an actual CoMap/CoOrb task faster or more accurately than existing baseline.
3. Only then qualify distribution to an opt-in receiver, preserving source credit, license terms, integrity and receiver readback.

`IMAGE_FOUND_NE_IMAGE_OWNED | SCREENSHOT_NE_LICENSE | LOOKS_RELEVANT_NE_TESTED | RESEARCH_FANOUT_NE_PERMISSION_TO_SPRAY | LOGICAL_INFINITY_NE_UNLIMITED_WORKERS`
