# CoTime+ Advisory Evidence R0

**Date:** 2026-09-24  
**State:** `CANDIDATE__BRANCH_ONLY__NO_CANON_RUNTIME_CLIENT_ADVICE_TRADE_OR_PUBLICATION_EFFECT`

## Lead

CoTime+ materially changes advisory work because advice is not one timeless sentence.

A useful advisory object should preserve:

`what was known | when it happened | when it was observed | when it became valid | what was inferred | what was forecast | what decision horizon applied | what later superseded it | how the forecast calibrated`

This is useful in finance, law, medicine, operations, governance, security, research and other fields where decisions degrade when old information is silently treated as current.

`ADVICE_NE_TIMELESS_FACT`  
`PREDICTION_NE_EVIDENCE`  
`CURRENTNESS_NE_RECENCY_ALONE`

## CoTime+ pivot

Traditional advisory products often look like:

`periodic meeting -> static report -> recommendation -> next periodic meeting`

A CoTime-aware model can instead become:

`source event -> observation -> evidence classification -> bounded interpretation -> scenario/forecast -> decision-support state -> currentness watch -> material delta -> review -> supersession/calibration`

The commercial/product implication is not "trade faster."

It is **maintain a better versioned relationship with evidence and uncertainty**.

Candidate service shift:

- from static report to living decision record;
- from annual/quarterly snapshot to event-aware review;
- from recommendation text to provenance-bound reasoning;
- from hidden model confidence to explicit uncertainty;
- from forgotten forecasts to later calibration;
- from newest-wins to supersession history;
- from one client clock to client-specific horizons and constraints;
- from generic alerts to materiality/currentness triggers;
- from adviser memory to auditable evidence lineage.

## Epistemic classes

Every material claim should carry one class:

- `OBSERVED`
- `INFERRED`
- `PREDICTED`
- `SCENARIO`
- `COUNTERFACTUAL`
- `UNKNOWN`

A prediction may be useful without being evidence.

A scenario may be decision-relevant without claiming probability.

`FORECAST_NE_FUTURE_FACT`  
`SCENARIO_NE_PREDICTION`

## Time envelope

Candidate fields:

- `source_time`: when the underlying event/fact occurred;
- `observed_at`: when this receiver learned it;
- `recorded_at`: when the object entered the evidence system;
- `valid_from` / `valid_to`: known applicability interval;
- `decision_time`: when a decision-support state was produced;
- `horizon_end`: relevant decision/forecast horizon;
- `calibration_due`: when a forecast should be compared with outcomes;
- `supersedes`: prior advisory/evidence object displaced for scope;
- `expires_at`: hard currentness boundary where appropriate.

`OBSERVATION_TIME_NE_EVENT_TIME`  
`LATEST_NE_CURRENT_FOR_PURPOSE`

## Information-class gate

For securities-sensitive work, information state should be explicit before any client/account action.

Candidate classes:

- `PUBLIC_INFORMATION`
- `PRIVATE_INFORMATION__MATERIALITY_NOT_ESTABLISHED`
- `POTENTIALLY_MATERIAL_NONPUBLIC_INFORMATION`
- `UNKNOWN_INFORMATION_CLASS`

This is a routing classification, not a final legal determination.

`PUBLIC_SOURCE_NE_IMMATERIAL_INFORMATION`  
`INFORMATION_CLASS_NE_LEGAL_CONCLUSION`

If information is potentially material/nonpublic or its class is unknown, any securities transaction/recommendation route should be held for qualified compliance/legal review.

## Action classes

Candidate action classes:

- `RESEARCH_ONLY`
- `PRIVATE_DISCUSSION`
- `CLIENT_DISCUSSION`
- `PORTFOLIO_REVIEW_TRIGGER`
- `SECURITIES_TRANSACTION_RECOMMENDATION`
- `TRADE_EXECUTION`

R0 never authorizes trade execution.

`ANALYSIS_NE_TRADE_AUTHORITY`  
`MODEL_OUTPUT_NE_CLIENT_RECOMMENDATION`

## Account/client strategy pattern

For a specific account or client relationship, a safe CoTime+ strategy is a **review protocol**, not an automatic prediction-to-trade pipeline.

Candidate loop:

1. bind client/account scope and authority;
2. bind current public and permitted private evidence;
3. classify claim epistemics;
4. bind time/horizon/currentness;
5. generate multiple scenarios and counterarguments;
6. identify material deltas since last acknowledged review;
7. preserve conflicts and unknowns;
8. produce a review trigger, not a trade;
9. route through the responsible regulated/professional human where required;
10. record the resulting human/client decision separately from the model analysis;
11. later calibrate forecasts and assumptions.

`REVIEW_TRIGGER_NE_RECOMMENDATION`  
`RECOMMENDATION_NE_EXECUTION`

## Regulatory-profile gate

The same content may have different consequences depending on whether the recipient is, for example:

- an unregulated private individual;
- an SEC-registered investment adviser;
- a broker-dealer representative;
- a Canadian registrant;
- an institutional fiduciary;
- another regulated professional.

Therefore R0 uses:

`REGULATORY_PROFILE_UNKNOWN -> HOLD_EFFECTFUL_FINANCIAL_ACTION`

