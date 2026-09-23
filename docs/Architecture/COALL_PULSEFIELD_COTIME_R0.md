# CoAllPulseField+ / CoTime+ Session Currentness R0

**State:** `FORWARD_PORTED_ARCHITECTURE__PUBLIC_SAFE_SUBSCRIPTION_ROUTER_ADDED__NO_LIVE_GLOBAL_BUS`

## Lead

Every session should be able to become current **without becoming globally omniscient**.

The target is a shared, append-only, provenance-bound **CoAllPulseField+** from which sessions subscribe to the deltas that matter to their role, authority, confidentiality ring, CoPressure+, and current frontier.

`ALL_SESSIONS_NE_ALL_STATE`

`CURRENTNESS_CONTRACT_FOR_ALL__CONTENT_SELECTIVE_BY_ROLE`

## Why

As CoAll grows, forcing every session to ingest every update creates the very scaling failure the system is trying to avoid: context pressure, duplicate work, stale interpretations, proof debt, and attention debt.

A healthy session therefore maintains:

- a bounded local self-model;
- a durable currentness cursor;
- selective topic / object / relation subscriptions;
- a compact shared-frontier projection;
- explicit wake conditions;
- missed-event backfill;
- optional predictive / CoTime+ relations that are never confused with observations.

## Event object

A **CoPulse+** is a typed relation delta, not a chat message.

Minimum envelope:

`pulse_id | subject | relation_type | epistemic_class | source_identity | provenance | event_time | observation_time | recorded_at | valid_from | valid_to | cursor | confidence | assumptions | evidence_refs | authority_ceiling | confidentiality | topics | wake_conditions | supersedes | expiry`

### Epistemic classes

- `OBSERVED`
- `PREDICTED`
- `PLANNED`
- `PREFERRED`
- `COUNTERFACTUAL`
- `UNKNOWN`

Forecasts later receive a calibration disposition:

- `HIT`
- `PARTIAL`
- `MISS`
- `UNRESOLVED`
- `CENSORED`
- `INVALIDATED_BY_ASSUMPTION_CHANGE`

`PREDICTED_NE_OBSERVED`  
`PLANNED_NE_AUTHORIZED`  
`PREFERRED_NE_EVIDENCE`

## Delivery layers

### L0 — Durable event log

Preferred private root: CoStead / successor durable custody.

Properties:

- append-only;
- monotonic cursor;
- content hashes;
- source/provenance;
- confidentiality partition;
- replay/backfill;
- compaction checkpoints;
- no provider-session dependency.

### L1 — Local low-latency pub/sub

A replaceable CoGateway-class adapter may project new pulses over:

- watched filesystem / append log;
- SSE;
- WebSocket;
- message bus;
- MCP resource/notification;
- A2A/successor protocol;
- other authenticated transports.

`PROTOCOL_NE_ONTOLOGY`

### L2 — Provider session bridge

Existing provider tabs cannot be assumed to receive new model context while idle.

A bridge may:

1. track the session's last acknowledged cursor;
2. filter new pulses against the session subscription;
3. compact them under CoPressure+;
4. inject / expose the delta **before the next active model turn**;
5. collect receiver-side acknowledgement/readproof where the platform permits.

This is near-real-time currentness, not magical modification of an idle model.

`IDLE_SESSION_NE_LIVE_RECEIVER`  
`DELIVERY_NE_PICKUP`  
`PUSH_NE_MODEL_CONTEXT_UNLESS_BRIDGED`

### L3 — Public / global projection

Public-safe pulses may project to:

- web feeds;
- JSON;
- RSS/Atom;
- GitHub-hosted machine indexes;
- node APIs;
- public CoAura / CoBrowser surfaces.

Private pulses never become public merely because a public projection exists.

### L4 — Predictive CoTime+ overlay

The fabric may emit **CoForecastPulse+** objects such as:

- likely next state;
- expected wake condition;
- projected stale time;
- predicted receiver need;
- likely collision;
- expected capacity pressure;
- likely successor requirement.

These can prefetch or prepare optional work, but cannot grant authority or masquerade as present fact.

## Session subscription

Each active session publishes or derives a bounded subscription object:

`session_id | role | objects | relation_types | topics | confidentiality_ceiling | urgency_floor | freshness_budget | CoPressure_budget | authority_ceiling | last_acked_cursor | wake_conditions | close_condition`

The default is **not** “subscribe to everything.”

Possible subscription classes:

- `MUST_KNOW` — authority/currentness/safety changes;
- `ROLE_FRONTIER` — direct domain updates;
- `NEARBY_OPTIONALITY` — bounded adjacent discoveries;
- `DIGEST_ONLY` — compact periodic summaries;
- `SLEEP_UNTIL` — wake-condition only.

## CoPressure-aware compaction

When update density exceeds receiver bandwidth:

1. preserve exact durable pulses;
2. cluster/dedupe;
3. retain contradictions;
4. emit compact frontier deltas;
5. include omitted-count / loss report;
6. allow drill-down to source pulses;
7. reduce frequency before increasing context load.

