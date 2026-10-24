# CoDoodle Intake R0 | from free-form ideas to reviewable experiment candidates

**State:** `TESTED_LOCAL_SYNTHETIC__NO_RUNTIME_OR_DEVICE_INPUT`. Public-safe zero-dependency Python 3 prototype. Not a replacement for CoExperimentSpace+, CoExperimentSelector+, CoThumb+, CoInterstice+, CoTurtle+ or CoResearchGate+.

## Purpose

Route a voluntarily submitted, bounded CoDoodle text into at most seven source-linked experiment proposals. No model, service, mouse, keyboard, provider account, clipboard, browser, filesystem crawler or network endpoint is accessed by the classifier. Input files are passed explicitly. The program prints JSON to stdout only. It neither launches tests nor estimates metrics. Raw text is **not** included in preview output: only its SHA-256 and size are retained, plus limited category hints.

The current categories are input, media, visual, inversion, recovery, provider and historical replay. Match quality is intentionally simple and **keyword-based**: collisions, missed paraphrases and false positives are expected. Sensitive-context words trigger a fail-closed hold; this is not a security-grade secret detector, and users should avoid giving the tool secrets.

## Run

```sh
python3 -m unittest discover -s experiments/codoodle-intake-r0 -p 'test_codoodle.py' -v
python3 experiments/codoodle-intake-r0/codoodle.py --input experiments/codoodle-intake-r0/fixture.json
```

Input JSON fields: `schema` must be `CoDoodle.Intake.R0`, `raw_doodle` a nonempty UTF-8 string up to 65,536 encoded bytes, `opt_in_local_review` an explicit boolean and `scope` `PUBLIC_SYNTHETIC` or `PRIVATE_LOCAL`. No raw local input is written to GitHub by the program.

## Integration contract

`raw voluntary input -> SHA256 source binding -> keyword-only candidate hints -> named prior document -> reviewable negative control -> CoExperimentSelector+ only after evidence-linked metrics -> static validation -> one bounded micro-canary -> receiver-value check -> receipt`.

The prototype does not create a `CoExperimentSelectorInputR0` envelope because the selector correctly **requires explicit evidence references for each benefit and penalty estimate**. Populating those numbers with invented scores would defeat the existing gate. No candidate is selected or executed, no model credentials are used, and no device hook is installed.

## Verified source snapshot

Local Linux Python 3 suite: **13/13 tests PASS** on 2026-10-24, covering opt-in, input size, no raw echo, negative sensitive contexts, no hidden effects, deterministic output, bounded logical scale and status honesty. Fixture yields seven candidate categories. This is local test evidence, **not** live X2, native Windows, human comprehension or provider adapter proof.

## Next useful test

1. Compare the seven cards with the user's intended meanings, record false and missing classifications.
2. Ask one consenting unfamiliar person to pick one useful card in under one minute, with a keyboard-accessible, cancellable surface. No account required.
3. Pin evidence-linked metrics for just one card and pass it to existing CoExperimentSelector+.
4. Run a single read-only micro-canary, comparing usefulness and human time against the original no-bridge workflow.

Symbols and spiritual, speculative, nonphysical and G_d/Planck imagery can be represented as labeled *perspectives/hypotheses*, not empirical proof or authority. Unlimited logical descriptors do not create unlimited resources or tokens. No automatic broadcast or stealth input capture.

`DOODLE_NE_INTENT` | `KEYWORD_HINT_NE_VERIFIED_TASK` | `RANDOMNESS_NE_VALUE` | `PREVIEW_NE_EXECUTION` | `POINTER_NE_ACK` | `X2_OFFLINE_NE_ALL_DEVICES_OFFLINE`.