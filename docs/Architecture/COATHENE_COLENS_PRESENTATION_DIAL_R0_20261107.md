# CoAthene CoLens+ Presentation Dial R0 | one question, several chosen views

**Public source candidate · 7 November 2026 · NOT a child-facing deployed service, online school, assessed syllabus, age-verification mechanism, registered child account or professional early-childhood programme.**

## A presentation lens, not a learner classification

Learners and adults should be able to change how an experience is **presented** without being typed into immutable age groups, hidden ability profiles or forced syllabus tracks. CoLens+ is already used by the public CoCivium visual projection examples; this learning-specific dial is a **presentation mode of CoPet**, not a new identity or credential system.

The [Teach Moss offline prototype](../../examples/coathene_copet_r0/index.html) now has a large visible dial with four positions. **No birth date, name, fingerprint, camera, grade or inference is requested.** Choosing a mode is not proof of a person's age, abilities, educational need or legal consent. The presentation affects information density, visuals and interaction, not truth, source criteria, student rights or actual school authorization.

| User-selected lens | What they see | What it is NOT |
|---|---|---|
| **Together · adult with 1–3** | Original large picture, single short cue, simple pointer question, an immediate off-screen activity, **no quiz or learner progress** | A one-year-old operating online school, recommended screen use at age one, formal nursery/school enrollment, unattended activity |
| **Play · roughly 4–7** | Colourful picture, two big short-answer choices, a non-graded correction, safe real-world suggestion, caregiver guidance | Developmental diagnosis, test score, child learning outcome, automatic reading level |
| **Explore · roughly 8–12** | The prior original teaching-by-teaching experience with evidence comparison, a counterexample and optional CoEntour | Ministry-certified lesson or assumed verified understanding |
| **Investigate · teen/adult** | Full original lesson with source, explicit limitation, evidence and responsible challenge | Scientific certification, expert substitute or formal course credit |

These approximate age hints are **optional design examples**, not age gates or guarantees. The responsible adult can choose a different view based on comprehension, disability access, interests, language and purpose. Do not infer age from device, behaviour, voice, face, gameplay or visual selection.

A **separate focus selector**, Wonder / Make / Explain / Challenge, changes the short next-task invitation **without** changing verified facts or a learner profile. The focus selection, CoEntour wardrobe and visit marks all vanish on refresh; the page uses no persistent storage, network calls, analytics, AI models, camera or mic.

## Under three: human relationships before screen experiences

The **Together** position should be an **adult prompt that sends the child away from the screen**. It includes four newly authored simple inline-SVG pictures (rain, sky, butterfly and blocks) without images fetched from an external site. Adult-controlled picture selection is deliberate; there are no autoplay sounds, streaks, manipulative mascots, child scores or long passages for toddlers.

