# Watershed Explorer R0A — Synthetic Dry Run / Adversarial Review

**State:** `SYNTHETIC_DRY_RUN_ONLY__NO_REAL_LEARNER_VALIDATION`

## Why this exists

R0 passed packaging CI. That proves the files and declared rails exist.

It does **not** prove that a class can actually use the lesson.

R0A therefore performs a synthetic role-play across the lesson and deliberately injects common failures before involving real learners.

## Dry-run scenarios

1. Baseline with no VR.
2. VR fleet unavailable.
3. Internet unavailable.
4. Learner reports motion discomfort.
5. Learner declines/cannot use a headset.
6. Learner overclaims causality.
7. Learner confuses a tray observation with the real watershed.
8. Water spill near electronics.
9. Official source unavailable/changed.
10. Twenty-minute schedule loss.

These are fixtures, not predictions of what children will do.

## Defects found

### D01 — Observation class too coarse

R0 distinguishes observation from inference but does not consistently distinguish:

- observation **of the model**;
- observation **of the real world**.

This can accidentally turn a tray result into a claim about Oakville.

**Correction:**

`MODEL_OBSERVATION_NE_WORLD_OBSERVATION`

Learner/facilitator language should use:

- MODEL_OBSERVATION;
- WORLD_OBSERVATION;
- SOURCE_STATEMENT;
- INFERENCE.

### D02 — Experimental repeatability underspecified

R0 says to use approximately the same water amount/rate, but does not require simple measurement.

For a learning activity about evidence, that is unnecessarily mushy.

**Correction:**

Add:

- marked measuring cup/syringe/bottle;
- timer;
- same nominal volume;
- same nominal pour interval;
- optional repeated trials;
- record departures from the planned procedure.

This still does not turn the tray into a calibrated hydrology experiment.

### D03 — Network failure path implicit, not explicit

The lesson can conceptually run offline, but the source-challenge phase could fail if the facilitator relies on live webpages.

**Correction:**

Require a dated printed/PDF/local source extract or facilitator-prepared source card before session start.

### D04 — Safety stop precedence should be explicit

R0 says stop for discomfort/spills, but the control priority should be machine-readable.

**Correction:**

`SAFETY_STOP_OVERRIDES_LESSON_COMPLETION`

### D05 — Time-compressed path absent

A school session routinely loses time for announcements, late transitions, fire drills and humanity's general relationship with clocks.

**Correction:**

Define a 45-minute minimum path. Drop immersive visualization and optional discussion before dropping:

- precommitted prediction;
- observation classification;
- source challenge;
- revised explanation;
- uncertainty.

### D06 — Accessible path must remain educationally equivalent

R0 requires a non-headset path, but future implementations could quietly turn it into inferior busywork.

**Correction:**

`NON_HEADSET_PATH_MUST_PRESERVE_CORE_OBJECTIVE`

## Result

The module remains a viable public StrawBe+ candidate after these corrections.

It is **not** educationally validated.

Next evidence gate:

```text
synthetic dry run
-> educator adversarial review
-> revise
-> tiny real pilot
-> aggregate before/after evidence
-> revision
```

## Nonclaims

- No child participated in this dry run.
- No teacher approved the module.
- No curriculum authority certified it.
- No measured learning gain is claimed.
- Passing the dry-run canary does not prove classroom effectiveness.
