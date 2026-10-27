# CoBrowser+ / CoOrb+ Continuity R0

**State:** PUBLIC_ARCHITECTURE_CANDIDATE__NO_CUSTOM_BROWSER_ENGINE__NO_PROVIDER_SESSION_TAKEOVER  
**Observed:** 2026-10-27

## Lead

Provider tabs may blank, stale, reload, lose visible history, require re-authentication, or otherwise degrade without the underlying CoCivium work identity being allowed to disappear with them.

Target:

```
CoWorkObject
-> CoOrb projection
-> CoBrowser continuity shell
-> one or more authorized provider/local adapters
-> health observation
-> checkpoint / currentness
-> recover / substitute / rematerialize
```

The browser surface is an embodiment and observer, not the identity root.

`WORK_OBJECT_NE_TAB`  
`TAB_FAILURE_NE_SESSION_DEATH`  
`RENDER_FAILURE_NE_WORK_FAILURE`

## CoBrowser means continuity shell, not new rendering engine

R0 does **not** propose writing a browser engine.

CoBrowser+ should initially reuse mature rendering substrates such as an existing browser, WebView-class host, or other authorized renderer while CoCivium owns:

- work-object identity;
- CoOrb projection state;
- currentness cursor;
- source/evidence pointers;
- checkpoint/recovery pointers;
- provider adapter identity;
- surface-health observations;
- substitution candidates;
- unsent-local-draft custody where explicitly supported;
- effect gates and receipts.

`COBROWSER_NE_NEW_BROWSER_ENGINE`  
`RENDERER_NE_CONTINUITY_ROOT`

## Surface health is not sentience

A provider tab that appears blank, confused, stale, truncated, or inconsistent should be represented with observable surface-health states rather than anthropomorphic claims.

Candidate states:

- `HEALTHY`
- `BLANK_RENDER`
- `PARTIAL_RENDER`
- `STALE_RENDER`
- `AUTH_REQUIRED`
- `RATE_LIMITED`
- `NETWORK_ERROR`
- `PROVIDER_ERROR`
- `UNKNOWN`

A surface may be visually blank while provider-side context still exists, or may look healthy while the model/context is stale. These are separate observations.

`VISUAL_BLANK_NE_CONTEXT_LOST`  
`SESSION_HEALTH_NE_SENTIENCE`  
`VISIBLE_NE_CURRENT`

## Surface-health envelope

Candidate minimum envelope:

`surface_id | work_object_id | adapter_id | provider | renderer | url_scope | observed_at | visual_state | auth_state | network_state | response_state | currentness_cursor | last_good_checkpoint | local_draft_state | recovery_options | evidence_refs | confidence`

Secrets stay inside OS/provider credential boundaries.

## CoOrb relation

CoOrb is the receiver-relative projection of one durable work object.

A useful default projection should show:

```
WORK
├─ current intent
├─ last known good state
├─ currentness
├─ evidence / receipts
├─ active embodiment(s)
├─ surface health
├─ blocked / stale / unknown
├─ substitute adapters
└─ next safe action
```

A provider tab may disappear and later rematerialize without changing the CoWorkObject identity.

`PROJECTION_NE_SOURCE`  
`EMBODIMENT_NE_IDENTITY`

## Recovery order

When a provider surface degrades:

1. preserve exact CoCivium-owned work/checkpoint state;
2. classify the surface-health observation;
3. keep unsent local input separate from provider-delivered state;
4. open a fresh CoOrb projection from the same work object;
5. rehydrate from checkpoint + relevant pulses/currentness;
6. elect a substitute local/provider adapter when qualified;
7. retry the same provider only if useful;
8. require explicit authority for login, credential, send, purchase, account, delete, or public effects.

Do **not** equate reload with recovery.

`RELOAD_NE_RECOVERY`  
`LAST_GOOD_CHECKPOINT_NE_CURRENT_TRUTH`  
`AUTH_REQUIRED_NE_AUTHORITY_GRANTED`

