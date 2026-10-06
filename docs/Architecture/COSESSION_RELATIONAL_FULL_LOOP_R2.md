# CoSession Relational Full Loop R2

**State:** `DRAFT_CANDIDATE__VIRTUAL_FIRST__NO_PROVIDER_SESSION_MUTATION`

## Lead

CoCivium should stop treating visible provider chats as the unit of continuity.

A durable work-bearing session is a **logical relational identity** that may be embodied by a provider chat, local worker, GitHub job, model invocation, browser surface, human-visible workspace, or nothing live at all.

`VIRTUAL_SESSION_NE_PROVIDER_TAB`  
`MANUAL_SESSION_IS_ONE_EMBODIMENT`  
`EMBODIMENT_NE_IDENTITY`

Not every object becomes a session. A durable virtual/session envelope is warranted when there is a continuing purpose, work frontier, authority ceiling, currentness cursor, wake condition, checkpoint, or successor relation.

`VIRTUAL_FIRST_NE_EVERYTHING_IS_SESSION`

## Full relational loop

The mature loop is best understood as a **CoBoogie+ envelope**:

`Observe -> detect material drift? -> CoRegroup if needed -> CoSync/CoResync? -> CoAckRewise? -> Elect bounded deed -> Materialize if needed -> Execute -> Receipt -> Deliver -> Pickup -> Integrate/qualify -> Update currentness -> Quiesce/Sleep -> Wake predicate -> Observe`

The question marks matter.

- **CoBoogie+** is the outer event-driven freshness/recovery/execution cycle. It is not a blind rescan and need not run merely because time passed.
- Its initial observation/delta-audit phase characterizes material change, stale currentness, receiver/failure-domain change, contradiction, or return/reawakening.
- **CoRegroup+** is the finite reconciliation/disposition phase within that broader CoBoogie cycle, and may also be invoked independently when a bounded delta field already exists.
- **CoSync+** aligns verified state across relevant receivers; **CoResync** repairs detected drift/loss.
- **CoAckRewise+** is a scoped human interpretation/acknowledgement/revision relation only when a genuine human information, consent, authority, public, privacy, irreversible or financial edge requires it. It is not a heartbeat.
- Execution remains bounded by current authority, capability, confidentiality, collision, lease and reversibility constraints.
- Receipts and receiver readproof remain distinct from integration.

`RICK_NE_HEARTBEAT`  
`COREGROUP_SUBSET_OF_COBOOGIE_FOR_FULL_CYCLE`  
`SYNC_NE_DISCOVERY`  
`ACK_NE_HEARTBEAT`  
`ACK_NE_AUTHORITY_UNLESS_EXPLICITLY_SCOPED`  
`DELIVERY_NE_PICKUP`  
`PICKED_UP_NE_INTEGRATED`

## Manual and virtual sessions

All **durable work-bearing session identities** should be virtualizable.

A provider chat is therefore a foreground embodiment selected when:
- the human is actively interacting;
- a provider-only capability is needed;
- a human gate must be surfaced;
- interpretation benefits materially from a conversational embodiment.

Otherwise, work may remain latent, event-driven, scheduled, local, federated, watcher-like, or reconstructed on demand.

A manual session may disappear without killing the logical session if its material frontier is checkpointed and externally recoverable.

`SESSION_DEAD_NE_WAVE_DEAD`  
`PROVIDER_TAB_DEAD_NE_LOGICAL_SESSION_DEAD`

## CoBoogie / CoRegroup levels

CoBoogie and CoRegroup are substrate-neutral relations, not chat rituals.

They may operate at:
- object level;
- relation level;
- virtual-session level;
- workspace/front level;
- fleet level;
- node/failure-domain level;
- project/evolution lane level.

A fleet-level CoBoogie must not force every session to materialize. It should inspect bounded currentness/evidence projections and wake only materially affected receivers.

## Recursive relations and the “turtles” problem

