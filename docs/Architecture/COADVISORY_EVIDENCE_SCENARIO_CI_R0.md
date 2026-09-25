# CoAdvisory Evidence / Scenario CI R0

**Date:** 2026-09-24
**State:** `CANDIDATE__BRANCH_ONLY__NO_INVESTMENT_OR_LEGAL_DECISION`

## Purpose

After a private advisory has been delivered, CoAll should be able to convert the underlying reasoning into a reusable evidence-and-scenario pipeline rather than leaving it as one persuasive document.

The pipeline keeps four epistemic layers separate:

- `OBSERVED`: sourced or directly reproducible observation.
- `INFERRED`: reasoning that follows from observations and stated assumptions.
- `HYPOTHESIS`: proposition requiring future testing or evidence.
- `SCENARIO`: conditional future possibility, not a prediction of fact.

`EVIDENCE_NE_INFERENCE`
`INFERENCE_NE_PREDICTION`
`PREDICTION_NE_FACT`
`SCENARIO_NE_FORECAST_CERTAINTY`

## Why this matters

A large advisory can be useful to a professional without becoming an instruction to trade, invest, litigate, evade regulation, or act on unverified claims.

Every major proposition should therefore carry:

`claim_id | class | statement | source_refs | assumptions | counterarguments | uncertainty | falsifier | time_horizon | affected_domains | materiality_flag | publication_scope`

## CoTime+ relation

CoTime+ already distinguishes source-time, observation-time, currentness, prediction and supersession.

Advisory scenarios should inherit that discipline:

- source time;
- observation time;
- scenario creation time;
- target horizon;
- review time;
- outcome time;
- superseding evidence;
- calibration outcome.

`SCENARIO_TIME_NE_EVENT_TIME`
`PREDICTION_NE_FUTURE_FACT`

## Financial / securities safety layer

For material touching investments or securities, retain a separate classification:

- `GENERAL_MACRO_SCENARIO`
- `GENERAL_BUSINESS_IMPLICATION`
- `ISSUER_SPECIFIC_ANALYSIS`
- `SECURITIES_SPECIFIC`
- `INVESTMENT_RECOMMENDATION`
- `UNKNOWN_FINANCIAL_SCOPE`

This is a classification rail, not a legal conclusion.

The SEC Investment Adviser Marketing Rule regulates certain advertisements by covered investment advisers and places conditions around hypothetical performance and other performance presentations. The SEC also distinguishes material nonpublic information from broadly disseminated public information. Applicability depends on facts, audience, role and context, so the system should route uncertainty to qualified human review rather than declare content "SEC-safe."

Primary sources:
- SEC Investment Adviser Marketing: https://www.sec.gov/resources-small-businesses/small-business-compliance-guides/investment-adviser-marketing
- SEC Marketing Compliance FAQs: https://www.sec.gov/rules-regulations/staff-guidance/division-investment-management-frequently-asked-questions/marketing-compliance
- SEC Insider Trading Arrangements and Related Disclosures: https://www.sec.gov/rules-regulations/2022/12/insider-trading-arrangements-related-disclosures

`SEC_CLASSIFICATION_NE_LEGAL_CONCLUSION`
`PUBLIC_INFORMATION_NE_AUTOMATICALLY_IMMATERIAL`
`HYPOTHETICAL_NE_PERFORMANCE_RESULT`

## Client/account boundary

An advisory can distinguish:

`CLIENT_FACT`
`CLIENT_OBJECTIVE`
`PUBLIC_MARKET_FACT`
`MODEL_SCENARIO`
`ACCOUNT_SPECIFIC_ACTION`

No scenario engine should silently turn a speculative macro view into an account-specific transaction.

Candidate gate:

`ACCOUNT_ACTION_REQUIRED -> EXPLICIT_AUTHORIZED_HUMAN_REVIEW`

## Scenario construction

For each scenario:

