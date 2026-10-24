# CoMiddle+ / CoPriMath GlyphRail R0

**State:** PUBLIC_ARCHITECTURE_CANDIDATE__NOT_NATIVE_MOUSE_RUNTIME  
**Observed:** 2026-10-24

## Core decision

The middle mouse button should be a **context summon / relation rail**, not a single overloaded command.

```
MIDDLE CLICK
-> identify context
-> bind object / region / selection
-> summon compact relation rail
-> rank reversible actions
-> expose inverse / else / not / unknown
-> explicit effect only after selection
-> receipt
```

`MIDDLE_NE_SEND`
`MIDDLE_NE_EXECUTE`
`MIDDLE_NE_AUTHORITY`

## Primary semantic question

Middle-click asks:

> What relates here, what is inverse, what is missing, what is next, and what can be safely done?

## First-ring glyph rail

Candidate compact first ring:

- `◎` focus / observer / inspect
- `?` ask / unknown / why
- `>` next / project / continue
- `<` prior / back / source
- `↔` relations / compare / reversible
- `⊂` include / scope / CoIn
- `⊃` outside / containing context / CoOut
- `¬` not / inverse / contradiction candidate
- `±` alternatives / else / trade-off
- `Δ` what changed
- `∞` wider possibility field, bounded execution
- `✓` proven / pass evidence
- `✕` fail / contradiction
- `⏸` held / blocked
- `⟳` evolve / refresh / rerun bounded cycle
- `⚑` flag / remember / highlight
- `⇢` route / receiver candidate
- `⌘` action menu / explicit command
- `⧉` copy / buffer / payload
- `⌁` trail / history / provenance

All glyphs require text fallback and decoder.

## Question rail

Every context may expose:

`WHO | WHAT | WHY | HOW | WHEN | WHERE | WHEREFORE | WHICH | WHITHER | WHENCE`

plus:

`Q&A&@+`

where:

- `Q` = question
- `A` = answer / candidate answer
- `&` = relation / conjunction / dependency
- `@` = receiver / actor / location / context binding
- `+` = expand / alternatives / evolve

## Relation families

The rail should lazily expose families rather than one giant menu.

### Object
- identity
- type
- source
- owner
- currentness
- confidence
- status
- receiver
- recovery

### Relational
- related to
- depends on
- blocks
- contradicts
- supports
- derives from
- supersedes
- duplicates
- complements
- inverse of
- generalizes
- specializes
- dual of
- predicts
- falsifies

### Temporal
- prior
- now
- next
- future
- expired
- forecast
- counterfactual
- backcast
- recovery
- wake condition

### Input / interaction
- select
- preview
- compare
- copy
- buffer
- drag
- attach
- transform
- summarize
- explain
- inspect source
- ask model
- challenge

### Evidence
- source
- proof
- receipt
- confidence
- uncertainty
- dissent
- missing evidence
- stale evidence
- independent witness

### Authority
- allowed
- not allowed
- requires approval
- local-only
- external effect
- privacy-sensitive
- irreversible
- reversible

### Receiver
- route to
- prepare for
- preview for
- send candidate
- ACK state
- adoption state
- follow-up state

### CoEvo
- expand
- invert
- randomize
- counterfactualize
- compare priors
- generate test
- rerun test
- compact
- retire
- wake
- sleep

## Gesture grammar

Candidate physical grammar:

- **middle click**: summon first-ring rail
- **middle hold**: expand relations / nearby context
- **middle double-click**: compare / related-search mode
- **middle drag**: summon receiver / relation trail
- **Ctrl + middle**: deep evidence / provenance
- **Shift + middle**: compare / inverse / alternatives
- **Alt + middle**: prior / history / supersession
- **middle + wheel**: rotate relation family
- **middle + XBUTTON1/2**: previous/next relation family
- **middle on empty space**: ask about context / what is missing
- **middle on selected text/object**: bind payload / relations
- **middle on CoOrb/CoMap node**: relation neighborhood
- **middle on status glyph**: explain meaning / evidence

