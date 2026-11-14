# CoProviderExit+ / Failure-Domain Resilience R0

**State:** `CANDIDATE_EXIT_READINESS__NO_ACCOUNT_DELETION_NO_PROVIDER_MUTATION_NO_RUNTIME_AUTHORITY`

## Lead

CoAll should be able to lose ChatGPT, a local machine, a home network, a model provider, a repository host, or a power source without losing its work identity, provenance, authority model, or recoverable frontier.

The target is not "leave every provider immediately." The target is:

`NO_SINGLE_PROVIDER_OR_LOCAL_DEVICE_IS_REQUIRED_FOR_CONTINUITY`

Provider and local surfaces remain useful embodiments, but none should be an irreplaceable root.

`PROVIDER_SESSION_NE_CONTROL_PLANE`
`LOCAL_DEVICE_NE_CUSTODY_ROOT`
`GITHUB_NE_CUSTODY_ROOT`
`MODEL_MEMORY_NE_SOURCE_OF_TRUTH`
`COBAR_NE_SINGLE_POINT_OF_CONTINUITY`

## Why account deletion is a later effect

Closing an account should occur only after an explicit exit-readiness proof.

```text
inventory
-> classify unique/private/provider-only state
-> externalize unique deltas
-> prove independent reconstruction
-> prove successor pickup
-> prove credential/account-independent bootstrap
-> freeze new provider dependency
-> bounded quiescence interval
-> final exception review
-> account/session closure if separately authorized
```

`DRAINED_NE_DELETE_SAFE`
`CLOSE_SAFE_NE_ACCOUNT_DELETE_SAFE`
`EXTERNALIZED_NE_RECONSTRUCTIBLE`
`RECONSTRUCTIBLE_NE_INDEPENDENT`

## Exit readiness gates

Before provider account deletion, require evidence for:

1. unique-state census;
2. independent bootstrap;
3. private custody;
4. public bootstrap;
5. receiver pickup;
6. credential independence;
7. failure-domain diversity;
8. human-access fallback;
9. revocation map for keys/billing/domains/external ownership;
10. exception register for unresolved provider-only capabilities.

A single green backup is not enough.

`BACKUP_NE_RECOVERY_PROOF`
`COPY_COUNT_NE_FAILURE_DOMAIN_COUNT`

## Local infrastructure is also a failure domain

Local optionality is valuable, but a house, workstation, NAS, router, local model host, or local power circuit is not an independent universe.

Candidate failure domains include provider account/region, public repository host, home/site power, home/site network, primary PC, local storage/NAS, mobile/offsite device, independent remote/offsite storage, independent compute/model provider, human-readable offline recovery material, and future peer/federated CoNodes.

Two devices on one power/network/storage root are not automatically two failure domains.

`DEVICE_COUNT_NE_FAILURE_DOMAIN_COUNT`
`LOCAL_REPLICA_NE_OFFSITE_REPLICA`
`SAME_POWER_DOMAIN_NE_POWER_RESILIENCE`
`SAME_CREDENTIAL_ROOT_NE_IDENTITY_RESILIENCE`

No UPS is not itself a crisis. It means local continuity must assume abrupt power loss rather than graceful shutdown.

`NO_UPS_REQUIRES_CRASH_TOLERANCE`

## Redundant surfaces

CoBar, CoDesktop, CoStead, GitHub, provider chats, local models, web services, APIs and future peer nodes should become replaceable projections and routes.

A useful surface contract answers:

`what function | what state | what authority | what privacy | what failure domain | what replacement route | what reconstruction recipe`

`USEFUL_SURFACE_NE_REQUIRED_SURFACE`
`PRIMARY_UI_NE_CONTINUITY_ROOT`

## Power-loss and memory-loss posture

Critical state should tolerate process kill, machine power loss, local disk loss, network loss, provider loss, account loss, stale model memory, and absent chat history.

Prefer append-only logs, atomic writes, content-addressed objects, checkpoints, exact hashes, replayable recipes, and receiver-local ACKs.

`VOLATILE_MEMORY_NE_DURABLE_STATE`
`PROCESS_LIVENESS_NE_CONTINUITY`

## Open-source and distributed alternatives

Open-source/local systems reduce vendor concentration and improve inspectability and custody. They do not automatically create independence.

A strong route mix may include deterministic local workers, local/open-weight models, independent remote/open-model nodes, public CI, private offsite custody, peer/federated CoNodes, and provider models where they still have comparative advantage.

`OPEN_SOURCE_NE_FAILURE_DOMAIN_INDEPENDENCE`
`LOCAL_MODEL_NE_PROVIDER_INDEPENDENCE_IF_ALL_HOSTING_IS_LOCAL`
`MODEL_DIVERSITY_NE_INFRASTRUCTURE_DIVERSITY`

The mature goal is capability routing across distinct failure domains, not ideological purity about where the silicon sits.

## Account retirement classes

- `ACTIVE_DEPENDENCY`
- `ACTIVE_OPTIONAL`
- `QUIESCENT_OPTIONAL`
- `EXIT_READY_UNAUTHORIZED`
- `EXIT_AUTHORIZED_PENDING`
- `RETIRED_WITH_RECOVERY_PROOF`

Current ChatGPT account state is not inferred by this document. No deletion or session closure is authorized here.

## Rails

`PROVIDER_SESSION_NE_CONTROL_PLANE`
`LOCAL_DEVICE_NE_CUSTODY_ROOT`
`DRAINED_NE_DELETE_SAFE`
`CLOSE_SAFE_NE_ACCOUNT_DELETE_SAFE`
`BACKUP_NE_RECOVERY_PROOF`
`COPY_COUNT_NE_FAILURE_DOMAIN_COUNT`
`DEVICE_COUNT_NE_FAILURE_DOMAIN_COUNT`
`NO_UPS_REQUIRES_CRASH_TOLERANCE`
`USEFUL_SURFACE_NE_REQUIRED_SURFACE`
`VOLATILE_MEMORY_NE_DURABLE_STATE`
`OPEN_SOURCE_NE_FAILURE_DOMAIN_INDEPENDENCE`
`MODEL_DIVERSITY_NE_INFRASTRUCTURE_DIVERSITY`
`ACCOUNT_RETIREMENT_REQUIRES_EXPLICIT_AUTHORITY`
`VALIDATION_IS_NOT_ACCEPTANCE`
