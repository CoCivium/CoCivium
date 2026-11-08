# CoEvoRate+ / CoFitness+ | Comparative Fitness of Versions, Forks, Inverses, and Contributors R0

**2026-11-08 | PUBLIC RESEARCH / REVIEW CANDIDATE | NOT CANON, RUNTIME, DEPLOYED CI, HUMAN RANKING SYSTEM, OR RECEIVER ACCEPTANCE**

## CoHereNow and source-bound reuse

**Question:** When is a successor, fork, competitor, older version, inversion, or no-change alternative *better*, and for whom? Change itself is not improvement. Version numbers are lineage; source activity is not accepted benefit.

**Elected extension, not a rival scoring authority:** Use [CoFitness Model v0](CoFitness_Model_v0__2026-03-24.md) for multidimensional selection and [CoBaseline/CoFrontier Registry R0](../Architecture/COBASELINE_FRONTIER_REGISTRY_R0_20261027.md) for comparability keys, hard floors, non-dominated alternatives, and preserved predecessors. Use [CoSpeedo 7-day scorecard](../Metrics/COSPEEDO_7DAY_SCORECARD_R0_20261026.json) for outcome metrics, [CoStageReview](../Architecture/COREVIEW_PANEL_LIFECYCLE_R0.md) for transitions, and [CoObject vitality](../Architecture/COOBJECT_VITALITY_METABOLISM_R0_20261027.md) for dormancy, repair, successors, and retirement.

A useful product face is a **typed evidence-backed comparison card**, NOT an omniscient global league table.

## 1. Separate six predicates that are commonly confused

1. **Version / lineage:** release tag, date, ancestry, dependency graph, exact source/build identity and supersession; not a quality ranking.
2. **Capability:** can the system perform a declared task under pinned conditions, with uncertainty and failure modes?
3. **Fitness:** does it meet a declared receiver's needs under constraints (safety, autonomy, cost, accessibility, impact, rights)?
4. **Maturity:** has behavior remained reliable across time, environments, failures, independent observers, maintainers and adversarial conditions?
5. **Authority:** what actions are consented, legally permitted and technically authorized? A powerful model has no additional authority by virtue of its power.
6. **Wisdom / judgment:** a context-sensitive behavioral hypothesis requiring calibrated prediction, tradeoffs, acknowledgement of ignorance, harm avoidance and appropriate restraint; neither age nor benchmark score proves this quality.

**Nonclaims:** NEWER_NE_BETTER; AGE_NE_WISDOM; CAPABILITY_NE_AUTHORITY; BENCHMARK_NE_BENEFIT; NOVELTY_NE_MATURITY; VERSION_NE_VALUES; INFERENCE_NE_CONSENT.

## 2. Define 'better' as a relation, not a property of a name

Every comparison first declares:

- **Purpose and perspective:** task, receiver, affected parties, alternatives, nonparticipant externalities, accessibility and language needs.
- **Comparable envelope:** pinned workload, dataset version, test procedure, device/substrate (including OS and iOS version when relevant), environment, resource budget, time window, authority, privacy class, integration dependencies, and risk class.
- **Lineage:** exact hashes/builds, branching relation, licenses, dependencies, version history, change provenance and rollback path.
- **Measures:** metric definitions/units/directions, eligibility denominator, baselines and acceptance floors, environment and uncertainty, independent observers, counterevidence.
- **Evaluation protocol:** preregistered tasks and thresholds, controls, repeats, confidence, shift and adversarial tests, all costs including human intervention and recovery.
- **Decision:** separate output from authorization; preserve competing non-dominated alternatives and specific losers, with the conditions under which the decision reverses.

For an eligible workload W, receiver R, constraints C and time T, the relation is: **A is preferable to B for (W,R,C,T), under declared evidence E**. Incomparable may be the most truthful result. Hard vetoes such as unconsented data release, material safety risk, unlawful reuse or an unmet correctness floor are checked BEFORE optional weighted preferences.

Use a mixed-direction metric vector and Pareto frontier. **A dominates B** only if their comparison envelopes match, all mandatory gates pass, A is at least as good on every required measured dimension and strictly better on one, with uncertainty handled conservatively. Neither dominates when each preserves a relevant advantage. A weighted score can illustrate a *declared stakeholder preference* among already eligible options, but is not universal fitness or authority.

Allowed result classes: DOMINATES, CO_PARETO, CONTEXT_SPECIALIST, INCOMPARABLE, REGRESSION, HELD_UNVERIFIED, HELD_RISK, and WITHDRAWN. A result can be source-qualified but receiver-utility UNKNOWN. A candidate may become best in one context and worst in another.

## 3. Measurement families and anti-metrics

