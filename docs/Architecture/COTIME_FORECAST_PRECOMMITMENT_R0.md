# CoTime Forecast Precommitment and Hindsight Guard R0

**State:** `SYNTHETIC_FORECAST_PRECOMMITMENT__NO_PREDICTIVE_ACCURACY_CLAIM_NO_EFFECT_AUTHORITY`

## Purpose

Calibration is meaningless if the forecast can be quietly rewritten after the outcome is known.

R0 therefore separates:

`FORECAST_REGISTRATION -> OUTCOME_OBSERVATION -> CALIBRATION`

and requires the registered forecast claim, horizon, assumptions, confidence and discriminating observation to remain addressable as historical evidence.

`POSTDICTION_NE_PREDICTION`

`OUTCOME_KNOWN_BEFORE_REGISTRATION_NE_VALID_FORECAST`

`FORECAST_EDIT_AFTER_OUTCOME_NE_CALIBRATION`

## Precommitment envelope

A registered forecast SHOULD bind:

- forecast ID;
- claim;
- epistemic class = PREDICTED;
- registered_at;
- horizon_end;
- assumptions;
- confidence;
- discriminating observation;
- source/provenance hash;
- calibration_due;
- effect authority = false.

The outcome is recorded separately.

`FORECAST_RECORD_NE_OUTCOME_RECORD`

## Hindsight guard

Calibration MUST compare the later outcome against the preserved registered forecast, not against a retrospectively improved paraphrase.

A later interpretation may supersede the old forecast for future use while the original remains historical evidence.

`SUPERSEDED_FORECAST_NE_ERASED_FORECAST`

`BETTER_LATER_MODEL_NE_BETTER_EARLIER_PREDICTION`

## Selective memory

A forecasting system MUST NOT report only memorable successes.

The calibration set should retain hits, misses, unresolved cases, censored cases and assumption-invalidated cases under the same selection rule.

`MEMORABLE_HIT_NE_CALIBRATED_SKILL`

`MISS_NE_DELETE`

`UNRESOLVED_NE_IGNORE`

## Confidence discipline

Confidence must be recorded before the outcome and must not be retroactively changed to improve calibration.

A confidence update belongs to a new forecast/version.

`CONFIDENCE_AFTER_OUTCOME_NE_PRECOMMITTED_CONFIDENCE`

## First canary

The synthetic canary proves:

1. registration before outcome is valid;
2. registration after outcome is rejected as postdiction;
3. mutating the claim after outcome invalidates calibration against the original forecast;
4. mutating confidence after outcome is rejected;
5. misses remain in the calibration set;
6. unresolved outcomes remain visible;
7. a superseding forecast creates a new ID/version instead of rewriting history.

No predictive skill, financial effect, neurological claim, paranormal claim, runtime adoption, canon or CoEx is established.

## Rails

`POSTDICTION_NE_PREDICTION`  
`OUTCOME_KNOWN_BEFORE_REGISTRATION_NE_VALID_FORECAST`  
`FORECAST_EDIT_AFTER_OUTCOME_NE_CALIBRATION`  
`FORECAST_RECORD_NE_OUTCOME_RECORD`  
`SUPERSEDED_FORECAST_NE_ERASED_FORECAST`  
`MEMORABLE_HIT_NE_CALIBRATED_SKILL`  
`CONFIDENCE_AFTER_OUTCOME_NE_PRECOMMITTED_CONFIDENCE`  
`PREDICTION_NE_EVIDENCE`  
`VALIDATION_IS_NOT_ACCEPTANCE`
