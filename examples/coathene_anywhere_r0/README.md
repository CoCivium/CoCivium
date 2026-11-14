# CoAthene Anywhere Studio R0 | Instabuild + Groupbuild

**State:** PUBLIC SOURCE DRAFT · Not a deployed website, AI tutor, school, school franchise, video room, real-time service, pupil registry, accredited course, virtual campus or completed learner evaluation.

**First-use task:** choose an inquiry question, choose SOLO / GROUP / MENTORED / INSTITUTION-SUPPORTED, select WHEREVER / OFFLINE / ONLINE-OPTION / PHYSICAL VENUE / MIXED, optionally pick a youth-with-supervisor plan. Instantly assemble an **in-memory one-front lesson plan** with an original domain explanation, activity, strong counterexample, transfer task and a prediction/reveal exercise. Groupbuild includes rotating *seat roles*, no names. Close/reload to discard everything.

[Open the source for the single-page offline preview](index.html). A GitHub source link is **not** a hosted runtime. Download/opening a reviewed copy is an optional way to test locally; no CoAthene account is required, and the prototype does not transmit data. A public Pages receiver and an actual first-time user test are separate future gates.

## Why this instead of building a virtual school

Decouple seven relations rather than making one campus/organisation mandatory:

`QUESTION | ACTIVITY | PEOPLE | FACILITATOR | LOCATION | INSTITUTION | CREDENTIAL`.

- **Question/activity**: a learning tool should work without requiring the remaining five.
- **People**: a group is optional; this **does not** connect, invite, record or verify real people. Real collaboration requires informed participation and a separately legitimate channel.
- **Facilitator**: optional for suitable adults; actual qualified supervision is mandatory where the intended participant/activity/law demands it.
- **Location**: digital, home, library, classroom, nature, community or mixed; material and safety constraints still exist. “Anywhere” means venue choice when appropriate, not permission to access any place.
- **Institution**: a lawful school, library, university, museum, club or consenting community may provide infrastructure without acquiring ownership of the learner's underlying question or content.
- **Credential**: only a separately authorized institution may confer credits or qualifications under applicable requirements; no app, badge, self-printed certificate or CoClan status can confer those rights.

**Therefore** `NO_BUILDING_REQUIRED_FOR_A_STANDALONE_LEARNING_TOOL` does not mean `NO_INSTITUTIONAL_SAFEGUARDING_OR_LEGAL_ATTENDANCE`.

### First two real product doors

**Instabuild:** an adult or supervised learner assembles a local inquiry from a source-bound question and receives an actionable plan. Duration and domain coverage are *not personalized algorithmically*; this is a deterministic scenario selector.

**Groupbuild:** the same question becomes an optional cooperative kit with Questioner, Evidence Checker, Counterexample Finder and Builder/Explainer seats. Changing from volunteer to paid/institutional contributor must retain the existing [GroupBuild+ rights and CoTeaming model](../../docs/Architecture/GROUPBUILD_COTEAMING_COPAYBACK_R0_20261101.md). This R0 has no chat, participant credentials, payment, social service or synchronisation.

**Later variants (NOT IMPLEMENTED):** mentor booking, educator review, child-safe physical field kit, accredited-course adapter, virtual school operation, library community lease, lawful hybrid campus, synchronized distributed study circle, school governance/funding and portable interoperable portfolios. Each needs its own qualifying legal, privacy, technical and human gates.

## Existing CoCivium lineage, preserved

- [GroupBuild+ R0](../../docs/Architecture/GROUPBUILD_COTEAMING_COPAYBACK_R0_20261101.md) already defines the commons/managed dual doorway and contributor rights.
- [CoAthene RoamLab](../../docs/Business/CoAthene_RoamLab_R0/README.md) already defines standalone / sidecar / CoAll-native products, and treats a vehicle as an optional substrate.
- [Watershed Explorer module](../../docs/Business/CoAthene_RoamLab_R0/modules/WatershedExplorer_R0/README.md) already has a learning-objective and safeguarding baseline. The R0 example reuses the educational *concept*, not learner records or a claim of independent user validation.
- [CoVirtualSession morphology](../../docs/Architecture/COVIRTUAL_SESSION_MORPHOLOGY_R0.md) separates durable role/question identity from a particular live tab/worker.
- [Why have schools? R0](../../docs/Public/COATHENE_WHY_HAVE_SCHOOLS_R0_20261107.md) supplies the human-purpose starting point.
- [CoPrivMin+](../../docs/Governance/COPRIVMIN_PUBLIC_PROJECTION_R0_20261107.md) requires original public-safe projection, not private repo dumping.