**Developmental caution:** [WHO guidance for children under five](https://www.who.int/news/item/24-04-2019-to-grow-up-healthy-children-need-to-sit-less-and-play-more) does **not recommend sedentary screen time for one-year-olds**, and says at age two it should be **no more than one hour per day, less is better**. [NAEYC infants-and-toddlers guidance](https://www.naeyc.org/resources/topics/technology-and-media/infants-and-toddlers) emphasizes adults as co-players and real-world interactions. The [AAP's 2026 digital ecosystems statement](https://publications.aap.org/pediatrics/article/157/2/e2025075320/206129/Digital-Ecosystems-Children-and-Adolescents-Policy) emphasizes age/context, quality, shared time and prioritizing play, sleep and activity.

Consequently we should **not market the 1–2 position as a screen-based independent school**. At one year it can be an *adult-only planning card*, followed by ordinary responsive play and speaking in the real world. At two, any appropriate screen viewing is short and co-used, not a substitute for toys, movement or interactions. There may eventually be specialized educational services for these ages, but those require qualified early-years professionals, parents/guardians, funding, accessibility and applicable child-care/school law. None is created by the dial.

## Product architecture

`ONE_RESEARCH_QUESTION -> SOURCE_FACTS -> {DISPLAY_LENS, OPTIONAL_FOCUS} -> AGE_APPROPRIATE_PRESENTATION -> OPTIONAL_OFFSCREEN_ACTION`

**The same source remains governing.** CoLens cannot silently remove safety warnings, hide factual counterexamples from responsible reviewers, rewrite correct claims, imply higher achievement, award official credits, or produce an access credential. An educator can inspect the original full explanation even if the learner sees a simplified picture.

The UI has one active lesson/front, with 4 inline vector pictures and large keyboard-accessible buttons. A young child does not have to decode paragraphs to see the selected picture. A caregiver can return to the mode dial and deliberately switch presentation. The **Finished · Let's play off-screen** action clears the current session's transient progress and outfit, leaving a plain stop screen rather than a reward loop.

The earlier [CoEntour+ wardrobe](COATHENE_COENTOUR_COSMETIC_ROUTE_R0_20261107.md) remains optional and cosmetic. [CoPassport+](COATHENE_COPASSPORT_LOGINLESS_CONTINUITY_R0_20261107.md) is still future only and separately protected. The same [CoPrivMin+ privacy rules](../Governance/COPRIVMIN_PUBLIC_PROJECTION_R0_20261107.md) apply to education/age preferences. Neither a digital hat nor a chosen presentation lens becomes a child's hidden identity.

## Proof gates

**Source QA:** compare the machine contract `examples/coathene_copet_r0/learning_map.json` against the exact HTML-embedded CoLens configuration. Test the **64 combinations** of 4 modes × 4 focus intents × 4 original picture scenes; ensure the mode never infers age, assigns mastery, authenticates children, or stores anything. Verify age-one warnings and the no-autoplay/no-quiz toddler boundary.

**Real-browser QA:** in headless Chromium at desktop/mobile sizes, actually click the dial, see the original vector art, select a focus, see the plain toddler cue, dismiss to offline play, return to dial, test Play's two choices, and switch back to Explore/Investigate. Check keyboard accessibility cues, zero horizontal overflow, no automatic network traffic, and original CoEntour and learning functionality. Browser screenshots are synthetic-only and are **not** a real learner response.

**Later independent gates:** adult early-years educator and guardian/learner-rights reviewer inspect the 1–3 view against appropriate guidelines; accessibility/print/text-to-speech alternatives are tested by users with relevant needs; subject-expert review of simplified explanations; guardian-authorized supervised pilots only under applicable law; actual comparison for understanding and developmental benefit against ordinary human play and age-appropriate alternatives. A young child viewing an illustration is not proof of learning.

**Most valuable disconfirming test:** show the Together mode to an independent caregiver and ask whether it encourages setting the screen aside, or instead keeps a one-year-old engaged on screen. If it increases inappropriate screen engagement, redesign or disable that mode regardless of aesthetic appeal.

## Source lineage

- [CoAthene CoPet Teach Moss](../../examples/coathene_copet_r0/README.md)
- [Existing CoLens+ living media twin](../../examples/colensmedia/README.md)
- [CoAthene RoamLab child-safety baseline](../Business/CoAthene_RoamLab_R0/SAFETY_PRIVACY_ACCESSIBILITY.md)
- [WHO early childhood activity/screen guidance](https://www.who.int/publications/i/item/9789241550536/)
- [NAEYC infants/toddlers technology examples](https://www.naeyc.org/resources/topics/technology-and-media/infants-and-toddlers)
- [AAP digital ecosystems, 2026](https://publications.aap.org/pediatrics/article/157/2/e2025075320/206129/Digital-Ecosystems-Children-and-Adolescents-Policy)

`CHOICE_OF_PRESENTATION_NE_AGE_VERIFICATION` · `TOGETHER_AGE_ONE_NE_SCREEN_SCHOOL` · `PICTURE_NE_PEDAGOGICAL_EFFICACY` · `FOCUS_NE_COGNITIVE_PROFILE` · `PARENT_GUIDANCE_NE_CHILD_PROTECTION_CERTIFICATION` · `MODE_SELECTION_NE_LEARNING_LEVEL` · `BROWSER_PASS_NE_CHILD_PILOT`.
