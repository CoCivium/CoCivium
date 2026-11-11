# CoCivium Proof Gallery R0 | Review-only launch bridge

**CoHereNow:** Source-linked public-safe preview, not a domain deployment, full multimedia release or approved outreach campaign.

## What is in this packet?

- `index.html`: local first-task home with one optional gallery link. A preserved local derivative of the original first-contact R0, not a substitute for GitHub branch readback.
- `proof-gallery.html`: self-contained offline view of nine source-linked public exhibits and their proof limits.
- `proof-gallery.json`: machine twin. Each exhibit carries stable ID, category, source URL, observed Git blob, epistemic type, scope/status, next first-use action and explicit nonclaims.
- `build.py`: deterministic generator with no network activity.
- `tests/`: unit, deliberately bad fixtures, and two-view Chromium interaction checks; `unit.log`, `browser.log`, and structured browser receipts are included.
- `previews/`: desktop and mobile screenshots from the isolated local browser.
- `receipt.json`: scope, hashes, test outcomes and hold gates.

## What changed in the existing review path?

Existing draft GitHub PR **#232** (`CoCivium/CoCivium`) has a separately sourced `proof-gallery.html` and `proof-gallery.json` under `experiments/first-contact-safe-page-r0/`. Its current draft `index.html` has an optional, relative link to the gallery. This does not merge or deploy either page. The GitHub source file is the operational review copy; the local index in this package remains a separately tested local derivative.

No extra domain or scheduler was created. No public-site mutation, DNS change, mail send, third-party contact, provider login, account change, hardware input, local background service or remote execution took place.

## Evidence and limits

- 28/28 deterministic unit/negative tests PASS.
- 38/38 headless Chromium content tests PASS across desktop and mobile, including filters, responsive width, accessibility affordances, disclosure and no observed fetches.
- 14/14 first-task-home link smoke checks PASS across desktop and mobile.
- The browser used an in-memory HTML page rather than navigating a deployed site or a local file URL.
- 43 files across three earlier local artifact roots were SHA-256 hashed with the existing `reconcile-cocivium-custody` script: 9 image candidates, 19 binary candidates and 15 structured/text candidates. Those files were **not semantically reviewed or landed** by this verification. The separate private inventory has exact paths/hashes and is not in the public gallery.
- Source links were read from the connected public GitHub repositories and their observed Git blob SHA-1s saved. Moving `main`/`master` URLs remain moving URLs. A future update must requalify the blob instead of claiming eternal freshness.
- The CoAcademy root license remains unverified. The gallery **links** public files; it copies none of CoAcademy's HTML/JavaScript. The full CC manuscript, private Synthkind artwork and personal correspondence are not published.
- `www.cocivium.org` is a legacy metadata-oriented page and `cocivium.org` returned 404 in a public reader. Privacy cleanup, separate externally verified domain routing, release owner, rollback, rights and independent first-use remain gates.

## First-person, low-noise outreach draft after release gates are met

> CoCivium is open research into making relationships, uncertainty and accountability easier to inspect. We've prepared a small, reversible first-use demonstration plus a source-linked proof gallery. We especially welcome one reproducible usability failure, competing approach, accessibility observation or a question we cannot answer yet. No account or endorsement is needed.

This copy is a **draft**, not an authorized delivery to any recipient. Replace the eventual URL only with one independently qualified, current public entrance. Do not mail contacts en masse, imply their endorsement or claim a reply/read receipt that has not occurred.

## Next decision-proof

One unrelated, consenting person with ordinary browser accessibility attempts the first task, then explains the result uncoached. Record source-bound comprehension, time to useful action, accessibility friction, whether they could undo/cancel and whether the evidence status made sense. In parallel, a qualified owner resolves public-domain exposure, rights and rollback. Then consider release and appropriate individual invitation separately.

`HIGHLIGHT_NE_RELEASE | FILE_NE_RECIPIENT_ACK | SOURCE_NE_RUNTIME | METAPHOR_NE_SCIENCE | CULTURE_HAS_EFFECTS_NE_DIVINE_PROOF | PRIVACY_BEFORE_BROADCAST`