### Independent public authorities to consult, not badge

[UNESCO Institute for Lifelong Learning](https://www.uil.unesco.org/en/unesco-institute/mandate/lifelong-learning) recognizes learning in home, school, communities, workplaces and online. The [Ontario K–12 online learning policy](https://www.ontario.ca/document/ontario-schools-kindergarten-grade-12-policy-and-program-requirements/online-and-remote-learning) acknowledges course delivery without teachers and students normally sharing a physical place. [Ontario's private-school notice page](https://www.ontario.ca/page/private-schools-notice-intention-operate-private-school) and online school rules require qualified operators to meet separate obligations. A location-free page is not a legal shortcut around a school's responsibilities.

## What the working source does

- Three original source-linked questions: runoff, appearance versus software permissions, and shared public-space design.
- One local question-led plan at a time, with solo/group/mentor/institution variants and five location modes.
- Live local prediction/reveal and correction. **No score, identity, answer or click history is stored**.
- Groupbuild role seats 2–6, no names; never claims connected participants.
- Youth participation context shows an unverified but explicit requirement for actual responsible adult supervision; not a way to enroll a child.
- Keeps basic activity available without a headset, account, institution, permanent Clan, payment, network or proprietary vendor.
- A user-initiated browser print action and explicit external source links. No auto-navigation.
- Inline assets, no analytics, web requests, cookies, localStorage, media capture, external images, remote fonts, persistent user state or server calls. An explicit click on an original source link can navigate outside the offline page.

This is a **source-level functional concept**, not evidence of classroom performance, correct operation on every browser, accessibility conformance certification, or deployment to CoAcademy/X2.

## QA and acceptance

**Pure engine and source policy:** `node --test tests/test_coathene_anywhere_r0.test.js` and `python -m unittest discover -s tests -p 'test_coathene_anywhere_r0.py' -v`. The Node test extracts the exact embedded script from this HTML and exercises the real pure `buildPlan` function against the machine-readable `recipe.json`; it does not claim real-browser GUI coverage.

**Necessary next proofs:** browser test on desktop and mobile, keyboard/tab/focus, a print/readability check, offline source opening, real human first use, and clear discrimination between a generated group plan and an actual live classroom. For *minors*, obtain an independent responsible educator/child-safety, accessibility, privacy and consent review first.

### Proposed independent first-use tasks

1. Without being told what a CoWay is, choose a question and build a no-account offline lesson.
2. Switch to group mode and find the optional roles, with no claim that anyone has been connected.
3. Choose an institution-supported youth path and identify what is still **not** provided: teacher, school, credits, guardian consent, attendance recognition.
4. Answer the first prediction and explain one case that defeats an over-broad claim; test whether the real subject was understood rather than whether a CoTerm was memorized.
5. Locate the source reference, exit, reset and print. Ask whether a venue could help or whether the same objective works without one.

**Real comparative metrics:** time-to-usable-plan, comprehension of the actual subject, false-institution-confusion rate, successful stop/reset, accessible path completion, no forced registration/venue, rights and cost clarity. No data from people have been collected.

## Rails

`INSTANT_PLAN_NE_LIVE_CLASS` · `GROUP_ROLE_NE_GROUP_CONSENT` · `VIRTUAL_SCHOOL_NE_UNREGULATED_SCHOOL` · `LEARN_ANYWHERE_NE_IGNORE_COMPULSORY_SCHOOLING` · `PRINT_NE_STUDENT_CREDENTIAL` · `NO_LOGIN_NE_NO_CHILD_PROTECTION_NEEDED` · `LOCAL_TEST_NE_HUMAN_ACCEPTANCE` · `PUBLIC_BRANCH_NE_LIVE_SITE`.
