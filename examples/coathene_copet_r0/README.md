# CoAthene CoPet R0 | Teach Moss, not a child profile

**PUBLIC SOURCE CANDIDATE · 2026-11-07 · OFFLINE local demo · No child accounts, IDs, records, AI companion service, certified syllabus, live educator, or deployment.**

## What actually works at source level

[Open the single-file HTML source](index.html) to inspect or run in a browser that permits local scripts. Choose any of four *explicit* interests (rivers and rain, space and motion, animals and habitats, games and inventions). Fictional Moss begins with a flawed belief. The learner chooses (1) a more defensible explanation and (2) appropriate evidence, then sees a factual explanation, a counterexample and one further transfer question.

The display counts only the topics encountered **in this visit**. It shows five broad school-coverage windows as exploration, **not scores, competency badges, grades, profiling, course completion or official Ontario curriculum strands**. Refreshing or closing the browser discards the interaction. No cookies, persistent storage, identity, camera/microphone, network calls, chat, AI model, notifications, linked guardians, purchases or third-party telemetry.

This supports the user's long-term vision of **interest-led, revisable syllabuses**, while admitting that teaching real literacy, mathematics, disciplinary knowledge, child safety and educational assessment requires more than an unbounded path generator. The student can ask a question first, but a real educator can still see missing prerequisites and qualifications, and reject harmful topic omissions.

## What “no login” actually means

The learner need not sign into this **read-only demo**. There is **no persistent progress** in R0. To restore a real learner's history safely across devices, the product will need a purpose-limited, pseudonymous progress handle, authorized recovery and selective access. That may look like a **guardian-controlled passkey or encrypted learner passport**, without username/password fields, but authentication, age-appropriate consent and security controls would still occur.

[CoPassport+ child identity and continuity contract](../../docs/Architecture/COATHENE_COPASSPORT_LOGINLESS_CONTINUITY_R0_20261107.md) distinguishes:
`CoGuest+ (ephemeral) | CoPet+ (story) | CoLearnerHandle+ (authorized random identity) | CoPassport+ (minimum records) | CoDelegation+ (scoped guardian/mentor/school access)`.

A child's pet is never their legal identity, trusted adult, authenticated school account or proof of cognitive status. A printed summary can be personal work, not proof of its author or an authorized key. No implicit server-side child identifier, browser/device fingerprint or hidden persistent profile.

## Pedagogical/safety limitations

- Moss is **explicitly fictional**, with no apparent sentience, human-friend promise, secret-keeping, manipulative streaks, personal bonding or private messages.
- The lesson checks an answer against **fixed authored examples**, not an AI arbitrator, psychometric test, human review or independently validated learning gain.
- Evidence selection and misconception revision are useful demonstrations; actual progress should require appropriate understanding, domain transfer and future review, not a click record.
- For children, a suitable guardian/educator must still be involved as needed. An under-13 child's personal information cannot be collected simply because a digital pet exists. See [Canadian OPC Children's Privacy Code](https://www.priv.gc.ca/en/privacy-topics/privacy-for-businesses/protection-of-children-for-businesses/childrens-privacy-code/children-code-final-report-2026/), [UNICEF AI-and-children guidance v3](https://www.unicef.org/innocenti/reports/policy-guidance-ai-children), and [Vanderbilt teachable agents research](https://www.vanderbilt.edu/oele/teachable-agents/) as prior work. These references **do not endorse this demo**.
- A content review is still needed for age suitability, disability/accessibility, scientific accuracy, cultural sensitivity and security. External sources can change; all lesson outcomes are unvalidated.
- In a future social or AI-guided service, real human guardianship, safe communications, consent, limits and appeal must be independently designed and audited. A synth must not autonomously decide important child outcomes.

## Build and test

Source twin: [`learning_map.json`](learning_map.json). Standalone browser UI: [`index.html`](index.html).

The repository tests extract the **actual embedded UI engine** to test lesson and answer logic without requiring a server:

`node --test tests/test_coathene_copet_r0.test.js`

The Python tests check private-info and offline rules, source-twin consistency, no mastery/persistent child profile claim, and no automatic identity:

`python -m unittest discover -s tests -p 'test_coathene_copet_r0.py' -v`

**Needed before child pilot:** independently reviewed science/learning examples, a child-safety/privacy impact assessment, age-appropriate guardian/learner consent, actual usability and keyboard/mobile/print testing, and independent adult educator comparison against a neutral explanation. For real progress continuity, separately build and security-review a cryptographic identity/consent/recovery subsystem. **No prototype code here constitutes that subsystem.**

## Prior source continuity

[CoAthene Anywhere Studio](../coathene_anywhere_r0/README.md) and [Why have schools?](../../docs/Public/COATHENE_WHY_HAVE_SCHOOLS_R0_20261107.md) are public-source companion concepts, not deployed sites. [CoPrivMin+](../../docs/Governance/COPRIVMIN_PUBLIC_PROJECTION_R0_20261107.md) guides public-safe source projections. This CoPet proposal does **not** include copies of any private learner thread, personal contact, child records or CoSteward-restricted research payloads.

`VISIT_COVERAGE_NE_MASTERY | PET_NE_PERSON | NO_LOGIN_NE_NO_AUTHENTICATION | LOCAL_MEMORY_NE_DURABLE_PROGRESS | SYNTH_EVIDENCE_CHECK_NE_CHILD_GUARDIAN | PUBLIC_SOURCE_NE_DEPLOYED_PRODUCT`.