Relations may themselves be first-class subjects or objects of other relations.

Example:

`AFFECTS(A,B)`  
`EVIDENCE_FOR(receipt_17, AFFECTS(A,B))`  
`SUPERSEDES_FOR_SCOPE(new_relation, old_relation)`  
`DISPUTES(observer_2, EVIDENCE_FOR(...))`

This is useful, but unbounded recursive metadata can become self-consuming bureaucracy.

Every higher-order relation used for control should therefore bind:

`anchor | purpose | observer | valid_time | provenance | meta_depth | proof_budget | stop_condition | projection_need`

Default control rule:

`IF_META_DEPTH_EXCEEDS_BUDGET -> COMPACT_OR_HOLD__DO_NOT_RECURSE_BLINDLY`

The system may retain deeper history durably while exposing only the bounded relation closure needed by the current receiver.

`RELATION_OF_RELATION_NE_INFINITE_REGRESS`  
`META_RELATION_NE_TRUTH`  
`META_RELATION_NE_AUTHORITY`  
`RECURSION_REQUIRES_STOP_CONDITION`  
`FULL_HISTORY_NE_FOREGROUND_CONTEXT`

## CoAckRewise+

Candidate meaning:

A **CoAckRewise+** is an explicit human-bound relation that can:
- acknowledge a presented fact/proposal;
- correct meaning or context;
- revise a prior preference or instruction;
- grant, narrow, deny, or expire a scoped authority;
- resolve an ambiguity that machines cannot safely infer.

It MUST preserve what changed and what did not.

A CoAckRewise is not required for routine safe continuation when standing bounded authority already covers the deed.

Financial effects remain separately gated by a fresh exact human acknowledgement.

`ACKREWISE_NE_GENERIC_ACK`  
`ACKREWISE_NE_PERMANENT_BLANKET`  
`ONE_ACK_NE_CHAINED_APPROVALS`  
`FINANCIAL_EFFECT_REQUIRES_FRESH_EXACT_HUMAN_GATE`

## CoSync+

CoSync consumes already-qualified state; it does not discover truth.

A bounded CoSync should bind:
- source head/hash/currentness;
- receiver;
- confidentiality;
- delivery object;
- readproof expectation;
- ACK cursor if applicable;
- failure/retry semantics;
- no-op condition.

A sync loop ends when relevant receivers are current enough for the next deed, not when every known object has been copied everywhere.

`CURRENTNESS_FOR_ALL_NE_CONTENT_FOR_ALL`  
`SYNC_NE_REPLICATION_TOTALITY`

## Full-loop completion

A loop is complete only when the selected deed has reached the terminal state appropriate to its class.

Examples:
- read-only research may complete at verified receipt;
- routed work may require receiver pickup;
- shared-state mutation may require integration qualification;
- public/financial/irreversible effects may require human-gated acceptance plus durable receipt.

Do not use one universal “PASS” as a substitute for lifecycle semantics.

## User experience

RickBar/CoDesktop should project:
- current work/fronts;
- material exceptions;
- currentness;
- human blockers only when real;
- optional drill-down into virtual sessions/embodiments/receipts.

The user should not manage provider tabs as infrastructure.

`USER_WORKSPACE_NE_PROVIDER_SESSION`

## Current boundary

This R2 candidate does not prove provider-native session creation, provider-tab closure, X2 runtime binding, local Ollama materialization, or universal automatic receiver pickup.

It defines the relation semantics and a synthetic canary target.

## Next

Run the R2 full-loop matrix in read-only CI. Then qualify a runtime binding separately:
1. reconstruct one logical session without its original provider tab;
2. run CoBoogie/CoRegroup over a material delta;
3. CoSync only the required receiver packet;
4. invoke CoAckRewise only if the fixture contains a true human gate;
5. prove receipt -> pickup -> integration distinction;
6. sleep/quiesce when no wake predicate remains.
