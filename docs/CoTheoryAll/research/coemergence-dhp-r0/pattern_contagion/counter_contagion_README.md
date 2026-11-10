# CoCounterContagion+ R0 | A correction must be allowed to challenge a cascade

**State:** `DRAFT_PUBLIC_SAFE_SYNTHETIC_SOURCE_ONLY__NO_RUNTIME_OR_COEX__NO_REAL_RECEIVER`.

This is a bounded **CoCounterSpread+ (PC-12)** research refinement on [CoPatternContagion R0](../pattern_contagion_r0.py) in [draft PR #445](https://github.com/CoCivium/CoCivium/pull/445). It is **not** a new root system, an automated moderation/influence service, or proof that a correction notice is true or has been accepted.

## Question

How much longer does an *unverified* claim circulate without a source-bound correction notice when the notice is delayed, compared to earlier propagation or no correction at all?

## Evidence design

- Two typed synthetic graphs contain an unverified claim flow and a distinct challenger notice flow. Original claim history is never erased.
- Each graph reuses the existing `pattern_contagion_r0.py` validator, including synthetic opt-out, edge authority `NONE`, and noise/tick budgets. Cross-graph nodes and permissions must match. A challenger cannot silently be the original claim's sole seed.
- All three scenarios run on exactly the same fixed graph: no correction, a notice beginning at tick 2, and one at tick 0.
- A notice reaching a node says nothing about whether its recipient read it, believed it, or whether either claim was correct. All such status fields remain `null`.
- There are three invented copies of the claim but just one declared source family. No independent corroboration is inferred.
- Time is synthetic *ticks*, not observed UTC or time travel. Backward explanation, prospective prediction and real causal claims are not made.

## Reproducible results

| Scenario | Uncorrected-exposure ticks | Receiver notice lag | Receiver ACK |
|---|---:|---|---|
| No correction | 27 | not reached | UNKNOWN |
| Delayed notice, tick 2 | 12 | 2 synthetic ticks | UNKNOWN |
| Early notice, tick 0 | 2 | 0 synthetic ticks | UNKNOWN |

This sum counts, at each simulated tick, exposed nodes without a synthetic correction notice. It is **not an effectiveness score**, evidence of social harm, evidence of human persuasion, or a reason to send unsolicited corrections. A notice can itself be mistaken; independent fact-finding and dissent remain separate.

## Product view and CI

`counterneedle.html` is a complete no-network, single-file HTML research prodlet with source-bound trace, three scenarios, accessible table, unknown-gauge boundaries and a held CoOomph status. It does not monitor real people or live infrastructure.

From this directory (containing the earlier `pattern_contagion_r0.py`):

```bash
python3 -m unittest -v test_counter_contagion_r0.py
python3 counter_contagion_r0.py counter_contagion_fixture.json > /tmp/counter_result.json
python3 build_counterneedle_r0.py --check
```

CI only runs these checks on source files, not real actors or devices. Source checks may pass when real impact is unknown.

## Where this belongs

- **CoWaveRelation+/CoCounterSpread+**: source-typed spread with negative/corrective waves and opt-out boundaries.
- **CoQuestionCommons+ / CoTheoryAll+**: every apparently successful spread raises the question 'who actually checked this, and what would change our mind?'
- **CoTime+**: preserve original exposure time and challenge-notice time separately; unknown real timestamps are `UNKNOWN`.
- **CoSpeedo+**: display synthetic activity, source family, correction gap, and uncertainty as separate, unblended needles. No independent receiver benefit is measured.
- **CoOomph+**: no effect or acceleration granted. `HOLD_EFFECTS_RESEARCH_ONLY`.
- **CoObject+/OVP+**: the readable offline prodlet is whole at its declared educational scale, without pretending to be a working distributed service.

## Counterfactual and negative tests

Test misreported authority, unqualified causal labels, altered rights across the two graphs, duplicate copies, invalid/late correction, fake acceptance, empty seeds, unmatched source families and missing cause/receiver information. Preserve the no-correction and early-correction alternatives even if the delayed policy looks good.

## Gates before stronger claims

1. Independent specialist review of established diffusion, corrections, cognitive bias, human factors and causal prior art.
2. Pre-registered, consented study with real independent reviewers, a strong normal correction baseline and no unauthorized messaging. Measure comprehension and actual downstream correction, including cases where a new notice makes things worse.
3. Real currentness, measured cost, independent evidence, privacy/rights review and alternative-no-action path.
4. Only then consider a read-only adapter to existing CoSpeedo. Any CoOomph effect still needs separately authenticated scope and authority.

**Rails:** `NOTICE_NE_TRUTH` · `DELIVERED_NE_ACCEPTED` · `SOURCE_COPIES_NE_INDEPENDENT_EVIDENCE` · `EARLIER_NE_ALWAYS_BETTER` · `SYNTHETIC_DELTA_NE_REAL_BENEFIT` · `SPEEDO_SOURCE_NE_LIVE_GAUGE` · `OOMPHEFFECT_NE_AUTOAUTHORITY`.