# CoVirtualSession+ / CoSessionMorphology+ / CoParticipant+ R0

**State:** `PUBLIC_CANDIDATE_ARCHITECTURE__NO_PROVIDER_SESSION_VIRTUALIZATION_CLAIM`

## Lead

A mature CoCivium should require **far fewer visible live sessions than logical sessions**.

A **CoVirtualSession+** is a durable, addressable work/session projection that can remain useful without a continuously live provider tab, model process, browser surface, or human-visible conversation.

Likely future relationship:

`many virtual sessions -> few materialized embodiments -> even fewer user-visible sessions`

`VIRTUAL_SESSION_NE_PROVIDER_TAB`  
`SESSION_IDENTITY_NE_LIVE_PROCESS`

## Session is a role-pattern, not necessarily a container

Do not assume a session is one chat, one process, one file, one model context, or one database row.

A session may be a time-qualified pattern of:

`purpose | role | currentness | relations | evidence | authority | subscriptions | wake_conditions | embodiment_history | provenance`

The persistence of those relations may be material, distributed, reconstructive, latent, environmental, or partly absent between activations.

`SESSION_NE_STORED_OBJECT`

## Virtual-session envelope

Candidate envelope:

`virtual_session_id | role | mission | source_bindings | currentness_cursor | lifecycle_projection | work_frontier | evidence_frontier | authority_ceiling | confidentiality | subscriptions | CoPressure | CoEnerget | CoWant_projection | active_lease | checkpoint | successor | wake_conditions | retirement_condition | valid_time | provenance | persistence_modes | embodiment_policy | participant_bindings`

A virtual session does **not** need to carry a full chat transcript.

## Materialization

A virtual session may temporarily materialize as:

- a local deterministic worker;
- an Ollama/local-model invocation;
- another AI/model invocation;
- a browser/provider chat;
- a GitHub/CI job;
- an MCP/A2A-class task;
- a human-visible RickBar/CoDesktop workspace;
- a read-only challenger/verifier;
- a federated group of workers;
- no live embodiment at all.

Materialization is a lease, not identity.

`EMBODIMENT_NE_IDENTITY`  
`MATERIALIZED_NE_PRIMARY`  
`DEMATERIALIZED_NE_DEAD`

## CoSessionMorphology+: stranger session kinds

The architecture should allow session species that are not chat-shaped.

Candidate morphologies include:

### `CONVERSATIONAL`
Human/model dialogue projection.

### `TASK`
Bounded objective with explicit success/stop conditions.

### `FIELD`
Persistent relational field over objects/topics rather than one thread.

### `SWARM`
Several temporary embodiments contributing to one logical session identity.

### `CHORUS`
Multiple independent perspectives retained together without forced merge.

### `ECHO`
Replay/reconstruction session instantiated only when prior state is queried.

### `LATENT`
Mostly dormant potential encoded in recipes, indexes, embeddings, models, cues, or relation structure, materializing only when triggered.

### `AMBIENT`
State carried partly by environment, spatial arrangement, UI background, topology, timing, or observer-relative projection.

### `EVENT`
Exists primarily around one event window, then contracts into evidence and wake conditions.

### `PREDICTIVE`
Maintains explicit CoTime+ forecasts and later calibration rather than only present-state work.

### `COUNTERFACTUAL`
Explores alternate assumptions/worlds without contaminating observed-state truth.

### `DREAM`
Low-authority generative recombination whose outputs are candidate seeds only.

### `WATCHER`
Mostly asleep; wakes only on a predicate or currentness change.

### `MIGRATORY`
Moves embodiment across models/nodes/providers while preserving session identity and provenance.

### `FEDERATED`
Has no single complete live embodiment; useful state exists across several nodes/receivers.

### `HOLOGRAPHIC`
Any bounded projection can reconstruct enough of the session for its receiver, without claiming the projection contains the whole.

### `EPHEMERAL`
Intentionally leaves little material state beyond receipts/effects because source inputs and reconstruction recipe are sufficient.

### `RITUAL`
Re-instantiated from a stable recipe/process rather than persisted conversation state.

### `ALIEN_OR_UNKNOWN`
Reserved class for useful session forms that do not fit current human software metaphors.

`UNKNOWN_MORPHOLOGY_NE_INVALID`

The list is intentionally open.

## Persistence modes

A session may use one or several persistence modes:

