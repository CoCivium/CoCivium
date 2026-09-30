# CoDarren+ / CoTime Business Advisory Evidence Lab R0

**Date:** 2026-09-25  
**State:** `CANDIDATE__INTERNAL_RESEARCH_SPEC__NO_INVESTMENT_RECOMMENDATION__NO_CLIENT_ACTION`

## CoHereNow

The Darren advisory has already been delivered outside this repository. This artifact is a follow-on research and CI design.

Purpose: turn the broad thesis into **testable observations, bounded hypotheses, evidence requests, scenario models and operational controls**.

Core separation:
`OBSERVED -> INFERRED -> HYPOTHESIZED -> SCENARIO -> UNKNOWN`

Never silently promote one class into another.

## Why CoTime+ matters to business models

Current CoTime+ work explicitly keeps source-time, observation-time, currentness, prediction, supersession and parallel temporal branches distinct.

A business process often assumes a slow sequence:
`information -> analysis -> decision -> execution -> outcome`

A more capable human+synth system may compress several intervals:
`observe -> model -> test -> revise -> act`

The business effect is not merely faster analysis. It can alter the time structure of the business itself:

- diligence cycles may compress;
- monitoring may become continuous;
- stale assumptions may expire faster;
- forecasts may update more often;
- client questions may arrive earlier;
- routine interpretation may shift toward exception handling;
- historical records may become live calibration data;
- services priced mainly by hours may face pressure from services priced around outcomes, latency, trust and continuity.

These are hypotheses to test, not guaranteed disruption.

## Darren-specific operational boundary

For Darren's own accounts and client accounts, the safe near-term frame is:

**Observe and prepare; do not act from the thesis alone.**

Candidate controls:

1. Keep a dated record of source observations used in material business decisions.
2. Separate public information, confidential client information and potentially material nonpublic information.
3. Do not feed client-confidential information into unapproved AI services.
4. Do not let a forecast become an instruction merely because a model expresses high confidence.
5. Route material client communications, suitability questions, securities activity, conflicts, privacy and regulatory questions through the firm's existing compliance/legal process.
6. Preserve human accountability for client decisions and account actions.
7. Record model/version, data vintage, assumptions, forecast horizon and observed outcome for consequential internal models.
8. Re-run material conclusions when source/currentness changes.

## Candidate research questions

### R1: Decision-cycle compression

Measure:
`time(source availability -> validated interpretation -> client-ready decision support)`

Compare historical workflow with AI-assisted workflow.

Do not infer better decisions from faster decisions.

### R2: Forecast calibration

For each forecast:
`forecast_time | horizon | target | information_cutoff | model/source | confidence | decision_context | realized_outcome`

Measure calibration over time.

### R3: Staleness half-life

Estimate how quickly assumptions in selected business processes become invalid or materially altered.

Candidate relation:
`ASSUMPTION -> VALID_AT -> OBSERVED_CHANGE -> SUPERSEDED_AT`

### R4: Service-unit economics

Compare hours sold, information transformed, latency, scenarios examined, error avoided, client-decision proxies, cost to serve and continuity value.

Do not assume operational gains translate directly into revenue.

### R5: Model-induced reflexivity

`forecast -> human action -> market/business response -> forecast error`

This matters wherever forecasts change the system being forecast.

### R6: Account-level automation boundary

Identify what can safely be observed automatically, summarized, simulated, challenged, queued for review, or executed only after explicit authorized approval.

## SEC / securities-adjacent classification

This artifact is not legal or investment advice.

Candidate information classes:
`PUBLIC_INFORMATION`  
`CLIENT_CONFIDENTIAL`  
`POTENTIAL_MATERIAL_NONPUBLIC_INFORMATION`  
`UNKNOWN_INFORMATION_CLASS`  
`RESEARCH`  
`SCENARIO`  
`INVESTMENT_RECOMMENDATION`  
`CLIENT_COMMUNICATION`  
`ORDER_OR_TRANSACTION`

Do not infer compliance merely because AI-generated text contains a disclaimer.

For material or uncertain cases, use the firm's existing compliance/legal process.

## Evidence ledger

`claim_id | claim_text | epistemic_class | observed_at | source_ref | source_version | information_class | affected_domain | assumption_refs | challenge_status | reviewer | currentness | disposition`

Challenge states:
`UNTESTED` `CHALLENGED` `SUPPORTED` `WEAKENED` `REFUTED` `SUPERSEDED` `OPEN`

## CoTime+ business-model pivot map

