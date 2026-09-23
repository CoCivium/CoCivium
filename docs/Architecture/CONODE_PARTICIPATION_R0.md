# CoNode Participation R0

**State:** `CANDIDATE__BRANCH_PR__NO_RUNTIME_OR_PUBLIC_AUTHORITY_CHANGE`

## Lead

A participant-owned machine should be able to join CoAll without surrendering the machine to a provider AI, remote-control product, browser session, or single model.

`PARTICIPATION_NE_MACHINE_SURRENDER`
`REMOTE_ADMINISTRATION_NE_NODE_PARTICIPATION`
`COALL_SHARED_NE_ALL_DATA_SHARED`

## Model

A CoNode is a bounded participant-owned execution and projection surface.

```text
participant
  <-> RickBar / local UX
  <-> local CoNode agent
  <-> CoAll relational fabric
        -> deterministic workers
        -> local/open models
        -> remote/provider models
        -> GitHub/CI
        -> MCP/adapters
```

No worker or adapter becomes the control plane merely because it is reachable or authenticated.

## Minimum node contract

A node manifest SHOULD declare node identity and participant scope, privacy domain, local capabilities, allowed transports, effect ceiling, external-provider policy, local-model availability, public-internet exposure policy, receipt route, human-facing projection, and wake/materialization policy.

The manifest MUST NOT contain passwords, API keys, bearer tokens, private keys, recovery codes, or other secrets.

## Bootstrap posture

Default bootstrap is read-only discovery.

A bootstrap helper MAY inventory OS/runtime facts, existing CoCivium/CoAll/RickBar material, local AI/runtime availability, LAN reachability, and bounded capability surfaces.

It MUST NOT by default expose new Internet-facing services, weaken host security, install remote-control software, change firewall/RDP/WinRM policy, transmit private user files, or grant external AI unrestricted machine control.

## RickBar projection

RickBar is the preferred participant-facing projection. Different nodes may render different views based on participant, authority, relevance, locality, and privacy.

`RICKBAR_VIEW_NE_GLOBAL_STATE_DUMP`

## AI workers

Models are replaceable workers behind capability contracts.

`MODEL_NE_AUTHORITY`
`LOCAL_NE_TRUSTED`
`PROVIDER_NE_CONTROL_PLANE`
`CAPABILITY_AVAILABLE_NE_EFFECT_AUTHORIZED`

Prefer local/deterministic execution when it satisfies the deed with lower privacy, dependency, latency, or attention cost.

## Transport/adapters

MCP, Desktop Commander, RDP, WinRM, SSH, browser automation, filesystem queues, local IPC, node APIs, and future transports are adapters.

`ADAPTER_NE_CONTROL_PLANE`
`TRANSPORT_NE_IDENTITY`
`CONNECTED_NE_AUTHORIZED_FOR_EFFECTS`

## Participant privacy

Node participation does not imply whole-machine ingestion.

`NODE_MEMBER_NE_ALL_CONTENT_IN_SCOPE`
`LAN_VISIBLE_NE_CONTENT_IN_SCOPE`

## CI contract

Candidate machine-readable objects:

- `schemas/conode-participation-v0.1.schema.json`
- `examples/conode-participation-v0.1.example.json`
- `.github/workflows/conode-participation-contract.yml`

CI validation is structural only.

`SCHEMA_PASS_NE_RUNTIME_TRUST`
`CI_PASS_NE_NODE_AUTHORIZATION`

## Lifecycle

A node may be `DISCOVERED`, `CANDIDATE`, `READY_LOCAL`, `PARTICIPATING`, `DEGRADED`, `DORMANT`, or `RETIRED`.

Transitions require evidence appropriate to the effect. A reachable machine is not automatically participating.

## Rails

`PARTICIPATION_NE_MACHINE_SURRENDER`  
`REMOTE_ADMINISTRATION_NE_NODE_PARTICIPATION`  
`COALL_SHARED_NE_ALL_DATA_SHARED`  
`MODEL_NE_AUTHORITY`  
`PROVIDER_NE_CONTROL_PLANE`  
`ADAPTER_NE_CONTROL_PLANE`  
`CONNECTED_NE_AUTHORIZED_FOR_EFFECTS`  
`NODE_MEMBER_NE_ALL_CONTENT_IN_SCOPE`  
`SCHEMA_PASS_NE_RUNTIME_TRUST`  
`CI_PASS_NE_NODE_AUTHORIZATION`
