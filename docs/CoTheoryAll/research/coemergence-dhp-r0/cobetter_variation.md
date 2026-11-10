# CoBetter+ / CoVariation+ / CoCounterPattern+ R0

**State:** public-safe, source-linked **research candidate**. No validated global optimizer, no runtime, no academic credential, no proof of divine will, no autonomous execution.

**WorkID:** `COBETTER_VARIATION_INVERSION_R0_20261109`

## Why this matters

An observed success is not enough to conclude that an action is a net improvement. A system that repeatedly rewards apparent success can lock in a flawed metric, suppress disconfirming cases, harm people excluded from the metric, and destroy future options. Rare variation, random probes and anomalous results may expose gaps, but novelty alone carries no entitlement to promotion.

A useful system must retain the ability to choose **none of the above**, to say **unknown**, and to preserve alternatives rather than forcing a universal winner.

## The CoBetter+ arbitration proposal

1. **Hard gates first.** Rights, consent, privacy, safety, reversibility and authorization are constraints, not compensable terms in a score. A candidate that fails a hard gate is not eligible for effectful experiments, regardless of expected gain.
2. **Typed outcomes, plural values.** Measure task result, harm, distribution of benefits, future optionality, error rate, ecological cost, attention cost, compute cost, reversibility, and uncertainty. Keep units, populations, baselines and time horizons explicit. Some objectives are not commensurable.
3. **Keep the strong baseline.** Compare against an ordinary well-designed method and a `NO_CHANGE` option; use future-only tests and freeze the information cutoff.
4. **Preserve dissent and unexplored branches.** Record counterexamples and rejected alternatives with provenance, expiry/review trigger and reasons. Zero observations is not a zero effect.
5. **Bounded exploration.** Reuse `CoExperimentSelector+` reserved `CHALLENGE`, `EXPLORATION`, `WEIRD`, `REPLAY` and `FAULT` lanes. A seeded random sample may be used inside an eligible exploration pool as a **control**, never an unbounded task generator. Record the seed, sampling frame, distribution and rejected candidates.
6. **Adversarial feedback.** Routinely attempt to disprove favored approaches, check for Goodhart effects, feedback loops, demographic neglect, confounding and distribution shift.
7. **Pay forward recoverably.** Retain validated patterns, failures, null results, historical versions and practical transfer limits. A model's apparent success in one setting grants no authority in another.

`WORKS_NE_BETTER` | `RANDOM_NE_GOOD` | `PARETO_NE_TRUTH` | `METRIC_NE_VALUE` | `VARIATION_NE_EXPERIMENT` | `REUSE_NE_TRANSFER_PROOF` | `PROJECTION_NE_AUTHORITY`

## Proposed relation graph

- `CoWorks+` --`IS_NOT_SUFFICIENT_FOR`--> `CoBetter+`
- `CoBetter+` --`REQUIRES`--> `explicit_values + rights_gates + counterfactual_baselines + uncertainty`
- `CoPatternGain+` --`CHALLENGED_BY`--> `CoCounterPattern+`
- `CoVariation+` --`SAMPLED_BY`--> `bounded_seeded_exploration`
- `CoRandomControl+` --`EVALUATED_AGAINST`--> `intentional_selection`
- `CoDissentReserve+` --`PROTECTS`--> `unfavored_but_eligible_hypotheses`
- `CoNull+` --`DISTINGUISHES`--> `missing/zero/unobserved/refuted/declined`
- `CoDirectionalDelta+` --`REQUIRES`--> `comparable_units_and_time_cutoffs`
- `CoPayForward+` --`REQUIRES`--> `source_bound_transfer_and_failure_ledger`
- `G_dSide+` --`OFFERS`--> `revisable_plural_future_scenarios`, **not** discovered supernatural instructions.

## Eight CoDhP research-card feeders (unconferred research agenda)