Exact mapping requires real device qualification.

## Context-sensitive behavior

Same gesture, different context:

- browser text -> explain / source / compare / ask / copy
- file -> hash / preview / relate / route / recover
- image -> inspect / caption / source / related assets
- code -> definition / references / tests / blame / compare
- email -> sender / thread / draft / evidence / receiver state
- CoMap node -> neighbors / inverse / history / next tests
- blank desktop -> CoOrb summon
- taskbar / CoBar -> currentness / blockers / next action
- diagram -> relation / source / alternate rendering
- terminal -> command explanation / safe candidate / history
- VR/spatial -> radial relation rail

## Inverse rail

Every selected relation may expose:

`RELATION -> INVERSE / NOT / ELSE / NULL / OUTSIDE / COUNTERFACTUAL`

Examples:

- `SUPPORTED_BY -> CHALLENGED_BY`
- `DEPENDS_ON -> CAN_SUBSTITUTE`
- `IN_SCOPE -> OUT_OF_SCOPE`
- `VISIBLE -> HIDDEN_BUT_INSPECTABLE`
- `CURRENT -> STALE / PRIOR`
- `SELECTED -> UNSELECTED_ALTERNATIVES`
- `CLAIM -> FALSIFIER`
- `SEND -> PREPARE_ONLY / DO_NOT_SEND`

## CoPriMath / CoGibberTru relation

The rail should project from a typed semantic core, not encode meaning only in visual ornament.

Preferred stack:

```
L0 exact source
-> L1 typed semantic relation
-> L2 CoGibberTru reversible IR
-> L3 glyph rail projection
-> L4 human-readable explanation
```

Every glyph record should preserve:
- semantic id
- meaning
- anti-meanings
- version
- source/provenance
- ASCII fallback
- spoken fallback
- screen-reader label
- cultural/locale scope
- collision set
- decoder
- loss ledger
- authority ceiling
- currentness
- tests

## Scaling to 1000+ relations

Do not render 1000 options.

Use:

`1000+ ADDRESSABLE -> CONTEXT FILTER -> 20 RELEVANT -> 8 FIRST RING -> 1 EXPLICIT EFFECT`

Candidate ranking inputs:
- object type
- foreground app
- pointer position
- selected object
- current work object
- recent action
- receiver
- authority
- privacy
- currentness
- user fluency
- device capability
- evidence state
- human-time saved

## Futures exemplar

The middle rail should be a seed grammar for future devices:

- mouse
- keyboard
- touch
- stylus
- gamepad
- VR controller
- eye-gaze
- voice
- accessibility switch
- future spatial / neural interfaces only with explicit consent

The semantic rail remains stable while physical gestures change.

## Why

This gives:
- high information density;
- low visual clutter;
- one consistent summon gesture;
- context-aware navigation;
- inverse/negative-space thinking;
- fewer manual menus;
- less Rick relay work;
- progressive learning;
- portable semantic grammar across devices.

## Acceptance tests

1. ordinary middle-click remains safe / reversible;
2. first-ring appears in under target latency;
3. same object yields stable semantic ids across renders;
4. glyphs decode to text exactly;
5. inverse relation is available for supported relation classes;
6. color removal does not destroy meaning;
7. keyboard-only equivalent exists;
8. no external effect occurs from summon alone;
9. one user can learn LITE rail without documentation burden;
10. DENSE mode remains opt-in and roundtrip-tested.

## Rails

`GLYPH_NE_AUTHORITY`
`SUMMON_NE_EFFECT`
`POSITION_NE_INTENT`
`ADDRESSABLE_NE_RENDERED`
`DENSE_NE_BETTER`
`INVERSE_NE_NEGATION_TRUTH`
`MIDDLE_NE_SEND`
`MIDDLE_NE_EXECUTE`
`MIDDLE_NE_AUTHORITY`
