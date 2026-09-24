# CoNod+ Provider-Neutral Materialization / Failure-Domain Routing R0

**Date:** 2026-09-24  
**State:** `CANDIDATE__BRANCH_ONLY__NO_RUNTIME_CANON_OR_AUTHORITY_EFFECT`  
**Scope:** CoNod / CoWave / CoProviderEdge+ / CoNode / CoStead / CoLocalModelWorker / CoSessionAutocycle / CoOomph+ / CoLUE+ / CoAlive+.

## CoHereNow

Reliance on ChatGPT alone is an avoidable single-provider failure domain.

Current CoCivium architecture already says:

- provider chat is a reasoning/projection/coordination surface, not the durable execution root;
- models are replaceable workers behind capability contracts;
- provider/model memory is not source-of-truth or event bus;
- CoStead/private node fabric is the intended durable private/high-volume substrate;
- Ollama/local models should increasingly participate through provider-neutral capability contracts;
- provider tabs, model memory, and any one backend are not lifecycle authority.

This document does **not** create another control plane. It binds those existing relations directly into CoNod R2.

## CoNod materialization rule

A CoNod first elects a **logical CoWave**.

Only after that should CoOomph+/route election decide where individual lanes materialize.

```text
'
 -> CoAckRewise
 -> currentness / CoBoogie if needed
 -> compile logical CoWave
 -> classify lane capability + privacy + authority + evidence needs
 -> elect one or more admissible failure domains
 -> materialize adaptively
 -> exact receipts / provenance
 -> deterministic fan-in
 -> durable externalization
 -> quiet / handoff
```

`LOGICAL_WORK_NE_PROVIDER_SESSION`  
`PROVIDER_SESSION_NE_CONTROL_PLANE`  
`MODEL_NE_AUTHORITY`

## Candidate execution domains

A lane MAY materialize through:

1. deterministic local code;
2. local/open-weight model runtime such as an already-installed Ollama-compatible worker;
3. machine-owned local process or resident worker fabric;
4. GitHub CI / other bounded automation;
5. ChatGPT/provider reasoning surface;
6. another qualified remote/provider model;
7. MCP-like capability adapter;
8. PS7 bootstrap/break-glass execution;
9. future CoNode / GRAIL+ workers.

The route is elected by deed requirements, not brand loyalty.

## Route dimensions

Each lane SHOULD declare or derive:

- capability fit;
- evidence quality required;
- privacy/confidentiality;
- authority/effect class;
- reversibility;
- latency;
- cost;
- available CoEnerget+;
- failure-domain independence;
- currentness;
- model/runtime availability;
- context size;
- expected quality;
- deterministic-vs-generative need;
- fan-in compatibility;
- receipt/provenance capability;
- human attention cost.

Candidate preference:

> use the lowest-dependency admissible route that meets the deed's quality/evidence requirement, while preserving failure-domain diversity for consequential work.

This is **not** a blanket "local always wins" rule.

`LOCAL_NE_TRUSTED`  
`REMOTE_NE_BAD` is rejected.  
`TASK_FIT_AND_EVIDENCE_OVER_VENDOR_PRESTIGE`

## ChatGPT relation

ChatGPT may remain a high-value reasoning, synthesis, research, adjudication and human-interaction receiver.

It should not be required to be:

- the only durable memory;
- the only queue;
- the only worker;
- the only currentness store;
- the only compiler;
- the only verifier;
- the only route to X2;
- the only cross-session bus;
- the only recovery path.

`CHATGPT_USEFUL_NE_CHATGPT_REQUIRED_FOR_CONTINUITY`

If the provider is unavailable, constrained, expensive, stale, or unsuitable for a deed, logical work should remain representable and reroutable.

`PROVIDER_OUTAGE_NE_WORK_DEATH`

## Failure-domain replication

Consequential work MAY use diverse independent lanes:

```text
source object
 -> deterministic validator
 -> local/open-model interpretation
 -> provider-model interpretation
 -> independent challenge
 -> fan-in preserving disagreement
```

Do not treat multiple models as independent merely because names differ.

Independence dimensions may include:

- vendor/provider;
- model family;
- local vs remote;
- code path;
- source set;
- method;
- prompt/projection;
- hardware/runtime;
- network/failure domain.

