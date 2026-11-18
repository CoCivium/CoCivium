# CoPatternGate+ | Emergent Pattern, Inversion and In-Between Transition R0

**2026-11-08 | PUBLIC REVIEW CANDIDATE | SOURCE_ONLY | NOT AN ACTIVE SCHEDULER, SESSION FAN-OUT, CANON OR RECEIVER ACK**

## Reuse, not a new control plane

This is a bounded read-only adapter proposal for the existing [CoEvo intake policy](../../ai/evolution-intake-policy-r0.json), [session write-back fan-in](../Evolution/COSESSION_WRITEBACK_FANIN_R1.md), [CoListFabric election](../Architecture/COLISTFABRIC_ALL_LISTS_IN_FIELD_R0_20261026.md), [CoFlow Delta Unblocking](../Architecture/COFLOW_DELTA_UNBLOCKING_R0_20261026.md), [CoNull/CoPriMath measures](COMEASURE_COPRIMATH_RELATIONAL_FABRIC_R0_20261108.md) and [CoEvoRate comparison](COEVORATE_COMPARATIVE_FITNESS_R0_20261108.md).

No new semantic ownership root. Preserve the pre-existing `ai/evolution-deltas/<YYYY-MM-DD>/` intake surface and CoEvoDelta version compatibility. This candidate's [question catalogue](../../ai/evolution-pattern-transition-r0.json) is advisory metadata, not an incompatible automatic extension of the existing v0.2 intake schema. Existing elected receivers and effect gates remain unchanged.

## Recommended phase transition

`SOURCE / OBSERVATION -> QUALIFY -> DEDUPE / FAN-IN -> CoPatternGate [OBSERVE + CHALLENGE + HYPOTHESIZE] -> ELECT -> REVIEW / SHADOW FAN-OUT -> AUTHORIZED TEST -> INDEPENDENT RETURN -> RECONCILE -> SLEEP / WAKE`.

The gate is **not** a permission to broadcast, spawn live workers, merge source, execute code, collect private data, or promote any hypothesis to governing truth. Its output is a small typed decision/review request with source, counterclaim, receiver, predicted effect, negative controls, bounded test, expiry/wake and explicit nonclaims.

### Trigger, throttling and admission

Run at **material deltas**, evidence-quality changes, resolved/stale dependencies, serious contradictions, an independent receiver result, a precommitted forecast mismatch, or a new high-value question. Identical unmodified ingestion and no-material-delta produce QUIESCENT, not repetitive summary.

Hard guards (consent, privacy, safety, provenance and permitted effects) are checked before any effect; a read-only exploration may continue even if an unrelated effect remains blocked. Source identity must be pinned; confidential material is not copied to a public branch. Duplicate hypotheses may share one canonical candidate ID plus many source projections.

## The questions at the middle

The [policy catalogue](../../ai/evolution-pattern-transition-r0.json) specifies 13 candidate lenses:

1. **Pattern:** recurrent structure or merely shared-source repetition?
2. **Worked/failed delta:** which first missing link caused stalls, and what differed in successes?
3. **Inversion:** reverse, delete, simplify, preserve predecessor, rollback, split, merge, or do nothing?
4. **In-between:** what interface, dependency, translator, lag, boundary, handoff or missing relation sits between endpoints?
5. **CoNull:** unknown versus observed zero, scoped absence, contradicted, censored, prohibited or stale?
6. **Prediction:** measurable outcome, horizon, prospective baseline, falsifier, sensitivity and uncertainty?
7. **Causal challenge:** controlled causal model or merely correlated/analogical edges?
8. **Competitor/alternative:** which independently sourced outside, older, simpler or adversarial baseline could win?
9. **Definition:** compatible semantic kinds, units, denominators, scopes, time frames and measurement methods?
10. **Ethics/authority:** privacy, affected-party, legal rights, human dignity, externalities and action limitations?
11. **Resource:** what's the least-cost discriminating experiment and its expected information gain?
12. **Receiver:** who can benefit, refuse, independently witness and contest the result?
13. **Return:** exact effect evidence, expiry, supersession, wake rule and retirement criterion?

Not all questions need a model invocation. The default is deterministic cheap filtering, then optional specialist challenge only when consequential.

## Emergent pattern candidates worth testing

These are **hypotheses inferred from repeatedly documented CoCivium failure classes**, not measured laws:

