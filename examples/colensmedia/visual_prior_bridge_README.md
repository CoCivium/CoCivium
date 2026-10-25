# CoVisualFinder+ → CoLens+ living visual bridge R1

**Scope:** one public-source metadata reference becomes an original, bounded source-bound Map / Orb / Text view. This is a portable proof, **not** the original artwork, a source-image reproduction, an independently accepted product, a real X2 CoOrb runtime, or a science claim.

## What's here

- `examples/covisual_finder_r1/sources.json`: one selected **metadata-only excerpt** of the existing four-source public registry. The exact source page/credit/rights wording was chosen from `CoCivium/CoCivium/examples/covisual_finder_r1/sources.json`; other three source records are omitted from this local fixture for narrow QA. The builder selects by source ID and can also consume the complete current four-source registry in a repository checkout, subject to review on any changed source record.
- `examples/colensmedia/template.html`: existing standalone CoLens template baseline from CoCivium's public GitHub.
- `examples/colensmedia/visual_prior_bridge.py`: pure Python metadata-policy guard and deterministic Map/Orb/Text projector. No API/model calls.
- `examples/colensmedia/visual_prior_bridge.json`: machine-readable source-bound output; includes selected record SHA-256, exact source page, credit, conditional CC BY-SA terms, one inverse question, one unknown, projection-loss ledger and zero authority.
- `examples/colensmedia/visual_prior_bridge.html`: standalone HTML with responsive mobile Text default; CSS/SVG constructed from source, no copied media image.
- `examples/colensmedia/tests/test_visual_prior_bridge.py`: 61 Python policy, drift and fail-closed checks.
- `examples/colensmedia/tests/browser_visual_prior_bridge.py`: optional isolated Playwright+Chromium browser regression script. It tests in-memory exact HTML; direct `file://` navigation was not qualified by the prior browser test environment.
- `browser_receipt.json`, `browser_receipt_first_fail.json`, `browser_receipt_second_fail.json`, `policy_tests_final.log`: complete verified local test history, not CI or user acceptance.
- `desktop_visual_bridge.png`, `mobile_visual_bridge.png`: screenshots of the produced **original** UI, not external source images.
- `reconcile_R1.json`: bounded local hashing/custody inventory; verified-local is not CoStead landing, receiver pickup or public deployment.

## Run, offline

From this archive's root:

```sh
python3 -B examples/colensmedia/visual_prior_bridge.py --check
python3 -B -m unittest discover -s examples/colensmedia/tests -p 'test_visual_prior_bridge.py' -v
```

To regenerate the local derivative after approving a source registry change, drop the `--check`; review the output diff before distribution.

Browser QA additionally requires Playwright Python + installed Chromium at `/usr/bin/chromium`:

```sh
python3 -B examples/colensmedia/tests/browser_visual_prior_bridge.py
```

## External source/rights

Original illustration **not included**. Source page:
https://commons.wikimedia.org/wiki/File:Commons_Interwiki_links_with_wikidata_3.svg

Credits on the public source registry: Jarekt (original), Visite fortuitement prolongee (derivative). The item lists CC BY-SA 3.0; this bridge does not itself grant rights to copy or redistribute the artwork. Only the metadata and a newly generated relation layout are shown. Credit and rights state are visible, but a separate item-specific review is still required for an artwork derivative.

CoCivium source donors:
- https://github.com/CoCivium/CoCivium/blob/main/examples/covisual_finder_r1/README.md
- https://github.com/CoCivium/CoCivium/blob/main/examples/covisual_finder_r1/sources.json
- https://github.com/CoCivium/CoCivium/blob/main/examples/colensmedia/README.md
- https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COVISUAL_PRIORS_TO_SPECS_R0_20261025.md

## Exact evaluation scope

**PASS:** 60/61 Python policy and negative tests; 42/42 desktop+mobile isolated Chromium interaction assertions, source-linked identity and conditional rights exposed, zero external script network requests, no image copies, no horizontal overflow. Early failed browser QA receipts retained, including one genuine mobile overflow defect and one test misreading collapsed details.

**HELD:** live X2 input or CoOrbWare install, independent human reader feedback, third-party media derivative rights, first-run direct-file browser navigation, source-image byte verification, GitHub CI for this particular new bridge, public source publication for these new source files, durable CoStead custody and any external broadcast.

**Evolution:** source/rights/receiver/material test changes may justify a new version. No global scan, perpetual worker, infinite-token extension or automatic fanout is claimed. `SOURCE_POINTER_NE_SOURCE_BYTES | MOTIF_NE_LICENSE | VIEW_NE_RECEIVER_ACK | SOURCE_HASH_NE_PRIVACY_CLEARANCE | LOCAL_IS_NOT_LANDED | VALIDATION_IS_NOT_ACCEPTANCE`.
