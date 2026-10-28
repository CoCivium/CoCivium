# CoExitRights+ / Data Erasure and Dependency Sunset R0

**State:** `CANDIDATE_EXIT_POLICY__NO_ACCOUNT_DELETION_NO_BILLING_MUTATION_NO_CREDENTIAL_EFFECT`

## Lead

A dependency is healthier when participants can leave it cleanly.

CoAll should prefer providers, accounts, devices, services and institutions whose exit path is explicit, low-friction, evidence-producing and proportionate to the value they provide.

The target is not "delete everything immediately."

The target is:

`DEPENDENCY_SHOULD_BE_REVOCABLE`

`EXIT_SHOULD_NOT_REQUIRE_LOSS_OF_IDENTITY_OR_WORK`

`PAYMENT_SHOULD_NOT_BE_REQUIRED_FOR_CONTINUITY_WHEN A SAFE ALTERNATIVE EXISTS`

## Exit dimensions

For each account or service, model separately:

- purpose;
- unique capability;
- recurring cost;
- switching cost;
- data held;
- credentials/keys;
- billing relation;
- domains or external ownership;
- export capability;
- deletion capability;
- retention policy;
- revocation path;
- provider-only dependencies;
- substitute routes;
- recovery evidence;
- legal/contractual constraints;
- human attention cost.

`ACCOUNT_NE_IDENTITY`

`SUBSCRIPTION_NE_CONTINUITY`

`BILLING_RELATION_NE_AUTHORITY`

## Sunset sequence

A candidate sunset proceeds:

```text
inventory
-> stop creating new dependency
-> export or externalize unique state
-> independently verify reconstruction
-> migrate required credentials/ownership
-> cancel recurring charges if authorized
-> revoke integrations/tokens if authorized
-> delete provider-held data where supported and authorized
-> delete account where separately authorized
-> verify post-exit state
-> retain only minimal exit receipt
```

Each step is separately evidenced.

`CANCELLED_NE_DATA_DELETED`

`DATA_DELETE_REQUESTED_NE_DATA_DELETED`

`ACCOUNT_DELETED_NE_ALL_COPIES_ERASED`

`EXPORT_COMPLETE_NE_PROVIDER_RETENTION_ZERO`

`NO_RECEIPT_NE_NO_CLAIM`

## Data minimization before deletion

The strongest exit is not merely deleting late. It is avoiding unnecessary accumulation early.

Prefer:

- local or participant-owned custody for private state;
- minimal provider-side history;
- replaceable credentials;
- scoped connectors;
- short retention where appropriate;
- content-addressed portable state;
- explicit provenance without unnecessary personal payload;
- provider memory treated as cache, never custody root.

`MINIMIZATION_BEFORE_ERASURE`

`MEMORY_CONVENIENCE_NE_PROJECT_CUSTODY`

## Cost and coercion pressure

Recurring financial cost, lock-in, forced bundling, data-retention asymmetry, export friction, unilateral policy change and inability to operate without a vendor are all legitimate dependency-pressure signals.

They should influence route election without becoming moralized automatic blockers.

`COST_PRESSURE_NE_BAD_ACTOR_PROOF`

`LOCK_IN_SIGNAL_NE_IMMEDIATE_EXIT_COMMAND`

`DEPENDENCY_PRESSURE_CAN_REDUCE_ROUTE_PREFERENCE`

Where two routes provide comparable capability, prefer the route with lower irreversible lock-in, lower recurring coercive pressure, clearer data custody and easier verified exit.

## Provider replacement is not enough

Replacing one mandatory vendor with one mandatory local machine or one mandatory open-source stack does not solve the architectural problem.

`VENDOR_EXIT_NE_SINGLE_LOCAL_ROOT`

`OPEN_SOURCE_NE_NO_DEPENDENCY`

`SELF_HOSTED_NE_FAILURE_PROOF`

The desired state is plural optionality across distinct failure and governance domains.

## Human ownership and recovery

A participant should be able to answer:

- what accounts exist;
- what they cost;
- what data each holds;
- what would break if each disappeared;
- how to export/replace it;
- how to revoke it;
- whether deletion has been verified;
- what unresolved residue remains.

No provider should become invisible simply because automation manages it.

`AUTOMATION_NE_HIDDEN_DEPENDENCY`

## Account retirement evidence

Candidate retirement state:

`EXIT_READY`
requires:
- no unique provider-only state;
- independent reconstruction proven;
- billing/dependency map complete;
- ownership migration complete;
- unresolved exceptions explicit.

`RETIRED`
requires:
- closure action separately authorized;
- provider acknowledgement where available;
- post-closure verification;
- residue/retention uncertainty recorded.

`RETIRED_NE_ERASURE_PROVEN`

## Rails

`DEPENDENCY_SHOULD_BE_REVOCABLE`
`ACCOUNT_NE_IDENTITY`
`SUBSCRIPTION_NE_CONTINUITY`
`CANCELLED_NE_DATA_DELETED`
`DATA_DELETE_REQUESTED_NE_DATA_DELETED`
`ACCOUNT_DELETED_NE_ALL_COPIES_ERASED`
`EXPORT_COMPLETE_NE_PROVIDER_RETENTION_ZERO`
`MINIMIZATION_BEFORE_ERASURE`
`COST_PRESSURE_NE_BAD_ACTOR_PROOF`
`LOCK_IN_SIGNAL_NE_IMMEDIATE_EXIT_COMMAND`
`VENDOR_EXIT_NE_SINGLE_LOCAL_ROOT`
`OPEN_SOURCE_NE_NO_DEPENDENCY`
`AUTOMATION_NE_HIDDEN_DEPENDENCY`
`RETIRED_NE_ERASURE_PROVEN`
`NO_RECEIPT_NE_NO_CLAIM`
`VALIDATION_IS_NOT_ACCEPTANCE`
