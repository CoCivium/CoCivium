# CoPublication Federation: Six Reader Doorways R0

Status: `SOURCE_PINNED_STATIC_SHADOW_CANARY__NOT_SUBSTACK_POSTED__NOT_REAL_READER_ACCEPTED`  
Date: 2026-10-25  
Source of truth: public `CoCivium/CoCivium` Great ReFact architecture, not a Substack account or this UI.

## First useful action

Open `index.html` locally in a modern browser. Choose **Curious reader**, **Developer**, **Vendor/operator**, **Researcher**, **Journalist**, or **Educator**. Observe that the entry text, suggested action, and strongest counterpoint change, but all six source-bound claim IDs and the pinned source blob stay identical. You can compare two **illustrative local editorial** editions and prepare a challenge without submitting it.

This HTML is a standalone, no-network local prototype. It requires no account, no external scripts, no analytics, and no client-side storage. External Github links only open if the reader explicitly clicks them. The six audience categories are reader-chosen editorial interest modes, not sensitive-trait profiles.

## The measured proof, not the marketing promise

- `59/59` Python source and policy unit tests PASS on the isolated authoring runtime.
- `36/36` Chromium interactions PASS across desktop 1280x840 and mobile 390x844 with zero outgoing network requests, zero JavaScript errors, no horizontal overflow and a local-only feedback record.
- A first test failed because the test URL allowlist incorrectly excluded the Github repository root. That error was corrected in the **test**, not by weakening the app's output permissions. Retained in `history_test_failure.txt`.
- No actual reader completion, email delivery, Substack post, recipient uptake, hosted website route, ads, model inference, device access or source mutation was attempted.
- `10**12` syntactic addresses is a lazy combinatorial **index space** (12 axes with 10 options each). It is **not** a trillion ready articles, useful outcomes, workers, generated tokens, accounts, or independent hypotheses.

## Source lineage and claims

- Architecture source: [`Great ReFact+ R0`](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COGREAT_REFACT_R0_20261025.md), observed blob SHA-1 `9202ab5a8d0bfef509922c8c047363ea7a346ce2`.
- Federation design donor: [`CoPublication Federation + Receiver Interest Fabric R0`](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COPUBLICATION_FEDERATION_RECEIVER_INTEREST_R0_20261025.md), observed blob SHA-1 `8d37873acfe1fbbb949db667ab55647d968f0d8f`.
- Source status is **candidate architecture**, not a verified deployed capability.
- `C01` product-as-capability hypothesis; `C02` preserve source identity and disagreement; `C03` consent and reversibility; `C04` CoOrbWare deployment nonclaim; `C05` native product preserved in first proof; `C06` human benefit unproven until measured.
- Every editorial projection carries exactly `C01..C06`, the same source blob, its own challenge, and a source link. Alternate phrasing is **not** independent evidence.

## CoMarketing 101: one umbrella before ten silos

A small set of **Substack Sections** under one umbrella is a practical initial design; separate publications become candidates only when reader use cases, maintenance/permissions, editorial identity and content volume justify them. Maintain immutable source records and explicit successors off-platform, with exportable material.

Substack product facts checked 2026-10-25 against official pages:

- [Multiple publications per account](https://support.substack.com/hc/en-us/articles/360037824371-Can-I-create-multiple-publications-under-the-same-account): up to ten, depending on account controls.
- [Sections / multiple newsletters](https://support.substack.com/hc/en-us/articles/360060687771-How-can-I-create-multiple-newsletters-or-podcasts-under-one-publication): reader-selectable subsets of a publication.
- [Recommendations](https://support.substack.com/hc/en-us/articles/5036794583828-How-can-I-recommend-other-publications-on-Substack): reader-facing cross-publication discovery.
- [Editing a published post](https://support.substack.com/hc/en-us/articles/360039017132-How-do-I-edit-a-post-that-I-ve-published-on-Substack): web/app changes do not retroactively edit emails already sent.
- [Exporting posts](https://support.substack.com/hc/en-us/articles/360037466012-How-do-I-export-my-posts): export pathway.

These are platform affordances, **not proof that a CoCivium Substack account is connected, that an audience federation is running, or that anyone consented to a mailing list**.

## Reader-evolution contract

`SOURCE -> EDITION -> READER CHOICE -> OPTIONAL, EXPLICIT CHALLENGE -> INDEPENDENT REVIEW -> EDITORIAL DELTA -> VERSIONED SUCCESSOR`.

A page view, scroll, click, open count or inferred trait may not silently mutate the source. A reader can choose `SNAPSHOT`, `LATEST`, or `DIFF` where implemented. Here only two **synthetic** local edition descriptions demonstrate predecessor/successor navigation. Earlier editions remain recoverable. Any actual urgent deadline must be independently true and transparent; deliberately rotting source links or fake scarcity is prohibited.

A valid future full-loop test needs one authorized Substack section or equivalent website, an externally observable reader task, voluntary feedback ingestion, editorial acceptance, a permanent predecessor, a successor change note, independently verified links, and receiver comprehension. Until then, **reader-to-core evolution is designed, not executing**.

## Build / replay

```sh
python3 build.py --check
python3 -m unittest -v test_federation
python3 browser_qa.py
```

Dependencies: Python 3 standard library; browser QA separately requires Python Playwright and a local Chromium executable `/usr/bin/chromium` on the reference Linux runner. Browser QA uses `page.set_content` on the exact compiled source; it is not a live hosted URL acceptance test.

`make_manifest.py` reconstructs `manifest.json` from the fully public source-bound candidate data. `build.py` generates `index.html` deterministically. All committed content is public-safe. The authoring screenshots demonstrate test-run rendering only.

## What an independent receiver must actually prove

One newcomer should successfully choose an interest, identify which part of the article is a proposal rather than an observed effect, recover the same source from two audience views, inspect an earlier version, submit or withhold a challenge knowingly, and explain the offered next action. Time-to-usefulness, comprehension, confusion, source recall, accessibility, opt-outs and repeat value must be measured before expanding the federation.

`TRILLION_CHOICES_NE_TRILLION_JOBS | ONE_SOURCE_MANY_VIEWS_NE_INDEPENDENT_EVIDENCE | SUBSTACK_NE_SOURCE_OF_TRUTH | READ_NE_MUTATION_AUTHORITY | EDITED_WEB_POST_NE_EDITED_EMAIL | FOREFRONT_FADE_NE_HISTORY_DELETION | URGENCY_NE_DECEPTION | VIEWS_NE_MEASURED_BENEFIT | NO_PUBLIC_BLAST_WITHOUT_AUTHORIZED_ROUTE`

FOSS Forever | CoGoAll | Working Together Respectfully.
