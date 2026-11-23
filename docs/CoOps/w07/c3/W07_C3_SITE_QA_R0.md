# W07-C3-J1 · Three-flagship visitor-readiness QA and delivery reconciliation (R0)

- WorkID: `W07-C3-J1` · worker W07 · session `w07-si-43d985bc720b4b4f` · 2026-11-20
- Scope: **read-only**. Candidates were scanned as local source copies in headless Chrome 153 with axe-core 4.10.3, under the same WCAG 2.0/2.1 A/AA tags and the same 390 / 1365 px viewports as the release-rail audit. All page network was blocked. Raw results: `W07_C3_SITE_QA_R0.json`. Tool: `w07_site_qa.cjs`.
- Independence: this is a different engine run from the candidates' own tests, but it is one Claude-lineage scan. **It is not one of three independent validations.**
- Nothing was written to any site repo, branch, domain or host.

## Bottom line
1. **The candidates are not the blocker.** All 7 current candidate pages pass the automated gate at both viewports: 0 axe A/AA violations, no mobile horizontal overflow, 0 broken internal links or anchors, 0 script errors, exactly one h1, a `main` landmark, a skip link and `lang`. They also read as credible front doors (contact sheets in this folder).
2. **Delivery is the blocker, and for InSeed it is worse than recorded.** The rail's live receipt (CI run 44627872957, 2026-11-19 22:21Z) hashed the live inseed.com apex body as `840db7d9…` (2,053 bytes). W07 searched **all 757 blobs** in a full mirror of CoCivium/InSeed, every ref including pull refs. **No blob matches**, and no blob is 2,053 bytes. The live site is therefore not served from any committed InSeed file, and its serving origin is **UNKNOWN**. Merging or promoting an InSeed candidate is not shown to change what visitors see.
3. The InSeed repo's own `main` page (it carries `CNAME inseed.com`) is not visitor-ready. It shows "We are now alive to all share — ⊂EvoAll+" and a "[ I AM IN — a+++ > all etc ]" button, and fails axe `html-has-lang`, `landmark-one-main` and `region`. It also does not match the live body.

## Per site
| Site | Candidate scanned (exact source) | Automated gate | Live state (from rail receipt; W07 could not reach the domains directly) | Delivery blocker |
|---|---|---|---|---|
| **CoCivium** | `home-r1` blob `ce97f53e` @ rail `37ef1317`; first-contact `index.html` and `proof-gallery.html` @ `84d435eb` | PASS ×3 pages | apex **404**; www serves a 91 KB technical index flagged for a Windows path and "not public hosted" claims | (a) **Two competing front doors**: home-r1 ("Better decisions through cooperative intelligence") and first-contact ("Start with one useful thing"). One must be elected. (b) www needs the owner's private review before anything replaces it. (c) apex hosting is not configured. |
| **InSeed** | `contrast-stable` `index.html` @ `d732424` (same visible text as PR1 `dc03e88`, with contrast fixes) | PASS | apex 200, 2,053 B, **not from this repo** (see above); www 301 | The owner must identify the actual host behind inseed.com (DNS/hosting), plus the still-unresolved hourly writer workflows on `main`. |
| **CoPolitic** | `contrast-stable` `index.html` @ `6e7efc0` | PASS | apex **404**; www network/TLS unavailable | The repo's `main` has only a README and no `CNAME`, so no hosting is configured. |

## Fixes the site writers could take (proposals; not applied by W07)
- **CoCivium:** elect one front door. If it's first-contact, replace the eyebrow "EVO ALL BETTERS +" with plain language. It is the first text a visitor reads and it means nothing to them.
- **InSeed:** the "Back to top" link is 75×23 px. Give it `min-height: 24px` (or padding) so it clears WCAG 2.2 target size without relying on the spacing exception.
- **CoPolitic:** the three nav links ("Begin", "From meme to institution", "Evidence and limits") are 23 px tall. Apply the same 1 px fix.
- **All three:** the pages pass with JavaScript-free reading. Keep the strict CSP that first-contact already uses (`script-src 'self'`). W07 had to bypass it only to inject the axe scanner, in a separate context; the page itself logged no errors.

## Not shown by this job
- Live-site behaviour, TLS, headers, real browsers or devices, screen-reader use, and human comprehension.
- Who controls DNS and hosting for any domain.
- Whether www.cocivium.org's technical index exposes anything sensitive. W07 did not fetch it.

## Next gates (owner-held)
1. **InSeed:** identify the real serving origin for inseed.com, then decide whether the repo becomes the source of truth.
2. **CoCivium:** elect the front door; privately review www; configure the apex.
3. **CoPolitic:** configure hosting for the elected candidate.
4. Get a genuinely independent reviewer (non-Claude) to rerun `w07_site_qa.cjs` or the rail audit against these exact commits.

## C3-J2 delta (2026-11-23; `W07_C3_J2_DELTA_QA_R0.json`)
- **InSeed `main` changed** at `d4f63d0` (Nov 21) to a human-first front door, which passes the automated gate. Its bytes still differ from the live apex hash recorded Nov 19, and the rail has no newer live receipt, so **what visitors see now is UNOBSERVED.**
- **The InSeed writer hazard is closed in source.** Both legacy workflows are manual-dispatch only and read-only, and both PowerShell loops fail on start. Residual: a copy already running on a local machine isn't stopped by a repo change.
- **CoPolitic** now has a clean minimal public branch (`f0feadd`) targeting the GitHub Pages fallback `cocivium.github.io/CoPolitic-site/`, with copolitic.org declared not bound. It passes the gate. Nit: the review branch's `ia.html` has no skip link. The fallback URL is not reachable from this session.
- **Identity collision:** rail commits `86cfa84a`/`ff0f5612` publish their own "W07" fenced-actuator work. They are not this session's output, and they are not a landing of this branch.