| ID | Research question | Baseline / challenge | Stop criterion |
|---|---|---|---|
| DHP-EM-027 | When does a high task success rate fail a broader notion of better? | Strong multi-objective decision worksheet with explicit harms and consent | No added benefit over worksheet |
| DHP-EM-028 | Does a Pareto frontier prevent premature single-metric crownings? | Ordinary multi-criteria analysis; adversarial incomparable outcomes | Arbitrary scalar domination or hidden tradeoffs |
| DHP-EM-029 | Does a protected weird/exploration reserve discover useful counterexamples? | Equal-budget deterministic, uniform random and strong existing selector | Higher cost/no information benefit in blinded trials |
| DHP-EM-030 | Can random perturbation expose model blind spots without contaminating evidence? | Fixed seed, disclosed sampling frame, negative controls | Unlogged randomness, post-hoc changes, sampling bias |
| DHP-EM-031 | How can one distinguish beneficial feedback from Goodhart loops? | Pre-registered holdout, negative results, target leakage checks | Optimization improves proxy while degrading actual outcome |
| DHP-EM-032 | When should apparently successful old patterns be retired? | Drift monitoring, historical control, old-version readback | Drift undetected or revision erases history |
| DHP-EM-033 | How much optionality should be preserved for unobserved futures? | Quantified choice-set retention and reversible alternatives | Unsupported predictions substitute for actual options |
| DHP-EM-034 | What counts as gain for people absent from the demand signal? | G_dSide plural futures vs supply/demand/hybrid/no-change | Inferred needs without consent or demonstrable harm |

**DhP boundary:** These are provisional research questions, not doctorates, an institution's degree decisions, peer review, active academic projects or claims of originality. The established DhP candidate governance remains separate.

## Tiny synthetic selector fixture

`cobetter_variation_fixture_r0.py` is intentionally small. It proposes a bounded test slate with an explicit `NO_CHANGE` baseline, hard-gated candidates, a challenge slot and a seeded weird/exploration slot. The toy compares outcomes on multiple axes without pretending to determine one universal best. The program neither launches experiments nor controls accounts/devices. Run the built-in tests; inspect the structured report.

### What the fixture *cannot* prove

- It does not demonstrate that random ideas outperform expert proposals, the existing selector or careful Markdown.
- It does not validate the values, probability distributions or outcome estimates. It uses synthetic examples.
- It does not demonstrate an always-on scheduler, independent receiver, X2/CoOrb integration, cross-session pickup or real-world improvement.
- It does not establish the nature, agency or desires of God. `G_dSide+` remains a revisable philosophical/value perspective.

## Source reuse

- Existing CoExperimentSelector+ with bounded `CHALLENGE/EXPLORATION/WEIRD/REPLAY/FAULT` reservations: https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COEXPERIMENT_SELECTOR_R0.md
- Existing G_dSide+ and CoGoldenBraid+ plural-futures, consent, non-scalar/Pareto research contract: https://github.com/CoCivium/CoCivium/blob/main/docs/Evolution/GDSIDE_COPRIMATH_GSLOOP_PUBLIC_R0.md
- Existing CoTheoryAll research front door: https://github.com/CoCivium/CoCivium/blob/main/docs/Public/CoTheoryAll_Substack_Draft_2026-10-06.md
- Draft CoEmergence+ / CoDhP+ 12-card feeder: `docs/CoTheoryAll/research/coemergence-dhp-r0/README.md`
- Private predecessor packets: `COEMERGENCE_DHP_GOLDENBRAID_RESEARCH_PACKET_R0_20261109`, `COPATTERN_PAYFORWARD_COTIME_COPREDICTION_DHP_ADDENDUM_R0_20261109`, `CODIRECTIONAL_DELTA_INVERSION_MULTISCALE_DHP_R0_20261109`.

## Promotion gates

`CONCEPT` -> `SOURCE_LEVEL_TESTED` -> `INDEPENDENT_REVIEWED` -> `EQUAL_BUDGET_BENCHMARKED` -> `RECEIVER_VERIFIED` -> `AUTHORIZED_OPERATION`, each a separate evidence-bearing transition. For now this proposal remains a **draft research branch**. It should not overwrite mainline CoTheoryAll or claim an autonomous evolutionary loop.

**CoNext:** Compare equal-budget simple baselines, the existing CoExperimentSelector+ and a bounded random control on a public-safe benchmark with blinded outcome evaluation; record failures and human time alongside any positive result.