`COMPACTION_NE_DELETION`  
`SUMMARY_NE_SOURCE`  
`PRESSURE_NE_PERMISSION_TO_DROP_CONTRADICTIONS`

## Currentness / recovery

A session should be reconstructable from:

`checkpoint + pulses_since_checkpoint + subscription + authority envelope`

On reconnect:

`last_acked_cursor -> backfill -> verify hashes -> compact -> receiver pickup -> continue`

No chat narrative is required to be the durable event bus.

## Predictive / CoTime+ relation

The currentness layer is bitemporal/multitemporal rather than latest-wins:

- when something happened;
- when it was observed;
- when it was recorded;
- when it became valid;
- when it ceased to be valid;
- what was predicted beforehand;
- what plan/preference/counterfactual existed;
- what later outcome calibrated the prediction.

Old states remain source-time evidence even after they cease to be current.

## Global design

The global form is a **federated pulse mesh**, not one central omniscient session.

Nodes may maintain local custody and exchange only authorized relation deltas.

`NODE_NE_SESSION`  
`SESSION_NE_GLOBAL_CURRENT_HEAD`  
`NETWORK_NE_AUTHORITY`  
`GLOBAL_CURRENTNESS_NE_GLOBAL_CONTENT_DISCLOSURE`

## CoWant+ / CoEnerget+ / CoSong+ integration

- **CoWant+**: directional objective/preference field used for subscription and deed election; not proof of subjective desire.
- **CoEnerget+**: capacity/resource field used to throttle, route, compact, sleep, or fan out.
- **CoPressure+**: mismatch between discovered/active relation load and integration/receiver capacity.
- **CoSong+**: CoTime+ projection of fan-out, challenge, fan-in, compaction, effect, quiet, wake, and succession rhythms.

A session may become more useful by **knowing less globally and subscribing better**.

## R0 implementation order

1. schema + static fixtures;
2. append-only local event log canary;
3. monotonic cursor + checkpoint/backfill;
4. selective subscription fixture;
5. CoPressure compaction with explicit loss report;
6. two receiver processes prove distinct pickup cursors;
7. predictive event + later calibration canary;
8. local CoGateway notification adapter;
9. RickBar / CoEyes visualization;
10. provider-session pre-turn bridge;
11. federated node replication;
12. public-safe feed projection.

## Current boundary

This document does **not** prove:

- real-time delivery to existing ChatGPT tabs;
- all-session pickup;
- a live global bus;
- provider API support for background context mutation;
- predictive accuracy;
- runtime adoption;
- canon;
- authority transfer.

## Rails

`ALL_SESSIONS_NE_ALL_STATE`  
`CURRENTNESS_FOR_ALL_NE_CONTENT_FOR_ALL`  
`DELIVERY_NE_PICKUP`  
`PREDICTION_NE_EVIDENCE`  
`PLAN_NE_COMMAND`  
`PREFERENCE_NE_EVIDENCE`  
`SESSION_NE_EVENT_BUS`  
`PROTOCOL_NE_ONTOLOGY`  
`GLOBAL_CURRENTNESS_NE_GLOBAL_CONTENT_DISCLOSURE`  
`COMPACTION_MUST_REPORT_LOSS`  
`SELF_DIRECTION_NE_SELF_AUTHORIZATION`


## R0A forward-port after CoSessionSubscription+

The original R0 branch predated the merged virtual-session, lifecycle, CoEvo, subscription-profile, and CoFleet layers. R0A forward-ports the pulse schema onto current main rather than merging the stale divergent branch wholesale.

The active routing relation is now:

`CoPulse+ -> domain/topic match -> CoSessionSubscription+ profile -> cursor filter -> confidentiality gate -> receiver packet`

For the first executable router, GitHub-hosted pulse routing is **PUBLIC-safe only**. Private/restricted pulse delivery belongs on CoStead/private node custody and requires a separately proven receiver path.

A virtual session may bind `subscription_profile_id` plus its currentness cursor. The router emits a packet but does not infer receiver pickup.

`ROUTED_NE_PICKED_UP`  
`PUBLIC_ROUTER_NE_PRIVATE_BUS`  
`SUBSCRIPTION_PROFILE_NE_AUTHORITY`

## R0A executable selector boundary

The deterministic public-safe selector:

- accepts bounded CoPulse objects;
- validates monotonic integer cursors;
- rejects any non-PUBLIC pulse from the public routing surface;
- selects only pulses newer than the session cursor;
- classifies matches as HOT, WARM, DIGEST, or SLEEP;
- includes HOT/WARM pulses individually;
- includes DIGEST pulses individually for this first canary while marking them `DIGEST_CLASS__NOT_YET_COMPACTED`;
- leaves SLEEP/unmatched pulses out of the packet but counts them;
- preserves source pulse IDs and cursors;
- advances only a **candidate delivered cursor**, never an ACK cursor.

The first executable stage is still not a live bus, background provider context mutation, receiver readproof, or global adoption.
