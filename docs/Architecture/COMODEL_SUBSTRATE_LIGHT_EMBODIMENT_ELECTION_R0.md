# CoModel substrate-light embodiment election R0

**State:** `SYNTHETIC_EMBODIMENT_ELECTION_CANARY__NO_RUNTIME_NO_CANON_NO_AUTHORITY_CHANGE`

## Why this follows from substrate-light identity

Once a logical model role is not identical to one continuously live process, a new question becomes first-class:

> Should this role materialize now, and if so on which admissible substrate?

That is an election problem, not merely a deployment detail.

The candidate rule is deliberately simple:

```text
hard gates
  capability
  authority
  confidentiality
  liveness
  currentness
  exact-model bind when required
      ↓
admissible routes only
      ↓
contract-supplied preference order
      ↓
elect one route
```

If no route satisfies the hard gates:

`HOLD_NO_ADMISSIBLE_EMBODIMENT`

The system must not make privacy, authority or capability requirements negotiable just because a cheaper or more available route exists.

## Dormancy becomes an elected state

If useful work does not require a live embodiment:

`DORMANT_OPTION`

is preferable to materializing something merely because capacity exists.

`SPARE_CAPACITY_NE_MATERIALIZATION_REQUIREMENT`

This turns materialization duty cycle into something the scheduler can actively reduce.

## Failover changes route, not logical lane

A failed embodiment may be replaced while preserving:

- logical lane identity;
- completed-step provenance;
- authority ceiling;
- confidentiality;
- currentness boundary.

Completed work is not replayed merely because the route changed.

`LOGICAL_LANE_NE_EXECUTION_ROUTE`  
`ROUTE_CHANGE_NE_REPLAY_COMPLETED_WORK`

Two models belonging to the same provider are also not counted as two independent failure domains merely because their names differ.

`MODEL_COUNT_NE_FAILURE_DOMAIN_INDEPENDENCE`

## What else this unlocks

A substrate-light architecture can eventually support:

- cold/warm/hot embodiment tiers;
- demand-driven model materialization;
- privacy-aware local/cloud routing;
- energy/thermal-aware scheduling when measured data exists;
- capability-specific temporary specialists;
- failure-domain-diverse replicas;
- branch/fan-in semantics for simultaneous embodiments;
- model-family replacement behind a stable role contract;
- migration without authority widening;
- retiring live processes while preserving dormant option value.

R0 does not implement those broader policies. It establishes the hard-gate election primitive they need.

## Donor relation

This contracts with the existing provider-neutral routing donor:

`COEVO.PR90.PROVIDER_NEUTRAL_ROUTING.UNIQUE_FANIN.R0`

rather than creating a competing routing ontology.

## Rails

`HARD_GATES_BEFORE_PREFERENCE`  
`PRIVACY_NE_TRADEABLE_FOR_CONVENIENCE`  
`AUTHORITY_NE_TRADEABLE_FOR_AVAILABILITY`  
`NO_ROUTE_NE_DEGRADE_REQUIREMENTS`  
`MATERIALIZATION_NOT_REQUIRED_NE_MATERIALIZE_ANYWAY`  
`LOGICAL_LANE_NE_EXECUTION_ROUTE`  
`ROUTE_CHANGE_NE_REPLAY_COMPLETED_WORK`  
`MODEL_COUNT_NE_FAILURE_DOMAIN_INDEPENDENCE`  
`SYNTHETIC_ROUTE_ELECTION_NE_RUNTIME_SCHEDULER`  
`VALIDATION_IS_NOT_ACCEPTANCE`
