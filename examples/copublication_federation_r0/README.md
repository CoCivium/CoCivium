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


## CoEdgeIn R0.1 | The first real-publication bridge (October 25, 2026)

This page now explicitly links **two different publication states**. The public RickPublic article [Does AI Make the Stock Market Obsolete (and Without Even Cheating)?](https://rickpublic.substack.com/p/does-ai-make-the-stock-market-obsolete) is an existing July 20, 2026 publication, independently checked as publicly readable. It is **not** a Great ReFact chapter and this prototype did not publish it. The companion [Great ReFact opening chapter](https://github.com/CoCivium/CoCivium/blob/1487b330d35ddec03f32000e6846dd3b35ed774a/docs/books/great-refact-r0/01-your-product-is-still-here.md) is an unmerged, source-controlled working draft (verified blob SHA-1: `21bb508b5b0fe9e34011590539993e14d4325edc`), **not** a Substack article.

For the one-reader canary: compare a narrow shared question about dependence on interconnected AI/product systems, identify a serious alternative explanation, and say what observation would change your view. A reader may choose to leave without submitting anything. The optional local challenge composer does not transmit data. Clicking an external link intentionally opens the destination site under that site's own privacy terms.

The manifest's `actual_substack_posts_created: 0` records **posts created by this preview**, not whether RickPublic has historically published posts. The six routes still use only source-bound GitHub action URLs. The additional RickPublic URL is one explicitly verified, fixed editorial outbound link, not a broad exception allowing arbitrary third-party destinations.

**Still HELD:** public deployment of this HTML; independently observed third-party reading/feedback, new Substack posts, subscriber activity, recipient acceptance, X2 native interaction, and cross-account shared execution. No subscriber count, open-rate lift, conversion or viral effect is inferred from the public permalink.

## CoEdgeIn R0.2 | Real clean-runner desktop/mobile QA (October 25, 2026)

The existing reader page now offers a first-screen link to compare one **actual published RickPublic article** with one **unmerged pinned Great ReFact chapter draft**. They remain separate evidence classes. No Substack account, email, author identity, subscriptions or recipients were changed.

**[GitHub Actions #40243859275](https://github.com/CoCivium/CoCivium/actions/runs/40243859275) SUCCESS:** 64/64 static/source/negative-case tests and 54/54 browser checks on a clean runner. [Runner visual receipt](https://github.com/CoCivium/CoCivium/actions/runs/40243859275): full-height screenshots on 1280-pixel desktop and 390-pixel mobile; zero JS errors and zero outbound requests during tested clicks. The mobile screenshot is exactly 390 pixels wide, not wider than its viewport.

**Historical failures remain preserved:** the CI YAML originally had duplicate root-level `permissions` keys that prevented normal workflow discovery. After repair, [the first Chromium run #40243637913](https://github.com/CoCivium/CoCivium/actions/runs/40243637913) failed the `mobile_no_horizontal_overflow` assertion; its screenshot was 469 pixels wide for a 390-pixel viewport. The new source digest in a comparison card was not breaking. Panel `overflow-wrap:anywhere` corrected the layout; the browser script now emits offender diagnostics on recurrence. Neither the earlier failure nor the successful fix should be erased from the evidence history.

**HELD independently of CI:** the page is not confirmed hosted as a public CoCivium reader destination, no invited or unfamiliar recipient has independently completed the proposed task, no subscriber metrics were measured, and no outgoing publication or social-message delivery was attempted. A zero-network local test does not prove a public click-through or recipient acknowledgment.

## CoGiggle+ | Humor that points back to evidence (R0 candidate)

The source-controlled federation now includes an **explicitly opt-in humorous explanation lens** for each of its six existing reader-chosen routes. It is deliberately **not a seventh audience, an inferred personality segment, a hidden recommendation engine, a new publication, or a permission to send anything**.

The original CoCivium [CoLoL+](../../docs/Evolution/EVO_ALL_BETTERS_EVERGREEN_PULSE_20261023.md) premise is *layers, laughs, love, learning*. CoPlay+/CoSatire+ and [AI Wars satire](../../docs/Outreach/AI_WARS_YOU_WERE_NEVER_SUPPOSED_TO_BE_THE_OPERATING_SYSTEM_R1.md) already demonstrate clearly labeled fictional illustration. CoGiggle+ is a narrowly defined **reader-facing projection**: one humorous line, one serious plain-language meaning, one CoTurtle counterpoint, and an exact original claim ID per route.

**Source model:** `make_manifest.py -> manifest.json (giggle_lens) -> build.py -> index.html`. An exact-manifest reproduction check is run in CI to prevent the authoring script, source data and displayed joke from quietly diverging. The original evidence kernel `C01..C06`, source blob SHA-1, old/current synthetic edition controls and first-reader links remain intact.

**Reader behavior:** the lens begins hidden, becomes visible only when a reader activates **Try the humorous lens**, follows a separately selected reader route, and returns to plain explanation on the second click. No cookie, account, browser storage, network request, analytic event, fabricated testimonial, scarcity timer or automatic transmission is introduced.

**CoTurtle guardrails:** `HUMOROUS_NE_OBSERVED | PUNCHLINE_NE_PERFORMANCE_METRIC | MEME_NE_MODEL | FUNNY_NE_TRUE | OPT_IN_TO_READ_NE_OPT_IN_TO_SEND | JOKE_NE_ENDORSEMENT | FICTIONAL_CHARACTER_NE_REAL_TESTIMONIAL`. The joke may explain the proposed behavior, but cannot replace a source, promise actual time saved, or confer execution authority.

**Acceptance limits:** source tests and controlled Chromium browser tests may demonstrate coherent UI, accessibility controls, fixed claim identity and zero network effects. They cannot prove laughter, reader enjoyment, comprehension, viral reach, Substack publication or independent adoption. To make such a claim, conduct a consent-based comparison between the plain and humor versions with independent participants, an unchanged question, source comprehension, optional exit and actual measured time/helpfulness.
