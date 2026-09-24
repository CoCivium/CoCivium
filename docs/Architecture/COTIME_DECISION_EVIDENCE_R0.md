# CoTime+ Decision Evidence R0

**Date:** 2026-09-24  
**State:** `CANDIDATE__BRANCH_ONLY__NO_CANON_RUNTIME_OR_EXTERNAL_EFFECT`

## Lead

CoTime+ turns a static advisory statement into a versioned decision-support relation.

A useful object keeps distinct:

`source-time | observation-time | recorded-time | valid-time | inference-time | forecast-horizon | currentness | supersession | calibration`

The general pattern applies to professional advice, research, governance, law, operations, security, medicine, finance and other domains where decisions can become wrong simply because an old statement is silently treated as current.

## Core relation

`source event -> observation -> evidence class -> interpretation -> scenario/forecast -> bounded decision support -> currentness watch -> material delta -> review -> supersession/calibration`

The objective is not faster action by default. It is better evidence-qualified, time-aware judgment.

## Epistemic classes

- `OBSERVED`
- `INFERRED`
- `PREDICTED`
- `SCENARIO`
- `COUNTERFACTUAL`
- `UNKNOWN`

`PREDICTION_NE_EVIDENCE`  
`FORECAST_NE_FUTURE_FACT`  
`SCENARIO_NE_PREDICTION`

## Time fields

Candidate fields include:

- source_time
- observed_at
- recorded_at
- valid_from
- valid_to
- decision_time
- horizon_end
- calibration_due
- supersedes
- expires_at

`OBSERVATION_TIME_NE_EVENT_TIME`  
`LATEST_NE_CURRENT_FOR_PURPOSE`

## Currentness states

- `CURRENT`
- `STALE`
- `SUPERSEDED`
- `UNKNOWN`

A stale or superseded object remains historical evidence but should not silently drive a new effect.

## Decision-support classes

- `RESEARCH_ONLY`
- `PRIVATE_DISCUSSION`
- `PROFESSIONAL_REVIEW_TRIGGER`
- `DECISION_CANDIDATE`
- `EFFECT_GATED`

R0 does not authorize external effects.

`ANALYSIS_NE_EFFECT_AUTHORITY`  
`REVIEW_TRIGGER_NE_DECISION`

## Professional-account/client relation

Where a regulated professional applies this pattern to a real account or client, the system should preserve role, jurisdiction, information classification, scope, conflicts, authority, disclosure and professional-review requirements separately from the analytic thesis.

No job title or conversational context should be treated as proof of regulatory status.

`ROLE_GUESS_NE_REGULATORY_STATUS`

## Forecast calibration

Forecasts should be revisited and classified as:

- `HIT`
- `PARTIAL`
- `MISS`
- `UNRESOLVED`
- `CENSORED`
- `INVALIDATED_BY_ASSUMPTION_CHANGE`

This turns prediction from rhetoric into a measurable CoTime relation.

`MEMORABLE_PREDICTION_NE_CALIBRATED_FORECASTER`

## Business-model implication

A CoTime-aware professional service can move from periodic static reports toward maintaining a living decision relationship:

- versioned thesis;
- provenance ledger;
- material-delta alerts;
- scenario history;
- counterargument register;
- currentness state;
- supersession history;
- forecast calibration;
- review triggers;
- explicit decision/effect receipts.

The valuable product becomes less "I possess information" and more "I maintain high-quality current decision context."

## Massive-parallel research

Low-authority work can parallelize aggressively:

- source discovery;
- currentness checking;
- claim extraction;
- counterarguments;
- scenario generation;
- historical analogs;
- contradiction detection;
- calibration;
- jurisdiction/source mapping;
- stale-assumption detection.

Fan-in remains bounded. Authority does not parallelize merely because research does.

`PARALLEL_RESEARCH_NE_PARALLEL_AUTHORITY`

## CI+ direction

CI can test that:

- predictions are not typed as observations;
- stale state cannot silently become current;
- forecasts include calibration hooks;
- supersession remains explicit;
- effect-gated objects do not gain authority from model output;
- missing role/jurisdiction/currentness becomes a hold, not a guess.

CI cannot establish legal correctness, professional suitability, substantive merit or future accuracy.

`CI_PASS_NE_SUBSTANTIVE_CORRECTNESS`

## Recipient-feedback loop

After an evidence pack is delivered:

`recipient reads -> questions/challenges -> typed feedback -> evidence/scenario revision -> concise delta`

Do not send another large packet merely because internal research continued.

## Nonclaims

This R0 is not professional advice, legal advice, investment advice, medical advice, a prediction of future fact, runtime, canon or an external decision.

## Rails

`ADVICE_NE_TIMELESS_FACT`  
`PREDICTION_NE_EVIDENCE`  
`FORECAST_NE_FUTURE_FACT`  
`SCENARIO_NE_PREDICTION`  
`OBSERVATION_TIME_NE_EVENT_TIME`  
`LATEST_NE_CURRENT_FOR_PURPOSE`  
`ANALYSIS_NE_EFFECT_AUTHORITY`  
`REVIEW_TRIGGER_NE_DECISION`  
`ROLE_GUESS_NE_REGULATORY_STATUS`  
`MEMORABLE_PREDICTION_NE_CALIBRATED_FORECASTER`  
`PARALLEL_RESEARCH_NE_PARALLEL_AUTHORITY`  
`CI_PASS_NE_SUBSTANTIVE_CORRECTNESS`
