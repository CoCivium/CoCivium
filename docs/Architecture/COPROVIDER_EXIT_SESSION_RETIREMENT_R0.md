# CoProviderExit+ / CoSessionRetirement+ R0

**State:** `CANDIDATE_RETIREMENT_GATE__NO_PROVIDER_TAB_CLOSE_NO_ACCOUNT_DELETE_NO_RUNTIME_AUTHORITY`

## Lead

CoCivium should be able to lose ChatGPT, a local PC, CoBar, a model family, a cloud host, or an entire provider without losing the identity of its work.

The target is not "move from ChatGPT to local."

The target is:

```text
logical work / durable relations
        ↓
several replaceable execution routes
        ↓
several independent custody/failure domains
        ↓
no provider tab, local machine, web service, or model family is mandatory
```

A local open-source stack remains valuable, but it should become an **optional embodiment**, not the new single point of failure.

## Session retirement

A provider chat/session is eligible to retire for scope only when:

- unique useful state has been externalized;
- the durable object has an elected destination;
- an elected receiver has exact-object readproof;
- reconstruction has been canaried;
- unfinished effect obligations are absent or transferred;
- at least one admissible alternative execution route exists.

`CHAT_TAB_NE_SESSION_IDENTITY`

`CLOSE_SAFE_NE_DATA_DELETED`

Closing a tab is not evidence that its history was preserved, and preserving history does not require keeping the tab alive.

## Account exit is a stronger gate

Retiring many individual chats is much easier than closing the provider account.

Account exit additionally requires:

- a bounded inventory/coverage claim over the account material we intend to retain;
- private-state custody outside the provider;
- exact receiver pickup for retained critical objects;
- recovery/reconstruction proof independent of the account;
- alternative execution routes;
- no unresolved provider-only credentials/effects/subscriptions that matter.

Until those are proven:

`ACCOUNT_CLOSE_REQUIRES_COVERAGE_PROOF`

Current project evidence does **not** prove complete coverage of all ChatGPT sessions or all private state.

Therefore this R0 does not declare the ChatGPT account close-safe today.

## Local / power failure

No UPS is required for local resources to remain useful.

It simply means the local site cannot be treated as a sufficient continuity root.

A power-off local machine can still be:

- a preferred privacy route while available;
- a cheap open-model execution surface;
- a cache;
- a reconstruction node;
- a private working surface;
- a recovery/fallback path.

But unique durable state should not depend on it.

`NO_UPS_NE_NO_LOCAL_VALUE`

`OPTIONAL_LOCAL_NE_REQUIRED_LOCAL`

`LOCAL_DEVICE_NE_CUSTODY_ROOT`

## CoBar / webservice redundancy

CoBar, RickBar, CoDesktop, or any future web service should become observer/control projections over durable relations rather than the only place those relations exist.

A mature front door may fail while work remains reconstructible elsewhere.

Candidate relationship:

```text
CoBar / local web UI
   = useful projection + control surface
   != durable identity root
   != sole scheduler
   != sole custody root
```

## Failure domains, not copy counts

Three copies on one powered-off machine are one failure domain.

Two model APIs from the same provider may be one provider failure domain.

A local PC and a NAS on the same unprotected mains circuit may share a power failure domain.

Real redundancy should consider:

- power;
- physical site;
- provider/account;
- network;
- credential authority;
- operating system/runtime;
- storage operator;
- legal/jurisdictional dependency;
- model/runtime family;
- human knowledge concentration.

`REDUNDANCY_NE_REPLICA_COUNT`

`FAILURE_DOMAIN_DIVERSITY_NE_COPY_COUNT`

## Desired exit posture

A strong future exit posture looks more like:

```text
public-safe durable projection      -> GitHub / mirrors
private durable state               -> private/offsite node fabric
local execution                     -> Ollama/open runtimes when available
remote open/independent execution   -> replaceable nodes/providers
CI/read-only verification           -> independent hosted runners
human observer/control              -> RickBar/CoBar/other fronts
provider chats                      -> occasional leased embodiment only
```

No single line is the control plane.

## ChatGPT decommission ladder

1. Stop creating new long-lived ChatGPT-dependent work identities.
2. Convert active work into virtual-session objects/checkpoints.
3. Drain provider-only unique deltas into elected durable surfaces.
4. Prove exact receiver pickup.
5. Prove reconstruction without the source chat.
6. Retire individual close-safe tabs.
7. Keep ChatGPT only as an optional leased reasoning provider while useful.
8. Prove private/account-wide retained-state coverage.
9. Prove independent recovery without ChatGPT login.
10. Only then classify account closure as eligible for declared scope.
11. Account deletion itself remains a human/provider effect and requires explicit execution outside this candidate.

## What this R0 proves

The synthetic canary proves the retirement policy distinguishes:

- one close-safe provider tab;
- an undrained provider tab;
- incomplete account-wide coverage;
- a local-only single failure domain;
- a single CoBar/local-service embodiment;
- an optional local embodiment being offline;
- a hypothetical scope-complete provider exit;
- an otherwise-safe session with pending effect obligations.

It does not prove the user's current ChatGPT account has been drained.

## Rails

`PROVIDER_ACCOUNT_NE_CUSTODY_ROOT`  
`PROVIDER_SESSION_NE_CONTROL_PLANE`  
`CHAT_TAB_NE_SESSION_IDENTITY`  
`LOCAL_DEVICE_NE_CUSTODY_ROOT`  
`NO_UPS_NE_NO_LOCAL_VALUE`  
`OPTIONAL_LOCAL_NE_REQUIRED_LOCAL`  
`ONE_REMOTE_PROVIDER_NE_DISTRIBUTED`  
`GITHUB_NE_PRIVATE_CUSTODY`  
`ACCOUNT_CLOSE_REQUIRES_COVERAGE_PROOF`  
`CLOSE_SAFE_NE_DATA_DELETED`  
`SESSION_RETIREMENT_NE_ACCOUNT_DELETION`  
`REDUNDANCY_NE_REPLICA_COUNT`  
`FAILURE_DOMAIN_DIVERSITY_NE_COPY_COUNT`  
`DELIVERY_NE_PICKUP`  
`PICKED_UP_NE_INTEGRATED`  
`VALIDATION_IS_NOT_ACCEPTANCE`

## Current nonclaim

`CHATGPT_ACCOUNT_CLOSE_SAFE = UNPROVEN`

The architecture supports the direction; account-wide custody evidence does not yet justify the final shutdown claim.