No model should infer a person's regulatory status from job title, conversation style or relationship.

`ROLE_GUESS_NE_REGULATORY_STATUS`

## SEC relationals

Where US securities regulation is actually applicable, useful primary-source anchors include:

- SEC 2019 Commission Interpretation Regarding Standard of Conduct for Investment Advisers;
- Regulation Best Interest / Form CRS rulemaking package;
- SEC enforcement showing that false or misleading claims about use of AI can create securities-law/compliance exposure.

These sources support operational gates around duty, disclosure, conflicts and accuracy of AI-related representations.

They do not establish which regime applies to a particular recipient without role/jurisdiction facts.

Primary sources:

- https://www.sec.gov/rules-regulations/2019/06/ia-5248
- https://www.sec.gov/newsroom/press-releases/2019-89
- https://www.sec.gov/newsroom/press-releases/2024-36

`SEC_SOURCE_NE_SEC_APPLICABILITY_TO_THIS_PERSON`

## Forecast discipline

A forecast object should preserve:

`forecast_id | claim | source_refs | assumptions | confidence | horizon | observation_time | calibration_due | outcome | calibration_disposition`

Candidate calibration dispositions inherited from CoTime+:

- `HIT`
- `PARTIAL`
- `MISS`
- `UNRESOLVED`
- `CENSORED`
- `INVALIDATED_BY_ASSUMPTION_CHANGE`

This makes "I called it" less important than measured forecasting skill.

`MEMORABLE_PREDICTION_NE_CALIBRATED_FORECASTER`

## Business-model implication

CoTime+ can pivot many advisory businesses from selling periodic information toward maintaining **current, accountable decision context**.

Potential product capabilities:

- currentness dashboard;
- versioned thesis;
- client-specific horizon map;
- source/provenance ledger;
- scenario tree;
- supersession history;
- forecast calibration;
- material-delta alerts;
- conflict/assumption register;
- disclosure/compliance gate;
- meeting-prep digest;
- post-decision learning loop.

The valuable service becomes less "I possess information you do not" and more:

> I maintain a high-quality, time-aware, evidence-qualified decision relationship with you.

That thesis applies outside finance as well.

## Massive-parallel research posture

High-volume work is appropriate for low-authority research tasks such as:

- source discovery;
- source-currentness checks;
- claim extraction;
- counterargument generation;
- scenario generation;
- historical analog retrieval;
- forecast calibration;
- contradiction detection;
- jurisdiction/source mapping;
- stale-assumption discovery.

Fan-in remains bounded.

Effectful client/account actions remain serialized behind authority/compliance gates.

`PARALLEL_RESEARCH_NE_PARALLEL_AUTHORITY`  
`MORE_SCENARIOS_NE_MORE_TRUTH`

## CI+ posture

CI should verify structural and semantic rails such as:

- predictions are not typed as observations;
- stale evidence cannot silently authorize an effectful route;
- potentially material/nonpublic or unknown information cannot flow directly to recommendation/trade;
- unknown regulatory profile blocks effectful financial actions;
- client-specific action requires explicit responsible-human/professional review;
- trade execution is not an R0 output;
- forecast objects include calibration hooks;
- superseded advice remains historically addressable.

CI cannot determine legal correctness, suitability, fiduciary compliance or investment quality.

`CI_PASS_NE_LEGAL_COMPLIANCE`  
`CI_PASS_NE_SUITABILITY`  
`CI_PASS_NE_INVESTMENT_MERIT`

## Outreach posture

After a recipient has received an evidence pack, do not immediately bury them under another one.

Prefer:

`recipient reads -> questions/challenges -> classify feedback -> update evidence/scenarios -> issue concise delta`

No additional outreach should be inferred merely because new internal research exists.

## Nonclaims

This R0 does not establish:

- investment advice;
- legal advice;
- client suitability;
- SEC/FINRA/CIRO or other regulatory applicability to any named person;
- authority over any account;
- a recommendation to buy, sell or hold any security;
- predictive accuracy;
- canon;
- runtime;
- public release.

## Rails

`ADVICE_NE_TIMELESS_FACT`  
`PREDICTION_NE_EVIDENCE`  
`FORECAST_NE_FUTURE_FACT`  
`SCENARIO_NE_PREDICTION`  
`OBSERVATION_TIME_NE_EVENT_TIME`  
`LATEST_NE_CURRENT_FOR_PURPOSE`  
`PUBLIC_SOURCE_NE_IMMATERIAL_INFORMATION`  
`INFORMATION_CLASS_NE_LEGAL_CONCLUSION`  
`ANALYSIS_NE_TRADE_AUTHORITY`  
`MODEL_OUTPUT_NE_CLIENT_RECOMMENDATION`  
`REVIEW_TRIGGER_NE_RECOMMENDATION`  
`RECOMMENDATION_NE_EXECUTION`  
`ROLE_GUESS_NE_REGULATORY_STATUS`  
`SEC_SOURCE_NE_SEC_APPLICABILITY_TO_THIS_PERSON`  
`MEMORABLE_PREDICTION_NE_CALIBRATED_FORECASTER`  
`PARALLEL_RESEARCH_NE_PARALLEL_AUTHORITY`  
`CI_PASS_NE_LEGAL_COMPLIANCE`