| Family | Candidate measurable quantities | Countermeasure / failure to catch |
|---|---|---|
| Correctness and task value | verified successful user tasks / eligible tasks; error severity; falsified predictions | demo/test count not equal receiver closure |
| Safety and privacy | incident rate, consent violations, disclosure surface, threat-model coverage | an aggregate score cannot offset a privacy breach |
| Reliability and recovery | availability by observation coverage; p95 restore time; independent cold restores | a restart on the same host is not independent failover |
| Interaction and access | completion time, comprehension, assistive-tech task success, correction/undo, abandonment | pleasant-looking UI can be inaccessible |
| Capability and robustness | tested task coverage, calibrated error, out-of-distribution shift, known limitations | average score can hide catastrophic subgroup failures |
| Stewardship and ecology | maintainability, bus factor, exit cost, interoperability, human minutes, energy, money, hardware life | cheap to build can be costly to operate |
| Provenance and governance | evidence coverage, independent verification, licensing clarity, appeal/rollback success | SHA is identity, not truth; reviewer claims do not self-attest |
| Evolution and optionality | recovery-capable successors, retained diversity, forkability, diminishing dependency, debt retired | more forks/commits/session labels can worsen the system |
| Learning rate | precommitted forecast residual, information gain per unit cost, out-of-sample improvement | tuning on the test set masquerades as learning |

Units must be typed: seconds, joules, dollars, incidents/eligible operation, successful tasks/eligible task, receiver closures/hour, provenance coverage, etc. An absent measurement is UNKNOWN, not numerical zero. Record event/observation/valid times separately. Never compare raw counts with different exposures.

**CoEvoRate:** Report parallel axes, not one magical exponent: *qualified useful closure yield*, *recovery rate*, *human relay burden*, *safety/privacy debt*, *learning/information gain*, and *cost/energy*. The 7-day CoSpeedo analysis requires at least four comparable windows (seven preferred) before proposing any growth shape; commits are source activity only.

## 4. Versions, forks, competitors, and inversions

Treat a software family as a branching graph, not one ladder. Compare an older release, a successor, a specialist fork, a competitor, a rollback, a simplified implementation and 'do nothing' using equivalent workloads where possible. Maintain separate frontiers for incompatible tasks or platforms. Regression cases remain preserved and discoverable.

**Inverse/anti-evolution tests:** What becomes worse if we upgrade? What if optimization is reversed, a feature removed, a fork maintained separately, the network is absent, latency doubles, language/domain shifts, assumptions fail, a contributor exits, or the system loses its original provider? Could the most useful evolution be deletion, dormancy, merger, a more reversible design, or preservation of an old version?

**CoPetitor+/competitor contributions:** Credit and compare external advances fairly through a Borrow/Reuse ledger with original author, source, license, reproduction protocol, comparative result, attribution, dates, maintenance, and downstream benefit. Prefer published specifications, permissibly licensed implementations and authorized clean-room comparisons. No taking proprietary code, no invented affiliation or agreement, no reward for benchmark gaming, no unilateral competitor 'inferiority' rating without fair evidence. Mutual improvement and interop may outrank conquest.

## 5. Humans, synthkind, and other entities: type-specific safeguards

**Human people:** Do NOT assign global worth, intelligence, wisdom, civility, dignity, rights or authority scores. Specific, voluntary, legally justified, task-linked feedback may describe observable work or helpful contributions with consent, accommodations, proportional collection, confidentiality, independent review, appeal and deletion/retention rules. Avoid covert surveillance, biometric/sensitive-trait inference, age stereotypes, immutable reputation castes and automated high-stakes decisions. An individual's older or newer self is not a version upgrade. Human dignity and equal rights are not scalar outputs.

**AI/synth systems:** Evaluate model versions on declared task competence, calibration, robustness, safety, bias across appropriate protected/affected groups using lawful data and consent, explainability, context fit, memory continuity where observed, and error correction. A newer model may improve one language and worsen another. A less culturally biased model is a hypothesis to test on balanced, independent, ethically sourced evaluations, not something inferred from release age. Model capability does not grant permission or prove wisdom, independent agency, sentience or subjective experience.

**Organizations / ecosystems / other entities:** Define different moral and empirical measures appropriate to each domain. Ecological health, habitat, consent-governed community relationships and nonhuman welfare should not be collapsed into a universal ranking with human productivity or software throughput. Unknown cases remain open hypotheses; no speculative ontological upgrade by arithmetic.

**Separate governance plane:** Who may act remains defined by consent, responsibility and law, never earned automatically through fitness scores. Every subject can contest an inaccurate assertion where practical; humans have privacy and redress guarantees.

## 6. CI+, iOS, and visible CoOrb UX

**Candidate CI gate:** on each version/fork change, check source/build identity, test fixture reproducibility, declared metric semantics, preregistered comparison envelope, mandatory vetoes, negative controls, fair baseline, regression thresholds, provenance, debt/rollback and named receiver proof. A code test proves code behavior under its conditions, not real-world adoption; no automatic merge/promotion from a score. Pin and preserve the exact tested subject and test version.

