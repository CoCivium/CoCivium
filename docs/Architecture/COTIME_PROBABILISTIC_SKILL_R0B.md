# CoTime+ Probabilistic Skill / Baseline Comparison R0B

**State:** `SYNTHETIC_PROPER_SCORING_AND_BASELINE_COMPARISON__NO_REAL_PREDICTIVE_SKILL_NO_EFFECT_AUTHORITY`

## Purpose

A forecast system should not call itself useful merely because some predictions eventually look right.

R0B adds a harder question:

> did the precommitted probabilistic forecast beat a stated baseline under a proper scoring rule while retaining misses, unresolved cases and assumption-invalidated cases?

This extends the existing CoTime+ calibration and forecast-precommitment canaries rather than creating another prediction ontology.

## Proper scoring

R0B uses the Brier score for binary probabilistic forecasts.

Lower is better.

For probability `p` and binary outcome `y`:

```text
Brier = mean((p - y)^2)
```

The fixture stores probabilities as integer basis points so the validator can score them exactly with rational arithmetic.

`PROPER_SCORE_NE_TRUTH`

`LOWER_BRIER_SCORE_NE_CAUSAL_MODEL`

## Registered set

Eight forecasts are registered.

Six become resolved and valid for scoring.

Two remain visible but unscored:

- one unresolved outcome;
- one invalidated by assumption change.

They are not deleted merely because they complicate the scorecard.

`UNRESOLVED_NE_DELETE`

`INVALIDATED_NE_MISS`

## Synthetic comparison

For the six resolved cases:

```text
candidate CoTime model
  Brier = 29/300 ~= 0.0967

constant 50% baseline
  Brier = 1/4 = 0.25

inverted overconfident challenger
  Brier = 113/150 ~= 0.7533
```

The candidate's synthetic Brier skill relative to the 50% baseline is:

`46/75 ~= 0.6133`

This proves only that the fixture and scorer can distinguish a better-scoring probabilistic sequence from a baseline and a deliberately poor challenger.

It does **not** prove real-world predictive skill.

`SYNTHETIC_SKILL_NE_REAL_PREDICTIVE_SKILL`

`BETTER_THAN_BASELINE_IN_FIXTURE_NE_GENERALIZATION`

## Discrimination versus calibration

The candidate assigns higher mean probability to positive outcomes than negative outcomes in the fixture:

```text
positive outcomes: 7000 bp mean
negative outcomes: 3000 bp mean
```

That is synthetic discrimination.

It is not the same as calibration.

A model can rank outcomes well while probabilities remain badly calibrated, or be calibrated in aggregate while discriminating poorly.

`DISCRIMINATION_NE_CALIBRATION`

## Better-question compiler donation

Every predictive relation should increasingly ask:

1. What explicit baseline must this forecast beat?
2. Was it registered before the outcome was knowable?
3. What selection rule keeps misses, unresolved cases and invalidations visible?
4. Which proper scoring rule is used and why?
5. Does the model discriminate outcomes as well as calibrate probability?
6. What assumptions changed between registration and outcome?
7. What decision threshold, if any, depends on the forecast?
8. Would the apparent skill survive an external holdout set?

This is the important evolution from:

```text
"What do we predict?"
```

toward:

```text
"What would distinguish useful foresight from hindsight, confidence or luck?"
```

## CoInBet+ relation

Probabilistic prediction is itself an in-between relation.

A forecast may remain between:

- true and false;
- open and resolved;
- supported and contradicted;
- calibrated and uncalibrated;
- actionable and merely interesting.

CoInBet+ should preserve those intermediate states rather than coercing them into early binary labels.

## Effect boundary

No score, probability, confidence, or forecast creates authority.

This R0 performs no:

- financial trade;
- treasury allocation;
- public prediction;
- medical or neurological inference;
- paranormal claim;
- runtime mutation.

`FORECAST_SCORE_NE_EFFECT_AUTHORITY`

`FORECAST_SCORE_NE_FINANCIAL_ADVICE`

## Next frontier

The next meaningful proof is a **sealed holdout** or later real-world forecast set where the outcome was unavailable at registration and the baseline was fixed in advance.

Until then:

`REAL_PREDICTIVE_SKILL = UNPROVEN`

## Rails

`LOWER_BRIER_SCORE_NE_CAUSAL_MODEL`  
`SYNTHETIC_SKILL_NE_REAL_PREDICTIVE_SKILL`  
`BETTER_THAN_BASELINE_IN_FIXTURE_NE_GENERALIZATION`  
`PROPER_SCORE_NE_TRUTH`  
`HIGH_PROBABILITY_NE_HIGH_SKILL`  
`CONFIDENCE_NE_CALIBRATION`  
`DISCRIMINATION_NE_CALIBRATION`  
`UNRESOLVED_NE_DELETE`  
`INVALIDATED_NE_MISS`  
`FORECAST_SCORE_NE_EFFECT_AUTHORITY`  
`FORECAST_SCORE_NE_FINANCIAL_ADVICE`  
`VALIDATION_IS_NOT_ACCEPTANCE`