| Candidate | Expected discriminating result | Inverse and intermediate |
|---|---|---|
| P-A Closure-limited ecology | Beyond a backlog threshold, additional generation raises atomic debt faster than verified useful closure | Can smaller, better-targeted fan-out still help? Is the actual gap receiver access, not generation? |
| P-B Interface debt dominates | Repairing missing source -> receiver edges beats rewriting sound internal code for selected user tasks | What if old interface was intentionally protective? Test an adapter/bridge before deletion |
| P-C Source-bound memory beats chat relay | Stable WorkIDs and readproof reduce human relay and re-explanation compared with transcript-only workflows | What if packet maintenance exceeds savings? Measure *total* attention |
| P-D Unknown-class precision reduces false greens | CoNull states and qualified relation types reduce unsupported promotion without suppressing valid experiments | What if HOLD increases false negatives? Permit cheap reversible shadow tests |
| P-E Contextual Pareto forks improve robustness | Keeping non-dominated predecessors improves recovery under real environment shifts | What if fork-maintenance cost exceeds option value? Dormancy/retirement controls |
| P-F Falsification improves prediction | Precommitted outcomes and negative controls improve out-of-sample calibration over narrative pattern selection | Negative results can be artifacts of bad instrument design; retest methods |
| P-G Integration pressure has a knee | When hypothesis arrival exceeds qualified fan-in capacity, dedupe cost, currentness debt and user delay increase nonlinearly | Detect when fan-in is too strict and suppresses independent useful ideas |
| P-H Diversity is not independence | Many model answers with correlated training/sources add fewer independent witnesses than their apparent count | Source-diverse slower comparison may outperform massive homogeneous output |
| P-I Better performance can be subtraction | Deleting duplicate layers, sleeping dormant services and reducing questions can improve user task throughput | Over-pruning may destroy recovery reserve or creative option value |
| P-J Boundary/latency drives temporal surprises | Separating event, observation, valid and receiver times reveals false currentness and apparent pattern shifts | A timestamp correction may eliminate the supposed anomaly |

For each, retain null or disconfirming cases and original baseline. No guarantee these candidates generalize.

## Legitimate placeholders and unsafe placeholders

A **placeholder** may be a typed, time-limited hypothesis slot with explicit provenance, unmeasured state, owner/receiver, next discriminating evidence, wake/expiry and permitted effect = NONE. This is a *research candidate*, not a fake measurement, incomplete button, invented service, or unallocated authority.

Good: `PATTERN_CANDIDATE | SOURCE_BOUND | HYPOTHESIS | TEST_REQUIRED | EXPIRES_ON_NO_NEW_EVIDENCE`.

Bad: `ACTIVE | ACKED | BEST | 0 | RUNNING` when no independent source supports those claims. Use CoNull typed UNKNOWN rather than numeric 0.

## Fan-out mode selection

- **QUIESCENT:** no material change; retain source and sleep.
- **HOLD_UNVERIFIED:** missing evidence/currentness/definition or untestable forecast; no speculative fan-out.
- **HOLD_PRIVATE / HOLD_EFFECT_GATE:** privacy or action scope not authorized; no exposure/action.
- **CHALLENGE_READ_ONLY:** conflicting or contested claims need independent review, preserve both.
- **REVIEW_SHADOW_ONLY:** qualified low-risk bounded hypothesis; propose one receiver-relative review or offline test without executing it.

Independent challenger roles can inspect alternative explanations and hidden dependence; role count does not imply separate model processes or sources. One authorized writer may later promote an exact effect after its own gate.

## Machine source and bounded synthetic tests

- [Read-only candidate adapter](../../scripts/CoEvoPatternTransitionR0.py)
- [Typed question and disposition catalogue](../../ai/evolution-pattern-transition-r0.json)

The adapter accepts one JSON claim object. It produces a plan/disposition only and never writes files, starts workers, contacts services or executes effects. Its `--selftest` defines synthetic positive/negative cases for materiality, privacy, currentness, test/falsifier requirements, inversions, gaps, contradictions and self-claimed receiver ACK. **A source-level test declaration is not a test execution receipt.**

Suggested CI command (not claimed executed here):

```sh
python3 scripts/CoEvoPatternTransitionR0.py --selftest
```

Real promotion later requires a current-main rebase/suite result, exact proof of semantic improvement compared with existing CoListFabric/CoFlow selection, and a qualified independent outcome. Source publication or a PR by itself does not demonstrate better review decisions.

## What is measured

For a pinned evaluation window and same incoming deltas compare **with gate** versus **without gate**:

- false-green rate, valid hypotheses accidentally held and stale/duplicate rates;
- qualified useful receiver closures per eligible work hour (not raw commits);
- time to first independently useful experiment;
- novelty *after* source dedupe and independent challenge;
- falsifier coverage and prospective predictive calibration;
- uncovered interfaces, contradictions resolved, negative controls retained;
- total attention, cost, review latency, and human relay events;
- abandonment/retirement/wake quality.

Measure whether the gate itself becomes a bottleneck. If no outcome improves after comparable windows, downgrade, simplify or remove it. A candidate gate's survival is not a right.

## CoOrb projection

Default small panel: `MATERIAL CHANGE | REPEATED PATTERN? | CONTRADICTION | INVERSION | MISSING LINK | NEXT DISCRIMINATING TEST | RECEIVER / PERMISSION | WAKE`. Deep inspection exposes precise sources and nulls. No glow or visual prominence may imply execution, currentness or authority. Existing CoLivingHighlight may project a short reusable pattern card without creating an additional source of truth.

**Rails:** `POSSIBLE_PATTERN_NE_OBSERVED_LAW | PLACEHOLDER_NE_MEASUREMENT | SAME_SOURCE_NE_INDEPENDENCE | INVERSION_NE_BETTER | BETWEEN_NE_CAUSE | HYPOTHESIS_NE_EFFECT | MORE_QUESTIONS_NE_MORE_VALUE | FANOUT_PLAN_NE_DELIVERY | DELIVERY_NE_PICKUP | MERGE_NE_CANON | SOURCE_TEST_NE_RUNTIME | NO_RICK_RELAY_REQUIRED`.
