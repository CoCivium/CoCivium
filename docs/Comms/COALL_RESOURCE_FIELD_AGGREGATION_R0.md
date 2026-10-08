# CoAll Resource Field Aggregation R0

**State:** `SYNTHETIC_AGGREGATION_CANARY__NO_REAL_RESOURCE_USE_NO_RUNTIME_AUTHORITY`

## Lead

Yes: as more participants explicitly opt in, CoAll can gain a larger field of eligible resources.

The correct relation is:

```text
participant
  -> explicit scoped grant
  -> current eligible resource
  -> CoResourceField+
  -> task-specific filtering
  -> candidate selection
  -> separate execution authority
```

Not:

```text
participant saw defaults
  -> CoAll owns their device/data/attention
```

## Why this matters

A growing participant ecology can materially increase:

- compute and local-model capacity;
- storage and replication;
- bandwidth and relay options;
- public mention discovery;
- review and adjudication attention;
- domain expertise;
- translation and accessibility capacity;
- moderation;
- failure-domain diversity;
- recovery paths;
- archive/mirror redundancy.

But the useful quantity is not user count alone.

A grant is usable only where its exact scope, purpose, privacy ceiling, currentness, cap, device/surface state, and effect authority fit the task.

`CAPACITY_NE_PERMISSION`

`RESOURCE_AVAILABLE_NE_RESOURCE_ELIGIBLE`

## Defaults UX

A participant may be shown a recommended low-risk default bundle and may accept it in one action after preview.

That bundle must remain decomposable into individually inspectable and revocable grants.

Recommended defaults may include public review attention, public mention forwarding, and explicitly submitted public content.

They must not silently include background compute, private messages, credentials, sensors, financial effects, or autonomous posting.

`DEFAULT_VISIBLE_NE_DEFAULT_GRANTED`

`ONE_CLICK_OPT_IN_NE_OPAQUE_BUNDLE`

The UX should make the consequence legible:

```text
You are enabling:
  [x] public mention forwarding
  [x] bounded public review requests
  [x] explicitly submitted public artifacts

Not enabled:
  [ ] background compute
  [ ] private messages
  [ ] contacts
  [ ] sensors
  [ ] credentials
  [ ] autonomous posting
```

## Synthetic aggregation canary

R0 constructs a synthetic grant field containing:

- active public review attention;
- active public discovery;
- active compute from two independently owned devices;
- active public storage;
- an active private-local model;
- revoked compute;
- referral-only offered storage;
- a visible but unaccepted compute offer.

The task-specific resource compiler must exclude the last three.

For the public synthetic compute task:

```text
baseline participants A+B+C:
  eligible compute = 300 units

expanded participants A+B+C+D:
  eligible compute = 900 units
```

This proves the narrow synthetic relation:

`MORE_VALID_ACTIVE_GRANTS_CAN_INCREASE_TASK_ELIGIBLE_CAPACITY`

It does not prove more progress, better truth, or permission to execute anything.

## Selection is not execution

The field may identify candidate resources whose grants fit a task.

That is still not a runtime effect.

`RESOURCE_ELIGIBLE_NE_SELECTED`

`SELECTED_NE_EXECUTED`

`SELECTED_NE_AUTHORITY_TRANSFER`

A later executor would require a live current grant, exact task bind, cap check, availability/currentness check, resource lease, privacy check, and receipt.

## Fairness / governance

All synthetic grants carry governance weight zero.

More compute, storage, money, attention, or participants do not purchase truth or governing power.

`RESOURCE_CONTRIBUTION_NE_GOVERNANCE_AUTHORITY`

`COMPUTE_CONTRIBUTION_NE_VOTING_POWER`

A very large donor may provide useful capacity while still being only one bounded resource source.

## CoCivia relation

The same field can eventually support ambient CoCivia correspondence.

Examples:

- a participant explicitly opts in to public mention forwarding;
- a translator explicitly offers review capacity;
- a local model is granted for private local drafting only;
- a public mirror grant stores a response artifact;
- a reviewer checks a draft before any external effect.

No mention wakes somebody else's machine merely because CoCivia's name appeared.

`MENTION_NE_RESOURCE_WAKE`

## Growth has costs

A larger field also increases:

- currentness work;
- proof/receipt volume;
- scheduling complexity;
- collision risk;
- privacy surface;
- attack surface;
- revocation handling;
- dedupe/compaction load.

Therefore:

`MORE_RESOURCES_NE_MORE_PROGRESS`

`RESOURCE_GROWTH_REQUIRES_COORDINATION_GROWTH`

The scheduler should prefer proven useful diversity and measured benefit, not raw hoarding of participant resources.

## Current boundary

This R0 uses synthetic grant objects only.

It activates no device, account, model, storage host, bandwidth, private data, sensor, money, or human attention.

No resource is executed.

No governance authority changes.

No canon/runtime/CoEx transition is inferred.

## Rails

`DEFAULT_VISIBLE_NE_DEFAULT_GRANTED`  
`ONE_CLICK_OPT_IN_NE_OPAQUE_BUNDLE`  
`OPT_IN_NE_PERPETUAL_CONSENT`  
`CAPACITY_NE_PERMISSION`  
`RESOURCE_AVAILABLE_NE_RESOURCE_ELIGIBLE`  
`RESOURCE_ELIGIBLE_NE_SELECTED`  
`SELECTED_NE_EXECUTED`  
`SELECTED_NE_AUTHORITY_TRANSFER`  
`RESOURCE_CONTRIBUTION_NE_GOVERNANCE_AUTHORITY`  
`COMPUTE_CONTRIBUTION_NE_VOTING_POWER`  
`REFERRAL_NE_RESOURCE_GRANT`  
`REVOKED_NE_FUTURE_USE_ALLOWED`  
`MORE_RESOURCES_NE_MORE_PROGRESS`  
`MENTION_NE_RESOURCE_WAKE`  
`VALIDATION_IS_NOT_ACCEPTANCE`
