# CoImage+ / CoVisualRelationScout R0

**State:** `DRAFT_SCOPED_TRACKED_PUBLIC_IMAGE_CENSUS__NO_AUTONOMOUS_WEB_CRAWL`

## Why it exists

CoOrbWare [OmniMedia priors PR #254](https://github.com/CoCivium/CoCivium/pull/254) has a source/evidence and media-relation contract. The **missing proof** is a real, reproducible inventory of source images and their identities, not another agent ontology. This scout provides a tiny bounded input to that established contract.

Its source scope is **only tracked images in the selected local Git checkout**, not every image in CoCivium history, X2, the NAS, external libraries or prior chat sessions. It never searches the network and never copies or edits source files. Output is JSON on stdout. Only the provided command-line user may redirect output into a file.

```sh
python3 scripts/CoImageRelationScoutR0.py --root . --max-files 100 --max-total-bytes 33554432 > visual_candidates.json
python3 -m unittest discover -s tests -p test_coimage_relation_scout_r0.py -v
```

## From image to possible relation

```text
bounded discovery
  -> tracked source path + exact SHA-256 bytes (subject to caps)
  -> plausible format header, no full media decode
  -> byte-identical duplicate groups (NOT licensing/semantic equivalence)
  -> filename-only suggested topic(s)
  -> hypothetical prior-art, contradiction, inverse/render and accessibility links
  -> RIGHTS / PRIVACY / SEMANTIC REVIEW HOLD
  -> eventual authorized CoMap / CoLens / CoOrb preview for selected receivers
```

All candidates carry license=`UNVERIFIED`, attribution=`UNKNOWN`, privacy=`REVIEW_REQUIRED`, publication=`HOLD` and semantic visual review=`NOT_PERFORMED`. A duplicate SHA does not merge ownership, provenance, consent or possible meanings. Header plausibility is not malware analysis or full safe image decoding. Symlinks are not followed. Truncated discoveries and byte caps are preserved as typed negative knowledge. An image cannot prove a conjectured physical relationship merely by resembling a diagram.

The source version is the observed Git HEAD (if present), each asset preserves the original repo-relative path, and all actual examined bytes get SHA-256 identity. The output does not claim that any outside reviewer or model has interpreted them.

## What Find / Fan / Filter / Route should eventually mean

1. **Find:** scope independent sources according to a named question or receiver need, never indiscriminate enumeration. Possible future official APIs: Openverse image discovery, MediaWiki Commons imageinfo, NASA media catalog and institution-owned datasets.
2. **Fan:** enumerate alternative explanations, historical priors, contrary visuals and accessible projections. Separate empirical images, generated/synthetic renders, diagrams and spiritual/metaphorical interpretation.
3. **Filter:** verify each original landing page, creator, license, rights/restrictions, bystanders/privacy, safety, provenance, original file identity, version/date and public disclosure authority. Openverse itself warns license metadata may be inaccurate, and its API forbids scraping/bulk extraction beyond allowed bounds.
4. **Relate:** attach typed candidate edges to CoSourceGraph, CoMap, CoTheoryAll and CoOrbWare; preserve absent/counterexample branches and derivation losses.
5. **Route:** bounded opt-in receiver subscriptions and preview-first actions. Neither an image search hit nor a mouse gesture authorizes publishing, mailing, copying into a model, redistributing or notifying people.

For thumbnails or actual images, verify dimensions/decode, malicious SVG/script content, alt text, licensing and right-to-use. Avoid exposing unpublished work or private scientific data to remote image recognition systems without appropriate permission.

## Execution and cadence

The CI check runs on changes to this bounded scanner/tests, optionally a single daily read-only census **after merger to the default branch**; GitHub scheduled workflows only execute from the default branch and may be delayed. The workflow has read-only contents permission, does not fetch external media, does not commit output, and no network request is made by the scanner itself. It is not an always-on service.

Proposed **next evidence gate:** choose one actual image from the scoped census, confirm its creator and rights independently, supply an accurate accessible alternative, obtain human visual review, add one dissimilar/prior counterexample and show identical source identity across headless/CoMap/CoOrb views. Do not infer all-session image access from one canary.

## Nonclaims

`CANDIDATE_RELATION_NE_FACT` | `PUBLIC_GIT_FILE_NE_LICENSE` | `SOURCE_HASH_NE_SEMANTIC_REVIEW` | `IMAGE_SIMILARITY_NE_CAUSALITY` | `UNLIKE_NE_IRRELEVANT` | `DISCOVERY_NE_ALL_MEDIA_HISTORY` | `NO_WEB_SCRAPE_DOWNLOAD_OR_FAN_SPRAY` | `NO_MODEL_AGENTS_OR_DEVICE_EVENTS` | `NO_INFINITY_OF_TOKENS_OR_RESOURCES` | `NO_RECEIVER_ACK_OR_RUNTIME`

**Reuse:** [CoLivingHighlight](../../docs/Architecture/COLIVING_HIGHLIGHT_ASSETS_R0.md), [CoThumb/CoPayload](../../docs/Architecture/COTHUMB_COPAYLOAD_R0_20261024.md), [CoOrbWare](../../docs/Architecture/COORBWARE_BEYOND_COSOFTWARE_R0_20261024.md), [CoLens](../../examples/colensmedia/README.md) and [OmniMedia PR #254](https://github.com/CoCivium/CoCivium/pull/254).
