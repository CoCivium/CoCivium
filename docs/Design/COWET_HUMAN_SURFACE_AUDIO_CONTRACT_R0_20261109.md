# CoWet+ / CoGlam+ Human Surface Contract R0

**Status:** PUBLIC-SAFE DRAFT; NOT CANON, NOT UNIVERSALLY DEPLOYED. **Observed:** 2026-11-09. **WorkID:** `CoAll.CoWet.HumanSurface.20261109`.

## Default for future public human-facing surfaces

At least one **purposeful, content-bound visual focal point** is the default for new human-facing public pages and, where practical, retroactive upgrades of high-value existing human-facing assets. The first viewport must not read as a wall of undifferentiated text. A hero may be a genuine photograph, illustration, typographic artwork, animated infographic, interactive diagram, or short rich-media scene. It must convey the page's purpose, meaning, evidence or navigation, not merely decorate. Support no-image, low-bandwidth, screen-reader, reduced-motion, print, localization and security contexts as equal functional variants.

**Not a mandate for all human surfaces:** safety-critical instructions, forms, assistive/screen-reader-first views, transactional confirmations, constrained terminals and clear-text/API projections may deliberately omit a hero with recorded reason. Nonhuman CoSynthVerse manifests retain machine-first utility without forced eye candy. No historical source should be silently rewritten just to satisfy a new design taste.

## CoDry <-> CoWet <-> CoWow

- **CoDry:** source-bound, concise, searchable, accessible explanation. Retain as a factual fallback and quality reference.
- **CoWet:** purposeful visual orientation, spatial narrative, story and semantic evidence map.
- **CoGlam:** polished hierarchy, typography, contrast, composition, motion where helpful.
- **CoWow:** a memorable interaction or reveal **only if** it strengthens comprehension and user choice; never an unbounded animation tax.
- **CoJaz:** optional temporal/rhythmic interaction, delight with user control.
- **CoGayAsAPeachBaby:** playful, exuberant expressive lane as an opt-in style/theme where context-appropriate, not universal default or an assumption about identity.
- **Inverse/antithesis:** Toggle visual-rich vs source-plain; motion vs still; audio vs silence; poetic vs precise; zoomed storytelling vs complete source graph, with no evidence/permission drift.

## Audio policy: CoAudioFkOff+

**Default SILENT. No scroll-triggered audio without an explicit prior sound-enabling action.** Browsers restrict audible autoplay, and automatic sound interferes with access needs. A visible `Enable ambience` control may activate a soft original/properly licensed soundscape. Scrolling *after* consent can vary a low capped volume/texture gradually. Mouse scroll is not consent.

- Start silent; no `autoplay` with sound, no implicit `AudioContext.resume()` on page navigation or scrolling.
- Provide an immediately discoverable, keyboard-operable `Sound off` action on the same surface, and an independent low-range volume control.
- Respect mute/stop for the active page immediately. If a user opts out, do not nag, auto-reenable, persist sound fingerprints, or retarget them.
- Focus changes, hidden tab, Escape, closing, or long inactivity should suspend or fade sound, with user control to resume. Never route through device microphones or read private preference stores merely to guess taste.
- Respect `prefers-reduced-motion`, `prefers-reduced-data` where applicable, network constraints, audio/cognitive sensitivities and assistive technology interference.
- Speech, captions and vital alerts must not be masked. Audio never sole carrier of information; provide text alternative and signposting. Volume floor 0; low recommended upper bound for ambience, adjustable by explicit user decision.
- Content rights, performance, licensing, and click/keyboard consent must be demonstrated before audio effects. No proprietary music or recordings by implication.

**Standards references:** [W3C WCAG Audio Control](https://www.w3.org/WAI/WCAG21/Understanding/audio-control) and [MDN Autoplay Guide](https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Autoplay). Where sound plays automatically >3 s W3C requires pause/stop or separate volume control; our policy is stronger: never unmute on scroll alone.

## Accept/reject for all new human-facing public surfaces

Required in the design PR:
1. Source WorkID, hero media subject, intended role, alt/caption, source/rights/provenance.
2. Hero improves comprehension or meaningful discovery: demonstrated via a short first-use task or small comparative check.
3. Fully usable without sight, sound, animation, high bandwidth or JavaScript. Provide static/semantic fallback.
4. Explicit sound consent and one-control `CoAudioFkOff`, no surprise unmute, capped optional progression only after enable.
5. Reduced-motion and keyboard/focus/zoom accessibility; tests include a11y/contrast and screenshots at narrow/desktop widths.
6. All claims same evidence spine as machine representations; identify speculative G_dSide/CoAGI as hypotheses, not observational results.
7. Avoid universal template uniformity: vary visual metaphor according to audience and WorkID, not arbitrary novelty. CoTurtle compares meaningful value, cost, energy and distraction.

## Retroactive rule

Prioritize the most frequently seen or strategically important public human pages (CoPre, CoOrb, CoMap/CoNav, CC, CoTheoryAll, onboarding, product demos). Attach a new **presentation projection** to each qualified historic WorkID rather than rewriting frozen witnesses. Preserve exact source, prior variant, and rollback. An existing page without a hero is not retroactively "broken"; it is an eligible improvement candidate.

## Candidate prototype

[CoWet human surface demonstration](../../examples/cowet/cowet-hero-audio-r0.html) is a source-only HTML/SVG/CSS demonstration, with a click-activated original low-volume Web Audio tone, scroll-responsive **only after** user opt-in, and an immediate sound-off button. It is **not** a deployed website, product, cross-session preference service, or proof of user acceptance.

**Next verification:** compare the plain-text source and rich-media projection of one WorkID; measure time-to-first-meaning, comprehension, voluntary return, muted/keyboard completion, media load and distraction. Retain whichever does better for each audience.
