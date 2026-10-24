# CoModelFabric+ / CoOrb Provider Adapters R0

**State:** PUBLIC_ARCHITECTURE_CANDIDATE__NO_PROVIDER_LOGIN_OR_X2_UI_MUTATION  
**Observed:** 2026-10-24

## Purpose

Provide one provider-neutral CoOrb / CoOrbWare control surface over many explicitly authorized model/runtime adapters without making provider tabs, accounts or sessions the continuity anchor.

Target:

```
CoOrb / CoWorkObject
-> task contract
-> capability router
-> bounded provider/local workers
-> fan-out where independent
-> fan-in / compare / challenge
-> explicit effect gate
-> receipt
-> checkpoint
```

## Identity rule

External provider accounts retain their real authorized account identity.

Do not create an Anthropic, OpenAI, Pi or other provider account "as ChatGPT", "as CoOrb", or as a synthetic human principal.

Internal worker identities may be named roles such as:

- CLAUDE_REVIEWER
- LOCAL_LLAMA_EXPLORER
- OLLAMA_CHECKER
- OPENAI_REASONER
- PI_ADAPTER
- DETERMINISTIC_VERIFIER
- CONTRADICTION_CHALLENGER

These are work-role identities, not provider-account ownership claims.

`WORKER_ROLE_NE_EXTERNAL_ACCOUNT_IDENTITY`

## Adapter contract

Each adapter should expose:

`adapter_id | provider/runtime | account/session_ref | auth_state | capabilities | model | cost | latency | context_limit | privacy | authority | lease | currentness | receipts | recovery | successor`

Secrets must remain in the provider/OS credential boundary and never enter receipts.

## Parallel + serial execution

Parallelize independent read-only or proposal-producing work.

Serialize:
- shared-state mutation;
- irreversible actions;
- external sends/publication;
- credential changes;
- financial effects;
- collision domains where duplicate effects are unsafe.

`MASSIVE_PARALLELISM_NE_UNBOUNDED_PARALLEL`
`MANY_MODELS_NE_INDEPENDENT_EVIDENCE`

## Multi-account policy

Multiple legitimately authorized accounts may be represented when they exist for a real operational reason, but:

- no deceptive identity;
- no account creation to evade provider limits, quotas, safety or billing controls;
- no credential sharing beyond provider terms and explicit authority;
- no claim that account count equals capacity or independence.

Prefer:
1. local/FOSS workers;
2. distinct providers for genuine failure-domain/model diversity;
3. bounded provider sessions only when they add measured value.

## CoOrb UX

The user should normally see one coherent surface:

```
WORK
├─ now
├─ moving
├─ blocked
├─ model/resource lanes
├─ dissent
├─ evidence
├─ cost/latency
└─ next effect gate
```

Provider tabs may remain hidden/optional implementation views.

## Current evidence boundary

Prior X2 evidence:
- local Ollama metadata route was reachable and parsed model tags in a bounded probe;
- Claude credential presence was not established in the sampled process;
- Pi CLI/runtime was not established;
- current X2 Remote Desktop Commander route is offline.

Therefore no current Claude login, browser session, CoOrb runtime binding, or multi-provider fan-out is claimed.

## First bounded runtime canary

When X2 becomes reachable:

1. restore one machine-observable control path;
2. inspect current browser/provider sessions without exposing secrets;
3. qualify one local Ollama worker;
4. qualify one authorized external-provider lane if an already-authenticated account/session exists;
5. run the same harmless source-bound task through both;
6. compare output, latency, cost, uncertainty and disagreement;
7. fan-in into one CoWorkObject receipt;
8. close or leave provider view unchanged according to explicit user preference.

No provider account creation is required.

## Rails

`SESSION_NE_WORK`
`TAB_NE_IDENTITY`
`WORKER_ROLE_NE_EXTERNAL_ACCOUNT_IDENTITY`
`AUTHENTICATED_SESSION_NE_SHARED_AUTHORITY`
`MULTI_ACCOUNT_NE_LIMIT_EVASION`
`MANY_MODELS_NE_INDEPENDENT_EVIDENCE`
`PROVIDER_FAILURE_NE_WORK_IDENTITY_FAILURE`
`LOCAL_MODEL_NE_AUTOMATICALLY_PRIVATE_FOR_ALL_DATA`
`USER_NE_SESSION_OPERATOR`