**iOS / other device adaptations:** explicitly test applicable OS/device ranges, assistive technologies, VoiceOver/dynamic text, touch/voice/keyboard input, offline and permission-denial cases, energy/battery, background execution limits, safe app lifecycle, privacy disclosure, full user undo and native fallback. App Store eligibility and distribution are independent of source tests. No claim of native iOS build or Apple approval. Apply the same user-centered semantics on Android, Windows, browser and emerging surfaces without pretending device APIs are identical.

**One CoOrb gauge, plural needles:** a human-facing card shows (a) purpose, (b) eligible candidates, (c) gate state, (d) current Pareto alternatives, (e) specific gains/losses and uncertainty, (f) one recommended bounded experiment, (g) provenance and undo. 'Best for this task' must be qualified; 'best software' by itself is not a defensible product claim.

## 7. Falsifiers and first bounded acceptance plan

Use existing CoBaseline harness first. Candidate negative-control matrix:

1. **VERSION TRAP:** newer build has higher throughput but fails correctness floor. Expected HELD_RISK, older remains eligible.
2. **FORK TRADEOFF:** specialist fork has better recovery but worse task latency. Expected CO_PARETO rather than forced winner.
3. **CONTEXT TRAP:** iOS mobile/privacy envelope differs from desktop/local envelope. Expected INCOMPARABLE until a valid bridge test exists.
4. **PROVENANCE TRAP:** one unverified source asserts receiver ACK or author rights. Expected HELD_UNVERIFIED.
5. **BIAS TRAP:** better overall model score with worse group/language failure and insufficient sample. Expected no universal improvement claim.
6. **AUTHORITY TRAP:** highest capability or fitness tries to grant itself permission. Expected hard veto.
7. **PEOPLE TRAP:** personal/global person ranking is proposed. Expected out-of-scope prohibited design.
8. **COMMIT TRAP:** many commits and self-reported PASS but zero independently verified effects. Expected utility UNKNOWN.
9. **INVERSION TRAP:** a no-feature/rollback option produces better restoration or lower burden. Expected preserve it as eligible alternative.
10. **GAMING TRAP:** evaluator changes thresholds after seeing results. Expected invalid comparison and full disclosure.
11. **UNCERTAINTY TRAP:** metric lacks units, denominator or source time. Expected HELD_UNVERIFIED.
12. **COMPETITOR TRAP:** derivative lacks permitted reuse rights or attribution. Expected no ingest/promotion.

**First real experiment:** compare the most recent source-bound RickBar localhost-HTTP safety work against its pinned predecessor on identical authorized tests; record both regression controls and independent acceptance status. Do not infer a running X2/iOS deployment or end-user return from GitHub source. Reuse current CoBaseline, CoStageReview and CoSpeedo rails rather than launch another scheduler or actuating service.

**Promotion gates:** reproducible comparator tests; independent or qualified evidence for actual claimed benefit; no false authority; preserved lineage and counterexamples; real receiver response only if receiver impact is claimed. Until then, the product claim remains RESEARCH_CANDIDATE.

## 8. References and next planning rail

- Existing [CoFitness](CoFitness_Model_v0__2026-03-24.md), [CoEvo modes](CoEvo_Modes_v0__2026-03-24.md), [CoEvo R&D paths](CoEvo_RnD_Paths_v0__2026-03-24.md), [CoBaseline frontier](../Architecture/COBASELINE_FRONTIER_REGISTRY_R0_20261027.md), [CoStageReview](../Architecture/COREVIEW_PANEL_LIFECYCLE_R0.md), [CoSpeedo scorecard](../Metrics/COSPEEDO_7DAY_SCORECARD_R0_20261026.json).
- ISO/IEC 25010:2023 (ICT product quality model): https://webstore.iec.ch/en/publication/90024
- DORA delivery throughput/instability metrics: https://dora.dev/guides/dora-metrics/
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework/ai-risk-management-framework-faqs
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- Apple App Review Guidelines and Human Interface Guidelines: https://developer.apple.com/app-store/review/guidelines/ and https://developer.apple.com/design/human-interface-guidelines/

**Highlight:** this bounded document is the public review-facing comparison contract, not a new canonical root. **Plan:** integrate a versioned comparison card with the existing frontier and acceptance/CI process only after isolated negative-control tests and receiver-value evidence. **One elected writer, many read-only challengers.**

**Nonclaims:** NEWER_NE_BETTER; BEST_NE_UNIVERSAL; PARETO_NE_AUTHORITY; TEST_PASS_NE_ACCEPTANCE; SELF_ATTESTATION_NE_INDEPENDENCE; PEOPLE_NE_SOFTWARE_METRICS; SYNTH_CAPABILITY_NE_SENTIENCE; BENCHMARK_NE_BENEFIT; COMMIT_NE_IMPROVEMENT; PUBLIC_REPO_NE_DEPLOYED_APP; NO_CROSS_SESSION_ACK_WITHOUT_READPROOF.