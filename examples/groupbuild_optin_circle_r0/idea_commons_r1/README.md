# GroupBuild Idea Commons R1 | Leave a spark. Not a job.

**State:** PUBLIC_SAFE_SOURCE_CANDIDATE__LOCAL_BROWSER_QA__NOT_LIVE_SUBMISSION. This is an additive UX-only experiment in the existing [GroupBuild opt-in draft PR #349](https://github.com/CoCivium/CoCivium/pull/349), preserving the earlier GroupBuild matching and Magic Workshop fixtures. It is not a new hosted service.

## Human promise

The visitor sees one lovely UX direction and can leave a single idea without being recruited into building it.

- **Float:** a small dismissible idea beside an imagined interface, not a live CoFloat service.
- **Sketch:** a different mockup framing an improvement; no product deployment.
- **Circle:** a fictional multi-perspective group exploration; no real members or collective endorsement.

The same idea object has a front-to-back interpretation (visitor vision, improvement, accessible alternatives, voluntary departure) and a back-to-front interpretation (stable local work identity, provenance, privacy, version, permissions, possible future external receiver). They must not silently change meaning or claim operational status during projection.

## Local retention, rights and exit

The HTML works locally without an account, remote service, analytics, tracking or automatic HTTP calls. It has an explicit **Keep on this device** control, a private **Export an unsent file** control, **Forget this local draft**, and a sample prompt. Drafts are at most 500 characters.

A Keep click attempts to write one browser-local draft. It does **not** produce independent backup, CoStead custody, server submission, source-authorized commons membership, or user agreement to volunteer. If storage fails, the UI says so. Export requests a private JSON file, marked `NOT_SENT`. A successful click is **not** receiver delivery or download verification. Nothing grants a commercial IP license. Users should avoid identifying information, especially on shared devices or in children's projects.

If the visitor leaves with an unsaved draft, the idea does not survive. That is a correct and important boundary: `WALK_AWAY_NE_ASSURED_INGESTION`. If the visitor explicitly keeps it locally, the browser may retain it; clearing is the user's choice. A later real commons receiver would need separate consent, licensing, spam protection, moderation, abuse reporting, version lineage, credit choices, public visibility and independent receipt.

## Existing source lineage

- `docs/Architecture/GROUPBUILD_COTEAMING_COPAYBACK_R0_20261101.md`
- `docs/Architecture/COFREE_EVOLVING_PUBLICATION_COMMONS_R0_20261026.md`
- `docs/Architecture/COPUBLICATION_FEDERATION_RECEIVER_INTEREST_R0_20261025.md`
- `docs/UX/COFLEET_RICKBAR_R4.md`
- `docs/Onramp/COCIVIA_FIRST_USE_R0.md`
- `examples/comail_r0/README.md`
- `examples/groupbuild_optin_circle_r0/magic_workshop_r0/`

`rickbar.org` is a possible presentation destination, not a verified or activated website. CoFloat, CoWalkAway, CoIdeaSeed and CoFed remain candidate names and must not silently become CoLex canon.

## Reproduce

`python test_idea_commons.py` runs 30 source-level checks. The optional `node qa_browser_r1.cjs [directory]` needs Puppeteer available in the environment and exercises three viewports, view switching, honest saving, clearing, and no external requests. It writes `BROWSER_QA_R1.json` and three screenshots.

Observed X2-mediated test results on 2026-11-23 UTC: **30/30 Python source tests PASS; 22/22 local Chromium checks PASS** on 390px, 768px and 1440px. One narrow mobile screenshot was visually inspected. No independent first-time user, screen-reader acceptance, production feedback delivery, native CoStead receiver, user consent proof or CoEx is claimed.

## Next real receiver test

Ask one voluntary first-time person to try three alternate UX views, leave a fictional improvement, export and clear it, then explain the difference between local Keep, Export requested and feedback actually received. Compare with a one-page plain text feedback baseline. No real submission endpoint, identity, child profile or external effect should be introduced without separate review.

**Rails:** `FRONT_NE_EFFECT | BACKEND_NE_USEFULNESS | FEEDBACK_NE_MEMBERSHIP | IDEA_NE_LABOUR | KEEP_NE_SHARED | EXPORT_NE_SENT | WALK_AWAY_NE_ASSURED_INGESTION | FEDERATION_NE_AUTOMATIC_LICENSE | PREVIEW_NE_DEPLOYMENT`.