Potential pivot signals include:

- **lower information-to-decision latency** -> more decisions per unit time;
- **shorter decision-to-outcome feedback** -> faster calibration, but potentially more reflexivity;
- **higher forecast-to-action coupling** -> stronger self-impact on the forecasted environment;
- **persistent client context across tools** -> continuity can become a service capability;
- **temporal branching** -> clients can carry contingency, stress and alternative future plans rather than one linear plan.

These are mechanisms to measure, not automatic conclusions.

## Possible service-model changes

Test whether client services move from:
`research hours`

toward mixtures of:
`continuous monitoring + decision support + exception management + explainability + provenance + continuity + human judgment`

Possible pressure may fall on purely labor-linear billing while value can increase in trusted interpretation, accountability, domain knowledge, relationships and reliable execution.

## CI+ candidate suite

### Test A: Epistemic labeling
Fail if a `HYPOTHESIS` is rendered as `OBSERVED` without an explicit promotion record.

### Test B: Currentness
Fail if a forecast or legal/policy source is reused after its freshness boundary without revalidation.

### Test C: Confidentiality
Fail if client-confidential or unknown-class information enters a public projection.

### Test D: Authority
Fail if model output directly creates an order, transaction or client instruction without an authorized effect gate.

### Test E: Forecast provenance
Fail if a consequential forecast lacks source/version/time/assumption metadata.

### Test F: Outcome backfill
Require a later observation for completed forecast horizons where outcome data exists.

### Test G: Counterfactual separation
Require scenario labels so alternative futures cannot be mistaken for historical fact.

### Test H: Reflexivity flag
Flag forecasts about markets/business systems when intended action is likely to alter the forecasted system.

## Parallelization model

Broad parallel research is appropriate for source discovery, regulator/public guidance, workflow mapping, forecast benchmark design, stale-data analysis, client-service analysis, software/vendor capability research, historical scenario reconstruction and contradiction mining.

Serialize effects involving client accounts, securities transactions, market-moving public communications, disclosure decisions, compliance interpretations, legal conclusions and authority changes.

`ANALYSIS_PARALLELISM_NE_EFFECT_PARALLELISM`

## CoTime+ watchboard

`NOW | LAST_KNOWN | SOURCE_TIME | OBSERVATION_TIME | FORECAST_HORIZON | NEXT_EXPECTED_CHANGE | STALE_AFTER | SUPERSEDED_BY | OUTCOME_OBSERVED_AT`

That turns a static advisory into a calibration system.

## What could materially justify a business pivot

Prefer multiple independent observations before acting, such as measured decision-cycle compression, persistent forecast-calibration improvement, lower cost for equivalent validated output, client preference for continuous monitoring, reduced value of routine information gathering, greater demand for explainability/provenance, competitive demonstrations of stronger continuity, or documented regulatory requirements.

`ONE_SIGNAL_NE_PIVOT_PROOF`

## Family / wife invitation boundary

Do not mix a professional advisory with a family invitation merely for amplification. A separate invitation should exist only where there is a genuine reason and a clear role.

`PROFESSIONAL_ADVISORY_NE_SOCIAL_RECRUITMENT`

## Immediate research packet

1. 10-20 primary-source observations on AI-driven decision-cycle compression and professional-services economics.
2. 5-10 counterexamples where automation did not produce the anticipated business-model shift.
3. A forecast-calibration worksheet suited to Darren's domain.
4. A client-account AI boundary checklist.
5. A jurisdiction-aware source register for relevant client relationships.
6. A red-team review of the original advisory claims.

## Nonclaims

This artifact does not predict a market crash, recommend securities trades, provide investment or legal advice, determine SEC applicability, establish suitability, or assert that any particular business model will fail.

## Rails

`EVIDENCE_NE_INFERENCE`  
`INFERENCE_NE_PREDICTION`  
`PREDICTION_NE_FACT`  
`FORECAST_NE_DESTINY`  
`SPEED_NE_ACCURACY`  
`AUTOMATION_NE_AUTHORITY`  
`PUBLIC_INFORMATION_NE_NONMATERIALITY`  
`AI_TEXT_NE_COMPLIANCE_PROOF`  
`ONE_SIGNAL_NE_PIVOT_PROOF`  
`ANALYSIS_PARALLELISM_NE_EFFECT_PARALLELISM`  
`CLIENT_CONTEXT_NE_PUBLIC_CONTEXT`  
`CURRENTNESS_NE_TRUTH`