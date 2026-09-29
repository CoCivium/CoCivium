# CoProjectionCI R0

**State:** `CANDIDATE__PUBLIC_RND__NOT_CANON__NOT_RUNTIME_ENFORCEMENT`

## Purpose

CoProjectionCI R0 defines a bounded acceptance contract for public-facing CoCivium projections such as README pages, websites, outreach copy, demo landing pages, research summaries, and contributor on-ramps.

The goal is simple: a public projection should be understandable, current enough for its claims, honest about uncertainty, and able to route important statements back to evidence.

This is a projection-quality contract, not a claim that one wording or one audience view is canonical.

## Core checks

A candidate projection SHOULD fail promotion when any required check below fails.

### Identity

A cold receiver should be able to answer, in one sentence:

> What is this?

### Status

A receiver should be able to distinguish material states such as:

- working / observed;
- experimental / candidate;
- speculative / story;
- unknown / unresolved.

`STATUS_LABEL_NE_PROOF`

### Purpose

The page should make clear why it exists and what kind of surface it is.

### Next action

A receiver should have an obvious next step appropriate to the surface.

### Jargon

No unexplained CoTerm should be required for first-screen comprehension.

Candidate baseline:

`UNEXPLAINED_COTERMS_ABOVE_FOLD <= 1`

### Claims

Speculative, aspirational, mythic, or future-facing language must not silently render as observed fact.

Candidate baseline:

`UNQUALIFIED_SPECULATIVE_CLAIMS = 0`

### Currentness

Status-bearing claims should have either:

- a currentness source;
- a last-verified marker;
- or an invalidation / expiry rule.

`STALE_STATUS_CLAIM_NE_CURRENT_FACT`

### Provenance

Major claims should have a path back to source, evidence, receipt, or clearly marked argument.

Candidate baseline:

`MISSING_PROVENANCE_FOR_MAJOR_CLAIM = 0`

### Receiver-category preservation

A receiver paraphrase should preserve the intended category closely enough to avoid material misunderstanding.

Example:

- intended: "experimental human/AI coordination environment"
- materially drifted: "recruiting company"

A mismatch is a projection-loss signal.

### Depth ordering

Philosophy, theory, story, and futures may deepen a public page, but should not obstruct first-pass orientation.

Suggested order:

`GLANCE -> ORIENT -> VERIFY -> EXPLORE -> THEORY -> PHILOSOPHY -> STORY/FUTURES`

## CoProjectionContract+

Each compiled or hand-authored public projection SHOULD declare, explicitly or by machine-readable sidecar:

- source objects;
- target audience;
- allowed compression;
- required nonclaims;
- currentness window;
- provenance requirements;
- render style;
- maximum complexity;
- call to action;
- invalidation conditions.

`SAME_SOURCE_NE_SAME_COPY`

`COMPRESSION_NE_DISTORTION`

`PROJECTION_STYLE_NE_TRUTH_STATUS`

## CoProjectionDiff+

Reviewable public changes SHOULD answer:

1. What changed?
2. Why?
3. Which source objects changed?
4. What receiver interpretation is expected to improve?
5. Which old wording became stale or invalid?

## CoReceiverParaphraseTest+

Human or synth receiver-canary evidence may be attached to a candidate projection.

Useful fields:

- receiver class;
- first-pass paraphrase;
- intended category;
- observed category;
- confusion points;
- next-action understood;
- claim-status understood;
- optional qualitative note.

This is evidence, not ground truth. Different receivers may reasonably interpret a projection differently.

## Candidate machine-checkable thresholds

These are starting thresholds, not permanent doctrine.

```text
FIRST_SCREEN_IDENTITY = PASS
OBVIOUS_NEXT_ACTION = PASS
UNEXPLAINED_COTERMS_ABOVE_FOLD <= 1
UNQUALIFIED_SPECULATIVE_CLAIMS = 0
STALE_STATUS_CLAIMS = 0
MISSING_PROVENANCE_FOR_MAJOR_CLAIM = 0
```

Some checks require heuristics or receiver evidence and therefore SHOULD NOT be represented as stronger than the evidence allows.

## Promotion loop

```text
semantic source
  -> projection compiler / authoring
  -> projection contract
  -> static checks
  -> claim-status checks
  -> receiver canary
  -> paraphrase / comprehension evidence
  -> projection diff
  -> promote or revise
```

## Initial target surfaces

- root README;
- CoCivium.org front door;
- public demo landing pages;
- outreach messages;
- contributor onboarding;
- research summaries;
- CoCivia / story projections.

## Rails

`PROJECTION_NE_CANON`

`README_NE_SOURCE_OF_TRUTH`

`SITE_NE_SOURCE_OF_TRUTH`

`RECEIVER_PARAPHRASE_NE_AUTHOR_INTENT`

`RECEIVER_CONFUSION_NE_RECEIVER_FAILURE`

`COMPREHENSION_NE_AGREEMENT`

`POPULARITY_NE_CLARITY`

`PUBLIC_COPY_NE_RUNTIME_STATE`

`CI_PASS_NE_SAFE_FOR_ALL_RECEIVERS`

## R0 non-goals

R0 does not:

- automatically publish or merge public copy;
- assert that a language model can perfectly judge comprehension;
- replace human receiver canaries;
- define a universal readability score;
- promote any current README wording to canon;
- establish runtime authority.

## Next

Implement minimal deterministic checks against a small fixture corpus, then compare them with real receiver-canary evidence before widening enforcement.
