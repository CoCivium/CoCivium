# CoWet+ / CoDry+ / CoGlam+ | Human-facing hero and consensual atmosphere R0

**Status:** PUBLIC-SAFE CANDIDATE AND OFFLINE EXPERIMENT. Not approved universal canon or deployed site behaviour. **Date:** 2026-11-09.

## Default rule, prospectively and retroactively
For every **new major human-facing entry surface**, offer a meaningful hero image, diagram, animated demonstration or interactive visual, **plus** a useful readable title, subtitle and next action. For high-value retrospective pages, backfill a semantic hero when rights and source fit permit. Explicit exceptions: utilitarian dashboards, urgent/safety tasks, low-bandwidth/assistive screens, privacy-sensitive contexts, or cases where visuals add no comprehension. A merely decorative placeholder **fails** the spirit of the rule. Do not gate release on an unavailable image: use an explanatory accessible SVG/diagram and log media debt.

## The inverted design vocabulary
- **CoDry+**: source/evidence/plain-text legibility, stability, fast loading and exports. Not inherently bad.
- **CoWet+**: sensory richness and exploration in service of comprehension. Not inherently good.
- **CoGlam+/CoWow+**: emotional invitation, delight, memorability and distinctive graphic identity. Measured, never deception.
- **CoJaz+**: rhythms, surprising but legible transitions, optional sound/animation; silence is a valid arrangement.
- **CoBeAxaKitten+**: playful curiosity and friendly challenge, suitable for children with accessible equivalents.
- **CoAudioFkOff+**: global, clear, reversible and durable mute, without nagging or repeated consent prompts.

**Inverse question:** What is the most useful thing the page can explain *without* the media? If nothing, media might be hiding a weak product. Conversely: which text-only page becomes meaningfully clearer with a visual?

## Sound is strictly opt-in
1. On first visit: **silence by default**. Neither scroll nor time nor focus nor hover may initiate sound. An auto-playing zero-volume WebAudio oscillator is not necessary.
2. Provide **Enable atmosphere** as an unambiguous user action and show **Audio off** within easy reach whenever sound is active.
3. After opt-in only, scroll may gently modulate volume toward a low user-adjustable ceiling; no sudden peaks. Respect browser autoplay restrictions.
4. Mute means silence and no automatic re-enabling, including on future pages, until an explicit user action changes the preference. Prefer local preference storage without a profiling cookie; if storage is unavailable, fail silent.
5. If reduced motion, data saver, unavailable audio APIs, audio already in use elsewhere, accessibility constraints or user preference conflicts, preserve visual/text experience with sound off; do not infer an individual's disability or sensitivity.
6. Respect prefers-reduced-motion and do not bind animation to scrolling where it causes vestibular discomfort. Provide captions, descriptions, transcripts and keyboard controls for meaningful media. Do not let ambient music mask speech readers.
7. Every page remains usable offline, without audio, without JavaScript, and without a graphic when CSS/image rendering is unavailable.
8. Public-source content and software must have media rights/provenance. Original ambient synthesis is a demo only, not a universal soundtrack. Never capture mic or transmit listening behaviour.

## Admission gates
- Hero's alt/accessibility twin conveys its meaning; decorative only if plainly decorative.
- First-use silent playback test and scroll-without-consent silent test.
- Explicit click-to-enable and single-click mute, keyboard operated.
- Muted preference survives reload in tested local browser; falls back silent when storage blocked.
- No sound API invocation before consent.
- Reduced-motion path, high-contrast and small-screen checks; no flashing or intrusive motion.
- With JS disabled, visible hero and content remain readable.
- Measure comprehension, time-to-value and voluntary return; clicks or spectacle alone are not evidence of benefit.

## Experimental source
`examples/cowet_r0/index.html` is an offline single-file demonstration of a meaningful hero, silent-first consent gating, optional original audio ambience and a persistent no-audio preference. It is **not** deployed to CoCivium.org or InSeed.com.

## Relations
Reuse: `docs/Architecture/COBOOK_LIVING_RICH_MEDIA_SYSTEM_R0_20261025.md` and `docs/Architecture/COPUBLIC_SURFACE_OBSERVER_R0_20261025.md`. Source-bound results should be available as CoSeed/CoPath/CoMap projections; avoid claiming every historical front is already rebuilt.

**Nonclaims:** NO_ALWAYS_ON_AUDIO, NO_UNIVERSAL_HERO_LAUNCH_GATE, NO_INDEPENDENT_ACCESSIBILITY_AUDIT, NO_PUBLIC_SITE_DEPLOYMENT, NO_CROSS_SESSION_SYNC.