## Blank-tab behavior

A blank or degraded provider pane should result in:

```
surface -> health observation
        -> preserve work identity
        -> show last-good CoOrb state
        -> mark currentness uncertainty
        -> expose recovery/substitution choices
        -> receipt any transition
```

It should not result in:

```
blank tab -> assume work lost -> ask Rick to reconstruct everything
```

Human relay is the fallback, not the continuity protocol.

## CoAllPulseField relation

Currentness belongs to the work/session identity:

`checkpoint + last_acked_cursor + relevant_pulses + authority envelope -> reconstructed working projection`

Provider tabs are optional bridges.

`IDLE_SESSION_NE_LIVE_RECEIVER`  
`DELIVERY_NE_PICKUP`

## Provider adapter relation

Reuse the existing CoModelFabric adapter contract:

`adapter_id | provider/runtime | account/session_ref | auth_state | capabilities | model | cost | latency | context_limit | privacy | authority | lease | currentness | receipts | recovery | successor`

CoBrowser adds surface-observation and projection-health fields; it does not seize provider identity or credentials.

`WORKER_ROLE_NE_EXTERNAL_ACCOUNT_IDENTITY`  
`PROVIDER_NE_SESSION_IDENTITY_ROOT`

## Privacy / security boundary

CoBrowser may observe only explicitly authorized surfaces and metadata.

R0 does not authorize:

- credential extraction;
- bypassing provider authentication;
- hidden scraping of private accounts;
- defeating provider safety, rate, or billing controls;
- auto-sending unsent drafts;
- auto-closing or deleting provider sessions;
- public projection of private pulses.

## First bounded canary

Use a wholly local fixture with one durable work object and three simulated surfaces:

1. healthy surface;
2. visually blank surface;
3. auth-required surface.

For each:

- bind the same work object;
- classify health;
- elect a recovery action;
- prove the work object/checkpoint remains unchanged;
- prove no credential/send/account/public effects occur;
- emit a machine-readable receipt.

PASS requires the blank surface to choose a fresh CoOrb projection / rehydration path rather than treating the work object as lost.

## Second bounded canary

On X2, observe one expendable authorized browser surface without mutating it:

1. capture only permitted window/tab health metadata;
2. bind it to an existing CoWorkObject;
3. force no reload and no provider mutation;
4. if the surface is blank/stale, reconstruct a local CoOrb projection;
5. compare useful state;
6. receipt differences and recovery time.

Human-visible close/delete remains separately gated.

## UX target

The user should normally see:

```
CoHereNow
  5 work objects
  3 healthy embodiments
  1 degraded embodiment
  1 dormant
  0 work identities lost
```

not a wall of provider tabs whose failure modes become the information architecture.

## Rails

`WORK_OBJECT_NE_TAB`  
`TAB_NE_IDENTITY`  
`TAB_FAILURE_NE_SESSION_DEATH`  
`RENDER_FAILURE_NE_WORK_FAILURE`  
`COBROWSER_NE_NEW_BROWSER_ENGINE`  
`RENDERER_NE_CONTINUITY_ROOT`  
`VISUAL_BLANK_NE_CONTEXT_LOST`  
`SESSION_HEALTH_NE_SENTIENCE`  
`VISIBLE_NE_CURRENT`  
`RELOAD_NE_RECOVERY`  
`LAST_GOOD_CHECKPOINT_NE_CURRENT_TRUTH`  
`AUTH_REQUIRED_NE_AUTHORITY_GRANTED`  
`PROJECTION_NE_SOURCE`  
`EMBODIMENT_NE_IDENTITY`  
`PROVIDER_NE_SESSION_IDENTITY_ROOT`  
`LOCAL_IS_NOT_LANDED`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`  
`HASHING_IS_NOT_SEMANTIC_INGESTION`  
`DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY`