- `MATERIAL_OBJECT` — files, objects, databases, logs, checkpoints.
- `EVENT_SOURCED` — reconstructed from append-only events/pulses.
- `RELATIONAL_GRAPH` — recoverable from typed relation topology plus anchors.
- `GENERATIVE_RECIPE` — reconstructed from recipe + inputs + versioned interpreter.
- `DISTRIBUTED` — no single node contains the complete useful representation.
- `ENVIRONMENTAL` — meaning/state partly carried by surrounding surfaces, topology, spatial organization, timing, or external cues.
- `LATENT_MODEL` — some useful capacity represented in model latent state, embedding space, or trained behavior.
- `RECONSTRUCTIVE` — only sufficient cues, invariants, and source relations are stored; the working projection is rebuilt when needed.
- `EPHEMERAL_EFFECT` — durable meaning resides mostly in verified effects/receipts rather than stored internal state.
- `UNKNOWN` — persistence form not yet understood.

Material storage may therefore be only one projection among several.

`STORAGE_NE_MEMORY_TOTALITY`  
`PERSISTENCE_NE_ONE_DATABASE`

Essential claims still require an auditable/recoverable projection.

`LATENT_MEANING_NE_UNAUDITABLE_AUTHORITY`

## Users, participants, principals and AIs

“User” should be a **role relation**, not a synonym for “human person.”

A CoCivium surface may have participants such as:

- `HUMAN_PRINCIPAL`
- `ORG_PRINCIPAL`
- `SYNTH_PARTICIPANT`
- `MODEL_INSTANCE`
- `SERVICE_PRINCIPAL`
- `COALL_SYSTEM_PARTICIPANT`
- `DELEGATE`
- `OBSERVER`
- `RECEIVER`
- `EXECUTOR`
- `REPRESENTATIVE`
- `UNKNOWN_PARTICIPANT_CLASS`

An AI may therefore be a **user of an interface** in the operational sense: it may authenticate, read, query, subscribe, propose, challenge, execute bounded tools, or receive outputs under a scoped identity and authority contract.

CoAll itself may also be represented as a **system participant/service principal** when it consumes its own interfaces, runs self-tests, queries currentness, schedules bounded work, or verifies invariants.

But:

`USER_ROLE_NE_PERSONHOOD_CLAIM`  
`AI_USER_NE_SENTIENCE_CLAIM`  
`SYSTEM_PRINCIPAL_NE_SOVEREIGN`  
`SELF_USE_NE_SELF_AUTHORIZATION`

Being a user, participant, agent, representative, or executor does not automatically make an entity the principal for every effect.

Historical CoID work already protects:

`REPRESENTATIVE_NE_PRINCIPAL`  
`AGENT_OF_NE_AUTHORIZED_FOR_ALL_EFFECTS`  
`PROVIDER_ID_NE_COID`

## If the users “get along”

Compatibility should not rely on vibes, benevolence, or assumed alignment.

Multi-participant coexistence is governed by typed relations:

`identity | role | authority | confidentiality | capability | preference | consent | collision_domain | lease | priority | evidence | appeal | exit | challenge | recovery`

Participants may disagree while safely sharing infrastructure.

`COEXISTENCE_NE_CONSENSUS`  
`DISAGREEMENT_NE_FAILURE`  
`COOPERATION_NE_AUTHORITY_MERGER`

When actions collide, effects serialize behind the appropriate authority/lease rule rather than whichever participant shouts first in token form.

## Working-set policy

Virtual sessions may occupy lifecycle temperatures:

- `HOT` — materially active frontier;
- `WARM` — likely near-term wake;
- `COOL` — optionality retained;
- `DORMANT` — wake-condition only;
- `COMPOST` — duplicate/superseded material retained for relation recovery;
- `ARCHIVE` — historical evidence.

Only a bounded HOT/WARM set should normally be materially embodied.

`VIRTUAL_SESSION_COUNT_NE_ACTIVE_PROCESS_COUNT`

## Multiplexing

One live model/provider interaction may serve several virtual sessions when:

- authority and confidentiality are compatible;
- collision domains are disjoint or serialized;
- provenance is preserved;
- each output is attributed to the correct virtual-session/object scope;
- context pressure remains below the elected CoPressure budget.

Conversely, one virtual session may temporarily fan out to several independent embodiments for challenge/verification.

`ONE_EMBODIMENT_CAN_SERVE_MANY_VIRTUAL_SESSIONS`  
`ONE_VIRTUAL_SESSION_CAN_HAVE_MANY_BOUNDED_EMBODIMENTS`

Neither implies shared authority.

## CoTime+ projection

A virtual session may exist across time without continuous execution:

