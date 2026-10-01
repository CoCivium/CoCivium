# CoTime Predictive Calibration Canary R0

**State:** `SYNTHETIC_FORECAST_CALIBRATION__NO_PREDICTIVE_ACCURACY_CLAIM_NO_EFFECT_AUTHORITY`

## Purpose

The CoInBet / CoTime candidate already says forecasts need calibration. This R0 makes that requirement executable instead of leaving it as attractive prose.

A forecast object binds:

`forecast_id | claim | epistemic_class | observer | horizon_end | assumptions | confidence | calibration_due | discriminating_observation | outcome | calibration_disposition`

Allowed dispositions reuse existing CoTime+ semantics:

`HIT | PARTIAL | MISS | UNRESOLVED | CENSORED | INVALIDATED_BY_ASSUMPTION_CHANGE`

## In-between forecast states

Before calibration, a forecast may be:

`OPEN`
`AWAITING_OBSERVATION`
`EVIDENCE_PARTIAL`
`ASSUMPTION_DRIFTED`

These are CoInBet-style states. They do not force an early binary success/failure judgment.

`UNCALIBRATED_NE_WRONG`

`PARTIAL_EVIDENCE_NE_PARTIAL_HIT_BY_DEFAULT`

## Preparation

A forecast may produce a reversible preparation candidate, but preparation remains separately authority-gated.

`FORECAST_NE_COMMAND`

`PREPARATION_NE_EXECUTION_AUTHORITY`

## First canary

The fixture proves:

1. a forecast cannot masquerade as OBSERVED;
2. every forecast has a calibration due point and discriminating observation;
3. a matching outcome can calibrate HIT;
4. a contradictory outcome can calibrate MISS;
5. mixed evidence can remain UNRESOLVED;
6. assumption change can invalidate calibration without rewriting the original forecast;
7. reversible preparation does not change effect authority.

No predictive skill, neurological mechanism, financial merit, trade, treasury action, runtime adoption, canon, or CoEx is claimed.

## Rails

`PREDICTION_NE_EVIDENCE`  
`FORECAST_NE_FUTURE_FACT`  
`UNCALIBRATED_NE_WRONG`  
`PARTIAL_EVIDENCE_NE_PARTIAL_HIT_BY_DEFAULT`  
`ASSUMPTION_CHANGE_NE_FORECAST_ERASURE`  
`PREPARATION_NE_EXECUTION_AUTHORITY`  
`CALIBRATION_NE_CAUSAL_PROOF`  
`VALIDATION_IS_NOT_ACCEPTANCE`
