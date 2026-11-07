# CoSysAll+ Semantic-Zoom Payload Substrate R0

**Status:** public experimental architecture, **not canon, deployed global CoMap, live X2 runtime or auto-evolving media network**.  
**Date:** 2026-11-06 (America/Toronto)  
**Existing donors:** [CoMap R3](https://github.com/CoCivium/CoCivium/issues/217), [CoMap source projection](../../ai/comap-source-projection-r0.json), [CoAll evolution fabric](../Evolution/COALL_GITHUB_EVOLUTION_FABRIC_R0.md), [Civ2+ federated cell hosting](CIV2_FEDERATED_CELL_HOSTING_R0.md), [CoBook rich-media architecture](COBOOK_LIVING_RICH_MEDIA_SYSTEM_R0_20261025.md).

## Governing decision

**CoSysAll+ is a candidate system-of-systems *payload and projection fabric*, not a replacement for CoAll or CoMap.** One durable source-bound relational/object graph may expose many user-relative views: CoMap, CoBar, CoOrb, CoBook, accessible list, machine packet, spatial scene, media edition, printed/cached page, or no visual surface at all.

**Payload density = useful, recoverable, inspectable meaning per constrained user/receiver cost.** The objective is not maximal bits on screen, number of nodes, shader complexity or physical resolution. Optimize multi-objective: information gain, correct task completion, comprehension, evidence fidelity, accessibility, autonomy, safety, frame latency, bandwidth, storage, energy, privacy exposure, maintainability, and voluntary return.

**PixelPlanck / inter-pixel universe is a metaphor, not a physical pixel limit or claim of infinite data.** An image has finite source resolution; interpolating pixels creates no new sourced fact. *Semantic zoom* can continue through newly qualified objects/relations/versions while preserving local coordinates and stable hierarchical addresses. Stop if a deeper source has not been supplied, or expose an explicit hypothesis/unknown rather than inventing detail.

## Coordinate and addressing model

Separable dimensions:
- **Spatial** `x,y,z` where actually meaningful (map, 3D scene, volumetric/physical media); retain CRS/units if geographic.
- **Semantic** `object_id, relation_id, source_ref, epistemic_class, intent/receiver, authority_scope`.
- **Temporal** `source_time, observation_time, validity_interval, version, event_path, counterfactual_time_lane`.
- **Media** `manifestation_id, mime, codec, intrinsic_resolution, transcript/captions/alt, rights, safe fallback`.
- **Structural** `parent, children, adjacency, provenance, contradiction_set, missing_link_unknowns`.

Use hierarchical, content-addressed **object/relationship manifests**. A path like `cosysall://cell/space/object/relation/source@version` is illustrative notation only, **not an implemented URI protocol**. Do not represent depth solely as one giant floating-point pixel coordinate: numerical precision fails, semantic branching is not Euclidean, and many relations have no meaningful geometry. Use stable IDs plus hierarchical local coordinates.

## Suggested tile/packet envelope (candidate fields, not schema enforcement)

```yaml
tile_id: stable-publisher-defined-id
source_object_refs: [typed-public-or-authorized-refs]
source_hashes: [digest-with-algorithm]
semantic_path: [space, object, relation, evidence]
spatial_extent: null  # optional, units and CRS if present
time_extent: null     # optional
lod_range: [0, 4]
epistemic_class: OBSERVED | INFERRED | HYPOTHESIS | UNKNOWN
claim_scope: SOURCE_REGISTERED_ONLY
authority_and_consent_refs: []
privacy_class: PUBLIC | PRIVATE | RESTRICTED | UNKNOWN
rights_license: UNKNOWN
media_variants: [text, svg, image-tile, video, audio, 3d-scene, structured-json]
accessible_fallback: text-and-list
estimated_bytes: null
estimated_compute_cost: null
expiry_or_revalidation: required
next_child_manifest: null
provenance_and_receipts: []
```

A `PUBLIC` status requires *actual publication authorization*, not a guessed label. The current R0 viewer embeds only already-public registry metadata; it is not proof of permission to harvest private documents or perform external actions.

## Render policies, including **no render**

1. **Qualify** source, receiver, privacy, rights, device capabilities, currentness, claim status, and effect authority *before* any payload fetch.
2. **Select** relevant semantic or spatial tiles with a bounded attention/compute/network budget.
3. **Render** only when useful and authorized. Prefer text/thumbnail/summary at coarse scale; progressively decode high-resolution imagery, sound, video, 3D or dense relations when an eligible viewer focuses.
4. **Defer** offscreen, out-of-context, lower-priority or excessive detail. `NOT_DRAWN` does not mean `DELETED` or `UNKNOWN`.
5. **Deny** private, revoked, malicious, unlicensed or unauthorized payloads, including speculative inferences of protected data; avoid fetching secrets solely to decide not to display them.
6. **Machine-only/no-screen** consumers receive typed source-bound packets, not a hidden canvas. Ambient/voice/braille/print projections are separately designed receivers, not falsely claimed as implemented by a JSON-only test.
7. **Refresh or invalidate** when source, consent, risk, schema, authority or expiry changes. `LAST_RENDERED` is not `OBSERVED_NOW`.
8. **Record** output claim, exact input hashes, what was suppressed and why, cost and meaningful reader/receiver outcome without unnecessary surveillance.

### No-render reason classes

`OFFSCREEN`, `BUDGET_EXCEEDED`, `LOD_NOT_RELEVANT`, `UNAUTHORIZED`, `REVOKED`, `RIGHTS_UNKNOWN`, `SOURCE_MISSING`, `UNVERIFIED_CLAIM`, `STALE`, `UNSUPPORTED_CODEC`, `MACHINE_ONLY`, `USER_PREFERS_NO_MEDIA`. These reasons are a proposal, not a universal vocabulary; distinguish temporary deferral from denial.

## Rich-media standards to reuse rather than rewrite

- **IIIF Image API 3.0** for very high-resolution images, region crops, multiscale tiling; **Presentation API 3.0** for compound media, annotations, page sequences and cultural/archival exchange ([specifications](https://iiif.io/api/)).
- **OGC 3D Tiles 1.1** for hierarchical streaming of massive *genuinely spatial* 3D asset sets, with local/world scale metadata ([OGC standard](https://www.ogc.org/standards/3dtiles/)). Do **not** force semantic links into fake physical coordinates.
- **MapLibre/vector tile ecosystems** for real geographic/spatial overlays where basemaps, geometry or vector styling are useful ([MapLibre docs](https://maplibre.org/maplibre-gl-js/docs/)). CoMap's abstract relation graph need not be georeferenced.
- **Existing web video/audio streaming standards and accessible captions/transcripts** for time-based media, with adaptive decoding and explicit consent. A caption or alt-text is a different projection of an authored asset, not a fabricated proof.

Do not build proprietary image/media formats until measured, rights-compliant needs are unmet by these standards. All third-party tiles, fonts and media must pass licensing/privacy/caching review.

## The spaces between: CoInBet is first-class *when warranted*

The gap between two visible objects can hold **an authored/source-registered relation, link history, uncertainty, a disputed inference, a transformation, temporal dependency, contrast, inverse test, null, or a frontier question**. It is not automatically a physical 'subpixel world'. A source-backed relation gets its own ID, provenance, time, privacy, and optional spatial geometry.

Inverse source edge `A --X--> B` does not imply `B --X--> A`. Create candidate `X_inverse?`, qualify separately, and preserve direction. Likewise, **absence of an edge in a snapshot is UNKNOWN**, not proof that a relationship is false. Negative claims require an actual scoped test/witness. A map may show inferred interstices using separate styling and an explicit `HYPOTHESIS` label.

## Evolution and production are separate channels

`DISCOVER / CoLex -> DEDUPE -> LINK -> CRITIQUE -> TEST -> SOURCE-BIND -> AUTHOR/EDIT -> BUILD -> RIGHTS/SECURITY REVIEW -> CANARY -> RECEIVER READBACK -> PRESERVE -> LEARN -> SLEEP/WAKE`

- Many independent workers may search for relevance, broken relations and promising new micro-tile variants, within bounded cost/time and consent. Their outputs are **proposals**.
- One elected, authorized actuator integrates changes with exact source versions, schema compatibility, privacy and rollback. `AUTO_PROPOSE_NE_AUTO_PROMOTE`.
- **CoMicroEvo+** measures a small local candidate delta; **CoProduce+** produces a reproducible asset and quality report; **CoServiceEvo+** measures useful deployment/reader outcomes, not a mere artifact count.
- Independently validate content correctness, render budget, accessible equivalence, contradictions, error cases and anti-capture. Keep accepted and failed experiments to avoid memoryless cycling.
- No perpetual work is assumed merely by this document; persistent evolution requires an actual scheduler/receiver, bounded authorization and durable custody.

## Civ2+ federation

Store manifests and bytes with explicit content hashes, operator/failure-domain identities, replicability and licenses. CoStead may be a local custody cell; cloud/edge CDNs serve public media; independent operators can cold-restore readers. No single registry, host, key, creator account or central agent is indispensable. Preserve anti-tracking and right-to-exit; do not federate consent automatically.

## Implemented R0 and its limits

[CoSysAll+ Semantic Zoom R0 browser example](../../examples/cosysall/semantic-zoom-r0.html) is a standalone offline projection of **56 existing public-registered objects and 61 source-registered edges**, from the earlier [CoMap R0 source](../../ai/comap-source-projection-r0.json). It shows seven bounded semantic levels, four lenses, provenance, registered relation trails, a local two-hop micro-evo proposal, attention budget and non-rendering output surfaces.

Tests: Chromium desktop/mobile, search selection, depth controls, interstitial lens, micro-proposal, accessible list, machine packet, zero canvas drawing in machine-only mode, no JavaScript errors, no outgoing network requests, no horizontal overflow. See [example README](../../examples/cosysall/README.md) and private QA receipt. This is **not** actual IIIF/3D Tiles streaming, an infinite repository, GPU-scale performance, true 3D CoMap, live CoOrb/X2, background ingestion, production CoSysAll, legal canon, or independent hosting survivorship.

**Next falsifiable benchmark:** supply 1 real IIIF image and 1 actual source-registered relation graph as separately versioned tiles; verify one-click discovery, staged region loading, no unnecessary/offscreen requests, rights/consent gating, a nonvisual equivalent, independent reader proof and concrete bytes/latency/energy readings. Keep the current finite source snapshot available during the test.

## 2026-11-07 | D1: CoAll to CoSysAll reciprocal systemic adapter

CoAll contributes stable identities, CoLex/CoIndex semantics, CoTime and provenance, consent/authority ceilings, CoEcoAll+ resource and diversity boundaries, CoEvoDelta change semantics and Civ2+ cell/receiver continuity. CoSysAll contributes receiver-relative rich-media projections, explicit no-render decisions, interstitial/inverse/unknown surfacing, accessibility evidence and micro-evolution *proposals*. Feedback from a map never grants authority to change the source it displays.

**Executable bounded donor:** [CoSysAll reciprocity adapter R0](../../tools/cosysall_reciprocity_r0/README.md) uses the existing CoEvoDelta v0.1 candidate format rather than inventing a controller. On a 3-object/2-edge copied-source synthetic fixture, 17 Python tests passed, including invalid source/edge, private data, authority escalation, time fields and no-render. Actual output `candidate_coevo_delta.json` is `HYPOTHESIS` + `PROPOSE` with `NO_EXTERNAL_EFFECTS__REVIEW_ONLY`. Its 2 original registered relation IDs also exist in the full 56-object/61-edge public source graph; a separately independent full-source execution/receiver ACK has **not** passed.

**Measured reciprocity rail:** `CoAll.source_bound -> CoSysAll.projection -> candidate_feedback -> independently_qualified_CoEvoDelta -> elected_test_or_HOLD`. No automatic promotion, inference of consent, hidden private fetch, session/watchdog creation or product deployment.

**Cross-exemplar opportunity:** [CoVector+ Exemplar Gap Research R0](COVECTOR_EXEMPLAR_GAP_RESEARCH_R0.md) compares this direction against IIIF, 3D Tiles, Wikidata, STAC, W3C PROV, OpenTelemetry and cloud cell/bulkhead designs. Standards already solve large pieces. A novel combination remains only a falsifiable candidate, not a discovery or patentability claim.

**Rails:** `VIEW_FEEDBACK_NE_FACT`, `GRAPH_PROXIMITY_NE_CAUSALITY`, `PROPOSAL_NE_EXECUTION`, `NOVEL_COMBINATION_NE_NOVELTY_PROVEN`.