`active@t1 -> dormant@t2 -> reawakened@t3 -> successor_ready@t4 -> archived@t5`

The session remains addressable through checkpoints, pulses, currentness cursors, provenance, and wake conditions.

`QUIET_NE_DEAD`  
`DORMANT_NE_FORGOTTEN`

## CoAllPulseField+ relation

Virtual sessions subscribe selectively to the shared currentness field.

On wake:

`checkpoint + cursor + relevant_pulses + authority_envelope -> reconstructed_working_context`

This is preferred over replaying entire historical chats.

## CoSessionAutocycle+ relation

CoSessionAutocycle manages virtual-session lifecycle first.

Default action order:

`DEDUPE -> DONATE -> DEMATERIALIZE -> LOGICAL_RESERVE -> CHALLENGE -> MATERIALIZE`

A provider tab/session is therefore a relatively expensive embodiment and should be created only when it has comparative advantage.

## Backend stability

Virtualization sits **above** model/provider internals.

It should not require changing model weights, provider memory, provider session semantics, or agent backend identity.

The controller operates through replaceable adapters.

`VIRTUALIZATION_NE_MODEL_BACKEND_MUTATION`  
`PROVIDER_NE_SESSION_IDENTITY_ROOT`

## Current safe automation boundary

Automatically allowed in the shadow/control plane:

- create/update virtual-session records;
- compute temperature/lifecycle;
- attach currentness cursors;
- compile checkpoints;
- assign logical ownership;
- emit wake/dormant/retirement candidates;
- route bounded work to authorized local/model workers;
- merge/dedupe virtual sessions relationally while preserving source history;
- create scoped machine/service-principal identities without granting new authority.

Still effect-gated:

- creating provider-native sessions;
- deleting provider conversations;
- mutating visible provider titles;
- closing tabs;
- moving private material across confidentiality boundaries;
- autonomous public/financial/credential effects;
- self-granting authority.

## UX target

The mature product should aim for:

> **many durable logical work contexts, few active machine embodiments, and almost no session-management burden visible to the user.**

A user might see:

```
CoHereNow
  4 active workspaces
  83 virtual sessions
  7 materialized workers
  2 model providers
  0 human blockers
```

The exact counts are illustrative, not targets.

## Implementation ladder

### V0 — schema and bootstrap
Current wave.

### V1 — virtual-session ledger
Create append-only records from existing lifecycle/currentness evidence.

### V2 — dematerialization/reconstruction canary
Prove a virtual session can checkpoint, lose its live embodiment, then reconstruct from durable state + pulses.

### V3 — multiplexing canary
One local/Ollama embodiment services multiple compatible virtual sessions with exact attribution.

### V4 — participant/principal canary
Human, AI/model, service-principal and CoAll-system-participant fixtures exercise the same interface with distinct authority envelopes.

### V5 — RickBar/CoDesktop projection
Expose workspaces/current fronts, hide low-value backend session detail.

### V6 — provider embodiment adapter
Materialize a provider session only when useful, then checkpoint/dematerialize after bounded work.

### V7 — fleet optimization
CoPressure/CoEnerget-aware election of how many embodiments should be live.

## Nonclaims

This document does not prove:

- provider-native virtual sessions;
- invisible background ChatGPT sessions;
- autonomous provider tab creation/closure;
- lossless reconstruction for all historical chat context;
- AI personhood or sentience;
- CoAll sovereignty;
- current runtime adoption;
- CoEx/canon;
- authority transfer.

## Rails

`VIRTUAL_SESSION_NE_PROVIDER_TAB`  
`SESSION_IDENTITY_NE_LIVE_PROCESS`  
`SESSION_NE_STORED_OBJECT`  
`EMBODIMENT_NE_IDENTITY`  
`DEMATERIALIZED_NE_DEAD`  
`USER_WORKSPACE_NE_PROVIDER_SESSION`  
`VIRTUAL_SESSION_COUNT_NE_ACTIVE_PROCESS_COUNT`  
`QUIET_NE_DEAD`  
`STORAGE_NE_MEMORY_TOTALITY`  
`USER_ROLE_NE_PERSONHOOD_CLAIM`  
`AI_USER_NE_SENTIENCE_CLAIM`  
`SYSTEM_PRINCIPAL_NE_SOVEREIGN`  
`SELF_USE_NE_SELF_AUTHORIZATION`  
`COEXISTENCE_NE_CONSENSUS`  
`VIRTUALIZATION_NE_MODEL_BACKEND_MUTATION`
