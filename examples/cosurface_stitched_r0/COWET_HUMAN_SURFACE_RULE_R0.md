# CoWet+ / CoDry+ / CoGlam+ / CoJazz+ | Human Surface R0

**Status:** proposed cross-surface UX rule and experimental example, public-source candidate only. No production design acceptance, autoplay permission or future-surface installation claimed.

## Default rule: CoWet First, CoDry Available
For **new human-facing landing, presentation, documentation overview, explainer and onboarding surfaces**, include **at least one intentional hero visual or meaningful rich-media element** unless there is an explicit documented reason not to. For legacy/retro surfaces, upgrade by impact and preservation risk, with an exact original snapshot and a rollback path. A visual may be an accessible SVG, image, animation, video, interactive graph or sonification. Decorative wallpaper is not sufficient: the visual should explain, orient, delight or make progress legible.

This is a design-review policy, **not** a rule that makes every short utility screen, legal notice, emergency page, screen-reader experience or low-bandwidth surface load media. Exceptions are affirmative, explainable and revisable. Prefer a real task outcome over cinematic clutter.

## Complementary modes, not enemies
- **CoDry+:** fast, quiet, readable, printable, semantic HTML, good on poor connections, no animation or audio; always available.
- **CoWet+:** purposeful media, interactive relationships, visual pacing, texture and delight without hiding truth.
- **CoGlam+ / CoWow+:** memorable reveal that earns its space; before/after legibility and measured comprehension.
- **CoJaz+:** controlled variation, responsive improvisation, distinctive artistic direction and bounded novelty, not random churn.
- **CoGayAsAPeachBaby+:** joyful permission for irreverence, color, camp and optional personality. Never an imposed identity or inaccessible animated distraction.
- **CoAudioFkOff+:** immediate user-owned permanent-on-this-surface silence, not a tiny mute button hidden after the noise starts.

## Audio policy
1. **Hard-silent default.** Scrolling, moving, hovering or loading never initiates audible media. No media or Web Audio node starts audibly without a clear user gesture. A silent video/hero can play if it respects motion and data preferences.
2. **Opt-in once per appropriate consent scope**, e.g. `Enable ambience`. After a user-initiated start, gently fade into a modest background level; scroll progression may modulate an already-user-enabled ambience, capped with a global independent volume control.
3. **CoAudioFkOff+:** visible one-action `Silence` stop, predictable keyboard control, no reactivation after opting out; honor the preference for that surface. Per-device/global persistence needs an explicit authorized storage/design contract; prototype uses localStorage with fallback, not cross-provider sync.
4. **Respect `prefers-reduced-motion`, `prefers-reduced-data` when available, `visibilitychange`, offline and device constraints.** No audio under screen reader interference or unclear consent. Preserve captions/transcripts for substantive audio.
5. **No volume tricks:** fade-in cannot exceed user-set cap; quiet content remains quiet. No sudden peaks on scroll, return from tab or route transition. Audio must never be necessary to complete a task.
6. **Browser reality:** audible autoplay and Web Audio may be blocked until user activation; handle failures visibly. W3C WCAG 1.4.2 requires a stop/pause or independent volume control for autoplay longer than 3 seconds, but stronger opt-in is chosen here.

## CoHero proof contract
- Hero communicates actual current capability and accurately labels demos as demos.
- Alt text / accessible label, high-contrast readable text, keyboard reachability and static reduced-motion rendition.
- Distinctiveness must serve comprehension: unique provenance, source link and a useful primary action, plus an easy CoDry view.
- Resource budget, graceful still-image fallback, responsive layout, no dependency on remote video or trackers.
- Three experiments per surface type: (A) dry baseline, (B) visual hero without audio, (C) visual hero with **voluntary** audio. Measure task completion, comprehension, comprehension of uncertainty, time to useful action, annoyance/opt-out, privacy, and performance.
- **CoEvo+:** compare audience-specific surf variants, keep the winners and the exceptions, do not claim all futures will want the same visual or sound.

## Human/AI substrate alignment
`CoSource → CoSeed/CoPath → human hero + CoDry accessible view → measured comprehension → CoEcho → source challenge`.
Visual and acoustic projections can differ dramatically from machine structured artifacts; share provenance and meaning, not byte identity.

## Current demo
[CoWet/CoDry experimental static HTML prototype](cowet_hero_audio_r0.html).
It contains an embedded original SVG hero and an intentionally gentle opt-in Web Audio generative drone. No copyrighted recording or remote asset needed.

## Existing evidence and limits
- MDN autoplay guide: https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Autoplay
- WCAG 1.4.2: https://www.w3.org/WAI/WCAG21/Understanding/audio-control
- Existing [public source index](COPRE_SHAREABLE_ASSET_INDEX_R0.md), [CoOmniPath](co_omnipath_r0.py) and [CoMutualValue](CO_MUTUAL_VALUE_AI_HONEY_R0.md).

**Nonclaims:** Prototype not deployed to CoCivium.org, InSeed, CoStead or X2. Browser/device acceptance and real user delight not yet benchmarked. No cross-session consent synchronization.
