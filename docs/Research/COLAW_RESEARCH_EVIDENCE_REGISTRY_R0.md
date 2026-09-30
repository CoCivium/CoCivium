# CoLawResearch+ Evidence Registry R0

**Date:** 2026-09-25  
**State:** `CANDIDATE__BRANCH_ONLY__NO_LEGAL_CONCLUSION`

## Purpose

Separate current law/rule text, historical proposals, enforcement evidence, official staff remarks, secondary analysis and CoAll scenario hypotheses.

A source can be authoritative about what it says without being authoritative about what CoAll should conclude.

## Evidence classes

- `OPERATIVE_RULE_OR_ORDER`
- `FINAL_RULE_WITHDRAWAL`
- `HISTORICAL_PROPOSAL`
- `ENFORCEMENT_ACTION`
- `OFFICIAL_STAFF_REMARK`
- `OFFICIAL_GUIDANCE`
- `CURRENTNESS_INDEX`
- `SECONDARY_ANALYSIS`
- `COALL_INFERENCE`
- `SCENARIO`

Rails:

`HISTORICAL_PROPOSAL_NE_OPERATIVE_RULE`  
`STAFF_REMARK_NE_COMMISSION_RULE`  
`ENFORCEMENT_CASE_NE_UNIVERSAL_REQUIREMENT`  
`COALL_INFERENCE_NE_SOURCE_FACT`

## SEC AI example set

### Predictive-data-analytics proposal

SEC File S7-12-23 concerned conflicts of interest associated with predictive data analytics by broker-dealers and investment advisers.

Evidence class: `HISTORICAL_PROPOSAL`.

The SEC states that it withdrew the proposal on June 12, 2025 and did not intend to issue a final rule with respect to that proposal. It must not be represented as current operative law. [SEC current rulemaking record]

### AI-marketing enforcement

On March 18, 2024, the SEC announced settled charges against Delphia (USA) Inc. and Global Predictions Inc. concerning false or misleading statements about purported AI use.

Evidence class: `ENFORCEMENT_ACTION`.

This is evidence about particular enforcement matters, not a universal AI rule. [SEC 2024-36]

### 2026 investment-management remarks

On February 3, 2026, Brian Daly, Director of the SEC Division of Investment Management, delivered remarks titled "Artificial Intelligence and the Future of Investment Management."

Evidence class: `OFFICIAL_STAFF_REMARK`.

The SEC page says the remarks were made in his official capacity but do not necessarily reflect the views of the Commission, Commissioners or other staff. They are therefore useful for staff-level signals and questions, not as a substitute for an operative Commission rule. [SEC, Feb. 3, 2026]

### Current rulemaking index

The SEC rulemaking index is a currentness aid for identifying proposed and final rulemaking activity. Current entries and underlying instruments must be checked separately.

## Darren-facing interpretation discipline

For a financial-services advisory, preserve:

`official source -> evidence class -> source date/version -> bounded interpretation -> counterinterpretation -> scenario -> implication`

Never collapse:

`scenario -> prediction -> recommendation`

A Darren advisory can discuss possible effects on advisory operations, client communication, AI marketing, supervision, controls, research workflows and business models without turning CoAll speculation into securities-specific recommendations.

## Currentness

Each external legal/regulatory object should preserve:

- exact official URL;
- publication/update date;
- effective date where applicable;
- withdrawal/repeal/supersession state;
- retrieval date;
- source hash where practical;
- evidence class;
- scope;
- unresolved applicability questions.

`SOURCE_DATE_NE_EFFECTIVE_DATE`  
`CURRENT_INDEX_NE_COMPLETE_LEGAL_REVIEW`  
`WITHDRAWN_NE_OPERATIVE`

## Research / CI separation

CI may verify structural completeness and internal consistency. CI must not declare a legal conclusion merely because an evidence record validates.

`CI_PASS_NE_LEGAL_CONCLUSION`

## References

- https://www.sec.gov/newsroom/press-releases/2024-36
- https://www.sec.gov/rules-regulations/2025/06/s7-12-23
- https://www.sec.gov/newsroom/speeches-statements/daly-020326-artificial-intelligence-future-investment-management
- https://www.sec.gov/rules-regulations/rulemaking-activity
