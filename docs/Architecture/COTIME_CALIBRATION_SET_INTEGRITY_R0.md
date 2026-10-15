# CoTime Calibration-Set Integrity R0

**State:** `SYNTHETIC_CALIBRATION_SET_INTEGRITY__NO_PREDICTIVE_ACCURACY_CLAIM_NO_EFFECT_AUTHORITY`

## Purpose

A forecast registry can still cheat even when each forecast is precommitted correctly.

If the system later calibrates only easy, memorable, favourable, or observable forecasts, the resulting score is misleading.

R0 therefore treats **forecast selection into the calibration set** as its own evidence problem.

`REGISTERED_FORECAST_NE_CALIBRATED_FORECAST`

`CALIBRATION_SET_NE_CONVENIENCE_SAMPLE`

## Registry discipline

Every registered forecast in scope should later receive one of:

- `HIT`
- `PARTIAL`
- `MISS`
- `UNRESOLVED`
- `CENSORED`
- `INVALIDATED_BY_ASSUMPTION_CHANGE`

or an explicit bounded reason why calibration is not yet due.

Forecasts must not disappear merely because:

- the outcome is expensive to observe;
- the result is embarrassing;
- the signal was weak;
- a different observer owns the outcome;
- the forecast was superseded;
- the forecast became operationally irrelevant.

`MISS_NE_DELETE`

`UNRESOLVED_NE_DROP`

`CENSORED_NE_SUCCESS`

`SUPERSEDED_NE_EXEMPT_FROM_HISTORY`

## Missingness

Missing outcome data is itself typed.

Candidate missingness classes:

- `NOT_YET_DUE`
- `OBSERVATION_UNAVAILABLE`
- `OBSERVATION_TOO_COSTLY`
- `OUTCOME_AMBIGUOUS`
- `RECEIVER_UNREACHABLE`
- `CENSORED_BY_POLICY`
- `SOURCE_LOST`
- `UNKNOWN_MISSINGNESS`

Missingness does not silently convert to success, failure, or exclusion.

`MISSING_OUTCOME_NE_MISS`

`MISSING_OUTCOME_NE_HIT`

`MISSING_OUTCOME_NE_EXCLUSION_PERMISSION`

## Calibration-set receipt

A calibration pass SHOULD report:

- registered forecast count;
- due forecast count;
- calibrated count;
- unresolved count;
- censored count;
- not-yet-due count;
- invalidated count;
- excluded count;
- explicit exclusion reasons;
- source registry digest;
- calibration policy version.

The dangerous value is unexplained exclusion.

`EXCLUSION_REQUIRES_REASON`

`ZERO_EXPLAINED_EXCLUSION_NE_COMPLETE_WORLD_COVERAGE`

## Selective-observation bias

Forecasts whose outcomes are easy to observe may dominate the calibration set.

R0 therefore requires the system to preserve a distinction between:

`CALIBRATION_PERFORMANCE_ON_OBSERVED_SET`

and

`PREDICTIVE_PERFORMANCE_OVER_REGISTERED_SET`

The latter remains unknown when observation coverage is incomplete.

`OBSERVED_SET_PERFORMANCE_NE_REGISTERED_SET_PERFORMANCE`

## First canary

The synthetic fixture proves:

1. all due registered forecasts remain addressable;
2. hits and misses both remain;
3. unresolved forecasts remain;
4. censored forecasts remain;
5. not-yet-due forecasts are not falsely calibrated;
6. unexplained exclusion fails;
7. observed-subset performance is not relabelled as full-registry performance.

No predictive skill, financial effect, neurological claim, paranormal claim, runtime adoption, canon or CoEx is established.

## Rails

`REGISTERED_FORECAST_NE_CALIBRATED_FORECAST`  
`CALIBRATION_SET_NE_CONVENIENCE_SAMPLE`  
`MISS_NE_DELETE`  
`UNRESOLVED_NE_DROP`  
`CENSORED_NE_SUCCESS`  
`MISSING_OUTCOME_NE_EXCLUSION_PERMISSION`  
`EXCLUSION_REQUIRES_REASON`  
`OBSERVED_SET_PERFORMANCE_NE_REGISTERED_SET_PERFORMANCE`  
`PREDICTION_NE_EVIDENCE`  
`VALIDATION_IS_NOT_ACCEPTANCE`