1. bind observations;
2. state assumptions;
3. produce a conditional chain;
4. list alternative explanations;
5. identify discriminating observations;
6. define time horizon;
7. define falsifiers;
8. record uncertainty;
9. define safe monitoring indicators;
10. stop before account-specific action unless separately authorized and reviewed.

## Scenario set for AI / software transition

Candidate scenarios include:

- software opacity becomes a weaker competitive moat;
- platform dependence becomes more costly as portable alternatives improve;
- AI-enabled compatibility work lowers migration barriers;
- regulatory complexity increases demand for jurisdiction-aware compliance tooling;
- professional roles shift from information access toward interpretation, accountability and relationship management;
- forecasts change the systems being forecast, creating reflexive markets;
- local execution and open-source alternatives reduce some provider lock-in;
- stronger machine observability creates both resilience gains and disclosure risks.

These are scenarios, not outcome claims.

## CoTime+ business-model pivot

The most important business-model relation is:

`PAST_DATA -> CURRENT_STATE -> FORECAST -> ACTION -> WORLD_CHANGE -> NEW_FORECAST`

When forecasts influence behavior, they become endogenous to the environment.

A firm that sells periodic analysis may therefore face pressure to evolve toward:

- continuously updated evidence;
- model/version provenance;
- forecast calibration;
- scenario monitoring;
- exception alerts;
- decision auditability;
- customer-specific interpretation;
- governance and accountability support.

This is a general structural hypothesis, not a prediction about any one professional or firm.

## CI+ strategy

Use massive parallelism only across **independent evidence/scenario checks**.

Parallel lanes may perform:

- source validation;
- citation freshness checks;
- claim classification;
- duplicate detection;
- assumption extraction;
- counterargument generation;
- falsifier generation;
- scenario decomposition;
- jurisdiction-tag checks;
- financial-scope tagging;
- provenance validation;
- policy/ethics flagging.

Then fan-in:

`parallel evidence lanes -> bounded fan-in -> contradiction review -> scenario packet -> receipt`

Effectful outputs remain fenced.

`PARALLEL_ANALYSIS_NE_PARALLEL_AUTHORITY`
`FANIN_NE_AUTOMATIC_ACCEPTANCE`

## Operationalization

A mature pipeline can run:

`CoSourceGraph -> CoEvidence -> CoClaim -> CoScenario -> CoTimeMonitor -> CoDrift -> CoReassess`

with currentness refreshes driven by:

- new authoritative source;
- material market/publication event;
- regulation/version change;
- observed scenario indicator;
- customer-requested review;
- scheduled horizon review.

No claim is silently upgraded because it survived one review cycle.

`SURVIVED_REVIEW_NE_PROVEN_TRUE`
`CURRENT_NE_CORRECT`

## Darren-use pattern

For a professional recipient, the strongest recurring form is not "here is the answer."

It is:

> Here is what is known; here is what we infer; here is what could happen; here is what would change our view; here is what to watch.

That lets the recipient apply their own professional judgment without inheriting the model's confidence.

## Nonclaims

This framework is not legal advice, investment advice, a trading instruction, an SEC determination, a forecast of a particular security, a guarantee of prediction accuracy, or authority to act on behalf of a client.

## Rails

`EVIDENCE_NE_INFERENCE`
`INFERENCE_NE_PREDICTION`
`PREDICTION_NE_FACT`
`SCENARIO_NE_FORECAST_CERTAINTY`
`SCENARIO_TIME_NE_EVENT_TIME`
`SEC_CLASSIFICATION_NE_LEGAL_CONCLUSION`
`PUBLIC_INFORMATION_NE_AUTOMATICALLY_IMMATERIAL`
`HYPOTHETICAL_NE_PERFORMANCE_RESULT`
`ACCOUNT_ACTION_REQUIRED -> EXPLICIT_AUTHORIZED_HUMAN_REVIEW`
`PARALLEL_ANALYSIS_NE_PARALLEL_AUTHORITY`
`FANIN_NE_AUTOMATIC_ACCEPTANCE`
`SURVIVED_REVIEW_NE_PROVEN_TRUE`
`CURRENT_NE_CORRECT`
