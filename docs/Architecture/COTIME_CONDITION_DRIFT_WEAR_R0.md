# CoTime Condition Drift and Wear Trajectory R0

**State:** `SYNTHETIC_CONDITION_TRAJECTORY__NO_MAINTENANCE_OR_REPLACEMENT_AUTHORITY`

## Purpose

Many systems do not jump from healthy to failed. They drift.

Shoes abrade, foam compresses, batteries lose capacity, storage accumulates errors, models drift, interfaces stale, assumptions age, and organizations accumulate friction. The useful state is often the **in-between condition trajectory** before hard failure.

R0 therefore models:

`USE -> CONDITION_CHANGE -> DRIFT -> THRESHOLD_PROXIMITY -> PREPARATION -> REPAIR_OR_REPLACE_CANDIDATE`

without equating age, usage, or predicted wear with actual failure.

`FUNCTIONING_NE_UNCHANGED`

`WEAR_NE_FAILURE`

`AGE_NE_CONDITION`

`USAGE_NE_WEAR_RATE_WITHOUT_CONTEXT`

## Condition envelope

A condition observation may bind:

- object or substrate;
- observed condition metric;
- observation time;
- usage since prior observation;
- environment/context;
- uncertainty;
- threshold definition;
- provenance;
- maintenance history;
- observer/sensor identity.

A trajectory may then estimate rate and threshold proximity.

`OBSERVED_CONDITION_NE_PREDICTED_TRAJECTORY`

## Predictive wear

A wear forecast must bind a horizon, assumptions, and later calibration path.

Example:

```text
condition@T1 = 90
condition@T2 = 80
candidate rate = -10 / interval
threshold = 50
predicted crossing = T5
```

The crossing forecast is not a failure fact.

`PREDICTED_WEAR_NE_FAILURE_FACT`

`THRESHOLD_FORECAST_NE_REPLACEMENT_COMMAND`

## Maintenance and identity

Repair, component replacement, adaptation, or substrate migration may preserve role continuity even while material state changes.

`MAINTENANCE_NE_IDENTITY_LOSS`

`REPLACEMENT_NE_CONTINUITY_LOSS`

`IDENTITY_CONTINUITY_NE_SUBSTRATE_IMMUTABILITY`

Conversely, role continuity does not imply unchanged physical state.

`SAME_ROLE_NE_SAME_MATERIAL_STATE`

## Visible versus hidden drift

Visible wear may indicate hidden drift, but does not prove it.

`VISIBLE_WEAR_CAN_BE_EVIDENCE_OF_HIDDEN_DRIFT`

`VISIBLE_WEAR_NE_HIDDEN_FAILURE_PROOF`

The same rule generalizes to model quality, stale assumptions, battery condition, storage reliability, UX friction, organizational load, and resource performance.

## First canary

The synthetic fixture proves:

1. condition can deteriorate while the object remains functioning;
2. age alone cannot determine condition;
3. equal usage under different context may produce different wear rates;
4. a threshold-crossing forecast requires a calibration horizon;
5. predicted threshold crossing does not authorize replacement;
6. maintenance may improve condition without changing object role identity;
7. replacement may preserve continuity when explicitly related as successor;
8. visible wear does not prove hidden failure.

No physical maintenance, purchase, replacement, device action, medical inference, financial effect, runtime adoption, canon or CoEx is authorized.

## Rails

`FUNCTIONING_NE_UNCHANGED`  
`WEAR_NE_FAILURE`  
`AGE_NE_CONDITION`  
`USAGE_NE_WEAR_RATE_WITHOUT_CONTEXT`  
`OBSERVED_CONDITION_NE_PREDICTED_TRAJECTORY`  
`PREDICTED_WEAR_NE_FAILURE_FACT`  
`THRESHOLD_FORECAST_NE_REPLACEMENT_COMMAND`  
`MAINTENANCE_NE_IDENTITY_LOSS`  
`REPLACEMENT_NE_CONTINUITY_LOSS`  
`IDENTITY_CONTINUITY_NE_SUBSTRATE_IMMUTABILITY`  
`VISIBLE_WEAR_NE_HIDDEN_FAILURE_PROOF`  
`VALIDATION_IS_NOT_ACCEPTANCE`
