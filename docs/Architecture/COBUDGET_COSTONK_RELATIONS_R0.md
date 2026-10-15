# CoBudget+ / CoBudGet+ / CoBud+ / CoStonk+ Relations R0

**State:** `CANDIDATE_RESOURCE_RELATION_MODEL__NO_FINANCIAL_AUTHORITY`

## Distinctions

- **CoBudget+**: bounded allocation envelope for resources.
- **CoBudGet+**: playful/query relation for how a budget is obtained, refreshed, earned, granted, released, or discovered.
- **CoBud+**: smaller relational resource unit, sub-allocation, companion budget, or budget node.
- **CoStonk+**: market/investment observation, simulation, strategy, and risk relation family.

None implies permission to move money.

`BUDGET_RELATION_NE_SPEND_AUTHORITY`

`MARKET_ANALYSIS_NE_TRADE_AUTHORITY`

## Resource vector

A CoBudget relation may bind:

`resource_type | quantity | unit | owner | custodian | purpose | reserve_floor | committed | available | time_horizon | risk_ceiling | authority | provenance | currentness`

Resource types need not be money:

- cash;
- crypto;
- compute;
- model tokens;
- storage;
- bandwidth;
- human attention;
- energy;
- time;
- legal/operational capacity.

`BUDGET_NE_ONLY_MONEY`

## CoBudGet+

Candidate relations include:

`ALLOCATED_FROM`  
`EARNED_FROM`  
`DONATED_FROM`  
`RELEASED_BY`  
`UNLOCKED_WHEN`  
`REFILLED_BY`  
`RESERVED_FOR`  
`EXPIRES_AT`  
`REQUIRES_AUTHORITY_FROM`

This makes "where did the budget come from?" first-class rather than an annotation humans inevitably forget to update.

## Crypto / CoStonk

Personal or legacy holdings must remain distinct from CoCivium treasury unless explicitly transferred into a separately authorized treasury relation.

`PERSONAL_ASSET_NE_COALL_TREASURY`

`KNOWN_BALANCE_NE_AVAILABLE_BUDGET`

`AVAILABLE_BUDGET_NE_AUTHORIZED_SPEND`

`SHADOW_STRATEGY_NE_LIVE_POSITION`

## Rails

`BUDGET_RELATION_NE_SPEND_AUTHORITY`  
`MARKET_ANALYSIS_NE_TRADE_AUTHORITY`  
`PERSONAL_ASSET_NE_COALL_TREASURY`  
`KNOWN_BALANCE_NE_AVAILABLE_BUDGET`  
`AVAILABLE_BUDGET_NE_AUTHORIZED_SPEND`  
`SHADOW_STRATEGY_NE_LIVE_POSITION`  
`BUDGET_NE_ONLY_MONEY`  
`VALIDATION_IS_NOT_ACCEPTANCE`
