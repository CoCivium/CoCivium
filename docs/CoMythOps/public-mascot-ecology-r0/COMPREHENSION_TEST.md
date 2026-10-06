# Public Mascot Ecology R0 — Blind Comprehension Test

**State:** `TEST_PROTOCOL_CANDIDATE__NOT_RUN`  
**Date:** 2026-10-06

## Question

Can a newcomer infer the intended functional distinction among Dragon, Kitten, Turtle, and Cloud without first being taught the internal CoTerms?

## Blind prompt

Show only these four short fragments, in randomized order:

1. **HEADLESS MAGIC DRAGON FROM BEYOND THE FRONTIER UPGRADES WORLDS**
2. **BEAXAKITTEN TO THE RESCUE: FIXING THE RELS THE DRAGON MISSED**
3. **THE TURTLE KEEPS GOING AFTER THE FIRST PROJECT ENDS**
4. **THE CLOUD HOLDS THREE POSSIBILITIES THAT DO NOT YET AGREE**

Then ask the participant to assign each to one or more plain-language roles:

- large-scale change / infrastructure;
- care / repair / nuance;
- persistence / branching / continuity;
- ambiguity / hypothesis / possibility.

Do not show the expected mapping until after the response is recorded.

## Expected mapping

```text
DRAGON -> SCALE / INFRASTRUCTURE / DISRUPTION
KITTEN -> CARE / REPAIR / RELATIONAL_NUANCE
TURTLE -> CONTINUITY / BRANCHING / PERSISTENCE
CLOUD -> POSSIBILITY / AMBIGUITY / HYPOTHESIS
```

## Scoring

Record separately:

- exact first-choice mapping;
- acceptable multi-role mapping;
- confidence;
- memorable phrase;
- confusing phrase;
- whether any mascot was interpreted as authority, nationality, factual scientific claim, or literal AI identity.

## Candidate success threshold

A candidate passes only if:

- at least 3 of 4 mascots are mapped to the intended role by a clear majority;
- Kitten is not dismissed as merely decorative;
- Dragon is not read primarily as a national stereotype;
- no mascot is commonly interpreted as having authority merely because it is a mascot;
- the distinction remains understandable without internal CoTerms.

A failed test is a useful result. Revise the symbol or wording rather than teaching the audience harder.

## Rails

```text
COMPREHENSION_NE_AGREEMENT
MEMORABILITY_NE_CORRECTNESS
MASCOT_NE_AUTHORITY
CUTE_NE_TRIVIAL
COUNTRY_NE_PUNCHLINE
TEST_RESULT_NE_PUBLIC_ADOPTION
```

## Next state

`NOT_RUN`

No claim of comprehension, usability, or adoption exists until responses are actually collected.
