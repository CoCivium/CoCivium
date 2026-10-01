# CoQuestion Selection Integrity R0

**State:** `SYNTHETIC_DISCRIMINATING_QUESTION_SELECTION__NO_EFFECT_AUTHORITY`

## Purpose

A system can preserve competing hypotheses and still bias itself by repeatedly asking only questions that favour the currently preferred explanation.

R0 therefore treats question election as an evidence-quality problem.

The preferred question is not the one most likely to confirm the current model. It is the one that most usefully separates live alternatives under the current evidence, cost, reversibility and authority constraints.

`QUESTION_SELECTION_NE_CONFIRMATION_SELECTION`

`PREFERRED_HYPOTHESIS_NE_PREFERRED_QUESTION`

## Candidate question envelope

A candidate question SHOULD bind:

- question ID;
- hypotheses or model states it discriminates;
- expected discriminatory value;
- whether it can falsify the currently preferred hypothesis;
- observation cost;
- reversibility;
- privacy / confidentiality impact;
- authority requirement;
- observer dependence;
- expected missingness risk;
- current evidence refs.

R0 uses ordinal synthetic values only. It does not claim a general information-theory optimizer.

`SYNTHETIC_INFORMATION_VALUE_NE_REAL_WORLD_INFORMATION_GAIN`

## Falsification coverage

If a preferred hypothesis exists, the selected set MUST include at least one eligible question capable of producing evidence against it whenever such a question exists.

`PREFERRED_MODEL_REQUIRES_FALSIFICATION_PATH`

A confirming-only question set is invalid when a bounded falsifying discriminator is available.

## Alternative coverage

Question election SHOULD preserve unresolved alternatives rather than repeatedly comparing the preferred model against a straw alternative.

`LIVE_ALTERNATIVE_NE_STRAW_MODEL`

Questions that discriminate among several still-live hypotheses may outrank highly confirmatory questions with little separating power.

## Cost, privacy and authority

High discriminatory value does not by itself authorize an observation or experiment.

A question may be ranked as scientifically useful while its execution remains blocked.

`QUESTION_VALUE_NE_OBSERVATION_AUTHORITY`

`QUESTION_SELECTION_NE_EFFECT_AUTHORITY`

The selector may therefore return:

- `SELECTABLE_NOW`
- `HIGH_VALUE_BUT_EFFECT_GATED`
- `HOLD_PRIVACY`
- `HOLD_AUTHORITY`
- `HOLD_COST`

## CoInBet+ relation

Some questions are valuable because they distinguish intermediate states rather than forcing a binary answer.

For example:

`SUPPORTED_CONTEXT_RELATION`

versus

`SUPPORTED_ATTENTION_RELATION`

versus

`UNKNOWN_OTHER`

may remain simultaneously live.

`DISCRIMINATION_NE_BINARY_COLLAPSE`

## First canary

The synthetic fixture proves:

1. a confirmation-only question is not elected when a bounded falsifying discriminator exists;
2. at least one elected question can falsify the preferred hypothesis;
3. unresolved alternatives receive coverage;
4. a high-value but effect-gated question remains unelected for execution;
5. a lower-cost bounded discriminator may be selected over an expensive near-equivalent;
6. question selection never changes effect authority;
7. question ordering is not evidence that the preferred hypothesis is true.

No experiment, medical interpretation, neurological claim, paranormal claim, financial effect, runtime mutation, canon or CoEx is authorized.

## Rails

`QUESTION_SELECTION_NE_CONFIRMATION_SELECTION`  
`PREFERRED_HYPOTHESIS_NE_PREFERRED_QUESTION`  
`PREFERRED_MODEL_REQUIRES_FALSIFICATION_PATH`  
`LIVE_ALTERNATIVE_NE_STRAW_MODEL`  
`QUESTION_VALUE_NE_OBSERVATION_AUTHORITY`  
`QUESTION_SELECTION_NE_EFFECT_AUTHORITY`  
`DISCRIMINATION_NE_BINARY_COLLAPSE`  
`QUESTION_ORDER_NE_HYPOTHESIS_TRUTH`  
`VALIDATION_IS_NOT_ACCEPTANCE`
