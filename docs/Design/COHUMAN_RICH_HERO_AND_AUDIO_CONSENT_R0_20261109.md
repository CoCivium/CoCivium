# CoHumanSurface+ | CoDry↔CoWet / CoWow+ / CoAudioFkOff+ R0

**Status:** Public-safe design standard candidate, not global canon or a deployed UI. Issued 2026-11-09.

## Default for future human-facing surfaces

Every substantial new human-facing **public, onboarding, explanatory, demo or landing page** should have a meaningful visual hero or deliberately richer primary medium. Legacy pages should be candidates for selective retrofitting by importance, audience and return, not forcibly reworked wholesale. A plain technical document is allowed when that is the best UX.

**Quality gate:** Hero serves comprehension, orientation, invitation or delight. It is not a generic stock image glued onto dry prose.

Choose one of:
1. Original illustrated hero with a meaningful caption and source/evidence relationship.
2. Purpose-built animated/system diagram with a usable static fallback.
3. Interactive map, timeline, constellation or explainer with keyboard and non-interactive equivalents.
4. Short captioned film or experimental audiovisual treatment, with controls.
5. Documented exception: dense technical reference, low bandwidth, privacy/trauma-sensitive context, incompatible accessibility needs or material that benefits from plain text.

CoDry+ = verified source and clarity; CoWet+ = embodiment, invitation, sensory resonance. CoGlam+/CoWow+/CoJaz+ = creative possibilities, not acceptance scores. CoGayAsAPeachBaby+ is an optional expressive direction, never a default audience assumption.

**Inversion:** The richer the surface, the easier it must be to recover the plain, fast, quiet, source-grounded version. Accessibility and speed are part of wow.

## Audio policy: default quiet; scrolling is not consent

**Audio state machine:** `UNASKED_SILENT -> USER_OPTED_IN_MUTED -> USER_ENABLED_AUDIBLE -> USER_MUTED` or `USER_NEVER_AUDIO`. No scrolling, hovering, passive reading, navigation, timer or page load may trigger audible output without an earlier intentional, scoped user action.

- The default is **no audible audio**, not a silent clip secretly scheduled to grow with scrolling.
- A single visible, keyboard-accessible "Enable ambient sound" affordance may grant bounded sound permission for this site or experience. Consent must not be inferred from unrelated clicks.
- After explicit opt-in, a user-selected `scroll-responsive ambient` mode may ramp **gently** from silence to a user-adjustable low ceiling, avoiding spikes, startling cues and volume override. It may also be disabled independently of sound itself.
- **CoAudioFkOff+** is a first-class "Never play ambient audio" preference: immediate mute/stop, visible simple control, persists where consented storage is available, and is respected on subsequent visits. Offer session-only choice and a way to change preferences. Do not ask repeatedly after "never".
- Respect device silent/mute, reduced-motion and saved accessibility preferences; where detectable, offer quieter defaults for assistive technology users, never use hidden inference about disability as a substitute for their preference.
- Foreground/focus visibility, media pause and tab switching should never cause surprise playback. Pause when tab is hidden or on page exit.
- Volume changes must be independent of operating-system master volume; user can always stop, mute or reduce to zero.
- Provide captions/transcripts for information-bearing audio, a static/no-audio route for every necessary action and explicit controls for video.
- No audio on privacy-sensitive, emergency, safety-critical, professional, educational quiet-mode or low-bandwidth surfaces by default. Do not add forced music.

## Suggested design tokens and experiment

- `audio_default=SILENT`; `autoplay_audible=false`; `scroll_enable_requires_explicit_optin=true`.
- `ambient_volume_cap_default=0.10` (fraction of local media element full volume, an initial engineering ceiling **not** a psychoacoustic loudness guarantee); honor lower user choice.
- `ambient_ramp_duration_ms>=3000` after opting in; no sudden jumps, caps or randomized peaks.
- `audio_never_preference` wins over all other page settings.
- `reduced_motion` wins over experimental parallax and excess motion, while keeping the static hero and keyboard controls.
- `hero_kind`, `hero_purpose`, `hero_alt`, `source_ref`, `audience`, `quiet_fallback`, `exception_reason` are required in the per-surface authoring decision.

Compare three variants: (A) static original hero, (B) original interactive or motion hero with quiet fallback, (C) richer consent-based audiovisual treatment. Measure first-30s comprehension, source trust, voluntary engagement, keyboard/accessibility completion, content performance, mute/never-audio rate, and return visits. Avoid measuring raw scroll depth as quality in isolation.

## Promotion and provenance

A human-facing projection references one source-bound CoSeed/CoPath object, and separates visual metaphor from evidence. Public release requires media rights/consent, captions/alt, performance, accessibility, privacy, rollback and exact release receipt. No retroactive public promotion of private prior images or conversations. An existing source without a hero is **NOT_REVIEWED**, not automatically noncompliant or "lost".

## Browser/accessibility constraints

Audible autoplay is frequently restricted unless there was a user gesture; implement a usable no-audio fallback rather than trying to evade browser policies. W3C WCAG 1.4.2 requires a pause/stop or independent volume mechanism when audio automatically plays >3 seconds; the safer design here disallows unrequested audible autoplay altogether. Respect interaction-triggered motion suppression and user controls.

References:
- https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Autoplay
- https://www.w3.org/WAI/WCAG21/Understanding/audio-control
- https://www.w3.org/WAI/WCAG21/Understanding/animation-from-interactions

## Break Glass / nonclaims

Do not publish a media surface without media-source rights, do not infer audio consent from scroll, do not force movement, do not claim this standard is integrated into all frontends, and do not claim subjective delight has been validated without testing.

**CoGlyphRail:** COSEED -> ORIGINAL HERO -> QUIET FALLBACK -> OPTIONAL SOUND -> MEASURE -> VERIFY -> CoEV.