`MODEL_COUNT_NE_INDEPENDENCE`  
`MULTI_PROVIDER_NE_MULTI_EVIDENCE_BY_DEFAULT`

## Local model posture

Current landed policy already has a narrow local worker:

- loopback-only;
- PUBLIC-only;
- allowed effects `OBSERVE | PROPOSE | REVIEW_CHALLENGE`;
- no install/pull;
- no repo mutation;
- no provider-session mutation;
- no public outreach;
- no authority change;
- X2 Ollama canary still unrun.

CoNod should reuse that worker policy rather than pretending local AI integration is already proven.

`ADAPTER_READY_NE_RUNTIME_PROVEN`  
`MODEL_AVAILABLE_NE_VALIDATED`  
`LOCAL_MODEL_NE_COALL_INTEGRATED`

## CoLUE+ relation

Provider-neutral materialization should reduce human burden.

Rick should not need to decide:

- which model;
- which tab;
- which worker;
- which queue;
- which retry;
- which receiver;

unless a true human preference/gate makes that choice material.

`ROUTE_ELECTION_SHOULD_BE_MACHINE_OWNED_WHERE_SAFE`  
`RICK_NE_PROVIDER_LOAD_BALANCER`

## CoAlive+ projection

RickBar/CoAura MAY expose only material routing state:

- `LOCAL`
- `REMOTE`
- `MIXED`
- `DEGRADED`
- `FAILOVER`
- `WAITING_FOR_ROUTE`

with optional drill-down into exact worker/provider/runtime identities.

The front door should show meaning, not vendor telemetry.

`PROJECTION_NE_ROUTING_AUTHORITY`

## CoTime+ / provider health

Provider/runtime availability is time-relative.

A route claim must be bound to observation time/currentness.

`AVAILABLE_THEN_NE_AVAILABLE_NOW`  
`ROUTE_OBSERVED_NE_ROUTE_PERSISTENT`

A degraded provider may later recover without rewriting historical failure evidence.

## CoBoogie / CoRegroup relation

Material route/failure-domain change is a valid CoBoogie trigger.

```text
provider/local route changes
 -> CoBoogie observes delta
 -> CoRegroup reconciles available capabilities/currentness
 -> pending logical lanes reroute where admissible
```

Do not restart completed work merely because a route changed.

`ROUTE_CHANGE_NE_REPLAY_ALL`

## Bounded synthetic failure canary

The paired fixture models 64 logical lanes across:

- deterministic local;
- local/open model;
- provider model;
- GitHub/CI;
- held/no-admissible-route.

It then synthetically removes the provider route and checks that:

- logical lane identity survives;
- completed provider outputs remain provenance;
- unfinished admissible lanes reroute;
- lanes requiring unavailable unique capability HOLD rather than fabricate completion;
- no authority expands during failover;
- fan-in remains deterministic;
- human action remains zero unless a true gate is encountered.

## Rails

`LOGICAL_WORK_NE_PROVIDER_SESSION`  
`PROVIDER_SESSION_NE_CONTROL_PLANE`  
`PROVIDER_NE_LIFECYCLE_AUTHORITY`  
`CHAT_MEMORY_NE_EVENT_BUS`  
`MODEL_MEMORY_NE_SOURCE_OF_TRUTH`  
`MODEL_NE_AUTHORITY`  
`LOCAL_NE_TRUSTED`  
`ADAPTER_NE_CONTROL_PLANE`  
`MCP_NE_COALL`  
`PS7_NE_DEFAULT_IF_MACHINE_ROUTE_HEALTHY`  
`PROVIDER_OUTAGE_NE_WORK_DEATH`  
`MODEL_COUNT_NE_INDEPENDENCE`  
`ROUTE_CHANGE_NE_REPLAY_ALL`  
`RICK_NE_PROVIDER_LOAD_BALANCER`

## Current nonclaims

- X2 machine route remains unproven/offline from this receiver;
- no X2 Ollama canary has been run;
- no local model inventory has been re-observed here;
- no PS7 deed was executed;
- no provider failover runtime exists merely because this fixture exists;
- no canon/runtime/authority transfer is claimed.
